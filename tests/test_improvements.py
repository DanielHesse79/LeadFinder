"""
Comprehensive tests for LeadFinder improvements

This module tests all the new improvements:
- Redis caching system
- Database indexing
- Async service patterns
- Performance optimizations
"""

import pytest
import asyncio
import tempfile
import os
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the new improvement modules
try:
    from utils.redis_cache import RedisCacheManager, get_redis_cache_manager, redis_cached
    from models.database_indexes import DatabaseIndexManager, get_index_manager, create_standard_indexes
    from utils.async_service import AsyncServiceManager, AsyncContextManager, async_retry, async_timeout
    from utils.async_service import run_in_thread_pool, AsyncQueue, AsyncServiceWrapper
except ImportError as e:
    pytest.skip(f"Improvement modules not available: {e}", allow_module_level=True)

class TestRedisCaching:
    """Test Redis caching system"""
    
    @pytest.fixture
    def redis_cache(self):
        """Create Redis cache manager with mocked Redis"""
        with patch('utils.redis_cache.redis') as mock_redis:
            # Mock Redis connection
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_client.setex.return_value = True
            mock_client.get.return_value = '{"test": "value"}'
            mock_client.delete.return_value = 1
            mock_client.exists.return_value = 1
            mock_client.ttl.return_value = 3600
            mock_client.info.return_value = {
                'connected_clients': 1,
                'used_memory_human': '1MB',
                'keyspace_hits': 100,
                'keyspace_misses': 10
            }
            
            mock_redis.Redis.return_value = mock_client
            mock_redis.ConnectionPool.return_value = Mock()
            
            cache = RedisCacheManager(host='localhost', port=6379)
            cache._redis_client = mock_client
            cache._is_healthy = True
            
            return cache
    
    def test_redis_cache_initialization(self, redis_cache):
        """Test Redis cache initialization"""
        assert redis_cache.host == 'localhost'
        assert redis_cache.port == 6379
        assert redis_cache._is_healthy is True
    
    def test_redis_cache_set_get(self, redis_cache):
        """Test setting and getting from Redis cache"""
        # Test set
        result = redis_cache.set("test_key", {"test": "value"}, ttl=3600)
        assert result is True
        
        # Test get
        value = redis_cache.get("test_key")
        assert value == {"test": "value"}
    
    def test_redis_cache_serialization(self, redis_cache):
        """Test value serialization and deserialization"""
        # Test complex object serialization
        test_data = {
            'string': 'test',
            'number': 42,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'}
        }
        
        serialized = redis_cache._serialize_value(test_data)
        assert isinstance(serialized, str)
        
        deserialized = redis_cache._deserialize_value(serialized)
        assert deserialized == test_data
    
    def test_redis_cache_fallback(self):
        """Test fallback to in-memory cache when Redis is unavailable"""
        with patch('utils.redis_cache.redis') as mock_redis:
            # Mock Redis connection failure
            mock_redis.Redis.side_effect = Exception("Connection failed")
            
            cache = RedisCacheManager(host='localhost', port=6379)
            
            # Should use fallback cache
            cache.set("test_key", "test_value", ttl=60)
            value = cache.get("test_key")
            assert value == "test_value"
    
    def test_redis_cache_decorator(self):
        """Test Redis cache decorator"""
        cache_manager = Mock()
        cache_manager.get.return_value = None
        cache_manager.set.return_value = True
        
        with patch('utils.redis_cache.get_redis_cache_manager', return_value=cache_manager):
            @redis_cached(ttl=3600)
            def test_function(param1, param2):
                return f"result_{param1}_{param2}"
            
            result = test_function("a", "b")
            assert result == "result_a_b"
            
            # Check that cache was used
            cache_manager.get.assert_called_once()
            cache_manager.set.assert_called_once()
    
    def test_redis_cache_stats(self, redis_cache):
        """Test cache statistics"""
        stats = redis_cache.get_stats()
        
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'sets' in stats
        assert 'hit_rate' in stats
        assert 'is_healthy' in stats
    
    def test_redis_cache_health(self, redis_cache):
        """Test cache health status"""
        health = redis_cache.get_health_status()
        
        assert 'is_healthy' in health
        assert 'redis_available' in health
        assert 'fallback_active' in health
        assert 'connection_info' in health
        assert 'stats' in health

