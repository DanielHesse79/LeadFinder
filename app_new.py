from flask import Flask
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from services.ollama_service import ollama_service

# Import blueprints
from routes.leads import leads_bp
from routes.search import search_bp
from routes.ollama import ollama_bp

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(leads_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(ollama_bp)
    
    # Start Ollama status check in background
    ollama_service.start_status_check()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT, host=FLASK_HOST) 