from flask import Blueprint, render_template, jsonify
from services.rag_generator import RAGGenerator
from services.vector_store_service import VectorStoreService
from models.database import get_rag_stats, get_lead_stats
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """
    Main dashboard page showing both data mining and data processing workflows
    """
    try:
        # Get system statistics
        stats = get_dashboard_stats()
        
        return render_template('dashboard.html', stats=stats)
    
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        # Return basic stats if there's an error
        stats = {
            'total_leads': 0,
            'rag_documents': 0,
            'total_searches': 0,
            'ai_analyses': 0,
            'rag_queries': 0,
            'success_rate': 0,
            'avg_response_time': 0,
            'uptime': 100
        }
        return render_template('dashboard.html', stats=stats)

@dashboard_bp.route('/api/stats')
def api_stats():
    """
    API endpoint for dashboard statistics
    """
    try:
        stats = get_dashboard_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/activity')
def api_activity():
    """
    API endpoint for recent activity
    """
    try:
        # Get recent activity from database
        activity = get_recent_activity()
        return jsonify({
            'success': True,
            'activity': activity
        })
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dashboard_bp.route('/api/system-status')
def api_system_status():
    """
    API endpoint for system status
    """
    try:
        status = get_system_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics
    """
    try:
        # Get lead statistics
        lead_stats = get_lead_stats()
        
        # Get RAG statistics
        rag_stats = get_rag_stats()
        
        # Get vector store statistics (with error handling)
        try:
            vector_store = VectorStoreService()
            vector_stats = vector_store.get_stats()
            rag_documents = vector_stats.total_documents if vector_stats else 0
        except Exception as e:
            if logger:
                logger.warning(f"Vector store stats unavailable: {e}")
            rag_documents = 0
        
        # Calculate success rate (placeholder - could be based on actual metrics)
        success_rate = 95  # Placeholder
        
        # Calculate average response time (placeholder)
        avg_response_time = 2.3  # Placeholder
        
        # Calculate uptime (placeholder)
        uptime = 99.8  # Placeholder
        
        # Ensure all values are numbers, not None
        total_leads = lead_stats.get('total_leads', 0) or 0
        total_searches = lead_stats.get('total_searches', 0) or 0
        ai_analyses = lead_stats.get('ai_analyses', 0) or 0
        rag_queries = rag_stats.get('total_sessions', 0) or 0
        
        return {
            'total_leads': total_leads,
            'rag_documents': rag_documents,
            'total_searches': total_searches,
            'ai_analyses': ai_analyses,
            'rag_queries': rag_queries,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'uptime': uptime
        }
    
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return {
            'total_leads': 0,
            'rag_documents': 0,
            'total_searches': 0,
            'ai_analyses': 0,
            'rag_queries': 0,
            'success_rate': 0,
            'avg_response_time': 0,
            'uptime': 0
        }

def get_recent_activity():
    """
    Get recent activity from the system
    """
    try:
        # This would typically query the database for recent activity
        # For now, return placeholder data
        return [
            {
                'type': 'search',
                'description': 'New search performed',
                'details': 'AI in healthcare trends',
                'time': '2 minutes ago',
                'icon': 'fas fa-search',
                'color': 'text-primary'
            },
            {
                'type': 'rag',
                'description': 'RAG query answered',
                'details': 'What are the latest AI trends?',
                'time': '5 minutes ago',
                'icon': 'fas fa-brain',
                'color': 'text-success'
            },
            {
                'type': 'ai_analysis',
                'description': 'AI analysis completed',
                'details': 'Lead relevance assessment',
                'time': '10 minutes ago',
                'icon': 'fas fa-robot',
                'color': 'text-info'
            }
        ]
    
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        return []

def get_system_status():
    """
    Get system component status
    """
    try:
        # Check RAG system status
        try:
            rag_generator = RAGGenerator()
            rag_status = 'online' if rag_generator.health_check() else 'offline'
        except Exception as e:
            if logger:
                logger.warning(f"RAG system status check failed: {e}")
            rag_status = 'offline'
        
        # Check vector store status
        try:
            vector_store = VectorStoreService()
            vector_status = 'online' if vector_store.health_check() else 'offline'
        except Exception as e:
            if logger:
                logger.warning(f"Vector store status check failed: {e}")
            vector_status = 'offline'
        
        # Check database status (placeholder)
        db_status = 'online'
        
        # Check Ollama status (placeholder - would need actual check)
        ollama_status = 'online'
        
        return {
            'ollama_service': ollama_status,
            'rag_system': rag_status,
            'vector_store': vector_status,
            'database': db_status
        }
    
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return {
            'ollama_service': 'offline',
            'rag_system': 'offline',
            'vector_store': 'offline',
            'database': 'offline'
        } 