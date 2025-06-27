"""
Configuration management routes

This module provides Flask routes for managing API keys and application
configuration through the web interface.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

# Import services with error handling
try:
    from models.config import ConfigManager
except ImportError:
    ConfigManager = None

try:
    from config import DB_PATH, update_config_from_database
except ImportError:
    DB_PATH = "leads.db"
    def update_config_from_database():
        pass

try:
    from utils.logger import get_logger
except ImportError:
    def get_logger(name):
        import logging
        return logging.getLogger(name)

logger = get_logger('config_routes')

config_bp = Blueprint('config', __name__)

@config_bp.route('/config')
def config_home():
    """Display configuration management interface"""
    if not ConfigManager:
        return "Configuration service not available", 500
    
    try:
        cm = ConfigManager(DB_PATH)
        configs = cm.get_all_configs(include_secrets=True)
        missing_configs = cm.get_missing_required_configs()
        is_configured = cm.is_configured()
        
        return render_template('config.html',
                             configs=configs,
                             missing_configs=missing_configs,
                             is_configured=is_configured)
    except Exception as e:
        logger.error(f"Error in config home: {e}")
        return f"Error: {e}", 500

@config_bp.route('/config/update', methods=['POST'])
def update_config():
    """Update configuration value"""
    if not ConfigManager:
        return "Configuration service not available", 500
    
    try:
        key_name = request.form.get('key_name')
        key_value = request.form.get('key_value', '').strip()
        
        if not key_name:
            flash('Konfigurationsnyckel saknas', 'error')
            return redirect(url_for('config.config_home'))
        
        cm = ConfigManager(DB_PATH)
        success = cm.set_config(key_name, key_value)
        
        if success:
            # Update global configuration
            update_config_from_database()
            flash(f'Konfiguration "{key_name}" uppdaterad', 'success')
            logger.info(f"Updated config: {key_name}")
        else:
            flash(f'Kunde inte uppdatera "{key_name}"', 'error')
        
        return redirect(url_for('config.config_home'))
    
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        flash(f'Fel vid uppdatering: {e}', 'error')
        return redirect(url_for('config.config_home'))

@config_bp.route('/config/bulk_update', methods=['POST'])
def bulk_update_config():
    """Update multiple configuration values at once"""
    if not ConfigManager:
        return "Configuration service not available", 500
    
    try:
        cm = ConfigManager(DB_PATH)
        updated_count = 0
        
        # Get all form data
        for key, value in request.form.items():
            if key.startswith('config_'):
                config_key = key.replace('config_', '')
                if value.strip():  # Only update if value is not empty
                    success = cm.set_config(config_key, value.strip())
                    if success:
                        updated_count += 1
        
        # Update global configuration
        update_config_from_database()
        
        if updated_count > 0:
            flash(f'{updated_count} konfigurationer uppdaterade', 'success')
            logger.info(f"Bulk updated {updated_count} configs")
        else:
            flash('Inga konfigurationer uppdaterades', 'info')
        
        return redirect(url_for('config.config_home'))
    
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        flash(f'Fel vid bulk-uppdatering: {e}', 'error')
        return redirect(url_for('config.config_home'))

@config_bp.route('/config/delete/<key_name>', methods=['POST'])
def delete_config(key_name):
    """Delete configuration key"""
    if not ConfigManager:
        return "Configuration service not available", 500
    
    try:
        cm = ConfigManager(DB_PATH)
        success = cm.delete_config(key_name)
        
        if success:
            flash(f'Konfiguration "{key_name}" borttagen', 'success')
            logger.info(f"Deleted config: {key_name}")
        else:
            flash(f'Kunde inte ta bort "{key_name}"', 'error')
        
        return redirect(url_for('config.config_home'))
    
    except Exception as e:
        logger.error(f"Error deleting config {key_name}: {e}")
        flash(f'Fel vid borttagning: {e}', 'error')
        return redirect(url_for('config.config_home'))

@config_bp.route('/config/test/<key_name>')
def test_config(key_name):
    """Test a specific configuration (e.g., API key)"""
    if not ConfigManager:
        return jsonify({'error': 'Configuration service not available'}), 500
    
    try:
        cm = ConfigManager(DB_PATH)
        config_value = cm.get_config(key_name)
        
        if not config_value:
            return jsonify({
                'success': False,
                'message': f'Konfiguration "{key_name}" är inte satt'
            })
        
        # Test different types of configurations
        if key_name == 'SERPAPI_KEY':
            return test_serpapi_key(config_value)
        elif key_name == 'OLLAMA_BASE_URL':
            return test_ollama_connection(config_value)
        elif key_name.startswith('SWECRIS_') or key_name.startswith('CORDIS_') or key_name.startswith('NIH_') or key_name.startswith('NSF_'):
            return test_research_api_key(key_name, config_value)
        else:
            return jsonify({
                'success': True,
                'message': f'Konfiguration "{key_name}" är satt (testning inte tillgänglig)'
            })
    
    except Exception as e:
        logger.error(f"Error testing config {key_name}: {e}")
        return jsonify({
            'success': False,
            'message': f'Fel vid testning: {e}'
        })

def test_serpapi_key(api_key):
    """Test SerpAPI key"""
    try:
        from serpapi import GoogleSearch
        search = GoogleSearch({
            "q": "test",
            "api_key": api_key,
            "num": 1
        })
        results = search.get_dict()
        
        if "error" in results:
            return jsonify({
                'success': False,
                'message': f'SerpAPI fel: {results["error"]}'
            })
        
        return jsonify({
            'success': True,
            'message': 'SerpAPI-nyckel fungerar korrekt'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'SerpAPI test misslyckades: {e}'
        })

def test_ollama_connection(base_url):
    """Test Ollama connection"""
    try:
        import requests
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Ollama-anslutning fungerar'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Ollama svarar inte korrekt (status: {response.status_code})'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ollama-anslutning misslyckades: {e}'
        })

def test_research_api_key(key_name, api_key):
    """Test research API key"""
    # For now, just check if the key is not empty
    if api_key:
        return jsonify({
            'success': True,
            'message': f'{key_name} är satt (testning inte implementerad)'
        })
    else:
        return jsonify({
            'success': False,
            'message': f'{key_name} är inte satt'
        })

@config_bp.route('/config/status')
def config_status():
    """Get configuration status as JSON"""
    try:
        cm = ConfigManager(DB_PATH)
        missing_configs = cm.get_missing_required_configs()
        is_configured = cm.is_configured()
        
        return jsonify({
            'is_configured': is_configured,
            'missing_configs': missing_configs,
            'total_missing': len(missing_configs)
        })
    
    except Exception as e:
        logger.error(f"Error getting config status: {e}")
        return jsonify({
            'is_configured': False,
            'missing_configs': ['DATABASE_ERROR'],
            'total_missing': 1,
            'error': str(e)
        })

@config_bp.route('/config/export')
def export_config():
    """Export configuration (non-sensitive) as JSON"""
    try:
        cm = ConfigManager(DB_PATH)
        configs = cm.get_all_configs(include_secrets=False)
        
        return jsonify({
            'configs': configs,
            'exported_at': '2024-01-01T00:00:00Z'  # You could use datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error exporting config: {e}")
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config/reset', methods=['POST'])
def reset_config():
    """Reset configuration to defaults"""
    try:
        cm = ConfigManager(DB_PATH)
        
        # This would reset to default values
        # For now, just show a message
        flash('Reset-funktion kommer snart', 'info')
        
        return redirect(url_for('config.config_home'))
    
    except Exception as e:
        logger.error(f"Error resetting config: {e}")
        flash(f'Fel vid reset: {e}', 'error')
        return redirect(url_for('config.config_home')) 