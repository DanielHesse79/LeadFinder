import requests
import re
from typing import List, Dict, Any, Optional

# Import config with fallbacks
try:
    from config import PUBMED_API_KEY, PUBMED_BASE_URL
except ImportError:
    PUBMED_API_KEY = ''
    PUBMED_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'

try:
    from utils.logger import get_logger
    logger = get_logger('pubmed_service')
except ImportError:
    logger = None

class PubMedService:
    """PubMed service for academic article search"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def search_articles(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for academic articles in PubMed
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of article dictionaries
        """
        if logger:
            logger.info(f"Searching PubMed for: {query}")
        
        try:
            # Step 1: Search for article IDs
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            if self.api_key:
                search_params['api_key'] = self.api_key
            
            response = requests.get(f"{self.base_url}/esearch.fcgi", params=search_params, timeout=30)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"PubMed search failed: {response.status_code}")
                return []
            
            # Parse search results
            search_data = response.json()
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            
            if not id_list:
                if logger:
                    logger.info("No PubMed articles found")
                return []
            
            if logger:
                logger.info(f"Found {len(id_list)} PubMed IDs, fetching details...")
            
            # Step 2: Get article details
            articles = []
            for pmid in id_list[:max_results]:
                article = self.get_article_details(pmid)
                if article:
                    articles.append(article)
                    if logger and article.get('doi'):
                        logger.info(f"Article {pmid} has DOI: {article['doi']}")
            
            if logger:
                logger.info(f"Found {len(articles)} PubMed articles with details")
            
            return articles
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching PubMed: {e}")
            return []
    
    def get_article_details(self, pmid: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific article
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Article details or None
        """
        try:
            # Get article details
            params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = requests.get(f"{self.base_url}/efetch.fcgi", params=params, timeout=30)
            
            if response.status_code != 200:
                if logger:
                    logger.error(f"PubMed article fetch failed for {pmid}: {response.status_code}")
                return None
            
            # Parse XML response (simplified)
            xml_content = response.text
            
            # Extract basic information using simple parsing
            title = self._extract_xml_field(xml_content, 'ArticleTitle')
            abstract = self._extract_xml_field(xml_content, 'AbstractText')
            journal = self._extract_journal_name(xml_content)
            pub_date = self._extract_publication_year(xml_content)
            authors = self._extract_authors(xml_content)
            doi = self._extract_doi(xml_content)
            
            article = {
                'pmid': pmid,
                'title': title or f'Article {pmid}',
                'abstract': abstract or 'No abstract available',
                'authors': authors,
                'journal': journal or 'Unknown Journal',
                'year': pub_date or 'Unknown',
                'url': f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',
                'doi': doi,
                'source': 'PubMed'
            }
            
            return article
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting article details for {pmid}: {e}")
            return None
    
    def _extract_xml_field(self, xml_content: str, field_name: str) -> str:
        """Extract a field from XML content"""
        pattern = f'<{field_name}[^>]*>(.*?)</{field_name}>'
        match = re.search(pattern, xml_content, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Clean up XML tags within the content
            content = re.sub(r'<[^>]+>', '', content)
            return content
        return ''
    
    def _extract_doi(self, xml_content: str) -> str:
        """Extract DOI from XML content"""
        # Look for DOI in ArticleIdList
        doi_pattern = r'<ArticleId IdType="doi">([^<]+)</ArticleId>'
        match = re.search(doi_pattern, xml_content)
        if match:
            doi = match.group(1).strip()
            if logger:
                logger.info(f"Extracted DOI: {doi}")
            return doi
        
        # Also check for DOI in other locations
        doi_patterns = [
            r'<ELocationID EIdType="doi">([^<]+)</ELocationID>',
            r'<ArticleId IdType="doi">([^<]+)</ArticleId>',
            r'doi[:\s]+([^\s]+)',  # Look for "doi:" in text
        ]
        
        for pattern in doi_patterns:
            match = re.search(pattern, xml_content, re.IGNORECASE)
            if match:
                doi = match.group(1).strip()
                if logger:
                    logger.info(f"Extracted DOI with pattern {pattern}: {doi}")
                return doi
        
        if logger:
            logger.debug("No DOI found in article")
        return ''
    
    def _extract_journal_name(self, xml_content: str) -> str:
        """Extract journal name from XML content"""
        # Look for Journal Title
        journal_pattern = r'<Title>([^<]+)</Title>'
        match = re.search(journal_pattern, xml_content)
        if match:
            return match.group(1).strip()
        return 'Unknown Journal'
    
    def _extract_publication_year(self, xml_content: str) -> str:
        """Extract publication year from XML content"""
        # Look for Year in PubDate
        year_pattern = r'<Year>([^<]+)</Year>'
        match = re.search(year_pattern, xml_content)
        if match:
            return match.group(1).strip()
        return 'Unknown'
    
    def _extract_authors(self, xml_content: str) -> List[str]:
        """Extract author names from XML content"""
        authors = []
        pattern = r'<Author[^>]*>.*?<LastName>([^<]+)</LastName>.*?<ForeName>([^<]+)</ForeName>.*?</Author>'
        matches = re.findall(pattern, xml_content, re.DOTALL)
        
        for last_name, first_name in matches:
            authors.append(f"{first_name} {last_name}")
        
        return authors
    


# Global service instance
pubmed_service = PubMedService() 