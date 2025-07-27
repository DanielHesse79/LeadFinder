# 📚 LeadFinder API Documentation

## Overview

LeadFinder provides a comprehensive REST API for lead discovery, AI analysis, research funding, and RAG (Retrieval-Augmented Generation). The API supports both synchronous and asynchronous operations, with real-time status monitoring, AutoGPT integration, and advanced RAG capabilities.

## 🔗 Base URL

```
http://localhost:5051
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
  "timestamp": "2025-07-28T10:30:00Z",
  "system": {
    "cpu_usage": 15.2,
    "memory_usage": 45.8,
    "disk_usage": 23.1,
    "network_active": true
  },
  "application": {
    "database_pool": {
      "active_connections": 2,
      "total_connections": 5,
      "max_connections": 10,
      "status": "healthy"
    },
    "cache": {
      "entries": 45,
      "hit_rate": 78.5,
      "memory_usage": "2.3MB",
      "status": "healthy"
    },
    "error_handling": {
      "total_errors": 3,
      "error_rate": 0.1,
      "last_error": "2025-07-28T10:25:00Z",
      "status": "healthy"
    },
    "search_services": {
      "available_services": 8,
      "response_time": 1.2,
      "status": "healthy"
    },
    "rag_system": {
      "status": "healthy",
      "vector_store": "connected",
      "embedding_service": "available",
      "total_documents": 1250
    }
  },
  "alerts": [],
  "configuration": "valid",
  "autogpt": "ready",
  "rag": "ready"
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
  "last_test": "AutoGPT test completed successfully...",
  "response_time": 2.3,
  "error_rate": 0.02
}
```

#### Get RAG Status
```http
GET /rag/status
```

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "embedding_service": "available",
    "vector_store": "connected",
    "ollama_service": "ready"
  },
  "stats": {
    "total_documents": 1250,
    "total_chunks": 3420,
    "collection_size": "45.2MB"
  },
  "performance": {
    "average_response_time": 1.8,
    "success_rate": 0.95,
    "cache_hit_rate": 0.78
  }
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
- `engines[]` (array, optional): Search engines (google, bing, duckduckgo, pubmed)
- `use_ai_analysis` (boolean, optional): Enable AI analysis
- `use_rag_search` (boolean, optional): Enable RAG search
- `rag_top_k` (integer, optional): Number of RAG results (default: 5)
- `rag_method` (string, optional): RAG method (vector, hybrid, conversational)

**Response:**
```json
{
  "success": true,
  "message": "Search completed! 15 leads saved.",
  "saved_count": 15,
  "total_leads": 15,
  "operation_id": "search_12345",
  "rag_results": {
    "documents_found": 8,
    "generated_response": "Based on the search results...",
    "confidence_score": 0.85
  }
}
```

#### AJAX Search with Progress Tracking
```http
POST /search_ajax
Content-Type: application/x-www-form-urlencoded
```

**Parameters:** Same as `/search` with additional progress tracking

**Response:**
```json
{
  "success": true,
  "message": "Search completed! 15 leads saved.",
  "saved_count": 15,
  "total_leads": 15,
  "operation_id": "search_12345",
  "progress": {
    "current_step": "AI Analysis",
    "progress_percentage": 75,
    "estimated_time_remaining": "30s"
  }
}
```

### 🧠 RAG (Retrieval-Augmented Generation) Endpoints

#### RAG Search
```http
POST /rag/search
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "What are the latest AI trends in healthcare?",
  "top_k": 5,
  "retrieval_method": "hybrid",
  "similarity_threshold": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "query": "What are the latest AI trends in healthcare?",
  "response": "Based on the available information, the latest AI trends in healthcare include...",
  "sources": [
    {
      "title": "AI in Healthcare Research",
      "source": "research_paper",
      "relevance_score": 0.85,
      "chunk_preview": "Recent developments in AI-powered diagnostic tools..."
    }
  ],
  "confidence_score": 0.78,
  "processing_time": 2.3,
  "chunks_retrieved": 5,
  "model_used": "mistral:latest",
  "retrieval_method": "hybrid"
}
```

#### Context Retrieval Only
```http
POST /rag/retrieve
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "machine learning applications",
  "top_k": 3,
  "similarity_threshold": 0.7
}
```

