# 📚 LeadFinder API Documentation

## Overview

LeadFinder provides a comprehensive REST API for lead discovery, AI analysis, and research funding. The API supports both synchronous and asynchronous operations, with real-time status monitoring and AutoGPT integration.

## 🔗 Base URL

```
http://localhost:5050
```

## 🔐 Authentication

Currently, the API uses environment-based configuration. API keys are managed through environment variables and the configuration system.

## 📋 API Endpoints

### 🏥 Health & Status

#### Get Application Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "configuration": "valid",
  "autogpt": "ready",
  "missing_configs": []
}
```

#### Get AutoGPT Status
```http
GET /autogpt/status
```

**Response:**
```json
{
  "enabled": true,
  "status": "ready",
  "model": "mistral:latest",
  "last_test": "AutoGPT test completed successfully..."
}
```

### 🔍 Search Endpoints

#### Perform Search
```http
POST /search
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `query` (string, required): Search query
- `research_question` (string, optional): Research question for AI analysis
- `search_type` (string, optional): "articles", "profiles", or "both"
- `use_ai_analysis` (boolean, optional): Enable AI analysis
- `engines[]` (array, optional): Search engines to use

**Response:**
```json
{
  "success": true,
  "message": "Search completed! 5 leads saved.",
  "redirect": "/"
}
```

#### AJAX Search
```http
POST /search_ajax
Content-Type: application/x-www-form-urlencoded
```

**Parameters:** Same as `/search`

**Response:**
```json
{
  "success": true,
  "leads": [
    {
      "title": "Lead Title",
      "snippet": "Lead description...",
      "link": "https://example.com",
      "ai_summary": "AI analysis of the lead...",
      "source": "google"
    }
  ],
  "total_results": 5,
  "saved_count": 5
}
```

### 🤖 AutoGPT Control Panel

#### Test AutoGPT
```http
POST /autogpt/test
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `test_prompt` (string, required): Test prompt
- `model` (string, optional): AI model to use

**Response:**
```json
{
  "success": true,
  "output": "Test response from AutoGPT...",
  "model": "mistral:latest",
  "message": "AutoGPT test completed successfully"
}
```

#### Analyze Text
```http
POST /autogpt/analyze
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `text` (string, required): Text to analyze
- `analysis_type` (string, optional): "general", "lead_relevance", or "company_research"
- `model` (string, optional): AI model to use

**Response:**
```json
{
  "success": true,
  "analysis": "Detailed analysis of the text...",
  "analysis_type": "lead_relevance",
  "model": "mistral:latest"
}
```

