# 🤖 LeadFinder - AI-Powered Lead Discovery Platform

LeadFinder is a comprehensive lead discovery and research platform that combines web search, AI analysis, and research funding databases to help you find and analyze potential business leads. **Now featuring advanced RAG (Retrieval-Augmented Generation) capabilities for intelligent, context-aware responses.**

## ✨ Features

### 🔍 **Intelligent Search**
- **Multi-engine search** (Google, Bing, DuckDuckGo)
- **AI-powered analysis** using local Mistral model via Ollama
- **Unified search interface** combining standard and research modes
- **AutoGPT integration** for comprehensive lead research
- **Consolidated search services** with parallel execution and AI relevance scoring
- **🆕 RAG-powered search** with semantic understanding and context-aware responses

### 🧠 **RAG (Retrieval-Augmented Generation)**
- **Semantic document search** using vector embeddings and ChromaDB
- **Intelligent context retrieval** from your knowledge base
- **AI-generated responses** with source references and citations
- **Document ingestion pipeline** for leads, research papers, and search results
- **Hybrid search capabilities** combining traditional and semantic search
- **Knowledge base management** with automatic chunking and embedding
- **Real-time RAG search** via web interface and API endpoints

### 🛡️ **System Reliability**
- **Comprehensive error handling** with custom exception hierarchy
- **Thread-safe caching system** with TTL and LRU eviction
- **Database connection pooling** for improved performance
- **Real-time health monitoring** with system metrics and alerts
- **Graceful degradation** and automatic recovery mechanisms

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
- **🆕 RAG-enhanced lead analysis** with contextual insights

### 🔬 **Research Funding**
- **Multi-API integration** (SweCRIS, CORDIS, NIH, NSF)
- **Funding opportunity discovery**
- **Research project analysis**
- **Academic collaboration identification**
- **Unified funding search** with AI-powered relevance analysis

### 📚 **Publication & Researcher Search**
- **PubMed integration** for scientific articles
- **ORCID integration** for researcher profiles
- **Semantic Scholar** for academic papers
- **AI-powered analysis** of research relevance
- **Unified research search** with parallel execution and caching

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
- **🆕 RAG Search Interface**: `http://localhost:5051/rag/search`

## 🎯 Usage

### General Search
1. Navigate to the main page
2. Enter your search terms
3. Select search engines
4. Enable AutoGPT analysis for AI insights
5. View and save discovered leads

### 🆕 RAG Search
1. Navigate to **RAG Search** in the navigation or visit `/rag/search`
2. Enter your question or query
3. Adjust settings (top-k results, retrieval method)
4. Get AI-generated responses with source references
5. View context snippets and confidence scores

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

## 🧠 RAG (Retrieval-Augmented Generation)

### What is RAG?
RAG combines the power of large language models with your own knowledge base to provide accurate, contextual responses. Instead of relying solely on the model's training data, RAG retrieves relevant information from your documents and uses it to generate informed answers.

### Key Benefits
- **Accurate Responses**: Based on your actual data, not just training data
- **Source Transparency**: Every response includes references to source documents
- **Up-to-date Information**: Reflects your current knowledge base
- **Contextual Understanding**: Understands the specific context of your queries
- **Hybrid Search**: Combines semantic and traditional keyword search

### RAG Features

#### Document Ingestion
- **Automatic Processing**: Ingests leads, research papers, search results, and workshop analyses
- **Smart Chunking**: Breaks documents into optimal-sized chunks for retrieval
- **Embedding Generation**: Creates vector representations using SentenceTransformers
- **Metadata Preservation**: Maintains source information and document relationships

#### Vector Search
- **Semantic Similarity**: Finds relevant content based on meaning, not just keywords
- **ChromaDB Integration**: Fast, scalable vector database for document storage
- **Connection Pooling**: Efficient resource management for high-performance search
- **Configurable Retrieval**: Adjustable top-k results and similarity thresholds

#### AI Generation
- **Context-Aware Responses**: Uses retrieved context to generate informed answers
- **Source Citations**: Includes references to source documents
- **Confidence Scoring**: Provides confidence levels for generated responses
- **Prompt Engineering**: Optimized prompts for accurate, helpful responses

