"""
Unified Search Routes for LeadFinder

This module provides unified search endpoints that combine standard search
and AutoGPT research functionality.
"""

from flask import Blueprint, request, jsonify, render_template
from typing import Dict, Any
import logging

# Import the unified search service
try:
    from services.unified_search import unified_search_service
except ImportError:
    unified_search_service = None

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
    if not unified_search_service:
        return jsonify({
            'success': False,
            'error': 'Unified search service not available'
        }), 500
    
    try:
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
            
            result = unified_search_service.quick_search(
                query=query,
                engines=engines,
                use_ai_analysis=use_ai_analysis,
                max_results=max_results,
                research_question=research_question
            )
            
        elif mode == 'research':
            # Comprehensive research parameters
            company_name = request.form.get('company_name', '').strip()
            industry = request.form.get('industry', '').strip()
            
            if not company_name or not industry:
                return jsonify({
                    'success': False,
                    'error': 'Company name and industry are required for research mode'
                }), 400
            
            result = unified_search_service.comprehensive_research(
                company_name=company_name,
                industry=industry
            )
            
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
    """
    Display the unified search form
    """
    autogpt_available = unified_search_service.is_autogpt_available() if unified_search_service else False
    
    return render_template('unified_search_form.html',
                         autogpt_available=autogpt_available)


@unified_search_bp.route('/search_stats')
def search_stats():
    """
    Get search service statistics
    """
    if not unified_search_service:
        return jsonify({
            'success': False,
            'error': 'Unified search service not available'
        }), 500
    
    try:
        cache_stats = unified_search_service.get_cache_stats()
        autogpt_available = unified_search_service.is_autogpt_available()
        
        return jsonify({
            'success': True,
            'cache_stats': cache_stats,
            'autogpt_available': autogpt_available
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to get search stats: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get stats: {str(e)}'
        }), 500


@unified_search_bp.route('/clear_cache', methods=['POST'])
def clear_cache():
    """
    Clear the search cache
    """
    if not unified_search_service:
        return jsonify({
            'success': False,
            'error': 'Unified search service not available'
        }), 500
    
    try:
        unified_search_service.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Search cache cleared successfully'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to clear cache: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to clear cache: {str(e)}'
        }), 500 