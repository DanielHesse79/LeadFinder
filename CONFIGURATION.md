# ⚙️ LeadFinder Configuration Guide

## Overview

LeadFinder uses a hierarchical configuration system that supports environment variables, configuration files, and database storage. This guide covers all configuration options and their usage.

## 🔧 Configuration Sources

### 1. Environment Variables (Highest Priority)
- Loaded from environment files (e.g., `env.development`)
- Override all other configuration sources
- Used for sensitive data like API keys

### 2. Configuration Database
- Stored in SQLite database
- Can be modified via web interface
- Persists across application restarts

### 3. Default Configuration
- Hardcoded defaults in `config.py`
- Used as fallback when other sources are unavailable

## 📋 Configuration Parameters

### 🔑 Required Configuration

#### SerpAPI Key
```bash
SERPAPI_KEY=your_serpapi_key_here
```
- **Description**: API key for web search functionality
- **Required**: Yes
- **Source**: Environment variable
- **Usage**: Google, Bing, DuckDuckGo search

#### Flask Secret Key
```bash
FLASK_SECRET_KEY=your_secret_key_here
```
- **Description**: Secret key for Flask session management
- **Required**: Yes
- **Source**: Environment variable
- **Usage**: Session encryption and security

### 🤖 AutoGPT Configuration

#### AutoGPT Enable/Disable
```bash
AUTOGPT_ENABLED=True
```
- **Description**: Enable or disable AutoGPT integration
- **Required**: No (default: True)
- **Values**: True/False
- **Usage**: Controls AutoGPT functionality

#### AutoGPT Model
```bash
AUTOGPT_MODEL=mistral:latest
```
- **Description**: AI model to use for AutoGPT operations
- **Required**: No (default: mistral:latest)
- **Values**: Any Ollama model name
- **Usage**: Text generation and analysis

#### AutoGPT Timeout
```bash
AUTOGPT_TIMEOUT=1800
```
- **Description**: Timeout for AutoGPT operations in seconds
- **Required**: No (default: 1800)
- **Values**: Integer (seconds)
- **Usage**: Complex research and analysis operations

### 🔧 Ollama Configuration

