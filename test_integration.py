#!/usr/bin/env python3
"""
Test script for local AutoGPT integration with Leadfinder app using Ollama
"""

import json
import sys
from autogpt_client import LocalAutoGPTClient, AutoGPTConfig
from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration

def test_ollama_connection():
    """Test Ollama connection"""
    print("🔍 Testing Ollama connection...")
    
    try:
        from services.ollama_service import ollama_service
        if not ollama_service:
            print("❌ Ollama service not available")
            return False
        
        status = ollama_service.check_status()
        if status.get("ok"):
            print(f"✅ Ollama connected! Status: {status.get('msg', 'OK')}")
            return True
        else:
            print(f"❌ Ollama not ready: {status.get('msg', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_text_generation():
    """Test text generation with local AutoGPT"""
    print("\n🤖 Testing text generation...")
    
    try:
        config = AutoGPTConfig(model="mistral:latest")
        client = LocalAutoGPTClient(config)
        
        # Test with a simple prompt
        result = client.execute_text_generation("Hello! Please respond with a short greeting.")
        
        if result["status"] == "COMPLETED":
            print("✅ Text generation successful!")
            print(f"📄 Response: {result['output'][:100]}...")
            return True
        else:
            print(f"❌ Text generation failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Text generation failed: {e}")
        return False

def test_web_search():
    """Test web search functionality"""
    print("\n🌐 Testing web search...")
    
    try:
        config = AutoGPTConfig(model="mistral:latest")
        client = LocalAutoGPTClient(config)
        
        # Test web search
        result = client.execute_web_search("AI companies Sweden")
        
        if result["status"] == "COMPLETED":
            print("✅ Web search successful!")
            print(f"📊 Found {len(result.get('output', []))} results")
            return True
        else:
            print(f"❌ Web search failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Web search failed: {e}")
        return False

def test_leadfinder_integration():
    """Test Leadfinder integration"""
    print("\n🎯 Testing Leadfinder integration...")
    
    try:
        integration = LeadfinderAutoGPTIntegration("mistral:latest")
        
        # Test lead research
        results = integration.research_leads(
            company_name="TechCorp Solutions",
            industry="SaaS"
        )
        
        if results.get("status") == "COMPLETED":
            print("✅ Lead research successful!")
            print(f"📋 AI Analysis: {results.get('ai_analysis', {}).get('output', '')[:100]}...")
            return True
        else:
            print(f"❌ Lead research failed: {results.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Leadfinder integration failed: {e}")
        return False

def test_enhanced_search():
    """Test enhanced search results"""
    print("\n🔍 Testing enhanced search...")
    
    try:
        integration = LeadfinderAutoGPTIntegration("mistral:latest")
        
        # Mock search results
        mock_results = [
            {
                "title": "AI Company in Stockholm",
                "snippet": "Leading AI company specializing in machine learning solutions",
                "link": "https://example.com"
            },
            {
                "title": "Tech Startup Sweden",
                "snippet": "Innovative startup in the technology sector",
                "link": "https://example2.com"
            }
        ]
        
        enhanced = integration.enhance_search_results(
            mock_results, 
            "Find potential AI clients in Sweden"
        )
        
        if enhanced.get("status") == "COMPLETED":
            print("✅ Enhanced search successful!")
            print(f"📊 Analysis: {enhanced.get('output', '')[:100]}...")
            return True
        else:
            print(f"❌ Enhanced search failed: {enhanced.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Enhanced search failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Local AutoGPT Integration Test (Ollama)")
    print("=" * 50)
    
    # Test Ollama connection
    if not test_ollama_connection():
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Verify Mistral model is installed: ollama pull mistral:latest")
        print("3. Check that Ollama is accessible at http://localhost:11434")
        sys.exit(1)
    
    # Test text generation
    if not test_text_generation():
        print("❌ Text generation test failed")
        sys.exit(1)
    
    # Test web search
    if not test_web_search():
        print("⚠️  Web search test failed (SerpAPI might not be configured)")
    
    # Test Leadfinder integration
    if not test_leadfinder_integration():
        print("❌ Leadfinder integration test failed")
        sys.exit(1)
    
    # Test enhanced search
    if not test_enhanced_search():
        print("❌ Enhanced search test failed")
        sys.exit(1)
    
    print("\n🎉 All tests completed successfully!")
    print("\n📋 Next steps:")
    print("1. Integration is ready to use in your Leadfinder app")
    print("2. You can now use enhanced search with AI analysis")
    print("3. AutoGPT features are available for lead research")

if __name__ == "__main__":
    main() 