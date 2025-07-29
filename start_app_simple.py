#!/usr/bin/env python3
"""
Simple script to start LeadFinder app with improved Redis handling
"""

import os
import sys
import signal
import time
from pathlib import Path

def signal_handler(signum, frame):
    print("\n🛑 Received interrupt signal. Shutting down gracefully...")
    sys.exit(0)

def main():
    """Start the LeadFinder application with improved error handling"""
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['SKIP_AUTOGPT_VALIDATION'] = 'true'
    
    # Load environment configuration
    env_file = Path('env.development')
    if env_file.exists():
        print("📁 Loading configuration from env.development")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    print("🚀 Starting LeadFinder with improved Redis handling...")
    
    try:
        # Import and create the app
        from app import create_app
        
        print("🔧 Creating Flask application...")
        app = create_app()
        
        # Get configuration
        host = os.environ.get('FLASK_HOST', '0.0.0.0')
        port = int(os.environ.get('FLASK_PORT', '5051'))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        print(f"🌐 Starting server on {host}:{port}")
        print(f"🔧 Debug mode: {debug}")
        print(f"🌍 Environment: {os.environ.get('FLASK_ENV', 'development')}")
        print("")
        print("🎉 LeadFinder is starting up!")
        print("📊 Health check: http://localhost:5051/health")
        print("📚 API docs: http://localhost:5051/api/docs")
        print("")
        print("Press Ctrl+C to stop the application")
        print("")
        
        # Start the application
        app.run(host=host, port=port, debug=debug, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("")
        print("Troubleshooting tips:")
        print("1. Check if all dependencies are installed: pip install -r requirements.txt")
        print("2. Verify your environment configuration in env.development")
        print("3. Check if the database is accessible")
        print("4. Try running with debug mode: export FLASK_DEBUG=true")
        sys.exit(1)

if __name__ == "__main__":
    main() 