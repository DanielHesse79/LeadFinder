"""
RAG Generator Service for LeadFinder

This module provides RAG generation functionality by combining retrieval
with AI generation using the local Ollama model.
"""

import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

try:
    from services.retrieval_service import get_retrieval_service, RetrievalResult
except ImportError:
    get_retrieval_service = None
    RetrievalResult = None

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('rag_generator')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

@dataclass
class RAGGenerationResult:
    """Result from RAG generation"""
    query: str
    generated_response: str
    retrieved_context: List[Dict[str, Any]]
    processing_time: float
    confidence_score: float
    model_used: str
    retrieval_method: str
    error: Optional[str] = None

@dataclass
class RAGPrompt:
    """RAG prompt structure"""
    system_prompt: str
    user_query: str
    context: str
    instructions: str

class RAGGenerator:
    """Service for RAG generation using retrieved context"""
    
    def __init__(self, model_name: str = "mistral:latest", max_context_length: int = 4000):
        self.model_name = model_name
        self.max_context_length = max_context_length
        
        # Initialize services
        self.retrieval_service = get_retrieval_service() if get_retrieval_service else None
        self.ollama_service = ollama_service
        
        if logger:
            logger.info(f"RAG generator initialized with model={model_name}, max_context={max_context_length}")
    
    def generate_with_context(self, query: str, top_k: int = 5, 
                            use_hybrid: bool = False) -> RAGGenerationResult:
        """
        Generate response with context using RAG
        
        Args:
            query: User query
            top_k: Number of context chunks to retrieve
            use_hybrid: Whether to use hybrid retrieval
        
        Returns:
            RAGGenerationResult with generated response
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant context
            if use_hybrid:
                retrieval_result = self.retrieval_service.hybrid_retrieve(query, top_k=top_k)
            else:
                retrieval_result = self.retrieval_service.retrieve(query, top_k=top_k)
            
            if not retrieval_result.retrieved_chunks:
                return self._create_error_result(
                    query, 
                    "No relevant context found for the query",
                    processing_time=time.time() - start_time
                )
            
            # Step 2: Build context from retrieved chunks
            context = self._build_context(retrieval_result.retrieved_chunks)
            
            # Step 3: Create RAG prompt
            rag_prompt = self._create_rag_prompt(query, context)
            
            # Step 4: Generate response
            generated_response = self._generate_response(rag_prompt)
            
            if not generated_response:
                return self._create_error_result(
                    query,
                    "Failed to generate response",
                    processing_time=time.time() - start_time
                )
            
            # Step 5: Prepare context for response
            retrieved_context = self._prepare_context_for_response(retrieval_result.retrieved_chunks)
            
            processing_time = time.time() - start_time
            
            return RAGGenerationResult(
                query=query,
                generated_response=generated_response,
                retrieved_context=retrieved_context,
                processing_time=processing_time,
                confidence_score=retrieval_result.confidence_score,
                model_used=self.model_name,
                retrieval_method=retrieval_result.retrieval_method
            )
            
        except Exception as e:
            error_msg = f"RAG generation failed for query '{query}': {str(e)}"
            if logger:
                logger.error(error_msg)
            
            return self._create_error_result(
                query,
                error_msg,
                processing_time=time.time() - start_time
            )
    
    def generate_with_custom_context(self, query: str, context_chunks: List[str]) -> RAGGenerationResult:
        """
        Generate response with custom context
        
        Args:
            query: User query
            context_chunks: List of context chunks
        
        Returns:
            RAGGenerationResult with generated response
        """
        start_time = time.time()
        
        try:
            if not context_chunks:
                return self._create_error_result(
                    query,
                    "No context provided",
                    processing_time=time.time() - start_time
                )
            
            # Build context from custom chunks
            context = self._build_context_from_chunks(context_chunks)
            
            # Create RAG prompt
            rag_prompt = self._create_rag_prompt(query, context)
            
            # Generate response
            generated_response = self._generate_response(rag_prompt)
            
            if not generated_response:
                return self._create_error_result(
                    query,
                    "Failed to generate response",
                    processing_time=time.time() - start_time
                )
            
            processing_time = time.time() - start_time
            
            return RAGGenerationResult(
                query=query,
                generated_response=generated_response,
                retrieved_context=[{'content': chunk} for chunk in context_chunks],
                processing_time=processing_time,
                confidence_score=0.8,  # Default confidence for custom context
                model_used=self.model_name,
                retrieval_method='custom'
            )
            
        except Exception as e:
            error_msg = f"Custom context generation failed: {str(e)}"
            if logger:
                logger.error(error_msg)
            
            return self._create_error_result(
                query,
                error_msg,
                processing_time=time.time() - start_time
            )
    
    def _build_context(self, retrieved_chunks: List[Any]) -> str:
        """
        Build context string from retrieved chunks
        
        Args:
            retrieved_chunks: List of retrieved chunks
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(retrieved_chunks[:5]):  # Limit to top 5 chunks
            # Extract content and metadata
            content = getattr(chunk, 'content', str(chunk))
            metadata = getattr(chunk, 'metadata', {})
            similarity = getattr(chunk, 'similarity_score', 0.0)
            
            # Format chunk
            chunk_info = f"Context {i+1} (Relevance: {similarity:.3f}):\n"
            
            # Add metadata if available
            if metadata.get('title'):
                chunk_info += f"Title: {metadata['title']}\n"
            if metadata.get('source'):
                chunk_info += f"Source: {metadata['source']}\n"
            
            chunk_info += f"Content: {content}\n"
            
            context_parts.append(chunk_info)
        
        return "\n\n".join(context_parts)
    
    def _build_context_from_chunks(self, chunks: List[str]) -> str:
        """
        Build context from raw text chunks
        
        Args:
            chunks: List of text chunks
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            context_parts.append(f"Context {i+1}:\n{chunk}")
        
        return "\n\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str) -> RAGPrompt:
        """
        Create RAG prompt with context
        
        Args:
            query: User query
            context: Retrieved context
        
        Returns:
            RAGPrompt object
        """
        system_prompt = """You are a helpful AI assistant for LeadFinder, a research lead discovery platform. 
