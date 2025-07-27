"""
RAG Routes for LeadFinder

This module provides Flask routes for RAG (Retrieval-Augmented Generation) functionality.
"""

from flask import Blueprint, request, jsonify, render_template
from typing import Dict, Any, Optional
import time

try:
    from services.rag_generator import get_rag_generator, RAGGenerationResult
except ImportError:
    get_rag_generator = None
    RAGGenerationResult = None

try:
    from services.retrieval_service import get_retrieval_service
except ImportError:
    get_retrieval_service = None

try:
    from services.ingestion_service import get_ingestion_service
except ImportError:
    get_ingestion_service = None

try:
    from services.vector_store_service import get_vector_store_service
except ImportError:
    get_vector_store_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('rag_routes')
except ImportError:
    logger = None

try:
    from utils.cache_manager import get_cache_manager, cached
except ImportError:
    get_cache_manager = None
    cached = None

try:
    from utils.error_handler import handle_errors, APIServiceError
except ImportError:
    handle_errors = None
    APIServiceError = None

# Create blueprint
rag_bp = Blueprint('rag', __name__, url_prefix='/rag')

@rag_bp.route('/search', methods=['POST'])
@handle_errors if handle_errors else lambda x: x
def rag_search():
    """
    RAG search endpoint
    
    Expected JSON payload:
    {
        "query": "user query string",
        "top_k": 5,
        "use_hybrid": false,
        "filters": {}
    }
    
    Returns:
    {
        "success": true,
        "query": "user query",
        "response": "generated response",
        "context": [...],
        "processing_time": 1.23,
        "confidence_score": 0.85,
        "model_used": "mistral:latest",
        "retrieval_method": "vector"
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Get parameters
        top_k = data.get('top_k', 5)
        use_hybrid = data.get('use_hybrid', False)
        filters = data.get('filters', {})
        
        # Validate parameters
        if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
            return jsonify({
                'success': False,
                'error': 'top_k must be an integer between 1 and 20'
            }), 400
        
        # Get RAG generator
        if not get_rag_generator:
            return jsonify({
                'success': False,
                'error': 'RAG generator service not available'
            }), 503
        
        rag_generator = get_rag_generator()
        
        # Generate response
        result = rag_generator.generate_with_context(
            query=query,
            top_k=top_k,
            use_hybrid=use_hybrid
        )
        
        # Check for errors
        if result.error:
            return jsonify({
                'success': False,
                'error': result.error,
                'query': query
            }), 500
        
        # Prepare response
        response_data = {
            'success': True,
            'query': result.query,
            'response': result.generated_response,
            'context': result.retrieved_context,
            'processing_time': round(result.processing_time, 3),
            'confidence_score': round(result.confidence_score, 3),
            'model_used': result.model_used,
            'retrieval_method': result.retrieval_method,
            'total_context_chunks': len(result.retrieved_context)
        }
        
        if logger:
            logger.info(f"RAG search completed for query: {query[:50]}...")
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"RAG search failed: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@rag_bp.route('/search', methods=['GET'])
def rag_search_form():
    """Render RAG search form"""
    return render_template('rag_search.html')

@rag_bp.route('/retrieve', methods=['POST'])
@handle_errors if handle_errors else lambda x: x
def retrieve_context():
    """
    Retrieve context without generation
    
    Expected JSON payload:
    {
        "query": "user query string",
        "top_k": 10,
        "filters": {}
    }
    
    Returns:
    {
        "success": true,
        "query": "user query",
        "context": [...],
        "processing_time": 0.5,
        "retrieval_method": "vector"
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Get parameters
        top_k = data.get('top_k', 10)
        filters = data.get('filters', {})
        
        # Get retrieval service
        if not get_retrieval_service:
            return jsonify({
                'success': False,
                'error': 'Retrieval service not available'
            }), 503
        
        retrieval_service = get_retrieval_service()
        
        # Retrieve context
        start_time = time.time()
        result = retrieval_service.retrieve(query, top_k=top_k, filters=filters)
        processing_time = time.time() - start_time
        
        # Prepare context for response
        context_list = []
        for chunk in result.retrieved_chunks:
            context_dict = {
                'content': chunk.content,
                'similarity_score': round(chunk.similarity_score, 3),
                'rank': chunk.rank
            }
            
            # Add metadata
            if chunk.metadata:
                context_dict.update({
                    'title': chunk.metadata.get('title', ''),
                    'source': chunk.metadata.get('source', ''),
                    'url': chunk.metadata.get('url', ''),
                    'type': chunk.metadata.get('type', '')
                })
            
            context_list.append(context_dict)
        
        response_data = {
            'success': True,
            'query': result.query,
            'context': context_list,
            'processing_time': round(processing_time, 3),
            'retrieval_method': result.retrieval_method,
            'total_results': result.total_results,
            'confidence_score': round(result.confidence_score, 3)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Context retrieval failed: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@rag_bp.route('/generate', methods=['POST'])
@handle_errors if handle_errors else lambda x: x
def generate_with_context():
    """
    Generate response with custom context
    
    Expected JSON payload:
    {
        "query": "user query string",
        "context": ["context chunk 1", "context chunk 2"]
    }
    
    Returns:
    {
        "success": true,
        "query": "user query",
        "response": "generated response",
        "processing_time": 1.23,
        "model_used": "mistral:latest"
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        context_chunks = data.get('context', [])
        if not context_chunks:
            return jsonify({
                'success': False,
                'error': 'Context is required'
            }), 400
        
        # Get RAG generator
        if not get_rag_generator:
            return jsonify({
                'success': False,
                'error': 'RAG generator service not available'
            }), 503
        
        rag_generator = get_rag_generator()
        
        # Generate response
        result = rag_generator.generate_with_custom_context(query, context_chunks)
        
        # Check for errors
        if result.error:
            return jsonify({
                'success': False,
                'error': result.error,
                'query': query
            }), 500
        
        response_data = {
            'success': True,
            'query': result.query,
            'response': result.generated_response,
            'processing_time': round(result.processing_time, 3),
            'confidence_score': round(result.confidence_score, 3),
            'model_used': result.model_used,
            'retrieval_method': result.retrieval_method
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Generation with context failed: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@rag_bp.route('/ingest', methods=['POST'])
@handle_errors if handle_errors else lambda x: x
def ingest_document():
    """
    Ingest a document into the RAG system
    
    Expected JSON payload:
    {
        "document_type": "lead",
        "document": {
            "id": 123,
            "title": "Document title",
            "description": "Document description",
            ...
        }
    }
    
    Returns:
    {
        "success": true,
        "document_id": "lead_123",
        "chunks_created": 3,
        "processing_time": 2.5
    }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        document_type = data.get('document_type', '').strip()
        if not document_type:
            return jsonify({
                'success': False,
                'error': 'Document type is required'
            }), 400
        
        document = data.get('document', {})
        if not document:
            return jsonify({
                'success': False,
                'error': 'Document data is required'
            }), 400
        
        # Get ingestion service
        if not get_ingestion_service:
            return jsonify({
                'success': False,
                'error': 'Ingestion service not available'
            }), 503
        
        ingestion_service = get_ingestion_service()
        
        # Ingest document
        start_time = time.time()
        
        if document_type == 'lead':
            result = ingestion_service.ingest_lead(document)
        elif document_type == 'paper':
            result = ingestion_service.ingest_research_paper(document)
        elif document_type == 'search':
            result = ingestion_service.ingest_search_result(document)
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported document type: {document_type}'
            }), 400
        
        processing_time = time.time() - start_time
        
        if not result.success:
            return jsonify({
                'success': False,
                'error': result.error or 'Ingestion failed'
            }), 500
        
        # Store chunks in vector store
        if result.chunks and get_vector_store_service:
            vector_store = get_vector_store_service()
            
            # Convert chunks to documents
            documents = []
            for chunk in result.chunks:
                if chunk.embedding:
                    documents.append({
                        'id': chunk.chunk_id,
                        'content': chunk.content,
                        'embedding': chunk.embedding,
                        'metadata': chunk.metadata
                    })
            
            if documents:
                vector_store.upsert_documents(documents)
        
        response_data = {
            'success': True,
            'document_id': result.document_id,
            'chunks_created': result.total_chunks,
            'processing_time': round(processing_time, 3)
        }
        
        if logger:
            logger.info(f"Document ingested: {result.document_id} ({result.total_chunks} chunks)")
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Document ingestion failed: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@rag_bp.route('/status', methods=['GET'])
def rag_status():
    """
    Get RAG system status
    
    Returns:
    {
        "success": true,
        "services": {
            "rag_generator": {...},
            "retrieval_service": {...},
            "ingestion_service": {...},
            "vector_store": {...}
        }
    }
    """
    try:
        services_status = {}
        
        # Check RAG generator
        if get_rag_generator:
            from services.rag_generator import get_rag_generator_health_status
            services_status['rag_generator'] = get_rag_generator_health_status()
        
        # Check retrieval service
        if get_retrieval_service:
            from services.retrieval_service import get_retrieval_service_health_status
            services_status['retrieval_service'] = get_retrieval_service_health_status()
        
        # Check ingestion service
        if get_ingestion_service:
            from services.ingestion_service import get_ingestion_service_health_status
            services_status['ingestion_service'] = get_ingestion_service_health_status()
        
        # Check vector store
        if get_vector_store_service:
            from services.vector_store_service import get_vector_store_service_health_status
            services_status['vector_store'] = get_vector_store_service_health_status()
        
        # Calculate overall status
        all_healthy = all(
            status.get('status') == 'healthy' 
            for status in services_status.values()
        )
        
        response_data = {
            'success': True,
            'overall_status': 'healthy' if all_healthy else 'unhealthy',
            'services': services_status
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Status check failed: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@rag_bp.route('/stats', methods=['GET'])
def rag_stats():
    """
    Get RAG system statistics
    
    Returns:
    {
        "success": true,
        "stats": {
            "total_documents": 150,
            "document_types": {...},
            "collection_size_mb": 25.5
        }
    }
    """
    try:
        stats = {}
        
        # Get vector store stats
        if get_vector_store_service:
            vector_store = get_vector_store_service()
            vector_stats = vector_store.get_stats()
            
            stats.update({
                'total_documents': vector_stats.total_documents,
                'document_types': vector_stats.document_types,
                'collection_size_mb': round(vector_stats.collection_size_mb, 2),
                'index_status': vector_stats.index_status
            })
        
        response_data = {
            'success': True,
            'stats': stats
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = f"Stats retrieval failed: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@rag_bp.route('/health', methods=['GET'])
def rag_health():
    """Health check endpoint for RAG system"""
    try:
        # Quick health check
        status_data = rag_status().get_json()
        
        if status_data.get('success'):
            return jsonify({
                'status': 'healthy',
                'message': 'RAG system is operational'
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'message': 'RAG system has issues'
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': f'Health check failed: {str(e)}'
        }), 503 