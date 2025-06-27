"""
Configuration database model

This module handles storage and retrieval of API keys and configuration
settings in the database instead of environment variables.
"""

import sqlite3
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger('config_model')

class ConfigManager:
    """Manages application configuration stored in database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_config_table()
    
    def _init_config_table(self):
        """Initialize the configuration table"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS app_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_name TEXT UNIQUE NOT NULL,
                key_value TEXT,
                description TEXT,
                is_secret BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Insert default configuration keys
            default_configs = [
                ('SERPAPI_KEY', '', 'SerpAPI key for Google search', 1),
                ('OLLAMA_BASE_URL', 'http://localhost:11434', 'Ollama server base URL', 0),
                ('OLLAMA_MODEL', 'mistral:latest', 'Default Ollama model', 0),
                ('SWECRIS_API_KEY', '', 'SweCRIS API key', 1),
                ('CORDIS_API_KEY', '', 'CORDIS API key', 1),
                ('NIH_API_KEY', '', 'NIH RePORTER API key', 1),
                ('NSF_API_KEY', '', 'NSF API key', 1),
                ('ORCID_CLIENT_ID', '', 'ORCID client ID', 1),
                ('ORCID_CLIENT_SECRET', '', 'ORCID client secret', 1),
                ('ORCID_BASE_URL', 'https://orcid.org/oauth', 'ORCID API base URL', 0),
                ('PUBMED_API_KEY', '', 'PubMed API key', 1),
                ('PUBMED_BASE_URL', 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils', 'PubMed API base URL', 0),
                ('FLASK_SECRET_KEY', '', 'Flask secret key for sessions', 1),
                ('FLASK_DEBUG', 'False', 'Flask debug mode', 0),
                ('RESEARCH_MAX_RESULTS', '50', 'Maximum results per research API', 0),
                ('RESEARCH_TIMEOUT', '30', 'Research API timeout in seconds', 0),
                ('LOG_LEVEL', 'INFO', 'Logging level (DEBUG, INFO, WARNING, ERROR)', 0),
                ('LOG_FILE', 'leadfinder.log', 'Log file path', 0),
                ('REQUEST_POOL_SIZE', '10', 'HTTP request connection pool size', 0),
            ]
            
            for key_name, key_value, description, is_secret in default_configs:
                c.execute('''INSERT OR IGNORE INTO app_config 
                            (key_name, key_value, description, is_secret) 
                            VALUES (?, ?, ?, ?)''', 
                         (key_name, key_value, description, is_secret))
            
            conn.commit()
            conn.close()
            logger.info("Configuration table initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize config table: {e}")
            raise
    
    def get_config(self, key_name: str, default: str = '') -> str:
        """Get configuration value by key name"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT key_value FROM app_config WHERE key_name = ?', (key_name,))
            result = c.fetchone()
            conn.close()
            
            return result[0] if result else default
            
        except Exception as e:
            logger.error(f"Error getting config {key_name}: {e}")
            return default
    
    def set_config(self, key_name: str, key_value: str, description: str = None, is_secret: bool = True) -> bool:
        """Set configuration value"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if description:
                c.execute('''INSERT OR REPLACE INTO app_config 
                            (key_name, key_value, description, is_secret, updated_at) 
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                         (key_name, key_value, description, is_secret))
            else:
                c.execute('''UPDATE app_config 
                            SET key_value = ?, updated_at = CURRENT_TIMESTAMP 
                            WHERE key_name = ?''',
                         (key_value, key_name))
            
            conn.commit()
            conn.close()
            logger.info(f"Updated config: {key_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting config {key_name}: {e}")
            return False
    
    def get_all_configs(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Get all configuration values"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            if include_secrets:
                c.execute('SELECT key_name, key_value, description, is_secret FROM app_config')
            else:
                c.execute('SELECT key_name, key_value, description, is_secret FROM app_config WHERE is_secret = 0')
            
            results = c.fetchall()
            conn.close()
            
            configs = {}
            for key_name, key_value, description, is_secret in results:
                configs[key_name] = {
                    'value': key_value if include_secrets or not is_secret else '***HIDDEN***',
                    'description': description,
                    'is_secret': bool(is_secret),
                    'has_value': bool(key_value)
                }
            
            return configs
            
        except Exception as e:
            logger.error(f"Error getting all configs: {e}")
            return {}
    
    def delete_config(self, key_name: str) -> bool:
        """Delete configuration key"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('DELETE FROM app_config WHERE key_name = ?', (key_name,))
            conn.commit()
            conn.close()
            logger.info(f"Deleted config: {key_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting config {key_name}: {e}")
            return False
    
    def get_missing_required_configs(self) -> list:
        """Get list of required configuration keys that are missing values"""
        required_keys = [
            'SERPAPI_KEY',
            'OLLAMA_BASE_URL',
            'OLLAMA_MODEL'
        ]
        
        missing = []
        for key in required_keys:
            value = self.get_config(key)
            if not value:
                missing.append(key)
        
        return missing
    
    def is_configured(self) -> bool:
        """Check if all required configurations are set"""
        return len(self.get_missing_required_configs()) == 0 