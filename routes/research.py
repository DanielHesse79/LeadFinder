"""
Research funding search routes

This module provides Flask routes for searching research funding databases
and displaying results in the web interface.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from typing import List, Dict, Any
from datetime import datetime

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
def apply_filters():
    """Apply filters to research results"""
    try:
        filters = request.form.to_dict()
        
        # Store filters in session for persistence
        session['research_filters'] = filters
        
        flash('Filters applied successfully', 'success')
        return redirect(url_for('research.research_home'))
        
    except Exception as e:
        if logger:
            logger.error(f"Filter application failed: {e}")
        flash(f'Failed to apply filters: {str(e)}', 'error')
        return redirect(url_for('research.research_home'))


@research_bp.route('/research/funding', methods=['POST'])
def research_funding():
    """Research funding endpoint for funding data analysis"""
    try:
        data = request.get_json() or request.form.to_dict()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract parameters
        query = data.get('query', '')
        sources = data.get('sources', [])
        max_results = data.get('max_results', 50)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Initialize research results
        results = {
            'query': query,
            'sources': sources,
            'results': [],
            'total_found': 0,
            'analysis': {}
        }
        
        # Search across different funding sources
        for source in sources:
            try:
                if source == 'nsf':
                    # NSF funding search
                    nsf_results = search_nsf_funding(query, max_results)
                    results['results'].extend(nsf_results)
                    results['total_found'] += len(nsf_results)
                    
                elif source == 'nih':
                    # NIH funding search
                    nih_results = search_nih_funding(query, max_results)
                    results['results'].extend(nih_results)
                    results['total_found'] += len(nih_results)
                    
                elif source == 'cordis':
                    # CORDIS funding search
                    cordis_results = search_cordis_funding(query, max_results)
                    results['results'].extend(cordis_results)
                    results['total_found'] += len(cordis_results)
                    
                elif source == 'swecris':
                    # SweCRIS funding search
                    swecris_results = search_swecris_funding(query, max_results)
                    results['results'].extend(swecris_results)
                    results['total_found'] += len(swecris_results)
                    
            except Exception as e:
                if logger:
                    logger.error(f"Funding search failed for {source}: {e}")
                results['errors'] = results.get('errors', {})
                results['errors'][source] = str(e)
        
        # Add analysis if AI service is available
        # Assuming ollama_service is defined elsewhere or will be added
        # if ollama_service and results['results']:
        #     try:
        #         analysis_prompt = f"""
        #         Analyze the following funding opportunities for relevance:
        #         Query: {query}
        #         Number of results: {len(results['results'])}
                
        #         Provide insights on:
        #         1. Most promising opportunities
        #         2. Common themes and patterns
        #         3. Funding amounts and timelines
        #         4. Eligibility requirements
        #         5. Application deadlines
        #         """
                
        #         analysis = ollama_service.analyze_relevance(
        #             "Funding Analysis",
        #             str(results['results'][:5]),  # Analyze first 5 results
        #             "",
        #             analysis_prompt
        #         )
                
        #         results['analysis'] = {
        #             'summary': analysis,
        #             'generated_at': datetime.now().isoformat()
        #         }
                
        #     except Exception as e:
        #         if logger:
        #             logger.error(f"Funding analysis failed: {e}")
        #         results['analysis'] = {'error': str(e)}
        
        return jsonify(results)
        
    except Exception as e:
        if logger:
            logger.error(f"Research funding failed: {e}")
        return jsonify({'error': f'Research funding failed: {str(e)}'}), 500


def search_nsf_funding(query: str, max_results: int) -> list:
    """Search NSF funding opportunities"""
    # Placeholder implementation
    return [
        {
            'title': f'NSF Funding Opportunity: {query}',
            'agency': 'NSF',
            'amount': '$500,000',
            'deadline': '2025-12-31',
            'description': f'NSF funding opportunity related to {query}',
            'url': 'https://www.nsf.gov/funding/',
            'source': 'nsf'
        }
    ]


def search_nih_funding(query: str, max_results: int) -> list:
    """Search NIH funding opportunities"""
    # Placeholder implementation
    return [
        {
            'title': f'NIH Grant: {query}',
            'agency': 'NIH',
            'amount': '$750,000',
            'deadline': '2025-11-30',
            'description': f'NIH grant opportunity related to {query}',
            'url': 'https://grants.nih.gov/',
            'source': 'nih'
        }
    ]


def search_cordis_funding(query: str, max_results: int) -> list:
    """Search CORDIS funding opportunities"""
    # Placeholder implementation
    return [
        {
            'title': f'EU Funding: {query}',
            'agency': 'CORDIS',
            'amount': '€1,000,000',
            'deadline': '2025-10-31',
            'description': f'EU funding opportunity related to {query}',
            'url': 'https://cordis.europa.eu/',
            'source': 'cordis'
        }
    ]


def search_swecris_funding(query: str, max_results: int) -> list:
    """Search SweCRIS funding opportunities"""
    # Placeholder implementation
    return [
        {
            'title': f'Swedish Funding: {query}',
            'agency': 'SweCRIS',
            'amount': 'SEK 2,000,000',
            'deadline': '2025-09-30',
            'description': f'Swedish funding opportunity related to {query}',
            'url': 'https://swecris.se/',
            'source': 'swecris'
        }
    ] 