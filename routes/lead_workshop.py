"""
Lead Workshop routes

This module provides Flask routes for AI-powered analysis of documents, files, and data
from other sections of the application with project management and relevancy scoring.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file
from typing import List, Dict, Any
import os
import tempfile
from werkzeug.utils import secure_filename

# Import services with error handling
try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from models.database import db
except ImportError:
    db = None

try:
    from services.pdf_service import pdf_service
except ImportError:
    pdf_service = None

try:
    from services.markdown_service import markdown_service
except ImportError:
    markdown_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('lead_workshop')
except ImportError:
    logger = None

lead_workshop_bp = Blueprint('lead_workshop', __name__)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'html', 'json', 'csv'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_ai_analysis(ai_response: str, lead_title: str) -> dict:
    """Parse AI analysis response to extract structured data"""
    try:
        # Initialize default values
        parsed_data = {
            'score': 3,
            'people': 'To be extracted',
            'contact': 'To be extracted',
            'analysis_summary': 'Analysis completed'
        }
        
        # Extract score (look for SCORE: pattern)
        import re
        score_match = re.search(r'SCORE:\s*(\d+)', ai_response, re.IGNORECASE)
        if score_match:
            score = int(score_match.group(1))
            if 1 <= score <= 5:
                parsed_data['score'] = score
        
        # Extract people (look for PEOPLE: pattern)
        people_match = re.search(r'PEOPLE:\s*(.*?)(?=\n[A-Z]+:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        if people_match:
            people = people_match.group(1).strip()
            if people and people.lower() not in ['none found', 'not available', 'unknown']:
                parsed_data['people'] = people
        
        # Extract contact (look for CONTACT: pattern)
        contact_match = re.search(r'CONTACT:\s*(.*?)(?=\n[A-Z]+:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        if contact_match:
            contact = contact_match.group(1).strip()
            if contact and contact.lower() not in ['not available', 'unknown']:
                parsed_data['contact'] = contact
        
        # Extract analysis summary
        analysis_match = re.search(r'ANALYSIS:\s*(.*?)(?=\n[A-Z]+:|$)', ai_response, re.IGNORECASE | re.DOTALL)
        if analysis_match:
            analysis = analysis_match.group(1).strip()
            if analysis:
                parsed_data['analysis_summary'] = analysis[:100] + "..." if len(analysis) > 100 else analysis
        
        return parsed_data
        
    except Exception as e:
        if logger:
            logger.error(f"Error parsing AI analysis for {lead_title}: {e}")
        return {
            'score': 3,
            'people': 'To be extracted',
            'contact': 'To be extracted',
            'analysis_summary': 'Analysis completed'
        }

@lead_workshop_bp.route('/lead-workshop')
def lead_workshop_home():
    """Lead Workshop home page with project management"""
    # Get lead IDs from query parameters if any
    lead_ids_param = request.args.get('lead_ids', '')
    selected_leads = []
    
    if logger:
        logger.info(f"Lead Workshop: lead_ids_param = '{lead_ids_param}'")
    
    if lead_ids_param and db:
        try:
            # Handle both comma-separated string and list formats
            if isinstance(lead_ids_param, str):
                # Split comma-separated string
                lead_ids = [lid.strip() for lid in lead_ids_param.split(',') if lid.strip()]
            else:
                # Already a list
                lead_ids = lead_ids_param
            
            if logger:
                logger.info(f"Lead Workshop: Parsed lead_ids = {lead_ids}")
            
            # Get leads by ID
            for lead_id in lead_ids:
                try:
                    lead = db.get_lead_by_id(int(lead_id))
                    if lead:
                        selected_leads.append(lead)
                        if logger:
                            logger.info(f"Lead Workshop: Found lead {lead_id}: {lead['title'][:50]}...")
                    else:
                        if logger:
                            logger.warning(f"Lead with ID {lead_id} not found")
                except ValueError:
                    if logger:
                        logger.warning(f"Invalid lead ID: {lead_id}")
                except Exception as e:
                    if logger:
                        logger.error(f"Error getting lead {lead_id}: {e}")
        except Exception as e:
            if logger:
                logger.error(f"Error processing lead IDs: {e}")
    
    if logger:
        logger.info(f"Lead Workshop: Found {len(selected_leads)} selected leads")
    
    # If no specific leads selected, show recent academic publications
    if not selected_leads and db:
        try:
            # Get recent academic publications (last 20)
            academic_leads = db.get_leads_by_source('academic_pubmed')
            if academic_leads:
                selected_leads = academic_leads[:20]  # Limit to 20 most recent
                if logger:
                    logger.info(f"Showing {len(selected_leads)} recent academic publications in workshop")
        except Exception as e:
            if logger:
                logger.error(f"Error getting academic publications: {e}")
    
    if not selected_leads and logger:
        logger.debug("No leads available - showing empty workshop")
    
    # Get all projects
    projects = db.get_projects() if db else []
    
    # Check AutoGPT availability
    try:
        from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
        autogpt_integration = LeadfinderAutoGPTIntegration("mistral:latest")
        autogpt_available = True
    except Exception as e:
        autogpt_available = False
    
    return render_template('lead_workshop.html', 
                         selected_leads=selected_leads,
                         projects=projects,
                         autogpt_available=autogpt_available)

@lead_workshop_bp.route('/lead-workshop/create-project', methods=['POST'])
def create_project():
    """Create a new workshop project"""
    if not db:
        return jsonify({'success': False, 'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': 'Project name is required'}), 400
        
        project_id = db.create_project(name, description)
        
        if project_id:
            return jsonify({
                'success': True,
                'project_id': project_id,
                'message': f'Project "{name}" created successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create project'}), 500
            
    except Exception as e:
        if logger:
            logger.error(f"Error creating project: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@lead_workshop_bp.route('/lead-workshop/analyze-leads', methods=['POST'])
def analyze_leads():
    """Analyze selected leads with AI and save to project"""
    if not db or not ollama_service:
        return jsonify({'success': False, 'error': 'Database or AI service not available'}), 500
    
    try:
        data = request.get_json()
        lead_ids_raw = data.get('lead_ids', [])
        project_id = data.get('project_id')
        project_context = data.get('project_context', '').strip()
        delete_after_analysis = data.get('delete_after_analysis', False)
        
        # Handle different formats of lead_ids (array, string, or comma-separated string)
        lead_ids = []
        if isinstance(lead_ids_raw, str):
            # If it's a string, split by comma and clean up
            lead_ids = [id.strip() for id in lead_ids_raw.split(',') if id.strip()]
        elif isinstance(lead_ids_raw, list):
            # If it's already a list, use as is
            lead_ids = lead_ids_raw
        else:
            return jsonify({'success': False, 'error': 'Invalid lead_ids format'}), 400
        
        if not lead_ids:
            return jsonify({'success': False, 'error': 'No leads selected'}), 400
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Project is required'}), 400
        
        # Get project details
        project = db.get_project(int(project_id))
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Get leads with proper error handling for each ID
        leads_data = []
        for lead_id_str in lead_ids:
            try:
                # Clean the lead_id string and convert to int
                lead_id_clean = lead_id_str.strip().replace('\n', '').replace('\r', '')
                lead_id_int = int(lead_id_clean)
                lead = db.get_lead_by_id(lead_id_int)
                if lead:
                    leads_data.append(lead)
                else:
                    if logger:
                        logger.warning(f"Lead with ID {lead_id_int} not found in database")
            except (ValueError, TypeError) as e:
                if logger:
                    logger.error(f"Invalid lead ID format: '{lead_id_str}' - {e}")
                continue
        
        if not leads_data:
            return jsonify({'success': False, 'error': 'No valid leads found'}), 400
        
        # Analyze each lead individually for better results
        saved_analyses = []
        analysis_summary = []
        
        for i, lead in enumerate(leads_data, 1):
            if logger:
                logger.info(f"Analyzing lead {i}/{len(leads_data)}: {lead['title'][:50]}...")
            
            # Create individual analysis prompt for each lead
            individual_prompt = f"""
            Project: {project['name']}
            Context: {project_context if project_context else 'General analysis'}
            
            Analyze this specific lead in detail:
            
            LEAD: {lead['title']}
            DESCRIPTION: {lead['description']}
            LINK: {lead['link']}
            SOURCE: {lead['source']}
            
            Provide a comprehensive analysis with the following format:
            
            SCORE: [1-5 relevancy score]
            JUSTIFICATION: [Detailed explanation of why this score]
            PEOPLE: [Names, titles, organizations mentioned or "None found"]
            CONTACT: [Contact details found or "Not available"]
            PRODUCTS: [Product names, technologies mentioned or "None mentioned"]
            COMPANY: [Company information or "Not available"]
            OPPORTUNITIES: [Potential collaboration opportunities or "None identified"]
            CONCERNS: [Red flags or concerns or "None identified"]
            ANALYSIS: [Comprehensive analysis and recommendations]
            
            Be thorough and specific to this lead. If information is not available, say "Not available" or "Unknown".
            Focus on extracting specific details like product names, company information, and contact details.
            """
            
            try:
                # Get AI analysis for this individual lead
                ai_response = ollama_service._call_ollama_with_retry(individual_prompt, max_retries=1)
                
                if not ai_response:
                    ai_response = "AI analysis failed - no response received"
                
                # Parse the AI response to extract structured data
                parsed_data = parse_ai_analysis(ai_response, lead['title'])
                
                # Save individual analysis
                analysis_id = db.save_lead_analysis(
                    project_id=int(project_id),
                    lead_id=lead['id'],
                    relevancy_score=parsed_data.get('score', 3),
                    ai_analysis=ai_response,
                    key_opinion_leaders=parsed_data.get('people', 'To be extracted'),
                    contact_info=parsed_data.get('contact', 'To be extracted'),
                    notes=f"Analyzed for project: {project['name']} - {parsed_data.get('analysis_summary', 'Analysis completed')}"
                )
                
                if analysis_id:
                    saved_analyses.append(analysis_id)
                    analysis_summary.append(f"Lead {i}: {lead['title'][:50]}... - Score: {parsed_data.get('score', 3)}")
                
                if logger:
                    logger.info(f"Completed analysis for lead {i}: {lead['title'][:50]}...")
                    
            except Exception as e:
                if logger:
                    logger.error(f"Failed to analyze lead {i} ({lead['title'][:50]}...): {e}")
                
                # Save fallback analysis for failed leads
                analysis_id = db.save_lead_analysis(
                    project_id=int(project_id),
                    lead_id=lead['id'],
                    relevancy_score=3,
                    ai_analysis=f"Analysis failed: {str(e)}",
                    key_opinion_leaders="Analysis failed",
                    contact_info="Analysis failed",
                    notes=f"Analysis failed for project: {project['name']}"
                )
                
                if analysis_id:
                    saved_analyses.append(analysis_id)
                    analysis_summary.append(f"Lead {i}: {lead['title'][:50]}... - FAILED")
        
        # Create summary response
        summary_response = f"""
        Analysis completed for {len(saved_analyses)} leads:
        
        {'\n'.join(analysis_summary)}
        
        Each lead was analyzed individually for detailed insights.
        """
        
        # Delete leads from workshop if requested
        deleted_leads = []
        if delete_after_analysis:
            for lead_id_str in lead_ids:
                try:
                    # Clean the lead_id string and convert to int
                    lead_id_clean = lead_id_str.strip().replace('\n', '').replace('\r', '')
                    lead_id_int = int(lead_id_clean)
                    success = db.delete_lead(lead_id_int)
                    if success:
                        deleted_leads.append(lead_id_int)
                except (ValueError, TypeError) as e:
                    if logger:
                        logger.error(f"Error converting lead ID '{lead_id_str}' for deletion: {e}")
                except Exception as e:
                    if logger:
                        logger.error(f"Error deleting lead {lead_id_str} after analysis: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Analyzed {len(saved_analyses)} leads for project "{project["name"]}"',
            'analysis_count': len(saved_analyses),
            'deleted_leads': deleted_leads,
            'ai_response': summary_response
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Error analyzing leads: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@lead_workshop_bp.route('/lead-workshop/delete-workshop-leads', methods=['POST'])
def delete_workshop_leads():
    """Delete leads from workshop after they've been shipped to a project"""
    if not db:
        return jsonify({'success': False, 'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        lead_ids_raw = data.get('lead_ids', [])
        
        # Handle different formats of lead_ids (array, string, or comma-separated string)
        lead_ids = []
        if isinstance(lead_ids_raw, str):
            # If it's a string, split by comma and clean up
            lead_ids = [id.strip() for id in lead_ids_raw.split(',') if id.strip()]
        elif isinstance(lead_ids_raw, list):
            # If it's already a list, use as is
            lead_ids = lead_ids_raw
        else:
            return jsonify({'success': False, 'error': 'Invalid lead_ids format'}), 400
        
        if not lead_ids:
            return jsonify({'success': False, 'error': 'No lead IDs provided'}), 400
        
        deleted_count = 0
        for lead_id_str in lead_ids:
            try:
                # Clean the lead_id string and convert to int
                lead_id_clean = lead_id_str.strip().replace('\n', '').replace('\r', '')
                lead_id_int = int(lead_id_clean)
                success = db.delete_lead(lead_id_int)
                if success:
                    deleted_count += 1
                else:
                    if logger:
                        logger.warning(f"Failed to delete lead {lead_id_int}")
            except (ValueError, TypeError) as e:
                if logger:
                    logger.error(f"Error converting lead ID '{lead_id_str}' for deletion: {e}")
                continue
            except Exception as e:
                if logger:
                    logger.error(f"Error deleting lead {lead_id_str}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {deleted_count} out of {len(lead_ids)} leads from workshop',
            'deleted_count': deleted_count,
            'total_requested': len(lead_ids)
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Error deleting workshop leads: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@lead_workshop_bp.route('/lead-workshop/project/<int:project_id>')
def view_project(project_id: int):
    """View a specific project and its analyses"""
    if not db:
        return "Database not available", 500
    
    project = db.get_project(project_id)
    if not project:
        return "Project not found", 404
    
    # Get sorting parameters from query string
    sort_by = request.args.get('sort_by', 'relevancy_score')
    sort_order = request.args.get('sort_order', 'DESC')
    
    analyses = db.get_project_analyses(project_id, sort_by, sort_order)
    
    return render_template('project_view.html', 
                         project=project,
                         analyses=analyses,
                         current_sort_by=sort_by,
                         current_sort_order=sort_order)

@lead_workshop_bp.route('/lead-workshop/delete-analyses', methods=['POST'])
def delete_analyses():
    """Delete multiple lead analyses from a project"""
    if not db:
        return jsonify({'success': False, 'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        analysis_ids = data.get('analysis_ids', [])
        project_id = data.get('project_id')
        
        if not analysis_ids:
            return jsonify({'success': False, 'error': 'No analysis IDs provided'}), 400
        
        if not project_id:
            return jsonify({'success': False, 'error': 'Project ID required'}), 400
        
        deleted_count = 0
        for analysis_id in analysis_ids:
            try:
                # Verify the analysis belongs to the project
                analyses = db.get_project_analyses(int(project_id))
                analysis_exists = any(a['id'] == int(analysis_id) for a in analyses)
                
                if analysis_exists:
                    success = db.delete_analysis(int(analysis_id))
                    if success:
                        deleted_count += 1
                else:
                    if logger:
                        logger.warning(f"Analysis {analysis_id} not found in project {project_id}")
            except Exception as e:
                if logger:
                    logger.error(f"Error deleting analysis {analysis_id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {deleted_count} out of {len(analysis_ids)} analyses',
            'deleted_count': deleted_count,
            'total_requested': len(analysis_ids)
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Error deleting analyses: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@lead_workshop_bp.route('/lead-workshop/update-analysis', methods=['POST'])
def update_analysis():
    """Update analysis with manual data entry"""
    if not db:
        return jsonify({'success': False, 'error': 'Database not available'}), 500
    
    try:
        data = request.get_json()
        analysis_id = data.get('analysis_id')
        relevancy_score = data.get('relevancy_score')
        key_opinion_leaders = data.get('key_opinion_leaders', '')
        contact_info = data.get('contact_info', '')
        notes = data.get('notes', '')
        
        if not analysis_id:
            return jsonify({'success': False, 'error': 'Analysis ID required'}), 400
        
        success = db.update_analysis(
            analysis_id=int(analysis_id),
            relevancy_score=relevancy_score,
            key_opinion_leaders=key_opinion_leaders,
            contact_info=contact_info,
            notes=notes
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Analysis updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update analysis'}), 500
            
    except Exception as e:
        if logger:
            logger.error(f"Error updating analysis: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@lead_workshop_bp.route('/lead-workshop/api/status')
def api_status():
    """Check AI service status"""
    if ollama_service:
        status = ollama_service.check_status()
        return jsonify({
            'status': 'ok' if status.get('ok') else 'error',
            'message': status.get('msg', 'Unknown status')
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'AI service not available'
        })

@lead_workshop_bp.route('/lead-workshop/export-pdf/<int:project_id>')
def export_project_pdf(project_id: int):
    """Export project report as PDF"""
    if not db or not pdf_service:
        return jsonify({'success': False, 'error': 'Database or PDF service not available'}), 500
    
    try:
        # Get project details
        project = db.get_project(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Get project analyses (sorted by relevance by default)
        analyses = db.get_project_analyses(project_id, 'relevancy_score', 'DESC')
        if not analyses:
            return jsonify({'success': False, 'error': 'No analyses found for this project'}), 400
        
        # Generate PDF report
        pdf_path = pdf_service.generate_project_report(project, analyses)
        
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'error': 'Failed to generate PDF'}), 500
        
        # Return the PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=os.path.basename(pdf_path),
            mimetype='application/pdf'
        )
        
    except Exception as e:
        if logger:
            logger.error(f"Error exporting PDF for project {project_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500 

@lead_workshop_bp.route('/lead-workshop/export-markdown/<int:project_id>')
def export_project_markdown(project_id: int):
    """Export project report as collaborative Markdown"""
    if not db or not markdown_service:
        return jsonify({'success': False, 'error': 'Database or Markdown service not available'}), 500
    
    try:
        # Get project details
        project = db.get_project(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Get project analyses (sorted by relevance by default)
        analyses = db.get_project_analyses(project_id, 'relevancy_score', 'DESC')
        if not analyses:
            return jsonify({'success': False, 'error': 'No analyses found for this project'}), 400
        
        # Generate Markdown workshop report
        markdown_path = markdown_service.generate_workshop_report(project, analyses)
        
        if not os.path.exists(markdown_path):
            return jsonify({'success': False, 'error': 'Failed to generate Markdown'}), 500
        
        # Return the Markdown file
        return send_file(
            markdown_path,
            as_attachment=True,
            download_name=os.path.basename(markdown_path),
            mimetype='text/markdown'
        )
        
    except Exception as e:
        if logger:
            logger.error(f"Error exporting Markdown for project {project_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500 

@lead_workshop_bp.route('/lead-workshop/edit-report/<int:project_id>')
def edit_report(project_id: int):
    """Edit report content before PDF generation"""
    if not db:
        return "Database not available", 500
    
    project = db.get_project(project_id)
    if not project:
        return "Project not found", 404
    
    analyses = db.get_project_analyses(project_id, 'relevancy_score', 'DESC')
    
    return render_template('edit_report.html', 
                         project=project,
                         analyses=analyses)

@lead_workshop_bp.route('/lead-workshop/generate-custom-pdf/<int:project_id>', methods=['POST'])
def generate_custom_pdf(project_id: int):
    """Generate PDF with custom content and company branding"""
    if not db or not pdf_service:
        return jsonify({'success': False, 'error': 'Database or PDF service not available'}), 500
    
    try:
        data = request.get_json()
        custom_content = data.get('custom_content', {})
        company_name = data.get('company_name', '4Front 2 Market AB')
        disclaimer = data.get('disclaimer', 'This is a beta-version. Data might be unreliable.')
        
        # Get project details
        project = db.get_project(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Get project analyses (sorted by relevance by default)
        analyses = db.get_project_analyses(project_id, 'relevancy_score', 'DESC')
        if not analyses:
            return jsonify({'success': False, 'error': 'No analyses found for this project'}), 400
        
        # Generate PDF report with custom content
        pdf_path = pdf_service.generate_custom_project_report(
            project, analyses, custom_content, company_name, disclaimer
        )
        
        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'error': 'Failed to generate PDF'}), 500
        
        # Return the PDF file
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=os.path.basename(pdf_path),
            mimetype='application/pdf'
        )
        
    except Exception as e:
        if logger:
            logger.error(f"Error generating custom PDF for project {project_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500 