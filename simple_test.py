#!/usr/bin/env python3
"""
Simple test for enhanced leads
"""
import sys
import os

def test_simple():
    try:
        from models.database import db
        
        # Get all leads
        leads = db.get_all_leads()
        print(f"✅ Found {len(leads)} leads in database")
        
        if leads:
            # Show first lead
            first_lead = leads[0]
            print(f"📋 First lead:")
            print(f"   ID: {first_lead.get('id')}")
            print(f"   Title: {first_lead.get('title')}")
            print(f"   Company: {first_lead.get('company')}")
            print(f"   Contact: {first_lead.get('contact_name')}")
            print(f"   Status: {first_lead.get('contact_status')}")
            print(f"   Tags: {first_lead.get('tags')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Enhanced Leads Test")
    success = test_simple()
    sys.exit(0 if success else 1) 