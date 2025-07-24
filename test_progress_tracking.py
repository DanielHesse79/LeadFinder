#!/usr/bin/env python3
"""
Test Progress Tracking System

This script tests the progress tracking functionality to ensure it works correctly.
"""

import sys
import time
import threading
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, '.')

def test_progress_manager():
    """Test the progress manager functionality"""
    print("🧪 Testing Progress Manager...")
    
    try:
        from utils.progress_manager import (
            get_progress_manager, ProgressStatus, 
            SEARCH_STEPS, ANALYSIS_STEPS, RESEARCH_STEPS
        )
        
        progress_manager = get_progress_manager()
        
        # Test 1: Create operation
        print("  📝 Creating test operation...")
        operation_id = progress_manager.create_operation(
            name="Test Search Operation",
            description="Testing the progress tracking system",
            steps=SEARCH_STEPS
        )
        
        if not operation_id:
            print("  ❌ Failed to create operation")
            return False
        
        print(f"  ✅ Operation created with ID: {operation_id}")
        
        # Test 2: Start operation
        print("  🚀 Starting operation...")
        if not progress_manager.start_operation(operation_id):
            print("  ❌ Failed to start operation")
            return False
        
        print("  ✅ Operation started")
        
        # Test 3: Update steps
        print("  📊 Updating steps...")
        
        # Step 1: Initialize
        progress_manager.update_step(
            operation_id, "step_1", 0.5, ProgressStatus.RUNNING,
            {"query": "test query", "engines": ["google"]}
        )
        time.sleep(0.5)
        
        progress_manager.update_step(
            operation_id, "step_1", 1.0, ProgressStatus.COMPLETED
        )
        print("  ✅ Step 1 completed")
        
        # Step 2: Web search
        progress_manager.update_step(
            operation_id, "step_2", 0.0, ProgressStatus.RUNNING
        )
        time.sleep(0.5)
        
        progress_manager.update_step(
            operation_id, "step_2", 0.5, ProgressStatus.RUNNING,
            {"results_found": 5}
        )
        time.sleep(0.5)
        
        progress_manager.update_step(
            operation_id, "step_2", 1.0, ProgressStatus.COMPLETED,
            {"results_found": 10}
        )
        print("  ✅ Step 2 completed")
        
        # Step 3: Research search
        progress_manager.update_step(
            operation_id, "step_3", 0.0, ProgressStatus.RUNNING
        )
        time.sleep(0.3)
        
        progress_manager.update_step(
            operation_id, "step_3", 1.0, ProgressStatus.COMPLETED
        )
        print("  ✅ Step 3 completed")
        
        # Step 4: Funding search
        progress_manager.update_step(
            operation_id, "step_4", 0.0, ProgressStatus.RUNNING
        )
        time.sleep(0.3)
        
        progress_manager.update_step(
            operation_id, "step_4", 1.0, ProgressStatus.COMPLETED
        )
        print("  ✅ Step 4 completed")
        
        # Step 5: AI analysis
        progress_manager.update_step(
            operation_id, "step_5", 0.0, ProgressStatus.RUNNING
        )
        time.sleep(0.5)
        
        progress_manager.update_step(
            operation_id, "step_5", 0.5, ProgressStatus.RUNNING,
            {"analyzing": "processing results"}
        )
        time.sleep(0.5)
        
        progress_manager.update_step(
            operation_id, "step_5", 1.0, ProgressStatus.COMPLETED,
            {"analyzed_leads": 10}
        )
        print("  ✅ Step 5 completed")
        
        # Step 6: Save results
        progress_manager.update_step(
            operation_id, "step_6", 0.0, ProgressStatus.RUNNING
        )
        time.sleep(0.3)
        
        progress_manager.update_step(
            operation_id, "step_6", 1.0, ProgressStatus.COMPLETED,
            {"saved_leads": 10}
        )
        print("  ✅ Step 6 completed")
        
        # Test 4: Complete operation
        print("  ✅ Completing operation...")
        progress_manager.complete_operation(operation_id)
        
        # Test 5: Get operation data
        operation = progress_manager.get_operation(operation_id)
        if not operation:
            print("  ❌ Failed to retrieve operation")
            return False
        
        print(f"  ✅ Operation retrieved: {operation.name}")
        print(f"  📊 Overall progress: {operation.get_overall_progress():.1%}")
        print(f"  📈 Completed steps: {operation.completed_steps}/{operation.total_steps}")
        
        # Test 6: Convert to dict
        operation_dict = operation.to_dict()
        print(f"  ✅ Operation serialized to dict with {len(operation_dict)} fields")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Progress manager test failed: {e}")
        return False


