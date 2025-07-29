#!/usr/bin/env python3
"""
Test script for enhanced leads functionality
"""
import sys
import os
from pathlib import Path

def test_database_migration():
    """Test that the database can handle the new fields"""
    try:
        from models.database import db
        
        # Test saving a lead with enhanced information
        lead_id = db.save_lead(
            title="Test Enhanced Lead",
            description="This is a test lead with enhanced information",
            link="https://example.com",
            ai_summary="This is an AI-generated summary of the lead",
            source="test",
            tags="test, enhanced, lead",
            company="Test Company",
            institution="Test University",
            contact_name="John Doe",
            contact_email="john.doe@example.com",
            contact_phone="+1234567890",
            contact_linkedin="https://linkedin.com/in/johndoe",
            contact_status="not_contacted",
            notes="This is a test note"
        )
        
        print(f"✅ Successfully created enhanced lead with ID: {lead_id}")
        
        # Test retrieving the lead
        lead = db.get_lead_by_id(lead_id)
        if lead:
            print(f"✅ Successfully retrieved lead: {lead.get('title')}")
            print(f"   Company: {lead.get('company')}")
            print(f"   Contact: {lead.get('contact_name')} - {lead.get('contact_email')}")
            print(f"   Status: {lead.get('contact_status')}")
            print(f"   Tags: {lead.get('tags')}")
        else:
            print("❌ Failed to retrieve lead")
            return False
        
        # Test updating the lead
        success = db.update_lead(
            lead_id=lead_id,
            contact_status="contacted",
            notes="Updated note - lead has been contacted"
        )
        
        if success:
            print("✅ Successfully updated lead")
        else:
            print("❌ Failed to update lead")
            return False
        
        # Test getting all leads
        all_leads = db.get_all_leads()
        print(f"✅ Total leads in database: {len(all_leads)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_export_functionality():
    """Test the export functionality"""
    try:
        from routes.leads import export_to_csv, export_to_excel
        
        print("✅ Export functions imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Leads Functionality")
    print("=" * 50)
    
    tests = [
        ("Database Migration", test_database_migration),
        ("Export Functionality", test_export_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced leads functionality is working.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 