"""
Analytics System for LeadFinder

This module provides comprehensive analytics and user behavior tracking:
- User interaction tracking
- Performance metrics collection
- Search analytics and insights
- Lead discovery analytics
- System usage patterns
- Custom event tracking
"""

import time
import json
import threading
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import uuid

try:
    from utils.redis_cache import get_redis_cache_manager
except ImportError:
    get_redis_cache_manager = None

try:
    from utils.logger import get_logger
    logger = get_logger('analytics')
except ImportError:
    logger = None

try:
    from flask import request, g
except ImportError:
    request = None
    g = None

@dataclass
class AnalyticsEvent:
    """Analytics event data"""
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: float = None
    properties: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.properties is None:
            self.properties = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SearchAnalytics:
    """Search analytics data"""
    query: str
    engines_used: List[str]
    results_count: int
    processing_time: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: float = None
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class LeadAnalytics:
    """Lead discovery analytics data"""
    lead_id: int
    source: str
    relevance_score: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: float = None
    action_taken: str = "discovered"  # discovered, viewed, exported, etc.

@dataclass
class PerformanceMetrics:
    """Performance metrics data"""
    endpoint: str
    response_time: float
    status_code: int
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: float = None
    error: Optional[str] = None

class AnalyticsTracker:
    """
    Comprehensive analytics tracking system
    """
    
    def __init__(self, redis_cache=None):
        self.redis_cache = redis_cache or get_redis_cache_manager()
        self.events = []
        self.lock = threading.Lock()
        self.session_data = {}
        
        # Analytics categories
        self.search_analytics = []
        self.lead_analytics = []
        self.performance_metrics = []
        self.user_sessions = {}
        
        # Start background processing
        self.running = True
        self._processor_thread = threading.Thread(target=self._process_events, daemon=True)
        self._processor_thread.start()
    
    def _get_session_id(self) -> str:
        """Get or create session ID"""
        if not request:
            return "no_session"
        
        session_id = getattr(g, 'session_id', None)
        if not session_id:
            session_id = str(uuid.uuid4())
            setattr(g, 'session_id', session_id)
        
        return session_id
    
    def _get_user_id(self) -> Optional[str]:
        """Get user ID from request context"""
        if not request:
            return None
        
        return getattr(g, 'user_id', None)
    
    def track_event(self, event_type: str, properties: Dict[str, Any] = None, 
                   metadata: Dict[str, Any] = None):
        """
        Track a custom analytics event
        
        Args:
            event_type: Type of event
            properties: Event properties
            metadata: Additional metadata
        """
        event = AnalyticsEvent(
            event_type=event_type,
            user_id=self._get_user_id(),
            session_id=self._get_session_id(),
            properties=properties or {},
            metadata=metadata or {}
        )
        
        with self.lock:
            self.events.append(event)
        
        if logger:
            logger.debug(f"Tracked event: {event_type}")
    
    def track_search(self, query: str, engines_used: List[str], results_count: int,
                    processing_time: float, success: bool = True, error_message: str = None):
        """
        Track search analytics
        
        Args:
            query: Search query
            engines_used: List of search engines used
            results_count: Number of results returned
            processing_time: Time taken to process search
            success: Whether search was successful
            error_message: Error message if search failed
        """
        search_data = SearchAnalytics(
            query=query,
            engines_used=engines_used,
            results_count=results_count,
            processing_time=processing_time,
            user_id=self._get_user_id(),
            session_id=self._get_session_id(),
            success=success,
            error_message=error_message
        )
        
        with self.lock:
            self.search_analytics.append(search_data)
        
        # Also track as general event
        self.track_event("search", {
            'query': query,
            'engines_used': engines_used,
            'results_count': results_count,
            'processing_time': processing_time,
            'success': success
        })
    
    def track_lead(self, lead_id: int, source: str, relevance_score: float, 
                  action_taken: str = "discovered"):
        """
        Track lead discovery analytics
        
        Args:
            lead_id: Lead ID
            source: Lead source
            relevance_score: AI relevance score
            action_taken: Action taken on lead
        """
        lead_data = LeadAnalytics(
            lead_id=lead_id,
            source=source,
            relevance_score=relevance_score,
            user_id=self._get_user_id(),
            session_id=self._get_session_id(),
            action_taken=action_taken
        )
        
        with self.lock:
            self.lead_analytics.append(lead_data)
        
        # Also track as general event
        self.track_event("lead_action", {
            'lead_id': lead_id,
            'source': source,
            'relevance_score': relevance_score,
            'action_taken': action_taken
        })
    
    def track_performance(self, endpoint: str, response_time: float, status_code: int,
                         error: str = None):
        """
        Track performance metrics
        
        Args:
            endpoint: API endpoint
            response_time: Response time in seconds
            status_code: HTTP status code
            error: Error message if any
        """
        perf_data = PerformanceMetrics(
            endpoint=endpoint,
            response_time=response_time,
            status_code=status_code,
            user_id=self._get_user_id(),
            session_id=self._get_session_id(),
            error=error
        )
        
        with self.lock:
            self.performance_metrics.append(perf_data)
        
        # Also track as general event
        self.track_event("performance", {
            'endpoint': endpoint,
            'response_time': response_time,
            'status_code': status_code,
            'error': error
        })
    
    def _process_events(self):
        """Background event processor"""
        while self.running:
            try:
                with self.lock:
                    if self.events:
                        # Process events in batches
                        batch = self.events[:100]
                        self.events = self.events[100:]
                        
                        # Store events in Redis for persistence
                        if self.redis_cache and self.redis_cache._is_healthy:
                            for event in batch:
                                event_key = f"analytics:event:{event.timestamp}:{hash(event.event_type)}"
                                self.redis_cache.set(event_key, asdict(event), ttl=86400)  # 24 hours
                        
                        # Keep only recent events in memory
                        if len(self.search_analytics) > 1000:
                            self.search_analytics = self.search_analytics[-500:]
                        if len(self.lead_analytics) > 1000:
                            self.lead_analytics = self.lead_analytics[-500:]
                        if len(self.performance_metrics) > 1000:
                            self.performance_metrics = self.performance_metrics[-500:]
                
                time.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                if logger:
                    logger.error(f"Error processing analytics events: {e}")
                time.sleep(5)
    
    def get_search_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get search analytics for the specified time period
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with search analytics
        """
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            recent_searches = [
                search for search in self.search_analytics
                if search.timestamp >= cutoff_time
            ]
        
        if not recent_searches:
            return {
                'total_searches': 0,
                'avg_processing_time': 0,
                'success_rate': 0,
                'top_queries': [],
                'engine_usage': {}
            }
        
        # Calculate metrics
        total_searches = len(recent_searches)
        successful_searches = sum(1 for s in recent_searches if s.success)
        avg_processing_time = sum(s.processing_time for s in recent_searches) / total_searches
        success_rate = (successful_searches / total_searches) * 100
        
        # Top queries
        query_counts = {}
        for search in recent_searches:
            query_counts[search.query] = query_counts.get(search.query, 0) + 1
        
        top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Engine usage
        engine_usage = {}
        for search in recent_searches:
            for engine in search.engines_used:
                engine_usage[engine] = engine_usage.get(engine, 0) + 1
        
        return {
            'total_searches': total_searches,
            'avg_processing_time': round(avg_processing_time, 3),
            'success_rate': round(success_rate, 2),
            'top_queries': top_queries,
            'engine_usage': engine_usage
        }
    
    def get_lead_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get lead analytics for the specified time period
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with lead analytics
        """
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            recent_leads = [
                lead for lead in self.lead_analytics
                if lead.timestamp >= cutoff_time
            ]
        
        if not recent_leads:
            return {
                'total_leads': 0,
                'avg_relevance_score': 0,
                'source_distribution': {},
                'action_distribution': {}
            }
        
        # Calculate metrics
        total_leads = len(recent_leads)
        avg_relevance_score = sum(lead.relevance_score for lead in recent_leads) / total_leads
        
        # Source distribution
        source_counts = {}
        for lead in recent_leads:
            source_counts[lead.source] = source_counts.get(lead.source, 0) + 1
        
        # Action distribution
        action_counts = {}
        for lead in recent_leads:
            action_counts[lead.action_taken] = action_counts.get(lead.action_taken, 0) + 1
        
        return {
            'total_leads': total_leads,
            'avg_relevance_score': round(avg_relevance_score, 3),
            'source_distribution': source_counts,
            'action_distribution': action_counts
        }
    
    def get_performance_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get performance analytics for the specified time period
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with performance analytics
        """
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            recent_metrics = [
                metric for metric in self.performance_metrics
                if metric.timestamp >= cutoff_time
            ]
        
        if not recent_metrics:
            return {
                'total_requests': 0,
                'avg_response_time': 0,
                'error_rate': 0,
                'endpoint_performance': {}
            }
        
        # Calculate metrics
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.status_code < 400)
        avg_response_time = sum(m.response_time for m in recent_metrics) / total_requests
        error_rate = ((total_requests - successful_requests) / total_requests) * 100
        
        # Endpoint performance
        endpoint_performance = {}
        for metric in recent_metrics:
            if metric.endpoint not in endpoint_performance:
                endpoint_performance[metric.endpoint] = {
                    'count': 0,
                    'total_time': 0,
                    'errors': 0
                }
            
            endpoint_performance[metric.endpoint]['count'] += 1
            endpoint_performance[metric.endpoint]['total_time'] += metric.response_time
            if metric.status_code >= 400:
                endpoint_performance[metric.endpoint]['errors'] += 1
        
        # Calculate averages
        for endpoint in endpoint_performance:
            count = endpoint_performance[endpoint]['count']
            endpoint_performance[endpoint]['avg_time'] = endpoint_performance[endpoint]['total_time'] / count
            endpoint_performance[endpoint]['error_rate'] = (endpoint_performance[endpoint]['errors'] / count) * 100
        
        return {
            'total_requests': total_requests,
            'avg_response_time': round(avg_response_time, 3),
            'error_rate': round(error_rate, 2),
            'endpoint_performance': endpoint_performance
        }
    
    def get_user_analytics(self, user_id: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get analytics for a specific user
        
        Args:
            user_id: User ID
            hours: Number of hours to look back
            
        Returns:
            Dictionary with user analytics
        """
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            user_searches = [
                search for search in self.search_analytics
                if search.user_id == user_id and search.timestamp >= cutoff_time
            ]
            
            user_leads = [
                lead for lead in self.lead_analytics
                if lead.user_id == user_id and lead.timestamp >= cutoff_time
            ]
        
        return {
            'searches': len(user_searches),
            'leads_discovered': len(user_leads),
            'avg_search_time': sum(s.processing_time for s in user_searches) / len(user_searches) if user_searches else 0,
            'top_queries': list(set(s.query for s in user_searches)),
            'lead_sources': list(set(l.source for l in user_leads))
        }
    
    def get_comprehensive_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get comprehensive analytics overview
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with comprehensive analytics
        """
        search_analytics = self.get_search_analytics(hours)
        lead_analytics = self.get_lead_analytics(hours)
        performance_analytics = self.get_performance_analytics(hours)
        
        return {
            'period_hours': hours,
            'search': search_analytics,
            'leads': lead_analytics,
            'performance': performance_analytics,
            'summary': {
                'total_activity': search_analytics['total_searches'] + lead_analytics['total_leads'],
                'system_health': 100 - performance_analytics['error_rate'],
                'user_engagement': search_analytics['total_searches'] > 0
            }
        }
    
    def export_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Export analytics data for external analysis
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with exported analytics data
        """
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            events = [event for event in self.events if event.timestamp >= cutoff_time]
            searches = [search for search in self.search_analytics if search.timestamp >= cutoff_time]
            leads = [lead for lead in self.lead_analytics if lead.timestamp >= cutoff_time]
            metrics = [metric for metric in self.performance_metrics if metric.timestamp >= cutoff_time]
        
        return {
            'export_timestamp': time.time(),
            'period_hours': hours,
            'events': [asdict(event) for event in events],
            'searches': [asdict(search) for search in searches],
            'leads': [asdict(lead) for lead in leads],
            'performance': [asdict(metric) for metric in metrics]
        }

