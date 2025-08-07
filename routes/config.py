"""
Configuration management routes

This module provides Flask routes for managing API keys and application
configuration through the web interface.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from typing import Dict, Any, Optional
from datetime import datetime

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
    """Reset configuration to defaults"""
    try:
        # Get all configs
        all_configs = config.get_all_configs()
        
        # Reset to defaults
        reset_count = 0
        for key, config_info in all_configs.items():
            if 'default' in config_info:
                config.set(key, config_info['default'], config_info.get('description', ''))
                reset_count += 1
        
        flash(f'Configuration reset successfully. {reset_count} settings restored to defaults.', 'success')
        return redirect(url_for('config.config_home'))
        
    except Exception as e:
        if logger:
            logger.error(f"Configuration reset failed: {e}")
        flash(f'Configuration reset failed: {str(e)}', 'error')
        return redirect(url_for('config.config_home'))


# REST API Endpoints
@config_bp.route('/api/config', methods=['GET'])
def get_config_api():
    """REST API endpoint for getting all configuration"""
    try:
        include_secrets = request.args.get('include_secrets', 'false').lower() == 'true'
        all_configs = config.get_all_configs(include_secrets=include_secrets)
        
        return jsonify({
            'config': all_configs,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        if logger:
            logger.error(f"API config fetch failed: {e}")
        return jsonify({'error': f'Failed to fetch configuration: {str(e)}'}), 500


@config_bp.route('/api/config/<key_name>', methods=['GET'])
def get_config_key_api(key_name: str):
    """REST API endpoint for getting a specific configuration key"""
    try:
        value = config.get(key_name)
        source = config.get_source(key_name)
        
        return jsonify({
            'key': key_name,
            'value': value,
            'source': source
        })
        
    except Exception as e:
        if logger:
            logger.error(f"API config key fetch failed: {e}")
        return jsonify({'error': f'Failed to fetch configuration key: {str(e)}'}), 500


@config_bp.route('/api/config/<key_name>', methods=['POST'])
def set_config_key_api(key_name: str):
    """REST API endpoint for setting a configuration key"""
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({'error': 'Value is required'}), 400
        
        value = data['value']
        description = data.get('description', '')
        
        success = config.set(key_name, value, description)
        
        if success:
            return jsonify({
                'success': True,
                'key': key_name,
                'value': value,
                'message': 'Configuration updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update configuration'}), 500
        
    except Exception as e:
        if logger:
            logger.error(f"API config key update failed: {e}")
        return jsonify({'error': f'Failed to update configuration: {str(e)}'}), 500


@config_bp.route('/api/config/<key_name>', methods=['DELETE'])
def delete_config_key_api(key_name: str):
    """REST API endpoint for deleting a configuration key"""
    try:
        # Check if key exists
        current_value = config.get(key_name)
        if current_value is None:
            return jsonify({'error': 'Configuration key not found'}), 404
        
        # Delete from database (set to None or empty)
        success = config.set(key_name, '', 'Deleted via API')
        
        if success:
            return jsonify({
                'success': True,
                'key': key_name,
                'message': 'Configuration key deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete configuration key'}), 500
        
    except Exception as e:
        if logger:
            logger.error(f"API config key deletion failed: {e}")
        return jsonify({'error': f'Failed to delete configuration key: {str(e)}'}), 500 