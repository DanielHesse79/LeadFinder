#!/bin/bash

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default environment
ENVIRONMENT=${1:-development}

echo "🚀 Starting LeadFinder app in $ENVIRONMENT environment..."

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

# Validate configuration before starting
echo "🔍 Validating configuration..."
venv/bin/python -c "
import sys
try:
    from config import validate_startup_config
    if validate_startup_config():
        print('✅ Configuration validation passed')
        sys.exit(0)
    else:
        print('❌ Configuration validation failed')
        sys.exit(1)
except ImportError as e:
    print(f'❌ Configuration import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Configuration validation error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Configuration validation failed!"
    echo ""
    echo "Please run the migration script to check your configuration:"
    echo "   venv/bin/python migrate_config.py --validate-only"
    echo ""
    echo "Or set the required environment variables:"
    echo "   export SERPAPI_KEY='your-api-key'"
    echo "   export FLASK_SECRET_KEY='your-secret-key'"
    echo ""
    exit 1
fi

# Get configuration values for display
FLASK_HOST=$(venv/bin/python -c "from config import config; print(config.get('FLASK_HOST', '0.0.0.0'))" 2>/dev/null | tail -n 1 || echo "0.0.0.0")
FLASK_PORT=$(venv/bin/python -c "from config import config; print(config.get('FLASK_PORT', '5050'))" 2>/dev/null | tail -n 1 || echo "5050")
FLASK_DEBUG=$(venv/bin/python -c "from config import config; print(config.get('FLASK_DEBUG', 'False'))" 2>/dev/null | tail -n 1 || echo "False")
LOG_LEVEL=$(venv/bin/python -c "from config import config; print(config.get('LOG_LEVEL', 'INFO'))" 2>/dev/null | tail -n 1 || echo "INFO")

echo ""
echo "📋 Configuration Summary:"
echo "   Host: $FLASK_HOST"
echo "   Port: $FLASK_PORT"
echo "   Debug: $FLASK_DEBUG"
echo "   Log Level: $LOG_LEVEL"
echo "   Environment: $ENVIRONMENT"
echo ""

echo "🚀 Starting LeadFinder on $FLASK_HOST:$FLASK_PORT"

# Start the application using venv Python
venv/bin/python app.py 