class TestDatabaseIndexing:
    """Test database indexing system"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def index_manager(self, temp_db):
        """Create index manager with temporary database"""
        with patch('models.database_indexes.get_db_pool') as mock_pool:
            mock_pool.return_value = None
            return DatabaseIndexManager(temp_db)
    
    def test_index_manager_initialization(self, index_manager):
        """Test index manager initialization"""
        assert index_manager.db_path is not None
        assert isinstance(index_manager.indexes, dict)
        assert isinstance(index_manager.query_performance, list)
    
    def test_create_index(self, index_manager):
        """Test index creation"""
        result = index_manager.create_index('test_table', ['column1', 'column2'])
        assert result is True
        
        # Check that index was added to tracking
        assert len(index_manager.indexes) > 0
    
    def test_drop_index(self, index_manager):
        """Test index dropping"""
        # Create an index first
        index_manager.create_index('test_table', ['column1'])
        
        # Get the index name
        index_name = list(index_manager.indexes.keys())[0]
        
        # Drop the index
        result = index_manager.drop_index(index_name)
        assert result is True
        
        # Check that index was removed from tracking
        assert index_name not in index_manager.indexes
    
    def test_get_indexes_for_table(self, index_manager):
        """Test getting indexes for a table"""
        # Create indexes for different tables
        index_manager.create_index('table1', ['col1'])
        index_manager.create_index('table2', ['col2'])
        index_manager.create_index('table1', ['col3'])
        
        # Get indexes for table1
        table1_indexes = index_manager.get_indexes_for_table('table1')
        assert len(table1_indexes) == 2
        
        # Get indexes for table2
        table2_indexes = index_manager.get_indexes_for_table('table2')
        assert len(table2_indexes) == 1
    
    def test_analyze_query_performance(self, index_manager):
        """Test query performance analysis"""
        query = "SELECT * FROM leads WHERE source = 'test'"
        index_manager.analyze_query_performance(
            query=query,
            execution_time=1.5,
            rows_returned=100,
            index_used="idx_leads_source"
        )
        
        assert len(index_manager.query_performance) == 1
        performance = index_manager.query_performance[0]
        assert performance.query == query
        assert performance.execution_time == 1.5
        assert performance.rows_returned == 100
        assert performance.index_used == "idx_leads_source"
    
    def test_get_slow_queries(self, index_manager):
        """Test getting slow queries"""
        # Add some performance records
        index_manager.analyze_query_performance("fast_query", 0.1, 10)
        index_manager.analyze_query_performance("slow_query", 2.0, 100)
        index_manager.analyze_query_performance("very_slow_query", 5.0, 1000)
        
        # Get slow queries with threshold 1.0
        slow_queries = index_manager.get_slow_queries(threshold=1.0)
        assert len(slow_queries) == 2
        
        # Check that only slow queries are returned
        query_names = [qp.query for qp in slow_queries]
        assert "fast_query" not in query_names
        assert "slow_query" in query_names
        assert "very_slow_query" in query_names
    
    def test_recommend_indexes(self, index_manager):
        """Test index recommendations"""
        # Add some slow queries
        index_manager.analyze_query_performance(
            "SELECT * FROM leads WHERE source = 'test'", 2.0, 100
        )
        index_manager.analyze_query_performance(
            "SELECT * FROM workshop_analysis WHERE project_id = 1", 1.5, 50
        )
        
        recommendations = index_manager.recommend_indexes()
        assert len(recommendations) > 0
        
        # Check recommendation structure
        for rec in recommendations:
            assert 'table' in rec
            assert 'columns' in rec
            assert 'reason' in rec
            assert 'estimated_improvement' in rec
    
    def test_optimize_database(self, index_manager):
        """Test database optimization"""
        # Add some slow queries to trigger recommendations
        index_manager.analyze_query_performance(
            "SELECT * FROM leads WHERE source = 'test'", 2.0, 100
        )
        
        results = index_manager.optimize_database()
        
        assert 'indexes_created' in results
        assert 'indexes_dropped' in results
        assert 'recommendations_applied' in results
        assert 'performance_improvement' in results
    
    def test_get_performance_report(self, index_manager):
        """Test performance report generation"""
        # Add some data
        index_manager.create_index('test_table', ['col1'])
        index_manager.analyze_query_performance("test_query", 1.0, 50)
        
        report = index_manager.get_performance_report()
        
        assert 'total_indexes' in report
        assert 'indexes_by_table' in report
        assert 'slow_queries_count' in report
        assert 'avg_query_time' in report
        assert 'recommendations' in report
        assert 'index_usage' in report

class TestAsyncService:
    """Test async service patterns"""
    
    @pytest.fixture
    def async_manager(self):
        """Create async service manager"""
        return AsyncServiceManager(max_workers=2, max_processes=1)
    
    def test_async_manager_initialization(self, async_manager):
        """Test async manager initialization"""
        assert async_manager.max_workers == 2
        assert async_manager.max_processes == 1
        assert async_manager.running is True
        assert isinstance(async_manager.tasks, dict)
    
    def test_submit_task(self, async_manager):
        """Test task submission"""
        def test_function(x, y):
            return x + y
        
        task_id = async_manager.submit_task(test_function, 1, 2)
        
        assert task_id in async_manager.tasks
        task = async_manager.tasks[task_id]
        assert task.func == test_function
        assert task.args == (1, 2)
        assert task.status == 'pending'
    
    def test_get_task_status(self, async_manager):
        """Test getting task status"""
        def test_function():
            return "test_result"
        
        task_id = async_manager.submit_task(test_function)
        task = async_manager.get_task_status(task_id)
        
        assert task is not None
        assert task.id == task_id
        assert task.func == test_function
    
    def test_cancel_task(self, async_manager):
        """Test task cancellation"""
        def test_function():
            time.sleep(1)
            return "test_result"
        
        task_id = async_manager.submit_task(test_function)
        
        # Cancel the task
        result = async_manager.cancel_task(task_id)
        assert result is True
        
        # Check task status
        task = async_manager.get_task_status(task_id)
        assert task.status == 'cancelled'
    
    def test_get_all_tasks(self, async_manager):
        """Test getting all tasks"""
        def test_function1():
            return "result1"
        
        def test_function2():
            return "result2"
        
        task_id1 = async_manager.submit_task(test_function1)
        task_id2 = async_manager.submit_task(test_function2)
        
        all_tasks = async_manager.get_all_tasks()
        assert len(all_tasks) == 2
        
        task_ids = [task.id for task in all_tasks]
        assert task_id1 in task_ids
        assert task_id2 in task_ids
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager"""
        async with AsyncContextManager("test_resource") as ctx:
            assert ctx.resource_name == "test_resource"
            assert ctx.start_time is not None
    
    @pytest.mark.asyncio
    async def test_async_retry_decorator(self):
        """Test async retry decorator"""
        call_count = 0
        
        @async_retry(max_retries=2, delay=0.1)
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await failing_function()
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_timeout_decorator(self):
        """Test async timeout decorator"""
        @async_timeout(0.1)
        async def slow_function():
            await asyncio.sleep(1.0)
            return "too_slow"
        
        with pytest.raises(asyncio.TimeoutError):
            await slow_function()
    
    @pytest.mark.asyncio
    async def test_run_in_thread_pool(self):
        """Test running function in thread pool"""
        def sync_function(x, y):
            return x + y
        
        future = run_in_thread_pool(sync_function, 1, 2)
        result = await future
        
        assert result == 3
    
    @pytest.mark.asyncio
    async def test_async_queue(self):
        """Test async queue"""
        queue = AsyncQueue(maxsize=10)
        
        # Put items in queue
        await queue.put("item1")
        await queue.put("item2")
        
        # Get items from queue
        item1 = await queue.get()
        item2 = await queue.get()
        
        assert item1 == "item1"
        assert item2 == "item2"
    
    @pytest.mark.asyncio
    async def test_async_service_wrapper(self):
        """Test async service wrapper"""
        # Create a mock service
        mock_service = Mock()
        mock_service.test_method.return_value = "test_result"
        
        wrapper = AsyncServiceWrapper(mock_service)
        
        # Call method asynchronously
        result = await wrapper.call_method("test_method", "arg1", kwarg1="value1")
        
        assert result == "test_result"
        mock_service.test_method.assert_called_once_with("arg1", kwarg1="value1")
    
    @pytest.mark.asyncio
    async def test_async_batch_process(self):
        """Test async batch processing"""
        async def process_item(item):
            return f"processed_{item}"
        
        items = ["item1", "item2", "item3", "item4", "item5"]
        results = await async_batch_process(items, process_item, batch_size=2, max_concurrent=2)
        
        assert len(results) == 5
        assert "processed_item1" in results
        assert "processed_item2" in results
        assert "processed_item3" in results
        assert "processed_item4" in results
        assert "processed_item5" in results
    
    @pytest.mark.asyncio
    async def test_async_retry_with_backoff(self):
        """Test async retry with backoff"""
        call_count = 0
        
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await async_retry_with_backoff(failing_function, max_retries=3, initial_delay=0.1)
        
        assert result == "success"
        assert call_count == 3

