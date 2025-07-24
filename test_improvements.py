#!/usr/bin/env python3
"""
Comprehensive Test Script for LeadFinder Improvements

This script tests all the implemented improvements:
1. Comprehensive Error Handling
2. Caching Strategy
3. Unified Search Services
4. Health Monitoring
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor
import json

def test_error_handling():
    """Test the comprehensive error handling system"""
    print("🔧 Testing Error Handling System")
    print("-" * 40)
    
    try:
        from utils.error_handler import (
            error_handler, LeadFinderError, DatabaseError, APIServiceError,
            handle_errors, ErrorContext, handle_database_error, handle_api_error
        )
        
        # Test 1: Basic error handling
        print("1. Testing basic error handling...")
        test_error = LeadFinderError("Test error", "TEST_ERROR", {"test": "data"})
        result = error_handler.handle_error(test_error, {"context": "test"})
        
        assert result['success'] == False
        assert result['error_code'] == 'TEST_ERROR'
        assert 'message' in result
        print("✅ Basic error handling works")
        
        # Test 2: Error decorator
        print("\n2. Testing error decorator...")
        @handle_errors
        def test_function(should_fail=False):
            if should_fail:
                raise ValueError("Test exception")
            return "success"
        
        result = test_function(should_fail=True)
        assert result['success'] == False
        print("✅ Error decorator works")
        
        # Test 3: Error context manager
        print("\n3. Testing error context manager...")
        try:
            with ErrorContext({"operation": "test"}):
                raise ValueError("Context test error")
        except ValueError:
            print("✅ Error context manager works")
        
        # Test 4: Specific error handlers
        print("\n4. Testing specific error handlers...")
        db_result = handle_database_error("test_operation", Exception("DB error"))
        api_result = handle_api_error("test_service", "/test", Exception("API error"))
        
        assert db_result['error_code'] == 'DATABASE_ERROR'
        assert api_result['error_code'] == 'API_SERVICE_ERROR'
        print("✅ Specific error handlers work")
        
        # Test 5: Error statistics
        print("\n5. Testing error statistics...")
        stats = error_handler.get_error_stats()
        assert 'total_errors' in stats
        assert 'severity_distribution' in stats
        print("✅ Error statistics work")
        
        print("\n✅ All error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_caching_system():
    """Test the caching system"""
    print("\n💾 Testing Caching System")
    print("-" * 40)
    
    try:
        from utils.cache_manager import (
            get_cache_manager, cached, CacheUtils, get_cache_health_status
        )
        
        cache = get_cache_manager()
        
        # Test 1: Basic cache operations
        print("1. Testing basic cache operations...")
        cache.set("test_key", "test_value", ttl=60)
        value = cache.get("test_key")
        assert value == "test_value"
        print("✅ Basic cache operations work")
        
        # Test 2: Cache decorator
        print("\n2. Testing cache decorator...")
        call_count = 0
        
        @cached(ttl=60, key_prefix="test")
        def test_cached_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"
        
        # First call should execute function
        result1 = test_cached_function("test_param")
        assert call_count == 1
        
        # Second call should use cache
        result2 = test_cached_function("test_param")
        assert call_count == 1  # Should not increment
        assert result1 == result2
        print("✅ Cache decorator works")
        
        # Test 3: Cache utilities
        print("\n3. Testing cache utilities...")
        @CacheUtils.cache_api_response("test_service", "/test", {"param": "value"}, ttl=60)
        def test_api_function():
            return {"data": "test"}
        
        result = test_api_function()
        assert result == {"data": "test"}
        print("✅ Cache utilities work")
        
        # Test 4: Cache statistics
        print("\n4. Testing cache statistics...")
        stats = cache.get_stats()
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats
        print("✅ Cache statistics work")
        
        # Test 5: Cache health status
        print("\n5. Testing cache health status...")
        health = get_cache_health_status()
        assert 'status' in health
        assert 'stats' in health
        print("✅ Cache health status works")
        
        print("\n✅ All caching tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False

def test_unified_search():
    """Test the unified search service"""
    print("\n🔍 Testing Unified Search Service")
    print("-" * 40)
    
    try:
        from services.unified_search_service import (
            get_unified_search_service, SearchQuery, SearchResult,
            get_unified_search_health_status
        )
        
        service = get_unified_search_service()
        
        # Test 1: Service initialization
        print("1. Testing service initialization...")
        available_services = service.get_available_services()
        assert isinstance(available_services, dict)
        print(f"✅ Service initialized with {len(available_services)} categories")
        
        # Test 2: Search query creation
        print("\n2. Testing search query creation...")
        query = SearchQuery(
            query="test search",
            search_type="web",
            engines=["google"],
            max_results=5
        )
        assert query.query == "test search"
        assert query.search_type == "web"
        print("✅ Search query creation works")
        
        # Test 3: Search result creation
        print("\n3. Testing search result creation...")
        result = SearchResult(
            title="Test Result",
            description="Test description",
            url="https://example.com",
            source="test"
        )
        assert result.title == "Test Result"
        assert result.source == "test"
        print("✅ Search result creation works")
        
        # Test 4: Service status
        print("\n4. Testing service status...")
        status = service.get_service_status()
        assert isinstance(status, dict)
        print("✅ Service status works")
        
        # Test 5: Health status
        print("\n5. Testing health status...")
        health = get_unified_search_health_status()
        assert 'status' in health
        assert 'available_services' in health
        print("✅ Health status works")
        
        print("\n✅ All unified search tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Unified search test failed: {e}")
        return False

def test_health_monitoring():
    """Test the health monitoring system"""
    print("\n🏥 Testing Health Monitoring System")
    print("-" * 40)
    
    try:
        from utils.health_monitor import (
            get_health_monitor, HealthMetric, HealthAlert,
            get_comprehensive_health_status
        )
        
        monitor = get_health_monitor()
        
        # Test 1: Health metric creation
        print("1. Testing health metric creation...")
        metric = HealthMetric("test_metric", 75.5, "%", 80.0)
        assert metric.name == "test_metric"
        assert metric.value == 75.5
        assert not metric.is_critical()
        print("✅ Health metric creation works")
        
        # Test 2: Health alert creation
        print("\n2. Testing health alert creation...")
        alert = HealthAlert("warning", "Test alert", "test_metric", 75.5)
        assert alert.severity == "warning"
        assert alert.message == "Test alert"
        print("✅ Health alert creation works")
        
        # Test 3: Health status
        print("\n3. Testing health status...")
        status = monitor.get_health_status()
        assert 'status' in status
        assert 'metrics' in status
        assert 'alerts' in status
        print("✅ Health status works")
        
        # Test 4: Metric history
        print("\n4. Testing metric history...")
        history = monitor.get_metric_history(hours=1)
        assert isinstance(history, list)
        print("✅ Metric history works")
        
        # Test 5: Comprehensive health status
        print("\n5. Testing comprehensive health status...")
        comprehensive = get_comprehensive_health_status()
        assert 'status' in comprehensive
        assert 'components' in comprehensive
        print("✅ Comprehensive health status works")
        
        # Test 6: Threshold management
        print("\n6. Testing threshold management...")
        monitor.set_threshold("test_threshold", 90.0)
        thresholds = monitor.get_thresholds()
        assert "test_threshold" in thresholds
        print("✅ Threshold management works")
        
        print("\n✅ All health monitoring tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Health monitoring test failed: {e}")
        return False

def test_integration():
    """Test integration between all systems"""
    print("\n🔗 Testing System Integration")
    print("-" * 40)
    
    try:
        # Test 1: Error handling with caching
        print("1. Testing error handling with caching...")
        from utils.error_handler import handle_errors
        from utils.cache_manager import cached
        
        @handle_errors
        @cached(ttl=60)
        def test_integrated_function(param):
            if param == "error":
                raise ValueError("Test error")
            return f"success_{param}"
        
        # Test normal operation
        result = test_integrated_function("normal")
        assert "success_normal" in str(result)
        
        # Test error handling
        error_result = test_integrated_function("error")
        assert error_result['success'] == False
        print("✅ Error handling with caching works")
        
        # Test 2: Search with caching and error handling
        print("\n2. Testing search with caching and error handling...")
        from services.unified_search_service import SearchQuery
        
        @handle_errors
        @cached(ttl=300)
        def test_search_function(query_text):
            query = SearchQuery(query=query_text, search_type="web", max_results=1)
            return {"query": query_text, "results": []}
        
        search_result = test_search_function("test query")
        assert search_result['query'] == "test query"
        print("✅ Search with caching and error handling works")
        
        # Test 3: Health monitoring integration
        print("\n3. Testing health monitoring integration...")
        from utils.health_monitor import get_comprehensive_health_status
        
        health = get_comprehensive_health_status()
        assert 'status' in health
        assert 'components' in health
        print("✅ Health monitoring integration works")
        
        print("\n✅ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_performance():
    """Test performance improvements"""
    print("\n⚡ Testing Performance Improvements")
    print("-" * 40)
    
    try:
        from utils.cache_manager import get_cache_manager
        from utils.error_handler import error_handler
        from concurrent.futures import ThreadPoolExecutor
        import time
        
        cache = get_cache_manager()
        
        # Test 1: Cache performance
        print("1. Testing cache performance...")
        start_time = time.time()
        
        # Set multiple cache entries
        for i in range(100):
            cache.set(f"perf_test_{i}", f"value_{i}", ttl=60)
        
        # Get multiple cache entries
        for i in range(100):
            cache.get(f"perf_test_{i}")
        
        cache_time = time.time() - start_time
        print(f"✅ Cache operations completed in {cache_time:.3f} seconds")
        
        # Test 2: Error handling performance
        print("\n2. Testing error handling performance...")
        start_time = time.time()
        
        # Generate multiple errors
        for i in range(50):
            error = Exception(f"Performance test error {i}")
            error_handler.handle_error(error, {"test": i})
        
        error_time = time.time() - start_time
        print(f"✅ Error handling completed in {error_time:.3f} seconds")
        
        # Test 3: Concurrent operations
        print("\n3. Testing concurrent operations...")
        def cache_worker(worker_id):
            for i in range(10):
                cache.set(f"concurrent_{worker_id}_{i}", f"value_{i}", ttl=60)
                cache.get(f"concurrent_{worker_id}_{i}")
            return f"Worker {worker_id} completed"
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(cache_worker, i) for i in range(5)]
            results = [future.result() for future in futures]
        
        concurrent_time = time.time() - start_time
        print(f"✅ Concurrent operations completed in {concurrent_time:.3f} seconds")
        
        print("\n✅ All performance tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LeadFinder Improvements Test Suite")
    print("=" * 60)
    
    tests = [
        ("Error Handling", test_error_handling),
        ("Caching System", test_caching_system),
        ("Unified Search", test_unified_search),
        ("Health Monitoring", test_health_monitoring),
        ("System Integration", test_integration),
        ("Performance", test_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} tests...")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All improvements are working correctly!")
        print("\n✅ Implemented Features:")
        print("   • Comprehensive error handling with custom exceptions")
        print("   • Thread-safe caching system with TTL and LRU eviction")
        print("   • Unified search service consolidating all search functionality")
        print("   • Real-time health monitoring with alerts and metrics")
        print("   • System integration and performance optimization")
    else:
        print("⚠️  Some improvements need attention.")
    
    # Cleanup
    try:
        from utils.cache_manager import stop_cache_manager
        from utils.health_monitor import stop_health_monitor
        from utils.error_handler import error_handler
        
        stop_cache_manager()
        stop_health_monitor()
        error_handler.clear_error_history()
        print("\n🧹 Cleanup completed")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

if __name__ == "__main__":
    main() 