**Response:**
```json
{
  "success": true,
  "query": "machine learning applications",
  "context": [
    {
      "content": "Machine learning applications in healthcare...",
      "source": "research_paper",
      "relevance_score": 0.92,
      "metadata": {
        "title": "ML in Healthcare",
        "author": "Dr. Smith",
        "year": 2024
      }
    }
  ],
  "processing_time": 0.5,
  "retrieval_method": "vector"
}
```

#### Document Ingestion
```http
POST /rag/ingest
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_type": "lead",
  "document": {
    "id": 123,
    "title": "AI Healthcare Startup",
    "description": "Company developing AI-powered diagnostic tools...",
    "source": "serp",
    "ai_summary": "High potential for collaboration in medical AI..."
  }
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "lead_123",
  "chunks_created": 3,
  "processing_time": 2.5,
  "embedding_model": "all-MiniLM-L6-v2"
}
```

#### RAG Statistics
```http
GET /rag/stats
```

**Response:**
```json
{
  "total_searches": 1250,
  "total_ingestions": 450,
  "average_response_time": 1.8,
  "success_rate": 0.95,
  "popular_queries": [
    "AI trends",
    "healthcare technology",
    "machine learning applications"
  ],
  "storage_usage": "45.2MB",
  "embedding_model": "all-MiniLM-L6-v2"
}
```

### 🤖 AutoGPT Endpoints

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
  "test_result": "AutoGPT test completed successfully...",
  "model": "mistral:latest",
  "response_time": 2.3
}
```

#### Analyze Text
```http
POST /autogpt/analyze
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `text` (string, required): Text to analyze
- `analysis_type` (string, optional): Type of analysis (general, lead_relevance, company_research)
- `model` (string, optional): AI model to use

**Response:**
```json
{
  "success": true,
  "analysis": "This company shows strong potential for collaboration...",
  "analysis_type": "lead_relevance",
  "confidence_score": 0.85,
  "processing_time": 3.2
}
```

#### Research Leads
```http
POST /autogpt/research
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `research_topic` (string, required): Research topic
- `company_name` (string, optional): Company name
- `industry` (string, optional): Industry focus

**Response:**
```json
{
  "success": true,
  "research_results": "Comprehensive research analysis...",
  "leads_found": 12,
  "processing_time": 45.2
}
```

### 📊 Lead Management

#### Get All Leads
```http
GET /leads
```

**Response:**
```json
{
  "success": true,
  "leads": [
    {
      "id": 1,
      "title": "AI Healthcare Startup",
      "description": "Company developing AI-powered diagnostic tools...",
      "link": "https://example.com",
      "ai_summary": "High potential for collaboration...",
      "source": "serp",
      "created_at": "2025-07-28T10:30:00Z"
    }
  ],
  "total_count": 150
}
```

#### Export Leads
```http
GET /leads/export
```

**Parameters:**
- `format` (string, optional): Export format (excel, pdf, csv)

**Response:** File download

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

### 🔬 Research Funding

#### Search Funding Opportunities
```http
POST /research/funding
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `query` (string, required): Search query
- `apis[]` (array, optional): APIs to search (swecris, cordis, nih, nsf)

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "title": "AI in Healthcare Research Grant",
      "funding_amount": "500000",
      "deadline": "2025-12-31",
      "source": "swecris",
      "description": "Research grant for AI applications in healthcare..."
    }
  ],
  "total_results": 25
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
- `source` (string, optional): Source (pubmed, semantic_scholar, orcid)

**Response:**
```json
{
  "success": true,
  "publications": [
    {
      "title": "AI Applications in Healthcare",
      "authors": ["Dr. Smith", "Dr. Johnson"],
      "journal": "Nature Medicine",
      "year": 2024,
      "doi": "10.1038/s41591-024-00000-0",
      "abstract": "Recent advances in AI applications..."
    }
  ],
  "total_results": 15
}
```

### ⚙️ Configuration

#### Get Configuration
```http
GET /config
```

**Response:**
```json
{
  "success": true,
  "config": {
    "SERPAPI_KEY": "configured",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "AUTOGPT_ENABLED": true,
    "RAG_ENABLED": true
  }
}
```

#### Update Configuration
```http
POST /config/update
Content-Type: application/json
```

