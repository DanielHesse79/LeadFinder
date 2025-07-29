from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from typing import List, Dict, Any
from datetime import datetime
import os
from pathlib import Path

# Import services with error handling
try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from services.pubmed_service import pubmed_service
except ImportError:
    pubmed_service = None

try:
    from services.orcid_service import orcid_service
except ImportError:
    orcid_service = None

try:
    from services.scihub_service import scihub_service
except ImportError:
    scihub_service = None

try:
    from services.scihub_enhanced_service import SciHubEnhancedService
    scihub_enhanced_service = SciHubEnhancedService()
except ImportError:
    scihub_enhanced_service = None

try:
    from services.semantic_scholar_service import semantic_scholar_service
except ImportError:
    semantic_scholar_service = None

try:
    from models.database import db
except ImportError:
    db = None



try:
    from utils.logger import get_logger
    logger = get_logger('ollama')
except ImportError:
    logger = None

ollama_bp = Blueprint('ollama', __name__)

@ollama_bp.route('/')
def ollama_home():
    """Ollama home page"""
    return render_template('ollama.html', 
                         ollama_status=ollama_service.check_status() if ollama_service else {"ok": False, "msg": "Service not available"})

@ollama_bp.route('/ollama_search', methods=['POST'])
def ollama_search():
    """Search using Ollama AI"""
    if not ollama_service:
        return jsonify({'error': 'Ollama service not available'}), 503
    
    try:
        query = request.form.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get search parameters
        max_results = int(request.form.get('max_results', 10))
        research_question = request.form.get('research_question', 'general relevance')
        
        if logger:
            logger.info(f"Ollama search: '{query}' with {max_results} results")
        
        # Perform search using Ollama
        search_results = ollama_service.search_with_ai(
            query, 
            max_results=max_results,
            research_question=research_question
        )
        
        return jsonify({
            'success': True,
            'query': query,
            'results': search_results,
            'total_results': len(search_results),
            'source': 'ollama'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Ollama search failed: {e}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@ollama_bp.route('/advanced', methods=['POST'])
def advanced_search():
    """Advanced search with filters"""
    query = request.form.get('query', '').strip()
    author = request.form.get('author', '').strip()
    journal = request.form.get('journal', '').strip()
    year_from = request.form.get('year_from', '').strip()
    year_to = request.form.get('year_to', '').strip()
    
    if logger:
        logger.info(f"Advanced search: {query}, author: {author}, journal: {journal}, years: {year_from}-{year_to}")
    
    publications = []
    
    # Advanced PubMed search
    if pubmed_service:
        try:
            # Build advanced query
            advanced_query = query
            if author:
                advanced_query += f" AND {author}[Author]"
            if journal:
                advanced_query += f" AND {journal}[Journal]"
            if year_from or year_to:
                year_filter = ""
                if year_from and year_to:
                    year_filter = f" AND ({year_from}[Date - Publication] : {year_to}[Date - Publication])"
                elif year_from:
                    year_filter = f" AND {year_from}[Date - Publication] : 3000[Date - Publication]"
                elif year_to:
                    year_filter = f" AND 1900[Date - Publication] : {year_to}[Date - Publication]"
                advanced_query += year_filter
            
            pubmed_results = pubmed_service.search_articles(advanced_query, max_results=30)
            publications.extend(pubmed_results)
            if logger:
                logger.info(f"Advanced search found {len(pubmed_results)} articles")
        except Exception as e:
            if logger:
                logger.error(f"Advanced PubMed search failed: {e}")
    
    return render_template('ollama.html',
                         query=query,
                         publications=publications,
                         researchers=[],
                         search_type='publications',
                         ollama_status=ollama_service.check_status() if ollama_service else {"ok": False, "msg": "Service not available"})

@ollama_bp.route('/check', methods=['POST'])
def check_ollama():
    """Check Ollama status"""
    if ollama_service:
        status = ollama_service.check_status()
        if logger:
            logger.info(f"Ollama status check: {status}")
        flash(f"Ollama status: {status['msg']}", 'info' if status['ok'] else 'warning')
    else:
        flash('Ollama service not available', 'error')
    
    return redirect(url_for('ollama.ollama_home'))

@ollama_bp.route('/models')
def models_ui():
    """Ollama models management UI"""
    if not ollama_service:
        flash('Ollama service not available', 'error')
        return redirect(url_for('leads.show_leads'))
    
    available_models = ollama_service.get_available_models()
    selected_model = ollama_service.get_selected_model()
    
    return render_template('ollama_models.html',
                         available_models=available_models,
                         selected_model=selected_model)

@ollama_bp.route('/set_model', methods=['POST'])
def set_model():
    """Set preferred Ollama model"""
    if not ollama_service:
        flash('Ollama service not available', 'error')
        return redirect(url_for('ollama.models_ui'))
    
    model_name = request.form.get('model_name', '').strip()
    if not model_name:
        flash('Model name is required', 'error')
        return redirect(url_for('ollama.models_ui'))
    
    success = ollama_service.set_preferred_model(model_name)
    if success:
        flash(f'Model set to: {model_name}', 'success')
    else:
        flash(f'Failed to set model: {model_name}', 'error')
    
    return redirect(url_for('ollama.models_ui'))

@ollama_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    """Get Sci-Hub URL for DOI"""
    if not scihub_service:
        return jsonify({'error': 'Sci-Hub service not available'}), 500
    
    doi = request.form.get('doi', '').strip()
    if not doi:
        return jsonify({'error': 'DOI is required'}), 400
    
    try:
        result = scihub_service.download_pdf(doi)
        if result['success']:
            return jsonify({
                'success': True,
                'redirect': result.get('redirect', False),
                'url': result.get('url', ''),
                'message': result.get('message', 'Sci-Hub URL generated successfully'),
                'mirror': result.get('mirror', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate Sci-Hub URL'),
                'invalid_doi': result.get('invalid_doi', False)
            })
    except Exception as e:
        if logger:
            logger.error(f"Sci-Hub URL generation failed for DOI {doi}: {e}")
        return jsonify({'error': str(e)}), 500

@ollama_bp.route('/download_multiple', methods=['POST'])
def download_multiple_pdfs():
    """Get Sci-Hub URLs for multiple DOIs"""
    if not scihub_service:
        return jsonify({'error': 'Sci-Hub service not available'}), 500
    
    dois = request.json.get('dois', [])
    if not dois:
        return jsonify({'error': 'DOIs are required'}), 400
    
    results = []
    for doi in dois:
        try:
            result = scihub_service.download_pdf(doi)
            results.append({
                'doi': doi,
                'success': result['success'],
                'redirect': result.get('redirect', False),
                'url': result.get('url', ''),
                'error': result.get('error', ''),
                'invalid_doi': result.get('invalid_doi', False)
            })
        except Exception as e:
            results.append({
                'doi': doi,
                'success': False,
                'error': str(e)
            })
    
    success_count = sum(1 for r in results if r['success'])
    return jsonify({
        'results': results,
        'total': len(dois),
        'successful': success_count
    })

@ollama_bp.route('/download_pdf_enhanced', methods=['POST'])
def download_pdf_enhanced():
    """Download PDF directly using enhanced Sci-Hub service"""
    if not scihub_enhanced_service:
        return jsonify({'error': 'Enhanced Sci-Hub service not available'}), 500
    
    identifier = request.form.get('identifier', '').strip()
    if not identifier:
        return jsonify({'error': 'Identifier (DOI, PMID, or URL) is required'}), 400
    
    try:
        result = scihub_enhanced_service.download_pdf(identifier)
        return jsonify(result)
    except Exception as e:
        if logger:
            logger.error(f"Enhanced PDF download failed for {identifier}: {e}")
        return jsonify({'error': str(e)}), 500

@ollama_bp.route('/batch_download', methods=['POST'])
def batch_download():
    """Download multiple PDFs using enhanced service"""
    if not scihub_enhanced_service:
        return jsonify({'error': 'Enhanced Sci-Hub service not available'}), 500
    
    identifiers = request.json.get('identifiers', [])
    if not identifiers:
        return jsonify({'error': 'Identifiers are required'}), 400
    
    try:
        result = scihub_enhanced_service.batch_download(identifiers)
        return jsonify(result)
    except Exception as e:
        if logger:
            logger.error(f"Batch download failed: {e}")
        return jsonify({'error': str(e)}), 500

@ollama_bp.route('/mirror_status')
def get_mirror_status():
    """Get status of Sci-Hub mirrors"""
    if not scihub_enhanced_service:
        return jsonify({'error': 'Enhanced Sci-Hub service not available'}), 500
    
    try:
        status = scihub_enhanced_service.get_mirror_status()
        return jsonify(status)
    except Exception as e:
        if logger:
            logger.error(f"Failed to get mirror status: {e}")
        return jsonify({'error': str(e)}), 500

@ollama_bp.route('/downloaded_files')
def get_downloaded_files():
    """Get list of downloaded PDF files"""
    # Try enhanced service first, fallback to original service
    service = scihub_enhanced_service or scihub_service
    if not service:
        return jsonify({'error': 'Sci-Hub service not available'}), 500
    
    try:
        files = service.get_downloaded_files()
        return jsonify({
            'files': files,
            'count': len(files),
            'download_folder': str(service.download_folder)
        })
    except Exception as e:
        if logger:
            logger.error(f"Failed to get downloaded files: {e}")
        return jsonify({'error': str(e)}), 500

@ollama_bp.route('/view_downloads')
def view_downloads():
    """View downloaded PDFs page"""
    try:
        # Get list of downloaded files (try enhanced service first)
        service = scihub_enhanced_service or scihub_service
        if service:
            files = service.get_downloaded_files()
        else:
            files = []
        
        # Get list of export files (PDFs and Markdown)
        export_files = []
        try:
            from config import EXPORT_FOLDER
            export_path = Path(EXPORT_FOLDER)
            if export_path.exists():
                # Get PDF files
                for file_path in export_path.glob("*.pdf"):
                    export_files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'type': 'pdf'
                    })
                
                # Get Markdown files
                for file_path in export_path.glob("*.md"):
                    export_files.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'type': 'markdown'
                    })
                
                # Sort by modification time (newest first)
                export_files.sort(key=lambda x: x['modified'], reverse=True)
                
        except Exception as e:
            if logger:
                logger.error(f"Error reading export files: {e}")
        
        return render_template('downloads.html', 
                             downloaded_files=files, 
                             export_files=export_files)
    except Exception as e:
        if logger:
            logger.error(f"Error in view_downloads: {e}")
        flash('Error loading downloads', 'error')
        return redirect(url_for('ollama.ollama_home'))

