#!/usr/bin/env python3
"""
Database Connection Pool Demonstration

This script demonstrates the usage and benefits of the database connection pool
in the LeadFinder application.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor
from models.database_pool import get_db_pool, close_db_pool
from models.database import db

def demonstrate_basic_usage():
    """Demonstrate basic connection pool usage"""
    print("🔧 Basic Connection Pool Usage")
    print("-" * 40)
    
    pool = get_db_pool()
    
    # Example 1: Simple query
    print("1. Simple SELECT query:")
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as lead_count FROM leads")
        result = cursor.fetchone()
        print(f"   Total leads in database: {result[0]}")
    
    # Example 2: Insert operation
    print("\n2. INSERT operation:")
    test_title = f"Demo Lead {int(time.time())}"
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leads (title, description, link, ai_summary, source)
            VALUES (?, ?, ?, ?, ?)
        """, (test_title, "Demo description", "https://example.com", "Demo AI summary", "demo"))
        lead_id = cursor.lastrowid
        conn.commit()
        print(f"   Inserted lead with ID: {lead_id}")
    
    # Example 3: Update operation
    print("\n3. UPDATE operation:")
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE leads SET description = ? WHERE id = ?", 
                      ("Updated demo description", lead_id))
        conn.commit()
        print(f"   Updated lead {lead_id}")
    
    # Example 4: Delete operation
    print("\n4. DELETE operation:")
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()
        print(f"   Deleted lead {lead_id}")
    
    print("\n✅ Basic usage demonstration completed")

def demonstrate_performance_comparison():
    """Demonstrate performance difference between pooled and direct connections"""
    print("\n⚡ Performance Comparison")
    print("-" * 40)
    
    def time_direct_connections():
        """Time using direct connections"""
        start_time = time.time()
        for i in range(50):
            with db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM leads")
                cursor.fetchone()
        return time.time() - start_time
    
    def time_pooled_connections():
        """Time using connection pool"""
        start_time = time.time()
        pool = get_db_pool()
        for i in range(50):
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM leads")
                cursor.fetchone()
        return time.time() - start_time
    
    # Run performance tests
    print("Running performance tests...")
    direct_time = time_direct_connections()
    pooled_time = time_pooled_connections()
    
    print(f"Direct connections: {direct_time:.3f} seconds")
    print(f"Pooled connections: {pooled_time:.3f} seconds")
    
    if pooled_time < direct_time:
        improvement = ((direct_time - pooled_time) / direct_time) * 100
        print(f"Performance improvement: {improvement:.1f}%")
    else:
        print("Performance is similar (pool overhead vs connection reuse)")

def demonstrate_concurrent_access():
    """Demonstrate concurrent access to the connection pool"""
    print("\n🔄 Concurrent Access Demonstration")
    print("-" * 40)
    
    def worker(worker_id):
        """Worker function for concurrent testing"""
        try:
            pool = get_db_pool()
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM leads")
                result = cursor.fetchone()
                return f"Worker {worker_id}: {result[0]} leads found"
        except Exception as e:
            return f"Worker {worker_id} failed: {e}"
    
    # Run concurrent workers
    num_workers = 10
    print(f"Running {num_workers} concurrent workers...")
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(worker, i) for i in range(num_workers)]
        results = [future.result() for future in futures]
    
    # Display results
    for result in results:
        print(f"   {result}")
    
    success_count = sum(1 for result in results if "failed" not in result)
    print(f"\n✅ {success_count}/{num_workers} workers completed successfully")

def demonstrate_pool_statistics():
    """Demonstrate connection pool statistics"""
    print("\n📊 Connection Pool Statistics")
    print("-" * 40)
    
    pool = get_db_pool()
    
    # Get initial stats
    initial_stats = pool.get_pool_stats()
    print("Initial pool statistics:")
    for key, value in initial_stats.items():
        print(f"   {key}: {value}")
    
    # Use some connections
    print("\nUsing connections...")
    for i in range(5):
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            print(f"   Used connection {i+1}")
    
    # Get updated stats
    updated_stats = pool.get_pool_stats()
    print("\nUpdated pool statistics:")
    for key, value in updated_stats.items():
        print(f"   {key}: {value}")
    
    # Show pool efficiency
    if updated_stats['total_connections_created'] > 0:
        efficiency = (updated_stats['pool_size'] / updated_stats['total_connections_created']) * 100
        print(f"\nPool efficiency: {efficiency:.1f}% (connections reused)")

def demonstrate_error_handling():
    """Demonstrate error handling in the connection pool"""
    print("\n🛡️ Error Handling Demonstration")
    print("-" * 40)
    
    pool = get_db_pool()
    
    # Example 1: Invalid SQL (should be handled gracefully)
    print("1. Testing invalid SQL handling:")
    try:
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM non_existent_table")
    except Exception as e:
        print(f"   ✅ Error handled gracefully: {type(e).__name__}")
    
    # Example 2: Connection pool exhaustion (if we try to use too many)
    print("\n2. Testing connection pool limits:")
    try:
        # Try to use more connections than the pool size
        connections = []
        for i in range(15):  # More than default pool size
            conn = pool.get_connection()
            connections.append(conn)
            print(f"   Got connection {i+1}")
    except Exception as e:
        print(f"   ✅ Pool limit enforced: {type(e).__name__}")
    finally:
        # Clean up any connections we got
        for conn in connections:
            try:
                conn.__exit__(None, None, None)
            except:
                pass
    
    print("\n✅ Error handling demonstration completed")

def main():
    """Run all demonstrations"""
    print("🚀 Database Connection Pool Demonstration")
    print("=" * 60)
    
    try:
        # Run demonstrations
        demonstrate_basic_usage()
        demonstrate_performance_comparison()
        demonstrate_concurrent_access()
        demonstrate_pool_statistics()
        demonstrate_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 All demonstrations completed successfully!")
        print("\nKey Benefits of Connection Pooling:")
        print("✅ Improved performance through connection reuse")
        print("✅ Better resource management")
        print("✅ Thread-safe concurrent access")
        print("✅ Automatic connection health checking")
        print("✅ Graceful error handling")
        print("✅ Configurable pool size and timeouts")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
    finally:
        # Clean up
        close_db_pool()
        print("\n🧹 Connection pool cleaned up")

if __name__ == "__main__":
    main() 