# 🤖 LeadFinder - AI-Powered Lead Discovery Platform

LeadFinder is a comprehensive lead discovery and research platform that combines web search, AI analysis, and research funding databases to help you find and analyze potential business leads.

## ✨ Features

### 🔍 **Intelligent Search**
- **Multi-engine search** (Google, Bing, DuckDuckGo)
- **AI-powered analysis** using local Mistral model via Ollama
- **Unified search interface** combining standard and research modes
- **AutoGPT integration** for comprehensive lead research

### 🤖 **AutoGPT Control Panel**
- **Real-time status monitoring** of AutoGPT functionality
- **Interactive testing** of AI models and prompts
- **Text analysis tools** for lead relevance and company research
- **Research automation** for comprehensive lead discovery
- **Model management** and configuration control

### 📊 **Lead Management**
- **Database storage** of discovered leads
- **AI analysis** of lead relevance and opportunities
- **Export capabilities** (Excel, PDF)
- **Lead workshop** for project-based analysis

### 🔬 **Research Funding**
- **Multi-API integration** (SweCRIS, CORDIS, NIH, NSF)
- **Funding opportunity discovery**
- **Research project analysis**
- **Academic collaboration identification**

### 📚 **Publication & Researcher Search**
- **PubMed integration** for scientific articles
- **ORCID integration** for researcher profiles
- **Semantic Scholar** for academic papers
- **AI-powered analysis** of research relevance

## 🚀 Quick Start

> **💡 For the fastest setup, see [QUICK_START.md](QUICK_START.md)**

### Prerequisites
- Python 3.8+
- Ollama with Mistral model
- SerpAPI key (for web search)

### Installation & Startup

**Option 1: Automated Setup (Recommended)**
```bash
# Clone the repository
git clone <repository-url>
cd leadfinder

# Configure environment (required)
cp env.example env.development
# Edit env.development with your API keys

# Start Ollama (required for AI features)
ollama serve
ollama pull mistral:latest

# Start the application (automatically handles everything else)
./start_app.sh development
```

**Option 2: Manual Setup**
```bash
# Clone the repository
git clone <repository-url>
cd leadfinder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example env.development
# Edit env.development with your API keys

# Start Ollama
ollama serve
ollama pull mistral:latest

# Run the application
./start_app.sh development
```

### Starting the Application

**Use the automated startup script (recommended):**
```bash
./start_app.sh [environment]
```

Where `[environment]` can be:
- `development` (default) - runs on port 5051 with debug mode
- `production` - runs on port 5050 with production settings
- `testing` - runs with test configuration

The script automatically:
- ✅ Creates virtual environment if missing
- ✅ Installs all dependencies
- ✅ Validates configuration
- ✅ Starts the application
- ✅ Shows access URLs

**Application URLs:**
- Main application: `http://localhost:5051` (development) or `http://localhost:5050` (production)
- Health check: `http://localhost:5051/health`
- AutoGPT status: `http://localhost:5051/autogpt/status`

## 🎯 Usage

### General Search
1. Navigate to the main page
2. Enter your search terms
3. Select search engines
4. Enable AutoGPT analysis for AI insights
5. View and save discovered leads

### AutoGPT Control Panel
1. Click "AutoGPT Control" in the navigation
2. Monitor AutoGPT status and configuration
3. Test different AI models and prompts
4. Analyze text for lead relevance
5. Perform comprehensive research

### Research Funding
1. Go to "Funding" page
2. Enter research keywords
3. Select funding databases
4. View funding opportunities and projects

### Lead Workshop
1. Select leads from your database
2. Create research projects
3. Use AutoGPT for enhanced analysis
4. Generate reports and insights

## 🔧 Configuration

### Environment Variables
```bash
# Required
SERPAPI_KEY=your_serpapi_key
FLASK_SECRET_KEY=your_secret_key

# AutoGPT Configuration
AUTOGPT_ENABLED=True
AUTOGPT_MODEL=mistral:latest
AUTOGPT_TIMEOUT=1800

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:latest
OLLAMA_TIMEOUT=180

# Research APIs (Optional)
SWECRIS_API_KEY=your_swecris_key
CORDIS_API_KEY=your_cordis_key
NIH_API_KEY=your_nih_key
NSF_API_KEY=your_nsf_key
```

