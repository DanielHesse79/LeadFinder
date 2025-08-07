"""
Redis Caching System for LeadFinder

This module provides a comprehensive Redis caching system with:
- Connection pooling and health monitoring
- TTL-based expiration
- Cache invalidation strategies
- Performance metrics tracking
- Graceful fallback to in-memory cache
"""

import redis
import json
import time
import threading
from typing import Any, Optional, Dict, List, Union
from functools import wraps
from datetime import datetime, timedelta
import hashlib

try:
    from utils.logger import get_logger
    logger = get_logger('redis_cache')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

class RedisCacheError(Exception):
    """Redis cache specific errors"""
    pass

class RedisCacheManager:
    """
    Comprehensive Redis caching system with fallback to in-memory cache
    """
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 max_connections: int = 10,
                 socket_timeout: int = 2,
                 socket_connect_timeout: int = 2,
                 retry_on_timeout: bool = True,
                 health_check_interval: int = 30):
        
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.retry_on_timeout = retry_on_timeout
        self.health_check_interval = health_check_interval
        
        # Connection pool
        self._pool = None
        self._redis_client = None
        self._connection_lock = threading.Lock()
        
        # Fallback in-memory cache
        self._fallback_cache = {}
        self._fallback_ttl = {}
        self._fallback_lock = threading.Lock()
        
        # Health monitoring
        self._last_health_check = 0
        self._is_healthy = False
        self._health_check_thread = None
        self._stop_health_check = False
        
        # Performance metrics
        self._metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0,
            'fallback_uses': 0
        }
        self._metrics_lock = threading.Lock()
        
        # Initialize connection (non-blocking)
        self._initialize_connection()
        self._start_health_check()
    
    def _initialize_connection(self):
        """Initialize Redis connection with connection pooling (non-blocking)"""
        try:
            self._pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                decode_responses=True
            )
            
            self._redis_client = redis.Redis(connection_pool=self._pool)
            
            # Don't test connection immediately - let health check handle it
            self._is_healthy = False
            
            if logger:
                logger.info(f"Redis client initialized (connection test deferred)")
                
        except Exception as e:
            if logger:
                logger.warning(f"Redis initialization failed: {e}. Using fallback cache.")
            self._is_healthy = False
            self._redis_client = None
    
    def _start_health_check(self):
        """Start health check thread"""
        if self._health_check_thread is None:
            self._health_check_thread = threading.Thread(
                target=self._health_check_worker,
                daemon=True
            )
            self._health_check_thread.start()
    
    def _health_check_worker(self):
        """Health check worker thread"""
        while not self._stop_health_check:
            try:
                if self._redis_client:
                    # Try to ping with timeout
                    self._redis_client.ping()
                    if not self._is_healthy:
                        self._is_healthy = True
                        if logger:
                            logger.info(f"Redis connection established to {self.host}:{self.port}")
                else:
                    # Try to reinitialize connection
                    self._initialize_connection()
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                if logger:
                    logger.debug(f"Redis health check failed: {e}")
                self._is_healthy = False
                time.sleep(self.health_check_interval)
    
    def _get_cache_key(self, key: str, prefix: str = "leadfinder") -> str:
        """Generate cache key with prefix"""
        return f"{prefix}:{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        if isinstance(value, (dict, list, tuple, set)):
            return json.dumps(value, default=str)
        elif isinstance(value, (int, float, str, bool)):
            return str(value)
        else:
            return json.dumps(value, default=str)
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from Redis storage"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def set(self, key: str, value: Any, ttl: int = 3600, 
            prefix: str = "leadfinder") -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            prefix: Key prefix
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._get_cache_key(key, prefix)
        serialized_value = self._serialize_value(value)
        
        try:
            if self._redis_client and self._is_healthy:
                result = self._redis_client.setex(cache_key, ttl, serialized_value)
                self._update_metrics('sets')
                return result
            else:
                # Fallback to in-memory cache
                with self._fallback_lock:
                    self._fallback_cache[cache_key] = serialized_value
                    self._fallback_ttl[cache_key] = time.time() + ttl
                    self._update_metrics('fallback_uses')
                    return True
                    
        except Exception as e:
            if logger:
                logger.error(f"Cache set error: {e}")
            self._update_metrics('errors')
            return False
    
    def get(self, key: str, prefix: str = "leadfinder") -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            prefix: Key prefix
            
        Returns:
            Cached value or None if not found
        """
        cache_key = self._get_cache_key(key, prefix)
        
        try:
            if self._redis_client and self._is_healthy:
                value = self._redis_client.get(cache_key)
                if value is not None:
                    self._update_metrics('hits')
                    return self._deserialize_value(value)
                else:
                    self._update_metrics('misses')
                    return None
            else:
                # Fallback to in-memory cache
                with self._fallback_lock:
                    if cache_key in self._fallback_cache:
                        # Check TTL
                        if time.time() < self._fallback_ttl.get(cache_key, 0):
                            value = self._fallback_cache[cache_key]
                            self._update_metrics('hits')
                            return self._deserialize_value(value)
                        else:
                            # Expired, remove from cache
                            del self._fallback_cache[cache_key]
                            if cache_key in self._fallback_ttl:
                                del self._fallback_ttl[cache_key]
                    
                    self._update_metrics('misses')
                    return None
                    
        except Exception as e:
            if logger:
                logger.error(f"Cache get error: {e}")
            self._update_metrics('errors')
            return None
    
    def delete(self, key: str, prefix: str = "leadfinder") -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            prefix: Key prefix
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._get_cache_key(key, prefix)
        
        try:
            if self._redis_client and self._is_healthy:
                result = self._redis_client.delete(cache_key)
                self._update_metrics('deletes')
                return result > 0
            else:
                # Fallback to in-memory cache
                with self._fallback_lock:
                    if cache_key in self._fallback_cache:
                        del self._fallback_cache[cache_key]
                        if cache_key in self._fallback_ttl:
                            del self._fallback_ttl[cache_key]
                        self._update_metrics('deletes')
                        return True
                    return False
                    
        except Exception as e:
            if logger:
                logger.error(f"Cache delete error: {e}")
            self._update_metrics('errors')
            return False
    
    def exists(self, key: str, prefix: str = "leadfinder") -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            prefix: Key prefix
            
        Returns:
            True if key exists, False otherwise
        """
        cache_key = self._get_cache_key(key, prefix)
        
        try:
            if self._redis_client and self._is_healthy:
                return bool(self._redis_client.exists(cache_key))
            else:
                # Fallback to in-memory cache
                with self._fallback_lock:
                    if cache_key in self._fallback_cache:
                        # Check TTL
                        if time.time() < self._fallback_ttl.get(cache_key, 0):
                            return True
                        else:
                            # Expired, remove from cache
                            del self._fallback_cache[cache_key]
                            if cache_key in self._fallback_ttl:
                                del self._fallback_ttl[cache_key]
                    return False
                    
        except Exception as e:
            if logger:
                logger.error(f"Cache exists error: {e}")
            return False
    
    def ttl(self, key: str, prefix: str = "leadfinder") -> int:
        """
        Get remaining TTL for key
        
        Args:
            key: Cache key
            prefix: Key prefix
            
        Returns:
            Remaining TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        cache_key = self._get_cache_key(key, prefix)
        
        try:
            if self._redis_client and self._is_healthy:
                return self._redis_client.ttl(cache_key)
            else:
                # Fallback to in-memory cache
                with self._fallback_lock:
                    if cache_key in self._fallback_ttl:
                        remaining = self._fallback_ttl[cache_key] - time.time()
                        return max(0, int(remaining))
                    return -2
                    
        except Exception as e:
            if logger:
                logger.error(f"Cache TTL error: {e}")
            return -2
    
    def clear_pattern(self, pattern: str, prefix: str = "leadfinder") -> int:
        """
        Clear all keys matching pattern
        
        Args:
            pattern: Key pattern to match
            prefix: Key prefix
            
        Returns:
            Number of keys deleted
        """
        try:
            if self._redis_client and self._is_healthy:
                keys = self._redis_client.keys(f"{prefix}:{pattern}")
                if keys:
                    return self._redis_client.delete(*keys)
                return 0
            else:
                # Fallback to in-memory cache
                with self._fallback_lock:
                    deleted_count = 0
                    pattern_key = f"{prefix}:{pattern}"
                    keys_to_delete = []
                    
                    for key in list(self._fallback_cache.keys()):
                        if pattern_key in key:
                            keys_to_delete.append(key)
                    
                    for key in keys_to_delete:
                        del self._fallback_cache[key]
                        if key in self._fallback_ttl:
                            del self._fallback_ttl[key]
                        deleted_count += 1
                    
                    return deleted_count
                    
        except Exception as e:
            if logger:
                logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        with self._metrics_lock:
            total_requests = self._metrics['hits'] + self._metrics['misses']
            hit_rate = (self._metrics['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            stats = {
                'hits': self._metrics['hits'],
                'misses': self._metrics['misses'],
                'sets': self._metrics['sets'],
                'deletes': self._metrics['deletes'],
                'errors': self._metrics['errors'],
                'fallback_uses': self._metrics['fallback_uses'],
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests,
                'is_healthy': self._is_healthy,
                'fallback_cache_size': len(self._fallback_cache)
            }
            
            if self._redis_client and self._is_healthy:
                try:
                    info = self._redis_client.info()
                    stats.update({
                        'redis_connected_clients': info.get('connected_clients', 0),
                        'redis_used_memory': info.get('used_memory_human', '0B'),
                        'redis_keyspace_hits': info.get('keyspace_hits', 0),
                        'redis_keyspace_misses': info.get('keyspace_misses', 0)
                    })
                except Exception:
                    pass
            
            return stats
    
    def _update_metrics(self, metric: str):
        """Update performance metrics"""
        with self._metrics_lock:
            if metric in self._metrics:
                self._metrics[metric] += 1
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get cache health status
        
        Returns:
            Dictionary with health information
        """
        return {
            'is_healthy': self._is_healthy,
            'redis_available': self._redis_client is not None,
            'fallback_active': len(self._fallback_cache) > 0,
            'connection_info': {
                'host': self.host,
                'port': self.port,
                'db': self.db
            },
            'stats': self.get_stats()
        }
    
    def close(self):
        """Close Redis connection and stop health check"""
        self._stop_health_check = True
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)
        
        if self._redis_client:
            self._redis_client.close()
        
        if self._pool:
            self._pool.disconnect()

