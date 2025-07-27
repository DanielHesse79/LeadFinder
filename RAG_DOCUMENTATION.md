# 🧠 RAG (Retrieval-Augmented Generation) Documentation

## Overview

LeadFinder's RAG implementation provides intelligent, context-aware responses by combining the power of large language models with your own knowledge base. This document provides comprehensive information about the RAG system, its components, and how to use it effectively.

## Table of Contents

1. [What is RAG?](#what-is-rag)
2. [Architecture Overview](#architecture-overview)
3. [Components](#components)
4. [Setup and Configuration](#setup-and-configuration)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Data Migration](#data-migration)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Advanced Features](#advanced-features)

## What is RAG?

Retrieval-Augmented Generation (RAG) is an AI technique that enhances language model responses by retrieving relevant information from a knowledge base before generating answers. Instead of relying solely on the model's training data, RAG:

- **Retrieves** relevant documents from your knowledge base
- **Augments** the model's context with this information
- **Generates** responses based on both the model's knowledge and your specific data

### Key Benefits

- **Accuracy**: Responses based on your actual data, not just training data
- **Transparency**: Source citations for every response
- **Freshness**: Reflects your current knowledge base
- **Context**: Understands your specific domain and context
- **Control**: You control what information is available

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Retrieval      │───▶│  RAG Generator  │
│                 │    │  Service        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Vector Store   │    │  Ollama Service │
                       │  (ChromaDB)     │    │  (Mistral)      │
                       └─────────────────┘    └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │  Ingestion      │
                       │  Service        │
                       └─────────────────┘
                                ▲
                                │
                       ┌─────────────────┐
                       │  Documents      │
                       │  (Leads, Papers,│
                       │   Search Results)│
                       └─────────────────┘
```

## Components

### 1. Ingestion Service (`services/ingestion_service.py`)

**Purpose**: Processes and prepares documents for the vector store.

**Key Features**:
- Document parsing and preprocessing
- Smart text chunking with overlap
- Embedding generation using SentenceTransformers
- Metadata preservation and indexing
- Batch processing capabilities

**Usage Example**:
```python
from services.ingestion_service import IngestionService

ingestion = IngestionService()

# Ingest a single document
result = ingestion.ingest_document(
    content="Your document content...",
    source="research_paper",
    metadata={"title": "AI in Healthcare", "author": "Dr. Smith"}
)

# Batch ingest multiple documents
documents = [
    {"content": "Doc 1...", "source": "lead", "metadata": {...}},
    {"content": "Doc 2...", "source": "paper", "metadata": {...}}
]
results = ingestion.batch_ingest(documents)
```

### 2. Vector Store Service (`services/vector_store_service.py`)

**Purpose**: Manages the ChromaDB vector database for document storage and retrieval.

**Key Features**:
- Connection pooling for efficient resource management
- Document upsertion with metadata
- Top-k similarity search
- Collection management and statistics
- Backup and restore capabilities

**Usage Example**:
```python
from services.vector_store_service import VectorStoreService

vector_store = VectorStoreService()

# Search for similar documents
results = vector_store.search(
    query="machine learning applications",
    top_k=5,
    similarity_threshold=0.7
)

# Get collection statistics
stats = vector_store.get_stats()
print(f"Total documents: {stats.total_documents}")
```

### 3. Retrieval Service (`services/retrieval_service.py`)

**Purpose**: Orchestrates the retrieval process, combining vector search with traditional search.

**Key Features**:
- Query embedding generation
- Vector similarity search
- Hybrid search capabilities
- Confidence scoring
- Fallback mechanisms

**Usage Example**:
```python
from services.retrieval_service import RetrievalService

retrieval = RetrievalService()

# Retrieve context for a query
result = retrieval.retrieve_context(
    query="What are the latest AI trends?",
    top_k=5,
    method="hybrid"
)

print(f"Found {len(result.chunks)} relevant chunks")
print(f"Confidence: {result.confidence_score}")
```

### 4. RAG Generator (`services/rag_generator.py`)

**Purpose**: Generates AI responses using retrieved context and the Ollama model.

**Key Features**:
- Context-aware prompt building
- Response generation with source citations
- Context truncation for model limits
- Confidence scoring
- Error handling and fallbacks

**Usage Example**:
```python
from services.rag_generator import RAGGenerator

generator = RAGGenerator()

# Generate a RAG response
result = generator.generate_with_context(
    query="What are the latest AI trends in healthcare?",
    top_k=5
)

print(f"Response: {result.response}")
print(f"Sources: {result.sources}")
print(f"Confidence: {result.confidence_score}")
```

### 5. Embedding Service (`services/embedding_service.py`)

**Purpose**: Generates vector embeddings for text using SentenceTransformers.

**Key Features**:
- Multiple embedding model support
- Batch processing
- Caching for performance
- Model management and health checks

**Usage Example**:
```python
from services.embedding_service import EmbeddingService

embedding_service = EmbeddingService()

# Generate embeddings
embeddings = embedding_service.generate_embeddings([
    "Text 1",
    "Text 2",
    "Text 3"
])

# Check service health
health = embedding_service.health_check()
```

## Setup and Configuration

### Prerequisites

1. **Python Dependencies**:
   ```bash
   pip install chromadb sentence-transformers numpy
   ```

2. **Ollama Setup**:
   ```bash
   ollama serve
   ollama pull mistral:latest
   ```

3. **ChromaDB** (optional, for production):
   ```bash
   pip install chromadb
   # ChromaDB runs in-memory by default
   ```

### Environment Configuration

Add these variables to your environment file:

```bash
# RAG Core Configuration
RAG_ENABLED=True
RAG_MODEL=mistral:latest
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Document Processing
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_SIMILARITY_THRESHOLD=0.7
RAG_TOP_K=5

# ChromaDB Configuration
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_COLLECTION=leadfinder_docs

# Performance Settings
RAG_CACHE_TTL=3600
RAG_MAX_CONTEXT_LENGTH=4000
```

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `RAG_CHUNK_SIZE` | 1000 | Size of document chunks in characters |
| `RAG_CHUNK_OVERLAP` | 200 | Overlap between chunks |
| `RAG_SIMILARITY_THRESHOLD` | 0.7 | Minimum similarity score for retrieval |
| `RAG_TOP_K` | 5 | Number of chunks to retrieve |
| `RAG_MAX_CONTEXT_LENGTH` | 4000 | Maximum context length for generation |

## Usage Guide

### Web Interface

1. **Access the RAG Search Interface**:
   - Navigate to `http://localhost:5051/rag/search`
   - Or click "RAG Search" in the navigation

2. **Using the Search Form**:
   - Enter your question in the query field
   - Adjust `top_k` (number of results)
   - Select retrieval method (vector, hybrid, traditional)
   - Click "Search"

3. **Understanding Results**:
   - **AI Response**: The generated answer
   - **Confidence Score**: How confident the system is
   - **Sources**: Links to source documents
   - **Context Snippets**: Retrieved document chunks

### API Usage

#### Basic RAG Search

```bash
curl -X POST http://localhost:5051/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest AI trends in healthcare?",
    "top_k": 5,
    "retrieval_method": "hybrid"
  }'
```

**Response**:
```json
{
  "success": true,
  "response": "Based on the available information...",
  "sources": [
    {
      "title": "AI in Healthcare Research",
      "source": "research_paper",
      "relevance_score": 0.85
    }
  ],
  "confidence_score": 0.78,
  "processing_time": 2.3,
  "chunks_retrieved": 5
}
```

#### Context Retrieval Only

```bash
curl -X POST http://localhost:5051/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning applications",
    "top_k": 3
  }'
```

#### Document Ingestion

```bash
curl -X POST http://localhost:5051/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "content": "Your document content...",
        "source": "research_paper",
        "metadata": {
          "title": "AI in Healthcare",
          "author": "Dr. Smith",
          "year": 2024
        }
      }
    ]
  }'
```

### Python Integration

```python
import requests

# RAG Search
response = requests.post('http://localhost:5051/rag/search', json={
    'query': 'What are the latest AI trends?',
    'top_k': 5,
    'retrieval_method': 'hybrid'
})

if response.status_code == 200:
    result = response.json()
    print(f"Response: {result['response']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Sources: {len(result['sources'])}")
```

## API Reference

### POST /rag/search

Main RAG search endpoint that retrieves context and generates responses.

**Request Body**:
```json
{
  "query": "string (required)",
  "top_k": "integer (optional, default: 5)",
  "retrieval_method": "string (optional, default: 'hybrid')",
  "similarity_threshold": "float (optional, default: 0.7)"
}
```

**Response**:
```json
{
  "success": "boolean",
  "response": "string",
  "sources": [
    {
      "title": "string",
      "source": "string",
      "relevance_score": "float",
      "chunk_preview": "string"
    }
  ],
  "confidence_score": "float",
  "processing_time": "float",
  "chunks_retrieved": "integer",
  "error": "string (if success: false)"
}
```

### POST /rag/retrieve

Retrieve context only, without generating a response.

**Request Body**:
```json
{
  "query": "string (required)",
  "top_k": "integer (optional, default: 5)",
  "similarity_threshold": "float (optional, default: 0.7)"
}
```

**Response**:
```json
{
  "success": "boolean",
  "chunks": [
    {
      "content": "string",
      "source": "string",
      "metadata": "object",
      "similarity_score": "float"
    }
  ],
  "confidence_score": "float",
  "processing_time": "float",
  "error": "string (if success: false)"
}
```

### POST /rag/ingest

Ingest documents into the knowledge base.

**Request Body**:
```json
{
  "documents": [
    {
      "content": "string (required)",
      "source": "string (required)",
      "metadata": "object (optional)"
    }
  ]
}
```

**Response**:
```json
{
  "success": "boolean",
  "ingested_count": "integer",
  "errors": ["string"],
  "processing_time": "float"
}
```

### GET /rag/status

Get RAG system status and health information.

**Response**:
```json
{
  "status": "healthy|degraded|unhealthy",
  "components": {
    "embedding_service": "string",
    "vector_store": "string",
    "ollama_service": "string"
  },
  "stats": {
    "total_documents": "integer",
    "total_chunks": "integer",
    "collection_size": "string"
  }
}
```

### GET /rag/stats

Get detailed usage statistics.

**Response**:
```json
{
  "total_searches": "integer",
  "total_ingestions": "integer",
  "average_response_time": "float",
  "success_rate": "float",
  "popular_queries": ["string"],
  "storage_usage": "string"
}
```

## Data Migration

### Migrating Existing Data

The migration script processes existing LeadFinder data and populates the RAG knowledge base:

```bash
python migrate_existing_data_to_rag.py
```

**What gets migrated**:
- **Leads**: Company information, descriptions, analysis results
- **Search History**: Previous search queries and results
- **Workshop Analyses**: Project-based research and insights
- **Research Papers**: Publication data and abstracts

**Migration Process**:
1. **Backup**: Creates backup of existing data
2. **Processing**: Converts data to appropriate formats
3. **Chunking**: Breaks documents into optimal chunks
4. **Embedding**: Generates vector embeddings
5. **Storage**: Stores in ChromaDB with metadata
6. **Verification**: Validates migration success

### Manual Data Ingestion

For custom data ingestion:

```python
from services.ingestion_service import IngestionService

ingestion = IngestionService()

# Ingest custom documents
documents = [
    {
        "content": "Your custom content...",
        "source": "custom_source",
        "metadata": {"category": "research", "priority": "high"}
    }
]

results = ingestion.batch_ingest(documents)
print(f"Ingested {len(results)} documents")
```

## Troubleshooting

### Common Issues

#### 1. "RAG service unavailable"

**Symptoms**: 503 errors on RAG endpoints

**Solutions**:
- Check if Ollama is running: `ollama serve`
- Verify model is available: `ollama list`
- Check embedding service: `curl http://localhost:5051/rag/status`

#### 2. "No relevant documents found"

**Symptoms**: Empty responses or low confidence scores

**Solutions**:
- Verify data migration completed successfully
- Check vector store statistics: `curl http://localhost:5051/rag/stats`
- Lower similarity threshold in configuration
- Ingest more relevant documents

#### 3. "Slow response times"

**Symptoms**: Long processing times for queries

**Solutions**:
- Reduce `top_k` value
- Enable embedding caching
- Optimize chunk size settings
- Check system resources

#### 4. "Embedding service errors"

**Symptoms**: Errors related to sentence-transformers

**Solutions**:
- Install required dependencies: `pip install sentence-transformers`
- Check model availability
- Restart the application

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
export RAG_DEBUG=True
export LOG_LEVEL=DEBUG
```

### Health Checks

Monitor system health:

```bash
# Overall RAG status
curl http://localhost:5051/rag/status

# Component health
curl http://localhost:5051/rag/health

# Usage statistics
curl http://localhost:5051/rag/stats
```

## Performance Optimization

### Configuration Tuning

#### For Speed
```bash
RAG_CHUNK_SIZE=500          # Smaller chunks, faster retrieval
RAG_TOP_K=3                 # Fewer results, faster processing
RAG_CACHE_TTL=7200          # Longer cache, fewer embeddings
```

#### For Accuracy
```bash
RAG_CHUNK_SIZE=1500         # Larger chunks, more context
RAG_TOP_K=10                # More results, better coverage
RAG_SIMILARITY_THRESHOLD=0.8 # Higher threshold, better relevance
```

### Caching Strategy

The RAG system implements multiple caching layers:

1. **Embedding Cache**: Caches generated embeddings
2. **Vector Search Cache**: Caches similarity search results
3. **Response Cache**: Caches generated responses

### Monitoring Performance

Track performance metrics:

```python
# Get performance statistics
stats = requests.get('http://localhost:5051/rag/stats').json()

print(f"Average response time: {stats['average_response_time']}s")
print(f"Success rate: {stats['success_rate']}%")
print(f"Total searches: {stats['total_searches']}")
```

## Advanced Features

### Custom Embedding Models

Configure different embedding models:

```bash
# For better quality (slower)
RAG_EMBEDDING_MODEL=all-mpnet-base-v2

# For faster processing
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2

# For multilingual support
RAG_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

### Hybrid Search

Combine vector search with traditional keyword search:

```python
# Use hybrid retrieval
result = retrieval.retrieve_context(
    query="machine learning applications",
    method="hybrid",
    top_k=5
)
```

### Custom Prompts

Modify the RAG generation prompts for specific use cases:

```python
from services.rag_generator import RAGGenerator

generator = RAGGenerator()

# Custom prompt template
custom_prompt = """
Based on the following context, answer the question.
Context: {context}
Question: {query}
Answer:"""

result = generator.generate_with_context(
    query="Your question",
    custom_prompt=custom_prompt
)
```

### Batch Processing

Process multiple queries efficiently:

```python
from services.rag_generator import RAGGenerator

generator = RAGGenerator()

queries = [
    "What are AI trends?",
    "How does machine learning work?",
    "What is deep learning?"
]

results = generator.batch_generate(queries)
```

### Export and Backup

Export your knowledge base:

```python
from services.vector_store_service import VectorStoreService

vector_store = VectorStoreService()

# Export collection
vector_store.backup_collection("backup_2024_01")

# Restore collection
vector_store.restore_collection("backup_2024_01")
```

## Integration Examples

### Flask Application Integration

```python
from flask import Flask, request, jsonify
from services.rag_generator import RAGGenerator

app = Flask(__name__)
rag_generator = RAGGenerator()

@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    query = data.get('question')
    
    try:
        result = rag_generator.generate_with_context(query)
        return jsonify({
            'answer': result.response,
            'sources': result.sources,
            'confidence': result.confidence_score
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Streamlit Dashboard

```python
import streamlit as st
import requests

st.title("RAG Search Dashboard")

query = st.text_input("Ask a question:")
if st.button("Search"):
    response = requests.post('http://localhost:5051/rag/search', json={
        'query': query,
        'top_k': 5
    })
    
    if response.status_code == 200:
        result = response.json()
        st.write("**Answer:**", result['response'])
        st.write("**Confidence:**", f"{result['confidence_score']:.2f}")
        
        st.write("**Sources:**")
        for source in result['sources']:
            st.write(f"- {source['title']} ({source['relevance_score']:.2f})")
```

### Jupyter Notebook

```python
import requests
import pandas as pd

def rag_search(query, top_k=5):
    response = requests.post('http://localhost:5051/rag/search', json={
        'query': query,
        'top_k': top_k
    })
    return response.json()

# Search and display results
result = rag_search("What are the latest AI trends?")

print("Answer:", result['response'])
print(f"Confidence: {result['confidence_score']:.2f}")

# Create a DataFrame of sources
sources_df = pd.DataFrame(result['sources'])
sources_df
```

## Best Practices

### Document Preparation

1. **Clean Content**: Remove formatting artifacts and irrelevant text
2. **Structured Metadata**: Include title, author, date, and category
3. **Appropriate Chunking**: Balance chunk size for context vs. retrieval
4. **Source Diversity**: Include various types of documents

### Query Optimization

1. **Be Specific**: Use detailed, specific questions
2. **Use Keywords**: Include relevant technical terms
3. **Context Matters**: Provide relevant context in queries
4. **Iterative Refinement**: Refine queries based on results

### System Maintenance

1. **Regular Backups**: Backup your knowledge base regularly
2. **Monitor Performance**: Track response times and success rates
3. **Update Content**: Keep your knowledge base current
4. **Optimize Settings**: Tune configuration based on usage patterns

### Security Considerations

1. **Input Validation**: Validate all user inputs
2. **Access Control**: Implement appropriate access controls
3. **Data Privacy**: Ensure sensitive data is properly handled
4. **Audit Logging**: Log all RAG interactions for compliance

## Support and Resources

### Getting Help

1. **Check Logs**: Review application logs for errors
2. **Health Checks**: Use status endpoints to diagnose issues
3. **Documentation**: Refer to this documentation and README
4. **Community**: Check GitHub issues and discussions

### Useful Commands

```bash
# Check RAG system status
curl http://localhost:5051/rag/status

# View system statistics
curl http://localhost:5051/rag/stats

# Test RAG functionality
python test_rag_implementation.py

# Run performance tests
python test_rag_implementation.py --performance

# Migrate existing data
python migrate_existing_data_to_rag.py
```

### Monitoring and Alerts

Set up monitoring for:
- Response times
- Success rates
- System health
- Storage usage
- Error rates

This comprehensive RAG documentation should help you understand, configure, and effectively use the RAG capabilities in LeadFinder. 