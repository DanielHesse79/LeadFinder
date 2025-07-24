"""
Comprehensive Health Monitoring System for LeadFinder

This module provides a robust health monitoring system with:
- System resource monitoring (CPU, memory, disk)
- Service availability checks
- Performance metrics tracking
- Alert system for critical issues
- Health status reporting
- Historical data tracking
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import deque
import json

try:
    from utils.logger import get_logger
    logger = get_logger('health_monitor')
except ImportError:
    logger = None

try:
    from utils.error_handler import get_error_health_status
except ImportError:
    get_error_health_status = None

try:
    from utils.cache_manager import get_cache_health_status
except ImportError:
    get_cache_health_status = None

try:
    from models.database_pool import get_db_pool
except ImportError:
    get_db_pool = None

try:
    from services.unified_search_service import get_unified_search_health_status
except ImportError:
    get_unified_search_health_status = None

class HealthMetric:
    """Represents a single health metric"""
    
    def __init__(self, name: str, value: float, unit: str = "", threshold: float = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.threshold = threshold
        self.timestamp = datetime.now()
    
    def is_critical(self) -> bool:
        """Check if metric exceeds critical threshold"""
        return self.threshold is not None and self.value > self.threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'threshold': self.threshold,
            'is_critical': self.is_critical(),
            'timestamp': self.timestamp.isoformat()
        }

class HealthAlert:
    """Represents a health alert"""
    
    def __init__(self, severity: str, message: str, metric: str = None, value: float = None):
        self.severity = severity  # 'info', 'warning', 'critical'
        self.message = message
        self.metric = metric
        self.value = value
        self.timestamp = datetime.now()
        self.acknowledged = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'severity': self.severity,
            'message': self.message,
            'metric': self.metric,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged
        }

class HealthMonitor:
    """
    Comprehensive health monitoring system
    """
    
    def __init__(self, max_history_size: int = 1000, check_interval: int = 30):
        """
        Initialize health monitor
        
        Args:
            max_history_size: Maximum number of historical records to keep
            check_interval: Interval between health checks in seconds
        """
        self.max_history_size = max_history_size
        self.check_interval = check_interval
        
        # Historical data storage
        self.metric_history = deque(maxlen=max_history_size)
        self.alert_history = deque(maxlen=max_history_size)
        
        # Current health status
        self.current_metrics = {}
        self.current_alerts = []
        
        # Monitoring thread
        self._monitoring_thread = None
        self._stop_monitoring = False
        
        # Thresholds for alerts
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 5.0,  # seconds
            'error_rate': 10.0,    # percentage
            'cache_hit_rate': 30.0  # minimum percentage
        }
        
        # Start monitoring
        self._start_monitoring()
        
        if logger:
            logger.info("Health monitor initialized")
    
    def _start_monitoring(self):
        """Start the monitoring thread"""
        def monitoring_worker():
            while not self._stop_monitoring:
                try:
                    self._perform_health_check()
                    time.sleep(self.check_interval)
                except Exception as e:
                    if logger:
                        logger.error(f"Health monitoring error: {e}")
        
        self._monitoring_thread = threading.Thread(target=monitoring_worker, daemon=True)
        self._monitoring_thread.start()
    
    def _perform_health_check(self):
        """Perform a comprehensive health check"""
        metrics = []
        
        # System metrics
        metrics.extend(self._get_system_metrics())
        
        # Application metrics
        metrics.extend(self._get_application_metrics())
        
        # Service metrics
        metrics.extend(self._get_service_metrics())
        
        # Store metrics
        self.current_metrics = {metric.name: metric for metric in metrics}
        self.metric_history.append({
            'timestamp': datetime.now().isoformat(),
            'metrics': [metric.to_dict() for metric in metrics]
        })
        
        # Check for alerts
        self._check_alerts(metrics)
    
    def _get_system_metrics(self) -> List[HealthMetric]:
        """Get system resource metrics"""
        metrics = []
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(HealthMetric(
                'cpu_percent', cpu_percent, '%', self.thresholds['cpu_percent']
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics.append(HealthMetric(
                'memory_percent', memory.percent, '%', self.thresholds['memory_percent']
            ))
            metrics.append(HealthMetric('memory_available', memory.available / (1024**3), 'GB'))
            
            # Disk usage
            disk = psutil.disk_usage('/')
            metrics.append(HealthMetric(
                'disk_percent', (disk.used / disk.total) * 100, '%', self.thresholds['disk_percent']
            ))
            metrics.append(HealthMetric('disk_free', disk.free / (1024**3), 'GB'))
            
            # Network I/O
            network = psutil.net_io_counters()
            metrics.append(HealthMetric('network_bytes_sent', network.bytes_sent / (1024**2), 'MB'))
            metrics.append(HealthMetric('network_bytes_recv', network.bytes_recv / (1024**2), 'MB'))
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting system metrics: {e}")
        
        return metrics
    
    def _get_application_metrics(self) -> List[HealthMetric]:
        """Get application-specific metrics"""
        metrics = []
        
        try:
            # Process metrics
            process = psutil.Process()
            metrics.append(HealthMetric('process_cpu_percent', process.cpu_percent(), '%'))
            metrics.append(HealthMetric('process_memory_mb', process.memory_info().rss / (1024**2), 'MB'))
            metrics.append(HealthMetric('process_threads', process.num_threads()))
            
            # Database connection pool metrics
            if get_db_pool:
                try:
                    pool = get_db_pool()
                    pool_stats = pool.get_pool_stats()
                    metrics.append(HealthMetric('db_pool_size', pool_stats['pool_size']))
                    metrics.append(HealthMetric('db_active_connections', pool_stats['active_connections']))
                    metrics.append(HealthMetric('db_total_connections', pool_stats['total_connections_created']))
                except Exception as e:
                    if logger:
                        logger.error(f"Error getting database pool metrics: {e}")
            
            # Cache metrics
            if get_cache_health_status:
                try:
                    cache_health = get_cache_health_status()
                    if cache_health['status'] != 'error':
                        cache_stats = cache_health['stats']
                        metrics.append(HealthMetric(
                            'cache_hit_rate', cache_stats['hit_rate'], '%', self.thresholds['cache_hit_rate']
                        ))
                        metrics.append(HealthMetric('cache_size', cache_stats['size']))
                        metrics.append(HealthMetric('cache_max_size', cache_stats['max_size']))
                except Exception as e:
                    if logger:
                        logger.error(f"Error getting cache metrics: {e}")
            
            # Error handling metrics
            if get_error_health_status:
                try:
                    error_health = get_error_health_status()
                    if error_health['status'] != 'error':
                        total_errors = error_health['total_errors']
                        high_errors = error_health['severity_distribution']['HIGH']
                        metrics.append(HealthMetric('total_errors', total_errors))
                        metrics.append(HealthMetric('high_severity_errors', high_errors))
                except Exception as e:
                    if logger:
                        logger.error(f"Error getting error handling metrics: {e}")
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting application metrics: {e}")
        
        return metrics
    
    def _get_service_metrics(self) -> List[HealthMetric]:
        """Get service availability metrics"""
        metrics = []
        
        try:
            # Unified search service
            if get_unified_search_health_status:
                try:
                    search_health = get_unified_search_health_status()
                    if search_health['status'] != 'error':
                        metrics.append(HealthMetric('search_available_services', search_health['available_services']))
                        metrics.append(HealthMetric('search_total_services', search_health['total_services']))
                        
                        # Calculate service availability percentage
                        if search_health['total_services'] > 0:
                            availability = (search_health['available_services'] / search_health['total_services']) * 100
                            metrics.append(HealthMetric('search_availability', availability, '%'))
                except Exception as e:
                    if logger:
                        logger.error(f"Error getting search service metrics: {e}")
            
            # Response time simulation (could be replaced with actual endpoint testing)
            response_time = self._measure_response_time()
            metrics.append(HealthMetric(
                'response_time', response_time, 's', self.thresholds['response_time']
            ))
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting service metrics: {e}")
        
        return metrics
    
    def _measure_response_time(self) -> float:
        """Measure response time for health check endpoint"""
        try:
            import requests
            start_time = time.time()
            response = requests.get('http://localhost:5051/health', timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return response_time
            else:
                return 10.0  # High response time for failed requests
        except Exception:
            return 10.0  # High response time for connection errors
    
    def _check_alerts(self, metrics: List[HealthMetric]):
        """Check metrics against thresholds and generate alerts"""
        new_alerts = []
        
        for metric in metrics:
            if metric.is_critical():
                alert = HealthAlert(
                    severity='critical',
                    message=f"{metric.name} is critical: {metric.value}{metric.unit}",
                    metric=metric.name,
                    value=metric.value
                )
                new_alerts.append(alert)
            elif metric.threshold and metric.value > metric.threshold * 0.8:
                # Warning at 80% of threshold
                alert = HealthAlert(
                    severity='warning',
                    message=f"{metric.name} is high: {metric.value}{metric.unit}",
                    metric=metric.name,
                    value=metric.value
                )
                new_alerts.append(alert)
        
        # Add new alerts
        self.current_alerts.extend(new_alerts)
        self.alert_history.extend(new_alerts)
        
        # Log critical alerts
        for alert in new_alerts:
            if alert.severity == 'critical':
                if logger:
                    logger.critical(f"Health alert: {alert.message}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        # Determine overall health status
        critical_alerts = [alert for alert in self.current_alerts if alert.severity == 'critical']
        warning_alerts = [alert for alert in self.current_alerts if alert.severity == 'warning']
        
        if critical_alerts:
            overall_status = 'critical'
        elif warning_alerts:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'metrics': {name: metric.to_dict() for name, metric in self.current_metrics.items()},
            'alerts': {
                'current': [alert.to_dict() for alert in self.current_alerts],
                'critical_count': len(critical_alerts),
                'warning_count': len(warning_alerts)
            },
            'system_info': self._get_system_info()
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                'platform': psutil.sys.platform,
                'python_version': psutil.sys.version,
                'cpu_count': psutil.cpu_count(),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'uptime': time.time() - psutil.boot_time()
            }
        except Exception as e:
            if logger:
                logger.error(f"Error getting system info: {e}")
            return {}
    
    def get_metric_history(self, metric_name: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metric history for the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = []
        
        for record in self.metric_history:
            record_time = datetime.fromisoformat(record['timestamp'])
            if record_time >= cutoff_time:
                if metric_name:
                    # Filter by specific metric
                    for metric in record['metrics']:
                        if metric['name'] == metric_name:
                            history.append({
                                'timestamp': record['timestamp'],
                                'metric': metric
                            })
                else:
                    # Return all metrics
                    history.append(record)
        
        return history
    
    def get_alert_history(self, severity: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for the specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = []
        
        for alert in self.alert_history:
            if alert.timestamp >= cutoff_time:
                if severity is None or alert.severity == severity:
                    history.append(alert.to_dict())
        
        return history
    
    def acknowledge_alert(self, alert_index: int):
        """Acknowledge an alert"""
        if 0 <= alert_index < len(self.current_alerts):
            self.current_alerts[alert_index].acknowledged = True
    
    def clear_alerts(self):
        """Clear all current alerts"""
        self.current_alerts.clear()
    
    def set_threshold(self, metric_name: str, threshold: float):
        """Set threshold for a metric"""
        self.thresholds[metric_name] = threshold
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get all thresholds"""
        return self.thresholds.copy()
    
    def stop(self):
        """Stop the health monitor"""
        self._stop_monitoring = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        if logger:
            logger.info("Health monitor stopped")

