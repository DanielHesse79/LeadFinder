#!/usr/bin/env python3
"""
Simple database connection test
"""
import sys
import os

def test_database_connection():
    """Test basic database connectivity"""
    try:
        from models.database import db
        
        print("🔍 Testing database connection...")
        
        # Test getting all leads
        leads = db.get_all_leads()
        print(f"✅ Successfully retrieved {len(leads)} leads")
        
        if leads:
            first_lead = leads[0]
            print(f"📋 Sample lead data:")
            print(f"   ID: {first_lead.get('id')}")
            print(f"   Title: {first_lead.get('title')}")
            print(f"   Company: {first_lead.get('company')}")
            print(f"   Contact: {first_lead.get('contact_name')}")
            print(f"   Status: {first_lead.get('contact_status')}")
            print(f"   Tags: {first_lead.get('tags')}")
        
        # Test getting lead count
        count = db.get_lead_count()
        print(f"📊 Total leads in database: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pool_stats():
    """Test connection pool statistics"""
    try:
        from models.database_pool import get_db_pool
        
        pool = get_db_pool()
        stats = pool.get_pool_stats()
        
        print("🔧 Connection pool statistics:")
        print(f"   Pool size: {stats['pool_size']}")
        print(f"   Max connections: {stats['max_connections']}")
        print(f"   Active connections: {stats['active_connections']}")
        print(f"   Total connections created: {stats['total_connections_created']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pool stats test failed: {e}")
        return False

def main():
    """Run all database tests"""
    print("🧪 Database Connection Test")
    print("=" * 40)
    
    success = True
    
    # Test basic connection
    if not test_database_connection():
        success = False
    
    print()
    
    # Test pool statistics
    if not test_pool_stats():
        success = False
    
    print()
    print("=" * 40)
    
    if success:
        print("✅ All database tests passed!")
    else:
        print("❌ Some database tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 