# 📝 Changelog

All notable changes to the LeadFinder project will be documented in this file.

## [Unreleased] - 2025-07-28

### 🐛 Fixed
- **PubMed Search Integration**: Fixed missing PubMed search results in the main search interface
  - Updated `collect_leads` function in `routes/search.py` to properly process PubMed results
  - Added PubMed search results to the leads list with proper formatting
  - Removed redundant PubMed search calls from `perform_search` function
  - Confirmed PubMed checkbox is present and functional in search form

- **Template Routing Issues**: Resolved multiple `BuildError` exceptions in templates
  - Fixed `config.index` to `config.config_home` in navigation templates
  - Updated `leads.view_lead` and `leads.edit_lead` to use JavaScript functions
  - Fixed `leads.export_leads` to `leads.export_to_excel`
  - Corrected RAG endpoints: `rag.search` to `rag.rag_search`
  - Fixed `ollama.ollama_home` to `ollama.ollama_models`
  - Updated `webscraper.webscraper` to `webscraper.webscraper_home`
  - Fixed report generation endpoints in `templates/reports_home.html`
  - Corrected lead workshop project links
  - Updated export links in project templates
  - Fixed AutoGPT search form action

- **Template Rendering Errors**: Resolved Jinja2 template errors
  - Fixed `lead.score` display to handle missing scores (`lead.score or 0`)
  - Updated `lead.created_at` display to handle string dates (`lead.created_at[:10]`)
  - Added JavaScript functions for lead actions instead of direct URL links

- **Non-existent Blueprint References**: Commented out references to non-existent blueprints
  - Removed `agents` and `interactions` blueprint references from templates
  - Added placeholder text for disabled functionality

### 🔧 Technical Improvements
- **Error Handling**: Enhanced error handling for missing dependencies
- **CSRF Protection**: Maintained CSRF token requirements for POST requests
- **Database Integration**: Confirmed PubMed service initialization and configuration
- **Lead Management**: Verified `save_lead` function can handle PubMed results

### 📚 Documentation
- **Updated README.md**: Added PubMed to search engines list
- **Enhanced Project Structure**: Updated file organization in documentation
- **Fixed Recent Updates**: Added PubMed search fixes and template routing resolutions

## [1.2.0] - 2025-07-27

### ✨ Added
- **RAG (Retrieval-Augmented Generation) System**
  - Complete RAG implementation with ChromaDB vector database
  - Document ingestion pipeline for leads, research papers, and search results
  - Semantic search with AI-generated responses
  - Vector embedding generation using SentenceTransformers
  - RAG API endpoints (`/rag/search`, `/rag/retrieve`, `/rag/ingest`)
  - RAG web interface with real-time search capabilities
  - Data migration tools for existing lead data
  - Comprehensive RAG testing suite

- **Enhanced Search Capabilities**
  - PubMed integration for scientific article search
  - Improved search form with RAG options
  - Hybrid search combining traditional and semantic search
  - Progress tracking for search operations

- **System Reliability Improvements**
  - Database connection pooling for improved performance
  - Thread-safe caching system with TTL and LRU eviction
  - Comprehensive error handling with custom exception hierarchy
  - Real-time health monitoring with system metrics

### 🔧 Changed
- **Architecture**: Migrated from simple script to modular Flask application
- **Configuration**: Centralized configuration management with environment variables
- **Database**: Enhanced SQLite schema with RAG-specific tables
- **Error Handling**: Implemented structured error handling throughout the application

### 🐛 Fixed
- **Security Issues**: Removed exposed API keys from environment files
- **Performance Issues**: Implemented connection pooling and caching
- **Template Issues**: Fixed multiple routing and rendering errors
- **Dependency Issues**: Resolved missing package installations

## [1.1.0] - 2025-07-20

### ✨ Added
- **AutoGPT Integration**
  - Local AI processing using Ollama and Mistral
  - Comprehensive lead research with multi-step analysis
  - Text analysis for lead relevance and opportunities
  - Research automation for industry and company analysis
  - Real-time monitoring and control panel

