"""
Document/Lead Ingestion Service for LeadFinder RAG

This module handles the ingestion, parsing, chunking, and embedding generation
for documents and leads to be stored in the vector database.
"""

import hashlib
import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass

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
    logger = get_logger('ingestion_service')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

@dataclass
class DocumentChunk:
    """Represents a chunk of document content"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    chunk_index: int = 0
    total_chunks: int = 1

@dataclass
class IngestionResult:
    """Result of document ingestion process"""
    document_id: str
    chunks: List[DocumentChunk]
    total_chunks: int
    processing_time: float
    success: bool
    error: Optional[str] = None

class DocumentIngestionService:
    """Service for ingesting and processing documents for RAG"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embedding service
        self.embedding_service = get_embedding_service() if get_embedding_service else None
        self.ollama_service = ollama_service
        
        if logger:
            logger.info(f"Ingestion service initialized with chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def ingest_lead(self, lead_data: Dict[str, Any]) -> IngestionResult:
        """
        Ingest a lead document into the RAG system
        
        Args:
            lead_data: Lead data dictionary with title, description, etc.
        
        Returns:
            IngestionResult with processed chunks
        """
        start_time = datetime.now()
        
        try:
            # Extract lead information
            lead_id = lead_data.get('id')
            title = lead_data.get('title', '')
            description = lead_data.get('description', '')
            ai_summary = lead_data.get('ai_summary', '')
            source = lead_data.get('source', 'unknown')
            link = lead_data.get('link', '')
            created_at = lead_data.get('created_at', datetime.now().isoformat())
            
            # Combine content
            content = self._combine_lead_content(title, description, ai_summary)
            
            if not content.strip():
                return IngestionResult(
                    document_id=f"lead_{lead_id}",
                    chunks=[],
                    total_chunks=0,
                    processing_time=0.0,
                    success=False,
                    error="No content to process"
                )
            
            # Create document metadata
            metadata = {
                'title': title,
                'source': source,
                'url': link,
                'created_at': created_at,
                'type': 'lead',
                'original_id': lead_id,
                'content_type': 'lead'
            }
            
            # Process document
            return self._process_document(
                document_id=f"lead_{lead_id}",
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            error_msg = f"Failed to ingest lead {lead_data.get('id', 'unknown')}: {str(e)}"
            if logger:
                logger.error(error_msg)
            
            return IngestionResult(
                document_id=f"lead_{lead_data.get('id', 'unknown')}",
                chunks=[],
                total_chunks=0,
                processing_time=0.0,
                success=False,
                error=error_msg
            )
    
    def ingest_research_paper(self, paper_data: Dict[str, Any]) -> IngestionResult:
        """
        Ingest a research paper into the RAG system
        
        Args:
            paper_data: Paper data with title, abstract, content, etc.
        
        Returns:
            IngestionResult with processed chunks
        """
        start_time = datetime.now()
        
        try:
            paper_id = paper_data.get('id')
            title = paper_data.get('title', '')
            abstract = paper_data.get('abstract', '')
            content = paper_data.get('content', '')
            authors = paper_data.get('authors', [])
            doi = paper_data.get('doi', '')
            source = paper_data.get('source', 'unknown')
            
            # Combine content
            full_content = self._combine_paper_content(title, abstract, content, authors)
            
            if not full_content.strip():
                return IngestionResult(
                    document_id=f"paper_{paper_id}",
                    chunks=[],
                    total_chunks=0,
                    processing_time=0.0,
                    success=False,
                    error="No content to process"
                )
            
            # Create metadata
            metadata = {
                'title': title,
                'authors': authors,
                'doi': doi,
                'source': source,
                'type': 'research_paper',
                'original_id': paper_id,
                'content_type': 'paper'
            }
            
            return self._process_document(
                document_id=f"paper_{paper_id}",
                content=full_content,
                metadata=metadata
            )
            
        except Exception as e:
            error_msg = f"Failed to ingest paper {paper_data.get('id', 'unknown')}: {str(e)}"
            if logger:
                logger.error(error_msg)
            
            return IngestionResult(
                document_id=f"paper_{paper_data.get('id', 'unknown')}",
                chunks=[],
                total_chunks=0,
                processing_time=0.0,
                success=False,
                error=error_msg
            )
    
    def ingest_search_result(self, search_data: Dict[str, Any]) -> IngestionResult:
        """
        Ingest a search result into the RAG system
        
        Args:
            search_data: Search result data
        
        Returns:
            IngestionResult with processed chunks
        """
        start_time = datetime.now()
        
        try:
            search_id = search_data.get('id')
            query = search_data.get('query', '')
            research_question = search_data.get('research_question', '')
            results_count = search_data.get('results_count', 0)
            engines = search_data.get('engines', '')
            
            # Combine content
            content = f"Search Query: {query}\nResearch Question: {research_question}"
            
            if not content.strip():
                return IngestionResult(
                    document_id=f"search_{search_id}",
                    chunks=[],
                    total_chunks=0,
                    processing_time=0.0,
                    success=False,
                    error="No content to process"
                )
            
            # Create metadata
            metadata = {
                'title': f"Search: {query[:50]}...",
                'query': query,
                'research_question': research_question,
                'engines': engines,
                'results_count': results_count,
                'type': 'search_query',
                'original_id': search_id,
                'content_type': 'search'
            }
            
            return self._process_document(
                document_id=f"search_{search_id}",
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            error_msg = f"Failed to ingest search {search_data.get('id', 'unknown')}: {str(e)}"
            if logger:
                logger.error(error_msg)
            
            return IngestionResult(
                document_id=f"search_{search_data.get('id', 'unknown')}",
                chunks=[],
                total_chunks=0,
                processing_time=0.0,
                success=False,
                error=error_msg
            )
    
    def _process_document(self, document_id: str, content: str, 
                         metadata: Dict[str, Any]) -> IngestionResult:
        """
        Process a document by chunking and generating embeddings
        
        Args:
            document_id: Unique document identifier
            content: Document content
            metadata: Document metadata
        
        Returns:
            IngestionResult with processed chunks
        """
        start_time = datetime.now()
        
        try:
            # Clean and preprocess content
            cleaned_content = self._preprocess_content(content)
            
            # Chunk the content
            chunks = self._chunk_content(cleaned_content)
            
            if not chunks:
                return IngestionResult(
                    document_id=document_id,
                    chunks=[],
                    total_chunks=0,
                    processing_time=0.0,
                    success=False,
                    error="No chunks generated"
                )
            
            # Create document chunks
            document_chunks = []
            for i, chunk_content in enumerate(chunks):
                chunk_id = self._generate_chunk_id(document_id, i)
                
                # Generate embedding
                embedding = None
                if self.embedding_service:
                    embedding = self.embedding_service.embed_text(chunk_content)
                
                # Create chunk
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    metadata=metadata.copy(),
                    embedding=embedding,
                    chunk_index=i,
                    total_chunks=len(chunks)
                )
                
                document_chunks.append(chunk)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if logger:
                logger.info(f"Processed document {document_id} into {len(chunks)} chunks in {processing_time:.3f}s")
            
            return IngestionResult(
                document_id=document_id,
                chunks=document_chunks,
                total_chunks=len(chunks),
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            error_msg = f"Failed to process document {document_id}: {str(e)}"
            if logger:
                logger.error(error_msg)
            
            return IngestionResult(
                document_id=document_id,
                chunks=[],
                total_chunks=0,
                processing_time=0.0,
                success=False,
                error=error_msg
            )
    
    def _combine_lead_content(self, title: str, description: str, ai_summary: str) -> str:
        """Combine lead content for processing"""
        parts = []
        
        if title:
            parts.append(f"Title: {title}")
        
        if description:
            parts.append(f"Description: {description}")
        
        if ai_summary:
            parts.append(f"AI Analysis: {ai_summary}")
        
        return "\n\n".join(parts)
    
    def _combine_paper_content(self, title: str, abstract: str, content: str, authors: List[str]) -> str:
        """Combine research paper content for processing"""
        parts = []
        
        if title:
            parts.append(f"Title: {title}")
        
        if authors:
            authors_str = ", ".join(authors)
            parts.append(f"Authors: {authors_str}")
        
        if abstract:
            parts.append(f"Abstract: {abstract}")
        
        if content:
            parts.append(f"Content: {content}")
        
        return "\n\n".join(parts)
    
    def _preprocess_content(self, content: str) -> str:
        """
        Preprocess content for chunking
        
        Args:
            content: Raw content
        
        Returns:
            Preprocessed content
        """
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove special characters that might interfere with chunking
        content = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]]', ' ', content)
        
        # Normalize line breaks
        content = content.replace('\n', ' ').replace('\r', ' ')
        
        return content.strip()
    
    def _chunk_content(self, content: str) -> List[str]:
        """
        Split content into overlapping chunks
        
        Args:
            content: Content to chunk
        
        Returns:
            List of content chunks
        """
        if not content:
            return []
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence endings within the last 100 characters
                for i in range(end, max(start, end - 100), -1):
                    if content[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(content):
                break
        
        return chunks
    
    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        chunk_data = f"{document_id}_{chunk_index}"
        return hashlib.md5(chunk_data.encode()).hexdigest()[:16]
    
    def batch_ingest(self, documents: List[Dict[str, Any]], 
                    document_type: str = 'lead') -> List[IngestionResult]:
        """
        Ingest multiple documents in batch
        
        Args:
            documents: List of document data
            document_type: Type of documents ('lead', 'paper', 'search')
        
        Returns:
            List of ingestion results
        """
        results = []
        
        for doc in documents:
            if document_type == 'lead':
                result = self.ingest_lead(doc)
            elif document_type == 'paper':
                result = self.ingest_research_paper(doc)
            elif document_type == 'search':
                result = self.ingest_search_result(doc)
            else:
                result = IngestionResult(
                    document_id=f"unknown_{doc.get('id', 'unknown')}",
                    chunks=[],
                    total_chunks=0,
                    processing_time=0.0,
                    success=False,
                    error=f"Unknown document type: {document_type}"
                )
            
            results.append(result)
        
        return results
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information"""
        return {
            'status': 'healthy',
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'embedding_service_available': self.embedding_service is not None,
            'ollama_service_available': self.ollama_service is not None
        }

# Global ingestion service instance
_ingestion_service = None

def get_ingestion_service(chunk_size: int = None, chunk_overlap: int = None) -> DocumentIngestionService:
    """Get the global ingestion service instance"""
    global _ingestion_service
    if _ingestion_service is None:
        chunk_size = chunk_size or 1000
        chunk_overlap = chunk_overlap or 200
        _ingestion_service = DocumentIngestionService(chunk_size, chunk_overlap)
    return _ingestion_service

def get_ingestion_service_health_status() -> Dict[str, Any]:
    """Get health status of the ingestion service"""
    try:
        ingestion_service = get_ingestion_service()
        status = ingestion_service.get_service_status()
        
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