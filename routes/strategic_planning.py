"""
Strategic Planning Routes

This module provides Flask routes for strategic planning including
company profiles, market research, and strategic plan generation.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from typing import Dict, Any, List
import json

try:
    from models.strategic_planning import get_strategic_db
except ImportError:
    get_strategic_db = None

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from services.company_mining_service import CompanyMiningService
except ImportError:
    CompanyMiningService = None

try:
    from utils.logger import get_logger
    logger = get_logger('strategic_planning_routes')
except ImportError:
    logger = None

strategic_bp = Blueprint('strategic', __name__)

@strategic_bp.route('/strategic')
def strategic_dashboard():
    """Strategic planning dashboard"""
    if not get_strategic_db:
        flash('Strategic planning system not available', 'error')
        return redirect(url_for('leads.show_leads'))
    
    try:
        db = get_strategic_db()
        companies = db.get_all_company_profiles()
        
        return render_template('strategic_dashboard.html', companies=companies)
        
    except Exception as e:
        if logger:
            logger.error(f"Strategic dashboard error: {e}")
        flash(f'Error loading strategic dashboard: {str(e)}', 'error')
        return redirect(url_for('leads.show_leads'))

@strategic_bp.route('/strategic/company/new', methods=['GET', 'POST'])
def create_company_profile():
    """Create a new company profile"""
    if not get_strategic_db:
        return jsonify({'success': False, 'error': 'Strategic planning system not available'}), 500
    
    if request.method == 'GET':
        # Redirect to strategic dashboard since the form is in a modal
        return redirect(url_for('strategic.strategic_dashboard'))
    
    try:
        data = request.get_json()
        company_data = {
            'company_name': data.get('company_name', '').strip(),
            'product_description': data.get('product_description', '').strip(),
            'target_market': data.get('target_market', '').strip(),
            'usps': data.get('usps', '').strip(),
            'service_portfolio': data.get('service_portfolio', '').strip(),
            'industry': data.get('industry', '').strip(),
            'business_model': data.get('business_model', '').strip(),
            'revenue_model': data.get('revenue_model', '').strip()
        }
        
        if not company_data['company_name']:
            return jsonify({'success': False, 'error': 'Company name is required'}), 400
        
        if not company_data['product_description']:
            return jsonify({'success': False, 'error': 'Product description is required'}), 400
        
        if not company_data['usps']:
            return jsonify({'success': False, 'error': 'Unique Selling Propositions (USPs) are required'}), 400
        
        db = get_strategic_db()
        company_id = db.create_company_profile(company_data)
        
        return jsonify({
            'success': True,
            'company_id': company_id,
            'message': f'Company profile "{company_data["company_name"]}" created successfully'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Create company profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@strategic_bp.route('/strategic/company/<int:company_id>')
def view_company_profile(company_id):
    """View company profile and strategic planning options"""
    if not get_strategic_db:
        flash('Strategic planning system not available', 'error')
        return redirect(url_for('strategic.strategic_dashboard'))
    
    try:
        db = get_strategic_db()
        company = db.get_company_profile(company_id)
        
        if not company:
            flash('Company profile not found', 'error')
            return redirect(url_for('strategic.strategic_dashboard'))
        
        # Get existing data
        market_research = db.get_market_research(company_id)
        swot_analysis = db.get_swot_analysis(company_id)
        strategic_plans = db.get_strategic_plans(company_id)
        financial_projections = db.get_financial_projections(company_id)
        
        return render_template('company_profile_view.html',
                             company=company,
                             market_research=market_research,
                             swot_analysis=swot_analysis,
                             strategic_plans=strategic_plans,
                             financial_projections=financial_projections)
        
    except Exception as e:
        if logger:
            logger.error(f"View company profile error: {e}")
        flash(f'Error loading company profile: {str(e)}', 'error')
        return redirect(url_for('strategic.strategic_dashboard'))

@strategic_bp.route('/strategic/company/<int:company_id>/update', methods=['POST'])
def update_company_profile(company_id):
    """Update an existing company profile"""
    if not get_strategic_db:
        return jsonify({'success': False, 'error': 'Strategic planning system not available'}), 500
    
    try:
        data = request.get_json()
        company_data = {
            'company_name': data.get('company_name', '').strip(),
            'product_description': data.get('product_description', '').strip(),
            'target_market': data.get('target_market', '').strip(),
            'usps': data.get('usps', '').strip(),
            'service_portfolio': data.get('service_portfolio', '').strip(),
            'industry': data.get('industry', '').strip(),
            'business_model': data.get('business_model', '').strip(),
            'revenue_model': data.get('revenue_model', '').strip()
        }
        
        if not company_data['company_name']:
            return jsonify({'success': False, 'error': 'Company name is required'}), 400
        
        if not company_data['product_description']:
            return jsonify({'success': False, 'error': 'Product description is required'}), 400
        
        if not company_data['usps']:
            return jsonify({'success': False, 'error': 'Unique Selling Propositions (USPs) are required'}), 400
        
        db = get_strategic_db()
        success = db.update_company_profile(company_id, company_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Company profile "{company_data["company_name"]}" updated successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Company profile not found'}), 404
        
    except Exception as e:
        if logger:
            logger.error(f"Update company profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@strategic_bp.route('/strategic/company/<int:company_id>/delete', methods=['POST'])
def delete_company_profile(company_id):
    """Delete a company profile"""
    if not get_strategic_db:
        return jsonify({'success': False, 'error': 'Strategic planning system not available'}), 500
    
    try:
        db = get_strategic_db()
        company = db.get_company_profile(company_id)
        
        if not company:
            return jsonify({'success': False, 'error': 'Company profile not found'}), 404
        
        success = db.delete_company_profile(company_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Company profile "{company["company_name"]}" deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to delete company profile'}), 500
        
    except Exception as e:
        if logger:
            logger.error(f"Delete company profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@strategic_bp.route('/strategic/company/<int:company_id>/mine-data', methods=['POST'])
def mine_company_data(company_id):
    """Mine comprehensive company data using the company mining service"""
    if not get_strategic_db or not CompanyMiningService:
        return jsonify({'success': False, 'error': 'Strategic planning or mining service not available'}), 500
    
    try:
        db = get_strategic_db()
        company = db.get_company_profile(company_id)
        
        if not company:
            return jsonify({'success': False, 'error': 'Company profile not found'}), 404
        
        # Initialize mining service
        mining_service = CompanyMiningService()
        
        # Mine comprehensive company data
        mined_data = mining_service.mine_company_data(company['company_name'])
        
        if 'error' in mined_data:
            return jsonify({'success': False, 'error': mined_data['error']}), 500
        
        # Update company profile with mined data
        enhanced_profile = _enhance_company_profile(company, mined_data)
        db.update_company_profile(company_id, enhanced_profile)
        
        return jsonify({
            'success': True,
            'message': f'Comprehensive data mining completed for {company["company_name"]}',
            'data_summary': {
                'basic_info': bool(mined_data.get('basic_info')),
                'news_analysis': bool(mined_data.get('news_analysis')),
                'financial_intelligence': bool(mined_data.get('financial_intelligence')),
                'ip_landscape': bool(mined_data.get('ip_landscape')),
                'industry_research': bool(mined_data.get('industry_research')),
                'talent_mapping': bool(mined_data.get('talent_mapping'))
            }
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Company data mining error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@strategic_bp.route('/strategic/company/<int:company_id>/market-research', methods=['POST'])
def conduct_market_research(company_id):
    """Conduct market research for a company"""
    if not get_strategic_db or not ollama_service:
        return jsonify({'success': False, 'error': 'Strategic planning or AI service not available'}), 500
    
    try:
        db = get_strategic_db()
        company = db.get_company_profile(company_id)
        
        if not company:
            return jsonify({'success': False, 'error': 'Company profile not found'}), 404
        
        # Generate market research using AI
        research_data = _generate_market_research(company)
        
        # Save to database
        research_id = db.save_market_research(company_id, research_data)
        
        return jsonify({
            'success': True,
            'research_id': research_id,
            'message': f'Market research completed for {company["company_name"]}'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Market research error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@strategic_bp.route('/strategic/company/<int:company_id>/swot-analysis', methods=['POST'])
def conduct_swot_analysis(company_id):
    """Conduct SWOT analysis for a company"""
    if not get_strategic_db or not ollama_service:
        return jsonify({'success': False, 'error': 'Strategic planning or AI service not available'}), 500
    
    try:
        db = get_strategic_db()
        company = db.get_company_profile(company_id)
        
        if not company:
            return jsonify({'success': False, 'error': 'Company profile not found'}), 404
        
        # Generate SWOT analysis using AI
        swot_data = _generate_swot_analysis(company)
        
        # Save to database
        swot_id = db.save_swot_analysis(company_id, swot_data)
        
        return jsonify({
            'success': True,
            'swot_id': swot_id,
            'message': f'SWOT analysis completed for {company["company_name"]}'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"SWOT analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@strategic_bp.route('/strategic/company/<int:company_id>/generate-plan/<plan_type>', methods=['POST'])
def generate_strategic_plan(company_id, plan_type):
    """Generate strategic plan (market plan, business plan, or GTM strategy)"""
    if not get_strategic_db or not ollama_service:
        return jsonify({'success': False, 'error': 'Strategic planning or AI service not available'}), 500
    
    try:
        db = get_strategic_db()
        company = db.get_company_profile(company_id)
        
        if not company:
            return jsonify({'success': False, 'error': 'Company profile not found'}), 404
        
        # Get supporting data
        market_research = db.get_market_research(company_id)
        swot_analysis = db.get_swot_analysis(company_id)
        financial_projections = db.get_financial_projections(company_id)
        
        # Generate plan based on type
        if plan_type == 'market_plan':
            plan_content = _generate_market_plan(company, market_research, swot_analysis)
        elif plan_type == 'business_plan':
            plan_content = _generate_business_plan(company, market_research, swot_analysis, financial_projections)
        elif plan_type == 'gtm_strategy':
            plan_content = _generate_gtm_strategy(company, market_research, swot_analysis)
        else:
            return jsonify({'success': False, 'error': 'Invalid plan type'}), 400
        
        # Save to database
        plan_id = db.save_strategic_plan(company_id, plan_type, plan_content)
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'plan_type': plan_type,
            'message': f'{plan_type.replace("_", " ").title()} generated for {company["company_name"]}'
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Generate plan error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@strategic_bp.route('/strategic/company/<int:company_id>/comprehensive-analysis', methods=['POST'])
def conduct_comprehensive_analysis(company_id):
    """Conduct comprehensive analysis including data mining, market research, and SWOT analysis"""
    if not get_strategic_db:
        return jsonify({'success': False, 'error': 'Strategic planning system not available'}), 500
    
    try:
        db = get_strategic_db()
        company = db.get_company_profile(company_id)
        
        if not company:
            return jsonify({'success': False, 'error': 'Company profile not found'}), 404
        
        # Step 1: Mine comprehensive data
        if CompanyMiningService:
            mining_service = CompanyMiningService()
            mined_data = mining_service.mine_company_data(company['company_name'])
            
            if 'error' not in mined_data:
                enhanced_profile = _enhance_company_profile(company, mined_data)
                db.update_company_profile(company_id, enhanced_profile)
        
        # Step 2: Generate market research
        if ollama_service:
            research_data = _generate_market_research(company)
            db.save_market_research(company_id, research_data)
        
        # Step 3: Generate SWOT analysis
        if ollama_service:
            swot_data = _generate_swot_analysis(company)
            db.save_swot_analysis(company_id, swot_data)
        
        return jsonify({
            'success': True,
            'message': f'Comprehensive analysis completed for {company["company_name"]}',
            'analysis_components': {
                'data_mining': CompanyMiningService is not None,
                'market_research': ollama_service is not None,
                'swot_analysis': ollama_service is not None
            }
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Comprehensive analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def _enhance_company_profile(company: Dict[str, Any], mined_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance company profile with mined data"""
    enhanced_profile = company.copy()
    
    # Enhance with basic info
    if mined_data.get('basic_info') and not mined_data['basic_info'].get('error'):
        basic_info = mined_data['basic_info']
        enhanced_profile.update({
            'website': basic_info.get('website', company.get('website')),
            'description': basic_info.get('description', company.get('description')),
            'industry': basic_info.get('industry', company.get('industry')),
            'location': basic_info.get('location', company.get('location'))
        })
    
    # Add mined data as JSON fields
    enhanced_profile.update({
        'mined_data': mined_data,
        'last_mined': mined_data.get('mining_timestamp')
    })
    
    return enhanced_profile