# Global analytics tracker instance
_analytics_tracker = None

def get_analytics_tracker() -> AnalyticsTracker:
    """Get global analytics tracker instance"""
    global _analytics_tracker
    
    if _analytics_tracker is None:
        _analytics_tracker = AnalyticsTracker()
    
    return _analytics_tracker

def track_event(event_type: str, properties: Dict[str, Any] = None, metadata: Dict[str, Any] = None):
    """Track a custom analytics event"""
    tracker = get_analytics_tracker()
    tracker.track_event(event_type, properties, metadata)

def track_search(query: str, engines_used: List[str], results_count: int, processing_time: float, 
                success: bool = True, error_message: str = None):
    """Track search analytics"""
    tracker = get_analytics_tracker()
    tracker.track_search(query, engines_used, results_count, processing_time, success, error_message)

def track_lead(lead_id: int, source: str, relevance_score: float, action_taken: str = "discovered"):
    """Track lead analytics"""
    tracker = get_analytics_tracker()
    tracker.track_lead(lead_id, source, relevance_score, action_taken)

def track_performance(endpoint: str, response_time: float, status_code: int, error: str = None):
    """Track performance metrics"""
    tracker = get_analytics_tracker()
    tracker.track_performance(endpoint, response_time, status_code, error)

def get_analytics_summary(hours: int = 24) -> Dict[str, Any]:
    """Get analytics summary"""
    tracker = get_analytics_tracker()
    return tracker.get_comprehensive_analytics(hours)

def export_analytics_data(hours: int = 24) -> Dict[str, Any]:
    """Export analytics data"""
    tracker = get_analytics_tracker()
    return tracker.export_analytics(hours) 