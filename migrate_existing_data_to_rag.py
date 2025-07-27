#!/usr/bin/env python3
"""
Migration Script: Convert Existing LeadFinder Data to RAG

This script migrates existing leads, search history, and workshop data
to the new RAG system by ingesting them into the vector database.
"""

import sys
import os
import time
import json
from typing import List, Dict, Any
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_leads_to_rag():
    """Migrate existing leads to RAG system"""
    print("📥 Migrating leads to RAG system...")
    
    try:
        from models.database import get_all_leads
        from services.ingestion_service import get_ingestion_service
        from services.vector_store_service import get_vector_store_service
        
        # Get all leads
        leads = get_all_leads()
        
        if not leads:
            print("   No leads found to migrate")
            return 0
        
        print(f"   Found {len(leads)} leads to migrate")
        
        # Initialize services
        ingestion_service = get_ingestion_service()
        vector_store = get_vector_store_service()
        
        migrated_count = 0
        failed_count = 0
        
        for lead in leads:
            try:
                # Ingest lead
                result = ingestion_service.ingest_lead(lead)
                
                if result.success and result.chunks:
                    # Store chunks in vector database
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
                        success = vector_store.upsert_documents(documents)
                        if success:
                            migrated_count += 1
                            print(f"   ✅ Migrated lead {lead.get('id')}: {lead.get('title', 'Unknown')[:50]}...")
                        else:
                            failed_count += 1
                            print(f"   ❌ Failed to store lead {lead.get('id')}")
                    else:
                        failed_count += 1
                        print(f"   ⚠️  No embeddings generated for lead {lead.get('id')}")
                else:
                    failed_count += 1
                    print(f"   ❌ Failed to ingest lead {lead.get('id')}: {result.error}")
                
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Error migrating lead {lead.get('id')}: {e}")
        
        print(f"   Migration complete: {migrated_count} successful, {failed_count} failed")
        return migrated_count
        
    except Exception as e:
        print(f"   ❌ Lead migration failed: {e}")
        return 0

def migrate_search_history_to_rag():
    """Migrate search history to RAG system"""
    print("\n📥 Migrating search history to RAG system...")
    
    try:
        from models.database import get_search_history
        from services.ingestion_service import get_ingestion_service
        from services.vector_store_service import get_vector_store_service
        
        # Get search history
        searches = get_search_history(limit=1000)  # Get more search history
        
        if not searches:
            print("   No search history found to migrate")
            return 0
        
        print(f"   Found {len(searches)} search records to migrate")
        
        # Initialize services
        ingestion_service = get_ingestion_service()
        vector_store = get_vector_store_service()
        
        migrated_count = 0
        failed_count = 0
        
        for search in searches:
            try:
                # Ingest search
                result = ingestion_service.ingest_search_result(search)
                
                if result.success and result.chunks:
                    # Store chunks in vector database
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
                        success = vector_store.upsert_documents(documents)
                        if success:
                            migrated_count += 1
                            print(f"   ✅ Migrated search {search.get('id')}: {search.get('query', 'Unknown')[:50]}...")
                        else:
                            failed_count += 1
                            print(f"   ❌ Failed to store search {search.get('id')}")
                    else:
                        failed_count += 1
                        print(f"   ⚠️  No embeddings generated for search {search.get('id')}")
                else:
                    failed_count += 1
                    print(f"   ❌ Failed to ingest search {search.get('id')}: {result.error}")
                
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Error migrating search {search.get('id')}: {e}")
        
        print(f"   Migration complete: {migrated_count} successful, {failed_count} failed")
        return migrated_count
        
    except Exception as e:
        print(f"   ❌ Search history migration failed: {e}")
        return 0

