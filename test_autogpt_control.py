#!/usr/bin/env python3
"""
Test script for AutoGPT Control Panel functionality
"""

import requests
import json

def test_autogpt_endpoints():
    """Test all AutoGPT control panel endpoints"""
    base_url = "http://localhost:5050"
    
    print("🤖 Testing AutoGPT Control Panel Endpoints")
    print("=" * 50)
    
    # Test 1: Status endpoint
    print("\n1. Testing AutoGPT Status...")
    try:
        response = requests.get(f"{base_url}/autogpt/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'unknown')}")
            print(f"✅ Enabled: {data.get('enabled', 'unknown')}")
            print(f"✅ Model: {data.get('model', 'unknown')}")
        else:
            print(f"❌ Status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status error: {e}")
    
    # Test 2: Control panel page
    print("\n2. Testing Control Panel Page...")
    try:
        response = requests.get(f"{base_url}/autogpt/control")
        if response.status_code == 200:
            print("✅ Control panel page loads successfully")
        else:
            print(f"❌ Control panel failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Control panel error: {e}")
    
    # Test 3: Test endpoint
    print("\n3. Testing AutoGPT Test Function...")
    try:
        data = {
            'test_prompt': 'Hello, this is a test of AutoGPT functionality.',
            'model': 'mistral:latest'
        }
        response = requests.post(f"{base_url}/autogpt/test", data=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ AutoGPT test completed successfully")
                print(f"✅ Output: {result.get('output', '')[:100]}...")
            else:
                print(f"❌ AutoGPT test failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Test endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Test 4: Analysis endpoint
    print("\n4. Testing Text Analysis...")
    try:
        data = {
            'text': 'This is a sample company description for testing AutoGPT analysis.',
            'analysis_type': 'general',
            'model': 'mistral:latest'
        }
        response = requests.post(f"{base_url}/autogpt/analyze", data=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Text analysis completed successfully")
                print(f"✅ Analysis: {result.get('analysis', '')[:100]}...")
            else:
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Analysis endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    # Test 5: Research endpoint
    print("\n5. Testing Research Function...")
    try:
        data = {
            'research_topic': 'AI in healthcare',
            'company_name': 'Test Company',
            'industry': 'Healthcare',
            'model': 'mistral:latest'
        }
        response = requests.post(f"{base_url}/autogpt/research", data=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Research completed successfully")
                print(f"✅ Research: {result.get('research', '')[:100]}...")
            else:
                print(f"❌ Research failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Research endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Research error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 AutoGPT Control Panel Testing Complete!")

if __name__ == "__main__":
    test_autogpt_endpoints() 