### AutoGPT Models
The system supports various Ollama models:
- `mistral:latest` (recommended)
- `llama2:latest`
- `deepseek-coder:latest`
- Custom models via Ollama

## 📁 Project Structure

```
leadfinder/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── autogpt_client.py           # AutoGPT client implementation
├── leadfinder_autogpt_integration.py  # LeadFinder AutoGPT integration
├── routes/                     # Flask route handlers
│   ├── leads.py               # Lead management routes
│   ├── search.py              # Search functionality
│   ├── autogpt_control.py     # AutoGPT control panel
│   ├── research.py            # Research funding routes
│   ├── ollama.py              # Publication search routes
│   └── config.py              # Configuration management routes
├── services/                   # Business logic services
│   ├── serp_service.py        # Web search service
│   ├── ollama_service.py      # Ollama AI service
│   ├── unified_search.py      # Unified search service
│   └── research_service.py    # Research funding service
├── models/                     # Data models
├── templates/                  # HTML templates
├── static/                     # Static assets
└── data/                       # Database and logs
```

## 🤖 AutoGPT Integration

### Features
- **Local AI processing** using Ollama and Mistral
- **Comprehensive lead research** with multi-step analysis
- **Text analysis** for lead relevance and opportunities
- **Research automation** for industry and company analysis
- **Real-time monitoring** and control

### Control Panel Features
- **Status monitoring** of AutoGPT functionality
- **Model testing** with custom prompts
- **Text analysis** with different analysis types
- **Research automation** for comprehensive discovery
- **Configuration management** for models and timeouts

### Usage Examples
```python
# Test AutoGPT connection
curl -X POST http://localhost:5051/autogpt/test \
  -d "test_prompt=Hello, test" \
  -d "model=mistral:latest"

# Analyze text for lead relevance
curl -X POST http://localhost:5051/autogpt/analyze \
  -d "text=Company description..." \
  -d "analysis_type=lead_relevance"

# Perform research
curl -X POST http://localhost:5051/autogpt/research \
  -d "research_topic=AI in healthcare" \
  -d "company_name=YourCompany" \
  -d "industry=Healthcare"
```

## 🔍 Search Functionality

### Search Modes
1. **Quick Search**: Standard web search with optional AI analysis
2. **Research Mode**: Comprehensive research with AutoGPT
3. **Unified Search**: Combined approach with caching

### Search Engines
- Google (default)
- Bing
- DuckDuckGo

### AI Analysis Types
- **General Analysis**: Basic text analysis
- **Lead Relevance**: Business opportunity assessment
- **Company Research**: Detailed company analysis

## 📊 Data Management

### Lead Storage
- SQLite database for lead storage
- AI analysis results storage
- Search history tracking
- Export capabilities

### Export Formats
- Excel (.xlsx)
- PDF reports
- CSV data export
- JSON API responses

## 🔬 Research Funding

### Supported APIs
- **SweCRIS**: Swedish research funding
- **CORDIS**: EU research projects
- **NIH RePORTER**: US National Institutes of Health
- **NSF**: US National Science Foundation

### Features
- Multi-API concurrent search
- Funding opportunity filtering
- Project analysis and insights
- Academic collaboration identification

## 🛠️ Development

### Running in Development
```bash
./start_app.sh development
```

### Running Tests
```bash
python -m pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📈 Performance

### Optimization Features
- **Request pooling** for API calls
- **Caching** for search results
- **Concurrent processing** for multiple APIs
- **Configurable timeouts** for different operations

### Monitoring
- **Health check endpoint**: `/health`
- **AutoGPT status**: `/autogpt/status`
- **Application logs**: `data/logs/leadfinder.log`

## 🔒 Security

### Features
- **Environment-based configuration** for sensitive data
- **API key management** through configuration system
- **Input validation** and sanitization
- **Error handling** without exposing sensitive information

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - Get started in 3 steps
- [Configuration Guide](CONFIGURATION.md)
- [AutoGPT Integration](AUTOGPT_INTEGRATION.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Development Guide](DEVELOPMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the logs in `data/logs/`
3. Test AutoGPT functionality via the control panel
4. Create an issue with detailed information

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates. 