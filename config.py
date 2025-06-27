"""
LeadFinder Configuration

This module contains all configuration settings for the LeadFinder application.
Modify these settings to customize the application behavior.

Author: LeadFinder Team
Version: 2.0.0
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# API KEYS AND EXTERNAL SERVICES
# =============================================================================

# SerpAPI Key for search functionality
# Get your key from: https://serpapi.com/
# Set via environment variable: export SERPAPI_KEY="your_key_here"
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY environment variable is required. Set it with: export SERPAPI_KEY='your_key_here'")

# =============================================================================
# OLLAMA AI CONFIGURATION
# =============================================================================

# Ollama API endpoint (default: localhost:11434)
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"

# Preferred AI model (will be auto-discovered if not available)
# Common models: 'mistral:latest', 'deepseek-coder:latest', 'llama2:latest'
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')

# Timeout for AI requests in seconds
OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', '120'))

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# SQLite database file path
DB_PATH = os.getenv('DB_PATH', 'leads.db')

# =============================================================================
# SEARCH ENGINE CONFIGURATION
# =============================================================================

# Available search engines via SerpAPI
# Options: google, bing, yahoo, duckduckgo, google_news, google_scholar, etc.
SERP_ENGINES = [
    "google", "bing", "yahoo", "duckduckgo", 
    "google_news", "google_scholar", 
    "google_ai_overview", "google_immersive_product"
]

# =============================================================================
# FILE SYSTEM CONFIGURATION
# =============================================================================

# Folder for downloaded content from lead links
EXPORT_FOLDER = os.getenv('EXPORT_FOLDER', '/mnt/seagate/leads_downloads')

# Folder for PDF downloads from Sci-Hub
SCIHUB_FOLDER = os.getenv('SCIHUB_FOLDER', 'scihub_pdfs')

# =============================================================================
# FLASK WEB APPLICATION CONFIGURATION
# =============================================================================

# Host address (0.0.0.0 = accessible from network)
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')

# Port number for the web application
FLASK_PORT = int(os.getenv('FLASK_PORT', '5050'))

# Debug mode (True for development, False for production)
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Secret key for Flask sessions
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# =============================================================================
# SEARCH AND ANALYSIS CONFIGURATION
# =============================================================================

# Default research question for AI analysis
DEFAULT_RESEARCH_QUESTION = os.getenv('DEFAULT_RESEARCH_QUESTION', "epigenetik och pre-diabetes")

# Maximum text length to extract from web pages
MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '4000'))

# Timeout for HTTP requests in seconds
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '15'))

# =============================================================================
# PUBMED INTEGRATION (FUTURE FEATURE)
# =============================================================================

# PubMed API key for academic article search
# Get your key from: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
PUBMED_API_KEY = os.getenv('PUBMED_API_KEY', '')

# PubMed API base URL
PUBMED_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

# =============================================================================
# ORCID INTEGRATION (FUTURE FEATURE)
# =============================================================================

# ORCID API credentials for researcher profiles
# Register at: https://orcid.org/developer-tools
ORCID_CLIENT_ID = os.getenv('ORCID_CLIENT_ID', '')
ORCID_CLIENT_SECRET = os.getenv('ORCID_CLIENT_SECRET', '')
ORCID_BASE_URL = 'https://pub.orcid.org/v3.0/'

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Log file path (optional, logs to console if not set)
LOG_FILE = os.getenv('LOG_FILE', '')

# =============================================================================
# PERFORMANCE CONFIGURATION
# =============================================================================

# Number of workers for Gunicorn (production)
GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', '4'))

# Connection pool size for requests
REQUEST_POOL_SIZE = int(os.getenv('REQUEST_POOL_SIZE', '10'))

# =============================================================================
# DIRECTORY CREATION
# =============================================================================

# Create necessary directories if they don't exist
Path(EXPORT_FOLDER).mkdir(parents=True, exist_ok=True)
Path(SCIHUB_FOLDER).mkdir(parents=True, exist_ok=True) 