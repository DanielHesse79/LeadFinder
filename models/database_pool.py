"""
Database Connection Pool Manager for LeadFinder

This module provides a connection pool for SQLite database operations,
improving performance by reusing database connections instead of creating
new ones for each operation.
"""

import sqlite3
import threading
import time
from typing import Optional, Dict, Any
from queue import Queue, Empty
from contextlib import contextmanager
from config import DATABASE_PATH, DB_POOL_MAX_CONNECTIONS, DB_POOL_CONNECTION_TIMEOUT, DB_POOL_HEALTH_CHECK_INTERVAL

try:
    from utils.logger import get_logger
    logger = get_logger('database_pool')
except ImportError:
    logger = None

class DatabaseConnectionPool:
    """
    Thread-safe connection pool for SQLite database operations.
    
    Features:
    - Connection reuse for better performance
    - Thread-safe operations
    - Automatic connection health checks
    - Configurable pool size and timeout
    - Connection cleanup on errors
    """
    
    def __init__(self, db_path: str = None, max_connections: int = None, 
                 connection_timeout: int = None, check_interval: int = None):
        """
        Initialize the connection pool.
        
        Args:
            db_path: Path to the SQLite database file
            max_connections: Maximum number of connections in the pool
            connection_timeout: Timeout for getting a connection (seconds)
            check_interval: Interval for checking connection health (seconds)
        """
        self.db_path = db_path or str(DATABASE_PATH)
        
        # Handle potential None values from configuration
        try:
            self.max_connections = max_connections or DB_POOL_MAX_CONNECTIONS or 10
        except (TypeError, ValueError):
            self.max_connections = 10
            
        try:
            self.connection_timeout = connection_timeout or DB_POOL_CONNECTION_TIMEOUT or 30
        except (TypeError, ValueError):
            self.connection_timeout = 30
            
        try:
            self.check_interval = check_interval or DB_POOL_HEALTH_CHECK_INTERVAL or 300
        except (TypeError, ValueError):
            self.check_interval = 300
        
        # Thread-safe connection pool
        self._pool = Queue(maxsize=max_connections)
        self._lock = threading.Lock()
        self._active_connections = 0
        self._total_connections_created = 0
        self._last_health_check = time.time()
        
        # Initialize the pool with a few connections
        self._initialize_pool()
        
        if logger:
            logger.info(f"Database connection pool initialized for {self.db_path}")
    
    def _initialize_pool(self):
        """Initialize the pool with initial connections"""
        try:
            for _ in range(min(3, self.max_connections)):
                conn = self._create_connection()
                if conn:
                    self._pool.put(conn)
                    self._total_connections_created += 1
        except Exception as e:
            if logger:
                logger.error(f"Failed to initialize connection pool: {e}")
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection with proper configuration"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=20.0)
            conn.row_factory = sqlite3.Row  # Set row_factory for consistent dictionary access
            
            # Enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Set WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode = WAL")
            
            # Set synchronous mode for better performance
            conn.execute("PRAGMA synchronous = NORMAL")
            
            # Set cache size for better performance
            conn.execute("PRAGMA cache_size = 10000")
            
            # Set temp store to memory for better performance
            conn.execute("PRAGMA temp_store = MEMORY")
            
            return conn
        except sqlite3.Error as e:
            if logger:
                logger.error(f"Failed to create database connection: {e}")
            return None
    
    def _is_connection_healthy(self, conn: sqlite3.Connection) -> bool:
        """Check if a connection is still healthy and usable"""
        try:
            # Simple health check - try to execute a lightweight query
            conn.execute("SELECT 1")
            return True
        except (sqlite3.Error, sqlite3.OperationalError):
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
        """Perform periodic health check on connections"""
        current_time = time.time()
        if current_time - self._last_health_check < self.check_interval:
            return
        
        self._last_health_check = current_time
        
        # Check connections in the pool
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
        
        # Put healthy connections back in the pool
        for conn in healthy_connections:
            try:
                self._pool.put_nowait(conn)
            except:
                self._cleanup_connection(conn)
                self._active_connections -= 1
        
        if logger:
            logger.debug(f"Health check completed. Pool size: {self._pool.qsize()}, "
                        f"Active connections: {self._active_connections}")
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection from the pool.
        
        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM leads")
                results = cursor.fetchall()
        """
        conn = None
        try:
            # Perform health check if needed
            self._health_check()
            
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
            
            # Verify connection is healthy
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
            if conn and self._is_connection_healthy(conn):
                try:
                    self._pool.put_nowait(conn)
                except:
                    # Pool is full, close the connection
                    self._cleanup_connection(conn)
                    self._active_connections -= 1
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of results as dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute an UPDATE, INSERT, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute the same query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
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