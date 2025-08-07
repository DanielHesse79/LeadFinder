"""
Rate Limiting System for LeadFinder

This module provides a comprehensive rate limiting system with:
- Token bucket algorithm for fair rate limiting
- Redis-based distributed rate limiting
- Per-user and per-endpoint rate limiting
- Automatic rate limit headers
- Rate limit monitoring and analytics
"""

import time
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from functools import wraps
import hashlib

try:
    from utils.redis_cache import get_redis_cache_manager
except ImportError:
    get_redis_cache_manager = None

try:
    from utils.logger import get_logger
    logger = get_logger('rate_limiter')
except ImportError:
    logger = None

try:
    from flask import request, jsonify, g
except ImportError:
    request = None
    jsonify = None
    g = None

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10
    window_size: int = 60  # seconds

@dataclass
class RateLimitResult:
    """Rate limit check result"""
    allowed: bool
    remaining: int
    reset_time: float
    limit: int
    retry_after: Optional[int] = None

class TokenBucketRateLimiter:
    """
    Token bucket rate limiter implementation
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Consume tokens from the bucket
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if bucket is empty
        """
        with self.lock:
            now = time.time()
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_remaining(self) -> int:
        """Get remaining tokens"""
        with self.lock:
            now = time.time()
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * self.refill_rate
            
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            return int(self.tokens)

class RateLimiter:
    """
    Comprehensive rate limiting system
    """
    
    def __init__(self, redis_cache=None):
        self.redis_cache = redis_cache or get_redis_cache_manager()
        self.local_limiters = {}
        self.lock = threading.Lock()
        
        # Default configurations
        self.default_config = RateLimitConfig()
        self.endpoint_configs = {}
        self.user_configs = {}
    
    def set_endpoint_config(self, endpoint: str, config: RateLimitConfig):
        """Set rate limit configuration for an endpoint"""
        self.endpoint_configs[endpoint] = config
    
    def set_user_config(self, user_id: str, config: RateLimitConfig):
        """Set rate limit configuration for a user"""
        self.user_configs[user_id] = config
    
    def _get_limiter_key(self, identifier: str, window: str) -> str:
        """Generate Redis key for rate limiter"""
        return f"rate_limit:{identifier}:{window}"
    
    def _get_user_identifier(self) -> str:
        """Get user identifier from request"""
        if not request:
            return "anonymous"
        
        # Try to get user ID from various sources
        user_id = getattr(g, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        return f"ip:{request.remote_addr}"
    
    def _get_endpoint_identifier(self) -> str:
        """Get endpoint identifier"""
        if not request:
            return "unknown"
        
        return f"endpoint:{request.endpoint}"
    
    def _check_redis_rate_limit(self, key: str, limit: int, window: int) -> RateLimitResult:
        """
        Check rate limit using Redis
        
        Args:
            key: Redis key for the rate limit
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            RateLimitResult with limit status
        """
        try:
            if not self.redis_cache or not self.redis_cache._is_healthy:
                # Fallback to local rate limiting
                return self._check_local_rate_limit(key, limit, window)
            
            current_time = time.time()
            window_start = current_time - window
            
            # Get current count from Redis
            current_count = self.redis_cache.get(key) or 0
            
            # Check if we're within the limit
            if current_count < limit:
                # Increment count
                self.redis_cache.set(key, current_count + 1, ttl=window)
                return RateLimitResult(
                    allowed=True,
                    remaining=limit - current_count - 1,
                    reset_time=current_time + window,
                    limit=limit
                )
            else:
                # Rate limit exceeded
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=current_time + window,
                    limit=limit,
                    retry_after=int(window - (current_time - window_start))
                )
                
        except Exception as e:
            if logger:
                logger.error(f"Redis rate limit check failed: {e}")
            # Fallback to local rate limiting
            return self._check_local_rate_limit(key, limit, window)
    
    def _check_local_rate_limit(self, key: str, limit: int, window: int) -> RateLimitResult:
        """
        Check rate limit using local storage
        
        Args:
            key: Rate limit key
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            RateLimitResult with limit status
        """
        with self.lock:
            if key not in self.local_limiters:
                self.local_limiters[key] = TokenBucketRateLimiter(limit, limit / window)
            
            limiter = self.local_limiters[key]
            allowed = limiter.consume(1)
            remaining = limiter.get_remaining()
            
            return RateLimitResult(
                allowed=allowed,
                remaining=remaining,
                reset_time=time.time() + window,
                limit=limit
            )
    
    def check_rate_limit(self, identifier: str, config: RateLimitConfig) -> RateLimitResult:
        """
        Check rate limit for an identifier
        
        Args:
            identifier: Rate limit identifier
            config: Rate limit configuration
            
        Returns:
            RateLimitResult with limit status
        """
        # Check per-minute limit
        minute_key = self._get_limiter_key(identifier, "minute")
        minute_result = self._check_redis_rate_limit(minute_key, config.requests_per_minute, 60)
        
        if not minute_result.allowed:
            return minute_result
        
        # Check per-hour limit
        hour_key = self._get_limiter_key(identifier, "hour")
        hour_result = self._check_redis_rate_limit(hour_key, config.requests_per_hour, 3600)
        
        if not hour_result.allowed:
            return hour_result
        
        # Check per-day limit
        day_key = self._get_limiter_key(identifier, "day")
        day_result = self._check_redis_rate_limit(day_key, config.requests_per_day, 86400)
        
        if not day_result.allowed:
            return day_result
        
        # All limits passed
        return RateLimitResult(
            allowed=True,
            remaining=min(minute_result.remaining, hour_result.remaining, day_result.remaining),
            reset_time=min(minute_result.reset_time, hour_result.reset_time, day_result.reset_time),
            limit=min(config.requests_per_minute, config.requests_per_hour, config.requests_per_day)
        )
    
    def check_request_rate_limit(self) -> RateLimitResult:
        """
        Check rate limit for current request
        
        Returns:
            RateLimitResult with limit status
        """
        if not request:
            return RateLimitResult(allowed=True, remaining=999, reset_time=time.time() + 60, limit=1000)
        
        # Get user identifier
        user_id = self._get_user_identifier()
        
        # Get endpoint identifier
        endpoint_id = self._get_endpoint_identifier()
        
        # Get configuration
        config = self.user_configs.get(user_id, self.endpoint_configs.get(endpoint_id, self.default_config))
        
        # Check rate limit
        return self.check_rate_limit(user_id, config)
    
    def get_rate_limit_headers(self, result: RateLimitResult) -> Dict[str, str]:
        """
        Generate rate limit headers
        
        Args:
            result: Rate limit result
            
        Returns:
            Dictionary of rate limit headers
        """
        headers = {
            'X-RateLimit-Limit': str(result.limit),
            'X-RateLimit-Remaining': str(result.remaining),
            'X-RateLimit-Reset': str(int(result.reset_time))
        }
        
        if result.retry_after:
            headers['Retry-After'] = str(result.retry_after)
        
        return headers

# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    
    return _rate_limiter

def rate_limit(config: RateLimitConfig = None):
    """
    Decorator for rate limiting Flask routes
    
    Args:
        config: Rate limit configuration (optional)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()
            
            # Use provided config or endpoint-specific config
            rate_config = config or limiter.endpoint_configs.get(request.endpoint, limiter.default_config)
            
            # Check rate limit
            result = limiter.check_request_rate_limit()
            
            if not result.allowed:
                headers = limiter.get_rate_limit_headers(result)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': result.retry_after
                }), 429, headers
            
            # Add rate limit headers to response
            response = func(*args, **kwargs)
            
            if isinstance(response, tuple):
                response_data, status_code, headers = response + (None,)
                headers = headers or {}
            else:
                response_data = response
                status_code = 200
                headers = {}
            
            # Add rate limit headers
            rate_headers = limiter.get_rate_limit_headers(result)
            headers.update(rate_headers)
            
            return response_data, status_code, headers
        
        return wrapper
    return decorator

def configure_rate_limits():
    """Configure default rate limits"""
    limiter = get_rate_limiter()
    
    # Configure endpoint-specific limits
    limiter.set_endpoint_config('search.perform_search', RateLimitConfig(
        requests_per_minute=30,
        requests_per_hour=500,
        requests_per_day=5000
    ))
    
    limiter.set_endpoint_config('ollama.call_ollama', RateLimitConfig(
        requests_per_minute=20,
        requests_per_hour=300,
        requests_per_day=3000
    ))
    
    limiter.set_endpoint_config('rag.generate_response', RateLimitConfig(
        requests_per_minute=15,
        requests_per_hour=200,
        requests_per_day=2000
    ))
    
    # Configure user-specific limits (for premium users)
    # limiter.set_user_config('user:123', RateLimitConfig(
    #     requests_per_minute=100,
    #     requests_per_hour=2000,
    #     requests_per_day=20000
    # ))

def get_rate_limit_stats() -> Dict[str, Any]:
    """Get rate limiting statistics"""
    limiter = get_rate_limiter()
    
    stats = {
        'total_endpoints': len(limiter.endpoint_configs),
        'total_users': len(limiter.user_configs),
        'local_limiters': len(limiter.local_limiters),
        'redis_available': limiter.redis_cache and limiter.redis_cache._is_healthy
    }
    
    return stats 