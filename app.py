"""
LeadFinder Main Application

This is the main Flask application entry point for LeadFinder.
It provides a web interface for lead discovery and management.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
from pathlib import Path

# Import the new configuration system
try:
    from config import config, validate_startup_config, ConfigurationError
except ImportError as e:
    print(f"❌ Configuration import failed: {e}")
    sys.exit(1)

# Import routes with error handling
try:
    from routes.leads import leads_bp
except ImportError:
    leads_bp = None

try:
    from routes.search import search_bp
except ImportError:
    search_bp = None

try:
    from routes.ollama import ollama_bp
except ImportError:
    ollama_bp = None

try:
    from routes.research import research_bp
except ImportError:
    research_bp = None

try:
    from routes.config import config_bp
except ImportError:
    config_bp = None

try:
    from routes.lead_workshop import lead_workshop_bp
except ImportError:
    lead_workshop_bp = None

try:
    from routes.unified_search import unified_search_bp
except ImportError:
    unified_search_bp = None

try:
    from routes.autogpt_control import autogpt_control_bp
except ImportError:
    autogpt_control_bp = None

try:
    from utils.logger import get_logger
    logger = get_logger('app')
except ImportError:
    logger = None

def create_app():
    """Create and configure the Flask application"""
    
    # Validate configuration before starting
    try:
        if not validate_startup_config():
            print("❌ Configuration validation failed. Please check your environment variables and database configuration.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        sys.exit(1)
    
    app = Flask(__name__)
    
    # Configure Flask
    app.config['SECRET_KEY'] = config.get('FLASK_SECRET_KEY', required=True)
    app.config['DEBUG'] = config.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialize database
    try:
        from models.database import db
        # Test database connection
        db.get_lead_count()
        if logger:
            logger.info("Database initialized successfully")
    except Exception as e:
        if logger:
            logger.error(f"Database initialization failed: {e}")
        print(f"⚠️  Database initialization failed: {e}")
    
    # Initialize AutoGPT integration
    try:
        from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
        autogpt_integration = LeadfinderAutoGPTIntegration("mistral:latest")
        # Test AutoGPT connection
        test_result = autogpt_integration.client.execute_text_generation("Test connection")
        if test_result.get('status') == 'COMPLETED':
            if logger:
                logger.info("AutoGPT integration initialized successfully")
            print("✅ AutoGPT integration ready")
        else:
            if logger:
                logger.warning("AutoGPT integration test failed")
            print("⚠️  AutoGPT integration test failed")
    except Exception as e:
        if logger:
            logger.warning(f"AutoGPT integration not available: {e}")
        print(f"⚠️  AutoGPT integration not available: {e}")
    
    # Register blueprints
    if leads_bp:
        app.register_blueprint(leads_bp)
        if logger:
            logger.info("Leads blueprint registered")
    
    if search_bp:
        app.register_blueprint(search_bp)
        if logger:
            logger.info("Search blueprint registered")
    
    if ollama_bp:
        app.register_blueprint(ollama_bp)
        if logger:
            logger.info("Ollama blueprint registered")
    
    if research_bp:
        app.register_blueprint(research_bp)
        if logger:
            logger.info("Research blueprint registered")
    
    if config_bp:
        app.register_blueprint(config_bp)
        if logger:
            logger.info("Config blueprint registered")
    
    if lead_workshop_bp:
        app.register_blueprint(lead_workshop_bp)
        if logger:
            logger.info("Lead Workshop blueprint registered")
    
    if unified_search_bp:
        app.register_blueprint(unified_search_bp)
        if logger:
            logger.info("Unified Search blueprint registered")
    
    if autogpt_control_bp:
        app.register_blueprint(autogpt_control_bp)
        if logger:
            logger.info("AutoGPT Control blueprint registered")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    @app.errorhandler(ConfigurationError)
    def configuration_error(error):
        flash(f'Configuration error: {error}', 'error')
        return redirect(url_for('config.config_home'))
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Check database connection
            from models.database import db
            db.get_lead_count()
            
            # Check configuration
            missing_configs = config.validate_required_configs()
            
            # Check AutoGPT integration
            autogpt_status = 'unavailable'
            try:
                from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
                autogpt_integration = LeadfinderAutoGPTIntegration("mistral:latest")
                test_result = autogpt_integration.client.execute_text_generation("Health check")
                autogpt_status = 'ready' if test_result.get('status') == 'COMPLETED' else 'failed'
            except Exception as e:
                autogpt_status = f'unavailable: {str(e)}'
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'configuration': 'valid' if not missing_configs else 'missing_required',
                'autogpt': autogpt_status,
                'missing_configs': missing_configs
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500
    
    if logger:
        logger.info("Flask application created successfully")
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    host = config.get('FLASK_HOST', '0.0.0.0')
    port = int(config.get('FLASK_PORT', '5050'))
    debug = config.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting LeadFinder on {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    # Check AutoGPT status at startup
    try:
        from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
        autogpt_integration = LeadfinderAutoGPTIntegration("mistral:latest")
        test_result = autogpt_integration.client.execute_text_generation("Startup test")
        if test_result.get('status') == 'COMPLETED':
            print("🤖 AutoGPT: Ready (Mistral + Ollama)")
        else:
            print("⚠️  AutoGPT: Test failed")
    except Exception as e:
        print(f"⚠️  AutoGPT: Not available ({str(e)[:50]}...)")
    
    app.run(host=host, port=port, debug=debug) 