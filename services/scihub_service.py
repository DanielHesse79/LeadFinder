import requests
from typing import List, Dict, Any, Optional
import re
from urllib.parse import quote_plus
from pathlib import Path
from datetime import datetime

try:
    from utils.logger import get_logger
    logger = get_logger('scihub_service')
except ImportError:
    logger = None

class SciHubService:
    """Sci-Hub service for accessing academic papers"""
    
    def __init__(self):
        # List of Sci-Hub mirrors to try
        self.mirrors = [
            "https://sci-hub.box",
            "https://sci-hub.se", 
            "https://sci-hub.st",
            "https://sci-hub.ru"
        ]
        self.base_url = self.mirrors[0]  # Default to first mirror
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LeadFinder/1.0 (https://github.com/your-repo; mailto:your-email@example.com)'
        })
        
        # Set up download folder
        try:
            from config import SCIHUB_FOLDER
            self.download_folder = Path(SCIHUB_FOLDER)
            self.download_folder.mkdir(parents=True, exist_ok=True)
        except ImportError:
            self.download_folder = Path('scihub_pdfs')
            self.download_folder.mkdir(parents=True, exist_ok=True)
    
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
        Search for open access articles in Sci-Hub
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of article dictionaries
        """
        if logger:
            logger.info(f"Searching Sci-Hub for: {query}")
        
        try:
            # Note: Sci-Hub doesn't have a public search API, so this is a simplified implementation
            # In a real implementation, you would need to implement web scraping or use alternative services
            
            # For now, return a placeholder with information about the limitation
            articles = []
            
            # Ensure max_results is an integer
            max_results_int = self._ensure_int(max_results, 5)
            for i in range(min(max_results_int, 5)):
                articles.append({
                    'title': f'Sci-Hub open access result for "{query}" (Placeholder {i+1})',
                    'authors': ['Sample Author'],
                    'abstract': f'This is a placeholder for Sci-Hub search results. Sci-Hub provides access to academic papers, but requires specific DOI or URL to access papers.',
                    'source': 'Sci-Hub',
                    'year': '2024',
                    'journal': 'Open Access Journal',
                    'url': f'https://sci-hub.se/search?q={quote_plus(query)}',
                    'pdf_url': None
                })
            
            if logger:
                logger.info(f"Returned {len(articles)} placeholder Sci-Hub results")
            
            return articles
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching Sci-Hub: {e}")
            return []
    
    def get_article_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get article by DOI from Sci-Hub
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Article details or None
        """
        if logger:
            logger.info(f"Getting Sci-Hub article for DOI: {doi}")
        
        try:
            # This would implement the actual Sci-Hub DOI lookup
            # For now, return a placeholder
            return {
                'title': f'Article with DOI: {doi}',
                'authors': ['Unknown Author'],
                'abstract': 'This is a placeholder for Sci-Hub DOI lookup.',
                'source': 'Sci-Hub',
                'year': '2024',
                'journal': 'Unknown Journal',
                'url': f'https://sci-hub.se/{doi}',
                'pdf_url': f'https://sci-hub.se/{doi}'
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting Sci-Hub article for DOI {doi}: {e}")
            return None
    
    def download_pdf(self, doi: str) -> Dict[str, Any]:
        """
        Get Sci-Hub URL for a DOI
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Dictionary with Sci-Hub URL or error
        """
        if logger:
            logger.info(f"Getting Sci-Hub URL for DOI: {doi}")
        
        # Validate DOI format
        if not doi or not self._is_valid_doi(doi):
            if logger:
                logger.warning(f"Invalid DOI format: {doi}")
            return {
                'success': False,
                'error': f'Invalid DOI format: {doi}',
                'invalid_doi': True
            }
        
        try:
            # Find a working Sci-Hub mirror
            working_mirror = None
            for mirror in self.mirrors:
                try:
                    # Test if mirror is accessible
                    test_url = f"{mirror}/10.1038/nature12373"  # Test with a known DOI
                    response = self.session.head(test_url, timeout=10)
                    if response.status_code in [200, 302, 404]:  # Mirror responds
                        working_mirror = mirror
                        break
                except Exception as e:
                    if logger:
                        logger.debug(f"Mirror {mirror} not accessible: {e}")
                    continue
            
            if not working_mirror:
                # Fallback to first mirror
                working_mirror = self.mirrors[0]
                if logger:
                    logger.warning(f"No working mirror found, using fallback: {working_mirror}")
            
            # Create Sci-Hub URL
            scihub_url = f"{working_mirror}/{doi}"
            
            if logger:
                logger.info(f"Generated Sci-Hub URL: {scihub_url}")
            
            return {
                'success': True,
                'redirect': True,
                'url': scihub_url,
                'message': f'Sci-Hub URL generated for DOI: {doi}',
                'mirror': working_mirror
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error generating Sci-Hub URL for DOI {doi}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_downloaded_files(self) -> List[Dict[str, Any]]:
        """
        Get list of downloaded PDF files
        
        Returns:
            List of file dictionaries with metadata
        """
        try:
            files = []
            if not self.download_folder.exists():
                return files
            
            for file_path in self.download_folder.glob("*.pdf"):
                try:
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': stat.st_size,
                        'size_formatted': self._format_file_size(stat.st_size),
                        'downloaded_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'modified': stat.st_mtime
                    })
                except Exception as e:
                    if logger:
                        logger.warning(f"Error reading file {file_path}: {e}")
                    continue
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            return files
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting downloaded files: {e}")
            return []

    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human readable format
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _is_valid_doi(self, doi: str) -> bool:
        """
        Validate DOI format
        
        Args:
            doi: Digital Object Identifier to validate
            
        Returns:
            True if DOI format is valid, False otherwise
        """
        if not doi:
            return False
        
        # Basic DOI validation - should contain at least one slash and be reasonably formatted
        # DOI format: 10.xxxx/xxxxx
        doi_pattern = r'^10\.\d{4,}(?:\.\d+)*\/.+$'
        import re
        return bool(re.match(doi_pattern, doi.strip()))
    
    def _save_pdf_to_file(self, doi: str, pdf_content: bytes) -> str:
        """
        Save PDF content to file
        
        Args:
            doi: Digital Object Identifier
            pdf_content: PDF content as bytes
            
        Returns:
            Path to saved file
        """
        try:
            import os
            from pathlib import Path
            
            # Create filename from DOI
            safe_doi = doi.replace('/', '_').replace(':', '_')
            filename = f"{safe_doi}.pdf"
            
            # Use configured download folder
            from config import SCIHUB_FOLDER
            download_path = Path(SCIHUB_FOLDER)
            download_path.mkdir(parents=True, exist_ok=True)
            
            file_path = download_path / filename
            
            # Save the PDF
            with open(file_path, 'wb') as f:
                f.write(pdf_content)
            
            if logger:
                logger.info(f"PDF saved to: {file_path}")
            
            return str(file_path)
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to save PDF for DOI {doi}: {e}")
            return ""

# Global service instance
scihub_service = SciHubService() 