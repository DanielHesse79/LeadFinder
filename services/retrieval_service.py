"""
Retrieval Service for LeadFinder RAG

This module handles the retrieval logic for RAG, including query processing,
vector search, and fallback to traditional search when needed.
"""

import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

try:
    from services.embedding_service import get_embedding_service
except ImportError:
    get_embedding_service = None

try:
    from services.vector_store_service import get_vector_store_service, VectorSearchResult
except ImportError:
    get_vector_store_service = None
    VectorSearchResult = None

try:
    from services.unified_search_service import get_unified_search_service
except ImportError:
    get_unified_search_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('retrieval_service')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

@dataclass
class RetrievalResult:
    """Result from retrieval service"""
    query: str
    retrieved_chunks: List[VectorSearchResult]
    fallback_results: List[Dict[str, Any]]
    processing_time: float
    retrieval_method: str  # 'vector', 'fallback', 'hybrid'
    total_results: int
    confidence_score: float

@dataclass
class QueryContext:
    """Context for query processing"""
    original_query: str
    processed_query: str
    query_embedding: Optional[List[float]]
    filters: Dict[str, Any]
    top_k: int
    similarity_threshold: float

class RetrievalService:
    """Service for retrieving relevant documents for RAG"""
    
    def __init__(self, similarity_threshold: float = 0.7, top_k: int = 10):
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        
        # Initialize services
        self.embedding_service = get_embedding_service() if get_embedding_service else None
        self.vector_store_service = get_vector_store_service() if get_vector_store_service else None
        self.unified_search_service = get_unified_search_service() if get_unified_search_service else None
        
        if logger:
            logger.info(f"Retrieval service initialized with threshold={similarity_threshold}, top_k={top_k}")
    
    def retrieve(self, query: str, top_k: int = None, 
                filters: Dict[str, Any] = None, 
                use_fallback: bool = True) -> RetrievalResult:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            filters: Metadata filters for search
            use_fallback: Whether to use fallback search if vector search fails
        
        Returns:
            RetrievalResult with retrieved documents
        """
        start_time = time.time()
        
        try:
            # Process query
            query_context = self._process_query(query, top_k or self.top_k, filters)
            
            # Try vector search first
            vector_results = self._vector_search(query_context)
            
            if vector_results and len(vector_results) > 0:
                # Vector search successful
                processing_time = time.time() - start_time
                
                return RetrievalResult(
                    query=query,
                    retrieved_chunks=vector_results,
                    fallback_results=[],
                    processing_time=processing_time,
                    retrieval_method='vector',
                    total_results=len(vector_results),
                    confidence_score=self._calculate_confidence(vector_results)
                )
            
            # Fallback to traditional search if enabled
            if use_fallback and self.unified_search_service:
                fallback_results = self._fallback_search(query_context)
                
                processing_time = time.time() - start_time
                
                return RetrievalResult(
                    query=query,
                    retrieved_chunks=[],
                    fallback_results=fallback_results,
                    processing_time=processing_time,
                    retrieval_method='fallback',
                    total_results=len(fallback_results),
                    confidence_score=0.5  # Lower confidence for fallback
                )
            
            # No results found
            processing_time = time.time() - start_time
            
            return RetrievalResult(
                query=query,
                retrieved_chunks=[],
                fallback_results=[],
                processing_time=processing_time,
                retrieval_method='none',
                total_results=0,
                confidence_score=0.0
            )
            
        except Exception as e:
            error_msg = f"Retrieval failed for query '{query}': {str(e)}"
            if logger:
                logger.error(error_msg)
            
            processing_time = time.time() - start_time
            
            return RetrievalResult(
                query=query,
                retrieved_chunks=[],
                fallback_results=[],
                processing_time=processing_time,
                retrieval_method='error',
                total_results=0,
                confidence_score=0.0
            )
    
    def hybrid_retrieve(self, query: str, top_k: int = None, 
                       filters: Dict[str, Any] = None) -> RetrievalResult:
        """
        Perform hybrid retrieval combining vector and traditional search
        
        Args:
            query: User query
            top_k: Number of results to retrieve
            filters: Metadata filters for search
        
        Returns:
            RetrievalResult with combined results
        """
        start_time = time.time()
        
        try:
            # Process query
            query_context = self._process_query(query, top_k or self.top_k, filters)
            
            # Get vector search results
            vector_results = self._vector_search(query_context)
            
            # Get traditional search results
            fallback_results = []
            if self.unified_search_service:
                fallback_results = self._fallback_search(query_context)
            
            # Combine and deduplicate results
            combined_chunks = self._combine_results(vector_results, fallback_results)
            
            processing_time = time.time() - start_time
            
            return RetrievalResult(
                query=query,
                retrieved_chunks=combined_chunks,
                fallback_results=fallback_results,
                processing_time=processing_time,
                retrieval_method='hybrid',
                total_results=len(combined_chunks),
                confidence_score=self._calculate_confidence(combined_chunks)
            )
            
        except Exception as e:
            error_msg = f"Hybrid retrieval failed for query '{query}': {str(e)}"
            if logger:
                logger.error(error_msg)
            
            processing_time = time.time() - start_time
            
            return RetrievalResult(
                query=query,
                retrieved_chunks=[],
                fallback_results=[],
                processing_time=processing_time,
                retrieval_method='error',
                total_results=0,
                confidence_score=0.0
            )
    
    def _process_query(self, query: str, top_k: int, 
                      filters: Dict[str, Any]) -> QueryContext:
        """
        Process and prepare query for retrieval
        
        Args:
            query: Original query
            top_k: Number of results to retrieve
            filters: Metadata filters
        
        Returns:
            QueryContext with processed query information
        """
        # Clean and preprocess query
        processed_query = self._preprocess_query(query)
        
        # Generate embedding
        query_embedding = None
        if self.embedding_service:
            query_embedding = self.embedding_service.embed_text(processed_query)
        
        # Prepare filters
        search_filters = filters or {}
        
        return QueryContext(
            original_query=query,
            processed_query=processed_query,
            query_embedding=query_embedding,
            filters=search_filters,
            top_k=top_k,
            similarity_threshold=self.similarity_threshold
        )
    
    def _vector_search(self, query_context: QueryContext) -> List[VectorSearchResult]:
        """
        Perform vector search
        
        Args:
            query_context: Processed query context
        
        Returns:
            List of vector search results
        """
        if not self.vector_store_service or not query_context.query_embedding:
            return []
        
        try:
            # Perform vector search
            results = self.vector_store_service.search(
                query_embedding=query_context.query_embedding,
                top_k=query_context.top_k,
                filters=query_context.filters
            )
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in results 
                if result.similarity_score >= query_context.similarity_threshold
            ]
            
            if logger:
                logger.debug(f"Vector search returned {len(results)} results, {len(filtered_results)} after filtering")
            
            return filtered_results
            
        except Exception as e:
            if logger:
                logger.error(f"Vector search failed: {e}")
            return []
    
    def _fallback_search(self, query_context: QueryContext) -> List[Dict[str, Any]]:
        """
        Perform fallback traditional search
        
        Args:
            query_context: Processed query context
        
        Returns:
            List of traditional search results
        """
        if not self.unified_search_service:
            return []
        
        try:
            # Use unified search service
            from services.unified_search_service import SearchQuery
            
            search_query = SearchQuery(
                query=query_context.processed_query,
                search_type="unified",
                engines=["web", "research"],
                max_results=query_context.top_k
            )
            
            results = self.unified_search_service.search(search_query)
            
            # Extract and format results
            fallback_results = []
            
            # Add web search results
            if 'web_results' in results:
                for result in results['web_results']:
                    fallback_results.append({
                        'title': result.get('title', ''),
                        'content': result.get('description', ''),
                        'url': result.get('url', ''),
                        'source': 'web_search',
                        'relevance_score': result.get('relevance_score', 0.5)
                    })
            
            # Add research results
            if 'research_results' in results:
                for result in results['research_results']:
                    fallback_results.append({
                        'title': result.get('title', ''),
                        'content': result.get('abstract', ''),
                        'url': result.get('url', ''),
                        'source': 'research_search',
                        'relevance_score': result.get('relevance_score', 0.5)
                    })
            
            if logger:
                logger.debug(f"Fallback search returned {len(fallback_results)} results")
            
            return fallback_results
            
        except Exception as e:
            if logger:
                logger.error(f"Fallback search failed: {e}")
            return []
    
    def _combine_results(self, vector_results: List[VectorSearchResult], 
                        fallback_results: List[Dict[str, Any]]) -> List[VectorSearchResult]:
        """
        Combine vector and traditional search results
        
        Args:
            vector_results: Vector search results
            fallback_results: Traditional search results
        
        Returns:
            Combined and deduplicated results
        """
        combined = vector_results.copy()
        
        # Convert fallback results to VectorSearchResult format
        for i, fallback_result in enumerate(fallback_results):
            # Create a mock VectorSearchResult for fallback results
            combined.append(VectorSearchResult(
                chunk_id=f"fallback_{i}",
                content=fallback_result.get('content', ''),
                metadata={
                    'title': fallback_result.get('title', ''),
                    'source': fallback_result.get('source', 'fallback'),
                    'url': fallback_result.get('url', ''),
                    'type': 'fallback_result'
                },
                similarity_score=fallback_result.get('relevance_score', 0.5),
                rank=len(combined) + 1
            ))
        
        # Sort by similarity score and remove duplicates
        combined.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Simple deduplication based on content similarity
        deduplicated = []
        seen_contents = set()
        
        for result in combined:
            content_hash = hash(result.content[:100])  # Hash first 100 chars
            if content_hash not in seen_contents:
                deduplicated.append(result)
                seen_contents.add(content_hash)
        
        return deduplicated
    
    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess query for better retrieval
        
        Args:
            query: Original query
        
        Returns:
            Preprocessed query
        """
        if not query:
            return ""
        
        # Basic preprocessing
        query = query.strip()
        
        # Remove excessive whitespace
        import re
        query = re.sub(r'\s+', ' ', query)
        
        # Convert to lowercase for better matching
        query = query.lower()
        
        return query
    
    def _calculate_confidence(self, results: List[VectorSearchResult]) -> float:
        """
        Calculate confidence score based on search results
        
        Args:
            results: Search results
        
        Returns:
            Confidence score between 0 and 1
        """
        if not results:
            return 0.0
        
        try:
            # Calculate average similarity score
            avg_similarity = sum(result.similarity_score for result in results) / len(results)
            
            # Boost confidence if we have multiple good results
            if len(results) >= 3:
                avg_similarity *= 1.1
            
            # Ensure confidence is between 0 and 1
            return min(avg_similarity, 1.0)
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to calculate confidence: {e}")
            return 0.0
    
    def get_relevant_chunks_for_rag(self, query: str, top_k: int = 5) -> List[str]:
        """
        Get relevant chunks for RAG generation
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
        
        Returns:
            List of relevant content chunks
        """
        try:
            result = self.retrieve(query, top_k=top_k)
            
            # Extract content from chunks
            chunks = []
            for chunk in result.retrieved_chunks:
                chunks.append(chunk.content)
            
            return chunks
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to get relevant chunks: {e}")
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information"""
        return {
            'status': 'healthy',
            'similarity_threshold': self.similarity_threshold,
            'top_k': self.top_k,
            'embedding_service_available': self.embedding_service is not None,
            'vector_store_available': self.vector_store_service is not None,
            'unified_search_available': self.unified_search_service is not None
        }

# Global retrieval service instance
_retrieval_service = None

def get_retrieval_service(similarity_threshold: float = None, top_k: int = None) -> RetrievalService:
    """Get the global retrieval service instance"""
    global _retrieval_service
    if _retrieval_service is None:
        threshold = similarity_threshold or 0.7
        k = top_k or 10
        _retrieval_service = RetrievalService(threshold, k)
    return _retrieval_service

def get_retrieval_service_health_status() -> Dict[str, Any]:
    """Get health status of the retrieval service"""
    try:
        retrieval_service = get_retrieval_service()
        status = retrieval_service.get_service_status()
        
        return {
            'status': status['status'],
            'available': True,
            'service_info': status,
            'error': None
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'available': False,
            'service_info': {},
            'error': str(e)
        } 