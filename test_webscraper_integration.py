#!/usr/bin/env python3
"""
Test script for WebScraper integration
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_webscraper_availability():
    """Test if WebScraper service is available"""
    print("🔍 Testing WebScraper availability...")
    
    try:
        from services.webscraper_service import webscraper_service
        
        status = webscraper_service.get_status()
        
        print(f"✅ WebScraper service initialized")
        print(f"   Available: {'Yes' if status.get('available') else 'No'}")
        print(f"   Playwright available: {'Yes' if status.get('playwright_available') else 'No'}")
        print(f"   BeautifulSoup available: {'Yes' if status.get('beautifulsoup_available') else 'No'}")
        print(f"   Initialized: {'Yes' if status.get('initialized') else 'No'}")
        print(f"   Browser running: {'Yes' if status.get('browser_running') else 'No'}")
        
        return status.get('available', False)
        
    except Exception as e:
        print(f"❌ Error testing WebScraper availability: {e}")
        return False

def test_langchain_availability():
    """Test if LangChain analyzer is available"""
    print("\n🧠 Testing LangChain availability...")
    
    try:
        from services.langchain_analyzer import langchain_analyzer
        
        status = langchain_analyzer.get_status()
        
        print(f"✅ LangChain analyzer initialized")
        print(f"   Available: {'Yes' if status.get('available') else 'No'}")
        print(f"   LangChain available: {'Yes' if status.get('langchain_available') else 'No'}")
        print(f"   Ollama available: {'Yes' if status.get('ollama_available') else 'No'}")
        print(f"   RunPod available: {'Yes' if status.get('runpod_available') else 'No'}")
        print(f"   Initialized: {'Yes' if status.get('initialized') else 'No'}")
        print(f"   Model: {status.get('model', 'Unknown')}")
        
        return status.get('available', False)
        
    except Exception as e:
        print(f"❌ Error testing LangChain availability: {e}")
        return False

async def test_webscraper_functionality():
    """Test WebScraper functionality with a sample URL"""
    print("\n🕷️ Testing WebScraper functionality...")
    
    try:
        from services.webscraper_service import webscraper_service
        
        if not webscraper_service.is_available():
            print("❌ WebScraper service not available - skipping functionality test")
            return False
        
        # Test with a simple URL
        test_url = "https://httpbin.org/html"
        
        print(f"   Testing with URL: {test_url}")
        
        result = await webscraper_service.scrape_url(test_url, "general")
        
        if result.success:
            print("✅ WebScraper functionality test successful!")
            print(f"   Title: {result.content.title}")
            print(f"   Content length: {len(result.content.content)} characters")
            print(f"   Processing time: {result.processing_time:.2f}s")
            print(f"   Source type: {result.content.source_type}")
            return True
        else:
            print(f"❌ WebScraper functionality test failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing WebScraper functionality: {e}")
        return False

def test_langchain_functionality():
    """Test LangChain analyzer functionality"""
    print("\n🧠 Testing LangChain functionality...")
    
    try:
        from services.langchain_analyzer import langchain_analyzer
        
        if not langchain_analyzer.is_available():
            print("❌ LangChain analyzer not available - skipping functionality test")
            return False
        
        # Test with sample content
        test_content = """
        Title: Test Scientific Paper
        Authors: John Doe, Jane Smith
        Abstract: This is a test abstract for a scientific paper about epigenetics and diabetes.
        Keywords: epigenetics, diabetes, research
        Institution: Test University
        """
        
        print("   Testing with sample scientific content...")
        
        analysis = langchain_analyzer.analyze_scientific_paper(
            test_content,
            "https://example.com/test-paper",
            "epigenetics research"
        )
        
        if analysis.success:
            print("✅ LangChain functionality test successful!")
            print(f"   Summary: {analysis.summary[:100]}...")
            print(f"   Insights: {len(analysis.insights)} insights found")
            print(f"   Processing time: {analysis.processing_time:.2f}s")
            print(f"   Model used: {analysis.model_used}")
            return True
        else:
            print(f"❌ LangChain functionality test failed: {analysis.error}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LangChain functionality: {e}")
        return False

async def test_integration():
    """Test the complete integration"""
    print("\n🔗 Testing complete integration...")
    
    try:
        from services.webscraper_service import webscraper_service
        from services.langchain_analyzer import langchain_analyzer
        
        if not webscraper_service.is_available() or not langchain_analyzer.is_available():
            print("❌ Services not available - skipping integration test")
            return False
        
        # Test with a simple URL
        test_url = "https://httpbin.org/html"
        
        print(f"   Testing integration with URL: {test_url}")
        
        # Step 1: Scrape content
        scraping_result = await webscraper_service.scrape_url(test_url, "general")
        
        if not scraping_result.success:
            print(f"❌ Scraping failed: {scraping_result.error}")
            return False
        
        print(f"   ✅ Scraping successful: {len(scraping_result.content.content)} characters")
        
        # Step 2: Analyze with LangChain
        analysis = langchain_analyzer.analyze_scientific_paper(
            scraping_result.content.content,
            scraping_result.content.url,
            "test research context"
        )
        
        if analysis.success:
            print("✅ Integration test successful!")
            print(f"   Total processing time: {scraping_result.processing_time + analysis.processing_time:.2f}s")
            print(f"   AI summary: {analysis.summary[:100]}...")
            return True
        else:
            print(f"❌ Analysis failed: {analysis.error}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("📦 Testing dependencies...")
    
    dependencies = {
        'playwright': 'Playwright for browser automation',
        'bs4': 'BeautifulSoup for HTML parsing',
        'langchain': 'LangChain for AI analysis',
        'pydantic': 'Pydantic for data validation'
    }
    
    missing_deps = []
    
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            print(f"   ✅ {dep}: {description}")
        except ImportError:
            print(f"   ❌ {dep}: {description} - MISSING")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("   Install with: pip install " + " ".join(missing_deps))
        return False
    else:
        print("   ✅ All dependencies available")
        return True

async def main():
    """Main test function"""
    print("🧪 WebScraper Integration Test")
    print("=" * 50)
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Dependencies missing - cannot proceed with tests")
        return 1
    
    # Test service availability
    webscraper_ok = test_webscraper_availability()
    langchain_ok = test_langchain_availability()
    
    if not webscraper_ok:
        print("\n❌ WebScraper service not available")
        return 1
    
    if not langchain_ok:
        print("\n⚠️  LangChain analyzer not available - some tests will be skipped")
    
    # Test functionality
    webscraper_func_ok = await test_webscraper_functionality()
    
    if langchain_ok:
        langchain_func_ok = test_langchain_functionality()
        integration_ok = await test_integration()
    else:
        langchain_func_ok = False
        integration_ok = False
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    print(f"   Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"   WebScraper Service: {'✅' if webscraper_ok else '❌'}")
    print(f"   LangChain Service: {'✅' if langchain_ok else '❌'}")
    print(f"   WebScraper Functionality: {'✅' if webscraper_func_ok else '❌'}")
    print(f"   LangChain Functionality: {'✅' if langchain_func_ok else '❌'}")
    print(f"   Integration: {'✅' if integration_ok else '❌'}")
    
    if deps_ok and webscraper_ok and webscraper_func_ok:
        print("\n🎉 WebScraper integration is working!")
        if langchain_ok and langchain_func_ok and integration_ok:
            print("   Full AI analysis capabilities are available!")
        else:
            print("   Basic scraping is available, but AI analysis needs configuration.")
        return 0
    else:
        print("\n❌ WebScraper integration has issues")
        print("   Check the error messages above and install missing dependencies.")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main())) 