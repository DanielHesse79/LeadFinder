"""
Unit tests for database module.
"""
import pytest
from unittest.mock import patch, MagicMock
from models.database import DatabaseConnection, get_all_leads, save_lead, delete_lead


class TestDatabaseConnection:
    """Test DatabaseConnection class."""
    
    def test_database_connection(self, temp_db):
        """Test database connection."""
        with patch('models.database.DATABASE_PATH', temp_db):
            db = DatabaseConnection()
            assert db is not None
    
    def test_create_tables(self, temp_db):
        """Test table creation."""
        with patch('models.database.DATABASE_PATH', temp_db):
            db = DatabaseConnection()
            db.create_tables()
            # Should not raise an exception


class TestLeadOperations:
    """Test lead database operations."""
    
    def test_save_lead(self, temp_db):
        """Test saving a lead."""
        with patch('models.database.DATABASE_PATH', temp_db):
            lead_data = {
                'title': 'Test Lead',
                'description': 'Test Description',
                'link': 'https://example.com',
                'ai_summary': 'AI Summary',
                'source': 'test'
            }
            
            lead_id = save_lead(**lead_data)
            assert lead_id is not None
    
    def test_get_all_leads(self, temp_db):
        """Test getting all leads."""
        with patch('models.database.DATABASE_PATH', temp_db):
            # First save a lead
            lead_data = {
                'title': 'Test Lead',
                'description': 'Test Description',
                'link': 'https://example.com',
                'ai_summary': 'AI Summary',
                'source': 'test'
            }
            save_lead(**lead_data)
            
            # Then get all leads
            leads = get_all_leads()
            assert len(leads) >= 1
            assert leads[0]['title'] == 'Test Lead'
    
    def test_delete_lead(self, temp_db):
        """Test deleting a lead."""
        with patch('models.database.DATABASE_PATH', temp_db):
            # First save a lead
            lead_data = {
                'title': 'Test Lead',
                'description': 'Test Description',
                'link': 'https://example.com',
                'ai_summary': 'AI Summary',
                'source': 'test'
            }
            lead_id = save_lead(**lead_data)
            
            # Then delete it
            result = delete_lead(lead_id)
            assert result is True
            
            # Verify it's gone
            leads = get_all_leads()
            assert len([l for l in leads if l['id'] == lead_id]) == 0 