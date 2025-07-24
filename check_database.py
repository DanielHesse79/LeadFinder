#!/usr/bin/env python3
"""
Check and fix database structure
"""

import sqlite3
from pathlib import Path

def check_database():
    """Check database structure"""
    print("🔍 Checking Database Structure")
    print("=" * 40)
    
    db_path = Path("data/leadfinder.db")
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"📋 Existing tables: {tables}")
    
    # Check if projects table exists
    if 'projects' not in tables:
        print("❌ Projects table missing!")
        print("   This is likely why Lead Workshop shows 'No leads selected'")
        return False
    
    # Check table structures
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"\n📊 Table '{table}' columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
    
    conn.close()
    return True

def create_missing_tables():
    """Create missing tables"""
    print("\n🔧 Creating Missing Tables")
    print("=" * 30)
    
    db_path = Path("data/leadfinder.db")
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if projects table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
    if not cursor.fetchone():
        print("📁 Creating projects table...")
        cursor.execute("""
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create a default project
        cursor.execute("""
            INSERT INTO projects (name, description) 
            VALUES ('Default Project', 'Default project for lead analysis')
        """)
        
        print("✅ Projects table created with default project")
    else:
        print("✅ Projects table already exists")
    
    # Check if lead_analyses table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lead_analyses'")
    if not cursor.fetchone():
        print("📊 Creating lead_analyses table...")
        cursor.execute("""
            CREATE TABLE lead_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                lead_id INTEGER NOT NULL,
                relevancy_score INTEGER DEFAULT 3,
                ai_analysis TEXT,
                key_opinion_leaders TEXT,
                contact_info TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        """)
        print("✅ Lead analyses table created")
    else:
        print("✅ Lead analyses table already exists")
    
    conn.commit()
    conn.close()
    print("\n✅ Database structure check completed!")
    return True

def test_lead_workshop_after_fix():
    """Test if Lead Workshop works after fixing database"""
    print("\n🧪 Testing Lead Workshop After Fix")
    print("=" * 40)
    
    db_path = Path("data/leadfinder.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check projects
    cursor.execute("SELECT COUNT(*) FROM projects")
    project_count = cursor.fetchone()[0]
    print(f"📁 Projects: {project_count}")
    
    # Check academic leads
    cursor.execute("SELECT COUNT(*) FROM leads WHERE source LIKE 'academic_%'")
    academic_count = cursor.fetchone()[0]
    print(f"📚 Academic leads: {academic_count}")
    
    # Test lead retrieval
    if academic_count > 0:
        cursor.execute("SELECT id, title FROM leads WHERE source LIKE 'academic_%' LIMIT 3")
        leads = cursor.fetchall()
        print("   Sample academic leads:")
        for lead in leads:
            print(f"     ID: {lead[0]}, Title: {lead[1][:50]}...")
    
    conn.close()
    print("✅ Lead Workshop should now work correctly!")

def main():
    """Main function"""
    print("🔧 Database Structure Check and Fix")
    print("=" * 50)
    
    # Check current structure
    if not check_database():
        print("\n⚠️  Database structure issues found!")
    
    # Create missing tables
    create_missing_tables()
    
    # Test after fix
    test_lead_workshop_after_fix()
    
    print("\n🎉 Database fix completed!")
    print("   Lead Workshop should now work correctly with publications from Publications and Researchers.")

if __name__ == "__main__":
    main() 