"""
Configuration management for LeadFinder.
"""
import os
import sys
from pathlib import Path
from typing import Any, Optional, Dict, List

# Import database configuration with error handling
try:
    from models.config import ConfigManager
except ImportError:
    ConfigManager = None

# Base directory setup
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class ConfigurationError(Exception):
    """Raised when required configuration is missing"""
    pass

class ConfigurationManager:
    """Single source of truth for all configuration with clear precedence:
    1. Environment variable (highest priority)
    2. Database value (fallback)
    3. Default value (lowest priority)
    """
    
    def __init__(self):
        self._db_config = ConfigManager() if ConfigManager else None
        self._cache = {}
        self._load_environment_config()
    
    def _load_environment_config(self):
        """Load environment-specific configuration file"""
        environment = os.getenv('FLASK_ENV', 'development').lower()
        env_file = BASE_DIR / f'env.{environment}'
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Only set if not already in environment
                        if not os.getenv(key):
                            os.environ[key] = value
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get configuration value with clear precedence:
        1. Environment variable (highest priority)
        2. Database value (fallback)
        3. Default value (lowest priority)
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]
        
        # 1. Environment variable (highest priority)
        env_value = os.getenv(key)
        if env_value is not None:
            self._cache[key] = env_value
            return env_value
        
        # 2. Database value (fallback)
        if self._db_config:
            db_value = self._db_config.get_config(key)
            if db_value is not None and db_value != '':
                self._cache[key] = db_value
                return db_value
        
        # 3. Default value (lowest priority)
        if default is not None:
            self._cache[key] = default
            return default
        
        # 4. Required configuration missing
        if required:
            raise ConfigurationError(f"Required configuration '{key}' is missing")
        
        return None
    
    def set(self, key: str, value: Any, description: str = "", is_secret: bool = False) -> bool:
        """Set configuration value in database (for UI management)"""
        if self._db_config:
            return self._db_config.set_config(key, value, description, is_secret)
        return False
    
    def get_source(self, key: str) -> str:
        """Determine where a configuration value comes from"""
        if os.getenv(key) is not None:
            return 'Environment'
        elif self._db_config and self._db_config.get_config(key):
            return 'Database'
        else:
            return 'Default'
    
    def validate_required_configs(self) -> List[str]:
        """Validate all required configurations are present"""
        missing = []
        for config_key, config_info in CONFIG_DEFINITIONS.items():
            if config_info.get('required', False):
                if not self.get(config_key):
                    missing.append(config_key)
        return missing
    
    def get_all_configs(self, include_secrets: bool = False) -> Dict[str, Dict[str, Any]]:
        """Get all configurations with their current values and metadata"""
        configs = {}
        for key, config_info in CONFIG_DEFINITIONS.items():
            value = self.get(key, config_info.get('default'))
            if not include_secrets and config_info.get('is_secret', False):
                value = '*' * len(str(value)) if value else ''
            
            configs[key] = {
                'value': value,
                'description': config_info['description'],
                'is_secret': config_info.get('is_secret', False),
                'source': self.get_source(key),
                'required': config_info.get('required', False),
                'has_value': bool(value)
            }
        return configs

