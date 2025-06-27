"""
SweCRIS API implementation

SweCRIS (Swedish Research Information System) provides information about
research projects funded by Swedish research councils and foundations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from services.api_base import ResearchFundingAPI, ResearchProject

class SweCRISAPI(ResearchFundingAPI):
    """
    SweCRIS API client for Swedish research funding data
    
    This implementation simulates data for demonstration purposes.
    In production, this would connect to the actual SweCRIS API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="SweCRIS",
            base_url="https://api.swecris.se/v1",
            api_key=api_key
        )
        
        # Simulated project data for demonstration
        self._mock_projects = self._generate_mock_projects()
    
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
        
        # Simulate API call delay
        import time
        time.sleep(0.5)
        
        # Filter mock projects based on query
        query_lower = query.lower()
        matching_projects = []
        
        for project in self._mock_projects:
            if (query_lower in project['title'].lower() or 
                query_lower in project['description'].lower() or
                any(query_lower in keyword.lower() for keyword in project['keywords'])):
                matching_projects.append(project)
        
        # Limit results
        matching_projects = matching_projects[:max_results]
        
        # Convert to ResearchProject objects
        projects = []
        for project_data in matching_projects:
            project = self.normalize_project_data(project_data)
            projects.append(project)
        
        self.logger.info(f"Found {len(projects)} projects in SweCRIS")
        return projects
    
    def get_project_details(self, project_id: str) -> Optional[ResearchProject]:
        """
        Get detailed information about a specific project
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            ResearchProject object or None if not found
        """
        self.logger.info(f"Getting project details for ID: {project_id}")
        
        # Find project in mock data
        for project_data in self._mock_projects:
            if project_data['id'] == project_id:
                return self.normalize_project_data(project_data)
        
        self.logger.warning(f"Project not found: {project_id}")
        return None
    
    def normalize_project_data(self, raw_data: Dict[str, Any]) -> ResearchProject:
        """
        Convert SweCRIS data to standardized ResearchProject format
        
        Args:
            raw_data: Raw data from SweCRIS API
            
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
    
    def _generate_mock_projects(self) -> List[Dict[str, Any]]:
        """Generate mock project data for demonstration"""
        
        organizations = [
            "Karolinska Institutet",
            "Uppsala universitet",
            "Lunds universitet",
            "Göteborgs universitet",
            "Stockholms universitet",
            "Umeå universitet",
            "Linköpings universitet",
            "Chalmers tekniska högskola",
            "KTH Royal Institute of Technology",
            "Örebro universitet"
        ]
        
        keywords_list = [
            ["epigenetik", "diabetes", "metabolism"],
            ["cancer", "onkologi", "behandling"],
            ["hjärna", "neurologi", "alzheimer"],
            ["hjärt-kärlsjukdomar", "kardiologi"],
            ["immunologi", "autoimmunitet"],
            ["mikrobiom", "tarmbakterier", "hälsa"],
            ["stamceller", "regenerativ medicin"],
            ["genetik", "DNA", "mutationer"],
            ["epidemiologi", "folkhälsa"],
            ["farmakologi", "läkemedel", "terapi"]
        ]
        
        projects = []
        
        for i in range(1, 101):  # Generate 100 mock projects
            keywords = random.choice(keywords_list)
            title_keyword = random.choice(keywords)
            
            project = {
                'id': f'swe-{i:06d}',
                'title': f'Forskning om {title_keyword} och dess påverkan på människors hälsa',
                'description': f'Detta projekt fokuserar på {title_keyword} och dess roll i mänsklig fysiologi. Projektet syftar till att förstå mekanismerna bakom {title_keyword} och utveckla nya behandlingsmetoder.',
                'principal_investigator': f'Dr. {random.choice(["Andersson", "Eriksson", "Johansson", "Nilsson", "Karlsson"])}',
                'organization': random.choice(organizations),
                'funding_amount': random.randint(500000, 5000000),
                'currency': 'SEK',
                'start_date': (datetime.now() - timedelta(days=random.randint(0, 1000))).strftime('%Y-%m-%d'),
                'end_date': (datetime.now() + timedelta(days=random.randint(365, 1460))).strftime('%Y-%m-%d'),
                'keywords': keywords,
                'url': f'https://swecris.se/project/{i:06d}',
                'funding_agency': random.choice(['Vetenskapsrådet', 'Forskningsrådet för hälsa', 'Cancerfonden', 'Hjärt-Lungfonden']),
                'project_type': random.choice(['Forskningsprojekt', 'Postdoktoralt projekt', 'Doktorandprojekt']),
                'status': random.choice(['Aktivt', 'Avslutat', 'Planerat'])
            }
            
            projects.append(project)
        
        return projects
    
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