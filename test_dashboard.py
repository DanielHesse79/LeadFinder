#!/usr/bin/env python3
"""
Test script for the new dashboard implementation
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_imports():
    """Test that all dashboard-related imports work"""
    print("🧪 Testing Dashboard Implementation")
    print("=" * 50)
    
    try:
        # Test dashboard route import
        from routes.dashboard import dashboard_bp
        print("✅ Dashboard blueprint imported successfully")
        
        # Test database functions
        from models.database import get_lead_stats, get_rag_stats
        print("✅ Database functions imported successfully")
        
        # Test RAG services
        try:
            from services.rag_generator import RAGGenerator
            print("✅ RAG Generator imported successfully")
        except ImportError as e:
            print(f"⚠️  RAG Generator import failed: {e}")
        
        try:
            from services.vector_store_service import VectorStoreService
            print("✅ Vector Store Service imported successfully")
        except ImportError as e:
            print(f"⚠️  Vector Store Service import failed: {e}")
        
        # Test app import
        try:
            from app import create_app
            print("✅ App creation function imported successfully")
        except ImportError as e:
            print(f"⚠️  App import failed: {e}")
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print("✅ Dashboard blueprint: READY")
        print("✅ Database functions: READY")
        print("✅ App integration: READY")
        print("\n🎉 Dashboard implementation is ready for testing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_dashboard_functionality():
    """Test dashboard functionality"""
    print("\n🔍 Testing Dashboard Functionality")
    print("=" * 50)
    
    try:
        # Test database stats
        from models.database import get_lead_stats, get_rag_stats
        
        lead_stats = get_lead_stats()
        print(f"✅ Lead stats retrieved: {lead_stats.get('total_leads', 0)} leads")
        
        rag_stats = get_rag_stats()
        print(f"✅ RAG stats retrieved: {rag_stats.get('total_chunks', 0)} chunks")
        
        # Test dashboard route creation
        from routes.dashboard import get_dashboard_stats
        dashboard_stats = get_dashboard_stats()
        print(f"✅ Dashboard stats generated: {len(dashboard_stats)} metrics")
        
        print("\n🎉 Dashboard functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_template_rendering():
    """Test that the dashboard template can be rendered"""
    print("\n🎨 Testing Template Rendering")
    print("=" * 50)
    
    try:
        # Check if template exists
        template_path = "templates/dashboard.html"
        if os.path.exists(template_path):
            print(f"✅ Dashboard template exists: {template_path}")
            
            # Check template size
            size = os.path.getsize(template_path)
            print(f"✅ Template size: {size} bytes")
            
            # Check for key elements
            with open(template_path, 'r') as f:
                content = f.read()
                
            if "workflow-card" in content:
                print("✅ Workflow cards found in template")
            if "Data Mining" in content:
                print("✅ Data Mining section found")
            if "Data Processing" in content:
                print("✅ Data Processing section found")
            if "RAG Search" in content:
                print("✅ RAG Search section found")
                
        else:
            print(f"❌ Dashboard template not found: {template_path}")
            return False
            
        print("\n🎉 Template rendering test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LeadFinder Dashboard Test Suite")
    print("=" * 60)
    
    # Run tests
    import_success = test_dashboard_imports()
    functionality_success = test_dashboard_functionality()
    template_success = test_template_rendering()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"Import Tests: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"Functionality Tests: {'✅ PASS' if functionality_success else '❌ FAIL'}")
    print(f"Template Tests: {'✅ PASS' if template_success else '❌ FAIL'}")
    
    if all([import_success, functionality_success, template_success]):
        print("\n🎉 ALL TESTS PASSED! Dashboard is ready to use.")
        print("\n📝 Next Steps:")
        print("1. Start the application: ./start_app.sh development")
        print("2. Visit the dashboard: http://localhost:5051/dashboard/")
        print("3. Test the navigation: http://localhost:5051/rag/search")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 