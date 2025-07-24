"""
Progress Manager for LeadFinder

This module provides real-time progress tracking for searches and analyses.
It supports WebSocket connections for live updates and fallback to polling.
"""

import time
import threading
import uuid
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json

try:
    from utils.logger import get_logger
    logger = get_logger('progress_manager')
except ImportError:
    logger = None


class ProgressStatus(Enum):
    """Progress status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProgressStep:
    """Represents a single step in a progress operation"""
    id: str
    name: str
    description: str
    status: ProgressStatus
    progress: float  # 0.0 to 1.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data


@dataclass
class ProgressOperation:
    """Represents a complete progress operation"""
    id: str
    name: str
    description: str
    status: ProgressStatus
    total_steps: int
    completed_steps: int
    current_step: Optional[str] = None
    start_time: datetime = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    steps: List[ProgressStep] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.steps is None:
            self.steps = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        data['steps'] = [step.to_dict() for step in self.steps]
        data['overall_progress'] = self.get_overall_progress()
        data['estimated_time_remaining'] = self.get_estimated_time_remaining()
        return data

    def get_overall_progress(self) -> float:
        """Calculate overall progress (0.0 to 1.0)"""
        if not self.steps:
            return 0.0
        total_progress = sum(step.progress for step in self.steps)
        return total_progress / len(self.steps)

    def get_estimated_time_remaining(self) -> Optional[float]:
        """Estimate time remaining in seconds"""
        if self.status != ProgressStatus.RUNNING or not self.steps:
            return None
        
        completed_steps = [s for s in self.steps if s.end_time]
        if not completed_steps:
            return None
        
        avg_time = sum((s.end_time - s.start_time).total_seconds() 
                      for s in completed_steps) / len(completed_steps)
        remaining_steps = len(self.steps) - len(completed_steps)
        return avg_time * remaining_steps


class ProgressManager:
    """Manages progress tracking for operations"""
    
    def __init__(self):
        self.operations: Dict[str, ProgressOperation] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._cleanup_interval = 3600  # 1 hour
        self._last_cleanup = time.time()
    
    def create_operation(self, name: str, description: str, 
                        steps: List[Dict[str, str]] = None) -> str:
        """Create a new progress operation"""
        operation_id = str(uuid.uuid4())
        
        # Create step objects from step definitions
        step_objects = []
        if steps:
            for i, step_def in enumerate(steps):
                step = ProgressStep(
                    id=f"step_{i+1}",
                    name=step_def.get('name', f'Step {i+1}'),
                    description=step_def.get('description', ''),
                    status=ProgressStatus.PENDING,
                    progress=0.0
                )
                step_objects.append(step)
        
        operation = ProgressOperation(
            id=operation_id,
            name=name,
            description=description,
            status=ProgressStatus.PENDING,
            total_steps=len(step_objects),
            completed_steps=0,
            steps=step_objects
        )
        
        with self._lock:
            self.operations[operation_id] = operation
            self.callbacks[operation_id] = []
        
        if logger:
            logger.info(f"Created progress operation: {name} (ID: {operation_id})")
        
        return operation_id
    
    def start_operation(self, operation_id: str) -> bool:
        """Start a progress operation"""
        with self._lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            operation.status = ProgressStatus.RUNNING
            operation.start_time = datetime.now()
            
            if logger:
                logger.info(f"Started progress operation: {operation.name}")
        
        self._notify_callbacks(operation_id)
        return True
    
    def update_step(self, operation_id: str, step_id: str, 
                   progress: float, status: ProgressStatus = None,
                   details: Dict[str, Any] = None, error: str = None) -> bool:
        """Update a specific step's progress"""
        with self._lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            step = next((s for s in operation.steps if s.id == step_id), None)
            
            if not step:
                return False
            
            # Update step
            if step.start_time is None:
                step.start_time = datetime.now()
            
            step.progress = max(0.0, min(1.0, progress))
            
            if status:
                step.status = status
                if status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED]:
                    step.end_time = datetime.now()
                    if status == ProgressStatus.COMPLETED:
                        operation.completed_steps += 1
            
            if details:
                step.details = details
            
            if error:
                step.error = error
                step.status = ProgressStatus.FAILED
                step.end_time = datetime.now()
            
            # Update operation status
            if step.status == ProgressStatus.FAILED:
                operation.status = ProgressStatus.FAILED
                operation.error = error
            elif all(s.status == ProgressStatus.COMPLETED for s in operation.steps):
                operation.status = ProgressStatus.COMPLETED
                operation.end_time = datetime.now()
        
        self._notify_callbacks(operation_id)
        return True
    
    def complete_operation(self, operation_id: str, error: str = None) -> bool:
        """Complete a progress operation"""
        with self._lock:
            if operation_id not in self.operations:
                return False
            
            operation = self.operations[operation_id]
            operation.status = ProgressStatus.FAILED if error else ProgressStatus.COMPLETED
            operation.end_time = datetime.now()
            if error:
                operation.error = error
            
            if logger:
                status = "failed" if error else "completed"
                logger.info(f"Progress operation {status}: {operation.name}")
        
        self._notify_callbacks(operation_id)
        return True
    
    def get_operation(self, operation_id: str) -> Optional[ProgressOperation]:
        """Get operation by ID"""
        with self._lock:
            return self.operations.get(operation_id)
    
    def add_callback(self, operation_id: str, callback: Callable) -> bool:
        """Add a callback for operation updates"""
        with self._lock:
            if operation_id not in self.operations:
                return False
            self.callbacks[operation_id].append(callback)
        return True
    
    def remove_callback(self, operation_id: str, callback: Callable) -> bool:
        """Remove a callback"""
        with self._lock:
            if operation_id not in self.callbacks:
                return False
            try:
                self.callbacks[operation_id].remove(callback)
                return True
            except ValueError:
                return False
    
    def _notify_callbacks(self, operation_id: str):
        """Notify all callbacks for an operation"""
        operation = self.get_operation(operation_id)
        if not operation:
            return
        
        callbacks = self.callbacks.get(operation_id, [])
        for callback in callbacks:
            try:
                callback(operation)
            except Exception as e:
                if logger:
                    logger.error(f"Callback error: {e}")
    
    def cleanup_old_operations(self, max_age_hours: int = 24):
        """Clean up old completed operations"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        with self._lock:
            to_remove = []
            for op_id, operation in self.operations.items():
                if (operation.status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED] and
                    operation.end_time and operation.end_time.timestamp() < cutoff_time):
                    to_remove.append(op_id)
            
            for op_id in to_remove:
                del self.operations[op_id]
                if op_id in self.callbacks:
                    del self.callbacks[op_id]
        
        self._last_cleanup = current_time
        if logger and to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old progress operations")


# Global progress manager instance
_progress_manager = None

def get_progress_manager() -> ProgressManager:
    """Get the global progress manager instance"""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ProgressManager()
    return _progress_manager


class ProgressContext:
    """Context manager for progress tracking"""
    
    def __init__(self, operation_name: str, description: str, 
                 steps: List[Dict[str, str]] = None):
        self.operation_name = operation_name
        self.description = description
        self.steps = steps or []
        self.operation_id = None
        self.progress_manager = get_progress_manager()
    
    def __enter__(self):
        self.operation_id = self.progress_manager.create_operation(
            self.operation_name, self.description, self.steps
        )
        self.progress_manager.start_operation(self.operation_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.operation_id:
            error = str(exc_val) if exc_val else None
            self.progress_manager.complete_operation(self.operation_id, error)
    
    def update_step(self, step_id: str, progress: float, 
                   status: ProgressStatus = None, details: Dict[str, Any] = None):
        """Update a step's progress"""
        if self.operation_id:
            self.progress_manager.update_step(
                self.operation_id, step_id, progress, status, details
            )
    
    def get_operation_id(self) -> str:
        """Get the operation ID"""
        return self.operation_id


