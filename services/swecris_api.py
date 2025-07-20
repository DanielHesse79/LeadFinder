"""
SweCRIS API implementation

SweCRIS (Swedish Research Information System) provides information about
research projects funded by Swedish research councils and foundations.
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

class SweCRISAPI(ResearchFundingAPI):
    """
    SweCRIS API client for Swedish research funding data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Use hardcoded public API key for SweCRIS
        api_key = api_key or "VRSwecrisAPI2025-1"
        
        super().__init__(
            name="SweCRIS",
            base_url="https://swecris-api.vr.se/v1",
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
        Search for research projects in SweCRIS
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of ResearchProject objects
        """
        self.logger.info(f"Searching SweCRIS for: '{query}'")
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 50)
        
        try:
            # Make API request to SweCRIS
            params = {
                'q': query,
                'limit': max_results_int,
                'format': 'json'
            }
            
            # Set up headers with API key - try different authentication methods
            headers = {
                'User-Agent': 'LeadFinder/1.0',
                'Accept': 'application/json'
            }
            
            if self.api_key:
                # Try different authentication header formats
                headers['X-API-Key'] = self.api_key
                # Alternative: headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = self.session.get(
                f"{self.base_url}/projects",
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                projects = self._parse_api_response(data, max_results)
                self.logger.info(f"Found {len(projects)} projects in SweCRIS")
                return projects
            elif response.status_code == 401:
                # Try alternative authentication
                self.logger.info("Trying alternative authentication for SweCRIS...")
                headers['Authorization'] = f'Bearer {self.api_key}'
                del headers['X-API-Key']
                
                response = self.session.get(
                    f"{self.base_url}/projects",
                    params=params,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    projects = self._parse_api_response(data, max_results)
                    self.logger.info(f"Found {len(projects)} projects in SweCRIS (alternative auth)")
                    return projects
                else:
                    self.logger.error(f"SweCRIS API error: {response.status_code} - {response.text}")
                    return self._fallback_search(query, max_results)
            else:
                self.logger.error(f"SweCRIS API error: {response.status_code} - {response.text}")
                return self._fallback_search(query, max_results)
                
        except Exception as e:
            self.logger.error(f"Error searching SweCRIS: {e}")
            return self._fallback_search(query, max_results)
    
    def _fallback_search(self, query: str, max_results: int) -> List[ResearchProject]:
        """
        Fallback search method that returns mock data when API is unavailable
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of ResearchProject objects with mock data
        """
        self.logger.warning(f"Using fallback mock data for SweCRIS search: '{query}'")
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 3)
        
        mock_projects = []
        for i in range(min(max_results_int, 3)):
            mock_project = ResearchProject(
                id=f"swecris_mock_{i+1}",
                title=f"SweCRIS Mock Project {i+1}: {query}",
                description=f"This is mock data for SweCRIS search. Query: {query}. This project demonstrates Swedish research funding in the area of {query}.",
                principal_investigator=f"Mock PI {i+1}",
                organization=f"Mock Institution {i+1}",
                funding_amount=300000 + (i * 50000),
                currency="SEK",
                start_date=None,
                end_date=None,
                keywords=[query, "mock", "fallback"],
                source=self.name,
                url=f"https://swecris-api.vr.se/project/mock/{i+1}",
                is_mock=True
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
                headers['X-API-Key'] = self.api_key
            
            # Test with a simple search query
            params = {
                'q': 'test',
                'limit': 1,
                'format': 'json'
            }
            
            response = self.session.get(
                f"{self.base_url}/projects",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'name': self.name,
                    'base_url': self.base_url,
                    'has_api_key': bool(self.api_key),
                    'status': 'ok',
                    'message': 'SweCRIS API is accessible'
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
        Parse SweCRIS API response into ResearchProject objects
        
        Args:
            data: Raw API response data
            max_results: Maximum number of results
            
        Returns:
            List of ResearchProject objects
        """
        projects = []
        
        # Handle different response formats
        if 'projects' in data:
            items = data['projects']
        elif 'results' in data:
            items = data['results']
        elif isinstance(data, list):
            items = data
        else:
            self.logger.warning(f"Unexpected SweCRIS response format: {list(data.keys())}")
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
        Parse a single project item from SweCRIS API
        
        Args:
            item: Raw project data from API
            
        Returns:
            ResearchProject object or None if parsing fails
        """
        try:
            # Extract project information with fallbacks
            project_id = str(item.get('id') or item.get('project_id') or '')
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
                currency = funding_data.get('currency', 'SEK')
            else:
                amount = item.get('funding_amount')
                currency = item.get('currency', 'SEK')
            
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
                self.logger.error(f"SweCRIS API error for project {project_id}: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting project details for {project_id}: {e}")
            return None
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check API health and connectivity
        
        Returns:
            Health status dictionary
        """
        try:
            # Try to connect to the API
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'message': 'SweCRIS API is accessible'
                }
            else:
                return {
                    'status': 'error',
                    'error': f'API returned status {response.status_code}',
                    'message': 'SweCRIS API is not responding correctly'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Cannot connect to SweCRIS API'
            }
    
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
            currency=str(raw_data.get('currency', 'SEK')),
            start_date=self._parse_date(raw_data.get('start_date')),
            end_date=self._parse_date(raw_data.get('end_date')),
            keywords=raw_data.get('keywords', []),
            source=self.name,
            url=raw_data.get('url'),
            raw_data=raw_data
        )
    
    def get_funding_agencies(self) -> List[str]:
        """Get list of available funding agencies"""
        return ['Vetenskapsrådet', 'Forskningsrådet för hälsa', 'Cancerfonden', 'Hjärt-Lungfonden']
    
    def search_by_agency(self, agency: str, max_results: int = 50) -> List[ResearchProject]:
        """Search projects by funding agency"""
        self.logger.info(f"Searching SweCRIS for agency: {agency}")
        
        matching_projects = [
            p for p in self._mock_projects 
            if agency.lower() in p.get('funding_agency', '').lower()
        ][:max_results]
        
        return [self.normalize_project_data(p) for p in matching_projects] 