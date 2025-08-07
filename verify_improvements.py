#!/usr/bin/env python3
"""
Simple verification script for LeadFinder improvements
"""

import os
import sys
from pathlib import Path

def check_files_exist():
    """Check that all improvement files exist"""
    print("🔍 Checking improvement files...")
    
    required_files = [
        'utils/redis_cache.py',
        'models/database_indexes.py',
        'utils/async_service.py',
        'utils/rate_limiter.py',
        'utils/analytics.py',
        'utils/api_docs.py',
        'tests/test_improvements.py',
        'tests/test_services.py',
        'deploy.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def check_app_integration():
    """Check that app.py has been updated with improvements"""
    print("\n🔧 Checking app.py integration...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for improvement imports
        improvement_imports = [
            'from utils.redis_cache import',
            'from models.database_indexes import',
            'from utils.async_service import',
            'from utils.rate_limiter import',
            'from utils.analytics import',
            'from utils.api_docs import'
        ]
        
        all_imports_found = True
        for import_line in improvement_imports:
            if import_line in content:
                print(f"✅ {import_line}")
            else:
                print(f"❌ {import_line} - MISSING")
                all_imports_found = False
        
        # Check for improvement initialization
        if '# Initialize improvement systems' in content:
            print("✅ Improvement systems initialization found")
        else:
            print("❌ Improvement systems initialization - MISSING")
            all_imports_found = False
        
        # Check for health endpoint updates
        if 'improvements' in content:
            print("✅ Health endpoint includes improvements")
        else:
            print("❌ Health endpoint improvements - MISSING")
            all_imports_found = False
        
        # Check for API docs endpoint
        if '@app.route(\'/api/docs\')' in content:
            print("✅ API documentation endpoint found")
        else:
            print("❌ API documentation endpoint - MISSING")
            all_imports_found = False
        
        return all_imports_found
        
    except Exception as e:
        print(f"❌ Error checking app.py: {e}")
        return False

def check_dependencies():
    """Check that required dependencies are in requirements.txt"""
    print("\n📦 Checking dependencies...")
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        required_deps = [
            'redis>=4.5.0',
            'aioredis>=2.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-mock>=3.10.0',
            'aiohttp>=3.8.0',
            'asyncio-mqtt>=0.11.0'
        ]
        
        all_deps_found = True
        for dep in required_deps:
            if dep in content:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep} - MISSING")
                all_deps_found = False
        
        return all_deps_found
        
    except Exception as e:
        print(f"❌ Error checking requirements.txt: {e}")
        return False

def check_documentation():
    """Check that documentation files exist"""
    print("\n📚 Checking documentation...")
    
    doc_files = [
        'IMPROVEMENTS_IMPLEMENTATION_SUMMARY.md',
        'IMPROVEMENTS_QUICK_START.md',
        'FINAL_IMPROVEMENTS_SUMMARY.md'
    ]
    
    all_docs_exist = True
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            print(f"✅ {doc_file}")
        else:
            print(f"❌ {doc_file} - MISSING")
            all_docs_exist = False
    
    return all_docs_exist

def main():
    """Run all verification checks"""
    print("🚀 LeadFinder Improvements Verification")
    print("=" * 50)
    
    # Check files exist
    files_ok = check_files_exist()
    
    # Check app integration
    app_ok = check_app_integration()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check documentation
    docs_ok = check_documentation()
    
    print("\n" + "=" * 50)
    print("📊 Verification Summary:")
    print(f"   Files: {'✅' if files_ok else '❌'}")
    print(f"   App Integration: {'✅' if app_ok else '❌'}")
    print(f"   Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"   Documentation: {'✅' if docs_ok else '❌'}")
    
    if files_ok and app_ok and deps_ok and docs_ok:
        print("\n🎉 All improvements are properly implemented!")
        print("✅ Ready for deployment")
        return True
    else:
        print("\n⚠️  Some improvements need attention")
        print("❌ Not ready for deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 