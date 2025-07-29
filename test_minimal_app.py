#!/usr/bin/env python3
"""
Minimal Flask app test to verify basic functionality
"""

from flask import Flask, jsonify
import os

def create_minimal_app():
    """Create a minimal Flask app for testing"""
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({"message": "LeadFinder is running!", "status": "ok"})
    
    @app.route('/health')
    def health():
        return jsonify({
            "status": "healthy",
            "message": "Minimal app test"
        })
    
    return app

if __name__ == "__main__":
    print("🚀 Starting minimal LeadFinder test...")
    
    app = create_minimal_app()
    
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5051'))
    
    print(f"🌐 Starting server on {host}:{port}")
    print("📊 Health check: http://localhost:5051/health")
    print("")
    print("Press Ctrl+C to stop")
    print("")
    
    app.run(host=host, port=port, debug=False) 