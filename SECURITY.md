# Security Guidelines for LeadFinder

## ⚠️ CRITICAL SECURITY NOTICE

**The environment files in this repository may contain sensitive API keys and credentials. These should NEVER be committed to version control.**

## Environment Configuration Security

### Current Status
- ✅ `env.development` - API keys replaced with placeholders
- ✅ `env.testing` - Uses test keys only
- ⚠️ **IMPORTANT**: If you have real API keys in your local environment files, they should be kept private

### Secure Configuration Steps

1. **Never commit real API keys to version control**
   ```bash
   # These files should be in .gitignore and never committed
   env.development
   env.production
   .env
   ```

2. **Use environment variables for production**
   ```bash
   export SERPAPI_KEY="your_real_key_here"
   export FLASK_SECRET_KEY="your_secret_key_here"
   ```

3. **Create local environment files**
   ```bash
   # Copy the template and add your real keys locally
   cp env.development env.development.local
   # Edit env.development.local with your real keys
   # This file should be in .gitignore
   ```

### API Keys Required

- **SerpAPI Key**: For web search functionality
  - Get free key from: https://serpapi.com/
  - Used for: Google, Bing, DuckDuckGo searches

- **Semantic Scholar API Key**: For academic search
  - Get free key from: https://www.semanticscholar.org/product/api
  - Used for: Research paper searches

- **Other API Keys**: Optional for enhanced functionality
  - CORDIS API: EU research funding
  - NIH API: US research funding
  - RunPod API: AI processing

### Security Best Practices

1. **Environment File Management**
   - Use `.env.local` for local development
   - Use environment variables in production
   - Never commit files with real credentials

2. **API Key Rotation**
   - Regularly rotate API keys
   - Monitor API usage for unusual activity
   - Use different keys for development and production

3. **Access Control**
   - Limit API key permissions to minimum required
   - Use read-only keys where possible
   - Monitor and log API usage

4. **Error Handling**
   - Don't expose API keys in error messages
   - Log errors without sensitive data
   - Use generic error messages for users

### Configuration Validation

The application validates required configurations on startup:

```python
# Check if required keys are present
missing_configs = config.validate_required_configs()
if missing_configs:
    print(f"Missing required configurations: {missing_configs}")
```

### Security Checklist

- [ ] No real API keys in version control
- [ ] Environment files in .gitignore
- [ ] Production uses environment variables
- [ ] API keys have minimal required permissions
- [ ] Error messages don't expose sensitive data
- [ ] Regular security audits of dependencies

### Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public issue
2. **DO** contact the maintainers privately
3. **DO** provide detailed reproduction steps
4. **DO** allow time for responsible disclosure

## Recent Security Fixes

### Fixed Issues
- ✅ Removed exposed SerpAPI key from `env.development`
- ✅ Added proper error handling for missing Flask imports
- ✅ Fixed configuration default value handling
- ✅ Updated .gitignore for better security coverage

### Ongoing Improvements
- 🔄 Enhanced logging without sensitive data exposure
- 🔄 Improved error message sanitization
- 🔄 Better configuration validation 