#!/usr/bin/env python3
"""
Test script to verify that AutoGPT now properly extracts names from text
"""

import requests
import json
import time

def test_name_extraction():
    """Test if AutoGPT properly extracts names from text"""
    
    print("🧪 Testing AutoGPT name extraction functionality...")
    
    # Test data with names
    test_text = """
    Dr. Sarah Johnson, CEO of TechCorp Solutions, announced today that the company 
    has hired John Smith as the new CTO. The announcement was made during a press 
    conference where Dr. Johnson was joined by Maria Rodriguez, VP of Engineering, 
    and David Chen, Head of Product Development.
    
    "We're excited to have John join our team," said Dr. Johnson. "His expertise 
    in AI and machine learning will be invaluable as we expand our research 
    division under the leadership of Prof. Michael Brown."
    """
    
    # Test prompt that should trigger name extraction
    test_prompt = f"""
    Analyze the following text and extract all person names mentioned:
    
    {test_text}
    
    Please provide:
    1. All person names mentioned (with titles and organizations)
    2. Brief summary of the content
    3. Relevance assessment
    """
    
    try:
        # Test AutoGPT integration directly
        print("📝 Testing AutoGPT with name extraction prompt...")
        
        # We'll test this by making a request to the search endpoint with AI analysis
        search_data = {
            "query": "Dr. Sarah Johnson TechCorp Solutions",
            "sources": ["google"],
            "num_results": 3,
            "research_question": "Find information about Dr. Sarah Johnson and TechCorp Solutions",
            "use_ai_analysis": True
        }
        
        response = requests.post(
            "http://localhost:5050/search_ajax",
            json=search_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search request successful")
            
            if result.get('success'):
                leads = result.get('leads', [])
                print(f"📊 Found {len(leads)} leads")
                
                # Check if any leads have AI analysis with name extraction
                for i, lead in enumerate(leads[:3], 1):
                    print(f"\n🔍 Lead {i}:")
                    print(f"   Title: {lead.get('title', 'N/A')}")
                    print(f"   AI Summary: {lead.get('ai_summary', 'No AI analysis')[:200]}...")
                    
                    # Check if the AI summary mentions names
                    ai_summary = lead.get('ai_summary', '').lower()
                    if any(name in ai_summary for name in ['dr.', 'sarah', 'johnson', 'john', 'smith', 'maria', 'rodriguez', 'david', 'chen']):
                        print("   ✅ AI analysis appears to include name extraction")
                    else:
                        print("   ⚠️  AI analysis may not include name extraction")
            else:
                print(f"❌ Search failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "="*50)
    print("🎯 Manual Test Instructions:")
    print("1. Go to http://localhost:5050")
    print("2. Enter a search query with person names")
    print("3. Check 'Enable AutoGPT Analysis'")
    print("4. Submit the search")
    print("5. Check if the AI analysis includes extracted names")
    print("="*50)

def test_lead_workshop_analysis():
    """Test lead workshop analysis with name extraction"""
    
    print("\n🧪 Testing Lead Workshop analysis with name extraction...")
    
    try:
        # Test the lead workshop analysis endpoint
        test_data = {
            "project_id": 1,
            "leads": [
                {
                    "id": 1,
                    "title": "Dr. Sarah Johnson appointed CEO of TechCorp Solutions",
                    "description": "TechCorp Solutions announced today that Dr. Sarah Johnson has been appointed as the new CEO. She will be joined by John Smith as CTO and Maria Rodriguez as VP of Engineering.",
                    "link": "https://example.com/article1",
                    "source": "test"
                }
            ]
        }
        
        response = requests.post(
            "http://localhost:5050/lead-workshop/analyze-leads",
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Lead workshop analysis request successful")
            
            if result.get('success'):
                ai_response = result.get('ai_response', '')
                print(f"📝 AI Response length: {len(ai_response)} characters")
                
                # Check if the AI response includes name extraction
                if 'PEOPLE:' in ai_response or 'people' in ai_response.lower():
                    print("✅ AI analysis includes PEOPLE section (name extraction)")
                else:
                    print("⚠️  AI analysis may not include name extraction")
                    
                # Show a snippet of the AI response
                print(f"📄 AI Response snippet: {ai_response[:300]}...")
            else:
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 LeadFinder AutoGPT Name Extraction Test")
    print("="*50)
    
    # Test 1: Search with AI analysis
    test_name_extraction()
    
    # Test 2: Lead workshop analysis
    test_lead_workshop_analysis()
    
    print("\n✅ Test completed!")
    print("\n💡 To manually test:")
    print("1. Open http://localhost:5050 in your browser")
    print("2. Try searching for content with person names")
    print("3. Enable AutoGPT analysis")
    print("4. Check if names are extracted in the AI analysis") 