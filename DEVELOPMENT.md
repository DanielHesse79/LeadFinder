# 🛠️ LeadFinder Development Guide

## Overview

This guide provides comprehensive information for developers working on LeadFinder, including setup, architecture, coding standards, and contribution guidelines.

## 🚀 Development Setup

### Prerequisites
- Python 3.8+
- Git
- Ollama with Mistral model
- SerpAPI key (for testing)

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd leadfinder
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment**
```bash
cp env.example env.development
# Edit env.development with your configuration
```

5. **Start Ollama**
```bash
ollama serve
ollama pull mistral:latest
```

6. **Run the application**
```bash
./start_app.sh development
```

### Development Environment Variables
```bash
# Required for development
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG

# API Keys (use test keys for development)
SERPAPI_KEY=your_test_serpapi_key
FLASK_SECRET_KEY=dev-secret-key-change-in-production

# AutoGPT Configuration
AUTOGPT_ENABLED=True
AUTOGPT_MODEL=mistral:latest
AUTOGPT_TIMEOUT=1800

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:latest
OLLAMA_TIMEOUT=180
```

## 🏗️ Architecture Overview

### Project Structure
```
leadfinder/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── autogpt_client.py           # AutoGPT client implementation
├── leadfinder_autogpt_integration.py  # LeadFinder AutoGPT integration
├── routes/                     # Flask route handlers
│   ├── __init__.py
│   ├── leads.py               # Lead management routes
│   ├── search.py              # Search functionality
│   ├── autogpt_control.py     # AutoGPT control panel
│   ├── research.py            # Research funding routes
│   ├── ollama.py              # Publication search routes
│   ├── config.py              # Configuration management routes
│   └── lead_workshop.py       # Lead workshop routes
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── serp_service.py        # Web search service
│   ├── ollama_service.py      # Ollama AI service
│   ├── unified_search.py      # Unified search service
│   ├── research_service.py    # Research funding service
│   ├── pubmed_service.py      # PubMed integration
│   ├── orcid_service.py       # ORCID integration
│   └── semantic_scholar_service.py  # Semantic Scholar integration
├── models/                     # Data models
│   ├── __init__.py
│   ├── database.py            # Database models and operations
│   └── config_model.py        # Configuration model
├── templates/                  # HTML templates
│   ├── leads.html             # Main search interface
│   ├── autogpt_control.html   # AutoGPT control panel
│   ├── research.html          # Research funding interface
│   ├── ollama.html            # Publication search interface
│   ├── config.html            # Configuration management
│   └── lead_workshop.html     # Lead workshop interface
├── static/                     # Static assets
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── logger.py              # Logging configuration
│   └── performance.py         # Performance utilities
├── tests/                      # Test files
├── data/                       # Database and logs
└── exports/                    # Export files
```

### Key Components

#### 1. Flask Application (`app.py`)
- Main application entry point
- Blueprint registration
- Configuration validation
- AutoGPT integration initialization
- Error handlers

#### 2. Configuration System (`config.py`)
- Hierarchical configuration management
- Environment variable support
- Database configuration storage
- Validation and error handling

#### 3. AutoGPT Integration
- `autogpt_client.py`: Local AutoGPT client using Ollama
- `leadfinder_autogpt_integration.py`: LeadFinder-specific integration
- `routes/autogpt_control.py`: Control panel routes
- `templates/autogpt_control.html`: Control panel interface

#### 4. Search Services
- `services/serp_service.py`: Web search via SerpAPI
- `services/unified_search.py`: Combined search functionality
- `services/ollama_service.py`: AI analysis via Ollama

#### 5. Research Services
- `services/research_service.py`: Research funding APIs
- `services/pubmed_service.py`: PubMed integration
- `services/orcid_service.py`: ORCID integration

## 🔧 Development Workflow

### 1. Feature Development

#### Adding New Features
1. **Create feature branch**
```bash
git checkout -b feature/new-feature-name
```

2. **Implement feature**
   - Add routes in appropriate blueprint
   - Create/update services as needed
   - Add templates for UI components
   - Update configuration if needed

3. **Add tests**
```bash
# Create test file
touch tests/test_new_feature.py

# Run tests
python -m pytest tests/test_new_feature.py -v
```

4. **Update documentation**
   - Update relevant documentation files
   - Add API documentation if needed
   - Update changelog

5. **Submit pull request**
```bash
git add .
git commit -m "feat: add new feature description"
git push origin feature/new-feature-name
```