class TestIntegration:
    """Integration tests for improvements"""
    
    @pytest.mark.asyncio
    async def test_redis_cache_with_async(self):
        """Test Redis cache with async operations"""
        with patch('utils.redis_cache.redis') as mock_redis:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_client.setex.return_value = True
            mock_client.get.return_value = '{"async": "test"}'
            
            mock_redis.Redis.return_value = mock_client
            mock_redis.ConnectionPool.return_value = Mock()
            
            cache = RedisCacheManager()
            cache._redis_client = mock_client
            cache._is_healthy = True
            
            # Test async cache operations
            async def async_cache_operation():
                cache.set("async_key", {"async": "test"})
                return cache.get("async_key")
            
            result = await run_in_thread_pool(async_cache_operation)
            assert result == {"async": "test"}
    
    def test_database_indexing_with_redis_cache(self):
        """Test database indexing with Redis cache integration"""
        with patch('models.database_indexes.get_db_pool') as mock_pool:
            mock_pool.return_value = None
            
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                db_path = f.name
            
            try:
                index_manager = DatabaseIndexManager(db_path)
                
                # Create some indexes
                index_manager.create_index('test_table', ['col1', 'col2'])
                
                # Test with Redis cache
                with patch('utils.redis_cache.get_redis_cache_manager') as mock_cache:
                    cache_manager = Mock()
                    cache_manager.get.return_value = None
                    cache_manager.set.return_value = True
                    mock_cache.return_value = cache_manager
                    
                    # Get performance report (should be cached)
                    report1 = index_manager.get_performance_report()
                    report2 = index_manager.get_performance_report()
                    
                    assert report1 == report2
                    
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_async_service_with_database_indexing(self):
        """Test async service with database indexing"""
        with patch('models.database_indexes.get_db_pool') as mock_pool:
            mock_pool.return_value = None
            
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                db_path = f.name
            
            try:
                index_manager = DatabaseIndexManager(db_path)
                async_manager = AsyncServiceManager(max_workers=2)
                
                # Submit database indexing task
                def create_indexes():
                    index_manager.create_index('test_table', ['col1'])
                    index_manager.create_index('test_table', ['col2'])
                    return len(index_manager.indexes)
                
                task_id = async_manager.submit_task(create_indexes)
                
                # Wait for task completion
                for _ in range(10):  # Wait up to 1 second
                    task = async_manager.get_task_status(task_id)
                    if task and task.status == 'completed':
                        break
                    time.sleep(0.1)
                
                task = async_manager.get_task_status(task_id)
                assert task.status == 'completed'
                assert task.result == 2  # Two indexes created
                
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)