Your role is to provide accurate, helpful responses based on the provided context."""

        instructions = """Instructions:
1. Answer the query based ONLY on the provided context
2. If the context doesn't contain enough information, say so clearly
3. Provide specific, actionable insights when possible
4. Reference the source documents when relevant
5. Be concise but comprehensive
6. Focus on research leads, collaborations, and business opportunities
7. If you're unsure about something, acknowledge the uncertainty"""

        return RAGPrompt(
            system_prompt=system_prompt,
            user_query=query,
            context=context,
            instructions=instructions
        )
    
    def _generate_response(self, rag_prompt: RAGPrompt) -> str:
        """
        Generate response using the LLM
        
        Args:
            rag_prompt: RAG prompt structure
        
        Returns:
            Generated response
        """
        try:
            if not self.ollama_service:
                return "AI service not available for response generation."
            
            # Build the full prompt
            full_prompt = self._build_full_prompt(rag_prompt)
            
            # Truncate if too long
            if len(full_prompt) > self.max_context_length:
                full_prompt = self._truncate_prompt(full_prompt)
            
            # Generate response
            response = self.ollama_service.generate_text(full_prompt)
            
            if not response:
                return "Unable to generate response based on available context."
            
            return response.strip()
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to generate response: {e}")
            return f"Error generating response: {str(e)}"
    
    def _build_full_prompt(self, rag_prompt: RAGPrompt) -> str:
        """
        Build the full prompt for generation
        
        Args:
            rag_prompt: RAG prompt structure
        
        Returns:
            Complete prompt string
        """
        return f"""{rag_prompt.system_prompt}

{rag_prompt.instructions}

User Query: {rag_prompt.user_query}

Context from LeadFinder database:
{rag_prompt.context}

Answer:"""
    
    def _truncate_prompt(self, prompt: str) -> str:
        """
        Truncate prompt if it's too long
        
        Args:
            prompt: Full prompt
        
        Returns:
            Truncated prompt
        """
        if len(prompt) <= self.max_context_length:
            return prompt
        
        # Find the context section and truncate it
        context_start = prompt.find("Context from LeadFinder database:")
        if context_start == -1:
            # If no context section, truncate from the end
            return prompt[:self.max_context_length] + "..."
        
        # Keep everything before context
        before_context = prompt[:context_start]
        
        # Calculate how much space we have for context
        available_space = self.max_context_length - len(before_context) - 100  # Buffer for instructions
        
        # Truncate context
        context_section = prompt[context_start:]
        if len(context_section) > available_space:
            context_section = context_section[:available_space] + "\n\n[Context truncated due to length]"
        
        return before_context + context_section
    
    def _prepare_context_for_response(self, retrieved_chunks: List[Any]) -> List[Dict[str, Any]]:
        """
        Prepare context for response format
        
        Args:
            retrieved_chunks: Retrieved chunks
        
        Returns:
            List of context dictionaries
        """
        context_list = []
        
        for chunk in retrieved_chunks:
            context_dict = {
                'content': getattr(chunk, 'content', str(chunk)),
                'similarity_score': getattr(chunk, 'similarity_score', 0.0),
                'rank': getattr(chunk, 'rank', 0)
            }
            
            # Add metadata if available
            metadata = getattr(chunk, 'metadata', {})
            if metadata:
                context_dict.update({
                    'title': metadata.get('title', ''),
                    'source': metadata.get('source', ''),
                    'url': metadata.get('url', ''),
                    'type': metadata.get('type', '')
                })
            
            context_list.append(context_dict)
        
        return context_list
    
    def _create_error_result(self, query: str, error_message: str, 
                           processing_time: float) -> RAGGenerationResult:
        """
        Create error result when generation fails
        
        Args:
            query: Original query
            error_message: Error description
            processing_time: Processing time
        
        Returns:
            RAGGenerationResult with error information
        """
        return RAGGenerationResult(
            query=query,
            generated_response=f"Generation failed: {error_message}",
            retrieved_context=[],
            processing_time=processing_time,
            confidence_score=0.0,
            model_used=self.model_name,
            retrieval_method='error',
            error=error_message
        )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information"""
        return {
            'status': 'healthy',
            'model_name': self.model_name,
            'max_context_length': self.max_context_length,
            'retrieval_service_available': self.retrieval_service is not None,
            'ollama_service_available': self.ollama_service is not None
        }

# Global RAG generator instance
_rag_generator = None

def get_rag_generator(model_name: str = None, max_context_length: int = None) -> RAGGenerator:
    """Get the global RAG generator instance"""
    global _rag_generator
    if _rag_generator is None:
        model = model_name or "mistral:latest"
        max_length = max_context_length or 4000
        _rag_generator = RAGGenerator(model, max_length)
    return _rag_generator

def get_rag_generator_health_status() -> Dict[str, Any]:
    """Get health status of the RAG generator"""
    try:
        rag_generator = get_rag_generator()
        status = rag_generator.get_service_status()
        
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