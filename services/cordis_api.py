"""
CORDIS API implementation

CORDIS (Community Research and Development Information Service) provides
information about EU-funded research projects and results.
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

class CORDISAPI(ResearchFundingAPI):
    """
    CORDIS API client for EU research funding data
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="CORDIS",
            base_url="https://cordis.europa.eu/api",
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
        Search for research projects in CORDIS
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of ResearchProject objects
        """
        self.logger.info(f"Searching CORDIS for: '{query}'")
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 50)
        
        # Try multiple CORDIS endpoints
        endpoints_to_try = [
            # Official CORDIS API endpoint
            "https://cordis.europa.eu/dataextractions/api/projects/search/en",
            # Alternative serverless API endpoint
            "https://5e5qfaxb1c.execute-api.eu-west-1.amazonaws.com/dev/graphql",
            # Fallback to base URL
            f"{self.base_url}/projects/search"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                if "graphql" in endpoint:
                    # Use GraphQL query for the serverless endpoint
                    return self._search_graphql(query, max_results_int, endpoint)
                else:
                    # Use REST API
                    return self._search_rest(query, max_results_int, endpoint)
            except Exception as e:
                self.logger.warning(f"Failed to search CORDIS via {endpoint}: {e}")
                continue
        
        # If all endpoints fail, use fallback
        self.logger.error("All CORDIS endpoints failed, using fallback")
        return self._fallback_search(query, max_results_int)
    
    def _search_rest(self, query: str, max_results: int, endpoint: str) -> List[ResearchProject]:
        """Search using REST API endpoint"""
        params = {
            'q': query,
            'num': max_results,
            'format': 'json'
        }
        
        headers = {
            'User-Agent': 'LeadFinder/1.0',
            'Accept': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        response = self.session.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            projects = self._parse_api_response(data, max_results)
            self.logger.info(f"Found {len(projects)} projects in CORDIS via {endpoint}")
            return projects
        else:
            raise Exception(f"API returned status {response.status_code}")
    
    def _search_graphql(self, query: str, max_results: int, endpoint: str) -> List[ResearchProject]:
        """Search using GraphQL endpoint"""
        # First try a simple introspection query to test the endpoint
        introspection_query = """
        query {
          __schema {
            types {
              name
            }
          }
        }
        """
        
        headers = {
            'User-Agent': 'LeadFinder/1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Test with introspection first
        payload = {
            "query": introspection_query
        }
        
        response = self.session.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            self.logger.info(f"GraphQL endpoint accessible, schema: {data}")
            
            # Try a simple search query
            search_query = """
            query {
              projects {
                id
                title
                description
              }
            }
            """
            
            payload = {
                "query": search_query
            }
            
            response = self.session.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'projects' in data['data']:
                    projects = []
                    for item in data['data']['projects']:
                        project = self._parse_graphql_project(item)
                        if project:
                            projects.append(project)
                    self.logger.info(f"Found {len(projects)} projects in CORDIS via GraphQL")
                    return projects[:max_results]
                else:
                    raise Exception(f"Invalid GraphQL response format: {data}")
            else:
                raise Exception(f"GraphQL search API returned status {response.status_code}")
        else:
            raise Exception(f"GraphQL introspection failed with status {response.status_code}")
    
    def _parse_graphql_project(self, item: Dict[str, Any]) -> Optional[ResearchProject]:
        """Parse GraphQL project response"""
        try:
            return ResearchProject(
                id=item.get('id', ''),
                title=item.get('title', ''),
                description=item.get('description', ''),
                principal_investigator=item.get('coordinator', {}).get('name', ''),
                organization=item.get('coordinator', {}).get('organization', ''),
                funding_amount=item.get('fundingAmount', 0),
                currency=item.get('currency', 'EUR'),
                start_date=datetime.fromisoformat(item.get('startDate', '')) if item.get('startDate') else None,
                end_date=datetime.fromisoformat(item.get('endDate', '')) if item.get('endDate') else None,
                keywords=item.get('keywords', []),
                source=self.name,
                url=item.get('url', ''),
                raw_data=item
            )
        except Exception as e:
            self.logger.error(f"Error parsing GraphQL project: {e}")
            return None
    
    def _fallback_search(self, query: str, max_results: int) -> List[ResearchProject]:
        """
        Fallback search method that returns mock data when API is unavailable
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of ResearchProject objects with mock data
        """
        self.logger.warning(f"Using fallback mock data for CORDIS search: '{query}'")
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 3)
        
        mock_projects = []
        for i in range(min(max_results_int, 3)):
            mock_project = ResearchProject(
                id=f"cordis_mock_{i+1}",
                title=f"CORDIS Mock Project {i+1}: {query}",
                description=f"This is mock data for CORDIS search. Query: {query}. This project demonstrates EU research funding in the area of {query}.",
                principal_investigator=f"Mock PI {i+1}",
                organization=f"Mock Institution {i+1}",
                funding_amount=500000 + (i * 100000),
                currency="EUR",
                start_date=None,
                end_date=None,
                keywords=[query, "mock", "fallback"],
                source=self.name,
                url=f"https://cordis.europa.eu/project/mock/{i+1}",
                raw_data={"is_mock": True}
            )
            mock_projects.append(mock_project)
        
        return mock_projects
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get API status and test connectivity
        
        Returns:
            Status dictionary with connection information
        """
        endpoints_to_test = [
            "https://cordis.europa.eu/dataextractions/api/projects/search/en",
            "https://5e5qfaxb1c.execute-api.eu-west-1.amazonaws.com/dev/graphql",
            f"{self.base_url}/projects/search"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                if "graphql" in endpoint:
                    # Test GraphQL endpoint
                    headers = {
                        'User-Agent': 'LeadFinder/1.0',
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                    
                    payload = {
                        "query": "query { __schema { types { name } } }"
                    }
                    
                    response = self.session.post(
                        endpoint,
                        json=payload,
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        return {
                            'name': self.name,
                            'base_url': endpoint,
                            'has_api_key': bool(self.api_key),
                            'status': 'ok',
                            'message': f'CORDIS GraphQL API is accessible via {endpoint}'
                        }
                else:
                    # Test REST endpoint
                    params = {
                        'q': 'test',
                        'num': 1,
                        'format': 'json'
                    }
                    headers = {
                        'User-Agent': 'LeadFinder/1.0',
                        'Accept': 'application/json'
                    }
                    if self.api_key:
                        headers['Authorization'] = f'Bearer {self.api_key}'
                    
                    response = self.session.get(
                        endpoint,
                        params=params,
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        return {
                            'name': self.name,
                            'base_url': endpoint,
                            'has_api_key': bool(self.api_key),
                            'status': 'ok',
                            'message': f'CORDIS REST API is accessible via {endpoint}'
                        }
                    elif response.status_code == 401:
                        return {
                            'name': self.name,
                            'base_url': endpoint,
                            'has_api_key': bool(self.api_key),
                            'status': 'error',
                            'error': 'API key authentication failed'
                        }
            except Exception as e:
                continue
        
        # If all endpoints fail
        return {
            'name': self.name,
            'base_url': self.base_url,
            'has_api_key': bool(self.api_key),
            'status': 'error',
            'error': 'All CORDIS endpoints are unreachable'
        }
    
    def _parse_api_response(self, data: Dict[str, Any], max_results: int) -> List[ResearchProject]:
        """
        Parse CORDIS API response into ResearchProject objects
        
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
            self.logger.warning(f"Unexpected CORDIS response format: {list(data.keys())}")
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
        Parse a single project item from CORDIS API
        
        Args:
            item: Raw project data from API
            
        Returns:
            ResearchProject object or None if parsing fails
        """
        try:
            # Extract project information with fallbacks
            project_id = str(item.get('id') or item.get('project_id') or item.get('rcn') or '')
            title = str(item.get('title') or item.get('project_title') or '')
            description = str(item.get('description') or item.get('abstract') or '')
            
            # Extract coordinator information
            coordinator_data = item.get('coordinator') or item.get('coordinating_organization') or {}
            if isinstance(coordinator_data, dict):
                org_name = coordinator_data.get('name', '')
            else:
                org_name = str(coordinator_data)
            
            # Extract funding information
            funding_data = item.get('funding') or {}
            if isinstance(funding_data, dict):
                amount = funding_data.get('amount')
                currency = funding_data.get('currency', 'EUR')
            else:
                amount = item.get('total_cost') or item.get('ec_contribution')
                currency = item.get('currency', 'EUR')
            
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
                principal_investigator=org_name,  # CORDIS uses coordinator as PI
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
            
            # Set up headers with API key
            headers = {
                'User-Agent': 'LeadFinder/1.0',
                'Accept': 'application/json'
            }
            
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = self.session.get(
                f"{self.base_url}/projects/{project_id}",
                params=params,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_project_item(data)
            else:
                self.logger.error(f"CORDIS API error for project {project_id}: {response.status_code}")
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
            currency=str(raw_data.get('currency', 'EUR')),
            start_date=self._parse_date(raw_data.get('start_date')),
            end_date=self._parse_date(raw_data.get('end_date')),
            keywords=raw_data.get('keywords', []),
            source=self.name,
            url=raw_data.get('url'),
            raw_data=raw_data
        ) 