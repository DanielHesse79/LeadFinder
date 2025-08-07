"""
RunPod.ai Service for Enhanced AI Analysis

This module provides integration with RunPod.ai for enhanced AI analysis capabilities
in the Lead Workshop, offering more powerful models and better data processing.
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

try:
    from utils.logger import get_logger
    logger = get_logger('runpod_service')
except ImportError:
    logger = None

try:
    from config import config, RUNPOD_ENABLED, RUNPOD_AUTO_ENABLE, RUNPOD_BATCH_THRESHOLD, RUNPOD_COMPLEX_ANALYSIS, RUNPOD_FALLBACK_TO_OLLAMA
except ImportError:
    config = None
    RUNPOD_ENABLED = False
    RUNPOD_AUTO_ENABLE = True
    RUNPOD_BATCH_THRESHOLD = 5
    RUNPOD_COMPLEX_ANALYSIS = True
    RUNPOD_FALLBACK_TO_OLLAMA = True

@dataclass
class RunPodConfig:
    """Configuration for RunPod.ai integration"""
    api_key: str
    endpoint_id: str
    base_url: str = "https://api.runpod.ai/v2"
    timeout: int = 300  # 5 minutes timeout
    max_retries: int = 3
    retry_delay: int = 2

@dataclass
class AnalysisResult:
    """Result from RunPod.ai analysis"""
    success: bool
    analysis: str
    score: int
    people: str
    contact: str
    products: str
    company: str
    opportunities: str
    concerns: str
    raw_response: Dict[str, Any]
    processing_time: float
    model_used: str

class RunPodService:
    """
    Service for interacting with RunPod.ai for enhanced AI analysis
    """
    
    def __init__(self, config: RunPodConfig = None):
        self.config = config or self._load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        })
        
        if logger:
            logger.info(f"RunPod service initialized with endpoint: {self.config.endpoint_id}")
    
    def _load_config(self) -> RunPodConfig:
        """Load configuration from environment or config file"""
        if config:
            return RunPodConfig(
                api_key=config.get('RUNPOD_API_KEY', ''),
                endpoint_id=config.get('RUNPOD_ENDPOINT_ID', ''),
                base_url=config.get('RUNPOD_BASE_URL', 'https://api.runpod.ai/v2'),
                timeout=int(config.get('RUNPOD_TIMEOUT', '300')),
                max_retries=int(config.get('RUNPOD_MAX_RETRIES', '3')),
                retry_delay=int(config.get('RUNPOD_RETRY_DELAY', '2'))
            )
        else:
            import os
            return RunPodConfig(
                api_key=os.getenv('RUNPOD_API_KEY', ''),
                endpoint_id=os.getenv('RUNPOD_ENDPOINT_ID', ''),
                base_url=os.getenv('RUNPOD_BASE_URL', 'https://api.runpod.ai/v2'),
                timeout=int(os.getenv('RUNPOD_TIMEOUT', '300')),
                max_retries=int(os.getenv('RUNPOD_MAX_RETRIES', '3')),
                retry_delay=int(os.getenv('RUNPOD_RETRY_DELAY', '2'))
            )
    
    def is_available(self) -> bool:
        """Check if RunPod service is available and configured"""
        return bool(self.config.api_key and self.config.endpoint_id)
    
    def should_use_runpod(self, lead_count: int = 1, analysis_type: str = "standard") -> bool:
        """
        Smart decision making for when to use RunPod vs Ollama
        
        Args:
            lead_count: Number of leads to analyze
            analysis_type: Type of analysis ("standard", "complex", "batch")
            
        Returns:
            True if RunPod should be used, False for Ollama
        """
        # Check if RunPod is enabled globally
        if not RUNPOD_ENABLED:
            return False
        
        # Check if RunPod is available
        if not self.is_available():
            return False
        
        # Auto-enable for batch processing
        if RUNPOD_AUTO_ENABLE and lead_count >= RUNPOD_BATCH_THRESHOLD:
            if logger:
                logger.info(f"Auto-enabling RunPod for batch processing ({lead_count} leads)")
            return True
        
        # Use for complex analysis
        if RUNPOD_COMPLEX_ANALYSIS and analysis_type == "complex":
            if logger:
                logger.info("Using RunPod for complex analysis")
            return True
        
        # Default to Ollama for single leads and standard analysis
        return False
    
    def get_recommended_service(self, lead_count: int = 1, analysis_type: str = "standard") -> str:
        """
        Get recommended service for the given workload
        
        Args:
            lead_count: Number of leads to analyze
            analysis_type: Type of analysis
            
        Returns:
            "runpod" or "ollama"
        """
        if self.should_use_runpod(lead_count, analysis_type):
            return "runpod"
        else:
            return "ollama"
    
    def analyze_with_fallback(self, lead_data: Dict[str, Any], project_context: str = "", 
                            ollama_service=None) -> AnalysisResult:
        """
        Analyze lead with automatic fallback to Ollama if RunPod fails
        
        Args:
            lead_data: Lead information
            project_context: Project context
            ollama_service: Ollama service for fallback
            
        Returns:
            AnalysisResult from either RunPod or Ollama
        """
        # Try RunPod first if it should be used
        if self.should_use_runpod(1, "complex"):
            try:
                result = self.analyze_lead(lead_data, project_context)
                if result.success:
                    return result
                elif RUNPOD_FALLBACK_TO_OLLAMA and ollama_service:
                    if logger:
                        logger.warning("RunPod failed, falling back to Ollama")
                    return self._fallback_to_ollama(lead_data, project_context, ollama_service)
            except Exception as e:
                if logger:
                    logger.error(f"RunPod analysis failed: {e}")
                if RUNPOD_FALLBACK_TO_OLLAMA and ollama_service:
                    return self._fallback_to_ollama(lead_data, project_context, ollama_service)
        
        # Use Ollama directly if RunPod shouldn't be used or is not available
        if ollama_service:
            return self._fallback_to_ollama(lead_data, project_context, ollama_service)
        
        # Return error result if no service available
        return AnalysisResult(
            success=False,
            analysis="No AI service available",
            score=3,
            people="Not available",
            contact="Not available",
            products="Not available",
            company="Not available",
            opportunities="Not available",
            concerns="Not available",
            raw_response={},
            processing_time=0,
            model_used="none"
        )
    
    def _fallback_to_ollama(self, lead_data: Dict[str, Any], project_context: str, 
                           ollama_service) -> AnalysisResult:
        """Fallback to Ollama service"""
        try:
            # Create a simple prompt for Ollama
            prompt = f"""
            Analyze this lead for business opportunities:
            
            Title: {lead_data.get('title', 'N/A')}
            Description: {lead_data.get('description', 'N/A')}
            Link: {lead_data.get('link', 'N/A')}
            Source: {lead_data.get('source', 'N/A')}
            
            Project Context: {project_context if project_context else 'General analysis'}
            
            Provide a brief analysis with:
            - Relevancy score (1-5)
            - Key people mentioned
            - Contact information
            - Products/technologies
            - Company details
            - Opportunities
            - Concerns
            """
            
            start_time = time.time()
            response = ollama_service._call_ollama(prompt)
            processing_time = time.time() - start_time
            
            if response:
                return AnalysisResult(
                    success=True,
                    analysis=response,
                    score=3,  # Default score
                    people="Extracted from analysis",
                    contact="Extracted from analysis",
                    products="Extracted from analysis",
                    company="Extracted from analysis",
                    opportunities="Extracted from analysis",
                    concerns="Extracted from analysis",
                    raw_response={"ollama_response": response},
                    processing_time=processing_time,
                    model_used="ollama"
                )
            else:
                return AnalysisResult(
                    success=False,
                    analysis="Ollama analysis failed",
                    score=3,
                    people="Not available",
                    contact="Not available",
                    products="Not available",
                    company="Not available",
                    opportunities="Not available",
                    concerns="Not available",
                    raw_response={},
                    processing_time=processing_time,
                    model_used="ollama"
                )
        except Exception as e:
            if logger:
                logger.error(f"Ollama fallback failed: {e}")
            return AnalysisResult(
                success=False,
                analysis=f"Fallback analysis failed: {str(e)}",
                score=3,
                people="Not available",
                contact="Not available",
                products="Not available",
                company="Not available",
                opportunities="Not available",
                concerns="Not available",
                raw_response={},
                processing_time=0,
                model_used="none"
            )
    
    def analyze_lead(self, lead_data: Dict[str, Any], project_context: str = "") -> AnalysisResult:
        """
        Analyze a single lead using RunPod.ai
        
        Args:
            lead_data: Lead information (title, description, link, source)
            project_context: Project context for analysis
            
        Returns:
            AnalysisResult with comprehensive analysis
        """
        start_time = time.time()
        
        if not self.is_available():
            return AnalysisResult(
                success=False,
                analysis="RunPod service not available",
                score=3,
                people="Not available",
                contact="Not available",
                products="Not available",
                company="Not available",
                opportunities="Not available",
                concerns="Not available",
                raw_response={},
                processing_time=0,
                model_used="none"
            )
        
        # Create enhanced prompt for RunPod
        prompt = self._create_enhanced_prompt(lead_data, project_context)
        
        try:
            # Call RunPod API
            response = self._call_runpod_api(prompt)
            
            if response and response.get('success'):
                # Parse the response
                parsed_result = self._parse_analysis_response(response.get('output', ''))
                
                processing_time = time.time() - start_time
                
                return AnalysisResult(
                    success=True,
                    analysis=parsed_result.get('analysis', 'Analysis completed'),
                    score=parsed_result.get('score', 3),
                    people=parsed_result.get('people', 'Not available'),
                    contact=parsed_result.get('contact', 'Not available'),
                    products=parsed_result.get('products', 'Not available'),
                    company=parsed_result.get('company', 'Not available'),
                    opportunities=parsed_result.get('opportunities', 'Not available'),
                    concerns=parsed_result.get('concerns', 'Not available'),
                    raw_response=response,
                    processing_time=processing_time,
                    model_used=response.get('model', 'runpod')
                )
            else:
                return AnalysisResult(
                    success=False,
                    analysis=f"RunPod analysis failed: {response.get('error', 'Unknown error')}",
                    score=3,
                    people="Not available",
                    contact="Not available",
                    products="Not available",
                    company="Not available",
                    opportunities="Not available",
                    concerns="Not available",
                    raw_response=response or {},
                    processing_time=time.time() - start_time,
                    model_used="none"
                )
                
        except Exception as e:
            if logger:
                logger.error(f"RunPod analysis error: {e}")
            
            return AnalysisResult(
                success=False,
                analysis=f"RunPod analysis error: {str(e)}",
                score=3,
                people="Not available",
                contact="Not available",
                products="Not available",
                company="Not available",
                opportunities="Not available",
                concerns="Not available",
                raw_response={},
                processing_time=time.time() - start_time,
                model_used="none"
            )
    
    def analyze_multiple_leads(self, leads_data: List[Dict[str, Any]], project_context: str = "") -> List[AnalysisResult]:
        """
        Analyze multiple leads using RunPod.ai (batch processing)
        
        Args:
            leads_data: List of lead information
            project_context: Project context for analysis
            
        Returns:
            List of AnalysisResult objects
        """
        results = []
        
        for i, lead in enumerate(leads_data, 1):
            if logger:
                logger.info(f"RunPod analyzing lead {i}/{len(leads_data)}: {lead.get('title', 'Unknown')[:50]}...")
            
            result = self.analyze_lead(lead, project_context)
            results.append(result)
            
            # Add delay between requests to avoid rate limiting
            if i < len(leads_data):
                time.sleep(self.config.retry_delay)
        
        return results
    
    def _create_enhanced_prompt(self, lead_data: Dict[str, Any], project_context: str) -> str:
        """Create an enhanced prompt for RunPod analysis"""
        return f"""
        You are an expert business analyst specializing in lead evaluation and market research.
        
        PROJECT CONTEXT: {project_context if project_context else 'General lead analysis'}
        
        Analyze the following lead with maximum detail and precision:
        
        LEAD TITLE: {lead_data.get('title', 'N/A')}
        DESCRIPTION: {lead_data.get('description', 'N/A')}
        LINK: {lead_data.get('link', 'N/A')}
        SOURCE: {lead_data.get('source', 'N/A')}
        
        Provide a comprehensive analysis in the following structured format:
        
        SCORE: [1-5 relevancy score with detailed justification]
        PEOPLE: [Extract all names, titles, roles, organizations mentioned]
        CONTACT: [Extract all contact information: emails, phones, social media]
        PRODUCTS: [Extract product names, technologies, services mentioned]
        COMPANY: [Extract company information, size, industry, location]
        OPPORTUNITIES: [Identify potential collaboration, partnership, or business opportunities]
        CONCERNS: [Identify any red flags, risks, or concerns]
        ANALYSIS: [Comprehensive analysis with actionable insights and recommendations]
        
        Instructions:
        - Be extremely thorough and extract every possible detail
        - If information is not available, state "Not available" or "Unknown"
        - Focus on actionable business intelligence
        - Identify specific names, companies, products, and contact details
        - Provide concrete recommendations for follow-up actions
        - Consider market trends and competitive landscape
        - Evaluate the lead's potential value and fit
        """
    
    def _call_runpod_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call RunPod API with retry logic"""
        url = f"{self.config.base_url}/{self.config.endpoint_id}/run"
        
        payload = {
            "input": {
                "prompt": prompt
            }
        }
        
        for attempt in range(self.config.max_retries):
            try:
                if logger:
                    logger.info(f"RunPod API call attempt {attempt + 1}/{self.config.max_retries}")
                
                response = self.session.post(url, json=payload, timeout=self.config.timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if the job is completed
                    if result.get('status') == 'COMPLETED':
                        return {
                            'success': True,
                            'output': result.get('output', ''),
                            'model': 'runpod',
                            'job_id': result.get('id')
                        }
                    elif result.get('status') == 'IN_PROGRESS':
                        # Wait and poll for completion
                        job_id = result.get('id')
                        return self._poll_job_completion(job_id)
                    else:
                        return {
                            'success': False,
                            'error': f"Job status: {result.get('status')}",
                            'output': result.get('output', '')
                        }
                else:
                    if logger:
                        logger.error(f"RunPod API error: {response.status_code} - {response.text}")
                    
                    if attempt < self.config.max_retries - 1:
                        time.sleep(self.config.retry_delay * (attempt + 1))
                        continue
                    else:
                        return {
                            'success': False,
                            'error': f"API call failed: {response.status_code}",
                            'output': response.text
                        }
                        
            except requests.exceptions.Timeout:
                if logger:
                    logger.warning(f"RunPod API timeout on attempt {attempt + 1}")
                
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Request timeout',
                        'output': ''
                    }
                    
            except Exception as e:
                if logger:
                    logger.error(f"RunPod API exception: {e}")
                
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'output': ''
                    }
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'output': ''
        }
    
    def _poll_job_completion(self, job_id: str) -> Dict[str, Any]:
        """Poll for job completion"""
        url = f"{self.config.base_url}/{self.config.endpoint_id}/status/{job_id}"
        
        max_polls = 30  # Maximum 30 polls
        poll_interval = 2  # 2 seconds between polls
        
        for poll in range(max_polls):
            try:
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('status') == 'COMPLETED':
                        return {
                            'success': True,
                            'output': result.get('output', ''),
                            'model': 'runpod',
                            'job_id': job_id
                        }
                    elif result.get('status') == 'FAILED':
                        return {
                            'success': False,
                            'error': f"Job failed: {result.get('error', 'Unknown error')}",
                            'output': ''
                        }
                    else:
                        # Still in progress, wait and poll again
                        time.sleep(poll_interval)
                        continue
                else:
                    return {
                        'success': False,
                        'error': f"Status check failed: {response.status_code}",
                        'output': ''
                    }
                    
            except Exception as e:
                if logger:
                    logger.error(f"Job polling error: {e}")
                
                if poll < max_polls - 1:
                    time.sleep(poll_interval)
                    continue
                else:
                    return {
                        'success': False,
                        'error': f"Polling failed: {str(e)}",
                        'output': ''
                    }
        
        return {
            'success': False,
            'error': 'Job polling timeout',
            'output': ''
        }
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the analysis response from RunPod"""
        try:
            # Initialize default values
            parsed_data = {
                'score': 3,
                'people': 'Not available',
                'contact': 'Not available',
                'products': 'Not available',
                'company': 'Not available',
                'opportunities': 'Not available',
                'concerns': 'Not available',
                'analysis': 'Analysis completed'
            }
            
            # Extract score
            import re
            score_match = re.search(r'SCORE:\s*(\d+)', response_text, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                if 1 <= score <= 5:
                    parsed_data['score'] = score
            
            # Extract other fields
            fields = ['PEOPLE', 'CONTACT', 'PRODUCTS', 'COMPANY', 'OPPORTUNITIES', 'CONCERNS', 'ANALYSIS']
            
            for field in fields:
                pattern = rf'{field}:\s*(.*?)(?=\n[A-Z]+:|$)'
                match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    if value and value.lower() not in ['not available', 'unknown', 'none found', 'none identified']:
                        parsed_data[field.lower()] = value
            
            return parsed_data
            
        except Exception as e:
            if logger:
                logger.error(f"Error parsing RunPod response: {e}")
            
            return {
                'score': 3,
                'people': 'Not available',
                'contact': 'Not available',
                'products': 'Not available',
                'company': 'Not available',
                'opportunities': 'Not available',
                'concerns': 'Not available',
                'analysis': 'Analysis completed'
            }

# Global instance
runpod_service = RunPodService() 