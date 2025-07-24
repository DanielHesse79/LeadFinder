/**
 * Progress Tracker Component
 * 
 * This module provides real-time progress tracking for LeadFinder operations.
 * It displays progress bars with detailed step-by-step information.
 */

class ProgressTracker {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            pollInterval: 1000, // 1 second
            maxRetries: 30, // 30 seconds
            showDetails: true,
            showTimeRemaining: true,
            ...options
        };
        
        this.currentOperation = null;
        this.pollTimer = null;
        this.retryCount = 0;
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error(`Progress tracker container not found: ${this.containerId}`);
            return;
        }
        
        this.render();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="progress-tracker" style="display: none;">
                <div class="progress-header">
                    <h5 class="progress-title mb-2">
                        <i class="fas fa-cog fa-spin me-2"></i>
                        <span class="operation-name">Processing...</span>
                    </h5>
                    <div class="progress-description text-muted mb-3"></div>
                </div>
                
                <div class="overall-progress mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="progress-label">Overall Progress</span>
                        <span class="progress-percentage">0%</span>
                    </div>
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" style="width: 0%"></div>
                    </div>
                    <div class="progress-details mt-2">
                        <small class="text-muted">
                            <span class="time-remaining"></span>
                            <span class="step-info"></span>
                        </small>
                    </div>
                </div>
                
                <div class="step-progress">
                    <h6 class="mb-3">Step Details</h6>
                    <div class="step-list"></div>
                </div>
                
                <div class="progress-actions mt-3">
                    <button class="btn btn-sm btn-outline-secondary cancel-operation" style="display: none;">
                        <i class="fas fa-times me-1"></i>Cancel
                    </button>
                    <button class="btn btn-sm btn-outline-primary view-details" style="display: none;">
                        <i class="fas fa-eye me-1"></i>View Details
                    </button>
                </div>
            </div>
        `;
        
        this.bindEvents();
    }
    
    bindEvents() {
        const cancelBtn = this.container.querySelector('.cancel-operation');
        const detailsBtn = this.container.querySelector('.view-details');
        
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelOperation());
        }
        
        if (detailsBtn) {
            detailsBtn.addEventListener('click', () => this.showDetails());
        }
    }
    
    startTracking(operationId) {
        if (!operationId) {
            console.error('Operation ID is required for progress tracking');
            return;
        }
        
        this.currentOperation = operationId;
        this.retryCount = 0;
        this.show();
        this.pollProgress();
    }
    
    pollProgress() {
        if (!this.currentOperation || this.retryCount >= this.options.maxRetries) {
            this.stopTracking();
            return;
        }
        
        fetch(`/progress/${this.currentOperation}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.updateProgress(data.operation);
                    this.retryCount = 0; // Reset retry count on successful response
                    
                    // Continue polling if operation is still running
                    if (data.operation.status === 'running' || data.operation.status === 'pending') {
                        this.pollTimer = setTimeout(() => this.pollProgress(), this.options.pollInterval);
                    } else {
                        this.handleCompletion(data.operation);
                    }
                } else {
                    console.error('Progress tracking error:', data.error);
                    this.retryCount++;
                    this.pollTimer = setTimeout(() => this.pollProgress(), this.options.pollInterval);
                }
            })
            .catch(error => {
                console.error('Progress tracking failed:', error);
                this.retryCount++;
                this.pollTimer = setTimeout(() => this.pollProgress(), this.options.pollInterval);
            });
    }
    
    updateProgress(operation) {
        const tracker = this.container.querySelector('.progress-tracker');
        const title = tracker.querySelector('.operation-name');
        const description = tracker.querySelector('.progress-description');
        const progressBar = tracker.querySelector('.progress-bar');
        const progressPercentage = tracker.querySelector('.progress-percentage');
        const timeRemaining = tracker.querySelector('.time-remaining');
        const stepInfo = tracker.querySelector('.step-info');
        const stepList = tracker.querySelector('.step-list');
        
        // Update header
        title.textContent = operation.name;
        description.textContent = operation.description;
        
        // Update overall progress
        const overallProgress = Math.round(operation.overall_progress * 100);
        progressBar.style.width = `${overallProgress}%`;
        progressPercentage.textContent = `${overallProgress}%`;
        
        // Update progress bar color based on status
        progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
        if (operation.status === 'completed') {
            progressBar.classList.add('bg-success');
        } else if (operation.status === 'failed') {
            progressBar.classList.add('bg-danger');
        } else {
            progressBar.classList.add('bg-primary');
        }
        
        // Update time remaining
        if (operation.estimated_time_remaining && this.options.showTimeRemaining) {
            const timeRemainingText = this.formatTimeRemaining(operation.estimated_time_remaining);
            timeRemaining.textContent = `Estimated time remaining: ${timeRemainingText}`;
        } else {
            timeRemaining.textContent = '';
        }
        
        // Update step info
        const currentStep = operation.steps.find(step => step.status === 'running');
        if (currentStep) {
            stepInfo.textContent = `Current step: ${currentStep.name}`;
        } else {
            stepInfo.textContent = '';
        }
        
        // Update step list
        this.updateStepList(operation.steps, stepList);
        
        // Update action buttons
        this.updateActionButtons(operation);
    }
    
    updateStepList(steps, stepListContainer) {
        if (!this.options.showDetails) {
            stepListContainer.style.display = 'none';
            return;
        }
        
        stepListContainer.style.display = 'block';
        stepListContainer.innerHTML = steps.map(step => `
            <div class="step-item mb-2 ${step.status}">
                <div class="d-flex justify-content-between align-items-center">
                    <div class="step-info">
                        <span class="step-name">${step.name}</span>
                        <small class="text-muted d-block">${step.description}</small>
                    </div>
                    <div class="step-status">
                        ${this.getStepStatusIcon(step.status)}
                        <span class="step-progress-text">${Math.round(step.progress * 100)}%</span>
                    </div>
                </div>
                <div class="progress mt-1" style="height: 4px;">
                    <div class="progress-bar ${this.getStepProgressClass(step.status)}" 
                         style="width: ${step.progress * 100}%"></div>
                </div>
                ${step.details ? `<small class="text-muted mt-1">${this.formatDetails(step.details)}</small>` : ''}
                ${step.error ? `<small class="text-danger mt-1">Error: ${step.error}</small>` : ''}
            </div>
        `).join('');
    }
    
    getStepStatusIcon(status) {
        const icons = {
            'pending': '<i class="fas fa-clock text-muted"></i>',
            'running': '<i class="fas fa-spinner fa-spin text-primary"></i>',
            'completed': '<i class="fas fa-check text-success"></i>',
            'failed': '<i class="fas fa-times text-danger"></i>'
        };
        return icons[status] || icons.pending;
    }
    
    getStepProgressClass(status) {
        const classes = {
            'pending': 'bg-secondary',
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger'
        };
        return classes[status] || 'bg-secondary';
    }
    
    formatDetails(details) {
        if (typeof details === 'object') {
            return Object.entries(details)
                .map(([key, value]) => `${key}: ${value}`)
                .join(', ');
        }
        return details;
    }
    
    formatTimeRemaining(seconds) {
        if (seconds < 60) {
            return `${Math.round(seconds)}s`;
        } else if (seconds < 3600) {
            return `${Math.round(seconds / 60)}m`;
        } else {
            return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`;
        }
    }
    
    updateActionButtons(operation) {
        const cancelBtn = this.container.querySelector('.cancel-operation');
        const detailsBtn = this.container.querySelector('.view-details');
        
        // Show cancel button only for running operations
        if (cancelBtn) {
            cancelBtn.style.display = operation.status === 'running' ? 'inline-block' : 'none';
        }
        
        // Show details button for completed operations
        if (detailsBtn) {
            detailsBtn.style.display = operation.status === 'completed' ? 'inline-block' : 'none';
        }
    }
    
    handleCompletion(operation) {
        // Add completion class
        const tracker = this.container.querySelector('.progress-tracker');
        tracker.classList.add('completed');
        
        // Update header icon
        const title = tracker.querySelector('.operation-name');
        const icon = tracker.querySelector('.fas.fa-cog');
        
        if (operation.status === 'completed') {
            icon.className = 'fas fa-check text-success me-2';
            title.textContent = `${operation.name} - Completed`;
        } else if (operation.status === 'failed') {
            icon.className = 'fas fa-times text-danger me-2';
            title.textContent = `${operation.name} - Failed`;
        }
        
        // Stop polling
        this.stopTracking();
        
        // Trigger completion event
        this.triggerEvent('progress-completed', { operation });
    }
    
    cancelOperation() {
        if (this.currentOperation) {
            // TODO: Implement cancel endpoint
            console.log('Canceling operation:', this.currentOperation);
            this.stopTracking();
        }
    }
    
    showDetails() {
        if (this.currentOperation) {
            // TODO: Implement details view
            console.log('Showing details for operation:', this.currentOperation);
        }
    }
    
    stopTracking() {
        if (this.pollTimer) {
            clearTimeout(this.pollTimer);
            this.pollTimer = null;
        }
        this.currentOperation = null;
    }
    
    show() {
        const tracker = this.container.querySelector('.progress-tracker');
        tracker.style.display = 'block';
    }
    
    hide() {
        const tracker = this.container.querySelector('.progress-tracker');
        tracker.style.display = 'none';
        this.stopTracking();
    }
    
    triggerEvent(eventName, data) {
        const event = new CustomEvent(eventName, { detail: data });
        this.container.dispatchEvent(event);
    }
}

// Global progress tracker instance
window.LeadFinderProgress = {
    trackers: new Map(),
    
    create(containerId, options) {
        const tracker = new ProgressTracker(containerId, options);
        this.trackers.set(containerId, tracker);
        return tracker;
    },
    
    get(containerId) {
        return this.trackers.get(containerId);
    },
    
    remove(containerId) {
        const tracker = this.trackers.get(containerId);
        if (tracker) {
            tracker.hide();
            this.trackers.delete(containerId);
        }
    }
};

// Auto-initialize progress tracking for forms
document.addEventListener('DOMContentLoaded', function() {
    // Find forms that should have progress tracking
    const searchForms = document.querySelectorAll('form[data-progress-tracking]');
    
    searchForms.forEach(form => {
        const containerId = form.getAttribute('data-progress-container');
        if (containerId) {
            const tracker = LeadFinderProgress.create(containerId);
            
            form.addEventListener('submit', function(e) {
                // Start progress tracking when form is submitted
                const formData = new FormData(form);
                
                // Submit form via AJAX
                e.preventDefault();
                
                fetch(form.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.operation_id) {
                        tracker.startTracking(data.operation_id);
                    } else {
                        console.error('Form submission failed:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Form submission error:', error);
                });
            });
        }
    });
}); 