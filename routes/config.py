"""
Configuration management routes

This module provides Flask routes for managing API keys and application
configuration through the web interface.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from typing import Dict, Any, Optional

# Import the new configuration system
try:
    from config import config, CONFIG_DEFINITIONS, ConfigurationError
except ImportError:
    config = None
    CONFIG_DEFINITIONS = {}
    ConfigurationError = Exception

try:
    from utils.logger import get_logger
    logger = get_logger('config')
except ImportError:
    logger = None

try:
    import requests
except ImportError:
    requests = None

config_bp = Blueprint('config', __name__)

@config_bp.route('/config')
def config_home():
    """Configuration management home page"""
    if not config:
        flash('Configuration service not available', 'error')
        return redirect(url_for('leads.show_leads'))
    
    try:
        # Get all configurations with their current values and metadata
        configs = config.get_all_configs(include_secrets=False)
        missing_configs = config.validate_required_configs()
        is_configured = len(missing_configs) == 0
        
        # Get default research question
        default_research_question = config.get('DEFAULT_RESEARCH_QUESTION', '')
        
        return render_template('config.html',
                             configs=configs,
                             missing_configs=missing_configs,
                             is_configured=is_configured,
                             default_research_question=default_research_question)
    except Exception as e:
        if logger:
            logger.error(f"Error loading configuration: {e}")
        flash('Error loading configuration', 'error')
        return redirect(url_for('leads.show_leads'))

@config_bp.route('/config/set_default_research_question', methods=['POST'])
def set_default_research_question():
    """Set default research question for AI analysis"""
    if not config:
        flash('Configuration service not available', 'error')
        return redirect(url_for('config.config_home'))
    
    research_question = request.form.get('default_research_question', '').strip()
    
    try:
        success = config.set('DEFAULT_RESEARCH_QUESTION', research_question, 
                           'Default research question for AI analysis', is_secret=False)
        
        if success:
            flash('Default research question updated', 'success')
        else:
            flash('Failed to update research question', 'error')
    except Exception as e:
        if logger:
            logger.error(f"Error setting research question: {e}")
        flash('Error updating research question', 'error')
    
    return redirect(url_for('config.config_home'))

@config_bp.route('/config/update', methods=['POST'])
def update_config():
    """Update a single configuration value"""
    if not config:
        flash('Configuration service not available', 'error')
        return redirect(url_for('config.config_home'))
    
    key_name = request.form.get('key_name', '').strip()
    key_value = request.form.get('key_value', '').strip()
    description = request.form.get('description', '').strip()
    
    if not key_name:
        flash('Configuration key is missing', 'error')
        return redirect(url_for('config.config_home'))
    
    try:
        # Get the configuration definition
        config_info = CONFIG_DEFINITIONS.get(key_name, {})
        is_secret = config_info.get('is_secret', False)
        
        success = config.set(key_name, key_value, description, is_secret)
        
        if success:
            flash(f'Configuration "{key_name}" updated', 'success')
        else:
            flash(f'Failed to update configuration "{key_name}"', 'error')
    except Exception as e:
        if logger:
            logger.error(f"Error updating config {key_name}: {e}")
        flash(f'Error updating configuration "{key_name}"', 'error')
    
    return redirect(url_for('config.config_home'))

@config_bp.route('/config/bulk_update', methods=['POST'])
def bulk_update_config():
    """Update multiple configuration values at once"""
    if not config:
        flash('Configuration service not available', 'error')
        return redirect(url_for('config.config_home'))
    
    try:
        updated_count = 0
        
        # Process all form fields that start with 'config_'
        for key, value in request.form.items():
            if key.startswith('config_'):
                config_key = key.replace('config_', '')
                if config_key and value is not None:
                    # Get the configuration definition
                    config_info = CONFIG_DEFINITIONS.get(config_key, {})
                    description = config_info.get('description', '')
                    is_secret = config_info.get('is_secret', False)
                    
                    success = config.set(config_key, value.strip(), description, is_secret)
                    if success:
                        updated_count += 1
        
        if updated_count > 0:
            flash(f'{updated_count} configurations updated', 'success')
        else:
            flash('No configurations were updated', 'info')
            
    except Exception as e:
        if logger:
            logger.error(f"Error in bulk config update: {e}")
        flash('Error updating configurations', 'error')
    
    return redirect(url_for('config.config_home'))

@config_bp.route('/config/delete/<key_name>', methods=['POST'])
def delete_config(key_name: str):
    """Delete a configuration key"""
    if not config:
        flash('Configuration service not available', 'error')
        return redirect(url_for('config.config_home'))
    
    try:
        # Check if this is a required configuration
        config_info = CONFIG_DEFINITIONS.get(key_name, {})
        if config_info.get('required', False):
            flash(f'Cannot delete required configuration "{key_name}"', 'error')
            return redirect(url_for('config.config_home'))
        
        success = config.set(key_name, '', 'Deleted', False)  # Clear the value
        
        if success:
            flash(f'Configuration "{key_name}" removed', 'success')
        else:
            flash(f'Failed to remove configuration "{key_name}"', 'error')
    except Exception as e:
        if logger:
            logger.error(f"Error deleting config {key_name}: {e}")
        flash(f'Error removing configuration "{key_name}"', 'error')
    
    return redirect(url_for('config.config_home'))

@config_bp.route('/config/test/<key_name>')
def test_config(key_name: str):
    """Test a configuration value"""
    if not config:
        return jsonify({'error': 'Configuration service not available'}), 500
    
    try:
        value = config.get(key_name)
        
        if not value:
            return jsonify({
                'success': False,
                'message': f'Configuration "{key_name}" is not set'
            })
        
        # Test specific configurations
        if key_name == 'SERPAPI_KEY':
            return test_serpapi_key(value)
        elif key_name == 'OLLAMA_BASE_URL':
            return test_ollama_url(value)
        else:
            return jsonify({
                'success': True,
                'message': f'Configuration "{key_name}" is set (testing not available)'
            })
            
    except Exception as e:
        if logger:
            logger.error(f"Error testing config {key_name}: {e}")
        return jsonify({'error': str(e)}), 500

def test_serpapi_key(api_key: str) -> Dict[str, Any]:
    """Test SerpAPI key"""
    if not requests:
        return {'error': 'Requests library not available'}
    
    try:
        # Simple test request to SerpAPI
        test_url = "https://serpapi.com/search"
        params = {
            'engine': 'google',
            'q': 'test',
            'api_key': api_key,
            'num': 1
        }
        
        response = requests.get(test_url, params=params, timeout=10)
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'SerpAPI key is valid'
            }
        else:
            return {
                'success': False,
                'message': f'SerpAPI test failed (status: {response.status_code})'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'SerpAPI test error: {str(e)}'
        }

def test_ollama_url(base_url: str) -> Dict[str, Any]:
    """Test Ollama base URL"""
    if not requests:
        return {'error': 'Requests library not available'}
    
    try:
        # Test Ollama API endpoint
        test_url = f"{base_url.rstrip('/')}/api/tags"
        response = requests.get(test_url, timeout=5)
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'Ollama server is responding'
            }
        else:
            return {
                'success': False,
                'message': f'Ollama not responding correctly (status: {response.status_code})'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Ollama test error: {str(e)}'
        }

@config_bp.route('/config/status')
def config_status():
    """Get configuration status as JSON"""
    if not config:
        return jsonify({
            'is_configured': False,
            'missing_configs': ['DATABASE_ERROR'],
            'total_missing': 1,
            'error': 'Configuration service not available'
        }), 500
    
    try:
        missing_configs = config.validate_required_configs()
        is_configured = len(missing_configs) == 0
        
        return jsonify({
            'is_configured': is_configured,
            'missing_configs': missing_configs,
            'total_missing': len(missing_configs)
        })
    except Exception as e:
        if logger:
            logger.error(f"Error getting config status: {e}")
        return jsonify({
            'is_configured': False,
            'missing_configs': ['ERROR'],
            'total_missing': 1,
            'error': str(e)
        }), 500

@config_bp.route('/config/export')
def export_config():
    """Export configuration as JSON"""
    if not config:
        return jsonify({'error': 'Configuration service not available'}), 500
    
    try:
        configs = config.get_all_configs(include_secrets=False)
        
        # Convert to simple key-value format
        export_data = {}
        for key, config_info in configs.items():
            export_data[key] = config_info['value']
        
        return jsonify(export_data)
    except Exception as e:
        if logger:
            logger.error(f"Error exporting config: {e}")
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config/reset', methods=['POST'])
def reset_config():
    """Reset all configuration values to defaults"""
    if not config:
        flash('Configuration service not available', 'error')
        return redirect(url_for('config.config_home'))
    
    try:
        # Clear all database configurations
        success = True
        for key in CONFIG_DEFINITIONS.keys():
            if not config.set(key, '', 'Reset to default', False):
                success = False
        
        if success:
            flash('Configuration reset to default values', 'success')
        else:
            flash('Could not reset configuration', 'error')
    except Exception as e:
        if logger:
            logger.error(f"Error resetting config: {e}")
        flash('Error resetting configuration', 'error')
    
    return redirect(url_for('config.config_home')) 