#### AutoGPT Feature Development
When adding AutoGPT-related features:

1. **Extend AutoGPT client** (`autogpt_client.py`)
```python
def new_autogpt_function(self, parameters):
    """New AutoGPT functionality"""
    try:
        # Implementation
        return {
            "status": "COMPLETED",
            "output": "result",
            "metadata": {}
        }
    except Exception as e:
        return {
            "status": "FAILED",
            "error": str(e)
        }
```

2. **Add integration method** (`leadfinder_autogpt_integration.py`)
```python
def new_integration_method(self, parameters):
    """Integration method for new feature"""
    return self.client.new_autogpt_function(parameters)
```

3. **Create route** (`routes/autogpt_control.py`)
```python
@autogpt_control_bp.route('/autogpt/new-feature', methods=['POST'])
def new_feature():
    """New AutoGPT feature endpoint"""
    # Implementation
    pass
```

4. **Update control panel** (`templates/autogpt_control.html`)
```html
<!-- Add UI elements for new feature -->
<div class="form-group">
    <label for="newFeature">New Feature:</label>
    <input type="text" class="form-control" id="newFeature">
</div>
```

### 2. Testing

#### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_autogpt.py

# Run with coverage
python -m pytest --cov=.

# Run with verbose output
python -m pytest -v
```

#### Test Structure
```python
# tests/test_autogpt.py
import pytest
from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration

class TestAutoGPT:
    def test_autogpt_connection(self):
        """Test AutoGPT connection"""
        integration = LeadfinderAutoGPTIntegration("mistral:latest")
        result = integration.client.execute_text_generation("Test")
        assert result.get('status') == 'COMPLETED'

    def test_autogpt_analysis(self):
        """Test AutoGPT text analysis"""
        # Test implementation
        pass
```

### 3. Code Quality

#### Code Formatting
```bash
# Format code with black
black .

# Check formatting
black --check .
```

#### Linting
```bash
# Run flake8
flake8 .

# Run with specific rules
flake8 --max-line-length=88 --ignore=E203,W503
```

#### Type Checking
```bash
# Run mypy
mypy .

# Run with specific files
mypy routes/ services/
```

### 4. Database Development

#### Database Models
```python
# models/database.py
class Lead:
    def __init__(self, id, title, description, link, ai_summary, source, created_at):
        self.id = id
        self.title = title
        self.description = description
        self.link = link
        self.ai_summary = ai_summary
        self.source = source
        self.created_at = created_at

    @staticmethod
    def create_table(cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                link TEXT NOT NULL,
                ai_summary TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
```

#### Database Operations
```python
def save_lead(self, title, description, link, ai_summary, source):
    """Save lead to database"""
    try:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO leads (title, description, link, ai_summary, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, link, ai_summary, source))
        self.conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to save lead: {e}")
        return False
```

### 5. Service Development

#### Service Structure
```python
# services/new_service.py
import logging
from typing import List, Dict, Any

try:
    from utils.logger import get_logger
    logger = get_logger('new_service')
except ImportError:
    logger = None

class NewService:
    def __init__(self, config):
        self.config = config
        self.logger = logger

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with error handling"""
        try:
            # Implementation
            result = self._process(data)
            if self.logger:
                self.logger.info(f"Processed data successfully")
            return result
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to process data: {e}")
            return {"error": str(e)}

    def _process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal processing method"""
        # Implementation
        pass
