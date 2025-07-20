"""
Abstract base class for research funding APIs

This module provides a common interface for all research funding database APIs,
ensuring consistent data structure and error handling across different sources.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from utils.logger import get_logger
from utils.performance import get_session

logger = get_logger('api_base')

@dataclass
class ResearchProject:
    """Standardized research project data structure"""
    id: str
    title: str
    description: str
    principal_investigator: str
    organization: str
    funding_amount: Optional[float]
    currency: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    keywords: List[str]
    source: str
    url: Optional[str]
    raw_data: Dict[str, Any]  # Original API response data

class ResearchFundingAPI(ABC):
    """
    Abstract base class for research funding APIs
    
    All API implementations should inherit from this class and implement
    the required methods to ensure consistent interface and data structure.
    """
    
    def __init__(self, name: str, base_url: str, api_key: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            name: Human-readable name of the API
            base_url: Base URL for the API
            api_key: Optional API key for authentication
        """
        self.name = name
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        
        # Use optimized session if available, but ensure it supports headers
        if get_session:
            self.session = get_session()
            # Create a new session for headers if optimized session doesn't support them
            if not hasattr(self.session, 'headers'):
                self.session = requests.Session()
        else:
            self.session = requests.Session()
        
        self.logger = get_logger(f'api.{name.lower()}')
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = None
        
    @abstractmethod
    def search(self, query: str, max_results: int = 50) -> List[ResearchProject]:
        """
        Search for research projects
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of ResearchProject objects
        """
        pass
    
    @abstractmethod
    def get_project_details(self, project_id: str) -> Optional[ResearchProject]:
        """
        Get detailed information about a specific project
        
        Args:
            project_id: Unique project identifier
            
        Returns:
            ResearchProject object or None if not found
        """
        pass
    
    def make_request(self, endpoint: str, params: Dict[str, Any] = None, 
                    headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to API with error handling and rate limiting
        
        Args:
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            headers: Request headers
            
        Returns:
            JSON response data or None if failed
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Add API key if available
        if self.api_key:
            if params is None:
                params = {}
            params['api_key'] = self.api_key
        
        # Set default headers
        if headers is None:
            headers = {}
        headers.setdefault('User-Agent', 'LeadFinder/1.0')
        
        try:
            self.logger.info(f"Making request to {url}")
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.logger.info(f"Successfully retrieved data from {self.name}")
                return response.json()
            elif response.status_code == 429:
                self.logger.warning(f"Rate limited by {self.name}")
                return None
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {self.name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error for {self.name}: {e}")
            return None
    
    def normalize_project_data(self, raw_data: Dict[str, Any]) -> ResearchProject:
        """
        Convert raw API data to standardized ResearchProject format
        
        Args:
            raw_data: Raw data from API response
            
        Returns:
            Standardized ResearchProject object
        """
        # This is a base implementation - subclasses should override
        return ResearchProject(
            id=str(raw_data.get('id', '')),
            title=str(raw_data.get('title', '')),
            description=str(raw_data.get('description', '')),
            principal_investigator=str(raw_data.get('pi', '')),
            organization=str(raw_data.get('organization', '')),
            funding_amount=float(raw_data.get('amount', 0)) if raw_data.get('amount') else None,
            currency=str(raw_data.get('currency', 'SEK')),
            start_date=self._parse_date(raw_data.get('start_date')),
            end_date=self._parse_date(raw_data.get('end_date')),
            keywords=raw_data.get('keywords', []),
            source=self.name,
            url=raw_data.get('url'),
            raw_data=raw_data
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def _ensure_int(self, value: Any, default: int = 50) -> int:
        """
        Ensure a value is an integer, with fallback to default
        
        Args:
            value: Value to convert to int
            default: Default value if conversion fails
            
        Returns:
            Integer value
        """
        try:
            if isinstance(value, str):
                return int(value)
            elif isinstance(value, (int, float)):
                return int(value)
            else:
                return default
        except (ValueError, TypeError):
            return default
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get API status and health information
        
        Returns:
            Dictionary with status information
        """
        try:
            # Try to make a simple request to check if API is available
            test_response = self.make_request('health') or self.make_request('')
            return {
                'name': self.name,
                'status': 'ok' if test_response is not None else 'error',
                'base_url': self.base_url,
                'has_api_key': bool(self.api_key)
            }
        except Exception as e:
            return {
                'name': self.name,
                'status': 'error',
                'error': str(e),
                'base_url': self.base_url,
                'has_api_key': bool(self.api_key)
            } 