### RAG API Endpoints

#### Main RAG Search
```bash
POST /rag/search
Content-Type: application/json

{
  "query": "What are the latest AI trends in healthcare?",
  "top_k": 5,
  "retrieval_method": "hybrid"
}
```

#### Context Retrieval Only
```bash
POST /rag/retrieve
Content-Type: application/json

{
  "query": "machine learning applications",
  "top_k": 3
}
```

#### Document Ingestion
```bash
POST /rag/ingest
Content-Type: application/json

{
  "documents": [
    {
      "content": "Document content...",
      "source": "research_paper",
      "metadata": {"title": "AI in Healthcare", "author": "Dr. Smith"}
    }
  ]
}
```

#### System Status
```bash
GET /rag/status    # RAG system health
GET /rag/stats     # Usage statistics
GET /rag/health    # Detailed health check
```

### RAG Configuration

#### Environment Variables
```bash
# RAG Configuration
RAG_ENABLED=True
RAG_MODEL=mistral:latest
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_SIMILARITY_THRESHOLD=0.7
RAG_TOP_K=5

# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION=leadfinder_docs
```

#### Advanced Settings
- **Chunk Size**: Adjust document chunking for optimal retrieval
- **Similarity Threshold**: Control relevance filtering
- **Top-K Results**: Number of context snippets to retrieve
- **Retrieval Method**: Choose between vector-only, hybrid, or traditional search

### Data Migration

To populate your RAG knowledge base with existing data:

```bash
# Run the migration script
python migrate_existing_data_to_rag.py

# This will:
# - Process existing leads from the database
# - Ingest search history and workshop analyses
# - Generate embeddings and store in ChromaDB
# - Verify the migration was successful
```

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

# RAG Configuration (New)
RAG_ENABLED=True
RAG_MODEL=mistral:latest
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_SIMILARITY_THRESHOLD=0.7
RAG_TOP_K=5
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION=leadfinder_docs
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
│   ├── config.py              # Configuration management routes
│   └── rag_routes.py          # 🆕 RAG API endpoints
├── services/                   # Business logic services
│   ├── serp_service.py        # Web search service
│   ├── ollama_service.py      # Ollama AI service
│   ├── unified_search.py      # Unified search service
│   ├── research_service.py    # Research funding service
│   ├── ingestion_service.py   # 🆕 Document ingestion service
│   ├── vector_store_service.py # 🆕 Vector database management
│   ├── retrieval_service.py   # 🆕 Context retrieval service
│   ├── rag_generator.py       # 🆕 RAG response generation
│   └── embedding_service.py   # 🆕 Text embedding service
├── models/                     # Data models
│   └── database.py            # Updated with RAG tables
├── templates/                  # HTML templates
│   └── rag_search.html        # 🆕 RAG search interface
├── static/                     # Static assets
├── data/                       # Database and logs
├── test_rag_implementation.py # 🆕 RAG test suite
└── migrate_existing_data_to_rag.py # 🆕 Data migration script
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
4. **🆕 RAG Search**: Semantic search with AI-generated responses

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
- **🆕 RAG document chunks** with vector embeddings

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
# Run all tests
python -m pytest tests/

# Run RAG-specific tests
python test_rag_implementation.py
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
- **🆕 Vector search optimization** with ChromaDB
- **🆕 Embedding caching** for improved response times

### Monitoring
- **Health check endpoint**: `/health`
- **AutoGPT status**: `/autogpt/status`
- **🆕 RAG status**: `/rag/status`
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
- **🆕 [RAG Documentation](RAG_DOCUMENTATION.md)** - Complete RAG guide

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
4. **🆕 Test RAG functionality** via `/rag/status`
5. Create an issue with detailed information

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

### Recent Updates (RAG Implementation)
- **Added RAG (Retrieval-Augmented Generation) capabilities**
- **Implemented vector search with ChromaDB**
- **Created document ingestion pipeline**
- **Added semantic search with AI-generated responses**
- **Integrated RAG with existing lead management**
- **Added comprehensive RAG API endpoints**
- **Created RAG web interface**
- **Implemented data migration tools**
- **Added RAG testing suite** 