@ollama_bp.route('/download/<path:file_path>')
def download_file(file_path):
    """Download a file from the exports folder"""
    try:
        from config import EXPORT_FOLDER
        from pathlib import Path
        import os
        
        # Ensure the file path is within the exports folder
        export_path = Path(EXPORT_FOLDER).resolve()
        file_path_obj = Path(file_path).resolve()
        
        # Security check: ensure file is within exports folder
        if not str(file_path_obj).startswith(str(export_path)):
            return jsonify({'error': 'Access denied'}), 403
        
        if not file_path_obj.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path_obj,
            as_attachment=True,
            download_name=file_path_obj.name
        )
        
    except Exception as e:
        if logger:
            logger.error(f"Error downloading file {file_path}: {e}")
        return jsonify({'error': str(e)}), 500

@ollama_bp.route('/send_pdf_to_workshop', methods=['POST'])
def send_pdf_to_workshop():
    """Send a downloaded PDF to Lead Workshop for processing"""
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Create a lead from the PDF file
        lead_data = {
            'title': os.path.basename(file_path),
            'url': f'file://{file_path}',
            'source': 'downloaded_pdf',
            'description': f'PDF file: {os.path.basename(file_path)}',
            'content': f'Local PDF file available for processing: {file_path}'
        }
        
        # Save to database
        if db:
            # Extract the required fields for save_lead
            title = lead_data.get('title', 'Unknown PDF')
            description = lead_data.get('description', '')
            link = lead_data.get('url', '')
            ai_summary = lead_data.get('content', '')
            source = lead_data.get('source', 'downloaded_pdf')
            
            lead_id = db.save_lead(title, description, link, ai_summary, source)
            if lead_id:
                return jsonify({
                    'success': True, 
                    'message': 'PDF sent to Lead Workshop',
                    'lead_id': lead_id,
                    'redirect_url': url_for('lead_workshop.lead_workshop_home', lead_ids=str(lead_id))
                })
            else:
                return jsonify({'success': False, 'error': 'Failed to save lead'}), 500
        else:
            return jsonify({'success': False, 'error': 'Database not available'}), 500
            
    except Exception as e:
        if logger:
            logger.error(f"Error sending PDF to workshop: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ollama_bp.route('/ollama_status')
def ollama_status():
    """Get Ollama status as JSON"""
    if ollama_service:
        status = ollama_service.check_status()
        return jsonify(status)
    else:
        return jsonify({'ok': False, 'msg': 'Service not available'})

@ollama_bp.route('/ollama_models')
def ollama_models():
    """Get available Ollama models as JSON"""
    if ollama_service:
        models = ollama_service.get_available_models()
        selected = ollama_service.get_selected_model()
        return jsonify({
            'models': models,
            'selected': selected
        })
    else:
        return jsonify({'models': [], 'selected': None})

@ollama_bp.route('/send_to_workshop', methods=['POST'])
def send_to_workshop():
    """Send selected publications to lead workshop"""
    try:
        # Get selected publications data
        publications_data = request.json.get('publications', [])
        
        if not publications_data:
            return jsonify({'error': 'No publications selected'}), 400
        
        # Import database functions
        from models.database import save_lead
        
        saved_count = 0
        saved_lead_ids = []
        for pub in publications_data:
            try:
                # Create lead title from publication title
                title = pub.get('title', 'Unknown Publication')
                
                # Create description from abstract and authors
                authors = pub.get('authors', [])
                authors_str = ', '.join(authors) if authors else 'Unknown Authors'
                abstract = pub.get('abstract', 'No abstract available')
                description = f"Authors: {authors_str}\n\nAbstract: {abstract}"
                
                # Create link from URL or DOI
                link = pub.get('url', '')
                if not link and pub.get('doi'):
                    link = f"https://doi.org/{pub['doi']}"
                
                # Create AI summary
                ai_summary = f"Academic publication from {pub.get('source', 'Unknown Source')}"
                if pub.get('journal'):
                    ai_summary += f" in {pub['journal']}"
                if pub.get('year'):
                    ai_summary += f" ({pub['year']})"
                
                # Save to database
                lead_id = save_lead(
                    title=title,
                    description=description,
                    link=link,
                    ai_summary=ai_summary,
                    source=f"academic_{pub.get('source', 'unknown').lower()}"
                )
                
                if lead_id:
                    saved_count += 1
                    saved_lead_ids.append(lead_id)
                    
            except Exception as e:
                if logger:
                    logger.error(f"Failed to save publication {pub.get('title', 'Unknown')}: {e}")
                continue
        
        if saved_count > 0:
            return jsonify({
                'success': True,
                'message': f'Successfully sent {saved_count} publication(s) to lead workshop',
                'saved_count': saved_count,
                'total_count': len(publications_data),
                'lead_ids': saved_lead_ids,
                'redirect_url': f'/lead-workshop?lead_ids={",".join(map(str, saved_lead_ids))}'
            })
        else:
            return jsonify({'error': 'Failed to save any publications'}), 500
            
    except Exception as e:
        if logger:
            logger.error(f"Error sending publications to workshop: {e}")
        return jsonify({'error': str(e)}), 500

 