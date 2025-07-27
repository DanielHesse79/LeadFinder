"""
Vector Store Management Service for LeadFinder RAG

This module provides vector store management using ChromaDB with connection
handling similar to the existing database_pool.py pattern.
"""

import os
import json
import threading
import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from contextlib import contextmanager

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.errors import ChromaDBError
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("ChromaDB not available. Install with: pip install chromadb")

try:
    from utils.logger import get_logger
    logger = get_logger('vector_store_service')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

@dataclass
class VectorSearchResult:
    """Result from vector search"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    rank: int

@dataclass
class VectorStoreStats:
    """Vector store statistics"""
    total_documents: int
    total_chunks: int
    document_types: Dict[str, int]
    last_updated: str
    collection_size_mb: float
    index_status: str

class VectorStoreConnection:
    """Individual vector store connection"""
    
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.last_used = time.time()
        self.is_healthy = True
    
    def initialize(self):
        """Initialize the connection"""
        try:
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_directory
            ))
            
            # Get or create the main collection
            self.collection = self.client.get_or_create_collection(
                name="leadfinder_docs",
                metadata={"description": "LeadFinder document embeddings"}
            )
            
            self.is_healthy = True
            self.last_used = time.time()
            
        except Exception as e:
            self.is_healthy = False
            if logger:
                logger.error(f"Failed to initialize vector store connection: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if connection is healthy"""
        try:
            if not self.client or not self.collection:
                return False
            
            # Simple health check - try to get collection count
            self.collection.count()
            self.is_healthy = True
            self.last_used = time.time()
            return True
            
        except Exception as e:
            self.is_healthy = False
            if logger:
                logger.error(f"Vector store health check failed: {e}")
            return False
    
    def close(self):
        """Close the connection"""
        try:
            if self.client:
                self.client = None
            if self.collection:
                self.collection = None
        except Exception as e:
            if logger:
                logger.error(f"Error closing vector store connection: {e}")

class VectorStorePool:
    """Connection pool for vector store operations"""
    
    def __init__(self, persist_directory: str, max_connections: int = 5, 
                 connection_timeout: int = 300):
        self.persist_directory = persist_directory
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        
        self._connections = []
        self._lock = threading.Lock()
        self._pool_initialized = False
        
        if logger:
            logger.info(f"Vector store pool initialized with max_connections={max_connections}")
    
    def _initialize_pool(self):
        """Initialize the connection pool"""
        if self._pool_initialized:
            return
        
        with self._lock:
            if self._pool_initialized:
                return
            
            try:
                # Ensure directory exists
                os.makedirs(self.persist_directory, exist_ok=True)
                
                # Create initial connection
                self._create_connection()
                self._pool_initialized = True
                
                if logger:
                    logger.info("Vector store pool initialized successfully")
                    
            except Exception as e:
                if logger:
                    logger.error(f"Failed to initialize vector store pool: {e}")
                raise
    
    def _create_connection(self) -> VectorStoreConnection:
        """Create a new connection"""
        connection = VectorStoreConnection(self.persist_directory)
        connection.initialize()
        return connection
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        self._initialize_pool()
        
        connection = None
        try:
            with self._lock:
                # Try to find an available healthy connection
                for conn in self._connections:
                    if conn.is_healthy and not self._is_connection_expired(conn):
                        connection = conn
                        break
                
                # If no healthy connection found, create a new one
                if not connection:
                    if len(self._connections) < self.max_connections:
                        connection = self._create_connection()
                        self._connections.append(connection)
                    else:
                        # Reuse the oldest connection
                        connection = min(self._connections, key=lambda c: c.last_used)
                        if not connection.health_check():
                            connection = self._create_connection()
                            self._connections.remove(connection)
                            self._connections.append(connection)
            
            yield connection
            
        except Exception as e:
            if connection:
                connection.is_healthy = False
            if logger:
                logger.error(f"Error in vector store connection: {e}")
            raise
    
    def _is_connection_expired(self, connection: VectorStoreConnection) -> bool:
        """Check if connection has expired"""
        return time.time() - connection.last_used > self.connection_timeout
    
    def close_all(self):
        """Close all connections in the pool"""
        with self._lock:
            for connection in self._connections:
                try:
                    connection.close()
                except Exception as e:
                    if logger:
                        logger.error(f"Error closing connection: {e}")
            self._connections.clear()
            self._pool_initialized = False

