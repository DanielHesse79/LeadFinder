"""
Comprehensive Error Handling System for LeadFinder

This module provides a centralized error handling system with:
- Custom exception classes
- Error logging and monitoring
- User-friendly error messages
- Error recovery strategies
- Performance monitoring
"""

import traceback
import sys
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime
import json

# Flask imports for error handlers
try:
    from flask import request, render_template, jsonify
except ImportError:
    request = None
    render_template = None
    jsonify = None

try:
    from utils.logger import get_logger
    logger = get_logger('error_handler')
except ImportError:
    logger = None

# Custom Exception Classes
class LeadFinderError(Exception):
    """Base exception class for LeadFinder application"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()

class DatabaseError(LeadFinderError):
    """Database-related errors"""
    def __init__(self, message: str, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "DATABASE_ERROR", details)
        self.operation = operation

class APIServiceError(LeadFinderError):
    """API service errors"""
    def __init__(self, message: str, service: str = None, endpoint: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "API_SERVICE_ERROR", details)
        self.service = service
        self.endpoint = endpoint

class ConfigurationError(LeadFinderError):
    """Configuration-related errors"""
    def __init__(self, message: str, config_key: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_key = config_key

class ValidationError(LeadFinderError):
    """Data validation errors"""
    def __init__(self, message: str, field: str = None, value: Any = None, details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value

class AIProcessingError(LeadFinderError):
    """AI/ML processing errors"""
    def __init__(self, message: str, model: str = None, operation: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "AI_PROCESSING_ERROR", details)
        self.model = model
        self.operation = operation

class ExternalServiceError(LeadFinderError):
    """External service errors"""
    def __init__(self, message: str, service: str = None, status_code: int = None, details: Dict[str, Any] = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)
        self.service = service
        self.status_code = status_code

class ResourceExhaustedError(LeadFinderError):
    """Resource exhaustion errors"""
    def __init__(self, message: str, resource_type: str = None, limit: Any = None, details: Dict[str, Any] = None):
        super().__init__(message, "RESOURCE_EXHAUSTED_ERROR", details)
        self.resource_type = resource_type
        self.limit = limit

# Error Categories
ERROR_CATEGORIES = {
    'DATABASE_ERROR': {
        'severity': 'HIGH',
        'recoverable': True,
        'user_message': 'Database operation failed. Please try again.',
        'retry_strategy': 'exponential_backoff'
    },
    'API_SERVICE_ERROR': {
        'severity': 'MEDIUM',
        'recoverable': True,
        'user_message': 'Service temporarily unavailable. Please try again.',
        'retry_strategy': 'linear_backoff'
    },
    'CONFIGURATION_ERROR': {
        'severity': 'HIGH',
        'recoverable': False,
        'user_message': 'System configuration error. Please contact support.',
        'retry_strategy': 'none'
    },
    'VALIDATION_ERROR': {
        'severity': 'LOW',
        'recoverable': True,
        'user_message': 'Invalid input data. Please check your input.',
        'retry_strategy': 'none'
    },
    'AI_PROCESSING_ERROR': {
        'severity': 'MEDIUM',
        'recoverable': True,
        'user_message': 'AI processing failed. Please try again.',
        'retry_strategy': 'exponential_backoff'
    },
    'EXTERNAL_SERVICE_ERROR': {
        'severity': 'MEDIUM',
        'recoverable': True,
        'user_message': 'External service error. Please try again later.',
        'retry_strategy': 'linear_backoff'
    },
    'RESOURCE_EXHAUSTED_ERROR': {
        'severity': 'HIGH',
        'recoverable': False,
        'user_message': 'System resources exhausted. Please try again later.',
        'retry_strategy': 'wait_and_retry'
    },
    'GENERAL_ERROR': {
        'severity': 'MEDIUM',
        'recoverable': True,
        'user_message': 'An unexpected error occurred. Please try again.',
        'retry_strategy': 'linear_backoff'
    }
}

class ErrorHandler:
    """Centralized error handling and monitoring"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
        self.max_history_size = 1000
        self.alert_thresholds = {
            'HIGH': 5,      # Alert after 5 high severity errors
            'MEDIUM': 10,   # Alert after 10 medium severity errors
            'LOW': 20       # Alert after 20 low severity errors
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle an error and return error information
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            Dictionary with error information and user message
        """
        # Convert to LeadFinderError if needed
        if not isinstance(error, LeadFinderError):
            error = LeadFinderError(str(error))
        
        # Get error category information
        category_info = ERROR_CATEGORIES.get(error.error_code, ERROR_CATEGORIES['GENERAL_ERROR'])
        
        # Log the error
        self._log_error(error, context, category_info)
        
        # Update error counts
        self._update_error_counts(error.error_code, category_info['severity'])
        
        # Check for alerts
        self._check_alerts(error.error_code, category_info['severity'])
        
        # Prepare response
        response = {
            'success': False,
            'error_code': error.error_code,
            'message': category_info['user_message'],
            'recoverable': category_info['recoverable'],
            'retry_strategy': category_info['retry_strategy'],
            'timestamp': error.timestamp.isoformat()
        }
        
        # Add debug information in development
        if self._is_development_mode():
            response['debug'] = {
                'original_message': error.message,
                'details': error.details,
                'traceback': error.traceback
            }
        
        return response
    
    def _log_error(self, error: LeadFinderError, context: Dict[str, Any], category_info: Dict[str, Any]):
        """Log error with appropriate level"""
        log_message = f"Error {error.error_code}: {error.message}"
        
        if context:
            log_message += f" | Context: {json.dumps(context, default=str)}"
        
        if category_info['severity'] == 'HIGH':
            if logger:
                logger.error(log_message, exc_info=True)
        elif category_info['severity'] == 'MEDIUM':
            if logger:
                logger.warning(log_message, exc_info=True)
        else:
            if logger:
                logger.info(log_message, exc_info=True)
        
        # Store in history
        self.error_history.append({
            'timestamp': error.timestamp,
            'error_code': error.error_code,
            'message': error.message,
            'severity': category_info['severity'],
            'context': context
        })
        
        # Trim history if too large
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _update_error_counts(self, error_code: str, severity: str):
        """Update error count tracking"""
        if error_code not in self.error_counts:
            self.error_counts[error_code] = {
                'count': 0,
                'severity': severity,
                'first_occurrence': datetime.now(),
                'last_occurrence': datetime.now()
            }
        
        self.error_counts[error_code]['count'] += 1
        self.error_counts[error_code]['last_occurrence'] = datetime.now()
    
    def _check_alerts(self, error_code: str, severity: str):
        """Check if error threshold is exceeded and alert"""
        threshold = self.alert_thresholds.get(severity, 10)
        count = self.error_counts.get(error_code, {}).get('count', 0)
        
        if count >= threshold:
            alert_message = f"Error threshold exceeded: {error_code} ({count} occurrences)"
            if logger:
                logger.critical(alert_message)
            
            # Here you could add additional alert mechanisms:
            # - Send email notification
            # - Create monitoring ticket
            # - Trigger automated recovery
    
    def _is_development_mode(self) -> bool:
        """Check if running in development mode"""
        try:
            from config import config
            return config.get('FLASK_DEBUG', 'False').lower() == 'true'
        except:
            return False
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        return {
            'total_errors': sum(count['count'] for count in self.error_counts.values()),
            'error_counts': self.error_counts,
            'recent_errors': self.error_history[-10:] if self.error_history else [],
            'severity_distribution': self._get_severity_distribution()
        }
    
    def _get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of errors by severity"""
        distribution = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for error_info in self.error_counts.values():
            severity = error_info['severity']
            distribution[severity] += error_info['count']
        return distribution
    
    def clear_error_history(self):
        """Clear error history (useful for testing)"""
        self.error_history.clear()
        self.error_counts.clear()

# Global error handler instance
error_handler = ErrorHandler()

# Decorator for automatic error handling
def handle_errors(func: Callable) -> Callable:
    """Decorator to automatically handle errors in functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = {
                'function': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            }
            return error_handler.handle_error(e, context)
    return wrapper

# Context manager for error handling
class ErrorContext:
    """Context manager for error handling with custom context"""
    
    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}
        self.original_excepthook = sys.excepthook
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            if isinstance(exc_val, LeadFinderError):
                error_handler.handle_error(exc_val, self.context)
            else:
                error = LeadFinderError(str(exc_val))
                error_handler.handle_error(error, self.context)
        return False  # Don't suppress the exception

# Utility functions for common error scenarios
def handle_database_error(operation: str, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle database errors specifically"""
    db_error = DatabaseError(str(error), operation, context or {})
    return error_handler.handle_error(db_error, context)

def handle_api_error(service: str, endpoint: str, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle API service errors specifically"""
    api_error = APIServiceError(str(error), service, endpoint, context or {})
    return error_handler.handle_error(api_error, context)

def handle_validation_error(field: str, value: Any, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle validation errors specifically"""
    validation_error = ValidationError(message, field, value, context or {})
    return error_handler.handle_error(validation_error, context)

def handle_ai_error(model: str, operation: str, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle AI processing errors specifically"""
    ai_error = AIProcessingError(str(error), model, operation, context or {})
    return error_handler.handle_error(ai_error, context)

def handle_resource_error(resource_type: str, limit: Any, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Handle resource exhaustion errors specifically"""
    resource_error = ResourceExhaustedError(str(error), resource_type, limit, context or {})
    return error_handler.handle_error(resource_error, context)

# Flask-specific error handling
def register_flask_error_handlers(app):
    """Register error handlers for Flask application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        context = {}
        if request:
            context = {'route': request.path, 'method': request.method}
        error_info = error_handler.handle_error(
            LeadFinderError("Page not found", "NOT_FOUND_ERROR", context),
            context
        )
        if render_template:
            return render_template('404.html', error=error_info), 404
        else:
            return jsonify(error_info), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        context = {}
        if request:
            context = {'route': request.path, 'method': request.method}
        error_info = error_handler.handle_error(
            LeadFinderError("Internal server error", "INTERNAL_ERROR", context),
            context
        )
        if render_template:
            return render_template('500.html', error=error_info), 500
        else:
            return jsonify(error_info), 500
    
    @app.errorhandler(LeadFinderError)
    def handle_leadfinder_error(error):
        error_info = error_handler.handle_error(error)
        return jsonify(error_info), 500
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        context = {}
        if request:
            context = {'route': request.path, 'method': request.method}
        error_info = error_handler.handle_error(error, context)
        return jsonify(error_info), 500

# Health check endpoint for error monitoring
def get_error_health_status() -> Dict[str, Any]:
    """Get error handling system health status"""
    stats = error_handler.get_error_stats()
    
    # Determine health status
    high_severity_errors = stats['severity_distribution']['HIGH']
    medium_severity_errors = stats['severity_distribution']['MEDIUM']
    
    if high_severity_errors > 10:
        status = 'critical'
    elif high_severity_errors > 5 or medium_severity_errors > 20:
        status = 'warning'
    else:
        status = 'healthy'
    
    return {
        'status': status,
        'total_errors': stats['total_errors'],
        'severity_distribution': stats['severity_distribution'],
        'recent_errors_count': len(stats['recent_errors']),
        'error_counts': len(stats['error_counts'])
    } 