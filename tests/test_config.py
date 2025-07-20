"""
Unit tests for configuration module.
"""
import pytest
from unittest.mock import patch, MagicMock
from config import get_config_value, load_config_from_env
from models.config import ConfigManager


class TestConfig:
    """Test configuration functionality."""
    
    def test_get_config_value_default(self, mock_env_vars):
        """Test getting config value with default."""
        value = get_config_value('TEST_KEY', 'TEST_KEY', 'default_value')
        assert value == 'default_value'
    
    def test_get_config_value_from_env(self, mock_env_vars):
        """Test getting config value from environment."""
        value = get_config_value('SERPAPI_KEY', 'SERPAPI_KEY', 'default')
        assert value == 'test_key'
    
    @patch('config.os.getenv')
    def test_load_config_from_env(self, mock_getenv, sample_config):
        """Test loading configuration from environment."""
        mock_getenv.side_effect = lambda key, default=None: sample_config.get(key, default)
        
        config = load_config_from_env()
        assert config['SERPAPI_KEY'] == 'test_key'
        assert config['OLLAMA_BASE_URL'] == 'http://localhost:11434'


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_config_manager_initialization(self, temp_db):
        """Test ConfigManager initialization."""
        with patch('models.config.DATABASE_PATH', temp_db):
            cm = ConfigManager()
            assert cm is not None
    
    def test_get_config(self, temp_db):
        """Test getting configuration."""
        with patch('models.config.DATABASE_PATH', temp_db):
            cm = ConfigManager()
            value = cm.get_config('TEST_KEY', 'default_value')
            assert value == 'default_value'
    
    def test_set_config(self, temp_db):
        """Test setting configuration."""
        with patch('models.config.DATABASE_PATH', temp_db):
            cm = ConfigManager()
            cm.set_config('TEST_KEY', 'test_value', 'Test description')
            value = cm.get_config('TEST_KEY')
            assert value == 'test_value' 