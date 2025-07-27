"""
Embedding Service for LeadFinder RAG

This module provides text embedding functionality using SentenceTransformers
for converting text documents into vector representations.
"""

import time
from typing import List, Dict, Any, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.util import cos_sim
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("SentenceTransformers not available. Install with: pip install sentence-transformers")

try:
    from utils.logger import get_logger
    logger = get_logger('embedding_service')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

class EmbeddingService:
    """Service for generating text embeddings using SentenceTransformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = None):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("SentenceTransformers is required for embedding functionality")
        
        self.model_name = model_name
        self.device = device
        
        # Initialize the model
        try:
            self.model = SentenceTransformer(model_name, device=device)
            if logger:
                logger.info(f"Embedding model loaded: {model_name}")
        except Exception as e:
            if logger:
                logger.error(f"Failed to load embedding model {model_name}: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats representing the embedding
        """
        try:
            if not text or not text.strip():
                return []
            
            start_time = time.time()
            embedding = self.model.encode(text, convert_to_tensor=False)
            processing_time = time.time() - start_time
            
            if logger:
                logger.debug(f"Generated embedding in {processing_time:.3f}s")
            
            return embedding.tolist()
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to embed text: {e}")
            return []
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
        
        Returns:
            List of embeddings
        """
        try:
            if not texts:
                return []
            
            # Filter out empty texts
            valid_texts = [text for text in texts if text and text.strip()]
            
            if not valid_texts:
                return []
            
            start_time = time.time()
            embeddings = self.model.encode(
                valid_texts, 
                batch_size=batch_size,
                convert_to_tensor=False,
                show_progress_bar=False
            )
            processing_time = time.time() - start_time
            
            if logger:
                logger.info(f"Generated {len(embeddings)} embeddings in {processing_time:.3f}s")
            
            return embeddings.tolist()
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to embed batch: {e}")
            return []
    
    def embed_documents(self, documents: List[Dict[str, Any]], 
                       content_field: str = 'content') -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of documents
        
        Args:
            documents: List of document dictionaries
            content_field: Field name containing the text content
        
        Returns:
            List of documents with embeddings added
        """
        try:
            if not documents:
                return []
            
            # Extract texts
            texts = [doc.get(content_field, '') for doc in documents]
            
            # Generate embeddings
            embeddings = self.embed_batch(texts)
            
            # Add embeddings to documents
            for i, doc in enumerate(documents):
                if i < len(embeddings):
                    doc['embedding'] = embeddings[i]
                else:
                    doc['embedding'] = []
            
            return documents
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to embed documents: {e}")
            return documents
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
        
        Returns:
            Similarity score between 0 and 1
        """
        try:
            if not embedding1 or not embedding2:
                return 0.0
            
            # Convert to numpy arrays
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            # Calculate cosine similarity
            similarity = cos_sim(emb1, emb2).item()
            
            return float(similarity)
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], 
                         candidate_embeddings: List[List[float]], 
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find the most similar embeddings to a query embedding
        
        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings
            top_k: Number of top results to return
        
        Returns:
            List of dictionaries with index and similarity score
        """
        try:
            if not query_embedding or not candidate_embeddings:
                return []
            
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                if candidate:  # Skip empty embeddings
                    sim = self.similarity(query_embedding, candidate)
                    similarities.append({
                        'index': i,
                        'similarity': sim
                    })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top_k results
            return similarities[:top_k]
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to find most similar: {e}")
            return []
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embeddings
        
        Returns:
            Embedding dimension
        """
        try:
            # Generate a test embedding to get dimension
            test_embedding = self.embed_text("test")
            return len(test_embedding)
        except Exception as e:
            if logger:
                logger.error(f"Failed to get embedding dimension: {e}")
            return 0
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model
        
        Returns:
            Dictionary with model information
        """
        try:
            return {
                'model_name': self.model_name,
                'device': str(self.model.device),
                'embedding_dimension': self.get_embedding_dimension(),
                'max_seq_length': self.model.max_seq_length,
                'available': True
            }
        except Exception as e:
            if logger:
                logger.error(f"Failed to get model info: {e}")
            return {
                'model_name': self.model_name,
                'available': False,
                'error': str(e)
            }
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding
        
        Args:
            text: Raw text
        
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Basic preprocessing
        text = text.strip()
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (keep within model limits)
        max_length = getattr(self.model, 'max_seq_length', 512)
        if len(text) > max_length * 4:  # Rough character limit
            text = text[:max_length * 4] + "..."
        
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, 
                   overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks

# Global embedding service instance
_embedding_service = None

def get_embedding_service(model_name: str = None) -> EmbeddingService:
    """Get the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        model = model_name or "all-MiniLM-L6-v2"
        _embedding_service = EmbeddingService(model)
    return _embedding_service

def get_embedding_service_health_status() -> Dict[str, Any]:
    """Get health status of the embedding service"""
    try:
        embedding_service = get_embedding_service()
        model_info = embedding_service.get_model_info()
        
        return {
            'status': 'healthy' if model_info['available'] else 'unhealthy',
            'available': model_info['available'],
            'model_info': model_info,
            'error': model_info.get('error')
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'available': False,
            'model_info': {},
            'error': str(e)
        } 