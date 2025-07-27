# 🚀 RAG Quick Start Guide

Get started with LeadFinder's RAG (Retrieval-Augmented Generation) capabilities in 5 minutes!

## Prerequisites

✅ **Python 3.8+** installed  
✅ **Ollama** with Mistral model  
✅ **LeadFinder** application running  

## Step 1: Install Dependencies

The RAG dependencies are already included in `requirements.txt`. If you haven't installed them yet:

```bash
pip install chromadb sentence-transformers numpy
```

## Step 2: Start Ollama

Make sure Ollama is running with the Mistral model:

```bash
# Start Ollama service
ollama serve

# Pull Mistral model (if not already installed)
ollama pull mistral:latest
```

## Step 3: Configure RAG

Add these environment variables to your `.env` file:

```bash
# RAG Configuration
RAG_ENABLED=True
RAG_MODEL=mistral:latest
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_SIMILARITY_THRESHOLD=0.7
RAG_TOP_K=5
```

## Step 4: Start LeadFinder

Start the application:

```bash
./start_app.sh development
```

## Step 5: Migrate Existing Data

Populate your RAG knowledge base with existing LeadFinder data:

```bash
python migrate_existing_data_to_rag.py
```

This will:
- Process existing leads, search history, and workshop analyses
- Generate embeddings and store them in ChromaDB
- Verify the migration was successful

## Step 6: Test RAG Search

### Web Interface

1. Open your browser and go to: `http://localhost:5051/rag/search`
2. Enter a question like: "What are the latest AI trends in healthcare?"
3. Click "Search" and see the AI-generated response with sources!

### API Testing

Test the RAG API directly:

```bash
curl -X POST http://localhost:5051/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest AI trends?",
    "top_k": 5
  }'
```

### Python Testing

```python
import requests

response = requests.post('http://localhost:5051/rag/search', json={
    'query': 'What are the latest AI trends?',
    'top_k': 5
})

if response.status_code == 200:
    result = response.json()
    print("Answer:", result['response'])
    print("Confidence:", result['confidence_score'])
    print("Sources:", len(result['sources']))
```

## Step 7: Verify Everything Works

Check the RAG system status:

```bash
# Check overall status
curl http://localhost:5051/rag/status

# View statistics
curl http://localhost:5051/rag/stats

# Run comprehensive tests
python test_rag_implementation.py
```

## What You Can Do Now

### 🧠 **Ask Questions**
- Get AI-generated answers based on your knowledge base
- Receive source citations for every response
- See confidence scores for response quality

### 📚 **Ingest New Documents**
```bash
curl -X POST http://localhost:5051/rag/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "content": "Your document content...",
        "source": "research_paper",
        "metadata": {"title": "AI in Healthcare", "author": "Dr. Smith"}
      }
    ]
  }'
```

### 🔍 **Retrieve Context Only**
```bash
curl -X POST http://localhost:5051/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning applications",
    "top_k": 3
  }'
```

## Troubleshooting

### Common Issues

**"RAG service unavailable"**
- Check if Ollama is running: `ollama serve`
- Verify model: `ollama list | grep mistral`

**"No relevant documents found"**
- Run data migration: `python migrate_existing_data_to_rag.py`
- Check status: `curl http://localhost:5051/rag/status`

**"Slow response times"**
- Reduce `top_k` in your query
- Check system resources
- Enable caching in configuration

### Get Help

- **Status Check**: `curl http://localhost:5051/rag/status`
- **Health Check**: `curl http://localhost:5051/rag/health`
- **Statistics**: `curl http://localhost:5051/rag/stats`
- **Logs**: Check `data/logs/leadfinder.log`

## Next Steps

1. **Explore the Web Interface**: Try different queries and settings
2. **Ingest Your Own Documents**: Add your research papers, reports, or notes
3. **Customize Configuration**: Adjust chunk sizes, similarity thresholds, etc.
4. **Read Full Documentation**: See `RAG_DOCUMENTATION.md` for advanced features
5. **Integrate with Your Workflow**: Use the API in your own applications

## Example Queries to Try

- "What companies are working on AI in healthcare?"
- "What are the latest research trends in machine learning?"
- "What funding opportunities exist for AI projects?"
- "What are the key challenges in implementing AI solutions?"
- "What are the best practices for AI project management?"

## Performance Tips

- **For Speed**: Use smaller `top_k` values (3-5)
- **For Accuracy**: Use larger `top_k` values (8-10)
- **For Relevance**: Increase similarity threshold (0.8+)
- **For Coverage**: Decrease similarity threshold (0.6-)

---

🎉 **Congratulations!** You're now using RAG-powered search in LeadFinder. The system will provide intelligent, context-aware responses based on your knowledge base. 