#!/usr/bin/env python3
"""
Migration script to add new columns to the leads table
"""
import sqlite3
import os
from pathlib import Path

def migrate_leads_table():
    """Add new columns to the leads table"""
    try:
        # Get database path
        from config import DATABASE_PATH
        db_path = DATABASE_PATH
        
        print(f"📁 Database path: {db_path}")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current table structure
        cursor.execute("PRAGMA table_info(leads)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Current columns: {columns}")
        
        # Define new columns to add
        new_columns = [
            ('tags', 'TEXT'),
            ('company', 'TEXT'),
            ('institution', 'TEXT'),
            ('contact_name', 'TEXT'),
            ('contact_email', 'TEXT'),
            ('contact_phone', 'TEXT'),
            ('contact_linkedin', 'TEXT'),
            ('contact_status', 'TEXT DEFAULT "not_contacted"'),
            ('notes', 'TEXT'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        # Add new columns if they don't exist
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE leads ADD COLUMN {column_name} {column_type}")
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Column {column_name} might already exist: {e}")
            else:
                print(f"ℹ️  Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        
        # Verify the new structure
        cursor.execute("PRAGMA table_info(leads)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Final columns: {final_columns}")
        
        # Test inserting a record with new fields
        test_lead = {
            'title': 'Migration Test Lead',
            'description': 'This is a test lead created during migration',
            'link': 'https://example.com',
            'ai_summary': 'Test AI summary',
            'source': 'migration',
            'tags': 'test, migration',
            'company': 'Test Company',
            'institution': 'Test University',
            'contact_name': 'Test Contact',
            'contact_email': 'test@example.com',
            'contact_phone': '+1234567890',
            'contact_linkedin': 'https://linkedin.com/in/test',
            'contact_status': 'not_contacted',
            'notes': 'Test note'
        }
        
        # Insert test record
        cursor.execute('''
            INSERT INTO leads (title, description, link, ai_summary, source, tags, 
                             company, institution, contact_name, contact_email, 
                             contact_phone, contact_linkedin, contact_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            test_lead['title'], test_lead['description'], test_lead['link'],
            test_lead['ai_summary'], test_lead['source'], test_lead['tags'],
            test_lead['company'], test_lead['institution'], test_lead['contact_name'],
            test_lead['contact_email'], test_lead['contact_phone'], test_lead['contact_linkedin'],
            test_lead['contact_status'], test_lead['notes']
        ))
        
        test_id = cursor.lastrowid
        print(f"✅ Successfully inserted test lead with ID: {test_id}")
        
        # Verify the record
        cursor.execute("SELECT * FROM leads WHERE id = ?", (test_id,))
        result = cursor.fetchone()
        if result:
            print("✅ Test record verified successfully")
        else:
            print("❌ Failed to verify test record")
        
        conn.close()
        print("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting leads table migration...")
    success = migrate_leads_table()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        exit(1) 