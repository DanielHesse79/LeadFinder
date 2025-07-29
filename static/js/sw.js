/**
 * LeadFinder Service Worker
 * Provides offline functionality and asset caching
 */

const CACHE_NAME = 'leadfinder-v1.0.0';
const STATIC_CACHE_NAME = 'leadfinder-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'leadfinder-dynamic-v1.0.0';

// Assets to cache for offline functionality
const STATIC_ASSETS = [
    '/',
    '/static/css/main.css',
    '/static/css/progress-tracker.css',
    '/static/js/main.js',
    '/static/js/progress-tracker.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    '/templates/base.html',
    '/templates/navigation.html'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
    '/api/dashboard/stats',
    '/api/leads/',
    '/api/search/history',
    '/api/config/'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('[SW] Installing service worker...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[SW] Static assets cached successfully');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('[SW] Failed to cache static assets:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[SW] Activating service worker...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE_NAME && 
                            cacheName !== DYNAMIC_CACHE_NAME && 
                            cacheName !== CACHE_NAME) {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[SW] Service worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }
    
    // Handle static assets
    if (isStaticAsset(request.url)) {
        event.respondWith(handleStaticAsset(request));
        return;
    }
    
    // Handle HTML pages
    if (request.headers.get('accept')?.includes('text/html')) {
        event.respondWith(handleHtmlRequest(request));
        return;
    }
});

/**
 * Handle API requests with network-first strategy
 */
async function handleApiRequest(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache for API:', request.url);
        
        // Fallback to cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response for API calls
        return new Response(
            JSON.stringify({ 
                error: 'Offline mode - please check your connection',
                offline: true 
            }),
            {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}

/**
 * Handle static assets with cache-first strategy
 */
async function handleStaticAsset(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[SW] Failed to fetch static asset:', request.url);
        
        // Return a basic offline response for CSS/JS
        if (request.url.includes('.css')) {
            return new Response('/* Offline mode */', {
                headers: { 'Content-Type': 'text/css' }
            });
        }
        
        if (request.url.includes('.js')) {
            return new Response('// Offline mode', {
                headers: { 'Content-Type': 'application/javascript' }
            });
        }
        
        throw error;
    }
}

/**
 * Handle HTML requests with network-first strategy
 */
async function handleHtmlRequest(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache for HTML:', request.url);
        
        // Fallback to cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return caches.match('/offline.html') || new Response(
            `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Offline - LeadFinder</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        text-align: center; 
                        padding: 50px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .offline-container {
                        background: rgba(255, 255, 255, 0.1);
                        padding: 2rem;
                        border-radius: 1rem;
                        backdrop-filter: blur(10px);
                    }
                    .offline-icon {
                        font-size: 4rem;
                        margin-bottom: 1rem;
                    }
                    .retry-btn {
                        background: rgba(255, 255, 255, 0.2);
                        border: 2px solid rgba(255, 255, 255, 0.3);
                        color: white;
                        padding: 0.75rem 2rem;
                        border-radius: 0.5rem;
                        text-decoration: none;
                        display: inline-block;
                        margin-top: 1rem;
                        transition: all 0.3s ease;
                    }
                    .retry-btn:hover {
                        background: rgba(255, 255, 255, 0.3);
                        color: white;
                        text-decoration: none;
                    }
                </style>
            </head>
            <body>
                <div class="offline-container">
                    <div class="offline-icon">📡</div>
                    <h1>You're Offline</h1>
                    <p>Please check your internet connection and try again.</p>
                    <a href="/" class="retry-btn" onclick="window.location.reload()">
                        Retry Connection
                    </a>
                </div>
            </body>
            </html>
            `,
            {
                headers: { 'Content-Type': 'text/html' }
            }
        );
    }
}

/**
 * Check if a URL is a static asset
 */
function isStaticAsset(url) {
    const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot'];
    return staticExtensions.some(ext => url.includes(ext)) || 
           url.includes('cdn.jsdelivr.net') || 
           url.includes('cdnjs.cloudflare.com');
}

/**
 * Background sync for offline actions
 */
self.addEventListener('sync', event => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    if (event.tag === 'background-sync') {
        event.waitUntil(performBackgroundSync());
    }
});

/**
 * Perform background sync operations
 */
async function performBackgroundSync() {
    try {
        // Get stored offline actions
        const offlineActions = await getOfflineActions();
        
        for (const action of offlineActions) {
            try {
                await performOfflineAction(action);
                await removeOfflineAction(action.id);
            } catch (error) {
                console.error('[SW] Failed to sync action:', action, error);
            }
        }
        
        console.log('[SW] Background sync completed');
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
    }
}

/**
 * Get stored offline actions from IndexedDB
 */
async function getOfflineActions() {
    // This would typically use IndexedDB
    // For now, return empty array
    return [];
}

/**
 * Perform a stored offline action
 */
async function performOfflineAction(action) {
    const response = await fetch(action.url, {
        method: action.method,
        headers: action.headers,
        body: action.body
    });
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response;
}

/**
 * Remove a completed offline action
 */
async function removeOfflineAction(actionId) {
    // This would typically remove from IndexedDB
    console.log('[SW] Removed offline action:', actionId);
}

/**
 * Push notification handling
 */
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from LeadFinder',
                        icon: '/static/images/4Front2market_logo.png',
                        badge: '/static/images/4Front2market_logo.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('LeadFinder', options)
    );
});

/**
 * Notification click handling
 */
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling for communication with main thread
self.addEventListener('message', event => {
    console.log('[SW] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(STATIC_CACHE_NAME)
                .then(cache => cache.addAll(event.data.urls))
        );
    }
}); 