# Configuration definitions - single source of truth
CONFIG_DEFINITIONS = {
    'SERPAPI_KEY': {
        'description': 'SerpAPI key for Google search',
        'is_secret': True,
        'required': True
    },
    'OLLAMA_BASE_URL': {
        'description': 'Ollama server base URL',
        'is_secret': False,
        'required': True,
        'default': 'http://localhost:11434'
    },
    'OLLAMA_MODEL': {
        'description': 'Default Ollama model',
        'is_secret': False,
        'required': False,
        'default': 'mistral:latest'
    },
    'OLLAMA_TIMEOUT': {
        'description': 'Ollama API timeout in seconds',
        'is_secret': False,
        'required': False,
        'default': '1800'
    },
    'DEFAULT_RESEARCH_QUESTION': {
        'description': 'Default research question for AI analysis',
        'is_secret': False,
        'required': False,
        'default': 'epigenetics and pre-diabetes'
    },
    'SWECRIS_API_KEY': {
        'description': 'SweCRIS API key',
        'is_secret': True,
        'required': False
    },
    'CORDIS_API_KEY': {
        'description': 'CORDIS API key',
        'is_secret': True,
        'required': False
    },
    'NIH_API_KEY': {
        'description': 'NIH RePORTER API key',
        'is_secret': True,
        'required': False
    },
    'NSF_API_KEY': {
        'description': 'NSF API key',
        'is_secret': True,
        'required': False
    },
    'ORCID_CLIENT_ID': {
        'description': 'ORCID client ID',
        'is_secret': True,
        'required': False
    },
    'ORCID_CLIENT_SECRET': {
        'description': 'ORCID client secret',
        'is_secret': True,
        'required': False
    },
    'ORCID_BASE_URL': {
        'description': 'ORCID API base URL',
        'is_secret': False,
        'required': False,
        'default': 'https://pub.orcid.org/v3.0'
    },
    'PUBMED_API_KEY': {
        'description': 'PubMed API key',
        'is_secret': True,
        'required': False
    },
    'PUBMED_BASE_URL': {
        'description': 'PubMed API base URL',
        'is_secret': False,
        'required': False,
        'default': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'
    },
    'SEMANTIC_SCHOLAR_API_KEY': {
        'description': 'Semantic Scholar API key',
        'is_secret': True,
        'required': False
    },
    'FLASK_SECRET_KEY': {
        'description': 'Flask secret key for sessions',
        'is_secret': True,
        'required': True
    },
    'FLASK_DEBUG': {
        'description': 'Flask debug mode',
        'is_secret': False,
        'required': False,
        'default': 'False'
    },
    'FLASK_HOST': {
        'description': 'Flask host address',
        'is_secret': False,
        'required': False,
        'default': '0.0.0.0'
    },
    'FLASK_PORT': {
        'description': 'Flask port number',
        'is_secret': False,
        'required': False,
        'default': '5051'
    },
    'RESEARCH_MAX_RESULTS': {
        'description': 'Maximum results per research API',
        'is_secret': False,
        'required': False,
        'default': '50'
    },
    'RESEARCH_TIMEOUT': {
        'description': 'Research API timeout in seconds',
        'is_secret': False,
        'required': False,
        'default': '30'
    },
    'LOG_LEVEL': {
        'description': 'Logging level (DEBUG, INFO, WARNING, ERROR)',
        'is_secret': False,
        'required': False,
        'default': 'INFO'
    },
    'LOG_FILE': {
        'description': 'Log file path',
        'is_secret': False,
        'required': False,
        'default': 'leadfinder.log'
    },
    'REQUEST_POOL_SIZE': {
        'description': 'HTTP request connection pool size',
        'is_secret': False,
        'required': False,
        'default': '10'
    },
    'REQUEST_TIMEOUT': {
        'description': 'HTTP request timeout in seconds',
        'is_secret': False,
        'required': False,
        'default': '10'
    },
    'MAX_TEXT_LENGTH': {
        'description': 'Maximum text length for AI processing',
        'is_secret': False,
        'required': False,
        'default': '1000'
    },
    'EXPORT_FOLDER': {
        'description': 'Export folder path',
        'is_secret': False,
        'required': False,
        'default': 'exports'
    },
    'SCIHUB_FOLDER': {
        'description': 'Sci-Hub PDF download folder',
        'is_secret': False,
        'required': False,
        'default': 'scihub_pdfs'
    },
    'AUTOGPT_ENABLED': {
        'description': 'Enable AutoGPT integration',
        'is_secret': False,
        'required': False,
        'default': 'True'
    },
    'AUTOGPT_MODEL': {
        'description': 'AutoGPT model to use (should match Ollama model)',
        'is_secret': False,
        'required': False,
        'default': 'mistral:latest'
    },
    'RUNPOD_API_KEY': {
        'description': 'RunPod.ai API key for enhanced AI analysis',
        'is_secret': True,
        'required': False
    },
    'RUNPOD_ENDPOINT_ID': {
        'description': 'RunPod.ai endpoint ID for AI analysis',
        'is_secret': False,
        'required': False
    },
    'RUNPOD_BASE_URL': {
        'description': 'RunPod.ai API base URL',
        'is_secret': False,
        'required': False,
        'default': 'https://api.runpod.ai/v2'
    },
    'RUNPOD_TIMEOUT': {
        'description': 'RunPod.ai API timeout in seconds',
        'is_secret': False,
        'required': False,
        'default': '300'
    },
    'RUNPOD_MAX_RETRIES': {
        'description': 'RunPod.ai maximum retry attempts',
        'is_secret': False,
        'required': False,
        'default': '3'
    },
    'RUNPOD_RETRY_DELAY': {
        'description': 'RunPod.ai retry delay in seconds',
        'is_secret': False,
        'required': False,
        'default': '2'
    },
    'RUNPOD_ENABLED': {
        'description': 'Enable RunPod.ai integration for enhanced AI analysis',
        'is_secret': False,
        'required': False,
        'default': 'False'
    },
    'RUNPOD_AUTO_ENABLE': {
        'description': 'Automatically enable RunPod for batch processing (>5 leads)',
        'is_secret': False,
        'required': False,
        'default': 'True'
    },
    'RUNPOD_BATCH_THRESHOLD': {
        'description': 'Number of leads that triggers automatic RunPod usage',
        'is_secret': False,
        'required': False,
        'default': '5'
    },
    'RUNPOD_COMPLEX_ANALYSIS': {
        'description': 'Use RunPod for complex analysis (detailed insights)',
        'is_secret': False,
        'required': False,
        'default': 'True'
    },
    'RUNPOD_FALLBACK_TO_OLLAMA': {
        'description': 'Fallback to Ollama if RunPod fails',
        'is_secret': False,
        'required': False,
        'default': 'True'
    },
    'AUTOGPT_TIMEOUT': {
        'description': 'AutoGPT request timeout in seconds',
        'is_secret': False,
        'required': False,
        'default': '30'
    },
    # RAG Configuration
    'RAG_ENABLED': {
        'description': 'Enable RAG (Retrieval-Augmented Generation) functionality',
        'is_secret': False,
        'required': False,
        'default': 'True'
    },
    'RAG_MODEL': {
        'description': 'RAG model for text generation',
        'is_secret': False,
        'required': False,
        'default': 'mistral:latest'
    },
    'RAG_EMBEDDING_MODEL': {
        'description': 'Embedding model for RAG vector search',
        'is_secret': False,
        'required': False,
        'default': 'all-MiniLM-L6-v2'
    },
    'RAG_CHUNK_SIZE': {
        'description': 'Size of document chunks in characters',
        'is_secret': False,
        'required': False,
        'default': '1000'
    },
    'RAG_CHUNK_OVERLAP': {
        'description': 'Overlap between chunks',
        'is_secret': False,
        'required': False,
        'default': '200'
    },
    'RAG_SIMILARITY_THRESHOLD': {
        'description': 'Minimum similarity score for retrieval',
        'is_secret': False,
        'required': False,
        'default': '0.7'
    },
    'RAG_TOP_K': {
        'description': 'Number of chunks to retrieve',
        'is_secret': False,
        'required': False,
        'default': '5'
    },
    'RAG_MAX_CONTEXT_LENGTH': {
        'description': 'Maximum context length for generation',
        'is_secret': False,
        'required': False,
        'default': '4000'
    },
    'RAG_CACHE_TTL': {
        'description': 'Cache TTL for RAG responses in seconds',
        'is_secret': False,
        'required': False,
        'default': '3600'
    },
    'RAG_DEBUG': {
        'description': 'Enable RAG debug mode',
        'is_secret': False,
        'required': False,
        'default': 'False'
    }
}

