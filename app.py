"""
LeadFinder Main Application

This is the main Flask application entry point for LeadFinder.
It provides a web interface for lead discovery and management.
"""

from flask import Flask
import os
import sys

# Import configuration and utilities with error handling
try:
    from config import FLASK_SECRET_KEY, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
    from utils.logger import get_logger
except ImportError as e:
    print(f"Configuration error: {e}")
    print("Please check your config.py file")
    sys.exit(1)

# Initialize logger
logger = get_logger('app')

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.secret_key = FLASK_SECRET_KEY
    
    # Register blueprints with error handling
    try:
        from routes.leads import leads_bp
        app.register_blueprint(leads_bp)
        logger.info("Registered leads blueprint")
    except ImportError as e:
        logger.warning(f"Could not register leads blueprint: {e}")
    
    try:
        from routes.search import search_bp
        app.register_blueprint(search_bp)
        logger.info("Registered search blueprint")
    except ImportError as e:
        logger.warning(f"Could not register search blueprint: {e}")
    
    try:
        from routes.ollama import ollama_bp
        app.register_blueprint(ollama_bp)
        logger.info("Registered ollama blueprint")
    except ImportError as e:
        logger.warning(f"Could not register ollama blueprint: {e}")
    
    try:
        from routes.research import research_bp
        app.register_blueprint(research_bp)
        logger.info("Registered research blueprint")
    except ImportError as e:
        logger.warning(f"Could not register research blueprint: {e}")
    
    try:
        from routes.config import config_bp
        app.register_blueprint(config_bp)
        logger.info("Registered config blueprint")
    except ImportError as e:
        logger.warning(f"Could not register config blueprint: {e}")
    
    return app

def main():
    """Main application entry point"""
    try:
        # Create the Flask app
        app = create_app()
        
        # Initialize database if needed
        try:
            from models.database import init_db
            init_db()
            logger.info("Database initialized successfully")
        except ImportError as e:
            logger.warning(f"Could not initialize database: {e}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
        
        # Start the application
        logger.info(f"Starting LeadFinder on {FLASK_HOST}:{FLASK_PORT}")
        logger.info(f"Debug mode: {FLASK_DEBUG}")
        
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"Error starting LeadFinder: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 