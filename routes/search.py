from flask import Blueprint, render_template, request, redirect, url_for
from typing import List, Dict, Any

from services.serp_service import serp_service
from services.ollama_service import ollama_service
from services.pubmed_service import pubmed_service
from services.orcid_service import orcid_service
from models.database import db
from config import SERP_ENGINES, DEFAULT_RESEARCH_QUESTION

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
def perform_search():
    """Perform search across selected sources"""
    query = request.form['query']
    research_question = request.form.get('research_question', DEFAULT_RESEARCH_QUESTION)
    search_type = request.form.get('search_type', 'articles')  # articles, profiles, both
    
    print(f"[LOG] Sökterm mottagen: {query}")
    print(f"[LOG] Frågeställning: {research_question}")
    print(f"[LOG] Söktyp: {search_type}")
    
    all_results = []
    relevant_leads = 0
    
    # SERP search (articles)
    if search_type in ['articles', 'both']:
        selected_engines = request.form.getlist('engines')
        if not selected_engines:
            selected_engines = ["google"]
        
        print(f"[LOG] Valda SERP-motorer: {selected_engines}")
        serp_results = serp_service.search(query, selected_engines)
        all_results.extend(serp_results)
        
        # Process SERP results
        for res in serp_results:
            title = res.get('title', '')
            snippet = res.get('snippet', '')
            link = res.get('link', '')
            print(f"[LOG] Analyserar SERP lead: {title}")
            
            ai_summary = ollama_service.analyze_relevance(title, snippet, link, research_question)
            
            if ai_summary:  # Only save if AI thinks it's relevant
                db.save_lead(title, snippet, link, ai_summary, source='serp')
                print(f"[LOG] Relevant SERP lead sparad: {title}")
                relevant_leads += 1
            else:
                print(f"[LOG] Inte relevant SERP lead, hoppar över: {title}")
    
    # PubMed search (articles)
    if search_type in ['articles', 'both']:
        print(f"[LOG] PubMed-sökning för: {query}")
        pubmed_results = pubmed_service.search_articles(query)
        # TODO: Process PubMed results when implemented
    
    # ORCID search (profiles)
    if search_type in ['profiles', 'both']:
        print(f"[LOG] ORCID-sökning för: {query}")
        orcid_results = orcid_service.search_researchers(query)
        # TODO: Process ORCID results when implemented
    
    print(f"[LOG] Totalt {len(all_results)} leads analyserade, {relevant_leads} relevanta sparade.")
    
    # Save search history
    engines_str = ','.join(selected_engines) if 'selected_engines' in locals() else 'none'
    db.save_search_history(query, research_question, engines_str, relevant_leads)
    
    return redirect(url_for('leads.show_leads'))

@search_bp.route('/search_form')
def search_form():
    """Display search form"""
    return render_template('search_form.html', 
                         engines=SERP_ENGINES,
                         research_question=DEFAULT_RESEARCH_QUESTION) 