# Progress Tracking System

## Overview

The Progress Tracking System provides real-time progress monitoring for LeadFinder operations, including searches and AI analyses. It offers detailed step-by-step progress updates with estimated time remaining, status indicators, and comprehensive error handling.

## Features

### 🎯 Real-Time Progress Monitoring
- **Live Updates**: Progress bars update in real-time as operations progress
- **Step-by-Step Details**: Each operation is broken down into detailed steps
- **Status Indicators**: Visual indicators for pending, running, completed, and failed states
- **Time Estimation**: Smart time remaining estimates based on completed steps

### 📊 Comprehensive Tracking
- **Overall Progress**: Main progress bar showing overall completion percentage
- **Step Details**: Individual progress for each step with descriptions
- **Error Handling**: Detailed error reporting with context
- **Performance Metrics**: Timing information for each step

### 🔄 Multi-Operation Support
- **Concurrent Operations**: Support for multiple simultaneous operations
- **Thread-Safe**: Thread-safe implementation for concurrent access
- **Operation Management**: Automatic cleanup of old operations
- **Unique IDs**: Each operation gets a unique identifier for tracking

### 🎨 Modern UI
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode Support**: Automatic dark mode detection and styling
- **Accessibility**: WCAG compliant with keyboard navigation and screen reader support
- **Customizable**: Configurable appearance and behavior

## Architecture

### Core Components

#### 1. Progress Manager (`utils/progress_manager.py`)
The central component that manages all progress operations:

```python
from utils.progress_manager import get_progress_manager, ProgressStatus

# Get the global progress manager
progress_manager = get_progress_manager()

# Create a new operation
operation_id = progress_manager.create_operation(
    name="Search Operation",
    description="Searching for leads",
    steps=SEARCH_STEPS
)

# Start the operation
progress_manager.start_operation(operation_id)

# Update step progress
progress_manager.update_step(
    operation_id, "step_1", 0.5, ProgressStatus.RUNNING,
    {"details": "Processing..."}
)

# Complete the operation
progress_manager.complete_operation(operation_id)
```

#### 2. Progress Context Manager
A context manager for automatic operation lifecycle management:

```python
from utils.progress_manager import ProgressContext, ProgressStatus

with ProgressContext("Analysis", "Analyzing data", ANALYSIS_STEPS) as ctx:
    operation_id = ctx.get_operation_id()
    
    # Update steps
    ctx.update_step("step_1", 0.5, ProgressStatus.RUNNING)
    # ... do work ...
    ctx.update_step("step_1", 1.0, ProgressStatus.COMPLETED)
    
    # Operation automatically completes when context exits
```

#### 3. Progress Routes (`routes/progress.py`)
Flask routes for accessing progress information:

- `GET /progress/<operation_id>` - Get progress for specific operation
- `GET /progress/active` - Get all active operations
- `GET /progress/recent` - Get recent completed operations
- `POST /progress/cleanup` - Clean up old operations

#### 4. Frontend Components
JavaScript and CSS components for displaying progress:

- `static/js/progress-tracker.js` - Progress tracker component
- `static/css/progress-tracker.css` - Styling for progress components

## Usage

### Backend Integration

#### 1. Basic Progress Tracking

```python
from utils.progress_manager import get_progress_manager, ProgressStatus, SEARCH_STEPS

def perform_search_with_progress(query, engines):
    progress_manager = get_progress_manager()
    
    # Create operation
    operation_id = progress_manager.create_operation(
        name=f"Search: {query}",
        description=f"Searching across {len(engines)} engines",
        steps=SEARCH_STEPS
    )
    
    try:
        # Start operation
        progress_manager.start_operation(operation_id)
        
        # Step 1: Initialize
        progress_manager.update_step(operation_id, "step_1", 0.5, ProgressStatus.RUNNING)
        # ... initialization code ...
        progress_manager.update_step(operation_id, "step_1", 1.0, ProgressStatus.COMPLETED)
        
        # Step 2: Web search
        progress_manager.update_step(operation_id, "step_2", 0.0, ProgressStatus.RUNNING)
        results = perform_web_search(query, engines)
        progress_manager.update_step(operation_id, "step_2", 1.0, ProgressStatus.COMPLETED,
                                   {"results_found": len(results)})
        
        # ... continue with other steps ...
        
        # Complete operation
        progress_manager.complete_operation(operation_id)
        return {"success": True, "operation_id": operation_id, "results": results}
        
    except Exception as e:
        # Handle errors
        progress_manager.complete_operation(operation_id, str(e))
        raise
```

