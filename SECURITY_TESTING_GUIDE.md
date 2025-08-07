# 🔒 LeadFinder Security Testing Guide

## Overview

This guide provides comprehensive testing procedures for all security features implemented in LeadFinder. Follow these tests to ensure the application is secure and functioning correctly.

## Prerequisites

- LeadFinder application running locally
- Browser developer tools enabled
- Network monitoring tools (optional)
- Security testing tools (optional)

## 1. Content Security Policy (CSP) Testing

### Test 1.1: CSP Header Verification
```bash
# Check CSP headers
curl -I http://localhost:5051/ | grep -i "content-security-policy"
```

**Expected Result**: CSP header should be present with strict directives.

### Test 1.2: XSS Prevention
```javascript
// Test in browser console
// Try to inject script
document.body.innerHTML = '<script>alert("xss")</script>';
```

**Expected Result**: Script should not execute due to CSP restrictions.

### Test 1.3: Inline Script Blocking
```html
<!-- Test in browser console -->
<script>console.log('This should be blocked');</script>
```

**Expected Result**: Inline scripts should be blocked by CSP.

## 2. CSRF Protection Testing

### Test 2.1: CSRF Token Presence
```javascript
// Check if CSRF token is present
const token = document.querySelector('meta[name="csrf-token"]');
console.log('CSRF Token:', token ? token.getAttribute('content') : 'Not found');
```

**Expected Result**: CSRF token should be present in meta tag.

### Test 2.2: Form CSRF Protection
```javascript
// Check if forms have CSRF tokens
document.querySelectorAll('form').forEach(form => {
    const csrfInput = form.querySelector('input[name="csrf_token"]');
    console.log('Form CSRF:', csrfInput ? 'Present' : 'Missing');
});
```

**Expected Result**: All forms should have CSRF tokens.

### Test 2.3: AJAX CSRF Protection
```javascript
// Test AJAX request without CSRF token
fetch('/api/test', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ test: 'data' })
}).then(response => {
    console.log('Response status:', response.status);
});
```

**Expected Result**: Should return 400 Bad Request without CSRF token.

## 3. XSS Prevention Testing

### Test 3.1: HTML Sanitization
```javascript
// Test sanitizeHTML function
const maliciousInput = '<script>alert("xss")</script><img src="x" onerror="alert(1)">';
const sanitized = sanitizeHTML(maliciousInput);
console.log('Sanitized:', sanitized);
```

**Expected Result**: Script tags and event handlers should be removed.

### Test 3.2: Safe HTML Insertion
```javascript
// Test safeInsertHTML function
const element = document.createElement('div');
const content = '<script>alert("xss")</script>Hello World';
safeInsertHTML(element, content, false);
console.log('Safe content:', element.textContent);
```

**Expected Result**: Script should be escaped, only text content should remain.

## 4. Input Validation Testing

### Test 4.1: Form Validation
```javascript
// Test form validation
const form = document.querySelector('#search-form');
const isValid = validateForm(form);
console.log('Form valid:', isValid);
```

**Expected Result**: Should return false for forms with empty required fields.

### Test 4.2: Required Field Validation
```javascript
// Test required field validation
const requiredFields = form.querySelectorAll('[required]');
requiredFields.forEach(field => {
    field.value = '';
    field.classList.remove('is-invalid');
    validateForm(form);
    console.log(`${field.name} valid:`, !field.classList.contains('is-invalid'));
});
```

**Expected Result**: Empty required fields should show validation errors.

## 5. Security Headers Testing

### Test 5.1: Security Headers Check
```bash
# Check all security headers
curl -I http://localhost:5051/ | grep -E "(X-Content-Type-Options|X-Frame-Options|X-XSS-Protection|Referrer-Policy)"
```

**Expected Result**: All security headers should be present.

### Test 5.2: X-Frame-Options Test
```html
<!-- Try to embed in iframe -->
<iframe src="http://localhost:5051/" width="500" height="300"></iframe>
```

**Expected Result**: Page should not load in iframe due to DENY policy.

## 6. Service Worker Security Testing

### Test 6.1: Service Worker Registration
```javascript
// Check if service worker is registered
navigator.serviceWorker.getRegistrations().then(registrations => {
    console.log('Service Workers:', registrations.length);
    registrations.forEach(reg => {
        console.log('SW State:', reg.active ? 'Active' : 'Inactive');
    });
});
```

**Expected Result**: Service worker should be registered and active.

### Test 6.2: Offline Functionality
```javascript
// Test offline functionality
// 1. Disconnect network
// 2. Try to access cached pages
// 3. Check if offline page is shown
```

**Expected Result**: Cached pages should load offline, uncached pages should show offline page.

## 7. API Security Testing

### Test 7.1: API Authentication
```javascript
// Test API endpoints without authentication
fetch('/api/leads/1', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' }
}).then(response => {
    console.log('Delete response:', response.status);
});
```

**Expected Result**: Should return 401 or 403 for unauthorized requests.

