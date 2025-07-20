"""
NIH RePORTER API implementation

NIH RePORTER provides information about research projects funded by the
US National Institutes of Health.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from services.api_base import ResearchFundingAPI, ResearchProject

try:
    from utils.performance import get_session
except ImportError:
    get_session = None

try:
    from utils.logger import get_logger
except ImportError:
    def get_logger(name):
        import logging
        return logging.getLogger(name)

class NIHAPI(ResearchFundingAPI):
    """
    NIH RePORTER API client for US research funding data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="NIH RePORTER",
            base_url="https://api.reporter.nih.gov/v2",
            api_key=api_key
        )
        
        # Use optimized session if available
        if get_session:
            self.session = get_session()
            # Create a new session for headers if optimized session doesn't support them
            if not hasattr(self.session, 'headers'):
                self.session = requests.Session()
        else:
            self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'LeadFinder/1.0',
            'Accept': 'application/json'
        })
    
    def search(self, query: str, max_results: int = 50) -> List[ResearchProject]:
        """
        Search for research projects in NIH RePORTER
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of ResearchProject objects
        """
        self.logger.info(f"Searching NIH RePORTER for: '{query}'")
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 50)
        
        try:
            # Make API request to NIH RePORTER
            params = {
                'query': query,
                'limit': max_results_int,
                'format': 'json'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            # NIH RePORTER v2 API uses POST with JSON body
            search_request = {
                "criteria": {
                    "search_text": query,
                    "limit": max_results_int
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = self.session.post(
                f"{self.base_url}/projects/search",
                json=search_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                projects = self._parse_api_response(data, max_results_int)
                self.logger.info(f"Found {len(projects)} projects in NIH RePORTER")
                return projects
            else:
                self.logger.error(f"NIH API error: {response.status_code} - {response.text}")
                return self._fallback_search(query, max_results_int)
                
        except Exception as e:
            self.logger.error(f"Error searching NIH RePORTER: {e}")
            return self._fallback_search(query, max_results_int)
    
    def _fallback_search(self, query: str, max_results: int) -> List[ResearchProject]:
        """
        Fallback search with mock data when API fails
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            
        Returns:
            List of ResearchProject objects with mock data
        """
        self.logger.warning(f"Using fallback mock data for NIH search: '{query}'")
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 5)
        
        # Generate mock projects based on query
        mock_projects = []
        for i in range(min(max_results_int, 5)):  # Max 5 mock results
            mock_project = ResearchProject(
                id=f"mock_nih_{i+1}",
                title=f"NIH Mock Project {i+1}: {query}",
                description=f"This is mock data for the search '{query}' from NIH RePORTER. Real API data would be shown here.",
                principal_investigator=f"Mock PI {i+1}",
                organization=f"Mock Institution {i+1}",
                funding_amount=750000 + (i * 150000),
                currency="USD",
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=1095),
                keywords=[query, "mock", "nih", "us"],
                source=self.name,
                url=f"https://reporter.nih.gov/mock/{i+1}",
                raw_data={"mock": True, "query": query}
            )
            mock_projects.append(mock_project)
        
        return mock_projects
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get API status and test connectivity
        
        Returns:
            Status dictionary with connection information
        """
        try:
            # Test API connectivity with a simple search request
            headers = {
                'User-Agent': 'LeadFinder/1.0',
                'Accept': 'application/json'
            }
            
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Test with a simple search request
            search_request = {
                "criteria": {
                    "search_text": "test",
                    "limit": 1
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/projects/search",
                json=search_request,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'name': self.name,
                    'base_url': self.base_url,
                    'has_api_key': bool(self.api_key),
                    'status': 'ok',
                    'message': 'NIH RePORTER API is accessible'
                }
            elif response.status_code == 401:
                return {
                    'name': self.name,
                    'base_url': self.base_url,
                    'has_api_key': bool(self.api_key),
                    'status': 'error',
                    'error': 'API key authentication failed'
                }
            else:
                return {
                    'name': self.name,
                    'base_url': self.base_url,
                    'has_api_key': bool(self.api_key),
                    'status': 'error',
                    'error': f'API returned status {response.status_code}'
                }
                
        except Exception as e:
            return {
                'name': self.name,
                'base_url': self.base_url,
                'has_api_key': bool(self.api_key),
                'status': 'error',
                'error': str(e)
            }
    
    def _parse_api_response(self, data: Dict[str, Any], max_results: int) -> List[ResearchProject]:
        """
        Parse NIH RePORTER API response into ResearchProject objects
        
        Args:
            data: Raw API response data
            max_results: Maximum number of results
            
        Returns:
            List of ResearchProject objects
        """
        projects = []
        
        # Handle different response formats
        if 'results' in data:
            items = data['results']
        elif 'projects' in data:
            items = data['projects']
        elif isinstance(data, list):
            items = data
        else:
            self.logger.warning(f"Unexpected NIH response format: {list(data.keys())}")
            return []
        
        for item in items[:max_results]:
            try:
                project = self._parse_project_item(item)
                if project:
                    projects.append(project)
            except Exception as e:
                self.logger.warning(f"Error parsing project item: {e}")
                continue
        
        return projects
    
    def _parse_project_item(self, item: Dict[str, Any]) -> Optional[ResearchProject]:
        """
        Parse a single project item from NIH RePORTER API
        
        Args:
            item: Raw project data from API
            
        Returns:
            ResearchProject object or None if parsing fails
        """
        try:
            # Extract project information with fallbacks
            project_id = str(item.get('id') or item.get('project_id') or item.get('application_id') or '')
            title = str(item.get('title') or item.get('project_title') or '')
            description = str(item.get('description') or item.get('abstract') or '')
            
            # Extract PI information
            pi_data = item.get('principal_investigator') or item.get('pi') or {}
            if isinstance(pi_data, dict):
                pi_name = pi_data.get('name', '')
            else:
                pi_name = str(pi_data)
            
            # Extract organization
            org_data = item.get('organization') or item.get('institution') or {}
            if isinstance(org_data, dict):
                org_name = org_data.get('name', '')
            else:
                org_name = str(org_data)
            
            # Extract funding information
            funding_data = item.get('funding') or {}
            if isinstance(funding_data, dict):
                amount = funding_data.get('amount')
                currency = funding_data.get('currency', 'USD')
            else:
                amount = item.get('total_cost') or item.get('nih_funding')
                currency = item.get('currency', 'USD')
            
            # Parse dates
            start_date = self._parse_date(item.get('start_date') or item.get('project_start'))
            end_date = self._parse_date(item.get('end_date') or item.get('project_end'))
            
            # Extract keywords
            keywords = []
            if 'keywords' in item:
                if isinstance(item['keywords'], list):
                    keywords = item['keywords']
                elif isinstance(item['keywords'], str):
                    keywords = [k.strip() for k in item['keywords'].split(',')]
            
            # Extract URL
            url = item.get('url') or item.get('project_url') or ''
            
            return ResearchProject(
                id=project_id,
                title=title,
                description=description,
                principal_investigator=pi_name,
                organization=org_name,
                funding_amount=float(amount) if amount else None,
                currency=currency,
                start_date=start_date,
                end_date=end_date,
                keywords=keywords,
                source=self.name,
                url=url,
                raw_data=item
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing project item: {e}")
            return None
    

    
    def get_project_details(self, project_id: str) -> Optional[ResearchProject]:
        """
        Get detailed information about a specific project
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            ResearchProject object or None if not found
        """
        self.logger.info(f"Getting project details for ID: {project_id}")
        
        try:
            params = {'format': 'json'}
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = self.session.get(
                f"{self.base_url}/projects/{project_id}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_project_item(data)
            else:
                self.logger.error(f"NIH API error for project {project_id}: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting project details for {project_id}: {e}")
            return None
    
    def normalize_project_data(self, raw_data: Dict[str, Any]) -> ResearchProject:
        """
        Convert raw data to standardized ResearchProject format
        
        Args:
            raw_data: Raw project data
            
        Returns:
            Standardized ResearchProject object
        """
        return ResearchProject(
            id=str(raw_data.get('id', '')),
            title=str(raw_data.get('title', '')),
            description=str(raw_data.get('description', '')),
            principal_investigator=str(raw_data.get('principal_investigator', '')),
            organization=str(raw_data.get('organization', '')),
            funding_amount=float(raw_data.get('funding_amount', 0)) if raw_data.get('funding_amount') else None,
            currency=str(raw_data.get('currency', 'USD')),
            start_date=self._parse_date(raw_data.get('start_date')),
            end_date=self._parse_date(raw_data.get('end_date')),
            keywords=raw_data.get('keywords', []),
            source=self.name,
            url=raw_data.get('url'),
            raw_data=raw_data
        ) 