# Global health monitor instance
_health_monitor = None

def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor

def stop_health_monitor():
    """Stop the global health monitor"""
    global _health_monitor
    if _health_monitor:
        _health_monitor.stop()
        _health_monitor = None

# Health check endpoint helper
def get_comprehensive_health_status() -> Dict[str, Any]:
    """Get comprehensive health status for all systems"""
    try:
        monitor = get_health_monitor()
        health_status = monitor.get_health_status()
        
        # Add component-specific health checks
        component_health = {}
        
        # Database health
        if get_db_pool:
            try:
                pool = get_db_pool()
                pool_stats = pool.get_pool_stats()
                component_health['database'] = {
                    'status': 'healthy' if pool_stats['pool_size'] > 0 else 'warning',
                    'pool_stats': pool_stats
                }
            except Exception as e:
                component_health['database'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Cache health
        if get_cache_health_status:
            try:
                cache_health = get_cache_health_status()
                component_health['cache'] = cache_health
            except Exception as e:
                component_health['cache'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Error handling health
        if get_error_health_status:
            try:
                error_health = get_error_health_status()
                component_health['error_handling'] = error_health
            except Exception as e:
                component_health['error_handling'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Search service health
        if get_unified_search_health_status:
            try:
                search_health = get_unified_search_health_status()
                component_health['search_services'] = search_health
            except Exception as e:
                component_health['search_services'] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        health_status['components'] = component_health
        
        return health_status
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        } 