/**
 * LeadFinder Main JavaScript - Centralized Functions
 * Includes security features, utility functions, and common functionality
 */

// ===== PWA & SERVICE WORKER =====

/**
 * Register service worker for offline functionality
 */
async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register('/static/js/sw.js');
            console.log('[SW] Service Worker registered successfully:', registration);
            
            // Handle service worker updates
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        // New service worker available
                        showNotification('New version available. Please refresh the page.', 'info');
                    }
                });
            });
            
            // Handle service worker messages
            navigator.serviceWorker.addEventListener('message', event => {
                console.log('[SW] Message from service worker:', event.data);
            });
            
        } catch (error) {
            console.error('[SW] Service Worker registration failed:', error);
        }
    }
}

/**
 * Check if the app is running in standalone mode (installed as PWA)
 */
function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches || 
           window.navigator.standalone === true;
}

/**
 * Install PWA prompt
 */
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button if not already installed
    if (!isStandalone()) {
        showInstallButton();
    }
});

/**
 * Show install button for PWA
 */
function showInstallButton() {
    const installButton = document.createElement('button');
    installButton.className = 'btn btn-primary position-fixed';
    installButton.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000;';
    installButton.innerHTML = '<i class="fas fa-download me-2"></i>Install App';
    installButton.onclick = installPWA;
    
    document.body.appendChild(installButton);
}

/**
 * Install PWA
 */
async function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        
        if (outcome === 'accepted') {
            console.log('PWA installed successfully');
            showNotification('App installed successfully!', 'success');
        }
        
        deferredPrompt = null;
    }
}

// ===== SECURITY UTILITIES =====

/**
 * Sanitize HTML content to prevent XSS attacks
 * @param {string} html - The HTML string to sanitize
 * @returns {string} - Sanitized HTML
 */
function sanitizeHTML(html) {
    if (!html) return '';
    
    // Create a temporary div to parse HTML
    const temp = document.createElement('div');
    temp.textContent = html; // This automatically escapes HTML
    
    // Only allow safe HTML tags and attributes
    const allowedTags = ['b', 'i', 'em', 'strong', 'a', 'br', 'p', 'span', 'div'];
    const allowedAttributes = ['href', 'class', 'id', 'title'];
    
    // If we need to allow some HTML, we can parse it more carefully
    // For now, we'll just return the text content to be safe
    return temp.textContent;
}

/**
 * Safely insert HTML content into DOM elements
 * @param {HTMLElement} element - The target element
 * @param {string} content - The content to insert
 * @param {boolean} allowHTML - Whether to allow HTML (default: false)
 */
function safeInsertHTML(element, content, allowHTML = false) {
    if (!element || !content) return;
    
    if (allowHTML) {
        // Use DOMPurify if available, otherwise sanitize manually
        if (typeof DOMPurify !== 'undefined') {
            element.innerHTML = DOMPurify.sanitize(content);
        } else {
            element.innerHTML = sanitizeHTML(content);
        }
    } else {
        element.textContent = content;
    }
}

/**
 * Validate CSRF token for AJAX requests
 * @param {Object} options - Fetch options
 * @returns {Object} - Updated options with CSRF token
 */
function addCSRFToken(options = {}) {
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    if (token && options.method && options.method.toUpperCase() !== 'GET') {
        options.headers = {
            ...options.headers,
            'X-CSRFToken': token
        };
    }
    return options;
}

// ===== AJAX UTILITIES =====

/**
 * Enhanced fetch with CSRF protection and error handling
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @returns {Promise} - Fetch promise
 */
async function secureFetch(url, options = {}) {
    try {
        // Add CSRF token
        options = addCSRFToken(options);
        
        // Add default headers
        options.headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        showNotification('Error: ' + error.message, 'danger');
        throw error;
    }
}

/**
 * Make a POST request with JSON data
 * @param {string} url - The URL to post to
 * @param {Object} data - The data to send
 * @returns {Promise} - Response promise
 */
async function postJSON(url, data) {
    return secureFetch(url, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * Make a GET request and return JSON
 * @param {string} url - The URL to get
 * @returns {Promise} - JSON response
 */
async function getJSON(url) {
    const response = await secureFetch(url, {
        method: 'GET'
    });
    return response.json();
}

// ===== UI UTILITIES =====

/**
 * Show notification message
 * @param {string} message - The message to show
 * @param {string} type - The type of notification (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Create notification container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
    
    // Handle manual close
    notification.querySelector('.btn-close').addEventListener('click', () => {
        notification.remove();
    });
}

/**
 * Serialize form data
 * @param {HTMLFormElement} form - The form to serialize
 * @returns {FormData} - Serialized form data
 */
function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        if (data[key]) {
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }
    
    return data;
}

/**
 * Validate form fields
 * @param {HTMLFormElement} form - The form to validate
 * @returns {boolean} - Whether the form is valid
 */
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Submit form with AJAX
 * @param {HTMLFormElement} form - The form to submit
 * @param {string} url - The URL to submit to
 * @param {Function} onSuccess - Success callback
 * @param {Function} onError - Error callback
 */
async function submitForm(form, url, onSuccess = null, onError = null) {
    if (!validateForm(form)) {
        showNotification('Please fill in all required fields', 'warning');
        return;
    }
    
    try {
        const formData = new FormData(form);
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message || 'Success!', 'success');
            if (onSuccess) onSuccess(data);
        } else {
            showNotification(data.error || 'An error occurred', 'danger');
            if (onError) onError(data);
        }
    } catch (error) {
        showNotification('Error: ' + error.message, 'danger');
        if (onError) onError(error);
    }
}