# Predefined step templates for common operations
SEARCH_STEPS = [
    {'name': 'Initializing Search', 'description': 'Setting up search parameters and validating configuration'},
    {'name': 'Web Search', 'description': 'Searching web engines (Google, Bing, DuckDuckGo)'},
    {'name': 'Research Search', 'description': 'Searching academic databases (PubMed, ORCID, Semantic Scholar)'},
    {'name': 'Funding Search', 'description': 'Searching funding databases (SweCRIS, CORDIS, NIH, NSF)'},
    {'name': 'AI Analysis', 'description': 'Analyzing results with AI for relevance and insights'},
    {'name': 'Saving Results', 'description': 'Saving leads to database and generating reports'}
]

ANALYSIS_STEPS = [
    {'name': 'Initializing Analysis', 'description': 'Setting up AI model and preparing analysis'},
    {'name': 'Text Processing', 'description': 'Processing and preparing text for analysis'},
    {'name': 'AI Processing', 'description': 'Running AI analysis with selected model'},
    {'name': 'Result Processing', 'description': 'Processing and formatting analysis results'},
    {'name': 'Saving Results', 'description': 'Saving analysis results to database'}
]

RESEARCH_STEPS = [
    {'name': 'Initializing Research', 'description': 'Setting up research parameters and AI model'},
    {'name': 'Topic Analysis', 'description': 'Analyzing research topic and generating search strategy'},
    {'name': 'Information Gathering', 'description': 'Gathering information from multiple sources'},
    {'name': 'AI Analysis', 'description': 'Analyzing gathered information with AI'},
    {'name': 'Report Generation', 'description': 'Generating comprehensive research report'},
    {'name': 'Saving Results', 'description': 'Saving research results and insights'}
] 