# LeadFinder API Documentation

## Overview

LeadFinder provides a comprehensive API for lead discovery and management through a Flask web application. This document describes all available endpoints, their parameters, and responses.

## Base URL

```
http://localhost:5050
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Endpoints

### 1. Lead Management

#### GET `/`
**Description:** Display all leads with search interface

**Response:** HTML page with leads table and search form

**Template Variables:**
- `leads`: List of lead objects
- `lead_count`: Total number of leads
- `search_history`: Recent search history
- `ollama_status`: Current Ollama server status
- `engines`: Available search engines
- `selected_engines`: Currently selected engines
- `research_question`: Default research question

---

#### GET `/export`
**Description:** Export all leads to Excel file

**Response:** Excel file download (`leads_export.xlsx`)

**Features:**
- Clickable hyperlinks in Excel
- Formatted columns with proper widths
- All lead data included

---

#### GET `/download_links`
**Description:** Download content from all lead links

**Response:** HTML page with download progress and results

**Features:**
- Downloads HTML content from all lead URLs
- Saves files to configured export folder
- Provides detailed progress feedback

---

#### POST `/delete/<int:lead_id>`
**Description:** Delete a specific lead

**Parameters:**
- `lead_id`: ID of the lead to delete

**Response:** Redirect to leads page or error message

---

#### GET `/leads_by_source/<source>`
**Description:** Filter leads by source

**Parameters:**
- `source`: Source name (e.g., "google", "bing")

**Response:** HTML page with filtered leads

---

### 2. Search Functionality

#### POST `/search`
**Description:** Perform a new search and analyze results

**Form Parameters:**
- `query`: Search query string
- `research_question`: AI analysis question
- `search_type`: Type of search ("articles", "profiles", "both")
- `engines`: List of search engines to use

**Response:** Redirect to leads page with new results

**Process:**
1. Searches selected engines via SerpAPI
2. Extracts text content from result pages
3. Analyzes relevance using Ollama AI
4. Saves relevant leads to database

---

### 3. Ollama AI Management

#### POST `/ollama_check`
**Description:** Check Ollama server status

**Response:** Redirect to leads page with updated status

---

#### GET `/ollama_status`
**Description:** Get Ollama status as JSON

**Response:**
```json
{
  "ok": true,
  "msg": "Ollama och modell 'mistral:latest' är redo."
}
```

---

#### GET `/ollama_models`
**Description:** Get list of available Ollama models

**Response:**
```json
{
  "models": ["mistral:latest", "deepseek-coder:latest"]
}
```

---

#### GET `/ollama_models_ui`
**Description:** Display Ollama model management interface

**Response:** HTML page with model selection interface

**Template Variables:**
- `available_models`: List of available models
- `selected_model`: Currently selected model

---

#### POST `/set_model`
**Description:** Set preferred Ollama model

**Form Parameters:**
- `model_name`: Name of the model to use

**Response:** Redirect to model management page

---

## Data Models

### Lead Object
```json
{
  "id": 1,
  "title": "Example Company",
  "description": "Company description",
  "link": "https://example.com",
  "ai_summary": "AI-generated summary",
  "source": "google",
  "created_at": "2024-01-01 12:00:00"
}
```

### Search History Object
```json
{
  "id": 1,
  "query": "epigenetik pre-diabetes",
  "research_question": "epigenetik och pre-diabetes",
  "search_type": "articles",
  "engines": "google,bing",
  "results_count": 5,
  "created_at": "2024-01-01 12:00:00"
}
```

### Ollama Status Object
```json
{
  "ok": true,
  "msg": "Ollama och modell 'mistral:latest' är redo."
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid parameters"
}
```

### 500 Internal Server Error
```json
{
  "error": "Server error message"
}
```

## Configuration

### Environment Variables
- `SERPAPI_KEY`: SerpAPI authentication key
- `PUBMED_API_KEY`: PubMed API key (future)
- `ORCID_CLIENT_ID`: ORCID client ID (future)
- `ORCID_CLIENT_SECRET`: ORCID client secret (future)

### Configuration File
Main configuration is in `config.py`:
- `OLLAMA_URL`: Ollama API endpoint
- `OLLAMA_MODEL`: Preferred AI model
- `FLASK_HOST`: Web server host
- `FLASK_PORT`: Web server port
- `EXPORT_FOLDER`: Download directory
- `DEFAULT_RESEARCH_QUESTION`: Default AI analysis question

## Rate Limits

- SerpAPI: Based on your subscription plan
- Ollama: No built-in limits (depends on server capacity)
- Flask endpoints: No rate limiting implemented

## Examples

### Search for Companies
```bash
curl -X POST http://localhost:5050/search \
  -d "query=epigenetik pre-diabetes" \
  -d "research_question=epigenetik och pre-diabetes" \
  -d "search_type=articles" \
  -d "engines=google,bing"
```

### Check Ollama Status
```bash
curl http://localhost:5050/ollama_status
```

### Get Available Models
```bash
curl http://localhost:5050/ollama_models
```

### Export Leads
```bash
curl -O http://localhost:5050/export
```

## Future Endpoints

### PubMed Integration
- `GET /pubmed/search` - Search academic articles
- `GET /pubmed/article/<id>` - Get article details

### ORCID Integration
- `GET /orcid/search` - Search researcher profiles
- `GET /orcid/profile/<id>` - Get researcher details

### Advanced Analytics
- `GET /analytics/trends` - Google Trends data
- `GET /analytics/sources` - Source distribution
- `GET /analytics/timeline` - Lead timeline analysis

## Support

For API support and questions:
- Check the main README.md for setup instructions
- Review error logs in the application console
- Ensure Ollama server is running for AI features
- Verify SerpAPI key is valid and has sufficient quota 