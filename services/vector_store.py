"""
Vector Store Service for LeadFinder RAG

This module provides ChromaDB integration for storing and retrieving
document embeddings for the RAG system.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

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
    logger = get_logger('vector_store')
except ImportError:
    logger = None

try:
    from config import config
except ImportError:
    config = None

class VectorStore:
    """ChromaDB-based vector store for document embeddings"""
    
    def __init__(self, persist_directory: str = None):
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB is required for vector store functionality")
        
        self.persist_directory = persist_directory or "./data/vector_db"
        self._ensure_directory_exists()
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=self.persist_directory
        ))
        
        # Get or create the main collection
        self.collection = self.client.get_or_create_collection(
            name="leadfinder_docs",
            metadata={"description": "LeadFinder document embeddings"}
        )
        
        if logger:
            logger.info(f"Vector store initialized at {self.persist_directory}")
    
    def _ensure_directory_exists(self):
        """Ensure the vector database directory exists"""
        os.makedirs(self.persist_directory, exist_ok=True)
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document dictionaries with 'id', 'content', 'embedding', 'metadata'
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not documents:
                return True
            
            # Extract data from documents
            ids = [doc['id'] for doc in documents]
            embeddings = [doc['embedding'] for doc in documents]
            contents = [doc['content'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            
            if logger:
                logger.info(f"Added {len(documents)} documents to vector store")
            
            return True
            
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to add documents to vector store: {e}")
            return False
        except Exception as e:
            if logger:
                logger.error(f"Unexpected error adding documents: {e}")
            return False
    
    def search(self, query_embedding: List[float], n_results: int = 10, 
               where: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query vector embedding
            n_results: Number of results to return
            where: Filter conditions for metadata
        
        Returns:
            Dict containing search results
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else [],
                'ids': results['ids'][0] if results['ids'] else []
            }
            
        except ChromaDBError as e:
            if logger:
                logger.error(f"Search failed: {e}")
            return {'documents': [], 'metadatas': [], 'distances': [], 'ids': []}
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID
        
        Args:
            document_id: Document ID to retrieve
        
        Returns:
            Document data or None if not found
        """
        try:
            result = self.collection.get(ids=[document_id])
            
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
    
    def update_document(self, document_id: str, content: str = None, 
                       metadata: Dict[str, Any] = None, 
                       embedding: List[float] = None) -> bool:
        """
        Update an existing document
        
        Args:
            document_id: Document ID to update
            content: New content (optional)
            metadata: New metadata (optional)
            embedding: New embedding (optional)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get existing document
            existing = self.get_document(document_id)
            if not existing:
                return False
            
            # Prepare update data
            update_data = {
                'ids': [document_id],
                'documents': [content] if content else [existing['content']],
                'metadatas': [metadata] if metadata else [existing['metadata']]
            }
            
            if embedding:
                update_data['embeddings'] = [embedding]
            
            # Update in collection
            self.collection.update(**update_data)
            
            if logger:
                logger.info(f"Updated document {document_id}")
            
            return True
            
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to update document {document_id}: {e}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector store
        
        Args:
            document_id: Document ID to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[document_id])
            
            if logger:
                logger.info(f"Deleted document {document_id}")
            
            return True
            
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        
        Returns:
            Dict containing collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get sample documents for metadata analysis
            sample = self.collection.peek(limit=min(100, count))
            
            # Analyze document types
            doc_types = {}
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    doc_type = metadata.get('type', 'unknown')
                    doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            return {
                'total_documents': count,
                'document_types': doc_types,
                'last_updated': datetime.now().isoformat(),
                'persist_directory': self.persist_directory
            }
            
        except ChromaDBError as e:
            if logger:
                logger.error(f"Failed to get collection stats: {e}")
            return {'total_documents': 0, 'error': str(e)}
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.collection.delete(where={})
            
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
            # Get all documents
            all_docs = self.collection.get()
            
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

# Global vector store instance
_vector_store = None

def get_vector_store() -> VectorStore:
    """Get the global vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

def get_vector_store_health_status() -> Dict[str, Any]:
    """Get health status of the vector store"""
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_collection_stats()
        
        return {
            'status': 'healthy',
            'available': True,
            'stats': stats,
            'error': None
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'available': False,
            'stats': {},
            'error': str(e)
        } 