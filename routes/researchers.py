"""
Researcher management routes

This module provides Flask routes for managing researcher profiles,
ORCID integration, and academic database functionality.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import services with error handling
try:
    from services.orcid_service import orcid_service
except ImportError:
    orcid_service = None

try:
    from services.pubmed_service import pubmed_service
except ImportError:
    pubmed_service = None

try:
    from models.database import db, save_researcher, get_researcher, get_all_researchers, search_researchers
except ImportError:
    db = None

try:
    from utils.logger import get_logger
    logger = get_logger('researcher_routes')
except ImportError:
    logger = None

researchers_bp = Blueprint('researchers', __name__)

@researchers_bp.route('/researchers')
def researchers_home():
    """Display researcher database home page"""
    try:
        # Get recent researchers
        recent_researchers = get_all_researchers(limit=10) if db else []
        
        # Get search statistics
        total_researchers = len(recent_researchers) if recent_researchers else 0
        
        return render_template('researchers.html',
                             recent_researchers=recent_researchers,
                             total_researchers=total_researchers,
                             orcid_available=orcid_service is not None,
                             pubmed_available=pubmed_service is not None)
    except Exception as e:
        if logger:
            logger.error(f"Error in researchers home: {e}")
        flash('Error loading researcher database', 'error')
        return redirect(url_for('leads.show_leads'))

@researchers_bp.route('/researchers/search', methods=['POST'])
def search_researchers_route():
    """Search for researchers using ORCID and other sources"""
    if not orcid_service:
        flash('ORCID service not available', 'error')
        return redirect(url_for('researchers.researchers_home'))
    
    try:
        query = request.form.get('query', '').strip()
        if not query:
            flash('Please enter a search query', 'error')
            return redirect(url_for('researchers.researchers_home'))
        
        max_results = int(request.form.get('max_results', 20))
        
        if logger:
            logger.info(f"Searching researchers for: {query}")
        
        # Search ORCID for researchers
        orcid_results = orcid_service.search_researchers(query, max_results)
        
        # Save search history
        if db:
            db.save_researcher_search_history(query, 'orcid', len(orcid_results))
        
        # Don't automatically save researchers - show for manual selection
        flash(f'Found {len(orcid_results)} researchers. Select the ones you want to save.', 'info')
        
        return render_template('researcher_results.html',
                             query=query,
                             researchers=orcid_results,
                             total_found=len(orcid_results),
                             saved_count=0)  # No auto-save
        
    except Exception as e:
        if logger:
            logger.error(f"Error searching researchers: {e}")
        flash(f'Error searching researchers: {str(e)}', 'error')
        return redirect(url_for('researchers.researchers_home'))

@researchers_bp.route('/researchers/save-selected', methods=['POST'])
def save_selected_researchers():
    """Save manually selected researchers to database"""
    try:
        selected_orcids = request.form.getlist('selected_researchers')
        
        if not selected_orcids:
            flash('No researchers selected', 'warning')
            return redirect(url_for('researchers.researchers_home'))
        
        if not orcid_service:
            flash('ORCID service not available', 'error')
            return redirect(url_for('researchers.researchers_home'))
        
        saved_count = 0
        for orcid_id in selected_orcids:
            try:
                # Get detailed profile from ORCID
                profile = orcid_service.get_researcher_profile(orcid_id)
                if profile and db:
                    researcher_id = save_researcher(
                        orcid_id=profile.get('orcid'),
                        name=profile.get('name', ''),
                        institution=profile.get('institution', ''),
                        bio=profile.get('bio', ''),
                        source='orcid'
                    )
                    if researcher_id:
                        saved_count += 1
            except Exception as e:
                if logger:
                    logger.error(f"Error saving researcher {orcid_id}: {e}")
                continue
        
        flash(f'Successfully saved {saved_count} researchers to database', 'success')
        return redirect(url_for('researchers.researchers_home'))
        
    except Exception as e:
        if logger:
            logger.error(f"Error saving selected researchers: {e}")
        flash(f'Error saving researchers: {str(e)}', 'error')
        return redirect(url_for('researchers.researchers_home'))

@researchers_bp.route('/researchers/<orcid_id>/remove', methods=['POST'])
def remove_researcher(orcid_id: str):
    """Remove a researcher from the database"""
    try:
        if not db:
            flash('Database not available', 'error')
            return redirect(url_for('researchers.researchers_home'))
        
        # Check if researcher exists
        researcher = get_researcher(orcid_id)
        if not researcher:
            flash('Researcher not found in database', 'error')
            return redirect(url_for('researchers.researchers_home'))
        
        # Remove researcher
        success = db.remove_researcher(orcid_id)
        if success:
            flash(f'Researcher {researcher.get("name", orcid_id)} removed from database', 'success')
        else:
            flash('Error removing researcher', 'error')
        
        return redirect(url_for('researchers.researchers_home'))
        
    except Exception as e:
        if logger:
            logger.error(f"Error removing researcher {orcid_id}: {e}")
        flash(f'Error removing researcher: {str(e)}', 'error')
        return redirect(url_for('researchers.researchers_home'))

@researchers_bp.route('/researchers/<orcid_id>/enhance', methods=['POST'])
def enhance_researcher_data(orcid_id: str):
    """Load additional data for a researcher"""
    try:
        if not orcid_service:
            flash('ORCID service not available', 'error')
            return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))
        
        # Get enhanced profile data
        enhanced_profile = orcid_service.get_enhanced_profile(orcid_id)
        if not enhanced_profile:
            flash('Could not load enhanced data for this researcher', 'warning')
            return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))
        
        # Update researcher in database
        if db:
            success = db.update_researcher(
                orcid_id=orcid_id,
                name=enhanced_profile.get('name', ''),
                institution=enhanced_profile.get('institution', ''),
                bio=enhanced_profile.get('bio', ''),
                publications=enhanced_profile.get('publications', []),
                funding=enhanced_profile.get('funding', []),
                keywords=enhanced_profile.get('keywords', []),
                last_updated=datetime.now()
            )
            if success:
                flash('Researcher data enhanced successfully', 'success')
            else:
                flash('Error updating researcher data', 'error')
        
        return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))
        
    except Exception as e:
        if logger:
            logger.error(f"Error enhancing researcher data {orcid_id}: {e}")
        flash(f'Error enhancing researcher data: {str(e)}', 'error')
        return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))

@researchers_bp.route('/researchers/<orcid_id>')
def researcher_profile(orcid_id: str):
    """Display detailed researcher profile"""
    try:
        # Get researcher from database
        researcher = get_researcher(orcid_id) if db else None
        
        if not researcher:
            # Try to get from ORCID service
            if orcid_service:
                orcid_profile = orcid_service.get_researcher_profile(orcid_id)
                if orcid_profile:
                    # Save to database
                    if db:
                        save_researcher(
                            orcid_id=orcid_profile.get('orcid'),
                            name=orcid_profile.get('name', ''),
                            institution=orcid_profile.get('institution', ''),
                            bio=orcid_profile.get('bio', ''),
                            source='orcid'
                        )
                    researcher = orcid_profile
        
        if not researcher:
            flash('Researcher not found', 'error')
            return redirect(url_for('researchers.researchers_home'))
        
        # Get publications if available
        publications = []
        if pubmed_service and researcher.get('orcid'):
            try:
                # This would need to be implemented to fetch publications by ORCID
                pass
            except Exception as e:
                if logger:
                    logger.error(f"Error fetching publications: {e}")
        
        return render_template('researcher_profile.html',
                             researcher=researcher,
                             publications=publications)
        
    except Exception as e:
        if logger:
            logger.error(f"Error loading researcher profile: {e}")
        flash('Error loading researcher profile', 'error')
        return redirect(url_for('researchers.researchers_home'))

@researchers_bp.route('/researchers/<orcid_id>/funding', methods=['POST'])
def lookup_researcher_funding(orcid_id: str):
    """Look up funding information for a specific researcher"""
    try:
        # Get researcher from database
        researcher = get_researcher(orcid_id) if db else None
        if not researcher:
            flash('Researcher not found', 'error')
            return redirect(url_for('researchers.researchers_home'))
        
        # Import research service for funding lookup
        try:
            from services.research_service import research_service
        except ImportError:
            research_service = None
        
        if not research_service:
            flash('Research service not available for funding lookup', 'error')
            return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))
        
        # Get researcher name and institution for funding search
        researcher_name = researcher.get('name', '')
        institution = researcher.get('institution', '')
        
        # Create search queries for funding
        search_queries = []
        if researcher_name:
            search_queries.append(researcher_name)
        if institution:
            search_queries.append(f"{researcher_name} {institution}")
        
        funding_results = []
        for query in search_queries:
            try:
                # Search funding databases for this researcher
                funding_projects = research_service.get_all_projects(query, max_results=10)
                funding_results.extend(funding_projects)
            except Exception as e:
                if logger:
                    logger.error(f"Error searching funding for {query}: {e}")
        
        # Remove duplicates
        unique_funding = []
        seen_ids = set()
        for project in funding_results:
            project_id = f"{project.source}_{project.id}"
            if project_id not in seen_ids:
                unique_funding.append(project)
                seen_ids.add(project_id)
        
        flash(f'Found {len(unique_funding)} funding records for {researcher_name}', 'success')
        
        return render_template('researcher_funding.html',
                             researcher=researcher,
                             funding_projects=unique_funding)
        
    except Exception as e:
        if logger:
            logger.error(f"Error looking up funding for {orcid_id}: {e}")
        flash(f'Error looking up funding: {str(e)}', 'error')
        return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))

@researchers_bp.route('/researchers/<orcid_id>/publications', methods=['POST'])
def lookup_researcher_publications(orcid_id: str):
    """Look up publications for a specific researcher"""
    try:
        # Get researcher from database
        researcher = get_researcher(orcid_id) if db else None
        if not researcher:
            flash('Researcher not found', 'error')
            return redirect(url_for('researchers.researchers_home'))
        
        if not pubmed_service:
            flash('PubMed service not available for publication lookup', 'error')
            return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))
        
        # Get researcher name for publication search
        researcher_name = researcher.get('name', '')
        if not researcher_name:
            flash('Researcher name not available', 'error')
            return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))
        
        # Search PubMed for publications by this researcher
        try:
            publications = pubmed_service.search_articles(researcher_name, max_results=20)
            
            # Save publications to database
            saved_count = 0
            if db:
                for pub in publications:
                    if pub.get('pmid'):
                        pub_id = save_researcher_publication(
                            researcher_id=researcher.get('id'),
                            publication_id=pub.get('pmid'),
                            title=pub.get('title', ''),
                            authors=pub.get('authors', ''),
                            journal=pub.get('journal', ''),
                            year=pub.get('year'),
                            doi=pub.get('doi'),
                            url=pub.get('url'),
                            abstract=pub.get('abstract', ''),
                            source='pubmed'
                        )
                        if pub_id:
                            saved_count += 1
            
            flash(f'Found {len(publications)} publications for {researcher_name}', 'success')
            
            return render_template('researcher_publications.html',
                                 researcher=researcher,
                                 publications=publications,
                                 saved_count=saved_count)
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching publications for {researcher_name}: {e}")
            flash(f'Error searching publications: {str(e)}', 'error')
            return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))
        
    except Exception as e:
        if logger:
            logger.error(f"Error looking up publications for {orcid_id}: {e}")
        flash(f'Error looking up publications: {str(e)}', 'error')
        return redirect(url_for('researchers.researcher_profile', orcid_id=orcid_id))

@researchers_bp.route('/researchers/database')
def researcher_database():
    """Display all researchers in the database"""
    try:
        if not db:
            flash('Database not available', 'error')
            return redirect(url_for('researchers.researchers_home'))
        
        # Get all researchers with pagination
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        all_researchers = get_all_researchers()
        total = len(all_researchers)
        
        # Simple pagination
        start = offset
        end = start + per_page
        paginated_researchers = all_researchers[start:end]
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('researcher_database.html',
                             researchers=paginated_researchers,
                             page=page,
                             total_pages=total_pages,
                             total=total)
        
    except Exception as e:
        if logger:
            logger.error(f"Error loading researcher database: {e}")
        flash('Error loading researcher database', 'error')
        return redirect(url_for('researchers.researchers_home'))

# REST API endpoints
@researchers_bp.route('/api/researchers', methods=['GET'])
def get_researchers_api():
    """REST API endpoint for getting all researchers"""
    if not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        query = request.args.get('q')
        
        if query:
            researchers = search_researchers(query, limit=per_page)
        else:
            researchers = get_all_researchers(limit=per_page)
        
        return jsonify({
            'researchers': researchers,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(researchers)
            }
        })
        
    except Exception as e:
        if logger:
            logger.error(f"API researchers fetch failed: {e}")
        return jsonify({'error': f'Failed to fetch researchers: {str(e)}'}), 500

@researchers_bp.route('/api/researchers/<orcid_id>', methods=['GET'])
def get_researcher_api(orcid_id: str):
    """REST API endpoint for getting a specific researcher"""
    if not db:
        return jsonify({'error': 'Database not available'}), 500
    
    try:
        researcher = get_researcher(orcid_id)
        if not researcher:
            return jsonify({'error': 'Researcher not found'}), 404
        
        return jsonify({'researcher': researcher})
        
    except Exception as e:
        if logger:
            logger.error(f"API researcher fetch failed: {e}")
        return jsonify({'error': f'Failed to fetch researcher: {str(e)}'}), 500

@researchers_bp.route('/api/researchers/search', methods=['POST'])
def search_researchers_api():
    """REST API endpoint for searching researchers"""
    if not orcid_service:
        return jsonify({'error': 'ORCID service not available'}), 503
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        max_results = data.get('max_results', 20)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Search ORCID
        orcid_results = orcid_service.search_researchers(query, max_results)
        
        # Save to database
        saved_count = 0
        if db:
            for researcher in orcid_results:
                if researcher.get('orcid'):
                    researcher_id = save_researcher(
                        orcid_id=researcher.get('orcid'),
                        name=researcher.get('name', ''),
                        institution=researcher.get('institution', ''),
                        bio=researcher.get('bio', ''),
                        source='orcid'
                    )
                    if researcher_id:
                        saved_count += 1
        
        return jsonify({
            'researchers': orcid_results,
            'total_found': len(orcid_results),
            'saved_count': saved_count
        })
        
    except Exception as e:
        if logger:
            logger.error(f"API researcher search failed: {e}")
        return jsonify({'error': f'Failed to search researchers: {str(e)}'}), 500 