from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from typing import List, Dict, Any
import logging
import time

# Import services with error handling
try:
    from services.serp_service import serp_service
except ImportError:
    serp_service = None

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
    from models.database import db
except ImportError:
    db = None

try:
    from config import config
    SERP_ENGINES = ["google", "bing", "duckduckgo"]
    DEFAULT_RESEARCH_QUESTION = config.get('DEFAULT_RESEARCH_QUESTION', 'epigenetics and pre-diabetes')
except ImportError:
    SERP_ENGINES = ["google"]
    DEFAULT_RESEARCH_QUESTION = "epigenetics and pre-diabetes"

try:
    from utils.logger import get_logger
    logger = get_logger('search')
except ImportError:
    logger = None

try:
    from utils.progress_manager import get_progress_manager, ProgressContext, ProgressStatus, SEARCH_STEPS
except ImportError:
    get_progress_manager = None
    ProgressContext = None
    ProgressStatus = None
    SEARCH_STEPS = None

try:
    from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
except ImportError:
    LeadfinderAutoGPTIntegration = None

# Initialize AutoGPT integration
try:
    autogpt_integration = LeadfinderAutoGPTIntegration("mistral:latest")
    AUTOGPT_AVAILABLE = True
except Exception as e:
    logging.warning(f"AutoGPT integration not available: {e}")
    autogpt_integration = None
    AUTOGPT_AVAILABLE = False

search_bp = Blueprint('search', __name__)

def collect_leads(query: str, engines: List[str], max_leads: int = 10) -> List[Dict[str, Any]]:
    """Collect leads without AI analysis"""
    leads = []
    
    if serp_service:
        serp_results = serp_service.search(query, engines, num_results=max_leads)
        for res in serp_results:
            leads.append({
                'title': res.get('title', ''),
                'snippet': res.get('snippet', ''),
                'link': res.get('link', ''),
                'source': 'serp'
            })
    
    return leads

def analyze_leads_with_ai(leads: List[Dict[str, Any]], research_question: str) -> List[Dict[str, Any]]:
    """Add AI analysis to leads if AI service is available"""
    if not ollama_service:
        # If no AI service, just add a default summary
        for lead in leads:
            if research_question == "general search":
                lead['ai_summary'] = "Manual review required - standard search"
            else:
                lead['ai_summary'] = f"Manual review required for: {research_question}"
        return leads
    
    if logger:
        logger.info(f"Analyzing {len(leads)} leads with AI")
    
    analyzed_leads = []
    for lead in leads:
        try:
            # Try to get AI summary, but don't fail if it doesn't work
            if research_question == "general search":
                # For general search, use a simpler analysis
                ai_summary = ollama_service.analyze_relevance(
                    lead['title'], 
                    lead['snippet'], 
                    lead['link'], 
                    "general relevance"
                )
            else:
                ai_summary = ollama_service.analyze_relevance(
                    lead['title'], 
                    lead['snippet'], 
                    lead['link'], 
                    research_question
                )
            lead['ai_summary'] = ai_summary if ai_summary else f"AI analysis failed - manual review required"
        except Exception as e:
            if logger:
                logger.warning(f"AI analysis failed for lead '{lead['title']}': {e}")
            lead['ai_summary'] = f"AI analysis failed - manual review required"
        
        analyzed_leads.append(lead)
    
    return analyzed_leads