#### 2. Using Context Manager

```python
from utils.progress_manager import ProgressContext, ProgressStatus, ANALYSIS_STEPS

def analyze_with_progress(text, analysis_type):
    with ProgressContext(f"AI Analysis: {analysis_type}", 
                        f"Analyzing text with AI", 
                        ANALYSIS_STEPS) as ctx:
        
        operation_id = ctx.get_operation_id()
        
        # Step 1: Initialize
        ctx.update_step("step_1", 0.5, ProgressStatus.RUNNING)
        model = load_ai_model()
        ctx.update_step("step_1", 1.0, ProgressStatus.COMPLETED)
        
        # Step 2: Process text
        ctx.update_step("step_2", 0.0, ProgressStatus.RUNNING)
        processed_text = preprocess_text(text)
        ctx.update_step("step_2", 1.0, ProgressStatus.COMPLETED,
                       {"text_length": len(processed_text)})
        
        # Step 3: AI analysis
        ctx.update_step("step_3", 0.0, ProgressStatus.RUNNING)
        result = model.analyze(processed_text)
        ctx.update_step("step_3", 1.0, ProgressStatus.COMPLETED,
                       {"analysis_complete": True})
        
        return {"success": True, "operation_id": operation_id, "result": result}
```

### Frontend Integration

#### 1. Basic Progress Tracking

```html
<!-- Add progress container -->
<div id="search-progress-container"></div>

<!-- Add progress tracking to form -->
<form method="POST" action="/search_ajax" 
      data-progress-tracking="true" 
      data-progress-container="search-progress-container">
    <!-- form fields -->
</form>

<!-- Include progress tracker -->
<link rel="stylesheet" href="/static/css/progress-tracker.css">
<script src="/static/js/progress-tracker.js"></script>
```

#### 2. Manual Progress Tracking

```javascript
// Create progress tracker
const tracker = LeadFinderProgress.create('progress-container', {
    pollInterval: 1000,  // Poll every second
    maxRetries: 30,      // Max 30 seconds
    showDetails: true,   // Show step details
    showTimeRemaining: true  // Show time estimates
});

// Start tracking an operation
tracker.startTracking('operation-id-here');

// Listen for completion
tracker.container.addEventListener('progress-completed', (event) => {
    const { operation } = event.detail;
    console.log('Operation completed:', operation.name);
});
```

#### 3. Custom Progress Updates

```javascript
// Update progress manually
fetch('/progress/operation-id')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateProgressUI(data.operation);
        }
    });
```

## Predefined Step Templates

### Search Steps (`SEARCH_STEPS`)
```python
SEARCH_STEPS = [
    {'name': 'Initializing Search', 'description': 'Setting up search parameters and validating configuration'},
    {'name': 'Web Search', 'description': 'Searching web engines (Google, Bing, DuckDuckGo)'},
    {'name': 'Research Search', 'description': 'Searching academic databases (PubMed, ORCID, Semantic Scholar)'},
    {'name': 'Funding Search', 'description': 'Searching funding databases (SweCRIS, CORDIS, NIH, NSF)'},
    {'name': 'AI Analysis', 'description': 'Analyzing results with AI for relevance and insights'},
    {'name': 'Saving Results', 'description': 'Saving leads to database and generating reports'}
]
```

### Analysis Steps (`ANALYSIS_STEPS`)
```python
ANALYSIS_STEPS = [
    {'name': 'Initializing Analysis', 'description': 'Setting up AI model and preparing analysis'},
    {'name': 'Text Processing', 'description': 'Processing and preparing text for analysis'},
    {'name': 'AI Processing', 'description': 'Running AI analysis with selected model'},
    {'name': 'Result Processing', 'description': 'Processing and formatting analysis results'},
    {'name': 'Saving Results', 'description': 'Saving analysis results to database'}
]
```

### Research Steps (`RESEARCH_STEPS`)
```python
RESEARCH_STEPS = [
    {'name': 'Initializing Research', 'description': 'Setting up research parameters and AI model'},
    {'name': 'Topic Analysis', 'description': 'Analyzing research topic and generating search strategy'},
    {'name': 'Information Gathering', 'description': 'Gathering information from multiple sources'},
    {'name': 'AI Analysis', 'description': 'Analyzing gathered information with AI'},
    {'name': 'Report Generation', 'description': 'Generating comprehensive research report'},
    {'name': 'Saving Results', 'description': 'Saving research results and insights'}
]
```

## Configuration

### Progress Manager Options

