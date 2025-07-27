"""
RAG Search Service for LeadFinder

This module provides Retrieval-Augmented Generation (RAG) functionality
by combining vector search with AI-powered response generation.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from services.vector_store import get_vector_store
except ImportError:
    get_vector_store = None

try:
    from services.embedding_service import get_embedding_service
except ImportError:
    get_embedding_service = None

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('rag_search')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

@dataclass
class RAGSearchResult:
    """Result from RAG search"""
    query: str
    retrieved_documents: List[Dict[str, Any]]
    generated_response: str
    processing_time: float
    metadata: Dict[str, Any]
    confidence_score: float = 0.0

class RAGSearchService:
    """Service for RAG-based search and response generation"""
    
    def __init__(self):
        self.vector_store = get_vector_store() if get_vector_store else None
        self.embedding_service = get_embedding_service() if get_embedding_service else None
        self.ollama_service = ollama_service
        
        if not self.vector_store:
            raise ImportError("Vector store is required for RAG search")
        if not self.embedding_service:
            raise ImportError("Embedding service is required for RAG search")
        
        if logger:
            logger.info("RAG search service initialized")
    
    def search(self, query: str, top_k: int = 10, 
               filters: Dict[str, Any] = None) -> RAGSearchResult:
        """
        Perform RAG search with retrieval and generation
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            filters: Metadata filters for search
        
        Returns:
            RAGSearchResult with retrieved documents and generated response
        """
        start_time = time.time()
        
        try:
            # Step 1: Generate query embedding
            query_embedding = self.embedding_service.embed_text(query)
            if not query_embedding:
                return self._create_error_result(query, "Failed to generate query embedding")
            
            # Step 2: Retrieve relevant documents
            search_results = self.vector_store.search(
                query_embedding=query_embedding,
                n_results=top_k,
                where=filters
            )
            
            if not search_results['documents']:
                return self._create_error_result(query, "No relevant documents found")
            
            # Step 3: Build context from retrieved documents
            context = self._build_context(search_results)
            
            # Step 4: Generate response using AI
            generated_response = self._generate_response(query, context)
            
            # Step 5: Calculate confidence score
            confidence_score = self._calculate_confidence(search_results)
            
            processing_time = time.time() - start_time
            
            # Create result
            result = RAGSearchResult(
                query=query,
                retrieved_documents=self._format_documents(search_results),
                generated_response=generated_response,
                processing_time=processing_time,
                metadata={
                    'total_documents': len(search_results['documents']),
                    'filters_applied': filters,
                    'embedding_model': self.embedding_service.model_name
                },
                confidence_score=confidence_score
            )
            
            if logger:
                logger.info(f"RAG search completed in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            if logger:
                logger.error(f"RAG search failed: {e}")
            return self._create_error_result(query, str(e))
    
    def search_with_context(self, query: str, context: str, 
                           top_k: int = 10) -> RAGSearchResult:
        """
        Perform RAG search with additional context
        
        Args:
            query: Search query
            context: Additional context to include
            top_k: Number of documents to retrieve
        
        Returns:
            RAGSearchResult with retrieved documents and generated response
        """
        # Combine query with context
        enhanced_query = f"{query}\n\nContext: {context}"
        return self.search(enhanced_query, top_k)
    
    def _build_context(self, search_results: Dict[str, Any]) -> str:
        """
        Build context string from retrieved documents
        
        Args:
            search_results: Results from vector search
        
        Returns:
            Formatted context string
        """
        documents = search_results['documents']
        metadatas = search_results['metadatas']
        distances = search_results['distances']
        
        context_parts = []
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # Format document with metadata
            doc_info = f"Document {i+1} (Relevance: {1-distance:.3f}):\n"
            doc_info += f"Title: {metadata.get('title', 'Unknown')}\n"
            doc_info += f"Source: {metadata.get('source', 'Unknown')}\n"
            doc_info += f"Content: {doc}\n"
            
            context_parts.append(doc_info)
        
        return "\n\n".join(context_parts)
    
    def _generate_response(self, query: str, context: str) -> str:
        """
        Generate AI response based on query and context
        
        Args:
            query: Original query
            context: Retrieved context
        
        Returns:
            Generated response
        """
        try:
            if not self.ollama_service:
                return "AI service not available for response generation."
            
            prompt = self._create_rag_prompt(query, context)
            
            response = self.ollama_service.generate_text(prompt)
            
            if not response:
                return "Unable to generate response based on available context."
            
            return response
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to generate response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """
        Create prompt for RAG response generation
        
        Args:
            query: User query
            context: Retrieved context
        
        Returns:
            Formatted prompt
        """
        return f"""
