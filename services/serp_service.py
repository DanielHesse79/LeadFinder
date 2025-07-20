import requests
from typing import List, Dict, Any

# Import config with fallbacks
try:
    from config import SERPAPI_KEY, SERP_ENGINES
except ImportError:
    SERPAPI_KEY = ''
    SERP_ENGINES = ["google"]

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

try:
    from utils.logger import get_logger
    logger = get_logger('serp_service')
except ImportError:
    logger = None

class SerpService:
    def __init__(self, api_key: str = SERPAPI_KEY):
        self.api_key = api_key
    
    def search(self, query: str, engines: List[str] = None, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search across multiple SERP engines
        
        Args:
            query: Search query
            engines: List of engines to search (default: ['google'])
            num_results: Number of results per engine
            
        Returns:
            List of search results
        """
        if engines is None:
            engines = ['google']
        
        all_results = []
        
        for engine in engines:
            if engine in SERP_ENGINES:
                results = self._search_engine(query, engine, num_results)
                all_results.extend(results)
            else:
                if logger:
                    logger.warning(f"Unknown engine: {engine}")
        
        return all_results
    
    def _search_engine(self, query: str, engine: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search a specific engine
        
        Args:
            query: Search query
            engine: Engine name
            num_results: Number of results
            
        Returns:
            List of search results
        """
        if logger:
            logger.info(f"Running {engine} search with query: '{query}'")
        
        if not GoogleSearch:
            if logger:
                logger.warning(f"GoogleSearch not available, skipping {engine} search")
            return []
        
        params = {
            "engine": engine,
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
            "hl": "en"
        }
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            organic = results.get('organic_results', [])
            if logger:
                logger.info(f"{engine} - Number of results: {len(organic)}")
            return organic
        except Exception as e:
            if logger:
                logger.error(f"Error searching {engine}: {e}")
            return []
    
    def get_available_engines(self) -> List[str]:
        """Get list of available SERP engines"""
        return SERP_ENGINES.copy()
    
    def validate_engine(self, engine: str) -> bool:
        """Validate if engine is supported"""
        return engine in SERP_ENGINES

# Global service instance
serp_service = SerpService() 