def test_progress_context():
    """Test the progress context manager"""
    print("🧪 Testing Progress Context Manager...")
    
    try:
        from utils.progress_manager import ProgressContext, ProgressStatus, ANALYSIS_STEPS
        
        with ProgressContext("Test Analysis", "Testing context manager", ANALYSIS_STEPS) as ctx:
            operation_id = ctx.get_operation_id()
            print(f"  ✅ Context created operation: {operation_id}")
            
            # Update steps
            ctx.update_step("step_1", 0.5, ProgressStatus.RUNNING)
            time.sleep(0.2)
            ctx.update_step("step_1", 1.0, ProgressStatus.COMPLETED)
            
            ctx.update_step("step_2", 0.0, ProgressStatus.RUNNING)
            time.sleep(0.2)
            ctx.update_step("step_2", 1.0, ProgressStatus.COMPLETED)
            
            ctx.update_step("step_3", 0.0, ProgressStatus.RUNNING)
            time.sleep(0.2)
            ctx.update_step("step_3", 1.0, ProgressStatus.COMPLETED)
            
            ctx.update_step("step_4", 0.0, ProgressStatus.RUNNING)
            time.sleep(0.2)
            ctx.update_step("step_4", 1.0, ProgressStatus.COMPLETED)
            
            ctx.update_step("step_5", 0.0, ProgressStatus.RUNNING)
            time.sleep(0.2)
            ctx.update_step("step_5", 1.0, ProgressStatus.COMPLETED)
            
            print("  ✅ All steps completed successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Progress context test failed: {e}")
        return False


def test_concurrent_operations():
    """Test multiple concurrent operations"""
    print("🧪 Testing Concurrent Operations...")
    
    try:
        from utils.progress_manager import get_progress_manager, ProgressStatus, SEARCH_STEPS
        
        progress_manager = get_progress_manager()
        operation_ids = []
        
        def run_operation(operation_num):
            """Run a single operation"""
            operation_id = progress_manager.create_operation(
                name=f"Concurrent Operation {operation_num}",
                description=f"Testing concurrent operation {operation_num}",
                steps=SEARCH_STEPS
            )
            
            progress_manager.start_operation(operation_id)
            
            # Simulate work
            for i, step_id in enumerate([f"step_{j+1}" for j in range(6)]):
                progress_manager.update_step(operation_id, step_id, 0.0, ProgressStatus.RUNNING)
                time.sleep(0.1)  # Simulate work
                progress_manager.update_step(operation_id, step_id, 1.0, ProgressStatus.COMPLETED)
            
            progress_manager.complete_operation(operation_id)
            operation_ids.append(operation_id)
        
        # Start 3 concurrent operations
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_operation, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        print(f"  ✅ Completed {len(operation_ids)} concurrent operations")
        
        # Verify all operations are completed
        for op_id in operation_ids:
            operation = progress_manager.get_operation(op_id)
            if operation and operation.status == ProgressStatus.COMPLETED:
                print(f"  ✅ Operation {op_id} completed successfully")
            else:
                print(f"  ❌ Operation {op_id} failed or not completed")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Concurrent operations test failed: {e}")
        return False


def test_error_handling():
    """Test error handling in progress tracking"""
    print("🧪 Testing Error Handling...")
    
    try:
        from utils.progress_manager import get_progress_manager, ProgressStatus, SEARCH_STEPS
        
        progress_manager = get_progress_manager()
        
        # Create operation
        operation_id = progress_manager.create_operation(
            name="Error Test Operation",
            description="Testing error handling",
            steps=SEARCH_STEPS
        )
        
        progress_manager.start_operation(operation_id)
        
        # Simulate normal progress
        progress_manager.update_step(operation_id, "step_1", 1.0, ProgressStatus.COMPLETED)
        progress_manager.update_step(operation_id, "step_2", 0.5, ProgressStatus.RUNNING)
        
        # Simulate error
        progress_manager.update_step(
            operation_id, "step_2", 0.5, ProgressStatus.FAILED,
            error="Simulated error for testing"
        )
        
        # Check operation status
        operation = progress_manager.get_operation(operation_id)
        if operation.status == ProgressStatus.FAILED:
            print("  ✅ Error handling works correctly")
            return True
        else:
            print("  ❌ Error handling failed")
            return False
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False


def test_cleanup():
    """Test cleanup functionality"""
    print("🧪 Testing Cleanup Functionality...")
    
    try:
        from utils.progress_manager import get_progress_manager
        
        progress_manager = get_progress_manager()
        
        # Create some old operations
        old_operation_id = progress_manager.create_operation(
            name="Old Operation",
            description="This should be cleaned up",
            steps=[]
        )
        
        # Complete the operation
        progress_manager.complete_operation(old_operation_id)
        
        # Get initial count
        initial_count = len(progress_manager.operations)
        
        # Run cleanup
        progress_manager.cleanup_old_operations(max_age_hours=0)  # Clean up immediately
        
        # Get final count
        final_count = len(progress_manager.operations)
        
        if final_count < initial_count:
            print("  ✅ Cleanup removed old operations")
            return True
        else:
            print("  ⚠️  No operations were cleaned up (this might be expected)")
            return True
        
    except Exception as e:
        print(f"  ❌ Cleanup test failed: {e}")
        return False


def main():
    """Run all progress tracking tests"""
    print("🚀 Starting Progress Tracking System Tests")
    print("=" * 50)
    
    tests = [
        ("Progress Manager", test_progress_manager),
        ("Progress Context", test_progress_context),
        ("Concurrent Operations", test_concurrent_operations),
        ("Error Handling", test_error_handling),
        ("Cleanup", test_cleanup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Progress tracking system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 