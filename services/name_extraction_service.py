"""
Name Extraction Service for LeadFinder

This service provides consistent name extraction functionality across the application.
It uses AI prompts to extract person names, titles, and organizations from text.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('name_extraction')
except ImportError:
    logger = None

@dataclass
class PersonInfo:
    """Data class for person information"""
    name: str
    title: Optional[str] = None
    organization: Optional[str] = None
    email: Optional[str] = None
    confidence: float = 0.0

class NameExtractionService:
    """Service for extracting person names from text using AI"""
    
    def __init__(self):
        self.ollama_service = ollama_service
    
    def extract_names_from_text(self, text: str, context: str = "") -> List[PersonInfo]:
        """
        Extract person names from text using AI
        
        Args:
            text: Text to analyze
            context: Optional context about what to look for
            
        Returns:
            List of PersonInfo objects
        """
        if not self.ollama_service:
            if logger:
                logger.warning("Ollama service not available for name extraction")
            return self._fallback_name_extraction(text)
        
        try:
            # Create AI prompt for name extraction
            prompt = f"""
            Extract all person names from the following text:
            
            {text}
            
            {f"Context: {context}" if context else ""}
            
            Please provide:
            1. Full names of all people mentioned
            2. Their titles or roles (if mentioned)
            3. Their organizations or affiliations (if mentioned)
            4. Any contact information (emails, phone numbers)
            
            Format your response as:
            NAME: [Full Name]
            TITLE: [Title/Role or "Not specified"]
            ORGANIZATION: [Organization or "Not specified"]
            CONTACT: [Contact info or "Not available"]
            ---
            
            If no names are found, respond with: "No person names found in the text."
            """
            
            # Get AI response
            response = self.ollama_service._call_ollama(prompt)
            
            if not response:
                if logger:
                    logger.warning("No AI response for name extraction")
                return self._fallback_name_extraction(text)
            
            # Parse AI response
            return self._parse_ai_response(response)
            
        except Exception as e:
            if logger:
                logger.error(f"Error in AI name extraction: {e}")
            return self._fallback_name_extraction(text)
    
    def extract_names_from_leads(self, leads: List[Dict[str, Any]]) -> Dict[str, List[PersonInfo]]:
        """
        Extract names from a list of leads
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            Dictionary mapping lead IDs to lists of PersonInfo objects
        """
        results = {}
        
        for lead in leads:
            lead_id = lead.get('id', lead.get('title', 'unknown'))
            
            # Combine title and snippet for analysis
            text = f"{lead.get('title', '')} {lead.get('snippet', '')}"
            
            # Extract names
            names = self.extract_names_from_text(text, "lead analysis")
            results[lead_id] = names
        
        return results
    
    def _parse_ai_response(self, response: str) -> List[PersonInfo]:
        """
        Parse AI response to extract person information
        
        Args:
            response: AI response text
            
        Returns:
            List of PersonInfo objects
        """
        if "no person names found" in response.lower():
            return []
        
        people = []
        
        # Split by separator
        sections = response.split('---')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Extract information using regex
            name_match = re.search(r'NAME:\s*(.+)', section, re.IGNORECASE)
            title_match = re.search(r'TITLE:\s*(.+)', section, re.IGNORECASE)
            org_match = re.search(r'ORGANIZATION:\s*(.+)', section, re.IGNORECASE)
            contact_match = re.search(r'CONTACT:\s*(.+)', section, re.IGNORECASE)
            
            if name_match:
                name = name_match.group(1).strip()
                title = title_match.group(1).strip() if title_match else None
                organization = org_match.group(1).strip() if org_match else None
                contact = contact_match.group(1).strip() if contact_match else None
                
                # Clean up values
                if title and title.lower() in ['not specified', 'none', 'n/a']:
                    title = None
                if organization and organization.lower() in ['not specified', 'none', 'n/a']:
                    organization = None
                if contact and contact.lower() in ['not available', 'none', 'n/a']:
                    contact = None
                
                person = PersonInfo(
                    name=name,
                    title=title,
                    organization=organization,
                    email=contact if contact and '@' in contact else None,
                    confidence=0.8  # AI extraction confidence
                )
                people.append(person)
        
        return people
    
    def _fallback_name_extraction(self, text: str) -> List[PersonInfo]:
        """
        Fallback name extraction using regex patterns
        
        Args:
            text: Text to analyze
            
        Returns:
            List of PersonInfo objects
        """
        people = []
        
        # Common name patterns
        name_patterns = [
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # First Last
            r'\b([A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+)\b',  # First M. Last
            r'\b(Dr\. [A-Z][a-z]+ [A-Z][a-z]+)\b',  # Dr. First Last
            r'\b(Prof\. [A-Z][a-z]+ [A-Z][a-z]+)\b',  # Prof. First Last
        ]
        
        for pattern in name_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1)
                
                # Skip if it's a common false positive
                if name.lower() in ['the company', 'the organization', 'the team']:
                    continue
                
                person = PersonInfo(
                    name=name,
                    confidence=0.5  # Lower confidence for regex extraction
                )
                people.append(person)
        
        return people
    
    def get_name_extraction_prompt(self) -> str:
        """
        Get the standard name extraction prompt for use in other services
        
        Returns:
            Standard name extraction prompt
        """
        return """
        IMPORTANT INSTRUCTION: Always extract and list all person names mentioned in the text, along with their titles and organizations. 
        
        For each person found, provide:
        - Full name
        - Title or role (if mentioned)
        - Organization or affiliation (if mentioned)
        - Contact information (if available)
        
        If no names are found, explicitly state "No person names found in the text."
        """
    
    def enhance_prompt_with_name_extraction(self, original_prompt: str) -> str:
        """
        Enhance an existing prompt with name extraction instructions
        
        Args:
            original_prompt: Original prompt text
            
        Returns:
            Enhanced prompt with name extraction instructions
        """
        return f"""
        {original_prompt}
        
        {self.get_name_extraction_prompt()}
        """

# Global instance
name_extraction_service = NameExtractionService() 