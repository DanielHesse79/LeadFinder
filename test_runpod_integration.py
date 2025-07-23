#!/usr/bin/env python3
"""
Test script for RunPod.ai integration
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_runpod_configuration():
    """Test RunPod configuration loading"""
    print("🔍 Testing RunPod configuration...")
    
    try:
        from services.runpod_service import RunPodService, RunPodConfig
        
        # Test configuration loading
        service = RunPodService()
        
        print(f"✅ RunPod service initialized")
        print(f"   API Key configured: {'Yes' if service.config.api_key else 'No'}")
        print(f"   Endpoint ID: {service.config.endpoint_id}")
        print(f"   Base URL: {service.config.base_url}")
        print(f"   Timeout: {service.config.timeout}s")
        print(f"   Max Retries: {service.config.max_retries}")
        
        # Test availability
        is_available = service.is_available()
        print(f"   Service available: {'Yes' if is_available else 'No'}")
        
        if not is_available:
            print("   ⚠️  Service not available - check API key and endpoint ID")
            return False
        
        # Test status
        status = service.get_status()
        print(f"   Status: {status.get('status', 'Unknown')}")
        
        if status.get('available'):
            print("✅ RunPod configuration is valid!")
            return True
        else:
            print(f"❌ RunPod status check failed: {status.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing RunPod configuration: {e}")
        return False

def test_runpod_api_call():
    """Test a simple RunPod API call"""
    print("\n🚀 Testing RunPod API call...")
    
    try:
        from services.runpod_service import RunPodService
        
        service = RunPodService()
        
        if not service.is_available():
            print("❌ RunPod service not available - skipping API test")
            return False
        
        # Test data
        test_lead = {
            'title': 'Test Lead - Healthcare Technology',
            'description': 'A healthcare company developing AI-powered diagnostic tools for early disease detection.',
            'link': 'https://example.com/test-lead',
            'source': 'Test Source'
        }
        
        print("   Sending test analysis request...")
        result = service.analyze_lead(test_lead, "Healthcare technology research")
        
        if result.success:
            print("✅ RunPod API call successful!")
            print(f"   Analysis: {result.analysis[:100]}...")
            print(f"   Score: {result.score}")
            print(f"   Processing time: {result.processing_time:.2f}s")
            print(f"   Model used: {result.model_used}")
            return True
        else:
            print(f"❌ RunPod API call failed: {result.analysis}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing RunPod API: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 RunPod.ai Integration Test")
    print("=" * 50)
    
    # Check environment variables
    print("📋 Environment Variables:")
    runpod_vars = ['RUNPOD_API_KEY', 'RUNPOD_ENDPOINT_ID', 'RUNPOD_BASE_URL']
    for var in runpod_vars:
        value = os.getenv(var, 'Not set')
        if var == 'RUNPOD_API_KEY' and value != 'Not set':
            value = f"{value[:8]}..." if len(value) > 8 else value
        print(f"   {var}: {value}")
    
    print()
    
    # Test configuration
    config_ok = test_runpod_configuration()
    
    if config_ok:
        # Test API call
        api_ok = test_runpod_api_call()
        
        if api_ok:
            print("\n🎉 All RunPod tests passed!")
            print("   The RunPod integration is working correctly.")
            return 0
        else:
            print("\n⚠️  RunPod configuration is valid but API calls failed.")
            print("   Check your API key and endpoint status.")
            return 1
    else:
        print("\n❌ RunPod configuration test failed.")
        print("   Please check your environment variables and endpoint setup.")
        return 1

if __name__ == "__main__":
    exit(main()) 