# Global configuration instance
config = ConfigurationManager()

def validate_startup_config():
    """Validate critical configurations on startup"""
    missing_configs = config.validate_required_configs()
    
    if missing_configs:
        print("❌ CRITICAL: Missing required configurations:")
        for missing in missing_configs:
            print(f"   - {missing}")
        print("\nPlease set these environment variables or configure them in the database.")
        return False
    
    print("✅ All required configurations are present")
    
    # Validate AutoGPT integration if enabled and not skipped
    import os
    skip_autogpt = os.getenv('SKIP_AUTOGPT_VALIDATION') == 'true'
    
    if skip_autogpt:
        print("🤖 AutoGPT validation skipped (SKIP_AUTOGPT_VALIDATION=true)")
    else:
        autogpt_enabled = config.get('AUTOGPT_ENABLED', 'True').lower() == 'true'
        if autogpt_enabled:
            try:
                from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
                autogpt_model = config.get('AUTOGPT_MODEL', 'mistral:latest')
                autogpt_integration = LeadfinderAutoGPTIntegration(autogpt_model)
                
                # Test AutoGPT connection - DISABLED for startup stability
                # test_result = autogpt_integration.client.execute_text_generation("Startup validation")
                # if test_result.get('status') == 'COMPLETED':
                #     print("🤖 AutoGPT integration validated successfully")
                # else:
                #     print("⚠️  AutoGPT integration test failed")
                print("🤖 AutoGPT integration available (validation skipped for startup stability)")
            except Exception as e:
                print(f"⚠️  AutoGPT integration not available: {str(e)[:50]}...")
    
    return True

