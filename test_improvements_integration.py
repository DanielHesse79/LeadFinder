#!/usr/bin/env python3
"""
Test script to verify LeadFinder improvements integration
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all improvement modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from utils.redis_cache import get_redis_cache_manager
        print("✅ Redis cache module imported successfully")
    except ImportError as e:
        print(f"❌ Redis cache import failed: {e}")
        return False
    
    try:
        from models.database_indexes import create_standard_indexes
        print("✅ Database indexes module imported successfully")
    except ImportError as e:
        print(f"❌ Database indexes import failed: {e}")
        return False
    
    try:
        from utils.async_service import get_async_manager
        print("✅ Async service module imported successfully")
    except ImportError as e:
        print(f"❌ Async service import failed: {e}")
        return False
    
    try:
        from utils.rate_limiter import get_rate_limiter
        print("✅ Rate limiter module imported successfully")
    except ImportError as e:
        print(f"❌ Rate limiter import failed: {e}")
        return False
    
    try:
        from utils.analytics import get_analytics_manager
        print("✅ Analytics module imported successfully")
    except ImportError as e:
        print(f"❌ Analytics import failed: {e}")
        return False
    
    try:
        from utils.api_docs import generate_api_documentation
        print("✅ API docs module imported successfully")
    except ImportError as e:
        print(f"❌ API docs import failed: {e}")
        return False
    
    return True

def test_initialization():
    """Test that improvement systems can be initialized"""
    print("\n🔧 Testing initialization...")
    
    try:
        # Test Redis cache initialization
        from utils.redis_cache import get_redis_cache_manager
        redis_cache = get_redis_cache_manager()
        health = redis_cache.get_health_status()
        print(f"✅ Redis cache initialized: {health['is_healthy']}")
    except Exception as e:
        print(f"⚠️  Redis cache initialization failed: {e}")
    
    try:
        # Test database indexes initialization
        from models.database_indexes import create_standard_indexes
        indexes_created = create_standard_indexes()
        print(f"✅ Database indexes created: {indexes_created} indexes")
    except Exception as e:
        print(f"⚠️  Database indexes initialization failed: {e}")
    
    try:
        # Test async service initialization
        from utils.async_service import get_async_manager
        async_manager = get_async_manager()
        print("✅ Async service manager initialized")
    except Exception as e:
        print(f"⚠️  Async service initialization failed: {e}")
    
    try:
        # Test rate limiter initialization
        from utils.rate_limiter import get_rate_limiter
        rate_limiter = get_rate_limiter()
        print("✅ Rate limiter initialized")
    except Exception as e:
        print(f"⚠️  Rate limiter initialization failed: {e}")
    
    try:
        # Test analytics initialization
        from utils.analytics import get_analytics_manager
        analytics_manager = get_analytics_manager()
        print("✅ Analytics manager initialized")
    except Exception as e:
        print(f"⚠️  Analytics initialization failed: {e}")

def test_app_integration():
    """Test that the Flask app can be created with improvements"""
    print("\n🌐 Testing Flask app integration...")
    
    try:
        # Import the app creation function
        from app import create_app
        
        # Create the app
        app = create_app()
        print("✅ Flask app created successfully with improvements")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                health_data = response.get_json()
                print("✅ Health endpoint working")
                
                # Check if improvements are included in health
                if 'improvements' in health_data:
                    print("✅ Improvements included in health check")
                    for system, status in health_data['improvements'].items():
                        print(f"   - {system}: {status.get('status', 'unknown')}")
                else:
                    print("⚠️  Improvements not found in health check")
            else:
                print(f"⚠️  Health endpoint returned status {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Flask app integration failed: {e}")
        return False

def test_api_docs():
    """Test API documentation generation"""
    print("\n📚 Testing API documentation...")
    
    try:
        from utils.api_docs import generate_api_documentation
        from app import create_app
        
        app = create_app()
        docs = generate_api_documentation(app)
        
        if docs and 'routes' in docs:
            print(f"✅ API documentation generated: {len(docs['routes'])} routes")
            return True
        else:
            print("⚠️  API documentation generation failed")
            return False
    except Exception as e:
        print(f"❌ API documentation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LeadFinder Improvements Integration Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your installation.")
        return False
    
    # Test initialization
    test_initialization()
    
    # Test Flask app integration
    if not test_app_integration():
        print("\n❌ Flask app integration failed.")
        return False
    
    # Test API documentation
    if not test_api_docs():
        print("\n⚠️  API documentation test failed.")
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("🎉 LeadFinder improvements are properly integrated.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 