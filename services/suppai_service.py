import requests
import time
from typing import List, Dict, Any, Optional
import re
from urllib.parse import quote_plus

try:
    from utils.logger import get_logger
    logger = get_logger('suppai_service')
except ImportError:
    logger = None

class SuppAIService:
    """SUPP.AI service for drug and supplement interactions"""
    
    def __init__(self):
        self.base_url = "https://supp.ai/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LeadFinder/1.0 (https://github.com/your-repo; mailto:your-email@example.com)'
        })
    
    def _ensure_int(self, value, default: int = 10) -> int:
        """
        Ensure a value is an integer, with fallback to default
        
        Args:
            value: Value to convert to int
            default: Default value if conversion fails
            
        Returns:
            Integer value
        """
        try:
            return int(value) if isinstance(value, str) else value
        except (ValueError, TypeError):
            return default
    
    def search_agents(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for drugs and supplements in SUPP.AI
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of agent dictionaries
        """
        if logger:
            logger.info(f"Searching SUPP.AI for: {query}")
        
        try:
            params = {
                'q': query,
                'p': 0  # Start with first page
            }
            
            response = self.session.get(f"{self.base_url}/agent/search", params=params, timeout=30)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"SUPP.AI search failed: {response.status_code}")
                return self._fallback_search(query, max_results)
            
            data = response.json()
            results = data.get('results', [])
            
            if logger:
                logger.info(f"Found {len(results)} SUPP.AI results")
            
            # Convert to our format
            agents = []
            for result in results[:max_results]:
                agent = self._parse_agent_result(result)
                if agent:
                    agents.append(agent)
            
            return agents
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching SUPP.AI: {e}")
            return self._fallback_search(query, max_results)
    
    def get_agent_details(self, cui: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific agent
        
        Args:
            cui: Agent CUI identifier
            
        Returns:
            Agent details or None
        """
        if logger:
            logger.info(f"Getting SUPP.AI agent details for: {cui}")
        
        try:
            response = self.session.get(f"{self.base_url}/agent/{cui}", timeout=30)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"Failed to get agent details: {response.status_code}")
                return None
            
            agent_data = response.json()
            return self._parse_agent_result(agent_data)
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting SUPP.AI agent details: {e}")
            return None
    
    def get_agent_interactions(self, cui: str, page: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get interactions for a specific agent
        
        Args:
            cui: Agent CUI identifier
            page: Page number (starts from 1)
            
        Returns:
            Interactions data or None
        """
        if logger:
            logger.info(f"Getting SUPP.AI interactions for: {cui}, page: {page}")
        
        try:
            params = {'p': page}
            response = self.session.get(f"{self.base_url}/agent/{cui}/interactions", params=params, timeout=30)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"Failed to get interactions: {response.status_code}")
                return None
            
            data = response.json()
            
            # Parse interactions
            interactions = []
            for interaction in data.get('interactions', []):
                parsed_interaction = self._parse_interaction(interaction)
                if parsed_interaction:
                    interactions.append(parsed_interaction)
            
            return {
                'page': data.get('page', page),
                'interactions': interactions,
                'interactions_per_page': data.get('interactions_per_page', 50),
                'total': data.get('total', 0)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting SUPP.AI interactions: {e}")
            return None
    
    def get_interaction_evidence(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get evidence for a specific interaction
        
        Args:
            interaction_id: Interaction ID (format: CUI1-CUI2)
            
        Returns:
            Interaction evidence or None
        """
        if logger:
            logger.info(f"Getting SUPP.AI interaction evidence for: {interaction_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/interaction/{interaction_id}", timeout=30)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"Failed to get interaction evidence: {response.status_code}")
                return None
            
            data = response.json()
            
            # Parse evidence
            evidence_list = []
            for evidence in data.get('evidence', []):
                parsed_evidence = self._parse_evidence(evidence)
                if parsed_evidence:
                    evidence_list.append(parsed_evidence)
            
            return {
                'interaction_id': data.get('interaction_id', interaction_id),
                'slug': data.get('slug', ''),
                'agents': data.get('agents', []),
                'evidence': evidence_list
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting SUPP.AI interaction evidence: {e}")
            return None
    
    def _parse_agent_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a SUPP.AI agent result
        
        Args:
            result: Raw result from SUPP.AI API
            
        Returns:
            Parsed agent dictionary or None
        """
        try:
            cui = result.get('cui', '')
            preferred_name = result.get('preferred_name', '')
            synonyms = result.get('synonyms', [])
            tradenames = result.get('tradenames', [])
            definition = result.get('definition', '')
            ent_type = result.get('ent_type', '')
            interacts_with_count = result.get('interacts_with_count', 0)
            slug = result.get('slug', '')
            
            agent = {
                'cui': cui,
                'name': preferred_name,
                'synonyms': synonyms,
                'tradenames': tradenames,
                'definition': definition,
                'type': ent_type,
                'interactions_count': interacts_with_count,
                'slug': slug,
                'source': 'SUPP.AI',
                'url': f"https://supp.ai/agent/{slug}" if slug else None
            }
            
            return agent
            
        except Exception as e:
            if logger:
                logger.warning(f"Error parsing SUPP.AI agent result: {e}")
            return None
    
    def _parse_interaction(self, interaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a SUPP.AI interaction
        
        Args:
            interaction: Raw interaction from SUPP.AI API
            
        Returns:
            Parsed interaction dictionary or None
        """
        try:
            interaction_id = interaction.get('interaction_id', '')
            slug = interaction.get('slug', '')
            agent = interaction.get('agent', {})
            evidence = interaction.get('evidence', [])
            
            return {
                'interaction_id': interaction_id,
                'slug': slug,
                'agent': self._parse_agent_result(agent) if agent else None,
                'evidence_count': len(evidence),
                'url': f"https://supp.ai/interaction/{slug}" if slug else None
            }
            
        except Exception as e:
            if logger:
                logger.warning(f"Error parsing SUPP.AI interaction: {e}")
            return None
    
    def _parse_evidence(self, evidence: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse SUPP.AI evidence
        
        Args:
            evidence: Raw evidence from SUPP.AI API
            
        Returns:
            Parsed evidence dictionary or None
        """
        try:
            paper = evidence.get('paper', {})
            sentences = evidence.get('sentences', [])
            
            # Parse paper information
            paper_info = {
                'pid': paper.get('pid', ''),
                'title': paper.get('title', ''),
                'authors': paper.get('authors', []),
                'year': paper.get('year', ''),
                'venue': paper.get('venue', ''),
                'doi': paper.get('doi', ''),
                'pmid': paper.get('pmid', ''),
                'fields_of_study': paper.get('fields_of_study', []),
                'animal_study': paper.get('animal_study', False),
                'human_study': paper.get('human_study', False),
                'clinical_study': paper.get('clinical_study', False),
                'retraction': paper.get('retraction', False)
            }
            
            # Parse sentences
            parsed_sentences = []
            for sentence in sentences:
                parsed_sentence = {
                    'uid': sentence.get('uid', ''),
                    'confidence': sentence.get('confidence', ''),
                    'paper_id': sentence.get('paper_id', ''),
                    'sentence_id': sentence.get('sentence_id', ''),
                    'spans': sentence.get('spans', [])
                }
                parsed_sentences.append(parsed_sentence)
            
            return {
                'paper': paper_info,
                'sentences': parsed_sentences
            }
            
        except Exception as e:
            if logger:
                logger.warning(f"Error parsing SUPP.AI evidence: {e}")
            return None
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check SUPP.AI API health status
        
        Returns:
            Health status dictionary
        """
        if logger:
            logger.info("Checking SUPP.AI API health")
        
        try:
            # Try a simple search to test API connectivity
            response = self.session.get(f"{self.base_url}/agent/search", params={'q': 'test', 'p': 0}, timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'message': 'SUPP.AI API is responding correctly',
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': f'SUPP.AI API returned status {response.status_code}',
                    'timestamp': time.time()
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'message': 'SUPP.AI API request timed out',
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'SUPP.AI API error: {str(e)}',
                'timestamp': time.time()
            }
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Fallback search when API is not available
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of placeholder agent dictionaries
        """
        if logger:
            logger.info("Using fallback SUPP.AI search")
        
        agents = []
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 5)
        for i in range(min(max_results_int, 5)):
            agents.append({
                'cui': f'C{i:07d}',
                'name': f'SUPP.AI result for "{query}" (Placeholder {i+1})',
                'synonyms': ['Sample Synonym'],
                'tradenames': [],
                'definition': f'This is a placeholder for SUPP.AI search results. SUPP.AI provides comprehensive drug and supplement interaction data.',
                'type': 'supplement' if i % 2 == 0 else 'drug',
                'interactions_count': 0,
                'slug': f'placeholder-{i}',
                'source': 'SUPP.AI',
                'url': f'https://supp.ai/search?q={quote_plus(query)}'
            })
        
        return agents

# Global service instance
suppai_service = SuppAIService() 