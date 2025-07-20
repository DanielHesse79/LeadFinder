"""
Research Service Manager

This module manages multiple research funding APIs and provides a unified
interface for searching across all available databases.
"""

from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Import config with fallbacks
try:
    from config import RESEARCH_APIS, RESEARCH_MAX_RESULTS
except ImportError:
    RESEARCH_APIS = {}
    RESEARCH_MAX_RESULTS = 50

try:
    from services.api_base import ResearchProject, ResearchFundingAPI
except ImportError:
    ResearchProject = None
    ResearchFundingAPI = None

try:
    from services.swecris_api import SweCRISAPI
except ImportError:
    SweCRISAPI = None

try:
    from utils.logger import get_logger
except ImportError:
    def get_logger(name):
        import logging
        return logging.getLogger(name)

logger = get_logger('research_service')

class ResearchServiceManager:
    """
    Manages multiple research funding APIs and provides unified search functionality
    """
    
    def __init__(self):
        self.apis: Dict[str, ResearchFundingAPI] = {}
        self._initialize_apis()
    
    def _initialize_apis(self):
        """Initialize all enabled research APIs"""
        logger.info("Initializing research funding APIs...")
        
        if not RESEARCH_APIS:
            logger.warning("No research APIs configured")
            return
        
        for api_id, config in RESEARCH_APIS.items():
            if not config['enabled']:
                logger.info(f"Skipping disabled API: {config['name']}")
                continue
            
            try:
                if api_id == 'swecris' and SweCRISAPI:
                    api = SweCRISAPI(api_key=config['api_key'])
                    self.apis[api_id] = api
                    logger.info(f"Initialized {config['name']} API")
                elif api_id == 'cordis':
                    # Import CORDIS API
                    try:
                        from services.cordis_api import CORDISAPI
                        api = CORDISAPI(api_key=config['api_key'])
                        self.apis[api_id] = api
                        logger.info(f"Initialized {config['name']} API")
                    except ImportError:
                        logger.warning(f"CORDIS API not available")
                elif api_id == 'nih':
                    # Import NIH API
                    try:
                        from services.nih_api import NIHAPI
                        api = NIHAPI(api_key=config['api_key'])
                        self.apis[api_id] = api
                        logger.info(f"Initialized {config['name']} API")
                    except ImportError:
                        logger.warning(f"NIH API not available")
                elif api_id == 'nsf':
                    # Import NSF API
                    try:
                        from services.nsf_api import NSFAPI
                        api = NSFAPI(api_key=config['api_key'])
                        self.apis[api_id] = api
                        logger.info(f"Initialized {config['name']} API")
                    except ImportError:
                        logger.warning(f"NSF API not available")
                
            except Exception as e:
                logger.error(f"Failed to initialize {config['name']} API: {e}")
        
        logger.info(f"Initialized {len(self.apis)} research APIs")
    
    def search_all_apis(self, query: str, max_results_per_api: int = None) -> Dict[str, List[ResearchProject]]:
        """
        Search all enabled APIs concurrently
        
        Args:
            query: Search query string
            max_results_per_api: Maximum results per API (defaults to config)
            
        Returns:
            Dictionary mapping API names to lists of ResearchProject objects
        """
        if max_results_per_api is None:
            max_results_per_api = RESEARCH_MAX_RESULTS
        
        logger.info(f"Searching all APIs for: '{query}'")
        start_time = time.time()
        
        results = {}
        
        if not self.apis:
            logger.warning("No APIs available for search")
            return results
        
        # Use ThreadPoolExecutor for concurrent API calls
        with ThreadPoolExecutor(max_workers=len(self.apis)) as executor:
            # Submit search tasks
            future_to_api = {
                executor.submit(self._search_single_api, api_id, api, query, max_results_per_api): api_id
                for api_id, api in self.apis.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_api):
                api_id = future_to_api[future]
                try:
                    api_results = future.result()
                    results[api_id] = api_results
                    logger.info(f"Completed search for {api_id}: {len(api_results)} results")
                except Exception as e:
                    logger.error(f"Search failed for {api_id}: {e}")
                    results[api_id] = []
        
        total_time = time.time() - start_time
        total_results = sum(len(projects) for projects in results.values())
        logger.info(f"Search completed in {total_time:.2f}s: {total_results} total results")
        
        return results
    
    def _search_single_api(self, api_id: str, api: ResearchFundingAPI, 
                          query: str, max_results: int) -> List[ResearchProject]:
        """Search a single API with error handling"""
        try:
            return api.search(query, max_results)
        except Exception as e:
            logger.error(f"Error searching {api_id}: {e}")
            return []
    
    def get_all_projects(self, query: str, max_results_per_api: int = None) -> List[ResearchProject]:
        """
        Get all projects from all APIs as a single list
        
        Args:
            query: Search query string
            max_results_per_api: Maximum results per API
            
        Returns:
            Combined list of all ResearchProject objects
        """
        api_results = self.search_all_apis(query, max_results_per_api)
        
        all_projects = []
        for api_id, projects in api_results.items():
            all_projects.extend(projects)
        
        # Sort by funding amount (highest first) if available
        all_projects.sort(key=lambda p: p.funding_amount or 0, reverse=True)
        
        logger.info(f"Combined {len(all_projects)} projects from all APIs")
        return all_projects
    
    def get_api_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all APIs
        
        Returns:
            Dictionary with status information for each API
        """
        status = {}
        
        for api_id, api in self.apis.items():
            try:
                status[api_id] = api.get_status()
            except Exception as e:
                status[api_id] = {
                    'name': api.name,
                    'status': 'error',
                    'error': str(e)
                }
        
        return status
    
    def get_project_details(self, project_id: str, source: str) -> Optional[ResearchProject]:
        """
        Get detailed information about a specific project
        
        Args:
            project_id: Unique project identifier
            source: API source (e.g., 'swecris', 'cordis')
            
        Returns:
            ResearchProject object or None if not found
        """
        if source not in self.apis:
            logger.error(f"Unknown API source: {source}")
            return None
        
        try:
            return self.apis[source].get_project_details(project_id)
        except Exception as e:
            logger.error(f"Error getting project details for {project_id} from {source}: {e}")
            return None
    
    def get_available_apis(self) -> List[Dict[str, Any]]:
        """
        Get list of available APIs with their configuration
        
        Returns:
            List of API configuration dictionaries
        """
        available = []
        if not RESEARCH_APIS:
            return available
        for api_id, config in RESEARCH_APIS.items():
            enabled = config['enabled'] and bool(config['api_key'])
            api_info = {
                'id': api_id,
                'name': config['name'],
                'description': config['description'],
                'enabled': enabled,
                'has_api_key': bool(config['api_key']),
                'base_url': config['base_url'],
                'mock_only': False
            }
            # Add status if API is initialized
            if api_id in self.apis:
                api_info['status'] = self.apis[api_id].get_status()
            available.append(api_info)
        return available
    
    def search_by_filters(self, query: str, filters: Dict[str, Any]) -> List[ResearchProject]:
        """
        Search with additional filters (organization, funding range, etc.)
        
        Args:
            query: Search query string
            filters: Dictionary of filters to apply
            
        Returns:
            Filtered list of ResearchProject objects
        """
        all_projects = self.get_all_projects(query)
        
        # Apply filters
        filtered_projects = []
        
        for project in all_projects:
            # Organization filter
            if 'organization' in filters:
                org_filter = filters['organization'].lower()
                if org_filter not in project.organization.lower():
                    continue
            
            # Funding amount filter
            if 'min_funding' in filters and project.funding_amount:
                if project.funding_amount < filters['min_funding']:
                    continue
            
            if 'max_funding' in filters and project.funding_amount:
                if project.funding_amount > filters['max_funding']:
                    continue
            
            # Date range filter
            if 'start_date' in filters and project.start_date:
                if project.start_date < filters['start_date']:
                    continue
            
            if 'end_date' in filters and project.end_date:
                if project.end_date > filters['end_date']:
                    continue
            
            # Keyword filter
            if 'keywords' in filters:
                project_keywords = [k.lower() for k in project.keywords]
                filter_keywords = [k.lower() for k in filters['keywords']]
                if not any(fk in pk for fk in filter_keywords for pk in project_keywords):
                    continue
            
            filtered_projects.append(project)
        
        logger.info(f"Applied filters: {len(all_projects)} -> {len(filtered_projects)} projects")
        return filtered_projects

# Global service instance
research_service = ResearchServiceManager() 