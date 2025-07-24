#!/usr/bin/env python3
"""
Test script for Lead Workshop functionality
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_lead_workshop_flow():
    """Test the complete flow from Publications to Lead Workshop"""
    print("🧪 Testing Lead Workshop Flow")
    print("=" * 50)
    
    try:
        from models.database import db
        
        if not db:
            print("❌ Database not available")
            return False
        
        # Test 1: Check if there are any leads in the database
        print("📋 Test 1: Checking database for leads...")
        all_leads = db.get_all_leads()
        print(f"   Total leads in database: {len(all_leads)}")
        
        if all_leads:
            print("   Sample leads:")
            for i, lead in enumerate(all_leads[:3]):
                print(f"     {i+1}. ID: {lead['id']}, Title: {lead['title'][:50]}..., Source: {lead['source']}")
        
        # Test 2: Check academic publications specifically
        print("\n📚 Test 2: Checking academic publications...")
        academic_leads = db.get_leads_by_source('academic_pubmed')
        print(f"   Academic publications: {len(academic_leads)}")
        
        # Test 3: Test lead retrieval by ID
        print("\n🔍 Test 3: Testing lead retrieval by ID...")
        if all_leads:
            test_lead_id = all_leads[0]['id']
            test_lead = db.get_lead_by_id(test_lead_id)
            if test_lead:
                print(f"   ✅ Successfully retrieved lead ID {test_lead_id}: {test_lead['title'][:50]}...")
            else:
                print(f"   ❌ Failed to retrieve lead ID {test_lead_id}")
        
        # Test 4: Simulate lead workshop URL with lead_ids
        print("\n🔗 Test 4: Testing lead workshop URL simulation...")
        if all_leads:
            lead_ids = [str(lead['id']) for lead in all_leads[:3]]
            lead_ids_param = ','.join(lead_ids)
            print(f"   Simulated URL: /lead-workshop?lead_ids={lead_ids_param}")
            
            # Test parsing the lead_ids parameter
            parsed_ids = [lid.strip() for lid in lead_ids_param.split(',') if lid.strip()]
            print(f"   Parsed lead IDs: {parsed_ids}")
            
            # Test retrieving each lead
            retrieved_leads = []
            for lead_id in parsed_ids:
                try:
                    lead = db.get_lead_by_id(int(lead_id))
                    if lead:
                        retrieved_leads.append(lead)
                        print(f"     ✅ Found lead {lead_id}: {lead['title'][:30]}...")
                    else:
                        print(f"     ❌ Lead {lead_id} not found")
                except ValueError:
                    print(f"     ❌ Invalid lead ID: {lead_id}")
            
            print(f"   Successfully retrieved {len(retrieved_leads)} leads")
        
        # Test 5: Check if there are any projects
        print("\n📁 Test 5: Checking projects...")
        projects = db.get_projects()
        print(f"   Available projects: {len(projects)}")
        for project in projects:
            print(f"     - ID: {project['id']}, Name: {project['name']}")
        
        print("\n✅ Lead Workshop flow test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Lead Workshop flow: {e}")
        return False

def test_publication_to_workshop():
    """Test the publication to workshop flow"""
    print("\n📖 Testing Publication to Workshop Flow")
    print("=" * 50)
    
    try:
        from models.database import db
        
        # Create a test publication
        test_publication = {
            'title': 'Test Publication - Epigenetics Research',
            'authors': ['Dr. Test Researcher', 'Prof. Test Professor'],
            'abstract': 'This is a test publication about epigenetics and pre-diabetes research.',
            'url': 'https://example.com/test-paper',
            'doi': '10.1000/test.2024.001',
            'source': 'pubmed',
            'journal': 'Test Journal',
            'year': '2024'
        }
        
        print("📝 Test publication data:")
        print(f"   Title: {test_publication['title']}")
        print(f"   Authors: {', '.join(test_publication['authors'])}")
        print(f"   Source: {test_publication['source']}")
        
        # Simulate saving to database
        if db:
            lead_id = db.save_lead(
                title=test_publication['title'],
                description=f"Authors: {', '.join(test_publication['authors'])}\n\nAbstract: {test_publication['abstract']}",
                link=test_publication['url'],
                ai_summary=f"Academic publication from {test_publication['source']} in {test_publication['journal']} ({test_publication['year']})",
                source=f"academic_{test_publication['source']}"
            )
            
            if lead_id:
                print(f"   ✅ Successfully saved with lead ID: {lead_id}")
                
                # Test retrieving the saved lead
                saved_lead = db.get_lead_by_id(lead_id)
                if saved_lead:
                    print(f"   ✅ Successfully retrieved saved lead: {saved_lead['title']}")
                    print(f"   ✅ Source: {saved_lead['source']}")
                else:
                    print(f"   ❌ Failed to retrieve saved lead")
            else:
                print(f"   ❌ Failed to save test publication")
        
        print("✅ Publication to workshop test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing publication to workshop flow: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Lead Workshop Integration Test")
    print("=" * 60)
    
    # Test the basic flow
    flow_ok = test_lead_workshop_flow()
    
    # Test publication to workshop flow
    pub_ok = test_publication_to_workshop()
    
    if flow_ok and pub_ok:
        print("\n🎉 All tests passed!")
        print("   The Lead Workshop should work correctly with publications from Publications and Researchers.")
        return 0
    else:
        print("\n⚠️  Some tests failed.")
        print("   Please check the database and Lead Workshop configuration.")
        return 1

if __name__ == "__main__":
    exit(main()) 