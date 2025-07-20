import requests
from typing import List, Dict, Any, Optional
import re
from urllib.parse import quote_plus

# Import config with fallbacks
try:
    from config import ORCID_CLIENT_ID, ORCID_CLIENT_SECRET, ORCID_BASE_URL
except ImportError:
    ORCID_CLIENT_ID = ''
    ORCID_CLIENT_SECRET = ''
    ORCID_BASE_URL = 'https://orcid.org/oauth'

try:
    from utils.logger import get_logger
    logger = get_logger('orcid_service')
except ImportError:
    logger = None

class OrcidService:
    def __init__(self, client_id: str = ORCID_CLIENT_ID, 
                 client_secret: str = ORCID_CLIENT_SECRET, 
                 base_url: str = ORCID_BASE_URL):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LeadFinder/1.0',
            'Accept': 'application/json'
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
    
    def search_researchers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for researchers in ORCID
        
        Args:
            query: Search query (name, institution, etc.)
            max_results: Maximum number of results
            
        Returns:
            List of researcher dictionaries
        """
        if logger:
            logger.info(f"Searching ORCID for researchers: {query}")
        
        try:
            # Note: ORCID requires authentication for API access
            # This is a simplified implementation that would need proper OAuth setup
            
            # For now, return placeholder results with information about the limitation
            researchers = []
            
            # Ensure max_results is an integer
            max_results_int = self._ensure_int(max_results, 5)
            for i in range(min(max_results_int, 5)):
                researchers.append({
                    'name': f'Researcher for "{query}" (Placeholder {i+1})',
                    'institution': 'Sample University',
                    'bio': f'This is a placeholder for ORCID search results. To get real results, you would need to configure ORCID API credentials and implement OAuth authentication.',
                    'source': 'ORCID',
                    'orcid': f'0000-0000-0000-{i:04d}',
                    'url': f'https://orcid.org/0000-0000-0000-{i:04d}'
                })
            
            if logger:
                logger.info(f"Returned {len(researchers)} placeholder ORCID results")
            
            return researchers
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching ORCID: {e}")
            return []
    
    def get_researcher_profile(self, orcid_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed profile for a specific researcher
        
        Args:
            orcid_id: ORCID identifier
            
        Returns:
            Researcher profile or None
        """
        if logger:
            logger.info(f"Getting ORCID profile for: {orcid_id}")
        
        try:
            # This would implement the actual ORCID profile lookup
            # For now, return a placeholder
            return {
                'name': f'Researcher {orcid_id}',
                'institution': 'Sample University',
                'bio': 'This is a placeholder for ORCID profile lookup.',
                'source': 'ORCID',
                'orcid': orcid_id,
                'url': f'https://orcid.org/{orcid_id}'
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting ORCID profile for {orcid_id}: {e}")
            return None
    


# Global service instance
orcid_service = OrcidService() 