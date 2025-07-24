"""
Research funding search routes

This module provides Flask routes for searching research funding databases
and displaying results in the web interface.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from typing import List, Dict, Any

# Import services with error handling
try:
    from services.research_service import research_service
except ImportError:
    research_service = None

try:
    from services.api_base import ResearchProject
except ImportError:
    ResearchProject = None

try:
    from utils.logger import get_logger
except ImportError:
    def get_logger(name):
        import logging
        return logging.getLogger(name)

logger = get_logger('research_routes')

research_bp = Blueprint('research', __name__)

@research_bp.route('/research')
def research_home():
    """Display research funding search interface"""
    if not research_service:
        return "Research service not available", 500
    
    try:
        # Get available APIs
        available_apis = research_service.get_available_apis()
        enabled_api_names = [api['name'] for api in available_apis if api['enabled']]
        
        # Get API status
        api_status = research_service.get_api_status()
        
        # Check AutoGPT availability
        try:
            from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
            autogpt_integration = LeadfinderAutoGPTIntegration("mistral:latest")
            autogpt_available = True
        except Exception as e:
            autogpt_available = False
        
        return render_template('research.html',
                             available_apis=available_apis,
                             api_status=api_status,
                             autogpt_available=autogpt_available)
    except Exception as e:
        logger.error(f"Error in research home: {e}")
        return f"Error: {e}", 500

@research_bp.route('/research/search', methods=['POST'])
def search_research():
    """Search research funding databases"""
    if not research_service:
        return "Research service not available", 500
    
    try:
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('research.research_home'))
        
        # Get available APIs
        available_apis = research_service.get_available_apis()
        enabled_api_names = [api['name'] for api in available_apis if api['enabled']]
        
        # Get selected APIs
        selected_apis = request.form.getlist('apis')
        max_results = int(request.form.get('max_results', 50))
        
        logger.info(f"Research search: '{query}' with APIs: {selected_apis}")
        
        # Search all APIs
        all_results = research_service.get_all_projects(query, max_results)
        
        # Filter by enabled APIs first
        all_results = [p for p in all_results if p.source in enabled_api_names]
        
        # Then filter by selected APIs if specified
        if selected_apis:
            filtered_results = []
            for project in all_results:
                if project.source.lower() in [api.lower() for api in selected_apis]:
                    filtered_results.append(project)
            all_results = filtered_results
        
        # Group results by source
        results_by_source = {}
        for project in all_results:
            source = project.source
            if source not in results_by_source:
                results_by_source[source] = []
            results_by_source[source].append(project)
        
        return render_template('research_results.html',
                             query=query,
                             results_by_source=results_by_source,
                             total_results=len(all_results),
                             selected_apis=selected_apis)
    
    except Exception as e:
        logger.error(f"Error in research search: {e}")
        return f"Search error: {e}", 500

@research_bp.route('/research/api/search')
def api_search():
    """API endpoint for research search"""
    if not research_service:
        return jsonify({'error': 'Research service not available'}), 500
    
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        max_results = int(request.args.get('max_results', 50))
        selected_apis = request.args.getlist('apis')
        
        logger.info(f"API research search: '{query}'")
        
        # Search all APIs
        all_results = research_service.get_all_projects(query, max_results)
        
        # Filter by selected APIs if specified
        if selected_apis:
            filtered_results = []
            for project in all_results:
                if project.source.lower() in [api.lower() for api in selected_apis]:
                    filtered_results.append(project)
            all_results = filtered_results
        
        # Convert to JSON-serializable format
        projects_data = []
        for project in all_results:
            project_data = {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'principal_investigator': project.principal_investigator,
                'organization': project.organization,
                'funding_amount': project.funding_amount,
                'currency': project.currency,
                'start_date': project.start_date.isoformat() if project.start_date and hasattr(project.start_date, 'isoformat') else None,
                'end_date': project.end_date.isoformat() if project.end_date and hasattr(project.end_date, 'isoformat') else None,
                'keywords': project.keywords,
                'source': project.source,
                'url': project.url
            }
            projects_data.append(project_data)
        
        return jsonify({
            'query': query,
            'total_results': len(projects_data),
            'projects': projects_data
        })
    
    except Exception as e:
        logger.error(f"Error in API research search: {e}")
        return jsonify({'error': str(e)}), 500

@research_bp.route('/research/project/<source>/<project_id>')
def project_details(source: str, project_id: str):
    """Display detailed information about a specific project"""
    if not research_service:
        return "Research service not available", 500
    
    try:
        project = research_service.get_project_details(project_id, source)
        
        if not project:
            return f"Project not found: {project_id}", 404
        
        return render_template('project_details.html',
                             project=project,
                             source=source)
    
    except Exception as e:
        logger.error(f"Error getting project details: {e}")
        return f"Error: {e}", 500

@research_bp.route('/research/api/status')
def api_status():
    """Get status of all research APIs"""
    if not research_service:
        return jsonify({'error': 'Research service not available'}), 500
    
    try:
        status = research_service.get_api_status()
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        return jsonify({'error': str(e)}), 500

@research_bp.route('/research/api/list')
def api_list():
    """Get list of available research APIs"""
    if not research_service:
        return jsonify({'error': 'Research service not available'}), 500
    
    try:
        available_apis = research_service.get_available_apis()
        return jsonify(available_apis)
    
    except Exception as e:
        logger.error(f"Error getting API list: {e}")
        return jsonify({'error': str(e)}), 500

@research_bp.route('/research/filters', methods=['POST'])
def search_with_filters():
    """Search with advanced filters"""
    if not research_service:
        return "Research service not available", 500
    
    try:
        query = request.form.get('query', '').strip()
        if not query:
            return redirect(url_for('research.research_home'))
        
        # Parse filters
        filters = {}
        
        # Organization filter
        organization = request.form.get('organization', '').strip()
        if organization:
            filters['organization'] = organization
        
        # Funding range
        min_funding = request.form.get('min_funding', '').strip()
        if min_funding:
            try:
                filters['min_funding'] = float(min_funding)
            except ValueError:
                pass
        
        max_funding = request.form.get('max_funding', '').strip()
        if max_funding:
            try:
                filters['max_funding'] = float(max_funding)
            except ValueError:
                pass
        
        # Keywords
        keywords = request.form.get('keywords', '').strip()
        if keywords:
            filters['keywords'] = [k.strip() for k in keywords.split(',')]
        
        logger.info(f"Research search with filters: '{query}' - {filters}")
        
        # Search with filters
        filtered_results = research_service.search_by_filters(query, filters)
        
        # Group results by source
        results_by_source = {}
        for project in filtered_results:
            source = project.source
            if source not in results_by_source:
                results_by_source[source] = []
            results_by_source[source].append(project)
        
        return render_template('research_results.html',
                             query=query,
                             results_by_source=results_by_source,
                             total_results=len(filtered_results),
                             filters=filters)
    
    except Exception as e:
        logger.error(f"Error in filtered research search: {e}")
        return f"Search error: {e}", 500 