"""
LeadFinder Configuration

This module handles application configuration, prioritizing database-stored
settings over environment variables for better security and flexibility.

Author: LeadFinder Team
Version: 2.0.0
"""

import os
from pathlib import Path
from typing import Dict, Any

# Try to load environment variables (fallback)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

# Database path
DB_PATH = os.getenv('DB_PATH', 'leadfinder.db')

# Initialize config manager (will be set after database is available)
config_manager = None

def get_config_manager():
    """Get or create config manager instance"""
    global config_manager
    if config_manager is None:
        from models.config import ConfigManager
        config_manager = ConfigManager(DB_PATH)
    return config_manager

def get_config_value(key: str, env_fallback: str = '', default: str = '') -> str:
    """
    Get configuration value from database, with fallback to environment variable
    
    Args:
        key: Configuration key name
        env_fallback: Environment variable name to fallback to
        default: Default value if neither database nor env has the key
        
    Returns:
        Configuration value
    """
    try:
        # Try database first
        cm = get_config_manager()
        db_value = cm.get_config(key)
        if db_value:
            return db_value
        
        # Fallback to environment variable
        if env_fallback:
            env_value = os.getenv(env_fallback)
            if env_value:
                return env_value
        
        return default
        
    except Exception:
        # If database is not available, use environment variable
        if env_fallback:
            return os.getenv(env_fallback, default)
        return default

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