### Test 7.2: SQL Injection Prevention
```javascript
// Test SQL injection attempts
const maliciousQuery = "'; DROP TABLE leads; --";
fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: maliciousQuery })
}).then(response => {
    console.log('SQL injection test response:', response.status);
});
```

**Expected Result**: Should handle malicious input safely without errors.

## 8. PWA Security Testing

### Test 8.1: Manifest Security
```javascript
// Check manifest for security issues
fetch('/static/manifest.json')
    .then(response => response.json())
    .then(manifest => {
        console.log('Manifest scope:', manifest.scope);
        console.log('Manifest permissions:', manifest.permissions);
    });
```

**Expected Result**: Manifest should have appropriate scope and permissions.

### Test 8.2: HTTPS Requirement
```javascript
// Check if running on HTTPS (for production)
console.log('Protocol:', window.location.protocol);
console.log('Is secure:', window.location.protocol === 'https:');
```

**Expected Result**: Should be HTTPS in production.

## 9. Session Security Testing

### Test 9.1: Session Management
```javascript
// Check session cookies
document.cookie.split(';').forEach(cookie => {
    console.log('Cookie:', cookie.trim());
});
```

**Expected Result**: Session cookies should have secure flags in production.

### Test 9.2: Session Timeout
```javascript
// Test session timeout (requires manual testing)
// 1. Login to application
// 2. Wait for session timeout
// 3. Try to access protected page
```

**Expected Result**: Should redirect to login after session timeout.

## 10. File Upload Security Testing

### Test 10.1: File Type Validation
```javascript
// Test file upload with malicious file
const maliciousFile = new File(['malicious content'], 'test.exe', { type: 'application/x-msdownload' });
const formData = new FormData();
formData.append('file', maliciousFile);

fetch('/api/upload', {
    method: 'POST',
    body: formData
}).then(response => {
    console.log('File upload response:', response.status);
});
```

**Expected Result**: Should reject executable files.

### Test 10.2: File Size Limits
```javascript
// Test large file upload
const largeFile = new File(['x'.repeat(10 * 1024 * 1024)], 'large.txt', { type: 'text/plain' });
const formData = new FormData();
formData.append('file', largeFile);

fetch('/api/upload', {
    method: 'POST',
    body: formData
}).then(response => {
    console.log('Large file upload response:', response.status);
});
```

**Expected Result**: Should reject files larger than limit.

## 11. Error Handling Security Testing

### Test 11.1: Error Information Disclosure
```javascript
// Test error handling
fetch('/api/nonexistent-endpoint')
    .then(response => response.text())
    .then(data => {
        console.log('Error response:', data);
        // Check if sensitive information is exposed
    });
```

**Expected Result**: Should not expose sensitive information in error messages.

### Test 11.2: Stack Trace Prevention
```javascript
// Trigger an error and check response
fetch('/api/test-error')
    .then(response => response.text())
    .then(data => {
        console.log('Error details:', data);
        // Should not contain stack traces
    });
```

**Expected Result**: Should not include stack traces in production.

## 12. Rate Limiting Testing

### Test 12.1: API Rate Limiting
```javascript
// Test rate limiting
for (let i = 0; i < 100; i++) {
    fetch('/api/test')
        .then(response => {
            if (response.status === 429) {
                console.log('Rate limited at request:', i);
            }
        });
}
```

**Expected Result**: Should return 429 after exceeding rate limit.

## Automated Security Testing

### Run Security Tests
```bash
# Install security testing tools
npm install -g security-checker

# Run security scan
security-checker http://localhost:5051/

# Run OWASP ZAP scan (if available)
zap-cli quick-scan --self-contained --start-url http://localhost:5051/
```

## Manual Security Checklist

- [ ] CSP headers are present and strict
- [ ] CSRF tokens are included in all forms
- [ ] XSS prevention is working
- [ ] Input validation is active
- [ ] Security headers are set
- [ ] Service worker is registered
- [ ] PWA manifest is secure
- [ ] API endpoints are protected
- [ ] File uploads are validated
- [ ] Error messages don't leak information
- [ ] Rate limiting is active
- [ ] Session management is secure

## Reporting Security Issues

If you find security vulnerabilities:

1. **Do not** publicly disclose the issue
2. Report to the development team privately
3. Include detailed reproduction steps
4. Provide proof-of-concept if possible
5. Allow reasonable time for fixes

## Security Best Practices

1. **Regular Testing**: Run security tests weekly
2. **Dependency Updates**: Keep dependencies updated
3. **Log Monitoring**: Monitor security logs
4. **Access Control**: Review user permissions regularly
5. **Backup Security**: Ensure backups are secure
6. **Incident Response**: Have a plan for security incidents

## Tools and Resources

- **OWASP ZAP**: Web application security scanner
- **Burp Suite**: Web application security testing
- **Security Headers**: Check security headers
- **Mozilla Observatory**: Security scanning tool
- **Lighthouse**: PWA and security auditing

## Conclusion

Regular security testing is essential for maintaining the integrity of the LeadFinder application. This guide should be used as part of the development and deployment process to ensure all security features are working correctly.

Remember: Security is an ongoing process, not a one-time task. Regular testing and updates are crucial for maintaining a secure application. 