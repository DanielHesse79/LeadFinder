import os
from pathlib import Path

# API Keys
SERPAPI_KEY = '3ec483ba975854440e360e49e098a19cb204d80455f39963fe1e2680799d970a'

# Ollama Configuration
OLLAMA_URL = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'mistral'
OLLAMA_TIMEOUT = 120

# Database Configuration
DB_PATH = 'leads.db'

# SERP API Engines
SERP_ENGINES = [
    "google", "bing", "yahoo", "duckduckgo", 
    "google_news", "google_scholar", 
    "google_ai_overview", "google_immersive_product"
]

# File Paths
EXPORT_FOLDER = '/mnt/seagate/leads_downloads'
SCIHUB_FOLDER = 'scihub_pdfs'

# Flask Configuration
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5050
FLASK_DEBUG = True

# Search Configuration
DEFAULT_RESEARCH_QUESTION = "epigenetik och pre-diabetes"
MAX_TEXT_LENGTH = 4000
REQUEST_TIMEOUT = 15

# PubMed Configuration (för framtida användning)
PUBMED_API_KEY = os.getenv('PUBMED_API_KEY', '')
PUBMED_BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

# ORCID Configuration (för framtida användning)
ORCID_CLIENT_ID = os.getenv('ORCID_CLIENT_ID', '')
ORCID_CLIENT_SECRET = os.getenv('ORCID_CLIENT_SECRET', '')
ORCID_BASE_URL = 'https://pub.orcid.org/v3.0/'

# Create necessary directories
Path(EXPORT_FOLDER).mkdir(parents=True, exist_ok=True)
Path(SCIHUB_FOLDER).mkdir(parents=True, exist_ok=True) 