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
    from services.vector_store import get_vector_store
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
        self.vector_store = get_vector_store()
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
            error_msg = f"Migration failed: {str(e)}"
            print(f"\n❌ {error_msg}")
            if logger:
                logger.error(error_msg)
            
            self.migration_stats['errors'].append(error_msg)
            return self.migration_stats
    
    def _migrate_leads(self):
        """Migrate existing leads to vector database"""
        try:
            # Get all leads from database
            leads = self.db.get_all_leads()
            
            if not leads:
                print("   ℹ️  No leads found to migrate")
                return
            
            print(f"   📝 Found {len(leads)} leads to migrate")
            
            # Process leads in batches
            batch_size = 50
            for i in range(0, len(leads), batch_size):
                batch = leads[i:i + batch_size]
                self._process_lead_batch(batch)
                
                # Progress update
                processed = min(i + batch_size, len(leads))
                print(f"   📈 Processed {processed}/{len(leads)} leads")
            
        except Exception as e:
            error_msg = f"Failed to migrate leads: {str(e)}"
            print(f"   ❌ {error_msg}")
            if logger:
                logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def _process_lead_batch(self, leads: List[Dict[str, Any]]):
        """Process a batch of leads"""
        try:
            documents = []
            
            for lead in leads:
                try:
                    # Create document for vector storage
                    doc = self._create_lead_document(lead)
                    if doc:
                        documents.append(doc)
                        self.migration_stats['leads_successful'] += 1
                    else:
                        self.migration_stats['leads_failed'] += 1
                        
                except Exception as e:
                    self.migration_stats['leads_failed'] += 1
                    error_msg = f"Failed to process lead {lead.get('id', 'unknown')}: {str(e)}"
                    self.migration_stats['errors'].append(error_msg)
                    if logger:
                        logger.error(error_msg)
                
                self.migration_stats['leads_processed'] += 1
            
            # Add documents to vector store
            if documents:
                success = self.vector_store.add_documents(documents)
                if not success:
                    print("   ⚠️  Failed to add some documents to vector store")
            
        except Exception as e:
            error_msg = f"Failed to process lead batch: {str(e)}"
            print(f"   ❌ {error_msg}")
            if logger:
                logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def _create_lead_document(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document from lead data"""
        try:
            # Extract lead information
            lead_id = lead.get('id')
            title = lead.get('title', '')
            description = lead.get('description', '')
            ai_summary = lead.get('ai_summary', '')
            source = lead.get('source', 'unknown')
            link = lead.get('link', '')
            created_at = lead.get('created_at', datetime.now().isoformat())
            
            # Combine content for embedding
            content = f"{title} {description} {ai_summary}".strip()
            
            if not content:
                return None
            
            # Generate embedding
            embedding = self.embedding_service.embed_text(content)
            if not embedding:
                return None
            
            # Create document
            document = {
                'id': f"lead_{lead_id}",
                'content': content,
                'embedding': embedding,
                'metadata': {
                    'title': title,
                    'source': source,
                    'url': link,
                    'created_at': created_at,
                    'type': 'lead',
                    'original_id': lead_id
                }
            }
            
            return document
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to create lead document: {e}")
            return None
    
    def _migrate_search_history(self):
        """Migrate search history (optional)"""
        try:
            # Get recent search history
            search_history = self.db.get_search_history(limit=100)
            
            if not search_history:
                print("   ℹ️  No search history to migrate")
                return
            
            print(f"   📝 Found {len(search_history)} search queries to migrate")
            
            # Process search queries
            for search in search_history:
                try:
                    query = search.get('query', '')
                    if query:
                        # Create document from search query
                        doc = self._create_search_document(search)
                        if doc:
                            self.vector_store.add_documents([doc])
                            
                except Exception as e:
                    if logger:
                        logger.error(f"Failed to migrate search query: {e}")
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to migrate search history: {e}")
    
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
        """Migrate workshop project data"""
        try:
            # Get all projects
            projects = self.db.get_projects()
            
            if not projects:
                print("   ℹ️  No workshop projects to migrate")
                return
            
            print(f"   📝 Found {len(projects)} workshop projects to migrate")
            
            for project in projects:
                try:
                    # Get project analyses
                    analyses = self.db.get_project_analyses(project['id'])
                    
                    if analyses:
                        # Create documents from analyses
                        for analysis in analyses:
                            doc = self._create_analysis_document(analysis, project)
                            if doc:
                                self.vector_store.add_documents([doc])
                
                except Exception as e:
                    if logger:
                        logger.error(f"Failed to migrate project {project.get('id')}: {e}")
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to migrate workshop projects: {e}")
    
    def _create_analysis_document(self, analysis: Dict[str, Any], 
                                 project: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document from analysis data"""
        try:
            ai_analysis = analysis.get('ai_analysis', '')
            notes = analysis.get('notes', '')
            key_opinion_leaders = analysis.get('key_opinion_leaders', '')
            
            content = f"{ai_analysis} {notes} {key_opinion_leaders}".strip()
            
            if not content:
                return None
            
            embedding = self.embedding_service.embed_text(content)
            if not embedding:
                return None
            
            return {
                'id': f"analysis_{analysis.get('id')}",
                'content': content,
                'embedding': embedding,
                'metadata': {
                    'title': f"Analysis for {project.get('name', 'Unknown Project')}",
                    'source': 'workshop_analysis',
                    'type': 'analysis',
                    'project_id': project.get('id'),
                    'lead_id': analysis.get('lead_id'),
                    'relevancy_score': analysis.get('relevancy_score'),
                    'created_at': analysis.get('created_at', datetime.now().isoformat())
                }
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to create analysis document: {e}")
            return None
    
    def _verify_migration(self):
        """Verify that migration was successful"""
        try:
            # Get vector store statistics
            stats = self.vector_store.get_collection_stats()
            
            print(f"   📊 Vector store contains {stats.get('total_documents', 0)} documents")
            print(f"   📊 Document types: {stats.get('document_types', {})}")
            
            # Test RAG search
            print("   🔍 Testing RAG search...")
            test_result = self.rag_service.search("test query", top_k=5)
            
            if test_result.retrieved_documents:
                print(f"   ✅ RAG search working - found {len(test_result.retrieved_documents)} documents")
            else:
                print("   ⚠️  RAG search returned no results (may be normal if no relevant data)")
            
        except Exception as e:
            error_msg = f"Verification failed: {str(e)}"
            print(f"   ❌ {error_msg}")
            if logger:
                logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def _print_migration_summary(self):
        """Print migration summary"""
        stats = self.migration_stats
        
        print("\n" + "="*50)
        print("📊 MIGRATION SUMMARY")
        print("="*50)
        print(f"⏱️  Total time: {stats['total_time']:.2f} seconds")
        print(f"📝 Leads processed: {stats['leads_processed']}")
        print(f"✅ Leads successful: {stats['leads_successful']}")
        print(f"❌ Leads failed: {stats['leads_failed']}")
        
        if stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(stats['errors']) > 5:
                print(f"   ... and {len(stats['errors']) - 5} more errors")
        
        # Get final vector store stats
        try:
            final_stats = self.vector_store.get_collection_stats()
            print(f"\n🗄️  Vector store status:")
            print(f"   Total documents: {final_stats.get('total_documents', 0)}")
            print(f"   Document types: {final_stats.get('document_types', {})}")
        except Exception as e:
            print(f"   ❌ Failed to get final stats: {e}")
        
        print("="*50)
    
    def create_backup(self, backup_path: str = None) -> bool:
        """Create a backup of the vector database"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"./data/vector_db_backup_{timestamp}.json"
            
            success = self.vector_store.backup_collection(backup_path)
            
            if success:
                print(f"✅ Backup created at: {backup_path}")
            else:
                print(f"❌ Failed to create backup")
            
            return success
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

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