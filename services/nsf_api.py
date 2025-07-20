import requests
from typing import List, Optional
from services.api_base import ResearchFundingAPI, ResearchProject
from datetime import datetime

class NSFAPI(ResearchFundingAPI):
    """
    Modern NSF API client using direct requests to the official NSF Award Search API
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="NSF",
            base_url="https://api.nsf.gov/services/v1/awards",
            api_key=api_key
        )

    def search(self, query: str, max_results: int = 50) -> List[ResearchProject]:
        """
        Search for NSF awards using the official API
        Based on: https://resources.research.gov/common/webapi/awardapisearch-v1.htm
        """
        # According to the documentation, the correct parameters are:
        # - keyword: Free text search
        # - rpp: Results per page (1-25, default 25)
        # - offset: Record offset (starts with 1)
        # - printFields: Comma separated output fields
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 25)
            
        params = {
            'keyword': query,
            'rpp': min(max_results_int, 25),  # API limit is 25 per page
            'offset': 1,
            'printFields': 'id,title,abstractText,piFirstName,piLastName,awardeeName,date,startDate,expDate,fundsObligatedAmt'
        }
        
        # Note: According to documentation, NSF API doesn't require API key for basic searches
        # API key is only needed for specific features
        
        try:
            response = requests.get(f"{self.base_url}.json", params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Handle both single award and multiple awards response format
            awards = data.get('response', {}).get('award', [])
            if not isinstance(awards, list):
                awards = [awards] if awards else []
            
            projects = []
            for award in awards:
                # Parse dates safely
                start_date = None
                end_date = None
                try:
                    if award.get('startDate'):
                        start_date = datetime.strptime(award.get('startDate'), '%m/%d/%Y')
                    if award.get('expDate'):
                        end_date = datetime.strptime(award.get('expDate'), '%m/%d/%Y')
                except ValueError:
                    self.logger.warning(f"Could not parse date for award {award.get('id')}")
                
                # Build PI name
                pi_first = award.get('piFirstName', '')
                pi_last = award.get('piLastName', '')
                pi_name = f"{pi_first} {pi_last}".strip()
                
                projects.append(ResearchProject(
                    id=award.get('id'),
                    title=award.get('title'),
                    description=award.get('abstractText', ''),
                    principal_investigator=pi_name,
                    organization=award.get('awardeeName', ''),
                    funding_amount=award.get('fundsObligatedAmt'),
                    currency='USD',
                    start_date=start_date,
                    end_date=end_date,
                    keywords=[query],
                    source=self.name,
                    url=f"https://www.nsf.gov/awardsearch/showAward?AWD_ID={award.get('id')}",
                    raw_data=award
                ))
            
            self.logger.info(f"NSF API search returned {len(projects)} results for query: '{query}'")
            return projects
            
        except Exception as e:
            self.logger.error(f"Error searching NSF API: {e}")
            return self._fallback_search(query, max_results)

    def _fallback_search(self, query: str, max_results: int) -> List[ResearchProject]:
        self.logger.warning(f"Using fallback mock data for NSF search: '{query}'")
        
        # Ensure max_results is an integer
        max_results_int = self._ensure_int(max_results, 3)
            
        mock_projects = []
        for i in range(min(max_results_int, 3)):
            mock_projects.append(ResearchProject(
                id=f"nsf_mock_{i+1}",
                title=f"NSF Mock Project {i+1}: {query}",
                description=f"This is mock data for NSF search. Query: {query}.",
                principal_investigator=f"Mock PI {i+1}",
                organization=f"Mock Institution {i+1}",
                funding_amount=100000 + (i * 50000),
                currency="USD",
                start_date=None,
                end_date=None,
                keywords=[query, "mock", "fallback"],
                source=self.name,
                url=f"https://www.nsf.gov/awardsearch/showAward?AWD_ID=mock{i+1}",
                raw_data={"mock": True, "query": query, "source": "fallback"}
            ))
        return mock_projects

    def get_project_details(self, project_id: str) -> Optional[ResearchProject]:
        """
        Get detailed information about a specific project
        
        Args:
            project_id: Project identifier
            
        Returns:
            ResearchProject object or None if not found
        """
        try:
            # This method is not yet implemented for the new NSFAPI
            # It will return None as a placeholder
            self.logger.warning(f"get_project_details not yet implemented for NSFAPI. Project ID: {project_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting NSF project details: {e}")
            return None 