You are a helpful AI assistant for LeadFinder, a research lead discovery platform. 
Based on the following context, provide a comprehensive and accurate answer to the user's query.

User Query: {query}

Context from LeadFinder database:
{context}

Instructions:
1. Answer the query based ONLY on the provided context
2. If the context doesn't contain enough information, say so clearly
3. Provide specific, actionable insights when possible
4. Reference the source documents when relevant
5. Be concise but comprehensive
6. Focus on research leads, collaborations, and business opportunities

Answer:
"""
    
    def _format_documents(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format search results into structured documents
        
        Args:
            search_results: Raw search results
        
        Returns:
            List of formatted documents
        """
        documents = []
        
        for i, (doc_id, doc_content, metadata, distance) in enumerate(zip(
            search_results['ids'],
            search_results['documents'],
            search_results['metadatas'],
            search_results['distances']
        )):
            documents.append({
                'id': doc_id,
                'content': doc_content,
                'metadata': metadata,
                'relevance_score': 1 - distance,
                'rank': i + 1
            })
        
        return documents
    
    def _calculate_confidence(self, search_results: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on search results
        
        Args:
            search_results: Search results
        
        Returns:
            Confidence score between 0 and 1
        """
        try:
            distances = search_results['distances']
            if not distances:
                return 0.0
            
            # Calculate average relevance (1 - distance)
            relevances = [1 - d for d in distances]
            avg_relevance = sum(relevances) / len(relevances)
            
            # Boost confidence if we have multiple good results
            if len(distances) >= 3:
                avg_relevance *= 1.1
            
            return min(avg_relevance, 1.0)
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to calculate confidence: {e}")
            return 0.0
    
    def _create_error_result(self, query: str, error_message: str) -> RAGSearchResult:
        """
        Create error result when search fails
        
        Args:
            query: Original query
            error_message: Error description
        
        Returns:
            RAGSearchResult with error information
        """
        return RAGSearchResult(
            query=query,
            retrieved_documents=[],
            generated_response=f"Search failed: {error_message}",
            processing_time=0.0,
            metadata={'error': error_message},
            confidence_score=0.0
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get status of RAG search service
        
        Returns:
            Service status information
        """
        try:
            vector_store_status = self.vector_store.get_collection_stats()
            embedding_status = self.embedding_service.get_model_info()
            
            return {
                'status': 'healthy',
                'vector_store': vector_store_status,
                'embedding_service': embedding_status,
                'ollama_available': self.ollama_service is not None,
                'total_documents': vector_store_status.get('total_documents', 0)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

# Global RAG search service instance
_rag_search_service = None

def get_rag_search_service() -> RAGSearchService:
    """Get the global RAG search service instance"""
    global _rag_search_service
    if _rag_search_service is None:
        _rag_search_service = RAGSearchService()
    return _rag_search_service

def get_rag_search_health_status() -> Dict[str, Any]:
    """Get health status of the RAG search service"""
    try:
        rag_service = get_rag_search_service()
        status = rag_service.get_service_status()
        
        return {
            'status': status['status'],
            'available': status['status'] == 'healthy',
            'service_info': status,
            'error': status.get('error')
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'available': False,
            'service_info': {},
            'error': str(e)
        } 