def migrate_workshop_data_to_rag():
    """Migrate workshop analysis data to RAG system"""
    print("\n📥 Migrating workshop data to RAG system...")
    
    try:
        from models.database import db
        from services.ingestion_service import get_ingestion_service
        from services.vector_store_service import get_vector_store_service
        
        # Get all projects
        projects = db.get_projects()
        
        if not projects:
            print("   No workshop projects found to migrate")
            return 0
        
        print(f"   Found {len(projects)} workshop projects to migrate")
        
        # Initialize services
        ingestion_service = get_ingestion_service()
        vector_store = get_vector_store_service()
        
        migrated_count = 0
        failed_count = 0
        
        for project in projects:
            try:
                # Get analyses for this project
                analyses = db.get_project_analyses(project['id'])
                
                if not analyses:
                    continue
                
                print(f"   Processing project: {project.get('name', 'Unknown')} ({len(analyses)} analyses)")
                
                for analysis in analyses:
                    try:
                        # Create workshop document
                        workshop_doc = {
                            'id': f"workshop_{analysis['id']}",
                            'title': f"Workshop Analysis: {project.get('name', 'Unknown')}",
                            'description': analysis.get('ai_analysis', ''),
                            'ai_summary': f"Relevancy Score: {analysis.get('relevancy_score', 0)}/5",
                            'source': 'workshop',
                            'link': '',
                            'created_at': analysis.get('created_at', datetime.now().isoformat()),
                            'project_name': project.get('name', ''),
                            'lead_id': analysis.get('lead_id'),
                            'key_opinion_leaders': analysis.get('key_opinion_leaders', ''),
                            'contact_info': analysis.get('contact_info', ''),
                            'notes': analysis.get('notes', '')
                        }
                        
                        # Ingest workshop document
                        result = ingestion_service.ingest_lead(workshop_doc)  # Reuse lead ingestion
                        
                        if result.success and result.chunks:
                            # Store chunks in vector database
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
                                success = vector_store.upsert_documents(documents)
                                if success:
                                    migrated_count += 1
                                else:
                                    failed_count += 1
                            else:
                                failed_count += 1
                        else:
                            failed_count += 1
                    
                    except Exception as e:
                        failed_count += 1
                        print(f"   ❌ Error migrating analysis {analysis.get('id')}: {e}")
                
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Error migrating project {project.get('id')}: {e}")
        
        print(f"   Migration complete: {migrated_count} successful, {failed_count} failed")
        return migrated_count
        
    except Exception as e:
        print(f"   ❌ Workshop data migration failed: {e}")
        return 0

def create_backup():
    """Create a backup of the current vector database"""
    print("\n💾 Creating backup of vector database...")
    
    try:
        from services.vector_store_service import get_vector_store_service
        
        vector_store = get_vector_store_service()
        
        # Create backup directory
        backup_dir = "./data/backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"rag_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Create backup
        success = vector_store.backup_collection(backup_path)
        
        if success:
            print(f"   ✅ Backup created: {backup_path}")
            return backup_path
        else:
            print("   ❌ Backup failed")
            return None
            
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return None

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        from services.vector_store_service import get_vector_store_service
        from services.rag_generator import get_rag_generator
        
        vector_store = get_vector_store_service()
        rag_generator = get_rag_generator()
        
        # Check vector store stats
        stats = vector_store.get_stats()
        print(f"   Vector store: {stats.total_documents} documents")
        print(f"   Document types: {stats.document_types}")
        
        # Test RAG functionality
        test_query = "research leads"
        result = rag_generator.generate_with_context(test_query, top_k=3)
        
        if result and not result.error:
            print(f"   RAG test: ✅ Working (confidence: {result.confidence_score:.3f})")
            return True
        else:
            print(f"   RAG test: ❌ Failed - {result.error if result else 'No result'}")
            return False
            
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 LeadFinder RAG Migration Script")
    print("=" * 50)
    
    # Check if vector store is available
    try:
        from services.vector_store_service import get_vector_store_service
        vector_store = get_vector_store_service()
        print("✅ Vector store service available")
    except Exception as e:
        print(f"❌ Vector store service not available: {e}")
        print("Please install ChromaDB: pip install chromadb")
        return 1
    
    # Check if embedding service is available
    try:
        from services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()
        print("✅ Embedding service available")
    except Exception as e:
        print(f"❌ Embedding service not available: {e}")
        print("Please install SentenceTransformers: pip install sentence-transformers")
        return 1
    
    # Create backup
    backup_path = create_backup()
    
    # Run migrations
    start_time = time.time()
    
    total_migrated = 0
    
    # Migrate leads
    leads_migrated = migrate_leads_to_rag()
    total_migrated += leads_migrated
    
    # Migrate search history
    searches_migrated = migrate_search_history_to_rag()
    total_migrated += searches_migrated
    
    # Migrate workshop data
    workshop_migrated = migrate_workshop_data_to_rag()
    total_migrated += workshop_migrated
    
    migration_time = time.time() - start_time
    
    print(f"\n📊 Migration Summary")
    print("=" * 50)
    print(f"Total documents migrated: {total_migrated}")
    print(f"Migration time: {migration_time:.2f} seconds")
    
    if backup_path:
        print(f"Backup created: {backup_path}")
    
    # Verify migration
    if verify_migration():
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the RAG system: python test_rag_implementation.py")
        print("2. Access RAG search at: http://localhost:5000/rag/search")
        print("3. Use the API endpoints for integration")
        return 0
    else:
        print("\n⚠️  Migration completed but verification failed")
        print("Please check the implementation and try again")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 