# Global cache manager instance
_redis_cache_manager = None

def get_redis_cache_manager() -> RedisCacheManager:
    """Get global Redis cache manager instance"""
    global _redis_cache_manager
    
    if _redis_cache_manager is None:
        # Get configuration
        host = config.get('REDIS_HOST', 'localhost') if config else 'localhost'
        port = config.get('REDIS_PORT', 6379) if config else 6379
        db = config.get('REDIS_DB', 0) if config else 0
        password = config.get('REDIS_PASSWORD') if config else None
        
        _redis_cache_manager = RedisCacheManager(
            host=host,
            port=port,
            db=db,
            password=password
        )
    
    return _redis_cache_manager

def redis_cached(ttl: int = 3600, prefix: str = "leadfinder", key_func=None):
    """
    Decorator for caching function results in Redis
    
    Args:
        ttl: Time to live in seconds
        prefix: Cache key prefix
        key_func: Function to generate cache key from function args
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = get_redis_cache_manager()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend([str(arg) for arg in args])
                key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key, prefix)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl, prefix)
            
            return result
        return wrapper
    return decorator

def clear_redis_cache():
    """Clear all Redis cache"""
    cache_manager = get_redis_cache_manager()
    return cache_manager.clear_pattern("*")

def get_redis_cache_stats() -> Dict[str, Any]:
    """Get Redis cache statistics"""
    cache_manager = get_redis_cache_manager()
    return cache_manager.get_stats()

def get_redis_cache_health() -> Dict[str, Any]:
    """Get Redis cache health status"""
    cache_manager = get_redis_cache_manager()
    return cache_manager.get_health_status() 