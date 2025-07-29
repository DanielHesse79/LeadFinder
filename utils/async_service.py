"""
Async Service Wrapper for LeadFinder

This module provides standardized async patterns and utilities:
- Async service wrapper with proper error handling
- Async context managers for resource management
- Async decorators for performance monitoring
- Async queue management for background tasks
- Async retry mechanisms with exponential backoff
"""

import asyncio
import time
import functools
from typing import Any, Callable, Optional, Dict, List, Union, TypeVar, Awaitable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from queue import Queue
import weakref

try:
    from utils.logger import get_logger
    logger = get_logger('async_service')
except ImportError:
    logger = None

try:
    from utils.error_handler import handle_errors, LeadFinderError
except ImportError:
    handle_errors = None
    LeadFinderError = Exception

T = TypeVar('T')

@dataclass
class AsyncTask:
    """Represents an async task"""
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    created_at: float
    status: str = 'pending'  # pending, running, completed, failed
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0

class AsyncServiceManager:
    """
    Manages async services and background tasks
    """
    
    def __init__(self, max_workers: int = 10, max_processes: int = 4):
        self.max_workers = max_workers
        self.max_processes = max_processes
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_processes)
        self.tasks = {}
        self.task_queue = Queue()
        self.running = True
        self._task_counter = 0
        self._lock = threading.Lock()
        
        # Start background task processor
        self._processor_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self._processor_thread.start()
    
    def _get_next_task_id(self) -> str:
        """Get next unique task ID"""
        with self._lock:
            self._task_counter += 1
            return f"task_{self._task_counter}_{int(time.time())}"
    
    def submit_task(self, func: Callable, *args, **kwargs) -> str:
        """
        Submit a task for async execution
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Task ID
        """
        task_id = self._get_next_task_id()
        
        task = AsyncTask(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            created_at=time.time()
        )
        
        self.tasks[task_id] = task
        self.task_queue.put(task)
        
        if logger:
            logger.debug(f"Submitted task {task_id}: {func.__name__}")
        
        return task_id
    
    def _process_tasks(self):
        """Background task processor"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                
                self._execute_task(task)
                
            except Exception as e:
                if logger:
                    logger.error(f"Error processing task: {e}")
    
    def _execute_task(self, task: AsyncTask):
        """Execute a single task"""
        task.status = 'running'
        start_time = time.time()
        
        try:
            # Execute in thread pool
            future = self.thread_pool.submit(task.func, *task.args, **task.kwargs)
            result = future.result(timeout=300)  # 5 minute timeout
            
            task.result = result
            task.status = 'completed'
            task.execution_time = time.time() - start_time
            
            if logger:
                logger.debug(f"Task {task.id} completed in {task.execution_time:.2f}s")
                
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.execution_time = time.time() - start_time
            
            if logger:
                logger.error(f"Task {task.id} failed: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[AsyncTask]:
        """Get task status"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[AsyncTask]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == 'pending':
                task.status = 'cancelled'
                return True
        return False
    
    def shutdown(self):
        """Shutdown the async service manager"""
        self.running = False
        self.task_queue.put(None)
        
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        
        if self.process_pool:
            self.process_pool.shutdown(wait=True)

