"""
Database Connection Pool Manager for LeadFinder

This module provides a connection pool for SQLite database operations,
improving performance by reusing database connections instead of creating
new ones for each operation.
"""

import sqlite3
import threading
import time
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from queue import Queue, Empty
import logging

try:
    from utils.logger import get_logger
    logger = get_logger('database_pool')
except ImportError:
    logger = None

try:
    from config import DATABASE_PATH
except ImportError:
    DATABASE_PATH = "data/leadfinder.db"

class DatabaseConnectionPool:
    """Thread-safe SQLite connection pool with improved error handling"""
    
    def __init__(self, db_path: str = None, max_connections: int = None, 
                 connection_timeout: int = None, check_interval: int = None):
        """
        Initialize the connection pool.
        
        Args:
            db_path: Path to SQLite database file
            max_connections: Maximum number of connections in pool
            connection_timeout: Timeout for getting connection from pool
            check_interval: Interval for health checks
        """
        self.db_path = db_path or str(DATABASE_PATH)
        self.max_connections = max_connections or 10
        self.connection_timeout = connection_timeout or 5
        self.check_interval = check_interval or 60
        
        # Thread-safe pool
        self._pool = Queue(maxsize=self.max_connections)
        self._lock = threading.Lock()
        self._active_connections = 0
        self._total_connections_created = 0
        self._last_health_check = 0
        
        # Initialize pool
        self._initialize_pool()
        
        if logger:
            logger.info(f"Database pool initialized with {self.max_connections} max connections")
    
    def _initialize_pool(self):
        """Initialize the connection pool with initial connections"""
        try:
            for _ in range(min(3, self.max_connections)):
                conn = self._create_connection()
                if conn:
                    self._pool.put(conn)
                    self._active_connections += 1
                    self._total_connections_created += 1
        except Exception as e:
            if logger:
                logger.warning(f"Failed to initialize some pool connections: {e}")
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new SQLite connection with proper settings"""
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,  # Allow multi-threaded access
                timeout=30.0,  # Connection timeout
                isolation_level=None  # Auto-commit mode
            )
            
            # Set SQLite pragmas for better performance
            try:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA cache_size=10000")
                conn.execute("PRAGMA temp_store=MEMORY")
                conn.execute("PRAGMA mmap_size=268435456")
            except Exception as e:
                if logger:
                    logger.warning(f"Failed to set SQLite pragmas: {e}")
            
            return conn
        except Exception as e:
            if logger:
                logger.error(f"Failed to create database connection: {e}")
            return None
    
    def _is_connection_healthy(self, conn: sqlite3.Connection) -> bool:
        """Check if a connection is still healthy"""
        try:
            # Simple health check that works in multi-threaded environments
            conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def _cleanup_connection(self, conn: sqlite3.Connection):
        """Safely close a database connection"""
        try:
            if conn:
                conn.close()
        except Exception as e:
            if logger:
                logger.warning(f"Error closing database connection: {e}")
    
    def _health_check(self):
        """Perform periodic health check on the pool"""
        current_time = time.time()
        if current_time - self._last_health_check < self.check_interval:
            return
        
        self._last_health_check = current_time
        
        # Clean up any unhealthy connections
        healthy_connections = []
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                if self._is_connection_healthy(conn):
                    healthy_connections.append(conn)
                else:
                    self._cleanup_connection(conn)
                    self._active_connections -= 1
            except Empty:
                break
        
        # Return healthy connections to pool
        for conn in healthy_connections:
            try:
                self._pool.put_nowait(conn)
            except:
                self._cleanup_connection(conn)
                self._active_connections -= 1
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection from the pool with improved error handling.
        
        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM leads")
                results = cursor.fetchall()
        """
        conn = None
        try:
            # Try to get a connection from the pool
            try:
                conn = self._pool.get(timeout=self.connection_timeout)
            except Empty:
                # Pool is empty, create a new connection if under limit
                with self._lock:
                    if self._active_connections < self.max_connections:
                        conn = self._create_connection()
                        if conn:
                            self._active_connections += 1
                            self._total_connections_created += 1
                        else:
                            raise Exception("Failed to create new database connection")
                    else:
                        raise Exception(f"Connection pool exhausted (max: {self.max_connections})")
            
            if conn is None:
                raise Exception("Failed to obtain database connection")
            
            # Verify connection is healthy before yielding
            if not self._is_connection_healthy(conn):
                self._cleanup_connection(conn)
                self._active_connections -= 1
                raise Exception("Database connection is not healthy")
            
            yield conn
            
        except Exception as e:
            if logger:
                logger.error(f"Database connection error: {e}")
            if conn:
                self._cleanup_connection(conn)
                self._active_connections -= 1
            raise
        finally:
            # Return connection to pool if it's still healthy
            if conn:
                try:
                    if self._is_connection_healthy(conn):
                        self._pool.put_nowait(conn)
                    else:
                        self._cleanup_connection(conn)
                        self._active_connections -= 1
                except:
                    # Pool is full or connection is unhealthy, close it
                    self._cleanup_connection(conn)
                    self._active_connections -= 1
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        Execute a SELECT query and return results with improved error handling.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of results as dictionaries
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    # Get column names for dict conversion
                    columns = [description[0] for description in cursor.description]
                    results = cursor.fetchall()
                    
                    # Convert to list of dictionaries
                    return [dict(zip(columns, row)) for row in results]
                    
            except Exception as e:
                if logger:
                    logger.error(f"Query execution failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1)  # Brief delay before retry
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute an UPDATE, INSERT, or DELETE query with improved error handling.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Number of affected rows
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    conn.commit()
                    return cursor.rowcount
                    
            except Exception as e:
                if logger:
                    logger.error(f"Update execution failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1)  # Brief delay before retry
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute the same query with multiple parameter sets with improved error handling.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.executemany(query, params_list)
                    conn.commit()
                    return cursor.rowcount
                    
            except Exception as e:
                if logger:
                    logger.error(f"Execute many failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1)  # Brief delay before retry
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            'pool_size': self._pool.qsize(),
            'max_connections': self.max_connections,
            'active_connections': self._active_connections,
            'total_connections_created': self._total_connections_created,
            'connection_timeout': self.connection_timeout,
            'last_health_check': self._last_health_check
        }
    
    def close_all(self):
        """Close all connections in the pool"""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                self._cleanup_connection(conn)
            except Empty:
                break
        
        self._active_connections = 0
        if logger:
            logger.info("All database connections closed")

# Global connection pool instance
_db_pool = None

def get_db_pool() -> DatabaseConnectionPool:
    """Get the global database connection pool instance"""
    global _db_pool
    if _db_pool is None:
        _db_pool = DatabaseConnectionPool()
    return _db_pool

def close_db_pool():
    """Close the global database connection pool"""
    global _db_pool
    if _db_pool:
        _db_pool.close_all()
        _db_pool = None 