# Load all configuration values using the new system
SERPAPI_KEY = config.get('SERPAPI_KEY', required=True)
OLLAMA_BASE_URL = config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = config.get('OLLAMA_MODEL', 'mistral:latest')
OLLAMA_TIMEOUT = int(config.get('OLLAMA_TIMEOUT', '1800'))
DEFAULT_RESEARCH_QUESTION = config.get('DEFAULT_RESEARCH_QUESTION', 'epigenetics and pre-diabetes')

# AutoGPT Configuration
AUTOGPT_ENABLED = config.get('AUTOGPT_ENABLED', 'True').lower() == 'true'
AUTOGPT_MODEL = config.get('AUTOGPT_MODEL', 'mistral:latest')
AUTOGPT_TIMEOUT = int(config.get('AUTOGPT_TIMEOUT', '30'))

# RunPod Configuration
RUNPOD_API_KEY = config.get('RUNPOD_API_KEY', '')
RUNPOD_ENDPOINT_ID = config.get('RUNPOD_ENDPOINT_ID', '')
RUNPOD_BASE_URL = config.get('RUNPOD_BASE_URL', 'https://api.runpod.ai/v2')
RUNPOD_TIMEOUT = int(config.get('RUNPOD_TIMEOUT', '300'))
RUNPOD_MAX_RETRIES = int(config.get('RUNPOD_MAX_RETRIES', '3'))
RUNPOD_RETRY_DELAY = int(config.get('RUNPOD_RETRY_DELAY', '2'))
RUNPOD_ENABLED = config.get('RUNPOD_ENABLED', 'False').lower() == 'true'
RUNPOD_AUTO_ENABLE = config.get('RUNPOD_AUTO_ENABLE', 'True').lower() == 'true'
RUNPOD_BATCH_THRESHOLD = int(config.get('RUNPOD_BATCH_THRESHOLD', '5'))
RUNPOD_COMPLEX_ANALYSIS = config.get('RUNPOD_COMPLEX_ANALYSIS', 'True').lower() == 'true'
RUNPOD_FALLBACK_TO_OLLAMA = config.get('RUNPOD_FALLBACK_TO_OLLAMA', 'True').lower() == 'true'

# Research API Keys - Now using database-based management
try:
    from models.api_keys import get_api_key
    SERPAPI_KEY = get_api_key('serpapi') or config.get('SERPAPI_KEY', '')
    SWECRIS_API_KEY = get_api_key('swecris') or config.get('SWECRIS_API_KEY', '')
    CORDIS_API_KEY = get_api_key('cordis') or config.get('CORDIS_API_KEY', '')
    NIH_API_KEY = get_api_key('nih') or config.get('NIH_API_KEY', '')
    NSF_API_KEY = get_api_key('nsf') or config.get('NSF_API_KEY', '')
    SEMANTIC_SCHOLAR_API_KEY = get_api_key('semantic_scholar') or config.get('SEMANTIC_SCHOLAR_API_KEY', '')
