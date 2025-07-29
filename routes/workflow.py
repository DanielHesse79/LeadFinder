"""
Lean Workflow Routes

This module provides Flask routes for the lean 3-phase data workflow:
1. Data In - Collect and ingest data from various sources
2. Data Process - Analyze and transform the data with AI
3. Data Out - Generate reports and insights
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from typing import Dict, Any, List
import json

try:
    from services.workflow_service import get_workflow
except ImportError:
    get_workflow = None

try:
    from models.database import db
except ImportError:
    db = None

try:
    from utils.logger import get_logger
    logger = get_logger('workflow_routes')
except ImportError:
    logger = None

workflow_bp = Blueprint('workflow', __name__)

@workflow_bp.route('/workflow')
def workflow_dashboard():
    """Main workflow dashboard"""
    if not get_workflow:
        flash('Workflow system not available', 'error')
        return redirect(url_for('leads.show_leads'))
    
    try:
        workflow = get_workflow()
        progress = workflow.get_progress()
        
        # Get recent data for display
        recent_data = []
        if db:
            recent_leads = db.get_all_leads(limit=10)
            recent_data = recent_leads
        
        return render_template('workflow_dashboard.html', 
                             progress=progress,
                             recent_data=recent_data)
        
    except Exception as e:
        if logger:
            logger.error(f"Workflow dashboard error: {e}")
        flash(f'Error loading workflow dashboard: {str(e)}', 'error')
        return redirect(url_for('leads.show_leads'))

@workflow_bp.route('/workflow/data-in')
def data_in_dashboard():
    """Data collection dashboard"""
    if not get_workflow:
        flash('Workflow system not available', 'error')
        return redirect(url_for('workflow.workflow_dashboard'))
    
    try:
        workflow = get_workflow()
        progress = workflow.get_progress()
        
        return render_template('data_in_dashboard.html', progress=progress)
        
    except Exception as e:
        if logger:
            logger.error(f"Data in dashboard error: {e}")
        flash(f'Error loading data in dashboard: {str(e)}', 'error')
        return redirect(url_for('workflow.workflow_dashboard'))

@workflow_bp.route('/workflow/data-process')
def data_process_dashboard():
    """Data processing dashboard"""
    if not get_workflow:
        flash('Workflow system not available', 'error')
        return redirect(url_for('workflow.workflow_dashboard'))
    
    try:
        workflow = get_workflow()
        progress = workflow.get_progress()
        
        # Get available data for processing
        available_data = []
        if db:
            all_leads = db.get_all_leads()
            available_data = all_leads
        
        return render_template('data_process_dashboard.html', 
                             progress=progress,
                             available_data=available_data)
        
    except Exception as e:
        if logger:
            logger.error(f"Data process dashboard error: {e}")
        flash(f'Error loading data process dashboard: {str(e)}', 'error')
        return redirect(url_for('workflow.workflow_dashboard'))

@workflow_bp.route('/workflow/data-out')
def data_out_dashboard():
    """Data output dashboard"""
    if not get_workflow:
        flash('Workflow system not available', 'error')
        return redirect(url_for('workflow.workflow_dashboard'))
    
    try:
        workflow = get_workflow()
        progress = workflow.get_progress()
        
        return render_template('data_out_dashboard.html', progress=progress)
        
    except Exception as e:
        if logger:
            logger.error(f"Data out dashboard error: {e}")
        flash(f'Error loading data out dashboard: {str(e)}', 'error')
        return redirect(url_for('workflow.workflow_dashboard'))

# Data In Routes
@workflow_bp.route('/workflow/data-in/quick-search', methods=['POST'])
def quick_search():
    """Quick web search"""
    if not get_workflow:
        return jsonify({'success': False, 'error': 'Workflow system not available'}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        engines = data.get('engines', ['google', 'bing', 'duckduckgo'])
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400
        
        workflow = get_workflow()
        result = workflow.collect_data('web_search', query, engines=engines)
        
        return jsonify(result)
        
    except Exception as e:
        if logger:
            logger.error(f"Quick search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_bp.route('/workflow/data-in/research-search', methods=['POST'])
def research_search():
    """Research API search"""
    if not get_workflow:
        return jsonify({'success': False, 'error': 'Workflow system not available'}), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        research_type = data.get('research_type', 'pubmed')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400
        
        workflow = get_workflow()
        result = workflow.collect_data('research_apis', query, research_type=research_type)
        
        return jsonify(result)
        
    except Exception as e:
        if logger:
            logger.error(f"Research search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_bp.route('/workflow/data-in/upload-documents', methods=['POST'])
def upload_documents():
    """Upload and process documents"""
    if not get_workflow:
        return jsonify({'success': False, 'error': 'Workflow system not available'}), 500
    
    try:
        # Handle file uploads
        files = request.files.getlist('files')
        file_data = []
        
        for file in files:
            if file.filename:
                content = file.read().decode('utf-8', errors='ignore')
                file_data.append({
                    'name': file.filename,
                    'type': file.filename.split('.')[-1].lower(),
                    'content': content
                })
        
        if not file_data:
            return jsonify({'success': False, 'error': 'No files uploaded'}), 400
        
        workflow = get_workflow()
        result = workflow.collect_data('document_upload', '', files=file_data)
        
        return jsonify(result)
        
    except Exception as e:
        if logger:
            logger.error(f"Document upload error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_bp.route('/workflow/data-in/ai-research', methods=['POST'])
def ai_research():
    """AI-powered research"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Research query is required'
            }), 400
        
        # TODO: Implement AI research functionality
        # This would integrate with AutoGPT or other AI research tools
        
        # Mock response for now
        results = [{
            'title': f'AI Research: {query}',
            'description': f'AI-generated research results for: {query}',
            'source': 'ai_research',
            'url': '#',
            'content': f'AI research content for {query}',
            'metadata': {
                'ai_generated': True,
                'query': query,
                'timestamp': '2024-01-01'
            }
        }]
        
        return jsonify({
            'success': True,
            'results': results,
            'source': 'AI Research'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"AI research error: {e}")
        return jsonify({
            'success': False,
            'error': f'AI research failed: {str(e)}'
        }), 500

@workflow_bp.route('/workflow/data-in/web-scraping', methods=['POST'])
def web_scraping():
    """Web scraping for data collection"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        content_type = data.get('content_type', 'scientific_paper')
        research_context = data.get('research_context', '').strip()
        use_ai_analysis = data.get('use_ai_analysis', True)
        
        if not urls:
            return jsonify({
                'success': False,
                'error': 'URLs are required'
            }), 400
        
        # Simple web scraping using requests and BeautifulSoup
        import requests
        from bs4 import BeautifulSoup
        import time
        
        results = []
        successful_scrapes = 0
        saved_to_db = 0
        
        for url in urls:
            try:
                start_time = time.time()
                
                # Make HTTP request
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract content
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ''
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                content = soup.get_text()
                
                # Clean up content
                lines = (line.strip() for line in content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                content = ' '.join(chunk for chunk in chunks if chunk)
                
                # Limit content length
                if len(content) > 5000:
                    content = content[:5000] + "..."
                
                # Extract metadata
                metadata = {
                    'content_length': len(content),
                    'title': title_text,
                    'links': [a.get('href') for a in soup.find_all('a', href=True)],
                    'extracted_patterns': {
                        'authors': [],
                        'publication_date': []
                    }
                }
                
                # Extract scientific patterns if it's a scientific paper
                if content_type == 'scientific_paper':
                    import re
                    # Look for author patterns
                    author_patterns = re.findall(r'(?i)(author|authors?|by)\s*:?\s*([^\.]+)', content)
                    metadata['extracted_patterns']['authors'] = author_patterns
                    
                    # Look for date patterns
                    date_patterns = re.findall(r'(?i)(published|date|year)\s*:?\s*([^\s]+)', content)
                    metadata['extracted_patterns']['publication_date'] = date_patterns
                
                processing_time = time.time() - start_time
                
                result = {
                    'url': url,
                    'title': title_text,
                    'content': content,
                    'metadata': metadata,
                    'processing_time': processing_time,
                    'source_type': content_type,
                    'success': True
                }
                
                results.append(result)
                successful_scrapes += 1
                
                # Save to database if available
                try:
                    from models.leads import Lead
                    from database import db
                    
                    lead = Lead(
                        title=title_text[:100] or f"Scraped content from {url}",
                        description=content[:500],
                        source_url=url,
                        source_type='web_scraping',
                        content_type=content_type,
                        metadata=metadata,
                        created_at=time.time()
                    )
                    
                    db.session.add(lead)
                    db.session.commit()
                    saved_to_db += 1
                    
                except Exception as db_error:
                    if logger:
                        logger.warning(f"Failed to save scraped content to database: {db_error}")
                
            except Exception as e:
                if logger:
                    logger.error(f"Failed to scrape {url}: {e}")
                
                results.append({
                    'url': url,
                    'title': '',
                    'content': '',
                    'metadata': {},
                    'processing_time': 0,
                    'source_type': content_type,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'source': 'Web Scraping',
            'total_urls': len(urls),
            'successful_scrapes': successful_scrapes,
            'saved_to_db': saved_to_db
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Web scraping error: {e}")
        return jsonify({
            'success': False,
            'error': f'Web scraping failed: {str(e)}'
        }), 500

# Data Process Routes
@workflow_bp.route('/workflow/data-process/analyze', methods=['POST'])
def analyze_data():
    """Analyze collected data"""
    if not get_workflow:
        return jsonify({'success': False, 'error': 'Workflow system not available'}), 500
    
    try:
        data = request.get_json()
        data_ids = data.get('data_ids', [])
        analysis_type = data.get('analysis_type', 'lead_analysis')
        
        if not data_ids:
            return jsonify({'success': False, 'error': 'No data selected for analysis'}), 400
        
        workflow = get_workflow()
        result = workflow.process_data(data_ids, analysis_type)
        
        return jsonify(result)
        
    except Exception as e:
        if logger:
            logger.error(f"Data analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Data Out Routes
@workflow_bp.route('/workflow/data-out/generate-report', methods=['POST'])
def generate_report():
    """Generate reports from processed data"""
    if not get_workflow:
        return jsonify({'success': False, 'error': 'Workflow system not available'}), 500
    
    try:
        data = request.get_json()
        processed_data = data.get('processed_data', {})
        report_type = data.get('report_type', 'lead_report')
        
        if not processed_data:
            return jsonify({'success': False, 'error': 'No processed data provided'}), 400
        
        workflow = get_workflow()
        result = workflow.generate_output(processed_data, report_type)
        
        return jsonify(result)
        
    except Exception as e:
        if logger:
            logger.error(f"Report generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Progress and Status Routes
@workflow_bp.route('/workflow/progress')
def get_progress():
    """Get current workflow progress"""
    if not get_workflow:
        return jsonify({'success': False, 'error': 'Workflow system not available'}), 500
    
    try:
        workflow = get_workflow()
        progress = workflow.get_progress()
        
        return jsonify({
            'success': True,
            'progress': progress
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Progress error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_bp.route('/workflow/reset', methods=['POST'])
def reset_workflow():
    """Reset workflow progress"""
    if not get_workflow:
        return jsonify({'success': False, 'error': 'Workflow system not available'}), 500
    
    try:
        workflow = get_workflow()
        workflow.reset_progress()
        
        return jsonify({
            'success': True,
            'message': 'Workflow progress reset successfully'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Reset workflow error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# API Routes for AJAX calls
@workflow_bp.route('/workflow/api/available-data')
def get_available_data():
    """Get available data for processing"""
    if not db:
        return jsonify({'success': False, 'error': 'Database not available'}), 500
    
    try:
        all_leads = db.get_all_leads()
        
        # If no data available, create sample data for testing
        if not all_leads:
            sample_data = [
                {
                    'title': 'Epigenetics Research in Diabetes',
                    'description': 'Study on epigenetic modifications in pre-diabetes patients using advanced sequencing techniques.',
                    'source': 'research_paper',
                    'created_at': '2025-01-15'
                },
                {
                    'title': 'AI in Healthcare Market Analysis',
                    'description': 'Comprehensive analysis of artificial intelligence applications in healthcare sector.',
                    'source': 'market_research',
                    'created_at': '2025-01-14'
                },
                {
                    'title': 'Biotech Startup Funding Trends',
                    'description': 'Analysis of funding patterns and investment opportunities in biotechnology startups.',
                    'source': 'industry_report',
                    'created_at': '2025-01-13'
                },
                {
                    'title': 'Precision Medicine Implementation',
                    'description': 'Case study on implementing precision medicine approaches in clinical settings.',
                    'source': 'clinical_study',
                    'created_at': '2025-01-12'
                },
                {
                    'title': 'Digital Health Innovation Hub',
                    'description': 'Overview of digital health innovation centers and their impact on healthcare delivery.',
                    'source': 'industry_analysis',
                    'created_at': '2025-01-11'
                }
            ]
            
            # Add sample data to database
            for item in sample_data:
                db.save_lead(item)
            
            all_leads = db.get_all_leads()
        
        # Format for frontend
        formatted_data = []
        for lead in all_leads:
            formatted_data.append({
                'id': lead.get('id'),
                'title': lead.get('title', ''),
                'description': lead.get('description', ''),
                'source': lead.get('source', ''),
                'created_at': lead.get('created_at', '')
            })
        
        return jsonify({
            'success': True,
            'data': formatted_data,
            'count': len(formatted_data)
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Get available data error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@workflow_bp.route('/workflow/api/statistics')
def get_workflow_statistics():
    """Get workflow statistics"""
    if not db:
        return jsonify({'success': False, 'error': 'Database not available'}), 500
    
    try:
        all_leads = db.get_all_leads()
        
        # Calculate statistics
        total_leads = len(all_leads)
        sources = {}
        for lead in all_leads:
            source = lead.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        statistics = {
            'total_leads': total_leads,
            'sources': sources,
            'recent_leads': len([l for l in all_leads if l.get('created_at', '') > '2025-07-28'])  # Last 24 hours
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Get statistics error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500