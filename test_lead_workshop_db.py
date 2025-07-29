#!/usr/bin/env python3
"""
Test Lead Workshop database functionality
"""
import sys
import os

def test_lead_workshop_db():
    """Test Lead Workshop database operations"""
    try:
        from models.database import db
        
        print("🔍 Testing Lead Workshop database functionality...")
        
        # Test getting projects
        projects = db.get_projects()
        print(f"✅ Found {len(projects)} projects")
        
        if projects:
            first_project = projects[0]
            print(f"📋 Sample project:")
            print(f"   ID: {first_project.get('id')}")
            print(f"   Name: {first_project.get('name')}")
            print(f"   Description: {first_project.get('description')}")
        
        # Test getting leads
        leads = db.get_all_leads(limit=5)
        print(f"✅ Found {len(leads)} leads (limited to 5)")
        
        if leads:
            first_lead = leads[0]
            print(f"📋 Sample lead:")
            print(f"   ID: {first_lead.get('id')}")
            print(f"   Title: {first_lead.get('title')}")
            print(f"   Source: {first_lead.get('source')}")
        
        # Test getting lead by ID
        if leads:
            lead_id = leads[0]['id']
            lead = db.get_lead_by_id(lead_id)
            if lead:
                print(f"✅ Successfully retrieved lead by ID: {lead_id}")
            else:
                print(f"❌ Failed to retrieve lead by ID: {lead_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lead Workshop database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_project_creation():
    """Test project creation functionality"""
    try:
        from models.database import db
        
        print("🔍 Testing project creation...")
        
        # Create a test project
        project_id = db.create_project("Test Project", "Test Description")
        
        if project_id:
            print(f"✅ Successfully created project with ID: {project_id}")
            
            # Get the project
            project = db.get_project(project_id)
            if project:
                print(f"✅ Successfully retrieved created project")
                print(f"   Name: {project.get('name')}")
                print(f"   Description: {project.get('description')}")
            else:
                print(f"❌ Failed to retrieve created project")
            
            return True
        else:
            print("❌ Failed to create project")
            return False
        
    except Exception as e:
        print(f"❌ Project creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all Lead Workshop database tests"""
    print("🧪 Lead Workshop Database Test")
    print("=" * 40)
    
    success = True
    
    # Test basic database functionality
    if not test_lead_workshop_db():
        success = False
    
    print()
    
    # Test project creation
    if not test_project_creation():
        success = False
    
    print()
    print("=" * 40)
    
    if success:
        print("✅ All Lead Workshop database tests passed!")
    else:
        print("❌ Some Lead Workshop database tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 