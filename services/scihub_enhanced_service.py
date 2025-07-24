import requests
import re
import time
import random
from typing import List, Dict, Any, Optional, Union
from urllib.parse import quote_plus, urlparse
from pathlib import Path
from datetime import datetime
import json

try:
    from utils.logger import get_logger
    logger = get_logger('scihub_enhanced_service')
except ImportError:
    logger = None

class SciHubEnhancedService:
    """
    Enhanced Sci-Hub service inspired by SciHubEVA
    Provides direct PDF downloads, multiple mirrors, and robust error handling
    """
    
    def __init__(self):
        # Sci-Hub mirrors (inspired by SciHubEVA)
        self.mirrors = [
            "https://sci-hub.box",
            "https://sci-hub.se", 
            "https://sci-hub.st",
            "https://sci-hub.ru",
            "https://sci-hub.ee",
            "https://sci-hub.wf",
            "https://sci-hub.mksa.top"
        ]
        
        # Set up session with realistic headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Set up download folder
        try:
            from config import SCIHUB_FOLDER
            self.download_folder = Path(SCIHUB_FOLDER)
        except ImportError:
            self.download_folder = Path('scihub_pdfs')
        
        self.download_folder.mkdir(parents=True, exist_ok=True)
        
        # Track working mirrors
        self.working_mirrors = []
        self.last_mirror_check = 0
        self.mirror_check_interval = 300  # 5 minutes
        
    def _is_valid_doi(self, doi: str) -> bool:
        """Validate DOI format"""
        if not doi:
            return False
        
        # Basic DOI validation
        doi_pattern = r'^10\.\d{4,}(?:\.\d+)*\/\S+(?:\S+)?$'
        return bool(re.match(doi_pattern, doi.strip()))
    
    def _is_valid_pmid(self, pmid: str) -> bool:
        """Validate PMID format"""
        if not pmid:
            return False
        
        # PMID should be numeric
        return pmid.strip().isdigit()
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _find_working_mirrors(self) -> List[str]:
        """Find working Sci-Hub mirrors"""
        current_time = time.time()
        
        # Check if we need to refresh mirror list
        if (current_time - self.last_mirror_check < self.mirror_check_interval and 
            self.working_mirrors):
            return self.working_mirrors
        
        if logger:
            logger.info("Checking Sci-Hub mirrors...")
        
        working_mirrors = []
        test_doi = "10.1038/nature12373"  # Test DOI
        
        for mirror in self.mirrors:
            try:
                test_url = f"{mirror}/{test_doi}"
                response = self.session.head(test_url, timeout=10)
                
                if response.status_code in [200, 302, 404]:
                    working_mirrors.append(mirror)
                    if logger:
                        logger.debug(f"Mirror {mirror} is working")
                else:
                    if logger:
                        logger.debug(f"Mirror {mirror} returned status {response.status_code}")
                        
            except Exception as e:
                if logger:
                    logger.debug(f"Mirror {mirror} failed: {e}")
                continue
        
        self.working_mirrors = working_mirrors
        self.last_mirror_check = current_time
        
        if logger:
            logger.info(f"Found {len(working_mirrors)} working mirrors")
        
        return working_mirrors
    
    def _extract_pdf_url(self, html_content: str, base_url: str) -> Optional[str]:
        """Extract PDF URL from Sci-Hub page"""
        try:
            # Look for PDF iframe
            iframe_pattern = r'<iframe[^>]*src=["\']([^"\']*\.pdf[^"\']*)["\'][^>]*>'
            iframe_match = re.search(iframe_pattern, html_content, re.IGNORECASE)
            
            if iframe_match:
                pdf_url = iframe_match.group(1)
                if pdf_url.startswith('//'):
                    pdf_url = 'https:' + pdf_url
                elif pdf_url.startswith('/'):
                    pdf_url = base_url + pdf_url
                return pdf_url
            
            # Look for direct PDF links
            pdf_pattern = r'href=["\']([^"\']*\.pdf[^"\']*)["\']'
            pdf_matches = re.findall(pdf_pattern, html_content, re.IGNORECASE)
            
            for pdf_url in pdf_matches:
                if pdf_url.startswith('//'):
                    pdf_url = 'https:' + pdf_url
                elif pdf_url.startswith('/'):
                    pdf_url = base_url + pdf_url
                return pdf_url
            
            return None
            
        except Exception as e:
            if logger:
                logger.error(f"Error extracting PDF URL: {e}")
            return None
    
    def _download_pdf_content(self, pdf_url: str) -> Optional[bytes]:
        """Download PDF content from URL"""
        try:
            response = self.session.get(pdf_url, timeout=30, stream=True)
            
            if response.status_code == 200:
                # Check if it's actually a PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type or pdf_url.lower().endswith('.pdf'):
                    return response.content
                else:
                    if logger:
                        logger.warning(f"URL does not return PDF content: {content_type}")
                    return None
            else:
                if logger:
                    logger.warning(f"Failed to download PDF: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            if logger:
                logger.error(f"Error downloading PDF: {e}")
            return None
    
    def _save_pdf_file(self, doi: str, pdf_content: bytes) -> str:
        """Save PDF content to file"""
        try:
            # Create filename from DOI
            safe_doi = re.sub(r'[^\w\-_.]', '_', doi)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_doi}_{timestamp}.pdf"
            filepath = self.download_folder / filename
            
            with open(filepath, 'wb') as f:
                f.write(pdf_content)
            
            if logger:
                logger.info(f"PDF saved: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            if logger:
                logger.error(f"Error saving PDF: {e}")
            raise
    
    def download_pdf(self, identifier: str) -> Dict[str, Any]:
        """
        Download PDF from Sci-Hub
        
        Args:
            identifier: DOI, PMID, or URL
            
        Returns:
            Dictionary with download result
        """
        if logger:
            logger.info(f"Attempting to download PDF for: {identifier}")
        
        # Validate identifier
        if not identifier:
            return {
                'success': False,
                'error': 'No identifier provided',
                'invalid_identifier': True
            }
        
        identifier = identifier.strip()
        
        # Determine identifier type
        if self._is_valid_doi(identifier):
            identifier_type = 'doi'
        elif self._is_valid_pmid(identifier):
            identifier_type = 'pmid'
        elif self._is_valid_url(identifier):
            identifier_type = 'url'
        else:
            return {
                'success': False,
                'error': f'Invalid identifier format: {identifier}',
                'invalid_identifier': True
            }
        
        # Find working mirrors
        working_mirrors = self._find_working_mirrors()
        if not working_mirrors:
            return {
                'success': False,
                'error': 'No working Sci-Hub mirrors found',
                'redirect': True,
                'url': f"https://sci-hub.se/{identifier}"
            }
        
        # Try each mirror
        for mirror in working_mirrors:
            try:
                if logger:
                    logger.info(f"Trying mirror: {mirror}")
                
                # Construct Sci-Hub URL
                scihub_url = f"{mirror}/{identifier}"
                
                # Get Sci-Hub page
                response = self.session.get(scihub_url, timeout=15)
                
                if response.status_code == 200:
                    # Extract PDF URL
                    pdf_url = self._extract_pdf_url(response.text, mirror)
                    
                    if pdf_url:
                        # Download PDF content
                        pdf_content = self._download_pdf_content(pdf_url)
                        
                        if pdf_content:
                            # Save PDF file
                            filepath = self._save_pdf_file(identifier, pdf_content)
                            
                            return {
                                'success': True,
                                'file_path': filepath,
                                'mirror': mirror,
                                'pdf_url': pdf_url,
                                'message': f'PDF downloaded successfully from {mirror}'
                            }
                        else:
                            if logger:
                                logger.warning(f"Failed to download PDF content from {pdf_url}")
                    else:
                        if logger:
                            logger.warning(f"No PDF URL found on {mirror}")
                
                elif response.status_code == 404:
                    if logger:
                        logger.warning(f"Article not found on {mirror}")
                else:
                    if logger:
                        logger.warning(f"Mirror {mirror} returned status {response.status_code}")
                
                # Add delay between requests
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                if logger:
                    logger.error(f"Error with mirror {mirror}: {e}")
                continue
        
        # If all mirrors failed, return redirect option
        return {
            'success': False,
            'error': 'Could not download PDF from any mirror',
            'redirect': True,
            'url': f"https://sci-hub.se/{identifier}",
            'message': 'Opening Sci-Hub in browser for manual download'
        }
    
    def batch_download(self, identifiers: List[str]) -> Dict[str, Any]:
        """
        Download multiple PDFs
        
        Args:
            identifiers: List of DOIs, PMIDs, or URLs
            
        Returns:
            Dictionary with batch results
        """
        if logger:
            logger.info(f"Starting batch download of {len(identifiers)} items")
        
        results = []
        successful = 0
        failed = 0
        
        for identifier in identifiers:
            try:
                result = self.download_pdf(identifier)
                results.append({
                    'identifier': identifier,
                    'success': result['success'],
                    'error': result.get('error', ''),
                    'file_path': result.get('file_path', ''),
                    'url': result.get('url', '')
                })
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                
                # Add delay between downloads
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                if logger:
                    logger.error(f"Error in batch download for {identifier}: {e}")
                results.append({
                    'identifier': identifier,
                    'success': False,
                    'error': str(e)
                })
                failed += 1
        
        return {
            'results': results,
            'total': len(identifiers),
            'successful': successful,
            'failed': failed
        }
    
    def get_downloaded_files(self) -> List[Dict[str, Any]]:
        """Get list of downloaded PDF files"""
        try:
            files = []
            
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
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_mirror_status(self) -> Dict[str, Any]:
        """Get status of all mirrors"""
        working_mirrors = self._find_working_mirrors()
        
        return {
            'total_mirrors': len(self.mirrors),
            'working_mirrors': len(working_mirrors),
            'mirrors': [
                {
                    'url': mirror,
                    'status': 'working' if mirror in working_mirrors else 'failed'
                }
                for mirror in self.mirrors
            ]
        } 