class AsyncContextManager:
    """Async context manager for resource management"""
    
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        self.resource = None
        self.start_time = None
    
    async def __aenter__(self):
        """Enter async context"""
        self.start_time = time.time()
        if logger:
            logger.debug(f"Entering async context: {self.resource_name}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        duration = time.time() - self.start_time
        if logger:
            logger.debug(f"Exiting async context: {self.resource_name} (duration: {duration:.2f}s)")
        
        if exc_type:
            if logger:
                logger.error(f"Async context error in {self.resource_name}: {exc_val}")
            return False
        return True

def async_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator for async retry with exponential backoff
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        if logger:
                            logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        if logger:
                            logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator

def async_timeout(timeout_seconds: float):
    """
    Decorator for async timeout
    
    Args:
        timeout_seconds: Timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                if logger:
                    logger.error(f"Function {func.__name__} timed out after {timeout_seconds}s")
                raise
        return wrapper
    return decorator

def async_performance_monitor(func_name: str = None):
    """
    Decorator for async performance monitoring
    
    Args:
        func_name: Custom function name for logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            name = func_name or func.__name__
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                if logger:
                    logger.debug(f"Async function {name} completed in {duration:.2f}s")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                if logger:
                    logger.error(f"Async function {name} failed after {duration:.2f}s: {e}")
                
                raise
        return wrapper
    return decorator

def run_in_thread_pool(func: Callable, *args, **kwargs) -> asyncio.Future:
    """
    Run a synchronous function in a thread pool
    
    Args:
        func: Function to run
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Future object
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

def run_in_process_pool(func: Callable, *args, **kwargs) -> asyncio.Future:
    """
    Run a function in a process pool
    
    Args:
        func: Function to run
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Future object
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

class AsyncQueue:
    """Async queue for background processing"""
    
    def __init__(self, maxsize: int = 1000):
        self.queue = asyncio.Queue(maxsize=maxsize)
        self.processing = False
        self.workers = []
    
    async def put(self, item: Any):
        """Put item in queue"""
        await self.queue.put(item)
    
    async def get(self) -> Any:
        """Get item from queue"""
        return await self.queue.get()
    
    def start_workers(self, num_workers: int, worker_func: Callable):
        """Start background workers"""
        self.processing = True
        
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(worker_func, i))
            self.workers.append(worker)
    
    async def _worker(self, worker_func: Callable, worker_id: int):
        """Background worker"""
        if logger:
            logger.debug(f"Starting async worker {worker_id}")
        
        while self.processing:
            try:
                item = await self.queue.get()
                await worker_func(item, worker_id)
                self.queue.task_done()
            except Exception as e:
                if logger:
                    logger.error(f"Worker {worker_id} error: {e}")
    
    async def stop_workers(self):
        """Stop all workers"""
        self.processing = False
        
        for worker in self.workers:
            worker.cancel()
        
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

# Global async service manager
_async_manager = None

def get_async_manager() -> AsyncServiceManager:
    """Get global async service manager"""
    global _async_manager
    
    if _async_manager is None:
        _async_manager = AsyncServiceManager()
    
    return _async_manager

def submit_async_task(func: Callable, *args, **kwargs) -> str:
    """Submit a task for async execution"""
    manager = get_async_manager()
    return manager.submit_task(func, *args, **kwargs)

def get_async_task_status(task_id: str) -> Optional[AsyncTask]:
    """Get async task status"""
    manager = get_async_manager()
    return manager.get_task_status(task_id)

def shutdown_async_manager():
    """Shutdown async service manager"""
    global _async_manager
    
    if _async_manager:
        _async_manager.shutdown()
        _async_manager = None

# Example async service wrapper
class AsyncServiceWrapper:
    """Wrapper for making services async-compatible"""
    
    def __init__(self, service_instance: Any):
        self.service = service_instance
        self._cache = {}
    
    async def call_method(self, method_name: str, *args, **kwargs) -> Any:
        """
        Call a service method asynchronously
        
        Args:
            method_name: Name of the method to call
            *args: Method arguments
            **kwargs: Method keyword arguments
            
        Returns:
            Method result
        """
        if not hasattr(self.service, method_name):
            raise AttributeError(f"Method {method_name} not found on service")
        
        method = getattr(self.service, method_name)
        
        # Run in thread pool
        return await run_in_thread_pool(method, *args, **kwargs)
    
    def __getattr__(self, name: str):
        """Delegate attribute access to wrapped service"""
        return getattr(self.service, name)

# Utility functions for common async patterns
async def async_batch_process(items: List[Any], 
                            processor_func: Callable,
                            batch_size: int = 10,
                            max_concurrent: int = 5) -> List[Any]:
    """
    Process items in batches asynchronously
    
    Args:
        items: List of items to process
        processor_func: Function to process each item
        batch_size: Size of each batch
        max_concurrent: Maximum concurrent batches
        
    Returns:
        List of processed results
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []
    
    async def process_batch(batch: List[Any]) -> List[Any]:
        async with semaphore:
            tasks = [processor_func(item) for item in batch]
            return await asyncio.gather(*tasks, return_exceptions=True)
    
    # Split items into batches
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    # Process batches concurrently
    batch_tasks = [process_batch(batch) for batch in batches]
    batch_results = await asyncio.gather(*batch_tasks)
    
    # Flatten results
    for batch_result in batch_results:
        results.extend(batch_result)
    
    return results

async def async_retry_with_backoff(func: Callable,
                                 max_retries: int = 3,
                                 initial_delay: float = 1.0,
                                 max_delay: float = 60.0,
                                 backoff_factor: float = 2.0) -> Any:
    """
    Retry function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplier
        
    Returns:
        Function result
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                if logger:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                if logger:
                    logger.error(f"All {max_retries + 1} attempts failed: {e}")
                raise last_exception
    
    raise last_exception 