class TestPerformance:
    """Performance tests for improvements"""
    
    def test_redis_cache_performance(self):
        """Test Redis cache performance"""
        with patch('utils.redis_cache.redis') as mock_redis:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_client.setex.return_value = True
            mock_client.get.return_value = '{"test": "value"}'
            
            mock_redis.Redis.return_value = mock_client
            mock_redis.ConnectionPool.return_value = Mock()
            
            cache = RedisCacheManager()
            cache._redis_client = mock_client
            cache._is_healthy = True
            
            # Test cache performance
            start_time = time.time()
            
            for i in range(100):
                cache.set(f"key_{i}", f"value_{i}")
                cache.get(f"key_{i}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete 200 operations in reasonable time
            assert duration < 1.0  # Less than 1 second for 200 operations
    
    def test_database_indexing_performance(self):
        """Test database indexing performance"""
        with patch('models.database_indexes.get_db_pool') as mock_pool:
            mock_pool.return_value = None
            
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                db_path = f.name
            
            try:
                index_manager = DatabaseIndexManager(db_path)
                
                # Test index creation performance
                start_time = time.time()
                
                for i in range(10):
                    index_manager.create_index(f'table_{i}', [f'col_{i}'])
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Should create 10 indexes in reasonable time
                assert duration < 1.0
                assert len(index_manager.indexes) == 10
                
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)
    
    @pytest.mark.asyncio
    async def test_async_service_performance(self):
        """Test async service performance"""
        async_manager = AsyncServiceManager(max_workers=5)
        
        def test_function(x):
            time.sleep(0.01)  # Simulate work
            return x * 2
        
        # Submit multiple tasks
        start_time = time.time()
        
        task_ids = []
        for i in range(20):
            task_id = async_manager.submit_task(test_function, i)
            task_ids.append(task_id)
        
        # Wait for all tasks to complete
        for _ in range(50):  # Wait up to 5 seconds
            completed = sum(
                1 for task_id in task_ids
                if async_manager.get_task_status(task_id)?.status == 'completed'
            )
            if completed == 20:
                break
            await asyncio.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 20 tasks in reasonable time
        assert duration < 2.0  # Less than 2 seconds for 20 tasks

if __name__ == "__main__":
    pytest.main([__file__]) 