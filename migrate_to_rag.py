#!/usr/bin/env python3
"""
LeadFinder RAG Migration Script

This script migrates existing LeadFinder data to the new RAG-based architecture.
It processes existing leads, research papers, and other documents to create
vector embeddings and populate the vector database.
"""

import sys
import os
import time
import json
from typing import List, Dict, Any
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from models.database import DatabaseConnection
except ImportError as e:
    print(f"❌ Failed to import database: {e}")
    sys.exit(1)

try:
    from services.vector_store_service import get_vector_store_service
    from services.embedding_service import get_embedding_service
    from services.rag_search_service import get_rag_search_service
except ImportError as e:
    print(f"❌ Failed to import RAG services: {e}")
    print("Please install required dependencies:")
    print("pip install chromadb sentence-transformers")
    sys.exit(1)

try:
    from utils.logger import get_logger
    logger = get_logger('rag_migration')
except ImportError:
    logger = None

class RAGMigration:
    """Handles migration of existing data to RAG system"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.vector_store = get_vector_store_service()
        self.embedding_service = get_embedding_service()
        self.rag_service = get_rag_search_service()
        
        self.migration_stats = {
            'leads_processed': 0,
            'leads_successful': 0,
            'leads_failed': 0,
            'start_time': time.time(),
            'errors': []
        }
    
    def migrate_all_data(self) -> Dict[str, Any]:
        """
        Migrate all existing data to RAG system
        
        Returns:
            Migration statistics
        """
        print("🔄 Starting RAG migration...")
        
        try:
            # Step 1: Migrate leads
            print("\n📊 Step 1: Migrating leads...")
            self._migrate_leads()
            
            # Step 2: Migrate search history (optional)
            print("\n📊 Step 2: Migrating search history...")
            self._migrate_search_history()
            
            # Step 3: Migrate workshop projects
            print("\n📊 Step 3: Migrating workshop projects...")
            self._migrate_workshop_projects()
            
            # Step 4: Verify migration
            print("\n📊 Step 4: Verifying migration...")
            self._verify_migration()
            
            # Calculate final statistics
            self.migration_stats['end_time'] = time.time()
            self.migration_stats['total_time'] = (
                self.migration_stats['end_time'] - self.migration_stats['start_time']
            )
            
            print(f"\n✅ Migration completed successfully!")
            self._print_migration_summary()
            
            return self.migration_stats
            
        except Exception as e:
            if logger:
                logger.error(f"Migration failed: {e}")
            print(f"❌ Migration failed: {e}")
            return self.migration_stats
    
    def _migrate_leads(self):
        """Migrate existing leads to RAG system"""
        try:
            # Get all leads from database
            leads = self.db.get_all_leads()
            
            if not leads:
                print("   No leads found to migrate")
                return
            
            print(f"   Found {len(leads)} leads to migrate")
            
            # Process leads in batches
            batch_size = 10
            for i in range(0, len(leads), batch_size):
                batch = leads[i:i + batch_size]
                self._process_lead_batch(batch)
                
                # Progress update
                processed = min(i + batch_size, len(leads))
                print(f"   Progress: {processed}/{len(leads)} leads processed")
            
        except Exception as e:
            error_msg = f"Failed to migrate leads: {e}"
            if logger:
                logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def _process_lead_batch(self, leads: List[Dict[str, Any]]):
        """Process a batch of leads"""
        documents = []
        
        for lead in leads:
            try:
                # Create document from lead
                doc = self._create_lead_document(lead)
                if doc:
                    documents.append(doc)
                    self.migration_stats['leads_successful'] += 1
                else:
                    self.migration_stats['leads_failed'] += 1
                    
            except Exception as e:
                self.migration_stats['leads_failed'] += 1
                error_msg = f"Failed to process lead {lead.get('id', 'unknown')}: {e}"
                if logger:
                    logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
        
        # Add documents to vector store
        if documents:
            try:
                success = self.vector_store.upsert_documents(documents)
                if success:
                    self.migration_stats['leads_processed'] += len(documents)
                else:
                    self.migration_stats['leads_failed'] += len(documents)
                    
            except Exception as e:
                error_msg = f"Failed to add documents to vector store: {e}"
                if logger:
                    logger.error(error_msg)
                self.migration_stats['errors'].append(error_msg)
    
    def _create_lead_document(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document from lead data"""
        try:
            # Extract lead information
            title = lead.get('title', '')
            description = lead.get('description', '')
            url = lead.get('url', '')
            source = lead.get('source', '')
            
            # Combine content
            content = f"{title}\n\n{description}".strip()
            
            if not content:
                return None
            
            # Generate embedding
            embedding = self.embedding_service.embed_text(content)
            if not embedding:
                return None
            
            return {
                'id': f"lead_{lead.get('id')}",
                'content': content,
                'embedding': embedding,
                'metadata': {
                    'title': title,
                    'url': url,
                    'source': source,
                    'type': 'lead',
                    'original_id': lead.get('id'),
                    'created_at': lead.get('created_at', datetime.now().isoformat())
                }
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to create lead document: {e}")
            return None
    
    def _migrate_search_history(self):
        """Migrate search history to RAG system"""
        try:
            # Get search history from database
            searches = self.db.get_search_history()
            
            if not searches:
                print("   No search history found to migrate")
                return
            
            print(f"   Found {len(searches)} search queries to migrate")
            
            documents = []
            for search in searches:
                doc = self._create_search_document(search)
                if doc:
                    documents.append(doc)
            
            # Add to vector store
            if documents:
                success = self.vector_store.upsert_documents(documents)
                if success:
                    print(f"   Successfully migrated {len(documents)} search queries")
                else:
                    print("   Failed to migrate search queries")
                    
        except Exception as e:
            error_msg = f"Failed to migrate search history: {e}"
            if logger:
                logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def _create_search_document(self, search: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document from search data"""
        try:
            query = search.get('query', '')
            research_question = search.get('research_question', '')
            
            content = f"{query} {research_question}".strip()
            
            if not content:
                return None
            
            embedding = self.embedding_service.embed_text(content)
            if not embedding:
                return None
            
            return {
                'id': f"search_{search.get('id')}",
                'content': content,
                'embedding': embedding,
                'metadata': {
                    'title': f"Search: {query[:50]}...",
                    'source': 'search_history',
                    'type': 'search_query',
                    'original_id': search.get('id'),
                    'created_at': search.get('created_at', datetime.now().isoformat())
                }
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to create search document: {e}")
            return None
    
    def _migrate_workshop_projects(self):
        """Migrate workshop project data to RAG system"""
        try:
            # Get workshop projects from database
            projects = self.db.get_workshop_projects()
            
            if not projects:
                print("   No workshop projects found to migrate")
                return
            
            print(f"   Found {len(projects)} workshop projects to migrate")
            
            documents = []
            for project in projects:
                doc = self._create_project_document(project)
                if doc:
                    documents.append(doc)
            
            # Add to vector store
            if documents:
                success = self.vector_store.upsert_documents(documents)
                if success:
                    print(f"   Successfully migrated {len(documents)} workshop projects")
                else:
                    print("   Failed to migrate workshop projects")
                    
        except Exception as e:
            error_msg = f"Failed to migrate workshop projects: {e}"
            if logger:
                logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def _create_project_document(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document from workshop project data"""
        try:
            name = project.get('name', '')
            description = project.get('description', '')
            analysis = project.get('analysis', '')
            
            content = f"{name}\n\n{description}\n\n{analysis}".strip()
            
            if not content:
                return None
            
            embedding = self.embedding_service.embed_text(content)
            if not embedding:
                return None
            
            return {
                'id': f"project_{project.get('id')}",
                'content': content,
                'embedding': embedding,
                'metadata': {
                    'title': name,
                    'source': 'workshop_project',
                    'type': 'project',
                    'original_id': project.get('id'),
                    'created_at': project.get('created_at', datetime.now().isoformat())
                }
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to create project document: {e}")
            return None
    
    def _verify_migration(self):
        """Verify that migration was successful"""
        try:
            # Get vector store statistics
            stats = self.vector_store.get_stats()
            
            print(f"   Vector store statistics:")
            print(f"     - Total documents: {stats.total_documents}")
            print(f"     - Total chunks: {stats.total_chunks}")
            print(f"     - Collection size: {stats.collection_size_mb:.2f} MB")
            
            # Test RAG search
            test_query = "test migration"
            result = self.rag_service.search(test_query, top_k=1)
            
            if result and result.retrieved_documents:
                print("   ✅ RAG search test successful")
            else:
                print("   ⚠️  RAG search test failed")
                
        except Exception as e:
            error_msg = f"Failed to verify migration: {e}"
            if logger:
                logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def _print_migration_summary(self):
        """Print migration summary"""
        stats = self.migration_stats
        
        print(f"\n📊 Migration Summary:")
        print(f"   Total leads processed: {stats['leads_processed']}")
        print(f"   Successful migrations: {stats['leads_successful']}")
        print(f"   Failed migrations: {stats['leads_failed']}")
        print(f"   Total time: {stats['total_time']:.2f} seconds")
        
        if stats['errors']:
            print(f"   Errors encountered: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"     - {error}")
    
    def create_backup(self) -> str:
        """Create backup of existing data"""
        try:
            backup_dir = f"backup_{int(time.time())}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup database
            if hasattr(self.db, 'backup'):
                backup_path = self.db.backup(backup_dir)
                print(f"   Database backup created: {backup_path}")
            
            # Backup vector store
            if hasattr(self.vector_store, 'backup_collection'):
                backup_path = f"{backup_dir}/vector_store_backup"
                success = self.vector_store.backup_collection(backup_path)
                if success:
                    print(f"   Vector store backup created: {backup_path}")
            
            return backup_dir
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to create backup: {e}")
            return None


def main():
    """Main migration function"""
    print("🔄 LeadFinder RAG Migration Tool")
    print("="*40)
    
    # Check if RAG services are available
    try:
        migration = RAGMigration()
    except Exception as e:
        print(f"❌ Failed to initialize migration: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("pip install chromadb sentence-transformers")
        sys.exit(1)
    
    # Ask user for confirmation
    print("\nThis will migrate existing LeadFinder data to the RAG system.")
    print("This process may take several minutes depending on data size.")
    
    response = input("\nDo you want to proceed? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Migration cancelled.")
        sys.exit(0)
    
    # Create backup first
    print("\n📦 Creating backup...")
    migration.create_backup()
    
    # Run migration
    stats = migration.migrate_all_data()
    
    # Exit with appropriate code
    if stats['errors']:
        print(f"\n⚠️  Migration completed with {len(stats['errors'])} errors")
        sys.exit(1)
    else:
        print(f"\n✅ Migration completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main() 