def _generate_market_research(company: Dict[str, Any]) -> Dict[str, Any]:
    """Generate market research using AI"""
    try:
        # Use mined data if available
        mined_data = company.get('mined_data', {})
        industry_research = mined_data.get('industry_research', {})
        financial_intelligence = mined_data.get('financial_intelligence', {})
        
        prompt = f"""
        Conduct comprehensive market research for {company['company_name']}:
        
        Company Details:
        - Product: {company.get('product_description', 'N/A')}
        - Target Market: {company.get('target_market', 'N/A')}
        - Industry: {company.get('industry', 'N/A')}
        - USPs: {company.get('usps', 'N/A')}
        
        Available Research Data:
        - Industry Research: {industry_research.get('industry_trends', [])}
        - Market Analysis: {industry_research.get('market_size_data', {})}
        - Financial Intelligence: {financial_intelligence.get('funding_history', {})}
        
        Please provide:
        1. Market Size Analysis (TAM, SAM, SOM)
        2. Competitive Landscape Analysis
        3. Industry Trends and Growth Projections
        4. Customer Insights and Pain Points
        5. Market Segments and Opportunities
        6. Growth Projections and Forecasts
        
        Format the response as structured data with clear sections.
        """
        
        response = ollama_service.generate_text(prompt)
        
        # Parse the response into structured data
        research_data = {
            'market_size_data': {'analysis': response},
            'competitive_analysis': {'analysis': response},
            'industry_trends': {'analysis': response},
            'customer_insights': {'analysis': response},
            'market_segments': {'analysis': response},
            'growth_projections': {'analysis': response},
            'mined_data_integration': bool(mined_data)
        }
        
        return research_data
        
    except Exception as e:
        if logger:
            logger.error(f"Market research generation error: {e}")
        raise

