"""
Performance optimization utilities for LeadFinder

This module provides connection pooling, session management, and other
performance optimizations for the application.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional
from config import REQUEST_POOL_SIZE, REQUEST_TIMEOUT
from utils.logger import get_logger

logger = get_logger('performance')

class OptimizedSession:
    """Optimized requests session with connection pooling and retry logic"""
    
    def __init__(self, pool_size: int = REQUEST_POOL_SIZE, timeout: int = REQUEST_TIMEOUT):
        self.session = requests.Session()
        self.timeout = timeout
        
        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
            max_retries=Retry(
                total=3,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        logger.info(f"Optimized session created with pool size {pool_size}")
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make a GET request with optimized settings"""
        kwargs.setdefault('timeout', self.timeout)
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make a POST request with optimized settings"""
        kwargs.setdefault('timeout', self.timeout)
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Close the session and free resources"""
        self.session.close()
        logger.info("Session closed")

# Global session instance
_global_session: Optional[OptimizedSession] = None

def get_session() -> OptimizedSession:
    """Get the global optimized session instance"""
    global _global_session
    if _global_session is None:
        _global_session = OptimizedSession()
    return _global_session

def close_session():
    """Close the global session"""
    global _global_session
    if _global_session:
        _global_session.close()

class DatabaseConnection:
    """Database connection manager with connection pooling"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None
    
    def __enter__(self):
        """Enter context manager"""
        self._connection = sqlite3.connect(self.db_path)
        return self._connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        if self._connection:
            self._connection.close()

def batch_save_leads(db_path: str, leads: list) -> int:
    """
    Save multiple leads in a single database transaction
    
    Args:
        db_path: Database file path
        leads: List of lead tuples (title, snippet, link, ai_summary)
        
    Returns:
        Number of leads saved
    """
    try:
        with DatabaseConnection(db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                'INSERT INTO leads (title, snippet, link, ai_summary) VALUES (?, ?, ?, ?)',
                leads
            )
            conn.commit()
            saved_count = len(leads)
            logger.info(f"Batch saved {saved_count} leads")
            return saved_count
    except Exception as e:
        logger.error(f"Batch save failed: {e}")
        raise

# Import sqlite3 for DatabaseConnection
import sqlite3 