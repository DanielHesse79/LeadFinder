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
    ORCID_BASE_URL = 'https://pub.orcid.org/v3.0'

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
        Search for researchers in ORCID using public API
        
        Args:
            query: Search query (name, institution, etc.)
            max_results: Maximum number of results
            
        Returns:
            List of researcher dictionaries
        """
        if logger:
            logger.info(f"Searching ORCID for researchers: {query}")
        
        try:
            # ORCID public API search endpoint
            search_url = f"{self.base_url}/expanded-search"
            params = {
                'q': query,
                'rows': min(max_results, 50)  # ORCID limit
            }
            
            response = self.session.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            researchers = []
            
            if 'expanded-result' in data:
                for result in data['expanded-result'][:max_results]:
                    orcid_id = result.get('orcid-id', '')
                    if orcid_id:
                        # Get detailed profile for each result
                        profile = self.get_researcher_profile(orcid_id)
                        if profile:
                            researchers.append(profile)
            
            if logger:
                logger.info(f"Found {len(researchers)} ORCID researchers")
            
            return researchers
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching ORCID: {e}")
            return []
    
    def get_researcher_profile(self, orcid_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed profile for a specific researcher using public API
        
        Args:
            orcid_id: ORCID identifier
            
        Returns:
            Researcher profile or None
        """
        if logger:
            logger.info(f"Getting ORCID profile for: {orcid_id}")
        
        try:
            # Clean ORCID ID format
            orcid_id = orcid_id.strip()
            if not re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$', orcid_id):
                if logger:
                    logger.warning(f"Invalid ORCID ID format: {orcid_id}")
                return None
            
            # Fetch profile from public API
            profile_url = f"{self.base_url}/{orcid_id}"
            response = self.session.get(profile_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract profile information
            profile = {
                'orcid': orcid_id,
                'url': f'https://orcid.org/{orcid_id}',
                'source': 'ORCID'
            }
            
            # Extract name
            if 'person' in data and 'name' in data['person']:
                name_data = data['person']['name']
                if 'given-names' in name_data and 'family-name' in name_data:
                    profile['name'] = f"{name_data['given-names']['value']} {name_data['family-name']['value']}"
                elif 'given-names' in name_data:
                    profile['name'] = name_data['given-names']['value']
                elif 'family-name' in name_data:
                    profile['name'] = name_data['family-name']['value']
            
            # Extract biography
            if 'person' in data and 'biography' in data['person']:
                bio_data = data['person']['biography']
                if bio_data and 'content' in bio_data:
                    profile['bio'] = bio_data['content']
            
            # Extract employment/affiliations
            if 'activities-summary' in data and 'employments' in data['activities-summary']:
                employments = data['activities-summary']['employments']
                if 'affiliation-group' in employments and employments['affiliation-group']:
                    # Get the most recent employment
                    employment = employments['affiliation-group'][0]['summaries'][0]['employment-summary']
                    profile['institution'] = employment['organization']['name']
                    if 'department-name' in employment:
                        profile['department'] = employment['department-name']
            
            # Extract research interests
            if 'person' in data and 'keywords' in data['person']:
                keywords_data = data['person']['keywords']
                if keywords_data and 'keyword' in keywords_data:
                    keywords = keywords_data['keyword']
                    if keywords:
                        profile['research_interests'] = ', '.join([k['content'] for k in keywords])
            
            # Extract email
            if 'person' in data and 'emails' in data['person']:
                emails_data = data['person']['emails']
                if emails_data and 'email' in emails_data:
                    emails = emails_data['email']
                    if emails:
                        profile['email'] = emails[0]['email']
            
            # Extract website
            if 'person' in data and 'researcher-urls' in data['person']:
                urls_data = data['person']['researcher-urls']
                if urls_data and 'researcher-url' in urls_data:
                    urls = urls_data['researcher-url']
                    if urls:
                        profile['website'] = urls[0]['url']['value']
            
            if logger:
                logger.info(f"Successfully retrieved ORCID profile for {orcid_id}")
            
            return profile
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting ORCID profile for {orcid_id}: {e}")
            return None
    
    def get_enhanced_profile(self, orcid_id: str) -> Optional[Dict[str, Any]]:
        """
        Get enhanced profile with publications, funding, and additional data
        
        Args:
            orcid_id: ORCID identifier
            
        Returns:
            Enhanced researcher profile or None
        """
        if logger:
            logger.info(f"Getting enhanced ORCID profile for: {orcid_id}")
        
        try:
            # Get basic profile first
            basic_profile = self.get_researcher_profile(orcid_id)
            if not basic_profile:
                return None
            
            # Clean ORCID ID format
            orcid_id = orcid_id.strip()
            if not re.match(r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$', orcid_id):
                if logger:
                    logger.warning(f"Invalid ORCID ID format: {orcid_id}")
                return None
            
            # Fetch enhanced profile from public API
            profile_url = f"{self.base_url}/{orcid_id}"
            response = self.session.get(profile_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            enhanced_profile = basic_profile.copy()
            
            # Extract publications
            publications = []
            if 'activities-summary' in data and 'works' in data['activities-summary']:
                works_data = data['activities-summary']['works']
                if 'group' in works_data:
                    for work_group in works_data['group']:
                        if 'work-summary' in work_group:
                            for work in work_group['work-summary']:
                                pub = {
                                    'id': work.get('put-code', ''),
                                    'title': work.get('title', {}).get('title', {}).get('value', ''),
                                    'authors': self._extract_authors(work),
                                    'journal': work.get('journal-title', {}).get('value', ''),
                                    'year': work.get('publication-date', {}).get('year', {}).get('value'),
                                    'doi': work.get('external-ids', {}).get('external-id', []),
                                    'url': work.get('url', {}).get('value', ''),
                                    'type': work.get('type', ''),
                                    'source': 'ORCID'
                                }
                                publications.append(pub)
            
            enhanced_profile['publications'] = publications
            
            # Extract funding information
            funding = []
            if 'activities-summary' in data and 'fundings' in data['activities-summary']:
                fundings_data = data['activities-summary']['fundings']
                if 'group' in fundings_data:
                    for funding_group in fundings_data['group']:
                        if 'funding-summary' in funding_group:
                            for fund in funding_group['funding-summary']:
                                funding_info = {
                                    'id': fund.get('put-code', ''),
                                    'title': fund.get('title', {}).get('title', {}).get('value', ''),
                                    'organization': fund.get('organization', {}).get('name', ''),
                                    'amount': fund.get('amount', {}).get('value', ''),
                                    'currency': fund.get('amount', {}).get('currency', ''),
                                    'start_date': fund.get('start-date', {}),
                                    'end_date': fund.get('end-date', {}),
                                    'type': fund.get('type', ''),
                                    'source': 'ORCID'
                                }
                                funding.append(funding_info)
            
            enhanced_profile['funding'] = funding
            
            # Extract additional keywords and research areas
            keywords = []
            if 'person' in data and 'keywords' in data['person']:
                keywords_data = data['person']['keywords']
                if keywords_data and 'keyword' in keywords_data:
                    keywords = [k['content'] for k in keywords_data['keyword']]
            
            enhanced_profile['keywords'] = keywords
            
            # Extract education history
            education = []
            if 'activities-summary' in data and 'educations' in data['activities-summary']:
                educations_data = data['activities-summary']['educations']
                if 'affiliation-group' in educations_data:
                    for edu_group in educations_data['affiliation-group']:
                        if 'summaries' in edu_group:
                            for edu in edu_group['summaries']:
                                education_info = {
                                    'institution': edu['education-summary']['organization']['name'],
                                    'department': edu['education-summary'].get('department-name', ''),
                                    'degree': edu['education-summary'].get('role-title', ''),
                                    'start_date': edu['education-summary'].get('start-date', {}),
                                    'end_date': edu['education-summary'].get('end-date', {}),
                                    'source': 'ORCID'
                                }
                                education.append(education_info)
            
            enhanced_profile['education'] = education
            
            # Extract peer review activities
            peer_reviews = []
            if 'activities-summary' in data and 'peer-reviews' in data['activities-summary']:
                reviews_data = data['activities-summary']['peer-reviews']
                if 'group' in reviews_data:
                    for review_group in reviews_data['group']:
                        if 'peer-review-summary' in review_group:
                            for review in review_group['peer-review-summary']:
                                review_info = {
                                    'id': review.get('put-code', ''),
                                    'journal': review.get('review-group-id', ''),
                                    'role': review.get('reviewer-role', ''),
                                    'subject': review.get('subject-container-name', {}).get('value', ''),
                                    'source': 'ORCID'
                                }
                                peer_reviews.append(review_info)
            
            enhanced_profile['peer_reviews'] = peer_reviews
            
            if logger:
                logger.info(f"Successfully retrieved enhanced ORCID profile for {orcid_id}")
            
            return enhanced_profile
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting enhanced ORCID profile for {orcid_id}: {e}")
            return None

    def _extract_authors(self, work: Dict[str, Any]) -> str:
        """Extract authors from work data"""
        try:
            if 'contributors' in work and 'contributor' in work['contributors']:
                contributors = work['contributors']['contributor']
                authors = []
                for contributor in contributors:
                    if 'credit-name' in contributor:
                        authors.append(contributor['credit-name']['value'])
                return ', '.join(authors)
            return ''
        except Exception:
            return ''

    def is_available(self) -> bool:
        """Check if ORCID service is available"""
        try:
            # Test with a known ORCID ID
            test_orcid = "0000-0002-1825-0097"  # Example ORCID
            response = self.session.get(f"{self.base_url}/{test_orcid}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            if logger:
                logger.error(f"ORCID service availability check failed: {e}")
            return False


# Global service instance
orcid_service = OrcidService() 