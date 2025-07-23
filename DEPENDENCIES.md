# LeadFinder Dependencies Documentation

This document provides a comprehensive overview of all dependencies used in the LeadFinder project, their purposes, and installation instructions.

## Overview

LeadFinder is a comprehensive lead discovery and management web application that integrates multiple research APIs, AI services, and provides sophisticated lead analysis capabilities. The project uses a modular architecture with clear separation of concerns.

## Core Dependencies

### Web Framework
- **Flask>=2.3.0**: Main web framework for the application
  - Provides routing, template rendering, and request handling
  - Used in `app.py` and all route modules
- **Werkzeug>=2.3.0**: WSGI utility library for Flask
  - Provides utilities like `secure_filename` for file uploads
  - Used in `routes/lead_workshop.py`

### HTTP and API Libraries
- **requests>=2.31.0**: HTTP library for making API calls
  - Used extensively across all service modules for external API integration
  - Primary HTTP client for SweCRIS, CORDIS, NIH, NSF, PubMed, and other APIs
- **urllib3>=2.0.0**: HTTP client library (dependency of requests)
  - Provides connection pooling and retry logic
  - Used in `utils/performance.py` for optimized sessions

### Data Processing and Analysis
- **pandas>=2.0.0**: Data manipulation and analysis library
  - Used in `routes/leads.py` for Excel export functionality
  - Handles data processing for lead exports
- **openpyxl>=3.1.0**: Excel file reading and writing
  - Used in `routes/leads.py` for Excel export with formatting
  - Provides advanced Excel features like styling and formulas

### PDF Generation
- **reportlab>=4.0.0**: PDF generation library
  - Used in `services/pdf_service.py` for generating project reports
  - Creates professional PDF reports with tables, styling, and links

### Data Serialization
- **dataclasses-json>=0.6.0**: JSON serialization for dataclasses
  - Used for API response handling and data serialization
  - Provides type-safe JSON conversion for dataclass objects

### Web Scraping and HTML Parsing
- **beautifulsoup4>=4.12.0**: HTML/XML parsing library
  - Used in `services/ollama_service.py` for web content extraction
  - Parses HTML content from web pages for analysis
- **lxml>=4.9.0**: XML and HTML processing library
  - Fast XML/HTML parser backend for BeautifulSoup
  - Provides better performance than the default parser

## Testing Dependencies

### Testing Framework
- **pytest>=7.0.0**: Testing framework
  - Used for unit and integration tests
  - Provides test discovery, fixtures, and assertions
- **pytest-cov>=4.0.0**: Coverage reporting for pytest
  - Generates code coverage reports
  - Helps ensure comprehensive testing

## Development Dependencies

### Code Quality
- **black>=23.0.0**: Code formatter
  - Automatically formats Python code to PEP 8 standards
  - Ensures consistent code style across the project
- **flake8>=6.0.0**: Linter for Python code
  - Checks for style guide enforcement and programming errors
  - Identifies potential issues and style violations
- **mypy>=1.0.0**: Static type checker
  - Performs static type checking on Python code
  - Helps catch type-related errors before runtime

## Optional Dependencies

### AutoGPT Integration
- **autogpt-client>=0.1.0**: AutoGPT client library (commented out)
  - Used for AI-powered text generation and analysis
  - Currently implemented as custom client in `autogpt_client.py`

### NSF API Integration
- **fundNSF>=0.1.0**: NSF funding API wrapper (commented out)
  - Alternative to direct NSF API integration
  - Currently using direct requests implementation in `services/nsf_api.py`

## Built-in Python Modules

The following modules are part of Python's standard library and don't require separate installation:

### Core Python Modules
- **sqlite3**: Database operations (used in `models/database.py`)
- **threading**: Multi-threading support (used in `services/ollama_service.py`)
- **tempfile**: Temporary file handling (used in `routes/lead_workshop.py`)
- **pathlib**: Path manipulation (used throughout the codebase)
- **typing**: Type hints (used extensively for type safety)
- **dataclasses**: Data classes (used in `services/api_base.py`)
- **datetime**: Date and time handling (used in multiple service modules)
- **json**: JSON processing (used for API responses)
- **re**: Regular expressions (used for text processing)
- **os**: Operating system interface (used for file operations)
- **sys**: System-specific parameters (used for configuration)
- **logging**: Logging framework (used in `utils/logger.py`)
- **abc**: Abstract base classes (used in `services/api_base.py`)
- **concurrent.futures**: Concurrent execution (used in `services/research_service.py`)
- **urllib.parse**: URL parsing (used in `services/scihub_service.py`)

## Installation Instructions

### Prerequisites
1. Python 3.8 or higher
2. pip (Python package installer)
3. Virtual environment (recommended)

### Setup Steps

1. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install optional dependencies** (if needed):
   ```bash
   # For AutoGPT integration
   pip install autogpt-client
   
   # For NSF API integration
   pip install fundNSF
   ```

4. **Verify installation**:
   ```bash
   python -c "import flask, requests, pandas, reportlab; print('All core dependencies installed successfully')"
   ```

## Dependency Management

### Version Pinning
- All dependencies use `>=` version constraints to allow compatible updates
- This ensures security updates while maintaining compatibility
- Specific versions can be pinned by removing `>=` if needed

### Security Considerations
- Regular updates recommended for security patches
- Use `pip list --outdated` to check for updates
- Consider using `pip-audit` for security vulnerability scanning

### Performance Impact
- **Heavy dependencies**: pandas, openpyxl, reportlab (large file sizes)
- **Light dependencies**: requests, beautifulsoup4, dataclasses-json
- **Minimal impact**: Flask, Werkzeug, urllib3

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Version conflicts**: Use `pip check` to identify conflicts
3. **Missing system libraries**: Some dependencies may require system packages
4. **Memory issues**: Large dependencies like pandas may require more RAM

### Dependency Conflicts
- If conflicts occur, try installing dependencies one by one
- Use `pip-tools` for dependency resolution
- Consider using `conda` for complex scientific computing dependencies

## Size Estimates

- **Core application**: ~5-10MB
- **Virtual environment**: ~300MB (includes all dependencies)
- **Heaviest dependencies**: pandas (~50MB), openpyxl (~30MB), reportlab (~25MB)

## Maintenance

### Regular Tasks
1. Update dependencies monthly for security patches
2. Review and remove unused dependencies
3. Monitor for breaking changes in major version updates
4. Test application after dependency updates

### Dependency Audit
- Use `pip-audit` for security scanning
- Review `pip list` output regularly
- Consider using `safety` for additional security checks

## Future Considerations

### Potential Additions
- **Redis**: For caching and session storage
- **Celery**: For background task processing
- **SQLAlchemy**: For more advanced database operations
- **FastAPI**: For API-only endpoints (if separating API from web interface)

### Optimization Opportunities
- Replace pandas with lighter alternatives for simple data operations
- Use async libraries for better performance with multiple API calls
- Consider containerization for consistent deployment environments 