// ===== TABLE UTILITIES =====

/**
 * Initialize DataTable with options
 * @param {string} tableSelector - CSS selector for the table
 * @param {Object} options - DataTable options
 */
function initDataTable(tableSelector, options = {}) {
    const table = document.querySelector(tableSelector);
    if (!table) return;
    
    // Default options
    const defaultOptions = {
        pageLength: 25,
        responsive: true,
        language: {
            search: "Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            paginate: {
                first: "First",
                last: "Last",
                next: "Next",
                previous: "Previous"
            }
        }
    };
    
    // Merge options
    const finalOptions = { ...defaultOptions, ...options };
    
    // Initialize DataTable if jQuery DataTables is available
    if (typeof $.fn.DataTable !== 'undefined') {
        return $(table).DataTable(finalOptions);
    } else {
        // Fallback to basic table functionality
        console.warn('DataTables not available, using basic table functionality');
        return initBasicTable(table);
    }
}

/**
 * Initialize basic table functionality
 * @param {HTMLElement} table - The table element
 */
function initBasicTable(table) {
    // Add search functionality
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search...';
    searchInput.className = 'form-control mb-3';
    searchInput.addEventListener('input', (e) => {
        filterTable(table, e.target.value);
    });
    
    table.parentNode.insertBefore(searchInput, table);
    
    return {
        search: (term) => filterTable(table, term),
        destroy: () => {
            if (searchInput.parentNode) {
                searchInput.parentNode.removeChild(searchInput);
            }
        }
    };
}

/**
 * Filter table rows
 * @param {HTMLElement} table - The table to filter
 * @param {string} searchTerm - The search term
 */
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

/**
 * Sort table by column
 * @param {HTMLElement} table - The table to sort
 * @param {HTMLElement} header - The header element to sort by
 */
function sortTable(table, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const isAscending = header.classList.contains('sort-asc');
    
    // Toggle sort direction
    header.classList.toggle('sort-asc', !isAscending);
    header.classList.toggle('sort-desc', isAscending);
    
    // Sort rows
    rows.sort((a, b) => {
        const aValue = a.children[columnIndex]?.textContent || '';
        const bValue = b.children[columnIndex]?.textContent || '';
        
        if (isAscending) {
            return bValue.localeCompare(aValue);
        } else {
            return aValue.localeCompare(bValue);
        }
    });
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
}

// ===== LOADING UTILITIES =====

/**
 * Show loading spinner
 * @param {HTMLElement} element - The element to show loading for
 */
function showLoading(element) {
    element.style.opacity = '0.5';
    element.style.pointerEvents = 'none';
}

/**
 * Hide loading spinner
 * @param {HTMLElement} element - The element to hide loading for
 */
function hideLoading(element) {
    element.style.opacity = '1';
    element.style.pointerEvents = 'auto';
}

// ===== UTILITY FUNCTIONS =====

/**
 * Debounce function calls
 * @param {Function} func - The function to debounce
 * @param {number} wait - The wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format date for display
 * @param {string|Date} date - The date to format
 * @returns {string} - Formatted date string
 */
function formatDate(date) {
    if (!date) return '';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';
    
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format number for display
 * @param {number} num - The number to format
 * @returns {string} - Formatted number string
 */
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString();
}

/**
 * Copy text to clipboard
 * @param {string} text - The text to copy
 * @returns {Promise} - Promise that resolves when copied
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        showNotification('Failed to copy to clipboard', 'danger');
    }
}

// ===== INITIALIZATION =====

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('LeadFinder application initializing...');
    
    // Register service worker
    registerServiceWorker();
    
    // Initialize PWA functionality
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then(registration => {
            console.log('Service Worker ready:', registration);
        });
    }
    
    // Add global error handler
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
        showNotification('An error occurred. Please try again.', 'danger');
    });
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        showNotification('An error occurred. Please try again.', 'danger');
    });
    
    console.log('LeadFinder application initialized successfully');
});

// Export functions for use in other modules
window.LeadFinder = {
    sanitizeHTML,
    safeInsertHTML,
    secureFetch,
    postJSON,
    getJSON,
    showNotification,
    serializeForm,
    validateForm,
    submitForm,
    initDataTable,
    filterTable,
    sortTable,
    showLoading,
    hideLoading,
    debounce,
    formatDate,
    formatNumber,
    copyToClipboard,
    isStandalone,
    installPWA
}; 