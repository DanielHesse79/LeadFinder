import requests
from typing import List, Dict, Any, Optional
import re
from urllib.parse import quote_plus

try:
    from utils.logger import get_logger
    logger = get_logger('semantic_scholar_service')
except ImportError:
    logger = None

try:
    from config import SEMANTIC_SCHOLAR_API_KEY
except ImportError:
    SEMANTIC_SCHOLAR_API_KEY = ''

class SemanticScholarService:
    """Semantic Scholar service for academic article search"""
    
    def __init__(self, api_key: str = SEMANTIC_SCHOLAR_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LeadFinder/1.0 (https://github.com/your-repo; mailto:your-email@example.com)'
        })
        
        # Add API key to headers if available
        if self.api_key:
            self.session.headers.update({
                'x-api-key': self.api_key
            })
            if logger:
                logger.info("Semantic Scholar API key configured")
        else:
            if logger:
                logger.warning("Semantic Scholar API key not configured - will use fallback mode")
    
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
    
    def search_articles(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for academic articles in Semantic Scholar
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of article dictionaries
        """
        if logger:
            logger.info(f"Searching Semantic Scholar for: {query}")
        
        try:
            # Ensure max_results is an integer
            max_results_int = self._ensure_int(max_results, 100)
            
            # Search parameters
            params = {
                'query': query,
                'limit': min(max_results_int, 100),  # API limit
                'fields': 'paperId,title,abstract,authors,year,venue,url,doi,citationCount,openAccessPdf'
            }
            
            response = self.session.get(f"{self.base_url}/paper/search", params=params, timeout=30)
            
            if response.status_code != 200:
                if logger:
                    if response.status_code == 403:
                        logger.error(f"Semantic Scholar search failed: 403 Forbidden - API key may be invalid or missing")
                    elif response.status_code == 401:
                        logger.error(f"Semantic Scholar search failed: 401 Unauthorized - API key required")
                    else:
                        logger.error(f"Semantic Scholar search failed: {response.status_code}")
                return self._fallback_search(query, max_results)
            
            data = response.json()
            papers = data.get('data', [])
            
            if logger:
                logger.info(f"Found {len(papers)} Semantic Scholar results")
            
            # Convert to our format
            articles = []
            for paper in papers[:max_results]:
                article = self._parse_semantic_result(paper)
                if article:
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching Semantic Scholar: {e}")
            return self._fallback_search(query, max_results)
    
    def _parse_semantic_result(self, paper: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a Semantic Scholar result
        
        Args:
            paper: Raw result from Semantic Scholar API
            
        Returns:
            Parsed article dictionary or None
        """
        try:
            title = paper.get('title', '')
            abstract = paper.get('abstract', '')
            paper_id = paper.get('paperId', '')
            
            # Extract authors
            authors_data = paper.get('authors', [])
            authors = [author.get('name', 'Unknown Author') for author in authors_data]
            
            # Extract venue (journal/conference)
            venue = paper.get('venue', '')
            
            # Extract year
            year = paper.get('year', '')
            
            # Extract DOI
            doi = paper.get('doi', '')
            
            # Extract citation count
            citations = paper.get('citationCount', 0)
            
            # Extract URLs
            url = paper.get('url', '')
            open_access_pdf = paper.get('openAccessPdf', {}).get('url', '')
            
            # Generate URL if not provided
            if not url and paper_id:
                url = f"https://www.semanticscholar.org/paper/{paper_id}"
            
            article = {
                'title': title,
                'authors': authors if authors else ['Unknown Author'],
                'abstract': abstract,
                'source': 'Semantic Scholar',
                'year': str(year) if year else 'Unknown',
                'journal': venue or 'Unknown Journal',
                'url': url,
                'doi': doi,
                'citations': citations,
                'pdf_url': open_access_pdf
            }
            
            return article
            
        except Exception as e:
            if logger:
                logger.warning(f"Error parsing Semantic Scholar result: {e}")
            return None
    
    def get_article_details(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific article
        
        Args:
            paper_id: Semantic Scholar paper ID
            
        Returns:
            Article details or None
        """
        if logger:
            logger.info(f"Getting Semantic Scholar article details for: {paper_id}")
        
        try:
            params = {
                'fields': 'paperId,title,abstract,authors,year,venue,url,doi,citationCount,openAccessPdf,references,citations'
            }
            
            response = self.session.get(f"{self.base_url}/paper/{paper_id}", params=params, timeout=30)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"Failed to get article details: {response.status_code}")
                return None
            
            paper = response.json()
            return self._parse_semantic_result(paper)
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting Semantic Scholar article details: {e}")
            return None
    
    def search_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Search for an article by DOI
        
        Args:
            doi: DOI of the article
            
        Returns:
            Article details or None
        """
        if logger:
            logger.info(f"Searching Semantic Scholar by DOI: {doi}")
        
        try:
            params = {
                'fields': 'paperId,title,abstract,authors,year,venue,url,doi,citationCount,openAccessPdf'
            }
            
            response = self.session.get(f"{self.base_url}/paper/DOI:{doi}", params=params, timeout=30)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"Failed to find article by DOI: {response.status_code}")
                return None
            
            paper = response.json()
            return self._parse_semantic_result(paper)
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching by DOI: {e}")
            return None
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Fallback search when API is not available
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of placeholder article dictionaries
        """
        if logger:
            logger.info("Using fallback Semantic Scholar search - API key not configured")
        
        articles = []
        
        # Create informative placeholder articles
        placeholder_articles = [
            {
                'title': f'🔑 Semantic Scholar API Key Required',
                'authors': ['LeadFinder System'],
                'abstract': f'To get real Semantic Scholar results for "{query}", you need to configure a Semantic Scholar API key. Go to https://www.semanticscholar.org/product/api to get a free API key, then add SEMANTIC_SCHOLAR_API_KEY=your_key_here to your env.development file.',
                'source': 'Semantic Scholar',
                'year': '2024',
                'journal': 'Configuration Required',
                'url': 'https://www.semanticscholar.org/product/api',
                'doi': '',
                'citations': 0,
                'pdf_url': None
            },
            {
                'title': f'📚 Sample Semantic Scholar Result for "{query}"',
                'authors': ['Example Author 1', 'Example Author 2'],
                'abstract': f'This is a sample result showing what Semantic Scholar would return for "{query}". With a proper API key, you would see real academic papers with titles, authors, abstracts, and citation counts.',
                'source': 'Semantic Scholar',
                'year': '2024',
                'journal': 'Example Journal',
                'url': f'https://www.semanticscholar.org/search?q={quote_plus(query)}',
                'doi': '10.1234/example.doi',
                'citations': 42,
                'pdf_url': None
            }
        ]
        
        # Return informative placeholders
        return placeholder_articles[:min(max_results, len(placeholder_articles))]

# Global service instance
semantic_scholar_service = SemanticScholarService() 