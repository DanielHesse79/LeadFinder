#!/bin/bash

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default environment
ENVIRONMENT=${1:-development}

echo "🔄 Restarting LeadFinder app in $ENVIRONMENT environment..."

# Stop any existing app instances
echo "🛑 Stopping any existing app instances..."
pkill -f "python app.py" || true
sleep 2

# Set Flask environment
export FLASK_ENV=$ENVIRONMENT

# Load environment-specific configuration safely
if [ -f "env.$ENVIRONMENT" ]; then
    echo "📁 Loading configuration from env.$ENVIRONMENT"
    # Use source to properly handle quoted values and spaces
    set -a  # automatically export all variables
    source "env.$ENVIRONMENT"
    set +a  # turn off automatic export
else
    echo "⚠️  Warning: env.$ENVIRONMENT not found, using defaults"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
    
    # Ensure fundNSF is installed in venv
    echo "📦 Checking fundNSF installation..."
    if ! venv/bin/python -c "import fundNSF" 2>/dev/null; then
        echo "📦 Installing fundNSF in virtual environment..."
        venv/bin/pip install fundNSF
    else
        echo "✅ fundNSF already installed"
    fi
else
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Get configuration values for display
FLASK_HOST=$(venv/bin/python -c "from config import config; print(config.get('FLASK_HOST', '0.0.0.0'))" 2>/dev/null | tail -n 1 || echo "0.0.0.0")
FLASK_PORT=$(venv/bin/python -c "from config import config; print(config.get('FLASK_PORT', '5051'))" 2>/dev/null | tail -n 1 || echo "5051")
FLASK_DEBUG=$(venv/bin/python -c "from config import config; print(config.get('FLASK_DEBUG', 'False'))" 2>/dev/null | tail -n 1 || echo "False")
LOG_LEVEL=$(venv/bin/python -c "from config import config; print(config.get('LOG_LEVEL', 'INFO'))" 2>/dev/null | tail -n 1 || echo "INFO")

echo "🚀 Starting LeadFinder on $FLASK_HOST:$FLASK_PORT"
echo "🔧 Debug mode: $FLASK_DEBUG"
echo "📝 Log level: $LOG_LEVEL"

# Start the application using venv Python
venv/bin/python app.py 