"""
Progress Tracking Routes

This module provides endpoints for tracking progress of operations.
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any
import logging

try:
    from utils.progress_manager import get_progress_manager, ProgressStatus
    from utils.logger import get_logger
    logger = get_logger('progress_routes')
except ImportError:
    logger = None
    get_progress_manager = None

progress_bp = Blueprint('progress', __name__)


@progress_bp.route('/progress/<operation_id>')
def get_progress(operation_id: str):
    """Get progress for a specific operation"""
    if not get_progress_manager:
        return jsonify({
            'success': False,
            'error': 'Progress manager not available'
        }), 500
    
    try:
        progress_manager = get_progress_manager()
        operation = progress_manager.get_operation(operation_id)
        
        if not operation:
            return jsonify({
                'success': False,
                'error': 'Operation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'operation': operation.to_dict()
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Error getting progress: {e}")
        return jsonify({
            'success': False,
            'error': f'Error getting progress: {str(e)}'
        }), 500


@progress_bp.route('/progress/<operation_id>/stream')
def stream_progress(operation_id: str):
    """Stream progress updates for a specific operation"""
    if not get_progress_manager:
        return jsonify({
            'success': False,
            'error': 'Progress manager not available'
        }), 500
    
    try:
        progress_manager = get_progress_manager()
        operation = progress_manager.get_operation(operation_id)
        
        if not operation:
            return jsonify({
                'success': False,
                'error': 'Operation not found'
            }), 404
        
        # For now, return the current state
        # In a real implementation, this would use Server-Sent Events or WebSockets
        return jsonify({
            'success': True,
            'operation': operation.to_dict(),
            'streaming': True
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Error streaming progress: {e}")
        return jsonify({
            'success': False,
            'error': f'Error streaming progress: {str(e)}'
        }), 500


@progress_bp.route('/progress/active')
def get_active_operations():
    """Get all active operations"""
    if not get_progress_manager:
        return jsonify({
            'success': False,
            'error': 'Progress manager not available'
        }), 500
    
    try:
        progress_manager = get_progress_manager()
        active_operations = []
        
        for operation in progress_manager.operations.values():
            if operation.status in [ProgressStatus.PENDING, ProgressStatus.RUNNING]:
                active_operations.append(operation.to_dict())
        
        return jsonify({
            'success': True,
            'operations': active_operations
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Error getting active operations: {e}")
        return jsonify({
            'success': False,
            'error': f'Error getting active operations: {str(e)}'
        }), 500


@progress_bp.route('/progress/recent')
def get_recent_operations():
    """Get recent completed operations"""
    if not get_progress_manager:
        return jsonify({
            'success': False,
            'error': 'Progress manager not available'
        }), 500
    
    try:
        progress_manager = get_progress_manager()
        recent_operations = []
        
        for operation in progress_manager.operations.values():
            if operation.status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED]:
                recent_operations.append(operation.to_dict())
        
        # Sort by end time, most recent first
        recent_operations.sort(key=lambda x: x.get('end_time', ''), reverse=True)
        
        # Limit to last 10 operations
        recent_operations = recent_operations[:10]
        
        return jsonify({
            'success': True,
            'operations': recent_operations
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Error getting recent operations: {e}")
        return jsonify({
            'success': False,
            'error': f'Error getting recent operations: {str(e)}'
        }), 500


@progress_bp.route('/progress/cleanup', methods=['POST'])
def cleanup_old_operations():
    """Clean up old completed operations"""
    if not get_progress_manager:
        return jsonify({
            'success': False,
            'error': 'Progress manager not available'
        }), 500
    
    try:
        progress_manager = get_progress_manager()
        max_age_hours = request.json.get('max_age_hours', 24) if request.is_json else 24
        
        progress_manager.cleanup_old_operations(max_age_hours)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up operations older than {max_age_hours} hours'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Error cleaning up operations: {e}")
        return jsonify({
            'success': False,
            'error': f'Error cleaning up operations: {str(e)}'
        }), 500 