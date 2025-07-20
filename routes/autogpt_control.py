"""
AutoGPT Control Panel Routes

This module provides routes for controlling and monitoring AutoGPT functionality.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from typing import Dict, Any
import logging

# Import AutoGPT integration
try:
    from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
except ImportError:
    LeadfinderAutoGPTIntegration = None

try:
    from config import config
except ImportError:
    config = None

try:
    from utils.logger import get_logger
    logger = get_logger('autogpt_control')
except ImportError:
    logger = None

autogpt_control_bp = Blueprint('autogpt_control', __name__)


@autogpt_control_bp.route('/autogpt/control')
def control_panel():
    """AutoGPT Control Panel"""
    if not LeadfinderAutoGPTIntegration:
        flash('AutoGPT integration not available', 'error')
        return redirect(url_for('leads.show_leads'))
    
    try:
        # Get current configuration
        autogpt_enabled = config.get('AUTOGPT_ENABLED', 'True').lower() == 'true' if config else True
        autogpt_model = config.get('AUTOGPT_MODEL', 'mistral:latest') if config else 'mistral:latest'
        autogpt_timeout = int(config.get('AUTOGPT_TIMEOUT', '1800')) if config else 1800
        
        # Test AutoGPT connection
        autogpt_integration = LeadfinderAutoGPTIntegration(autogpt_model)
        test_result = autogpt_integration.client.execute_text_generation("Connection test")
        autogpt_status = 'ready' if test_result.get('status') == 'COMPLETED' else 'failed'
        
        return render_template('autogpt_control.html',
                             autogpt_enabled=autogpt_enabled,
                             autogpt_model=autogpt_model,
                             autogpt_timeout=autogpt_timeout,
                             autogpt_status=autogpt_status)
                             
    except Exception as e:
        if logger:
            logger.error(f"AutoGPT control panel error: {e}")
        flash(f'AutoGPT control panel error: {str(e)}', 'error')
        return redirect(url_for('leads.show_leads'))


@autogpt_control_bp.route('/autogpt/test', methods=['POST'])
def test_autogpt():
    """Test AutoGPT functionality"""
    if not LeadfinderAutoGPTIntegration:
        return jsonify({
            'success': False,
            'error': 'AutoGPT integration not available'
        }), 500
    
    try:
        test_prompt = request.form.get('test_prompt', 'Hello, this is a test.')
        model = request.form.get('model', 'mistral:latest')
        
        if logger:
            logger.info(f"Testing AutoGPT with model {model}")
        
        autogpt_integration = LeadfinderAutoGPTIntegration(model)
        result = autogpt_integration.client.execute_text_generation(test_prompt)
        
        if result.get('status') == 'COMPLETED':
            return jsonify({
                'success': True,
                'output': result.get('output', ''),
                'model': model,
                'message': 'AutoGPT test completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'model': model
            }), 500
            
    except Exception as e:
        if logger:
            logger.error(f"AutoGPT test failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500


@autogpt_control_bp.route('/autogpt/analyze', methods=['POST'])
def analyze_with_autogpt():
    """Analyze text with AutoGPT"""
    if not LeadfinderAutoGPTIntegration:
        return jsonify({
            'success': False,
            'error': 'AutoGPT integration not available'
        }), 500
    
    try:
        text_to_analyze = request.form.get('text', '')
        analysis_type = request.form.get('analysis_type', 'general')
        model = request.form.get('model', 'mistral:latest')
        
        if not text_to_analyze:
            return jsonify({
                'success': False,
                'error': 'Text to analyze is required'
            }), 400
        
        if logger:
            logger.info(f"Analyzing text with AutoGPT: {analysis_type}")
        
        autogpt_integration = LeadfinderAutoGPTIntegration(model)
        
        # Create analysis prompt based on type
        if analysis_type == 'lead_relevance':
            prompt = f"""
            Analyze this lead for business relevance:
            
            {text_to_analyze}
            
            Please provide:
            1. Relevance score (1-10)
            2. Key insights
            3. Potential opportunities
            4. Recommended next steps
            """
        elif analysis_type == 'company_research':
            prompt = f"""
            Research and analyze this company information:
            
            {text_to_analyze}
            
            Please provide:
            1. Company overview
            2. Key decision makers
            3. Recent developments
            4. Business opportunities
            5. Contact strategies
            """
        else:
            prompt = f"""
            Analyze this text and provide insights:
            
            {text_to_analyze}
            
            Please provide a comprehensive analysis with key points and recommendations.
            """
        
        result = autogpt_integration.client.execute_text_generation(prompt)
        
        if result.get('status') == 'COMPLETED':
            return jsonify({
                'success': True,
                'analysis': result.get('output', ''),
                'analysis_type': analysis_type,
                'model': model
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Analysis failed'),
                'analysis_type': analysis_type,
                'model': model
            }), 500
            
    except Exception as e:
        if logger:
            logger.error(f"AutoGPT analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


@autogpt_control_bp.route('/autogpt/research', methods=['POST'])
def research_with_autogpt():
    """Perform research with AutoGPT"""
    if not LeadfinderAutoGPTIntegration:
        return jsonify({
            'success': False,
            'error': 'AutoGPT integration not available'
        }), 500
    
    try:
        research_topic = request.form.get('research_topic', '')
        company_name = request.form.get('company_name', '')
        industry = request.form.get('industry', '')
        model = request.form.get('model', 'mistral:latest')
        
        if not research_topic:
            return jsonify({
                'success': False,
                'error': 'Research topic is required'
            }), 400
        
        if logger:
            logger.info(f"Researching with AutoGPT: {research_topic}")
        
        autogpt_integration = LeadfinderAutoGPTIntegration(model)
        
        if company_name and industry:
            # Lead research with company and industry
            prompt = f"""
            Research potential leads for {company_name} in the {industry} industry.
            
            Please provide:
            1. Company names and descriptions
            2. Key decision makers and their roles
            3. Contact information (emails, phone numbers, LinkedIn profiles)
            4. Company size and revenue estimates
            5. Recent news or developments
            6. Potential pain points or opportunities
            7. Why they would benefit from {company_name}'s services
            8. Best approach strategy for contacting them
            
            Format as a comprehensive list of leads with actionable information.
            """
            result = autogpt_integration.client.execute_text_generation(prompt)
        else:
            # General research
            prompt = f"""
            Conduct comprehensive research on: {research_topic}
            
            Please provide:
            1. Overview and background
            2. Key players and companies
            3. Recent developments and trends
            4. Opportunities and challenges
            5. Recommendations and next steps
            
            Make this research actionable and detailed.
            """
            result = autogpt_integration.client.execute_text_generation(prompt)
        
        if result.get('status') == 'COMPLETED':
            return jsonify({
                'success': True,
                'research': result.get('output', ''),
                'topic': research_topic,
                'model': model
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Research failed'),
                'topic': research_topic,
                'model': model
            }), 500
            
    except Exception as e:
        if logger:
            logger.error(f"AutoGPT research failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Research failed: {str(e)}'
        }), 500


@autogpt_control_bp.route('/autogpt/status')
def autogpt_status():
    """Get AutoGPT status"""
    try:
        autogpt_enabled = config.get('AUTOGPT_ENABLED', 'True').lower() == 'true' if config else True
        autogpt_model = config.get('AUTOGPT_MODEL', 'mistral:latest') if config else 'mistral:latest'
        
        if not autogpt_enabled:
            return jsonify({
                'enabled': False,
                'status': 'disabled',
                'model': autogpt_model
            })
        
        if not LeadfinderAutoGPTIntegration:
            return jsonify({
                'enabled': True,
                'status': 'not_available',
                'model': autogpt_model
            })
        
        # Test connection
        autogpt_integration = LeadfinderAutoGPTIntegration(autogpt_model)
        test_result = autogpt_integration.client.execute_text_generation("Status check")
        
        return jsonify({
            'enabled': True,
            'status': 'ready' if test_result.get('status') == 'COMPLETED' else 'failed',
            'model': autogpt_model,
            'last_test': test_result.get('output', '')[:100] + '...' if test_result.get('output') else ''
        })
        
    except Exception as e:
        if logger:
            logger.error(f"AutoGPT status check failed: {e}")
        return jsonify({
            'enabled': True,
            'status': 'error',
            'error': str(e)
        }), 500 