#### Ollama Base URL
```bash
OLLAMA_BASE_URL=http://localhost:11434
```
- **Description**: URL for Ollama server
- **Required**: No (default: http://localhost:11434)
- **Usage**: AI model communication

#### Ollama Model
```bash
OLLAMA_MODEL=mistral:latest
```
- **Description**: Default Ollama model for AI operations
- **Required**: No (default: mistral:latest)
- **Usage**: Text generation and analysis

#### Ollama Timeout
```bash
OLLAMA_TIMEOUT=180
```
- **Description**: Timeout for Ollama requests in seconds
- **Required**: No (default: 180)
- **Usage**: AI model requests

### 🌐 Flask Configuration

#### Flask Environment
```bash
FLASK_ENV=development
```
- **Description**: Flask environment mode
- **Required**: No (default: development)
- **Values**: development, production, testing
- **Usage**: Application behavior and debugging

#### Flask Debug
```bash
FLASK_DEBUG=True
```
- **Description**: Enable Flask debug mode
- **Required**: No (default: True in development)
- **Values**: True/False
- **Usage**: Development debugging and auto-reload

#### Flask Host
```bash
FLASK_HOST=0.0.0.0
```
- **Description**: Host address for Flask server
- **Required**: No (default: 0.0.0.0)
- **Usage**: Server binding

#### Flask Port
```bash
FLASK_PORT=5051
```
- **Description**: Port for Flask server
- **Required**: No (default: 5051)
- **Usage**: Server port

### 📊 Research Configuration

#### Research Max Results
```bash
RESEARCH_MAX_RESULTS=50
```
- **Description**: Maximum results per research query
- **Required**: No (default: 50)
- **Usage**: Research API limits

#### Research Timeout
```bash
RESEARCH_TIMEOUT=30
```
- **Description**: Timeout for research API calls in seconds
- **Required**: No (default: 30)
- **Usage**: Research API requests

#### Default Research Question
```bash
DEFAULT_RESEARCH_QUESTION=epigenetics and pre-diabetes
```
- **Description**: Default research question for AI analysis
- **Required**: No (default: epigenetics and pre-diabetes)
- **Usage**: AI analysis prompts

### 🔬 External API Keys (Optional)

#### Semantic Scholar API Key
```bash
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key_here
```
- **Description**: API key for Semantic Scholar
- **Required**: No
- **Usage**: Academic paper search

#### SweCRIS API Key
```bash
SWECRIS_API_KEY=your_swecris_key_here
```
- **Description**: API key for SweCRIS
- **Required**: No
- **Usage**: Swedish research funding

#### CORDIS API Key
```bash
CORDIS_API_KEY=your_cordis_key_here
```
- **Description**: API key for CORDIS
- **Required**: No
- **Usage**: EU research projects

#### NIH API Key
```bash
NIH_API_KEY=your_nih_key_here
```
- **Description**: API key for NIH RePORTER
- **Required**: No
- **Usage**: US research funding

#### NSF API Key
```bash
NSF_API_KEY=your_nsf_key_here
```
- **Description**: API key for NSF
- **Required**: No
- **Usage**: US National Science Foundation

### 📝 Logging Configuration

#### Log Level
```bash
LOG_LEVEL=DEBUG
```
- **Description**: Logging level for application
- **Required**: No (default: INFO)
- **Values**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Usage**: Application logging

## 🚀 Environment Setup

### Development Environment
```bash
# Copy development environment file
cp env.example env.development

# Edit with your configuration
nano env.development
```

### Production Environment
```bash
# Copy production environment file
cp env.example env.production

# Edit with production settings
nano env.production
```

### Environment File Structure
```bash
# Development Environment Configuration
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG

# API Keys (replace with your actual keys)
SERPAPI_KEY=your_serpapi_key_here
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_key_here
SWECRIS_API_KEY=your_swecris_key_here
CORDIS_API_KEY=your_cordis_key_here
NIH_API_KEY=your_nih_key_here
NSF_API_KEY=your_nsf_key_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:latest
OLLAMA_TIMEOUT=180

# AutoGPT Configuration
AUTOGPT_ENABLED=True
AUTOGPT_MODEL=mistral:latest
AUTOGPT_TIMEOUT=1800

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_HOST=0.0.0.0
FLASK_PORT=5051

# Research Configuration
RESEARCH_MAX_RESULTS=50
RESEARCH_TIMEOUT=30
DEFAULT_RESEARCH_QUESTION=epigenetics and pre-diabetes
```

## 🎛️ Configuration Management

### Web Interface
Access configuration management at `/config`:
- View all configuration parameters
- Update configuration values
- See configuration sources
- Validate configuration

### API Endpoints

#### Get Configuration
```http
GET /config
```

**Response:**
```json
{
  "configs": [
    {
      "key": "SERPAPI_KEY",
      "value": "***",
      "description": "SerpAPI key for Google search",
      "is_secret": true,
      "required": true,
      "source": "Environment"
    }
  ]
}
```

#### Update Configuration
```http
POST /config/update
Content-Type: application/x-www-form-urlencoded

key=SERPAPI_KEY&value=your_new_key
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

### Command Line Configuration

#### Validate Configuration
```bash
python startup_check.py
```

**Output:**
```
✅ All required configurations are present
🤖 AutoGPT integration validated successfully
✅ Configuration validation passed
```

#### Check Missing Configuration
```bash
python -c "
from config import config
missing = config.get_missing_configs()
print(f'Missing configs: {missing}')
"
```

## 🔍 Configuration Validation

### Startup Validation
The application validates configuration on startup:
1. **Required Configuration**: Checks for required parameters
2. **AutoGPT Validation**: Tests AutoGPT connection and model
3. **API Validation**: Validates external API connections
4. **Database Validation**: Checks database connectivity

### Validation Errors
Common validation errors and solutions:

#### Missing Required Configuration
```
❌ Missing required configuration: SERPAPI_KEY
```
**Solution**: Add SERPAPI_KEY to environment file

#### AutoGPT Connection Failed
```
❌ AutoGPT connection failed: Connection refused
```
**Solution**: Start Ollama server with `ollama serve`

#### Model Not Found
```
❌ AutoGPT model not found: mistral:latest
```
**Solution**: Install model with `ollama pull mistral:latest`

#### API Key Invalid
```
❌ API key validation failed: 403 Forbidden
```
**Solution**: Check API key validity and quota

## 🔒 Security Considerations

### Sensitive Configuration
- **API Keys**: Store in environment variables, never in code
- **Secret Keys**: Use strong, unique secret keys
- **Database Credentials**: Use environment variables for database access
- **Logging**: Avoid logging sensitive configuration values

### Environment Security
```bash
# Set proper file permissions
chmod 600 env.development
chmod 600 env.production

# Use secure secret generation
python -c "import secrets; print(secrets.token_hex(32))"
```

### Production Security
```bash
# Use environment variables in production
export SERPAPI_KEY="your_production_key"
export FLASK_SECRET_KEY="your_production_secret"

# Disable debug mode
export FLASK_DEBUG=False
export FLASK_ENV=production
```

## 🔧 Advanced Configuration

### Custom AutoGPT Models
```bash
# Use different models for different tasks
AUTOGPT_MODEL=llama2:latest
OLLAMA_MODEL=deepseek-coder:latest

# Custom model configuration
AUTOGPT_TIMEOUT=3600  # 1 hour for complex operations
```

### Database Configuration
```bash
# Custom database path
DATABASE_PATH=/path/to/custom/database.db

# Database connection settings
DATABASE_TIMEOUT=30
DATABASE_CHECK_SAME_THREAD=False
```

### Logging Configuration
```bash
# Custom log file
LOG_FILE=/path/to/custom/logs/leadfinder.log

# Log rotation
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

### Performance Configuration
```bash
# Request pooling
REQUEST_POOL_SIZE=10
REQUEST_TIMEOUT=30

# Caching
CACHE_ENABLED=True
CACHE_TIMEOUT=3600
```

## 🚀 Deployment Configuration

### Development Deployment
```bash
# Start with development configuration
./start_app.sh development

# Or manually
export $(cat env.development | xargs)
python app.py
```

### Production Deployment
```bash
# Start with production configuration
./start_app.sh production

# Or manually
export $(cat env.production | xargs)
export FLASK_ENV=production
export FLASK_DEBUG=False
python app.py
```

### Docker Deployment
```dockerfile
# Dockerfile with configuration
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set production environment
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False

EXPOSE 5050
CMD ["python", "app.py"]
```

## 🔍 Troubleshooting

### Configuration Issues

#### Environment File Not Loaded
```bash
# Check if environment file exists
ls -la env.development

# Check file permissions
chmod 600 env.development

# Test environment loading
source env.development
echo $SERPAPI_KEY
```

#### Configuration Not Applied
```bash
# Restart application after configuration changes
pkill -f "python app.py"
./start_app.sh development

# Check configuration via API
curl http://localhost:5051/config
```

#### AutoGPT Configuration Issues
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test AutoGPT connection
curl -X POST http://localhost:5051/autogpt/test \
  -d "test_prompt=Hello" \
  -d "model=mistral:latest"
```

### Common Configuration Errors

#### Missing API Key
```
Error: SERPAPI_KEY not found in environment
```
**Solution**: Add SERPAPI_KEY to environment file

#### Invalid Model Name
```
Error: Model 'invalid-model' not found
```
**Solution**: Use valid Ollama model name

#### Configuration Validation Failed
```
Error: Configuration validation failed
```
**Solution**: Run `python startup_check.py` for details

## 📚 Related Documentation

- [README.md](README.md) - Main project documentation
- [AUTOGPT_INTEGRATION.md](AUTOGPT_INTEGRATION.md) - AutoGPT configuration details
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Configuration API endpoints
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development configuration
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment configuration 