@search_bp.route('/search', methods=['POST'])
def perform_search():
    """Perform search and save all results, with optional AI analysis"""
    try:
        # Safe form access with validation
        query = request.form.get('query', '').strip()
        if not query:
            flash('Search term is required', 'error')
            return redirect(url_for('leads.show_leads'))
        
        research_question = request.form.get('research_question', '').strip()
        if not research_question:
            research_question = "general search"  # Default for standard search
        search_type = request.form.get('search_type', 'articles')  # articles, profiles, both
        use_ai_analysis = request.form.get('use_ai_analysis') == 'on'  # Checkbox for AI analysis
        
        if logger:
            logger.info(f"Search term received: {query}")
            logger.info(f"Research question: {research_question}")
            logger.info(f"Search type: {search_type}")
            logger.info(f"AI analysis: {'Enabled' if use_ai_analysis else 'Disabled'}")
        
        selected_engines = request.form.getlist('engines')
        if not selected_engines:
            selected_engines = ["google"]
        
        if logger:
            logger.info(f"Selected SERP engines: {selected_engines}")
        
        # Check if serp_service is available
        if not serp_service:
            flash('Search service not available. Please check configuration.', 'error')
            return redirect(url_for('leads.show_leads'))
        
        # Step 1: Collect leads without AI analysis
        leads = collect_leads(query, selected_engines, max_leads=10)
        
        if not leads:
            if logger:
                logger.info("No leads found")
            flash('No results found for your search', 'warning')
            return redirect(url_for('leads.show_leads'))
        
        if logger:
            logger.info(f"Found {len(leads)} leads")
        
        # Step 2: Add AI analysis if requested
        if use_ai_analysis:
            # Use AutoGPT if available, otherwise fall back to Ollama
            if AUTOGPT_AVAILABLE and autogpt_integration:
                try:
                    # Enhanced search with AutoGPT
                    enhanced_results = autogpt_integration.enhance_search_results(leads, query)
                    if enhanced_results and enhanced_results.get('status') == 'COMPLETED':
                        # AutoGPT provided analysis, use it
                        for i, lead in enumerate(leads):
                            lead['ai_summary'] = f"AutoGPT Analysis: {enhanced_results.get('output', '')[:200]}..."
                    else:
                        # Fall back to regular AI analysis
                        leads = analyze_leads_with_ai(leads, research_question)
                except Exception as e:
                    if logger:
                        logger.warning(f"AutoGPT analysis failed, falling back to Ollama: {e}")
                    leads = analyze_leads_with_ai(leads, research_question)
            else:
                # Use regular Ollama analysis
                leads = analyze_leads_with_ai(leads, research_question)
        else:
            # Add default summary for leads without AI analysis
            for lead in leads:
                if research_question == "general search":
                    lead['ai_summary'] = "Manual review required - standard search"
                else:
                    lead['ai_summary'] = f"Manual review required for: {research_question}"
        
        # Step 3: Save all leads (not just "relevant" ones)
        saved_count = 0
        for lead in leads:
            if db:
                try:
                    success = db.save_lead(
                        lead['title'], 
                        lead['snippet'],  # This will be saved as 'description' in database
                        lead['link'], 
                        lead.get('ai_summary', ''), 
                        source=lead['source']
                    )
                    if success:
                        saved_count += 1
                except Exception as e:
                    if logger:
                        logger.error(f"Failed to save lead '{lead['title']}': {e}")
                    continue
        
        if logger:
            logger.info(f"Saved {saved_count} leads out of {len(leads)} total")
        
        # PubMed search (articles) - TODO: implement similar processing
        if search_type in ['articles', 'both'] and pubmed_service:
            if logger:
                logger.info(f"PubMed search for: {query}")
            pubmed_results = pubmed_service.search_articles(query)
            # TODO: Process PubMed results when implemented
        
        # ORCID search (profiles) - TODO: implement similar processing
        if search_type in ['profiles', 'both'] and orcid_service:
            if logger:
                logger.info(f"ORCID search for: {query}")
            orcid_results = orcid_service.search_researchers(query)
            # TODO: Process ORCID results when implemented
        
        # Save search history
        if db:
            engines_str = ','.join(selected_engines)
            db.save_search_history(query, research_question, engines_str, saved_count)
        
        flash(f'Search completed! {saved_count} leads saved.', 'success')
        return redirect(url_for('leads.show_leads'))
        
    except Exception as e:
        if logger:
            logger.error(f"Search error: {e}")
        flash(f'Search failed: {str(e)}', 'error')
        return redirect(url_for('leads.show_leads'))