# Flask configuration
FLASK_HOST = get_config_value('FLASK_HOST', 'FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(get_config_value('FLASK_PORT', 'FLASK_PORT', '5050'))
FLASK_DEBUG = get_config_value('FLASK_DEBUG', 'FLASK_DEBUG', 'False').lower() == 'true'
FLASK_SECRET_KEY = get_config_value('FLASK_SECRET_KEY', 'FLASK_SECRET_KEY', 'your-secret-key-change-this')

# Logging configuration
LOG_LEVEL = get_config_value('LOG_LEVEL', 'LOG_LEVEL', 'INFO')
LOG_FILE = get_config_value('LOG_FILE', 'LOG_FILE', 'leadfinder.log')

# =============================================================================
# API CONFIGURATION
# =============================================================================

# SerpAPI configuration
SERPAPI_KEY = get_config_value('SERPAPI_KEY', 'SERPAPI_KEY', '')

# Ollama configuration
OLLAMA_BASE_URL = get_config_value('OLLAMA_BASE_URL', 'OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_MODEL = get_config_value('OLLAMA_MODEL', 'OLLAMA_MODEL', 'mistral:latest')
OLLAMA_TIMEOUT = int(get_config_value('OLLAMA_TIMEOUT', 'OLLAMA_TIMEOUT', '30'))

# =============================================================================
# SEARCH CONFIGURATION
# =============================================================================

# Search engines
SERP_ENGINES = ["google", "bing", "yahoo", "duckduckgo"]

# Default research question
DEFAULT_RESEARCH_QUESTION = get_config_value('DEFAULT_RESEARCH_QUESTION', 'DEFAULT_RESEARCH_QUESTION', 'epigenetik och pre-diabetes')

# Text processing limits
MAX_TEXT_LENGTH = int(get_config_value('MAX_TEXT_LENGTH', 'MAX_TEXT_LENGTH', '5000'))
REQUEST_TIMEOUT = int(get_config_value('REQUEST_TIMEOUT', 'REQUEST_TIMEOUT', '30'))
REQUEST_POOL_SIZE = int(get_config_value('REQUEST_POOL_SIZE', 'REQUEST_POOL_SIZE', '10'))

# =============================================================================
# FILE PATHS AND FOLDERS
# =============================================================================

# Create necessary directories
EXPORT_FOLDER = os.getenv('EXPORT_FOLDER', 'exports')
SCIHUB_FOLDER = os.getenv('SCIHUB_FOLDER', 'scihub_downloads')

Path(EXPORT_FOLDER).mkdir(parents=True, exist_ok=True)
Path(SCIHUB_FOLDER).mkdir(parents=True, exist_ok=True)

# =============================================================================
# RESEARCH FUNDING API CONFIGURATION
# =============================================================================

# SweCRIS API (Swedish Research Information System)
SWECRIS_API_KEY = get_config_value('SWECRIS_API_KEY', 'SWECRIS_API_KEY', '')
SWECRIS_BASE_URL = get_config_value('SWECRIS_BASE_URL', 'SWECRIS_BASE_URL', 'https://api.swecris.se/v1')

# CORDIS API (EU Research Projects)
CORDIS_API_KEY = get_config_value('CORDIS_API_KEY', 'CORDIS_API_KEY', '')
CORDIS_BASE_URL = get_config_value('CORDIS_BASE_URL', 'CORDIS_BASE_URL', 'https://cordis.europa.eu/api')

# NIH RePORTER API (US Research Projects)
NIH_API_KEY = get_config_value('NIH_API_KEY', 'NIH_API_KEY', '')
NIH_BASE_URL = get_config_value('NIH_BASE_URL', 'NIH_BASE_URL', 'https://api.reporter.nih.gov/v2')

# NSF API (US National Science Foundation)
NSF_API_KEY = get_config_value('NSF_API_KEY', 'NSF_API_KEY', '')
NSF_BASE_URL = get_config_value('NSF_BASE_URL', 'NSF_BASE_URL', 'https://api.nsf.gov/v1')

# Available research funding APIs
RESEARCH_APIS = {
    'swecris': {
        'enabled': get_config_value('SWECRIS_ENABLED', 'SWECRIS_ENABLED', 'True').lower() == 'true',
        'name': 'SweCRIS',
        'description': 'Swedish Research Information System',
        'api_key': SWECRIS_API_KEY,
        'base_url': SWECRIS_BASE_URL
    },
    'cordis': {
        'enabled': get_config_value('CORDIS_ENABLED', 'CORDIS_ENABLED', 'True').lower() == 'true',
        'name': 'CORDIS',
        'description': 'EU Research Projects Database',
        'api_key': CORDIS_API_KEY,
        'base_url': CORDIS_BASE_URL
    },
    'nih': {
        'enabled': get_config_value('NIH_ENABLED', 'NIH_ENABLED', 'True').lower() == 'true',
        'name': 'NIH RePORTER',
        'description': 'US National Institutes of Health',
        'api_key': NIH_API_KEY,
        'base_url': NIH_BASE_URL
    },
    'nsf': {
        'enabled': get_config_value('NSF_ENABLED', 'NSF_ENABLED', 'True').lower() == 'true',
        'name': 'NSF',
        'description': 'US National Science Foundation',
        'api_key': NSF_API_KEY,
        'base_url': NSF_BASE_URL
    }
}

# Research search configuration
RESEARCH_MAX_RESULTS = int(get_config_value('RESEARCH_MAX_RESULTS', 'RESEARCH_MAX_RESULTS', '50'))
RESEARCH_TIMEOUT = int(get_config_value('RESEARCH_TIMEOUT', 'RESEARCH_TIMEOUT', '30'))

# =============================================================================
# ORCID CONFIGURATION
# =============================================================================

ORCID_CLIENT_ID = get_config_value('ORCID_CLIENT_ID', 'ORCID_CLIENT_ID', '')
ORCID_CLIENT_SECRET = get_config_value('ORCID_CLIENT_SECRET', 'ORCID_CLIENT_SECRET', '')
ORCID_BASE_URL = get_config_value('ORCID_BASE_URL', 'ORCID_BASE_URL', 'https://orcid.org/oauth')

# =============================================================================
# PUBMED CONFIGURATION
# =============================================================================

PUBMED_API_KEY = get_config_value('PUBMED_API_KEY', 'PUBMED_API_KEY', '')
PUBMED_BASE_URL = get_config_value('PUBMED_BASE_URL', 'PUBMED_BASE_URL', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils')

# =============================================================================
# CONFIGURATION UTILITY FUNCTIONS
# =============================================================================

def update_config_from_database():
    """Update all configuration values from database"""
    try:
        cm = get_config_manager()
        
        # Update global variables with database values
        global SERPAPI_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL, FLASK_SECRET_KEY, FLASK_DEBUG
        global SWECRIS_API_KEY, CORDIS_API_KEY, NIH_API_KEY, NSF_API_KEY
        global ORCID_CLIENT_ID, ORCID_CLIENT_SECRET, ORCID_BASE_URL
        
        SERPAPI_KEY = cm.get_config('SERPAPI_KEY', '')
        OLLAMA_BASE_URL = cm.get_config('OLLAMA_BASE_URL', 'http://localhost:11434')
        OLLAMA_MODEL = cm.get_config('OLLAMA_MODEL', 'mistral:latest')
        FLASK_SECRET_KEY = cm.get_config('FLASK_SECRET_KEY', 'your-secret-key-change-this')
        FLASK_DEBUG = cm.get_config('FLASK_DEBUG', 'False').lower() == 'true'
        
        SWECRIS_API_KEY = cm.get_config('SWECRIS_API_KEY', '')
        CORDIS_API_KEY = cm.get_config('CORDIS_API_KEY', '')
        NIH_API_KEY = cm.get_config('NIH_API_KEY', '')
        NSF_API_KEY = cm.get_config('NSF_API_KEY', '')
        
        ORCID_CLIENT_ID = cm.get_config('ORCID_CLIENT_ID', '')
        ORCID_CLIENT_SECRET = cm.get_config('ORCID_CLIENT_SECRET', '')
        ORCID_BASE_URL = cm.get_config('ORCID_BASE_URL', 'https://orcid.org/oauth')
        
        # Update OLLAMA_URL
        global OLLAMA_URL
        OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate"
        
        # Update RESEARCH_APIS
        global RESEARCH_APIS
        RESEARCH_APIS['swecris']['api_key'] = SWECRIS_API_KEY
        RESEARCH_APIS['cordis']['api_key'] = CORDIS_API_KEY
        RESEARCH_APIS['nih']['api_key'] = NIH_API_KEY
        RESEARCH_APIS['nsf']['api_key'] = NSF_API_KEY
        
    except Exception as e:
        # If database is not available, keep current values
        pass

def is_fully_configured() -> bool:
    """Check if all required configurations are set"""
    try:
        cm = get_config_manager()
        return cm.is_configured()
    except Exception:
        # If database is not available, check environment variables
        return bool(SERPAPI_KEY and OLLAMA_BASE_URL and OLLAMA_MODEL) 