"""
Unit tests for configuration module.
"""
import pytest
from unittest.mock import patch, MagicMock
from config import ConfigurationManager, ConfigurationError
from models.config import ConfigManager


class TestConfigurationManager:
    """Test ConfigurationManager class."""
    
    def test_configuration_manager_initialization(self):
        """Test ConfigurationManager initialization."""
        cm = ConfigurationManager()
        assert cm is not None
    
    def test_get_config_with_default(self):
        """Test getting config value with default."""
        cm = ConfigurationManager()
        value = cm.get('TEST_KEY', 'default_value')
        assert value == 'default_value'
    
    def test_get_config_from_env(self, mock_env_vars):
        """Test getting config value from environment."""
        cm = ConfigurationManager()
        value = cm.get('SERPAPI_KEY', 'default')
        assert value == 'test_key'
    
    def test_get_config_required_missing(self):
        """Test getting required config that is missing."""
        cm = ConfigurationManager()
        with pytest.raises(ConfigurationError):
            cm.get('REQUIRED_KEY', required=True)
    
    def test_set_config(self, temp_db):
        """Test setting configuration."""
        with patch('models.config.DATABASE_PATH', temp_db):
            cm = ConfigurationManager()
            success = cm.set('TEST_KEY', 'test_value', 'Test description')
            assert success is True
            value = cm.get('TEST_KEY')
            assert value == 'test_value'
    
    def test_get_source_environment(self, mock_env_vars):
        """Test getting config source from environment."""
        cm = ConfigurationManager()
        source = cm.get_source('SERPAPI_KEY')
        assert source == 'Environment'
    
    def test_get_source_database(self, temp_db):
        """Test getting config source from database."""
        with patch('models.config.DATABASE_PATH', temp_db):
            cm = ConfigurationManager()
            cm.set('TEST_KEY', 'test_value')
            source = cm.get_source('TEST_KEY')
            assert source == 'Database'
    
    def test_get_source_default(self):
        """Test getting config source from default."""
        cm = ConfigurationManager()
        source = cm.get_source('NONEXISTENT_KEY')
        assert source == 'Default'
    
    def test_validate_required_configs(self):
        """Test validating required configurations."""
        cm = ConfigurationManager()
        missing = cm.validate_required_configs()
        # Should include SERPAPI_KEY since it's required but not set in test
        assert 'SERPAPI_KEY' in missing
    
    def test_get_all_configs(self):
        """Test getting all configurations."""
        cm = ConfigurationManager()
        configs = cm.get_all_configs()
        assert 'SERPAPI_KEY' in configs
        assert 'OLLAMA_BASE_URL' in configs
        assert configs['OLLAMA_BASE_URL']['value'] == 'http://localhost:11434'


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