```python
# Global progress manager configuration
progress_manager = get_progress_manager()

# Cleanup old operations (default: 24 hours)
progress_manager.cleanup_old_operations(max_age_hours=24)

# Add custom callbacks
def progress_callback(operation):
    print(f"Operation {operation.name} updated: {operation.status}")

progress_manager.add_callback(operation_id, progress_callback)
```

### Frontend Options

```javascript
const tracker = LeadFinderProgress.create('container', {
    pollInterval: 1000,        // Poll every 1 second
    maxRetries: 30,           // Max 30 retries
    showDetails: true,        // Show step details
    showTimeRemaining: true,  // Show time estimates
    autoStart: true,          // Auto-start tracking
    onComplete: (operation) => {
        // Custom completion handler
    }
});
```

## API Endpoints

### Get Operation Progress
```http
GET /progress/{operation_id}
```

**Response:**
```json
{
    "success": true,
    "operation": {
        "id": "uuid",
        "name": "Search Operation",
        "description": "Searching for leads",
        "status": "running",
        "overall_progress": 0.75,
        "estimated_time_remaining": 30.5,
        "steps": [
            {
                "id": "step_1",
                "name": "Initializing Search",
                "status": "completed",
                "progress": 1.0,
                "start_time": "2024-01-01T12:00:00",
                "end_time": "2024-01-01T12:00:05"
            }
        ]
    }
}
```

### Get Active Operations
```http
GET /progress/active
```

### Get Recent Operations
```http
GET /progress/recent
```

### Cleanup Old Operations
```http
POST /progress/cleanup
Content-Type: application/json

{
    "max_age_hours": 24
}
```

## Error Handling

### Backend Error Handling

```python
try:
    with ProgressContext("Operation", "Description", steps) as ctx:
        # ... operation code ...
        pass
except Exception as e:
    # Context manager automatically marks operation as failed
    logger.error(f"Operation failed: {e}")
```

### Frontend Error Handling

```javascript
tracker.container.addEventListener('progress-completed', (event) => {
    const { operation } = event.detail;
    
    if (operation.status === 'failed') {
        showError(`Operation failed: ${operation.error}`);
    } else if (operation.status === 'completed') {
        showSuccess('Operation completed successfully!');
    }
});
```

## Testing

Run the progress tracking tests:

```bash
python3 test_progress_tracking.py
```

This will test:
- Progress manager functionality
- Context manager usage
- Concurrent operations
- Error handling
- Cleanup functionality

## Performance Considerations

### Memory Management
- Operations are automatically cleaned up after 24 hours (configurable)
- Step details are stored in memory for real-time access
- Large operation histories can be cleaned up manually

### Polling Optimization
- Default polling interval is 1 second
- Polling stops when operation completes or fails
- Maximum retry limit prevents infinite polling

### Thread Safety
- All progress manager operations are thread-safe
- Multiple operations can run concurrently
- Lock-based synchronization prevents race conditions

## Troubleshooting

### Common Issues

1. **Progress not updating**
   - Check that the operation ID is correct
   - Verify the progress manager is properly initialized
   - Check for JavaScript errors in browser console

2. **Operations not completing**
   - Ensure `complete_operation()` is called
   - Check for unhandled exceptions
   - Verify all steps are properly updated

3. **Memory leaks**
   - Run cleanup regularly: `progress_manager.cleanup_old_operations()`
   - Monitor operation count in long-running applications
   - Consider implementing custom cleanup strategies

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger('progress_manager').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **WebSocket Support**: Real-time updates without polling
- **Progress Persistence**: Save progress to database for long operations
- **Operation Queuing**: Queue operations for background processing
- **Progress Templates**: Predefined progress patterns for common operations
- **Mobile Notifications**: Push notifications for operation completion

### Customization Options
- **Custom Step Types**: Define custom step templates
- **Progress Themes**: Customizable visual themes
- **Integration APIs**: REST API for external integrations
- **Analytics**: Progress analytics and performance metrics

## Contributing

When adding progress tracking to new features:

1. **Define Steps**: Create appropriate step templates for the operation
2. **Add Progress Updates**: Update progress at key points in the operation
3. **Handle Errors**: Ensure errors are properly reported
4. **Test Thoroughly**: Test with the progress tracking test suite
5. **Document**: Update this documentation with new features

## Support

For issues with the progress tracking system:

1. Check the test suite: `python3 test_progress_tracking.py`
2. Review the logs for error messages
3. Verify the operation is properly initialized
4. Check browser console for JavaScript errors
5. Ensure all required dependencies are installed 