class VectorStoreService:
    """Main vector store service with connection pooling"""
    
    def __init__(self, persist_directory: str = None, max_connections: int = 5):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required for vector store functionality")
        
        self.persist_directory = persist_directory or "./data/vector_db"
        self.pool = VectorStorePool(self.persist_directory, max_connections)
        
        if logger:
            logger.info(f"Vector store service initialized at {self.persist_directory}")
    
    def upsert_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Upsert documents to the vector store
        
        Args:
            documents: List of document dictionaries with 'id', 'content', 'embedding', 'metadata'
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not documents:
                return True
            
            with self.pool.get_connection() as connection:
                # Extract data from documents
                ids = [doc['id'] for doc in documents]
                embeddings = [doc['embedding'] for doc in documents]
                contents = [doc['content'] for doc in documents]
                metadatas = [doc['metadata'] for doc in documents]
                
                # Upsert to collection
                connection.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=contents,
                    metadatas=metadatas
                )
                
                if logger:
                    logger.info(f"Upserted {len(documents)} documents to vector store")
                
                return True
                
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to upsert documents to vector store: {e}")
            return False
        except Exception as e:
            if logger:
                logger.error(f"Unexpected error upserting documents: {e}")
            return False
    
    def search(self, query_embedding: List[float], top_k: int = 10, 
               filters: Dict[str, Any] = None) -> List[VectorSearchResult]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            filters: Metadata filters for search
        
        Returns:
            List of VectorSearchResult objects
        """
        try:
            with self.pool.get_connection() as connection:
                results = connection.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=filters
                )
                
                # Convert to VectorSearchResult objects
                search_results = []
                for i, (doc_id, doc_content, metadata, distance) in enumerate(zip(
                    results['ids'][0] if results['ids'] else [],
                    results['documents'][0] if results['documents'] else [],
                    results['metadatas'][0] if results['metadatas'] else [],
                    results['distances'][0] if results['distances'] else []
                )):
                    search_results.append(VectorSearchResult(
                        chunk_id=doc_id,
                        content=doc_content,
                        metadata=metadata,
                        similarity_score=1 - distance,  # Convert distance to similarity
                        rank=i + 1
                    ))
                
                return search_results
                
        except ChromaDBError as e:
            if logger:
                logger.error(f"Search failed: {e}")
            return []
        except Exception as e:
            if logger:
                logger.error(f"Unexpected error in search: {e}")
            return []
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            document_id: Document ID to retrieve
        
        Returns:
            Document data or None if not found
        """
        try:
            with self.pool.get_connection() as connection:
                result = connection.collection.get(ids=[document_id])
                
                if result['ids']:
                    return {
                        'id': result['ids'][0],
                        'content': result['documents'][0],
                        'metadata': result['metadatas'][0],
                        'embedding': result['embeddings'][0] if result['embeddings'] else None
                    }
                
                return None
                
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to get document {document_id}: {e}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector store
        
        Args:
            document_id: Document ID to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.pool.get_connection() as connection:
                connection.collection.delete(ids=[document_id])
                
                if logger:
                    logger.info(f"Deleted document {document_id}")
                
                return True
                
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def get_stats(self) -> VectorStoreStats:
        """
        Get vector store statistics
        
        Returns:
            VectorStoreStats object
        """
        try:
            with self.pool.get_connection() as connection:
                count = connection.collection.count()
                
                # Get sample documents for metadata analysis
                sample = connection.collection.peek(limit=min(100, count))
                
                # Analyze document types
                doc_types = {}
                if sample['metadatas']:
                    for metadata in sample['metadatas']:
                        doc_type = metadata.get('type', 'unknown')
                        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                
                # Calculate collection size
                collection_size_mb = 0
                try:
                    if os.path.exists(self.persist_directory):
                        total_size = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(self.persist_directory)
                            for filename in filenames
                        )
                        collection_size_mb = total_size / (1024 * 1024)
                except Exception:
                    collection_size_mb = 0
                
                return VectorStoreStats(
                    total_documents=count,
                    total_chunks=count,  # In this implementation, documents are chunks
                    document_types=doc_types,
                    last_updated=datetime.now().isoformat(),
                    collection_size_mb=collection_size_mb,
                    index_status="healthy"
                )
                
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to get vector store stats: {e}")
            return VectorStoreStats(
                total_documents=0,
                total_chunks=0,
                document_types={},
                last_updated=datetime.now().isoformat(),
                collection_size_mb=0,
                index_status="error"
            )
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.pool.get_connection() as connection:
                connection.collection.delete(where={})
                
                if logger:
                    logger.info("Cleared all documents from vector store")
                
                return True
                
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to clear collection: {e}")
            return False
    
    def backup_collection(self, backup_path: str) -> bool:
        """
        Create a backup of the collection
        
        Args:
            backup_path: Path to save the backup
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.pool.get_connection() as connection:
                # Get all documents
                all_docs = connection.collection.get()
                
                # Save to JSON file
                backup_data = {
                    'documents': all_docs['documents'],
                    'metadatas': all_docs['metadatas'],
                    'embeddings': all_docs['embeddings'],
                    'ids': all_docs['ids'],
                    'backup_date': datetime.now().isoformat()
                }
                
                with open(backup_path, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                
                if logger:
                    logger.info(f"Backup created at {backup_path}")
                
                return True
                
        except Exception as e:
            if logger:
                logger.error(f"Failed to create backup: {e}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status information"""
        try:
            stats = self.get_stats()
            return {
                'status': 'healthy',
                'persist_directory': self.persist_directory,
                'pool_size': len(self.pool._connections),
                'stats': {
                    'total_documents': stats.total_documents,
                    'document_types': stats.document_types,
                    'collection_size_mb': stats.collection_size_mb,
                    'index_status': stats.index_status
                }
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def close(self):
        """Close the service and all connections"""
        self.pool.close_all()

# Global vector store service instance
_vector_store_service = None

def get_vector_store_service(persist_directory: str = None) -> VectorStoreService:
    """Get the global vector store service instance"""
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService(persist_directory)
    return _vector_store_service

def get_vector_store_service_health_status() -> Dict[str, Any]:
    """Get health status of the vector store service"""
    try:
        vector_store_service = get_vector_store_service()
        status = vector_store_service.get_service_status()
        
        return {
            'status': status['status'],
            'available': True,
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