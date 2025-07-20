#!/usr/bin/env python3
"""
LeadFinder Startup Check

This script validates all required services before starting LeadFinder.
It checks database, Ollama, and AutoGPT integration.
"""

import sys
import time
from pathlib import Path

def check_database():
    """Check database connection"""
    print("🔍 Checking database...")
    try:
        from models.database import db
        count = db.get_lead_count()
        print(f"✅ Database: Connected ({{count}} leads)")
        return True
    except Exception as e:
        print(f"❌ Database: Failed - {e}")
        return False

def check_ollama():
    """Check Ollama service"""
    print("🔍 Checking Ollama...")
    try:
        from services.ollama_service import ollama_service
        status = ollama_service.check_status()
        if status.get("ok"):
            print(f"✅ Ollama: {status.get('msg', 'Ready')}")
            return True
        else:
            print(f"❌ Ollama: {status.get('msg', 'Not ready')}")
            return False
    except Exception as e:
        print(f"❌ Ollama: Failed - {e}")
        return False

def check_autogpt():
    """Check AutoGPT integration"""
    print("🔍 Checking AutoGPT integration...")
    try:
        from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
        from config import AUTOGPT_MODEL
        
        autogpt_integration = LeadfinderAutoGPTIntegration(AUTOGPT_MODEL)
        test_result = autogpt_integration.client.execute_text_generation("Startup check")
        
        if test_result.get('status') == 'COMPLETED':
            print(f"✅ AutoGPT: Ready (using {AUTOGPT_MODEL})")
            return True
        else:
            print(f"❌ AutoGPT: Test failed - {test_result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"⚠️  AutoGPT: Not available - {str(e)[:50]}...")
        return False

def check_serpapi():
    """Check SerpAPI configuration"""
    print("🔍 Checking SerpAPI...")
    try:
        from config import SERPAPI_KEY
        if SERPAPI_KEY and SERPAPI_KEY != 'your_serpapi_key_here':
            print("✅ SerpAPI: Key configured")
            return True
        else:
            print("⚠️  SerpAPI: Key not configured (some search features may not work)")
            return False
    except Exception as e:
        print(f"❌ SerpAPI: Configuration error - {e}")
        return False

def main():
    """Main startup check"""
    print("🚀 LeadFinder Startup Check")
    print("=" * 50)
    
    checks = {
        'Database': check_database,
        'Ollama': check_ollama,
        'AutoGPT': check_autogpt,
        'SerpAPI': check_serpapi
    }
    
    results = {}
    for name, check_func in checks.items():
        results[name] = check_func()
        time.sleep(0.5)  # Small delay between checks
    
    print("\n" + "=" * 50)
    print("📊 Startup Check Results:")
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! LeadFinder is ready to start.")
        print("💡 You can now run: python app.py")
        return True
    else:
        print("⚠️  Some checks failed. LeadFinder may have limited functionality.")
        print("💡 Check the configuration and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 