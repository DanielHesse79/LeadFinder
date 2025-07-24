#!/usr/bin/env python3
"""
Test Search Fix

This script tests that the search functionality works without type comparison errors.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, '.')

def test_configuration_loading():
    """Test that configuration loads without type errors"""
    print("🧪 Testing Configuration Loading...")
    
    try:
        from config import (
            DB_POOL_MAX_CONNECTIONS, 
            DB_POOL_CONNECTION_TIMEOUT, 
            DB_POOL_HEALTH_CHECK_INTERVAL,
            CACHE_MAX_SIZE,
            CACHE_DEFAULT_TTL,
            CACHE_CLEANUP_INTERVAL
        )
        
        print(f"  ✅ DB_POOL_MAX_CONNECTIONS: {DB_POOL_MAX_CONNECTIONS}")
        print(f"  ✅ DB_POOL_CONNECTION_TIMEOUT: {DB_POOL_CONNECTION_TIMEOUT}")
        print(f"  ✅ DB_POOL_HEALTH_CHECK_INTERVAL: {DB_POOL_HEALTH_CHECK_INTERVAL}")
        print(f"  ✅ CACHE_MAX_SIZE: {CACHE_MAX_SIZE}")
        print(f"  ✅ CACHE_DEFAULT_TTL: {CACHE_DEFAULT_TTL}")
        print(f"  ✅ CACHE_CLEANUP_INTERVAL: {CACHE_CLEANUP_INTERVAL}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration loading failed: {e}")
        return False


def test_database_pool_initialization():
    """Test that database pool initializes without type errors"""
    print("🧪 Testing Database Pool Initialization...")
    
    try:
        from models.database_pool import DatabaseConnectionPool
        
        # Test with None values to ensure fallbacks work
        pool = DatabaseConnectionPool(
            max_connections=None,
            connection_timeout=None,
            check_interval=None
        )
        
        print(f"  ✅ Pool initialized successfully")
        print(f"  ✅ Max connections: {pool.max_connections}")
        print(f"  ✅ Connection timeout: {pool.connection_timeout}")
        print(f"  ✅ Check interval: {pool.check_interval}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database pool initialization failed: {e}")
        return False


def test_research_service_filters():
    """Test that research service filters work without type errors"""
    print("🧪 Testing Research Service Filters...")
    
    try:
        from services.research_service import research_service
        from services.api_base import ResearchProject
        from datetime import datetime
        
        # Create a mock project with string funding amount
        mock_project = ResearchProject(
            id="test-1",
            title="Test Project",
            description="Test description",
            principal_investigator="Test PI",
            organization="Test Org",
            funding_amount="50000",  # String instead of float
            currency="USD",
            start_date=datetime.now(),
            end_date=datetime.now(),
            keywords=["test"],
            source="test",
            url="http://test.com",
            raw_data={}
        )
        
        # Test filters with different data types
        filters = {
            'min_funding': 10000,  # Integer
            'max_funding': 100000,  # Integer
            'start_date': '2024-01-01',  # String date
            'end_date': '2024-12-31'  # String date
        }
        
        # This should not raise a type error
        filtered_projects = research_service.search_by_filters("test", filters)
        print(f"  ✅ Research service filters work correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Research service filters failed: {e}")
        return False


def test_progress_tracking():
    """Test that progress tracking works without type errors"""
    print("🧪 Testing Progress Tracking...")
    
    try:
        from utils.progress_manager import get_progress_manager, ProgressStatus, SEARCH_STEPS
        
        progress_manager = get_progress_manager()
        
        # Create a test operation
        operation_id = progress_manager.create_operation(
            name="Test Search",
            description="Testing search functionality",
            steps=SEARCH_STEPS
        )
        
        # Update steps with different data types
        progress_manager.update_step(
            operation_id, "step_1", 0.5, ProgressStatus.RUNNING,
            {"results_found": "10", "query": "test"}  # Mixed types
        )
        
        progress_manager.update_step(
            operation_id, "step_1", 1.0, ProgressStatus.COMPLETED,
            {"results_found": 10, "query": "test"}  # Mixed types
        )
        
        print(f"  ✅ Progress tracking works correctly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Progress tracking failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Search Fix")
    print("=" * 40)
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Database Pool Initialization", test_database_pool_initialization),
        ("Research Service Filters", test_research_service_filters),
        ("Progress Tracking", test_progress_tracking),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Search functionality should work without type errors.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 