**Request Body:**
```json
{
  "key": "OLLAMA_MODEL",
  "value": "mistral:latest",
  "description": "AI model for text generation"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

## 📊 Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-07-28T10:30:00Z"
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

### RAG-Specific Errors
- `RAG_NOT_AVAILABLE`: RAG system not available
- `VECTOR_STORE_ERROR`: Vector database error
- `EMBEDDING_FAILED`: Embedding generation failed
- `CONTEXT_NOT_FOUND`: No relevant context found
- `GENERATION_FAILED`: Response generation failed

## 🔄 Rate Limiting

Currently, the API does not implement rate limiting, but it's recommended to:
- Limit requests to reasonable frequencies
- Use appropriate timeouts for long-running operations
- Implement client-side retry logic with exponential backoff

## 📝 Request Examples

### cURL Examples

#### Test AutoGPT
```bash
curl -X POST http://localhost:5051/autogpt/test \
  -d "test_prompt=Hello, this is a test" \
  -d "model=mistral:latest"
```

#### Search for Leads
```bash
curl -X POST http://localhost:5051/search_ajax \
  -d "query=AI in healthcare" \
  -d "use_ai_analysis=on" \
  -d "engines[]=google" \
  -d "engines[]=pubmed"
```

#### RAG Search
```bash
curl -X POST http://localhost:5051/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest AI trends?",
    "top_k": 5,
    "retrieval_method": "hybrid"
  }'
```

#### Analyze Text
```bash
curl -X POST http://localhost:5051/autogpt/analyze \
  -d "text=Company description to analyze..." \
  -d "analysis_type=lead_relevance" \
  -d "model=mistral:latest"
```

#### Get Health Status
```bash
curl http://localhost:5051/health
```

### Python Examples

#### Test AutoGPT Connection
```python
import requests

response = requests.post('http://localhost:5051/autogpt/test', data={
    'test_prompt': 'Hello, test',
    'model': 'mistral:latest'
})

if response.status_code == 200:
    result = response.json()
    print(f"Test result: {result['test_result']}")
```

#### Perform RAG Search
```python
import requests

response = requests.post('http://localhost:5051/rag/search', json={
    'query': 'What are the latest AI trends in healthcare?',
    'top_k': 5,
    'retrieval_method': 'hybrid'
})

if response.status_code == 200:
    result = response.json()
    print(f"Response: {result['response']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Sources: {len(result['sources'])}")
```

#### Search for Leads
```python
import requests

response = requests.post('http://localhost:5051/search_ajax', data={
    'query': 'AI healthcare companies',
    'use_ai_analysis': 'on',
    'engines[]': ['google', 'pubmed']
})

if response.status_code == 200:
    result = response.json()
    print(f"Found {result['saved_count']} leads")
```

#### Get Application Health
```python
import requests

response = requests.get('http://localhost:5051/health')
if response.status_code == 200:
    health = response.json()
    print(f"Status: {health['status']}")
    print(f"Database: {health['application']['database_pool']['status']}")
    print(f"RAG: {health['application']['rag_system']['status']}")
```

## 🔒 Security Considerations

### CSRF Protection
All POST requests require CSRF tokens. Include the token from the page's meta tag:
```html
<meta name="csrf-token" content="your_csrf_token_here">
```

### API Key Management
- Store API keys in environment variables
- Never expose keys in client-side code
- Rotate keys regularly
- Monitor API usage for unusual activity

### Input Validation
- All inputs are validated server-side
- SQL injection protection through parameterized queries
- XSS protection through input sanitization
- Rate limiting recommendations for production use

## 📈 Performance Tips

### Optimizing Requests
1. **Use appropriate timeouts** for long-running operations
2. **Implement caching** for repeated requests
3. **Batch operations** when possible
4. **Use async requests** for multiple operations

### Monitoring Performance
1. **Check health endpoint** regularly
2. **Monitor response times** for degradation
3. **Track error rates** and investigate spikes
4. **Monitor resource usage** (CPU, memory, disk)

## 🤝 Contributing

When contributing to the API:

1. **Follow REST conventions** for endpoint design
2. **Add comprehensive error handling** for new endpoints
3. **Include input validation** for all parameters
4. **Add tests** for new functionality
5. **Update documentation** for API changes

## 📄 License

This API is part of the LeadFinder project and follows the same licensing terms. 