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
pkill -f "venv/bin/python app.py" || true
pkill -f "app.py" || true
sleep 2

# Set Flask environment
export FLASK_ENV=$ENVIRONMENT

# Skip AutoGPT validation by default to avoid timeout issues
export SKIP_AUTOGPT_VALIDATION=true

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

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "🐍 Virtual environment not found. Creating new virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment. Please ensure python3 and venv are installed."
        exit 1
    fi
    echo "✅ Virtual environment created successfully"
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! venv/bin/python -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies from requirements.txt..."
    venv/bin/pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please check requirements.txt and your internet connection."
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Ensure fundNSF is installed in venv
echo "📦 Checking fundNSF installation..."
if ! venv/bin/python -c "import fundNSF" 2>/dev/null; then
    echo "📦 Installing fundNSF in virtual environment..."
    venv/bin/pip install fundNSF
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: Failed to install fundNSF, but continuing..."
    else
        echo "✅ fundNSF installed successfully"
    fi
else
    echo "✅ fundNSF already installed"
fi

# Check for syntax errors in critical files before validation
echo "🔍 Checking for syntax errors in critical files..."
SYNTAX_ERRORS=0

# Check database.py for syntax errors
if ! venv/bin/python -c "import models.database" 2>/dev/null; then
    echo "❌ Syntax error found in models/database.py"
    echo "   Please fix the syntax error before continuing."
    echo "   Common issues:"
    echo "   - Missing 'try:' or 'except:' blocks"
    echo "   - Incorrect indentation"
    echo "   - Unclosed parentheses or brackets"
    SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
else
    echo "✅ models/database.py syntax OK"
fi

# Check app.py for syntax errors
if ! venv/bin/python -c "import app" 2>/dev/null; then
    echo "❌ Syntax error found in app.py"
    echo "   Please fix the syntax error before continuing."
    SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
else
    echo "✅ app.py syntax OK"
fi

# Check routes for basic syntax errors (using py_compile instead of import)
echo "🔍 Checking route files for syntax errors..."
for route_file in routes/*.py; do
    if [ -f "$route_file" ]; then
        if ! venv/bin/python -m py_compile "$route_file" 2>/dev/null; then
            echo "❌ Syntax error found in $route_file"
            SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
        else
            echo "✅ $route_file syntax OK"
        fi
    fi
done

if [ $SYNTAX_ERRORS -gt 0 ]; then
    echo ""
    echo "❌ Found $SYNTAX_ERRORS syntax error(s). Please fix them before starting the app."
    echo ""
    echo "Common fixes:"
    echo "1. Check for missing 'try:' or 'except:' blocks"
    echo "2. Verify indentation is consistent (4 spaces)"
    echo "3. Ensure all parentheses and brackets are properly closed"
    echo "4. Check for missing colons after function definitions"
    echo ""
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
FLASK_PORT=$(venv/bin/python -c "from config import config; print(config.get('FLASK_PORT', '5051'))" 2>/dev/null | tail -n 1 || echo "5051")
FLASK_DEBUG=$(venv/bin/python -c "from config import config; print(config.get('FLASK_DEBUG', 'False'))" 2>/dev/null | tail -n 1 || echo "False")
LOG_LEVEL=$(venv/bin/python -c "from config import config; print(config.get('LOG_LEVEL', 'INFO'))" 2>/dev/null | tail -n 1 || echo "INFO")

echo ""
echo "📋 Configuration Summary:"
echo "   Host: $FLASK_HOST"
echo "   Port: $FLASK_PORT"
echo "   Debug: $FLASK_DEBUG"
echo "   Log Level: $LOG_LEVEL"
echo "   Environment: $ENVIRONMENT"
echo "   AutoGPT Validation: Skipped (SKIP_AUTOGPT_VALIDATION=true)"
echo ""

# Test if port is already in use
echo "🔍 Checking if port $FLASK_PORT is available..."
if command -v netstat >/dev/null 2>&1; then
    if netstat -tlnp 2>/dev/null | grep ":$FLASK_PORT " >/dev/null; then
        echo "⚠️  Warning: Port $FLASK_PORT is already in use"
        echo "   The app might not start properly if the port is occupied."
        echo "   Consider stopping other services using this port."
    else
        echo "✅ Port $FLASK_PORT is available"
    fi
elif command -v ss >/dev/null 2>&1; then
    if ss -tlnp 2>/dev/null | grep ":$FLASK_PORT " >/dev/null; then
        echo "⚠️  Warning: Port $FLASK_PORT is already in use"
        echo "   The app might not start properly if the port is occupied."
        echo "   Consider stopping other services using this port."
    else
        echo "✅ Port $FLASK_PORT is available"
    fi
else
    echo "⚠️  Could not check port availability (netstat/ss not available)"
fi

echo ""
echo "🚀 Starting LeadFinder on $FLASK_HOST:$FLASK_PORT"
echo "🌐 Access the application at: http://localhost:$FLASK_PORT"

# Start the application
venv/bin/python app.py 