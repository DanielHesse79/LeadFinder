"""
WebScraper Service for Scientific Information

This module provides web scraping capabilities for scientific information
using Playwright for browser automation and BeautifulSoup for content extraction.
Can be integrated with LangChain + LLM for analysis and structured data extraction.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    from utils.logger import get_logger
    logger = get_logger('webscraper_service')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

@dataclass
class ScrapedContent:
    """Container for scraped content"""
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    html: str
    timestamp: float
    source_type: str  # 'scientific_paper', 'research_profile', 'institution', etc.

@dataclass
class ScrapingResult:
    """Result from web scraping operation"""
    success: bool
    content: Optional[ScrapedContent]
    error: Optional[str]
    processing_time: float
    source_url: str

class WebScraperService:
    """
    Service for scraping scientific information from web pages
    """
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None
        self._initialized = False
        
        # Configuration
        self.timeout = 30000  # 30 seconds
        self.max_content_length = 50000  # 50KB
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # Scientific content patterns
        self.scientific_patterns = {
            'authors': r'(?i)(author|authors?|by)\s*:?\s*([^\.]+)',
            'abstract': r'(?i)(abstract|summary)\s*:?\s*([^\.]+)',
            'doi': r'(?i)doi\s*:?\s*([^\s]+)',
            'publication_date': r'(?i)(published|date|year)\s*:?\s*([^\s]+)',
            'institution': r'(?i)(university|institute|college|department)\s*:?\s*([^\.]+)',
            'keywords': r'(?i)(keywords?|tags?)\s*:?\s*([^\.]+)',
            'funding': r'(?i)(funded|grant|sponsored)\s*:?\s*([^\.]+)',
        }
        
        if logger:
            logger.info("WebScraper service initialized")
    
    async def initialize(self) -> bool:
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            if logger:
                logger.error("Playwright not available")
            return False
        
        # Clean up any existing browser
        if self._initialized:
            await self.close()
        
        try:
            if logger:
                logger.info("Starting Playwright browser initialization...")
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            self.page = await self.browser.new_page()
            # Set user agent and viewport
            await self.page.set_extra_http_headers({"User-Agent": self.user_agent})
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Test the page to ensure it's working
            try:
                await self.page.goto("data:text/html,<html><body>Test</body></html>", timeout=5000)
            except Exception as e:
                if logger:
                    logger.error(f"Page test failed: {e}")
                return False
            
            self._initialized = True
            if logger:
                logger.info("Playwright browser initialized successfully")
            return True
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to initialize Playwright: {e}")
            return False
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
        except Exception as e:
            if logger:
                logger.warning(f"Error closing page: {e}")
        
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            if logger:
                logger.warning(f"Error closing browser: {e}")
        
        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            if logger:
                logger.warning(f"Error stopping playwright: {e}")
        
        self._initialized = False
    
    async def scrape_url(self, url: str, content_type: str = "scientific_paper") -> ScrapingResult:
        """
        Scrape content from a URL
        
        Args:
            url: URL to scrape
            content_type: Type of content expected ('scientific_paper', 'research_profile', etc.)
            
        Returns:
            ScrapingResult with scraped content or error
        """
        start_time = time.time()
        
        if not self._initialized:
            success = await self.initialize()
            if not success:
                return ScrapingResult(
                    success=False,
                    content=None,
                    error="Failed to initialize browser",
                    processing_time=time.time() - start_time,
                    source_url=url
                )
        
        try:
            if logger:
                logger.info(f"Scraping URL: {url}")
            
            # Navigate to page
            await self.page.goto(url, timeout=self.timeout, wait_until='networkidle')
            
            # Wait for content to load
            await asyncio.sleep(2)
            
            # Get page content
            html = await self.page.content()
            title = await self.page.title()
            
            # Extract content based on type
            if content_type == "scientific_paper":
                content = await self._extract_scientific_paper_content(html)
            elif content_type == "research_profile":
                content = await self._extract_research_profile_content(html)
            elif content_type == "institution":
                content = await self._extract_institution_content(html)
            else:
                content = await self._extract_general_content(html)
            
            # Extract metadata
            metadata = self._extract_metadata(html, title, content)
            
            # Create scraped content object
            scraped_content = ScrapedContent(
                url=url,
                title=title,
                content=content,
                metadata=metadata,
                html=html,
                timestamp=time.time(),
                source_type=content_type
            )
            
            processing_time = time.time() - start_time
            
            if logger:
                logger.info(f"Successfully scraped {url} in {processing_time:.2f}s")
            
            return ScrapingResult(
                success=True,
                content=scraped_content,
                error=None,
                processing_time=processing_time,
                source_url=url
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Failed to scrape {url}: {str(e)}"
            
            if logger:
                logger.error(error_msg)
            
            return ScrapingResult(
                success=False,
                content=None,
                error=error_msg,
                processing_time=processing_time,
                source_url=url
            )
    
    async def _extract_scientific_paper_content(self, html: str) -> str:
        """Extract content from scientific paper pages"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return html
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content areas
        content_selectors = [
            'main', 'article', '.content', '.main-content', '.paper-content',
            '.abstract', '.introduction', '.methodology', '.results', '.conclusion',
            '#content', '#main', '.scientific-content', '.research-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = " ".join([elem.get_text(strip=True) for elem in elements])
                break
        
        # If no specific content found, get body text
        if not content:
            content = soup.get_text(strip=True)
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content)
        content = content[:self.max_content_length]
        
        return content
    
    async def _extract_research_profile_content(self, html: str) -> str:
        """Extract content from research profile pages"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return html
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Look for profile-specific content
        profile_selectors = [
            '.profile', '.researcher-profile', '.author-profile',
            '.bio', '.biography', '.about', '.research-interests',
            '.publications', '.research-areas', '.expertise'
        ]
        
        content = ""
        for selector in profile_selectors:
            elements = soup.select(selector)
            if elements:
                content = " ".join([elem.get_text(strip=True) for elem in elements])
                break
        
        # Fallback to general content
        if not content:
            content = soup.get_text(strip=True)
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content)
        content = content[:self.max_content_length]
        
        return content
    
    async def _extract_institution_content(self, html: str) -> str:
        """Extract content from institution pages"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return html
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Look for institution-specific content
        institution_selectors = [
            '.institution', '.university', '.department', '.faculty',
            '.research', '.about', '.mission', '.vision',
            '.academics', '.programs', '.faculty-profiles'
        ]
        
        content = ""
        for selector in institution_selectors:
            elements = soup.select(selector)
            if elements:
                content = " ".join([elem.get_text(strip=True) for elem in elements])
                break
        
        # Fallback to general content
        if not content:
            content = soup.get_text(strip=True)
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content)
        content = content[:self.max_content_length]
        
        return content
    
    async def _extract_general_content(self, html: str) -> str:
        """Extract general content from any page"""
        if not BEAUTIFULSOUP_AVAILABLE:
            return html
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get main content
        content = soup.get_text(strip=True)
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content)
        content = content[:self.max_content_length]
        
        return content
    
    def _extract_metadata(self, html: str, title: str, content: str) -> Dict[str, Any]:
        """Extract metadata from HTML and content"""
        metadata = {
            'title': title,
            'content_length': len(content),
            'extracted_patterns': {}
        }
        
        # Extract patterns from content
        for pattern_name, pattern in self.scientific_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                metadata['extracted_patterns'][pattern_name] = matches
        
        # Extract meta tags
        if BEAUTIFULSOUP_AVAILABLE:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Meta tags
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name', meta.get('property', ''))
                content_val = meta.get('content', '')
                if name and content_val:
                    metadata[f'meta_{name}'] = content_val
            
            # Links
            links = soup.find_all('a', href=True)
            metadata['links'] = [link['href'] for link in links[:10]]  # First 10 links
        
        return metadata
    
    async def scrape_multiple_urls(self, urls: List[str], content_types: Optional[List[str]] = None) -> List[ScrapingResult]:
        """
        Scrape multiple URLs concurrently
        
        Args:
            urls: List of URLs to scrape
            content_types: List of content types (optional)
            
        Returns:
            List of ScrapingResult objects
        """
        if content_types is None:
            content_types = ["scientific_paper"] * len(urls)
        
        # Ensure we have the same number of content types as URLs
        if len(content_types) != len(urls):
            content_types = content_types + ["scientific_paper"] * (len(urls) - len(content_types))
        
        # Create tasks for concurrent scraping
        tasks = []
        for url, content_type in zip(urls, content_types):
            task = self.scrape_url(url, content_type)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to ScrapingResult objects
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ScrapingResult(
                    success=False,
                    content=None,
                    error=str(result),
                    processing_time=0,
                    source_url=urls[i]
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def is_available(self) -> bool:
        """Check if webscraper service is available"""
        return PLAYWRIGHT_AVAILABLE and BEAUTIFULSOUP_AVAILABLE
    
    def get_status(self) -> Dict[str, Any]:
        """Get webscraper service status"""
        return {
            'available': self.is_available(),
            'playwright_available': PLAYWRIGHT_AVAILABLE,
            'beautifulsoup_available': BEAUTIFULSOUP_AVAILABLE,
            'initialized': self._initialized,
            'browser_running': self.browser is not None
        }

# Global instance
webscraper_service = WebScraperService() 