def _generate_swot_analysis(company: Dict[str, Any]) -> Dict[str, Any]:
    """Generate SWOT analysis using AI"""
    try:
        # Use mined data if available
        mined_data = company.get('mined_data', {})
        news_analysis = mined_data.get('news_analysis', {})
        financial_intelligence = mined_data.get('financial_intelligence', {})
        ip_landscape = mined_data.get('ip_landscape', {})
        
        prompt = f"""
        Conduct a comprehensive SWOT analysis for {company['company_name']}:
        
        Company Details:
        - Product: {company.get('product_description', 'N/A')}
        - Target Market: {company.get('target_market', 'N/A')}
        - Industry: {company.get('industry', 'N/A')}
        - USPs: {company.get('usps', 'N/A')}
        - Business Model: {company.get('business_model', 'N/A')}
        
        Available Intelligence:
        - News Sentiment: {news_analysis.get('sentiment_analysis', 'N/A')}
        - Financial Health: {financial_intelligence.get('financial_metrics', {})}
        - IP Strength: {ip_landscape.get('ip_strength', 'N/A')}
        - Innovation Indicators: {ip_landscape.get('innovation_indicators', {})}
        
        Please provide:
        1. Strengths (internal positive factors)
        2. Weaknesses (internal negative factors)
        3. Opportunities (external positive factors)
        4. Threats (external negative factors)
        
        Format as a structured analysis with clear points for each category.
        """
        
        response = ollama_service.generate_text(prompt)
        
        # Parse the response into structured data
        swot_data = {
            'strengths': [response],  # Simplified - would parse into list
            'weaknesses': [response],
            'opportunities': [response],
            'threats': [response],
            'mined_data_integration': bool(mined_data)
        }
        
        return swot_data
        
    except Exception as e:
        if logger:
            logger.error(f"SWOT analysis generation error: {e}")
        raise