- **Enhanced Search Functionality**
  - Multi-engine search (Google, Bing, DuckDuckGo)
  - AI-powered analysis using local Mistral model
  - Unified search interface combining standard and research modes
  - Consolidated search services with parallel execution

- **Lead Management System**
  - Database storage of discovered leads
  - AI analysis of lead relevance and opportunities
  - Export capabilities (Excel, PDF)
  - Lead workshop for project-based analysis

- **Research Funding Integration**
  - Multi-API integration (SweCRIS, CORDIS, NIH, NSF)
  - Funding opportunity discovery
  - Research project analysis
  - Academic collaboration identification

### 🔧 Changed
- **Project Structure**: Reorganized from single script to modular Flask application
- **Configuration**: Implemented environment-based configuration system
- **Database**: Enhanced SQLite schema with additional tables
- **Error Handling**: Added comprehensive error handling and logging

### 🐛 Fixed
- **API Integration**: Resolved issues with external API services
- **Performance**: Optimized database operations and request handling
- **Security**: Implemented proper API key management
- **Template Issues**: Fixed routing and rendering problems

## [1.0.0] - 2025-07-15

### ✨ Added
- **Initial Release**
  - Basic web search functionality
  - Lead discovery and storage
  - Simple AI analysis using Ollama
  - Export capabilities
  - Web interface with Bootstrap styling

### 🔧 Features
- **Search**: Google, Bing, DuckDuckGo integration
- **AI**: Basic text analysis with Mistral model
- **Database**: SQLite storage for leads and search history
- **Export**: Excel and PDF export functionality
- **Web Interface**: Responsive design with modern UI

## 🔄 Migration Guide

### Upgrading from 1.1.0 to 1.2.0

1. **Install New Dependencies**
   ```bash
   pip install chromadb sentence-transformers numpy
   ```

2. **Update Environment Variables**
   ```bash
   # Add RAG configuration
   RAG_ENABLED=True
   RAG_MODEL=mistral:latest
   RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
   RAG_CHUNK_SIZE=1000
   RAG_CHUNK_OVERLAP=200
   RAG_SIMILARITY_THRESHOLD=0.7
   RAG_TOP_K=5
   ```

3. **Migrate Existing Data**
   ```bash
   python migrate_existing_data_to_rag.py
   ```

4. **Test RAG Functionality**
   ```bash
   python test_rag_implementation.py
   ```

### Upgrading from 1.0.0 to 1.1.0

1. **Install AutoGPT Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AutoGPT**
   ```bash
   # Add to your environment file
   AUTOGPT_ENABLED=True
   AUTOGPT_MODEL=mistral:latest
   AUTOGPT_TIMEOUT=1800
   ```

3. **Test AutoGPT Integration**
   ```bash
   curl http://localhost:5051/autogpt/status
   ```

## 🐛 Known Issues

### Current Issues
- **ChromaDB Initialization**: ChromaDB may not be initialized on first run
  - **Workaround**: Create `data/vector_db` directory manually
  - **Status**: Will be fixed in next release

- **CSRF Token Requirements**: Direct API calls require CSRF tokens
  - **Workaround**: Use web interface or include CSRF tokens in requests
  - **Status**: Expected behavior for security

### Resolved Issues
- ✅ **PubMed Search**: Fixed missing PubMed results in search interface
- ✅ **Template Routing**: Resolved all `BuildError` exceptions
- ✅ **API Key Exposure**: Removed exposed API keys from environment files
- ✅ **Performance Issues**: Implemented connection pooling and caching
- ✅ **Error Handling**: Added comprehensive error handling system

## 📚 Documentation

- [README.md](README.md) - Main project documentation
- [AUTOGPT_INTEGRATION.md](AUTOGPT_INTEGRATION.md) - AutoGPT integration guide
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [RAG_DOCUMENTATION.md](RAG_DOCUMENTATION.md) - RAG system guide

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the logs in `data/logs/`
3. Test AutoGPT functionality via the control panel
4. Test RAG functionality via `/rag/status`
5. Create an issue with detailed information 