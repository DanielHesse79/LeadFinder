#!/usr/bin/env python3
"""
Simple test script for the dashboard implementation (no Flask required)
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_functions():
    """Test database functions without Flask"""
    print("🧪 Testing Database Functions")
    print("=" * 50)
    
    try:
        # Test database functions
        from models.database import get_lead_stats, get_rag_stats
        
        lead_stats = get_lead_stats()
        print(f"✅ Lead stats: {lead_stats.get('total_leads', 0)} leads")
        
        rag_stats = get_rag_stats()
        print(f"✅ RAG stats: {rag_stats.get('total_chunks', 0)} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_dashboard_stats():
    """Test dashboard stats function"""
    print("\n📊 Testing Dashboard Stats")
    print("=" * 50)
    
    try:
        # Import the function directly
        import routes.dashboard
        
        # Test the stats function
        stats = routes.dashboard.get_dashboard_stats()
        
        print(f"✅ Total leads: {stats.get('total_leads', 0)}")
        print(f"✅ RAG documents: {stats.get('rag_documents', 0)}")
        print(f"✅ Total searches: {stats.get('total_searches', 0)}")
        print(f"✅ AI analyses: {stats.get('ai_analyses', 0)}")
        print(f"✅ RAG queries: {stats.get('rag_queries', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard stats test failed: {e}")
        return False

def test_template_exists():
    """Test that templates exist"""
    print("\n🎨 Testing Templates")
    print("=" * 50)
    
    templates_to_check = [
        "templates/dashboard.html",
        "templates/navigation.html"
    ]
    
    all_exist = True
    for template in templates_to_check:
        if os.path.exists(template):
            size = os.path.getsize(template)
            print(f"✅ {template}: {size} bytes")
        else:
            print(f"❌ {template}: NOT FOUND")
            all_exist = False
    
    return all_exist

def test_route_structure():
    """Test that route files exist and are valid Python"""
    print("\n🛣️  Testing Route Structure")
    print("=" * 50)
    
    routes_to_check = [
        "routes/dashboard.py",
        "routes/rag_routes.py"
    ]
    
    all_valid = True
    for route in routes_to_check:
        if os.path.exists(route):
            try:
                # Try to compile the Python file
                with open(route, 'r') as f:
                    compile(f.read(), route, 'exec')
                print(f"✅ {route}: Valid Python")
            except SyntaxError as e:
                print(f"❌ {route}: Syntax error - {e}")
                all_valid = False
        else:
            print(f"❌ {route}: NOT FOUND")
            all_valid = False
    
    return all_valid

def main():
    """Run all tests"""
    print("🚀 LeadFinder Dashboard Simple Test Suite")
    print("=" * 60)
    
    # Run tests
    db_success = test_database_functions()
    stats_success = test_dashboard_stats()
    template_success = test_template_exists()
    route_success = test_route_structure()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"Database Functions: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"Dashboard Stats: {'✅ PASS' if stats_success else '❌ FAIL'}")
    print(f"Templates: {'✅ PASS' if template_success else '❌ FAIL'}")
    print(f"Route Structure: {'✅ PASS' if route_success else '❌ FAIL'}")
    
    if all([db_success, stats_success, template_success, route_success]):
        print("\n🎉 ALL TESTS PASSED! Dashboard implementation is ready.")
        print("\n📝 Next Steps:")
        print("1. Install Flask: pip install flask")
        print("2. Start the application: ./start_app.sh development")
        print("3. Visit the dashboard: http://localhost:5051/dashboard/")
        print("4. Test the navigation: http://localhost:5051/rag/search")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 