def _generate_market_plan(company: Dict[str, Any], market_research: Dict[str, Any], 
                         swot_analysis: Dict[str, Any]) -> str:
    """Generate market plan"""
    try:
        prompt = f"""
        Create a comprehensive market plan for {company['company_name']}:
        
        Company Profile:
        - Product: {company.get('product_description', 'N/A')}
        - Target Market: {company.get('target_market', 'N/A')}
        - USPs: {company.get('usps', 'N/A')}
        - Industry: {company.get('industry', 'N/A')}
        
        Market Research: {market_research}
        SWOT Analysis: {swot_analysis}
        
        Please create a professional market plan with:
        1. Executive Summary
        2. Market Analysis
        3. Competitive Landscape
        4. Target Market Definition
        5. Marketing Strategy
        6. Implementation Plan
        7. Financial Projections
        
        Format as a professional business document.
        """
        
        return ollama_service.generate_text(prompt)
        
    except Exception as e:
        if logger:
            logger.error(f"Market plan generation error: {e}")
        raise

def _generate_business_plan(company: Dict[str, Any], market_research: Dict[str, Any],
                           swot_analysis: Dict[str, Any], financial_projections: Dict[str, Any]) -> str:
    """Generate business plan"""
    try:
        prompt = f"""
        Create a comprehensive business plan for {company['company_name']}:
        
        Company Profile:
        - Product: {company.get('product_description', 'N/A')}
        - Target Market: {company.get('target_market', 'N/A')}
        - USPs: {company.get('usps', 'N/A')}
        - Business Model: {company.get('business_model', 'N/A')}
        - Revenue Model: {company.get('revenue_model', 'N/A')}
        
        Market Research: {market_research}
        SWOT Analysis: {swot_analysis}
        Financial Projections: {financial_projections}
        
        Please create a professional business plan with:
        1. Executive Summary
        2. Company Description
        3. Market Analysis
        4. Organization & Management
        5. Service Description
        6. Marketing & Sales Strategy
        7. Funding Requirements
        8. Financial Projections
        
        Format as a professional business document.
        """
        
        return ollama_service.generate_text(prompt)
        
    except Exception as e:
        if logger:
            logger.error(f"Business plan generation error: {e}")
        raise

def _generate_gtm_strategy(company: Dict[str, Any], market_research: Dict[str, Any],
                          swot_analysis: Dict[str, Any]) -> str:
    """Generate go-to-market strategy"""
    try:
        prompt = f"""
        Create a comprehensive go-to-market strategy for {company['company_name']}:
        
        Company Profile:
        - Product: {company.get('product_description', 'N/A')}
        - Target Market: {company.get('target_market', 'N/A')}
        - USPs: {company.get('usps', 'N/A')}
        - Industry: {company.get('industry', 'N/A')}
        
        Market Research: {market_research}
        SWOT Analysis: {swot_analysis}
        
        Please create a professional go-to-market strategy with:
        1. Executive Summary
        2. Market Entry Strategy
        3. Target Customer Segments
        4. Value Proposition
        5. Marketing Channels
        6. Sales Strategy
        7. Implementation Timeline
        8. Success Metrics
        
        Format as a professional business document.
        """
        
        return ollama_service.generate_text(prompt)
        
    except Exception as e:
        if logger:
            logger.error(f"GTM strategy generation error: {e}")
        raise