@search_bp.route('/search_ajax', methods=['POST'])
def perform_search_ajax():
    """AJAX version of search with progress tracking"""
    try:
        # Safe form access with validation
        query = request.form.get('query', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Search term is required'}), 400
        
        research_question = request.form.get('research_question', '').strip()
        if not research_question:
            research_question = "general search"
        
        search_type = request.form.get('search_type', 'articles')
        use_ai_analysis = request.form.get('use_ai_analysis') == 'on'
        
        selected_engines = request.form.getlist('engines')
        if not selected_engines:
            selected_engines = ["google"]
        
        if logger:
            logger.info(f"AJAX Search: {query} with engines {selected_engines}")
        
        # Create progress tracking
        operation_id = None
        if get_progress_manager:
            progress_manager = get_progress_manager()
            operation_id = progress_manager.create_operation(
                name=f"Search: {query[:50]}...",
                description=f"Searching for '{query}' across {len(selected_engines)} engines",
                steps=SEARCH_STEPS
            )
            progress_manager.start_operation(operation_id)
        
        leads = []
        saved_count = 0
        
        try:
            # Step 1: Initialize search
            if operation_id:
                progress_manager.update_step(operation_id, "step_1", 0.5, ProgressStatus.RUNNING, 
                                           {"query": query, "engines": selected_engines})
            
            # Step 2: Web search
            if operation_id:
                progress_manager.update_step(operation_id, "step_1", 1.0, ProgressStatus.COMPLETED)
                progress_manager.update_step(operation_id, "step_2", 0.0, ProgressStatus.RUNNING)
            
            leads = collect_leads(query, selected_engines, max_leads=10)
            
            if not leads:
                if operation_id:
                    progress_manager.complete_operation(operation_id, "No results found")
                return jsonify({'success': False, 'error': 'No results found for your search'}), 404
            
            if operation_id:
                progress_manager.update_step(operation_id, "step_2", 1.0, ProgressStatus.COMPLETED,
                                           {"results_found": len(leads)})
            
            # Step 3: Research search (if applicable)
            if search_type in ['both', 'research'] and operation_id:
                progress_manager.update_step(operation_id, "step_3", 0.0, ProgressStatus.RUNNING)
                # Add research search logic here
                progress_manager.update_step(operation_id, "step_3", 1.0, ProgressStatus.COMPLETED)
            
            # Step 4: Funding search (if applicable)
            if search_type in ['both', 'funding'] and operation_id:
                progress_manager.update_step(operation_id, "step_4", 0.0, ProgressStatus.RUNNING)
                # Add funding search logic here
                progress_manager.update_step(operation_id, "step_4", 1.0, ProgressStatus.COMPLETED)
            
            # Step 5: AI analysis
            if use_ai_analysis:
                if operation_id:
                    progress_manager.update_step(operation_id, "step_5", 0.0, ProgressStatus.RUNNING)
                
                # Use AutoGPT if available, otherwise fall back to Ollama
                if AUTOGPT_AVAILABLE and autogpt_integration:
                    try:
                        # Enhanced search with AutoGPT
                        enhanced_results = autogpt_integration.enhance_search_results(leads, query)
                        if enhanced_results and enhanced_results.get('status') == 'COMPLETED':
                            # AutoGPT provided analysis, use it
                            for i, lead in enumerate(leads):
                                lead['ai_summary'] = f"AutoGPT Analysis: {enhanced_results.get('output', '')[:200]}..."
                        else:
                            # Fall back to regular AI analysis
                            leads = analyze_leads_with_ai(leads, research_question)
                    except Exception as e:
                        if logger:
                            logger.warning(f"AutoGPT analysis failed, falling back to Ollama: {e}")
                        leads = analyze_leads_with_ai(leads, research_question)
                else:
                    # Use regular Ollama analysis
                    leads = analyze_leads_with_ai(leads, research_question)
                
                if operation_id:
                    progress_manager.update_step(operation_id, "step_5", 1.0, ProgressStatus.COMPLETED,
                                               {"analyzed_leads": len(leads)})
            else:
                for lead in leads:
                    if research_question == "general search":
                        lead['ai_summary'] = "Manual review required - standard search"
                    else:
                        lead['ai_summary'] = f"Manual review required for: {research_question}"
                
                if operation_id:
                    progress_manager.update_step(operation_id, "step_5", 1.0, ProgressStatus.COMPLETED,
                                               {"manual_review": len(leads)})
            
            # Step 6: Save results
            if operation_id:
                progress_manager.update_step(operation_id, "step_6", 0.0, ProgressStatus.RUNNING)
            
            for lead in leads:
                if db:
                    success = db.save_lead(
                        lead['title'], 
                        lead['snippet'], 
                        lead['link'], 
                        lead.get('ai_summary', ''), 
                        source=lead['source']
                    )
                    if success:
                        saved_count += 1
            
            # Save search history
            if db:
                engines_str = ','.join(selected_engines)
                db.save_search_history(query, research_question, engines_str, saved_count)
            
            if operation_id:
                progress_manager.update_step(operation_id, "step_6", 1.0, ProgressStatus.COMPLETED,
                                           {"saved_leads": saved_count})
                progress_manager.complete_operation(operation_id)
            
        except Exception as e:
            if operation_id:
                progress_manager.complete_operation(operation_id, str(e))
            raise
        
        return jsonify({
            'success': True,
            'message': f'Search completed! {saved_count} leads saved.',
            'saved_count': saved_count,
            'total_leads': len(leads),
            'operation_id': operation_id
        })
        
    except Exception as e:
        if logger:
            logger.error(f"AJAX Search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@search_bp.route('/search_form')
def search_form():
    """Display search form"""
    return render_template('search_form.html', 
                         engines=SERP_ENGINES,
                         research_question=DEFAULT_RESEARCH_QUESTION,
                         autogpt_available=AUTOGPT_AVAILABLE) 

@search_bp.route('/test_search')
def test_search():
    """Test route to verify search functionality"""
    try:
        # Test serp_service
        serp_status = "Available" if serp_service else "Not available"
        
        # Test database
        db_status = "Available" if db else "Not available"
        
        # Test configuration
        config_status = "Available" if 'config' in globals() else "Not available"
        
        # Test serpapi key
        try:
            from config import config
            serpapi_key = config.get('SERPAPI_KEY', 'Not set')
            serpapi_status = "Set" if serpapi_key and serpapi_key != 'Not set' else "Not set"
        except:
            serpapi_status = "Error accessing"
        
        return {
            'serp_service': serp_status,
            'database': db_status,
            'config': config_status,
            'serpapi_key': serpapi_status,
            'engines': SERP_ENGINES,
            'default_question': DEFAULT_RESEARCH_QUESTION
        }
    except Exception as e:
        return {'error': str(e)} 



@search_bp.route('/analyze_lead', methods=['POST'])
def analyze_lead():
    """Analyze a specific lead with AutoGPT"""
    if not AUTOGPT_AVAILABLE or not autogpt_integration:
        return jsonify({'error': 'AutoGPT not available'}), 400
    
    try:
        data = request.get_json()
        lead_title = data.get('title', '')
        lead_description = data.get('description', '')
        research_question = session.get('search_query', '')
        
        if not lead_title:
            return jsonify({'error': 'Lead title is required'}), 400
        
        # Generate lead summary
        summary = autogpt_integration.generate_lead_summary(
            lead_title, 
            lead_description, 
            research_question
        )
        
        if summary.get('status') == 'COMPLETED':
            return jsonify({
                'success': True,
                'analysis': summary.get('output', ''),
                'lead_title': lead_title
            })
        else:
            return jsonify({
                'error': summary.get('error', 'Analysis failed')
            }), 500
            
    except Exception as e:
        logging.error(f"Lead analysis error: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@search_bp.route('/research_leads', methods=['POST'])
def research_leads():
    """Research leads for a specific company/industry"""
    if not AUTOGPT_AVAILABLE or not autogpt_integration:
        return jsonify({'error': 'AutoGPT not available'}), 400
    
    try:
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        industry = data.get('industry', '').strip()
        
        if not company_name or not industry:
            return jsonify({'error': 'Company name and industry are required'}), 400
        
        # Research leads
        results = autogpt_integration.research_leads(company_name, industry)
        
        if results.get('status') == 'COMPLETED':
            return jsonify({
                'success': True,
                'research': results,
                'company_name': company_name,
                'industry': industry
            })
        else:
            return jsonify({
                'error': results.get('error', 'Research failed')
            }), 500
            
    except Exception as e:
        logging.error(f"Lead research error: {e}")
        return jsonify({'error': f'Research failed: {str(e)}'}), 500 