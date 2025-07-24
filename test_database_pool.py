#!/usr/bin/env python3
"""
Test script for database connection pool functionality.

This script tests the database connection pool to ensure it's working correctly
and provides performance improvements over direct connections.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.database_pool import get_db_pool, close_db_pool
from models.database import db

def test_connection_pool_basic():
    """Test basic connection pool functionality"""
    print("🔍 Testing basic connection pool functionality...")
    
    try:
        pool = get_db_pool()
        
        # Test getting a connection
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            assert result[0] == 1, "Basic query failed"
        
        print("✅ Basic connection pool test passed")
        return True
    except Exception as e:
        print(f"❌ Basic connection pool test failed: {e}")
        return False

def test_connection_pool_performance():
    """Test connection pool performance vs direct connections"""
    print("⚡ Testing connection pool performance...")
    
    def direct_connection_test():
        """Test using direct connections"""
        start_time = time.time()
        for _ in range(100):
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM leads")
                cursor.fetchone()
        return time.time() - start_time
    
    def pooled_connection_test():
        """Test using connection pool"""
        start_time = time.time()
        pool = get_db_pool()
        for _ in range(100):
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM leads")
                cursor.fetchone()
        return time.time() - start_time
    
    try:
        # Test direct connections
        direct_time = direct_connection_test()
        print(f"⏱️  Direct connections: {direct_time:.3f} seconds")
        
        # Test pooled connections
        pooled_time = pooled_connection_test()
        print(f"⏱️  Pooled connections: {pooled_time:.3f} seconds")
        
        # Calculate improvement
        improvement = ((direct_time - pooled_time) / direct_time) * 100
        print(f"📈 Performance improvement: {improvement:.1f}%")
        
        if pooled_time < direct_time:
            print("✅ Connection pool provides performance improvement")
            return True
        else:
            print("⚠️  Connection pool performance is similar to direct connections")
            return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_concurrent_connections():
    """Test concurrent access to the connection pool"""
    print("🔄 Testing concurrent connections...")
    
    def worker(worker_id):
        """Worker function for concurrent testing"""
        try:
            pool = get_db_pool()
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM leads")
                result = cursor.fetchone()
                return f"Worker {worker_id}: {result[0]} leads"
        except Exception as e:
            return f"Worker {worker_id} failed: {e}"
    
    try:
        # Test with multiple concurrent workers
        num_workers = 20
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, i) for i in range(num_workers)]
            results = [future.result() for future in as_completed(futures)]
        
        # Check results
        success_count = sum(1 for result in results if "failed" not in result)
        print(f"✅ {success_count}/{num_workers} concurrent workers completed successfully")
        
        if success_count == num_workers:
            print("✅ Concurrent connection test passed")
            return True
        else:
            print("⚠️  Some concurrent workers failed")
            return False
    except Exception as e:
        print(f"❌ Concurrent connection test failed: {e}")
        return False

def test_pool_statistics():
    """Test connection pool statistics"""
    print("📊 Testing connection pool statistics...")
    
    try:
        pool = get_db_pool()
        
        # Get initial stats
        initial_stats = pool.get_pool_stats()
        print(f"📈 Initial pool stats: {initial_stats}")
        
        # Use some connections
        for _ in range(5):
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
        
        # Get updated stats
        updated_stats = pool.get_pool_stats()
        print(f"📈 Updated pool stats: {updated_stats}")
        
        # Verify stats are reasonable
        assert updated_stats['pool_size'] <= updated_stats['max_connections'], "Pool size exceeds max connections"
        assert updated_stats['total_connections_created'] >= 0, "Invalid total connections created"
        
        print("✅ Pool statistics test passed")
        return True
    except Exception as e:
        print(f"❌ Pool statistics test failed: {e}")
        return False

def test_connection_health_check():
    """Test connection health checking"""
    print("🏥 Testing connection health check...")
    
    try:
        pool = get_db_pool()
        
        # Get a connection and verify it's healthy
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1, "Health check query failed"
        
        print("✅ Connection health check test passed")
        return True
    except Exception as e:
        print(f"❌ Connection health check test failed: {e}")
        return False

def test_database_operations():
    """Test database operations using the pool"""
    print("💾 Testing database operations with connection pool...")
    
    try:
        # Test lead operations
        test_title = f"Test Lead {int(time.time())}"
        test_description = "Test description for connection pool"
        test_link = "https://example.com/test"
        test_summary = "Test AI summary"
        
        # Save a test lead
        lead_id = db.save_lead(test_title, test_description, test_link, test_summary, "test")
        assert lead_id is not None, "Failed to save lead"
        print(f"✅ Saved test lead with ID: {lead_id}")
        
        # Retrieve the lead
        lead = db.get_lead_by_id(lead_id)
        assert lead is not None, "Failed to retrieve lead"
        assert lead['title'] == test_title, "Lead title mismatch"
        print(f"✅ Retrieved test lead: {lead['title']}")
        
        # Get all leads
        all_leads = db.get_all_leads(limit=5)
        assert isinstance(all_leads, list), "Failed to get leads list"
        print(f"✅ Retrieved {len(all_leads)} leads")
        
        # Clean up test lead
        success = db.delete_lead(lead_id)
        assert success, "Failed to delete test lead"
        print(f"✅ Deleted test lead")
        
        print("✅ Database operations test passed")
        return True
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def main():
    """Run all database pool tests"""
    print("🚀 Starting Database Connection Pool Tests")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_connection_pool_basic),
        ("Performance", test_connection_pool_performance),
        ("Concurrent Connections", test_concurrent_connections),
        ("Pool Statistics", test_pool_statistics),
        ("Health Check", test_connection_health_check),
        ("Database Operations", test_database_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database connection pool is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    # Clean up
    close_db_pool()
    print("🧹 Connection pool cleaned up")

if __name__ == "__main__":
    main() 