except ImportError:
    # Fallback to environment variables if API key management is not available
    SERPAPI_KEY = config.get('SERPAPI_KEY', '')
    SWECRIS_API_KEY = config.get('SWECRIS_API_KEY', '')
    CORDIS_API_KEY = config.get('CORDIS_API_KEY', '')
    NIH_API_KEY = config.get('NIH_API_KEY', '')
    NSF_API_KEY = config.get('NSF_API_KEY', '')
    SEMANTIC_SCHOLAR_API_KEY = config.get('SEMANTIC_SCHOLAR_API_KEY', '')

# External APIs
ORCID_BASE_URL = config.get('ORCID_BASE_URL', 'https://pub.orcid.org/v3.0')
PUBMED_BASE_URL = config.get('PUBMED_BASE_URL', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils')

# Flask Configuration
FLASK_SECRET_KEY = config.get('FLASK_SECRET_KEY', required=True)
FLASK_DEBUG = config.get('FLASK_DEBUG', 'False').lower() == 'true'
FLASK_HOST = config.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(config.get('FLASK_PORT', '5051'))

# Research Configuration
RESEARCH_MAX_RESULTS = int(config.get('RESEARCH_MAX_RESULTS', '50'))
RESEARCH_TIMEOUT = int(config.get('RESEARCH_TIMEOUT', '30'))

# Logging
LOG_LEVEL = config.get('LOG_LEVEL', 'INFO')
LOG_FILE = config.get('LOG_FILE', 'leadfinder.log')

# Performance
REQUEST_POOL_SIZE = int(config.get('REQUEST_POOL_SIZE', '10'))
REQUEST_TIMEOUT = int(config.get('REQUEST_TIMEOUT', '10'))
MAX_TEXT_LENGTH = int(config.get('MAX_TEXT_LENGTH', '1000'))

# Database Connection Pool Configuration
try:
    DB_POOL_MAX_CONNECTIONS = int(config.get('DB_POOL_MAX_CONNECTIONS', '10'))
except (TypeError, ValueError):
    DB_POOL_MAX_CONNECTIONS = 10

try:
    DB_POOL_CONNECTION_TIMEOUT = int(config.get('DB_POOL_CONNECTION_TIMEOUT', '30'))
except (TypeError, ValueError):
    DB_POOL_CONNECTION_TIMEOUT = 30

try:
    DB_POOL_HEALTH_CHECK_INTERVAL = int(config.get('DB_POOL_HEALTH_CHECK_INTERVAL', '300'))
except (TypeError, ValueError):
    DB_POOL_HEALTH_CHECK_INTERVAL = 300

# RAG Configuration
RAG_ENABLED = config.get('RAG_ENABLED', 'True').lower() == 'true'
RAG_PERSIST_DIRECTORY = config.get('RAG_PERSIST_DIRECTORY', 'data/chroma')
RAG_COLLECTION_NAME = config.get('RAG_COLLECTION_NAME', 'leadfinder_docs')
RAG_EMBEDDING_MODEL = config.get('RAG_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
RAG_CHUNK_SIZE = int(config.get('RAG_CHUNK_SIZE', '1000'))
RAG_CHUNK_OVERLAP = int(config.get('RAG_CHUNK_OVERLAP', '200'))
RAG_TOP_K = int(config.get('RAG_TOP_K', '5'))

# Redis Configuration
REDIS_HOST = config.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(config.get('REDIS_PORT', '6379'))
REDIS_DB = int(config.get('REDIS_DB', '0'))
REDIS_PASSWORD = config.get('REDIS_PASSWORD', '')
REDIS_MAX_CONNECTIONS = int(config.get('REDIS_MAX_CONNECTIONS', '10'))

# ChromaDB Configuration
CHROMADB_HOST = config.get('CHROMADB_HOST', 'localhost')
CHROMADB_PORT = int(config.get('CHROMADB_PORT', '8000'))
CHROMADB_PERSIST_DIRECTORY = config.get('CHROMADB_PERSIST_DIRECTORY', 'data/chroma')

# Database paths
DATABASE_PATH = Path(__file__).parent / "data" / "leadfinder.db"
DATABASE_PATH.parent.mkdir(exist_ok=True)

# Environment detection
ENVIRONMENT = os.getenv('FLASK_ENV', 'development').lower()

# Validate configuration on import
if __name__ != '__main__':
    try:
        validate_startup_config()
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        # Don't exit during import, let the application handle it 