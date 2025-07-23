"""
Configuration database model

This module handles storage and retrieval of API keys and configuration
settings in the database instead of environment variables.
"""

import sqlite3
import os
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger('config_model')

class ConfigManager:
    """Manages application configuration stored in database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default database path
            base_dir = Path(__file__).parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "leadfinder.db")
        
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
            
            # Import configuration definitions from main config
            try:
                from config import CONFIG_DEFINITIONS
                default_configs = []
                for key, config_info in CONFIG_DEFINITIONS.items():
                    default_configs.append((
                        key,
                        config_info.get('default', ''),
                        config_info['description'],
                        config_info.get('is_secret', False)
                    ))
            except ImportError:
                # Fallback to basic configs if main config not available
                default_configs = [
                    ('SERPAPI_KEY', '', 'SerpAPI key for Google search', 1),
                    ('OLLAMA_BASE_URL', 'http://localhost:11434', 'Ollama server base URL', 0),
                    ('FLASK_SECRET_KEY', '', 'Flask secret key for sessions', 1),
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
            'FLASK_SECRET_KEY'
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
    
    def reset_to_defaults(self) -> bool:
        """Reset all configuration values to defaults"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Reset all values to empty/default
            c.execute('UPDATE app_config SET key_value = "" WHERE is_secret = 1')
            
            # Set specific defaults for non-secret values
            defaults = {
                'OLLAMA_BASE_URL': 'http://localhost:11434',
                'OLLAMA_MODEL': 'mistral:latest',
                'OLLAMA_TIMEOUT': '30',
                'DEFAULT_RESEARCH_QUESTION': 'epigenetics and pre-diabetes',
                'ORCID_BASE_URL': 'https://pub.orcid.org/v3.0',
                'PUBMED_BASE_URL': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils',
                'FLASK_DEBUG': 'False',
                'FLASK_HOST': '0.0.0.0',
                'FLASK_PORT': '5051',
                'RESEARCH_MAX_RESULTS': '50',
                'RESEARCH_TIMEOUT': '30',
                'LOG_LEVEL': 'INFO',
                'LOG_FILE': 'leadfinder.log',
                'REQUEST_POOL_SIZE': '10',
                'REQUEST_TIMEOUT': '10',
                'MAX_TEXT_LENGTH': '1000',
                'EXPORT_FOLDER': 'exports',
                'SCIHUB_FOLDER': 'scihub_pdfs'
            }
            
            for key, value in defaults.items():
                c.execute('UPDATE app_config SET key_value = ? WHERE key_name = ?', (value, key))
            
            conn.commit()
            conn.close()
            logger.info("Reset all configurations to defaults")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting configs: {e}")
            return False 