```

## 🎛️ AutoGPT Development

### AutoGPT Client Development

#### Adding New AutoGPT Functions
```python
# autogpt_client.py
def execute_new_function(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute new AutoGPT function"""
    try:
        prompt = self._build_prompt(parameters)
        result = self._generate_text(prompt)
        return {
            "status": "COMPLETED",
            "output": result,
            "function": "new_function",
            "parameters": parameters
        }
    except Exception as e:
        return {
            "status": "FAILED",
            "error": str(e),
            "function": "new_function"
        }

def _build_prompt(self, parameters: Dict[str, Any]) -> str:
    """Build prompt for new function"""
    return f"""
    Task: {parameters.get('task', '')}
    
    Parameters:
    {parameters}
    
    Instructions:
    {parameters.get('instructions', '')}
    """
```

#### Testing AutoGPT Functions
```python
# tests/test_autogpt_client.py
def test_new_function():
    """Test new AutoGPT function"""
    config = AutoGPTConfig(model="mistral:latest")
    client = LocalAutoGPTClient(config)
    
    result = client.execute_new_function({
        "task": "Test task",
        "instructions": "Test instructions"
    })
    
    assert result.get('status') == 'COMPLETED'
    assert 'output' in result
```

### Control Panel Development

#### Adding New Control Panel Features
```python
# routes/autogpt_control.py
@autogpt_control_bp.route('/autogpt/new-feature', methods=['POST'])
def new_feature():
    """New AutoGPT feature endpoint"""
    if not LeadfinderAutoGPTIntegration:
        return jsonify({
            'success': False,
            'error': 'AutoGPT integration not available'
        }), 500
    
    try:
        # Get parameters
        param1 = request.form.get('param1', '')
        param2 = request.form.get('param2', '')
        
        # Validate parameters
        if not param1:
            return jsonify({
                'success': False,
                'error': 'Parameter 1 is required'
            }), 400
        
        # Execute AutoGPT function
        autogpt_integration = LeadfinderAutoGPTIntegration("mistral:latest")
        result = autogpt_integration.new_integration_method({
            "param1": param1,
            "param2": param2
        })
        
        if result.get('status') == 'COMPLETED':
            return jsonify({
                'success': True,
                'result': result.get('output', ''),
                'metadata': result.get('metadata', {})
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        if logger:
            logger.error(f"New feature failed: {e}")
        return jsonify({
            'success': False,
            'error': f'Feature failed: {str(e)}'
        }), 500
```

## 🔍 Debugging

### Application Logs
```bash
# View application logs
tail -f data/logs/leadfinder.log

# View specific log levels
grep "ERROR" data/logs/leadfinder.log
```

### AutoGPT Debugging
```python
# Enable AutoGPT debugging
import logging
logging.getLogger('autogpt').setLevel(logging.DEBUG)

# Test AutoGPT connection
from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
integration = LeadfinderAutoGPTIntegration("mistral:latest")
result = integration.client.execute_text_generation("Debug test")
print(f"AutoGPT result: {result}")
```

### Database Debugging
```python
# Test database connection
from models.database import db
count = db.get_lead_count()
print(f"Lead count: {count}")

# Check database schema
import sqlite3
conn = sqlite3.connect('data/leadfinder.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables: {tables}")
```

### API Debugging
```bash
# Test health endpoint
curl http://localhost:5050/health

# Test AutoGPT status
curl http://localhost:5050/autogpt/status

# Test AutoGPT functionality
curl -X POST http://localhost:5050/autogpt/test \
  -d "test_prompt=Hello, test" \
  -d "model=mistral:latest"
```

## 📊 Performance Optimization

### Database Optimization
```python
# Use indexes for frequently queried columns
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_leads_source 
    ON leads(source)
''')

cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_leads_created_at 
    ON leads(created_at)
''')
```

### AutoGPT Optimization
```python
# Use appropriate timeouts
config = AutoGPTConfig(
    model="mistral:latest",
    timeout=1800  # 30 minutes for complex operations
)

# Cache results for repeated queries
cache_key = f"analysis_{hash(text)}"
cached_result = cache.get(cache_key)
if cached_result:
    return cached_result
```

### API Optimization
```python
# Use connection pooling
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

## 🚀 Deployment

### Development Deployment
```bash
# Start development server
./start_app.sh development

# Check application status
curl http://localhost:5050/health
```

### Production Deployment
```bash
# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Start production server
./start_app.sh production
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5050

CMD ["python", "app.py"]
```

## 🤝 Contributing

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Add docstrings for all functions and classes
- Write comprehensive tests for new features
- Update documentation for any changes

### Commit Messages
Use conventional commit format:
```
feat: add new AutoGPT feature
fix: resolve search timeout issue
docs: update API documentation
test: add tests for new functionality
refactor: improve error handling
```

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request with detailed description

### Review Process
- All code must be reviewed before merging
- Tests must pass
- Documentation must be updated
- Code quality checks must pass

## 📚 Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [SerpAPI Documentation](https://serpapi.com/docs)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)
- [Pytest Testing Framework](https://docs.pytest.org/)

### Best Practices
- [Python Best Practices](https://docs.python-guide.org/)
- [Flask Best Practices](https://flask.palletsprojects.com/en/2.3.x/patterns/)
- [API Design Best Practices](https://restfulapi.net/)
- [Testing Best Practices](https://realpython.com/python-testing/)

## 🆘 Support

For development issues:
1. Check the documentation
2. Review the logs
3. Test individual components
4. Create an issue with detailed information
5. Join the development discussion

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 