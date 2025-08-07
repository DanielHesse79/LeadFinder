"""
Unified Search Routes for LeadFinder

This module provides unified search endpoints that combine standard search
and AutoGPT research functionality.
"""

from flask import Blueprint, request, jsonify, render_template
from typing import Dict, Any
import logging

# Import the unified search service (RAG-compatible version)
try:
    from services.unified_search_service import get_unified_search_service
except ImportError:
    get_unified_search_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('unified_search_routes')
except ImportError:
    logger = None

unified_search_bp = Blueprint('unified_search', __name__)


@unified_search_bp.route('/unified_search', methods=['POST'])
def unified_search():
    """
    Unified search endpoint that handles both quick search and comprehensive research
    """
    if not get_unified_search_service:
        return jsonify({
            'success': False,
            'error': 'Unified search service not available'
        }), 500
    
    try:
        # Get the unified search service
        unified_search_service = get_unified_search_service()
        
        # Get search parameters
        mode = request.form.get('mode', 'quick')
        query = request.form.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        if logger:
            logger.info(f"Unified search request: mode={mode}, query={query}")
        
        # Handle different search modes
        if mode == 'quick':
            # Quick search parameters
            engines = request.form.getlist('engines') or ['google']
            use_ai_analysis = request.form.get('use_ai_analysis') == 'on'
            max_results = int(request.form.get('max_results', 10))
            research_question = request.form.get('research_question', '').strip()
            
            # Create SearchQuery object for the service
            from services.unified_search_service import SearchQuery
            search_query = SearchQuery(
                query=query,
                search_type='web',
                engines=engines,
                max_results=max_results,
                research_question=research_question
            )
            
            result = unified_search_service.search(search_query)
            
        elif mode == 'research':
            # Comprehensive research parameters
            company_name = request.form.get('company_name', '').strip()
            industry = request.form.get('industry', '').strip()
            
            if not company_name or not industry:
                return jsonify({
                    'success': False,
                    'error': 'Company name and industry are required for research mode'
                }), 400
            
            # Create SearchQuery for research
            from services.unified_search_service import SearchQuery
            search_query = SearchQuery(
                query=f"{company_name} {industry}",
                search_type='unified',
                max_results=20,
                research_question=f"Research {company_name} in {industry} industry"
            )
            
            result = unified_search_service.search(search_query)
            
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown search mode: {mode}'
            }), 400
        
        return jsonify(result)
        
    except Exception as e:
        if logger:
            logger.error(f"Unified search failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500


@unified_search_bp.route('/unified_search_form')
def unified_search_form():
    """Render the unified search form"""
    return render_template('unified_search_form.html')


@unified_search_bp.route('/search_stats')
def search_stats():
    """Get search statistics"""
    if not get_unified_search_service:
        return jsonify({
            'success': False,
            'error': 'Unified search service not available'
        }), 500
    
    try:
        unified_search_service = get_unified_search_service()
        stats = unified_search_service.get_service_status()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to get search stats: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get search stats: {str(e)}'
        }), 500


@unified_search_bp.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear search cache"""
    if not get_unified_search_service:
        return jsonify({
            'success': False,
            'error': 'Unified search service not available'
        }), 500
    
    try:
        unified_search_service = get_unified_search_service()
        unified_search_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to clear cache: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to clear cache: {str(e)}'
        }), 500 