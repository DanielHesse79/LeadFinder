"""
Pytest configuration and fixtures for LeadFinder tests.
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'SERPAPI_KEY': 'test_key',
        'OLLAMA_BASE_URL': 'http://localhost:11434',
        'OLLAMA_MODEL': 'mistral',
        'FLASK_SECRET_KEY': 'test_secret',
        'FLASK_DEBUG': 'False'
    }

@pytest.fixture
def mock_env_vars(monkeypatch, sample_config):
    """Mock environment variables for testing."""
    for key, value in sample_config.items():
        monkeypatch.setenv(key, value)
    return sample_config 