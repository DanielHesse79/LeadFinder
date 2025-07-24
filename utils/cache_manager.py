"""
Comprehensive Caching System for LeadFinder

This module provides a robust caching system with:
- In-memory caching with TTL (Time To Live)
- Cache statistics and monitoring
- Automatic cleanup of expired entries
- Thread-safe operations
- Cache invalidation strategies
- Performance optimization
"""

import time
import threading
import hashlib
import json
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime, timedelta
from collections import OrderedDict
from functools import wraps

try:
    from utils.logger import get_logger
    logger = get_logger('cache_manager')
except ImportError:
    logger = None

class CacheEntry:
    """Represents a single cache entry"""
    
    def __init__(self, key: str, value: Any, ttl: int = 300):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        self.ttl = ttl  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return time.time() - self.created_at > self.ttl
    
    def access(self):
        """Mark the entry as accessed"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def get_age(self) -> float:
        """Get the age of the entry in seconds"""
        return time.time() - self.created_at
    
    def get_remaining_ttl(self) -> float:
        """Get remaining TTL in seconds"""
        return max(0, self.ttl - self.get_age())

class CacheManager:
    """
    Thread-safe cache manager with TTL support
    
    Features:
    - LRU (Least Recently Used) eviction policy
    - TTL (Time To Live) for automatic expiration
    - Cache statistics and monitoring
    - Automatic cleanup of expired entries
    - Thread-safe operations
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300, cleanup_interval: int = 60):
        """
        Initialize the cache manager
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default TTL in seconds
            cleanup_interval: Interval for cleanup in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        
        # Thread-safe cache storage
        self._cache = OrderedDict()
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'expired': 0,
            'evicted': 0
        }
        
        # Start cleanup thread
        self._cleanup_thread = None
        self._stop_cleanup = False
        self._start_cleanup_thread()
        
        if logger:
            logger.info(f"Cache manager initialized with max_size={max_size}, default_ttl={default_ttl}s")
    
    def _start_cleanup_thread(self):
        """Start the cleanup thread"""
        def cleanup_worker():
            while not self._stop_cleanup:
                try:
                    time.sleep(self.cleanup_interval)
                    self._cleanup_expired()
                except Exception as e:
                    if logger:
                        logger.error(f"Cache cleanup error: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                self._stats['expired'] += 1
            
            if expired_keys and logger:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if self._cache:
            # Remove the oldest entry (first in OrderedDict)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._stats['evicted'] += 1
            
            if logger:
                logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        # Create a string representation of the arguments
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from cache
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                if entry.is_expired():
                    # Remove expired entry
                    del self._cache[key]
                    self._stats['expired'] += 1
                    self._stats['misses'] += 1
                    return default
                
                # Mark as accessed and move to end (LRU)
                entry.access()
                self._cache.move_to_end(key)
                self._stats['hits'] += 1
                return entry.value
            else:
                self._stats['misses'] += 1
                return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successful
        """
        with self._lock:
            # Evict if cache is full
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            # Create cache entry
            entry = CacheEntry(key, value, ttl or self.default_ttl)
            self._cache[key] = entry
            self._cache.move_to_end(key)  # Move to end (LRU)
            self._stats['sets'] += 1
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key was found and deleted
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['deletes'] += 1
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            if logger:
                logger.info("Cache cleared")
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache and is not expired"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_expired():
                    del self._cache[key]
                    self._stats['expired'] += 1
                    return False
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'sets': self._stats['sets'],
                'deletes': self._stats['deletes'],
                'expired': self._stats['expired'],
                'evicted': self._stats['evicted'],
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a cache entry"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                return {
                    'key': entry.key,
                    'created_at': datetime.fromtimestamp(entry.created_at).isoformat(),
                    'last_accessed': datetime.fromtimestamp(entry.last_accessed).isoformat(),
                    'access_count': entry.access_count,
                    'ttl': entry.ttl,
                    'age': round(entry.get_age(), 2),
                    'remaining_ttl': round(entry.get_remaining_ttl(), 2),
                    'is_expired': entry.is_expired(),
                    'value_type': type(entry.value).__name__
                }
            return None
    
    def get_all_keys(self) -> list:
        """Get all cache keys"""
        with self._lock:
            return list(self._cache.keys())
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching a pattern
        
        Args:
            pattern: Pattern to match (simple substring match)
            
        Returns:
            Number of entries invalidated
        """
        with self._lock:
            keys_to_delete = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self._cache[key]
                self._stats['deletes'] += 1
            
            if logger:
                logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")
            
            return len(keys_to_delete)
    
    def stop(self):
        """Stop the cache manager and cleanup thread"""
        self._stop_cleanup = True
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        if logger:
            logger.info("Cache manager stopped")

# Global cache instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def stop_cache_manager():
    """Stop the global cache manager"""
    global _cache_manager
    if _cache_manager:
        _cache_manager.stop()
        _cache_manager = None

# Decorator for function caching
def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{cache._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Cache utilities for common operations
class CacheUtils:
    """Utility functions for common caching operations"""
    
    @staticmethod
    def cache_api_response(service: str, endpoint: str, params: Dict[str, Any], ttl: int = 300):
        """Cache API response with service-specific key"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache = get_cache_manager()
                
                # Create cache key from service, endpoint, and parameters
                param_str = json.dumps(params, sort_keys=True) if params else ""
                cache_key = f"api:{service}:{endpoint}:{hashlib.md5(param_str.encode()).hexdigest()}"
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def cache_database_query(table: str, operation: str, params: Dict[str, Any], ttl: int = 60):
        """Cache database query results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache = get_cache_manager()
                
                # Create cache key from table, operation, and parameters
                param_str = json.dumps(params, sort_keys=True) if params else ""
                cache_key = f"db:{table}:{operation}:{hashlib.md5(param_str.encode()).hexdigest()}"
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_table_cache(table: str):
        """Invalidate all cache entries for a specific table"""
        cache = get_cache_manager()
        return cache.invalidate_pattern(f"db:{table}:")
    
    @staticmethod
    def invalidate_service_cache(service: str):
        """Invalidate all cache entries for a specific service"""
        cache = get_cache_manager()
        return cache.invalidate_pattern(f"api:{service}:")

# Health check for cache system
def get_cache_health_status() -> Dict[str, Any]:
    """Get cache system health status"""
    try:
        cache = get_cache_manager()
        stats = cache.get_stats()
        
        # Determine health status based on hit rate and size
        hit_rate = stats['hit_rate']
        size_ratio = stats['size'] / stats['max_size'] if stats['max_size'] > 0 else 0
        
        if hit_rate < 50 and size_ratio > 0.8:
            status = 'warning'
        elif hit_rate < 30:
            status = 'critical'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'stats': stats,
            'size_ratio': round(size_ratio * 100, 2)
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        } 