#### Perform Research
```http
POST /autogpt/research
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `research_topic` (string, required): Research topic
- `company_name` (string, optional): Company name for lead research
- `industry` (string, optional): Target industry
- `model` (string, optional): AI model to use

**Response:**
```json
{
  "success": true,
  "research": "Comprehensive research results...",
  "topic": "AI in healthcare",
  "model": "mistral:latest"
}
```

### 📊 Lead Management

#### Get All Leads
```http
GET /leads
```

**Query Parameters:**
- `page` (integer, optional): Page number
- `per_page` (integer, optional): Items per page
- `source` (string, optional): Filter by source
- `search` (string, optional): Search in leads

**Response:**
```json
{
  "leads": [
    {
      "id": 1,
      "title": "Lead Title",
      "description": "Lead description",
      "link": "https://example.com",
      "ai_summary": "AI analysis...",
      "source": "google",
      "created_at": "2025-07-18T19:30:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

#### Get Lead Count
```http
GET /leads/count
```

**Response:**
```json
{
  "count": 100
}
```

#### Delete Lead
```http
DELETE /leads/{lead_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Lead deleted successfully"
}
```

#### Export Leads
```http
GET /leads/export
```

**Query Parameters:**
- `format` (string, optional): "excel" or "csv"
- `source` (string, optional): Filter by source

**Response:** File download

### 🔬 Research Funding

#### Search Research Projects
```http
POST /research/search
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `query` (string, required): Search query
- `apis[]` (array, optional): APIs to search
- `max_results` (integer, optional): Maximum results

**Response:**
```json
{
  "query": "epigenetics",
  "results_by_source": {
    "SweCRIS": [
      {
        "id": "project-1",
        "title": "Project Title",
        "description": "Project description...",
        "principal_investigator": "Dr. John Doe",
        "organization": "University of Example",
        "funding_amount": 500000,
        "currency": "SEK",
        "start_date": "2024-01-01",
        "end_date": "2027-12-31",
        "keywords": ["epigenetics", "diabetes"],
        "source": "SweCRIS",
        "url": "https://example.com/project"
      }
    ]
  },
  "total_results": 25,
  "selected_apis": ["SweCRIS", "CORDIS"]
}
```

#### API Research Search
```http
GET /research/api/search
```

**Query Parameters:**
- `query` (string, required): Search query
- `max_results` (integer, optional): Maximum results
- `apis[]` (array, optional): APIs to search

**Response:**
```json
{
  "projects": [
    {
      "id": "project-1",
      "title": "Project Title",
      "description": "Project description...",
      "principal_investigator": "Dr. John Doe",
      "organization": "University of Example",
      "funding_amount": 500000,
      "currency": "SEK",
      "start_date": "2024-01-01",
      "end_date": "2027-12-31",
      "keywords": ["epigenetics", "diabetes"],
      "source": "SweCRIS",
      "url": "https://example.com/project"
    }
  ],
  "total": 25
}
```

### 📚 Publication Search

#### Search Publications
```http
POST /ollama/search
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `query` (string, required): Search query
- `search_type` (string, optional): "articles", "profiles", or "both"
- `sources[]` (array, optional): Sources to search

**Response:**
```json
{
  "publications": [
    {
      "title": "Publication Title",
      "authors": ["Author 1", "Author 2"],
      "abstract": "Abstract text...",
      "doi": "10.1234/example",
      "source": "pubmed",
      "url": "https://example.com/paper"
    }
  ],
  "researchers": [
    {
      "name": "Dr. John Doe",
      "affiliation": "University of Example",
      "orcid": "0000-0000-0000-0000",
      "source": "orcid"
    }
  ]
}
```

### 🎛️ Configuration

#### Get Configuration
```http
GET /config
```

**Response:**
```json
{
  "configs": [
    {
      "key": "SERPAPI_KEY",
      "value": "***",
      "description": "SerpAPI key for Google search",
      "is_secret": true,
      "required": true,
      "source": "Environment"
    }
  ]
}
```

#### Update Configuration
```http
POST /config/update
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `key` (string, required): Configuration key
- `value` (string, required): Configuration value

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

### 🔧 Ollama Management

#### Check Ollama Status
```http
POST /ollama/check
```

**Response:**
```json
{
  "ok": true,
  "msg": "Ollama is running",
  "models": ["mistral:latest", "llama2:latest"]
}
```

#### Get Available Models
```http
GET /ollama/models
```

**Response:**
```json
{
  "models": [
    {
      "name": "mistral:latest",
      "size": "4.1GB",
      "modified_at": "2025-07-18T10:00:00Z"
    }
  ],
  "selected_model": "mistral:latest"
}
```

### 🏭 Lead Workshop

#### Get Workshop Status
```http
GET /lead-workshop/api/status
```

**Response:**
```json
{
  "status": "idle",
  "current_project": null,
  "total_projects": 5
}
```

#### Analyze Leads
```http
POST /lead-workshop/analyze-leads
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `lead_ids[]` (array, required): Lead IDs to analyze
- `analysis_type` (string, optional): Type of analysis

**Response:**
```json
{
  "success": true,
  "analysis": "Analysis results...",
  "project_id": "project-123"
}
```

## 📊 Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### Common Error Codes
- `400`: Bad Request - Invalid parameters
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Permission denied
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - Service temporarily unavailable

### AutoGPT-Specific Errors
- `AUTOGPT_NOT_AVAILABLE`: AutoGPT integration not available
- `MODEL_NOT_FOUND`: Specified AI model not found
- `TIMEOUT_ERROR`: Request timed out
- `ANALYSIS_FAILED`: Text analysis failed
- `RESEARCH_FAILED`: Research operation failed

## 🔄 Rate Limiting

Currently, the API does not implement rate limiting, but it's recommended to:
- Limit requests to reasonable frequencies
- Use appropriate timeouts for long-running operations
- Implement client-side retry logic with exponential backoff

## 📝 Request Examples

### cURL Examples

#### Test AutoGPT
```bash
curl -X POST http://localhost:5050/autogpt/test \
  -d "test_prompt=Hello, this is a test" \
  -d "model=mistral:latest"
```

#### Search for Leads
```bash
curl -X POST http://localhost:5050/search_ajax \
  -d "query=AI in healthcare" \
  -d "use_ai_analysis=on" \
  -d "engines[]=google" \
  -d "engines[]=bing"
```

#### Analyze Text
```bash
curl -X POST http://localhost:5050/autogpt/analyze \
  -d "text=Company description to analyze..." \
  -d "analysis_type=lead_relevance" \
  -d "model=mistral:latest"
```

#### Get Health Status
```bash
curl http://localhost:5050/health
```

### Python Examples

#### Test AutoGPT Connection
```python
import requests

response = requests.post('http://localhost:5050/autogpt/test', data={
    'test_prompt': 'Hello, test',
    'model': 'mistral:latest'
})

if response.status_code == 200:
    result = response.json()
    print(f"Test successful: {result['output']}")
else:
    print(f"Test failed: {response.text}")
```

#### Search for Leads
```python
import requests

response = requests.post('http://localhost:5050/search_ajax', data={
    'query': 'AI in healthcare',
    'use_ai_analysis': 'on',
    'engines': ['google', 'bing']
})

if response.status_code == 200:
    result = response.json()
    print(f"Found {result['total_results']} leads")
    for lead in result['leads']:
        print(f"- {lead['title']}")
```

#### Analyze Text
```python
import requests

response = requests.post('http://localhost:5050/autogpt/analyze', data={
    'text': 'Company description to analyze...',
    'analysis_type': 'lead_relevance',
    'model': 'mistral:latest'
})

if response.status_code == 200:
    result = response.json()
    print(f"Analysis: {result['analysis']}")
```

## 🔮 Future API Features

### Planned Endpoints
- **Webhook support** for real-time notifications
- **Batch operations** for multiple leads
- **Advanced filtering** and sorting options
- **Export templates** customization
- **User management** and authentication
- **API rate limiting** and quotas

### Integration Features
- **OAuth2 authentication** for external integrations
- **GraphQL support** for complex queries
- **WebSocket support** for real-time updates
- **File upload** for bulk data import
- **Scheduled operations** for automated tasks

## 🆘 Support

For API issues:
1. Check the health endpoint: `GET /health`
2. Review application logs: `data/logs/leadfinder.log`
3. Test AutoGPT functionality: `POST /autogpt/test`
4. Verify configuration: `GET /config`
5. Check Ollama status: `POST /ollama/check`

## 📚 Related Documentation

- [Configuration Guide](CONFIGURATION.md)
- [AutoGPT Integration](AUTOGPT_INTEGRATION.md)
- [Development Guide](DEVELOPMENT.md)
- [Deployment Guide](DEPLOYMENT.md) 