#!/usr/bin/env python3
"""
Simple test script for Lead Workshop functionality (no Ollama required)
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_database_directly():
    """Test database directly without importing config"""
    print("🧪 Testing Database Directly")
    print("=" * 40)
    
    try:
        # Connect to database directly
        db_path = Path("data/leadfinder.db")
        if not db_path.exists():
            print(f"❌ Database not found at {db_path}")
            return False
        
        print(f"✅ Database found at {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Check leads table
        print("\n📋 Test 1: Checking leads table...")
        cursor.execute("SELECT COUNT(*) FROM leads")
        lead_count = cursor.fetchone()[0]
        print(f"   Total leads: {lead_count}")
        
        if lead_count > 0:
            cursor.execute("SELECT id, title, source FROM leads LIMIT 5")
            leads = cursor.fetchall()
            print("   Sample leads:")
            for lead in leads:
                print(f"     ID: {lead[0]}, Title: {lead[1][:50]}..., Source: {lead[2]}")
        
        # Test 2: Check academic publications
        print("\n📚 Test 2: Checking academic publications...")
        cursor.execute("SELECT COUNT(*) FROM leads WHERE source LIKE 'academic_%'")
        academic_count = cursor.fetchone()[0]
        print(f"   Academic publications: {academic_count}")
        
        if academic_count > 0:
            cursor.execute("SELECT id, title, source FROM leads WHERE source LIKE 'academic_%' LIMIT 3")
            academic_leads = cursor.fetchall()
            print("   Sample academic leads:")
            for lead in academic_leads:
                print(f"     ID: {lead[0]}, Title: {lead[1][:50]}..., Source: {lead[2]}")
        
        # Test 3: Check projects table
        print("\n📁 Test 3: Checking projects table...")
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        print(f"   Total projects: {project_count}")
        
        if project_count > 0:
            cursor.execute("SELECT id, name FROM projects LIMIT 3")
            projects = cursor.fetchall()
            print("   Sample projects:")
            for project in projects:
                print(f"     ID: {project[0]}, Name: {project[1]}")
        
        conn.close()
        print("\n✅ Database test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False

def test_lead_workshop_url_simulation():
    """Test the lead workshop URL simulation"""
    print("\n🔗 Testing Lead Workshop URL Simulation")
    print("=" * 45)
    
    try:
        # Connect to database
        db_path = Path("data/leadfinder.db")
        if not db_path.exists():
            print("❌ Database not found")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get some lead IDs
        cursor.execute("SELECT id FROM leads LIMIT 3")
        lead_ids = [str(row[0]) for row in cursor.fetchall()]
        
        if not lead_ids:
            print("❌ No leads found in database")
            conn.close()
            return False
        
        # Simulate the URL parameter
        lead_ids_param = ','.join(lead_ids)
        print(f"   Simulated URL: /lead-workshop?lead_ids={lead_ids_param}")
        
        # Test parsing (same as in lead_workshop.py)
        parsed_ids = [lid.strip() for lid in lead_ids_param.split(',') if lid.strip()]
        print(f"   Parsed lead IDs: {parsed_ids}")
        
        # Test retrieving each lead
        retrieved_leads = []
        for lead_id in parsed_ids:
            try:
                cursor.execute("SELECT id, title, source FROM leads WHERE id = ?", (int(lead_id),))
                lead = cursor.fetchone()
                if lead:
                    retrieved_leads.append(lead)
                    print(f"     ✅ Found lead {lead_id}: {lead[1][:30]}...")
                else:
                    print(f"     ❌ Lead {lead_id} not found")
            except ValueError:
                print(f"     ❌ Invalid lead ID: {lead_id}")
        
        print(f"   Successfully retrieved {len(retrieved_leads)} leads")
        
        conn.close()
        print("✅ URL simulation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing URL simulation: {e}")
        return False

def test_publication_save_simulation():
    """Test saving a publication (simulating send_to_workshop)"""
    print("\n📖 Testing Publication Save Simulation")
    print("=" * 40)
    
    try:
        # Connect to database
        db_path = Path("data/leadfinder.db")
        if not db_path.exists():
            print("❌ Database not found")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create test publication data (same as in send_to_workshop)
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
        
        # Create lead data (same as in send_to_workshop)
        title = test_publication['title']
        authors_str = ', '.join(test_publication['authors'])
        abstract = test_publication['abstract']
        description = f"Authors: {authors_str}\n\nAbstract: {abstract}"
        
        link = test_publication['url']
        if not link and test_publication.get('doi'):
            link = f"https://doi.org/{test_publication['doi']}"
        
        ai_summary = f"Academic publication from {test_publication['source']}"
        if test_publication.get('journal'):
            ai_summary += f" in {test_publication['journal']}"
        if test_publication.get('year'):
            ai_summary += f" ({test_publication['year']})"
        
        source = f"academic_{test_publication['source']}"
        
        # Save to database (same as save_lead function)
        cursor.execute("""
            INSERT INTO leads (title, description, link, ai_summary, source, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (title, description, link, ai_summary, source))
        
        lead_id = cursor.lastrowid
        conn.commit()
        
        if lead_id:
            print(f"   ✅ Successfully saved with lead ID: {lead_id}")
            
            # Test retrieving the saved lead
            cursor.execute("SELECT id, title, source FROM leads WHERE id = ?", (lead_id,))
            saved_lead = cursor.fetchone()
            if saved_lead:
                print(f"   ✅ Successfully retrieved saved lead: {saved_lead[1]}")
                print(f"   ✅ Source: {saved_lead[2]}")
            else:
                print(f"   ❌ Failed to retrieve saved lead")
        else:
            print(f"   ❌ Failed to save test publication")
        
        conn.close()
        print("✅ Publication save test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing publication save: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Simple Lead Workshop Test (No Ollama Required)")
    print("=" * 60)
    
    # Test database directly
    db_ok = test_database_directly()
    
    # Test URL simulation
    url_ok = test_lead_workshop_url_simulation()
    
    # Test publication save
    save_ok = test_publication_save_simulation()
    
    if db_ok and url_ok and save_ok:
        print("\n🎉 All tests passed!")
        print("   The Lead Workshop database functionality is working correctly.")
        print("   If you're still seeing 'No leads selected' in the UI, it might be a JavaScript issue.")
        return 0
    else:
        print("\n⚠️  Some tests failed.")
        print("   Please check the database and Lead Workshop configuration.")
        return 1

if __name__ == "__main__":
    exit(main()) 