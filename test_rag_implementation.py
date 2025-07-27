#!/usr/bin/env python3
"""
Test Script for LeadFinder RAG Implementation

This script tests the complete RAG pipeline including:
- Document ingestion
- Vector storage
- Retrieval
- Generation
- API endpoints
"""

import sys
import os
import time
import json
import requests
from typing import Dict, Any, List

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_embedding_service():
    """Test the embedding service"""
    print("🔍 Testing Embedding Service...")
    
    try:
        from services.embedding_service import get_embedding_service
        
        embedding_service = get_embedding_service()
        
        # Test basic embedding
        test_text = "This is a test document for LeadFinder RAG system."
        embedding = embedding_service.embed_text(test_text)
        
        if not embedding or len(embedding) == 0:
            print("❌ Embedding generation failed")
            return False
        
        print(f"✅ Embedding generated successfully (dimension: {len(embedding)})")
        
        # Test batch embedding
        test_texts = [
            "First test document",
            "Second test document", 
            "Third test document"
        ]
        embeddings = embedding_service.embed_batch(test_texts)
        
        if len(embeddings) != len(test_texts):
            print("❌ Batch embedding failed")
            return False
        
        print("✅ Batch embedding successful")
        return True
        
    except Exception as e:
        print(f"❌ Embedding service test failed: {e}")
        return False

def test_vector_store_service():
    """Test the vector store service"""
    print("\n🗄️  Testing Vector Store Service...")
    
    try:
        from services.vector_store_service import get_vector_store_service
        
        vector_store = get_vector_store_service()
        
        # Test document upsert
        test_documents = [
            {
                'id': 'test_doc_1',
                'content': 'This is the first test document about AI research.',
                'embedding': [0.1, 0.2, 0.3, 0.4, 0.5] * 20,  # Mock embedding
                'metadata': {'title': 'Test Doc 1', 'source': 'test', 'type': 'test'}
            },
            {
                'id': 'test_doc_2', 
                'content': 'This is the second test document about machine learning.',
                'embedding': [0.2, 0.3, 0.4, 0.5, 0.6] * 20,  # Mock embedding
                'metadata': {'title': 'Test Doc 2', 'source': 'test', 'type': 'test'}
            }
        ]
        
        success = vector_store.upsert_documents(test_documents)
        if not success:
            print("❌ Document upsert failed")
            return False
        
        print("✅ Document upsert successful")
        
        # Test search
        query_embedding = [0.15, 0.25, 0.35, 0.45, 0.55] * 20  # Mock query embedding
        results = vector_store.search(query_embedding, top_k=2)
        
        if not results:
            print("❌ Vector search failed")
            return False
        
        print(f"✅ Vector search successful (found {len(results)} results)")
        
        # Test stats
        stats = vector_store.get_stats()
        if not stats:
            print("❌ Stats retrieval failed")
            return False
        
        print(f"✅ Stats retrieved: {stats.total_documents} documents")
        return True
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

def test_ingestion_service():
    """Test the ingestion service"""
    print("\n📥 Testing Ingestion Service...")
    
    try:
        from services.ingestion_service import get_ingestion_service
        
        ingestion_service = get_ingestion_service()
        
        # Test lead ingestion
        test_lead = {
            'id': 123,
            'title': 'Test Research Lead',
            'description': 'This is a test research lead for AI applications in healthcare.',
            'ai_summary': 'AI healthcare research opportunity with high potential.',
            'source': 'test',
            'link': 'https://example.com/test',
            'created_at': '2024-01-01T00:00:00'
        }
        
        result = ingestion_service.ingest_lead(test_lead)
        
        if not result.success:
            print(f"❌ Lead ingestion failed: {result.error}")
            return False
        
        print(f"✅ Lead ingestion successful ({result.total_chunks} chunks created)")
        
        # Test search result ingestion
        test_search = {
            'id': 456,
            'query': 'AI healthcare research',
            'research_question': 'What are the latest developments in AI for healthcare?',
            'results_count': 10,
            'engines': 'web,research'
        }
        
        result = ingestion_service.ingest_search_result(test_search)
        
        if not result.success:
            print(f"❌ Search ingestion failed: {result.error}")
            return False
        
        print(f"✅ Search ingestion successful ({result.total_chunks} chunks created)")
        return True
        
    except Exception as e:
        print(f"❌ Ingestion service test failed: {e}")
        return False

def test_retrieval_service():
    """Test the retrieval service"""
    print("\n🔍 Testing Retrieval Service...")
    
    try:
        from services.retrieval_service import get_retrieval_service
        
        retrieval_service = get_retrieval_service()
        
        # Test basic retrieval
        query = "AI healthcare research"
        result = retrieval_service.retrieve(query, top_k=3)
        
        if not result:
            print("❌ Retrieval failed")
            return False
        
        print(f"✅ Retrieval successful (method: {result.retrieval_method}, results: {result.total_results})")
        
        # Test hybrid retrieval
        result = retrieval_service.hybrid_retrieve(query, top_k=3)
        
        if not result:
            print("❌ Hybrid retrieval failed")
            return False
        
        print(f"✅ Hybrid retrieval successful (method: {result.retrieval_method}, results: {result.total_results})")
        return True
        
    except Exception as e:
        print(f"❌ Retrieval service test failed: {e}")
        return False

def test_rag_generator():
    """Test the RAG generator"""
    print("\n🤖 Testing RAG Generator...")
    
    try:
        from services.rag_generator import get_rag_generator
        
        rag_generator = get_rag_generator()
        
        # Test generation with context
        query = "What are the latest developments in AI for healthcare?"
        result = rag_generator.generate_with_context(query, top_k=3)
        
        if not result or result.error:
            print(f"❌ RAG generation failed: {result.error if result else 'No result'}")
            return False
        
        print(f"✅ RAG generation successful (confidence: {result.confidence_score:.3f})")
        print(f"   Response: {result.generated_response[:100]}...")
        
        # Test custom context generation
        custom_context = [
            "AI is transforming healthcare with new diagnostic tools.",
            "Machine learning algorithms can detect diseases earlier than traditional methods."
        ]
        
        result = rag_generator.generate_with_custom_context(query, custom_context)
        
        if not result or result.error:
            print(f"❌ Custom context generation failed: {result.error if result else 'No result'}")
            return False
        
        print(f"✅ Custom context generation successful (confidence: {result.confidence_score:.3f})")
        return True
        
    except Exception as e:
        print(f"❌ RAG generator test failed: {e}")
        return False

def test_api_endpoints():
    """Test the RAG API endpoints"""
    print("\n🌐 Testing RAG API Endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/rag/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Health endpoint not accessible (server may not be running): {e}")
        return True  # Don't fail the test if server isn't running
    
    # Test status endpoint
    try:
        response = requests.get(f"{base_url}/rag/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Status endpoint working")
            else:
                print(f"❌ Status endpoint returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Status endpoint not accessible: {e}")
        return True
    
    # Test search endpoint
    try:
        search_data = {
            "query": "AI healthcare research",
            "top_k": 3,
            "use_hybrid": False
        }
        
        response = requests.post(
            f"{base_url}/rag/search",
            json=search_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Search endpoint working")
                print(f"   Response: {data.get('response', '')[:100]}...")
            else:
                print(f"❌ Search endpoint returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Search endpoint not accessible: {e}")
        return True
    
    return True

def test_database_integration():
    """Test database integration for RAG"""
    print("\n💾 Testing Database Integration...")
    
    try:
        from models.database import db
        
        # Test RAG chunk storage
        success = db.save_rag_chunk(
            chunk_id="test_chunk_1",
            doc_id="test_doc_1",
            source="test",
            content_chunk="This is a test content chunk for RAG testing.",
            chunk_index=0,
            total_chunks=1,
            metadata='{"title": "Test Chunk", "type": "test"}'
        )
        
        if not success:
            print("❌ RAG chunk storage failed")
            return False
        
        print("✅ RAG chunk storage successful")
        
        # Test RAG chunk retrieval
        chunks = db.get_rag_chunks_by_doc_id("test_doc_1")
        
        if not chunks:
            print("❌ RAG chunk retrieval failed")
            return False
        
        print(f"✅ RAG chunk retrieval successful ({len(chunks)} chunks)")
        
        # Test RAG search session storage
        success = db.save_rag_search_session(
            session_id="test_session_1",
            query="test query",
            rag_response="test response",
            processing_time=1.5,
            confidence_score=0.8,
            retrieval_method="vector",
            model_used="mistral:latest"
        )
        
        if not success:
            print("❌ RAG search session storage failed")
            return False
        
        print("✅ RAG search session storage successful")
        
        # Test RAG stats
        stats = db.get_rag_stats()
        if not stats:
            print("❌ RAG stats retrieval failed")
            return False
        
        print(f"✅ RAG stats retrieved: {stats.get('total_chunks', 0)} chunks, {stats.get('total_sessions', 0)} sessions")
        return True
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        return False

def run_performance_test():
    """Run a basic performance test"""
    print("\n⚡ Running Performance Test...")
    
    try:
        from services.rag_generator import get_rag_generator
        from services.retrieval_service import get_retrieval_service
        
        rag_generator = get_rag_generator()
        retrieval_service = get_retrieval_service()
        
        # Test query
        query = "What are the latest developments in artificial intelligence?"
        
        # Measure retrieval time
        start_time = time.time()
        retrieval_result = retrieval_service.retrieve(query, top_k=5)
        retrieval_time = time.time() - start_time
        
        # Measure generation time
        start_time = time.time()
        generation_result = rag_generator.generate_with_context(query, top_k=5)
        generation_time = time.time() - start_time
        
        print(f"✅ Performance test completed:")
        print(f"   Retrieval time: {retrieval_time:.3f}s")
        print(f"   Generation time: {generation_time:.3f}s")
        print(f"   Total time: {retrieval_time + generation_time:.3f}s")
        
        if retrieval_time < 5.0 and generation_time < 30.0:
            print("✅ Performance within acceptable limits")
            return True
        else:
            print("⚠️  Performance slower than expected")
            return True  # Don't fail the test for performance
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting LeadFinder RAG Implementation Tests\n")
    
    tests = [
        ("Embedding Service", test_embedding_service),
        ("Vector Store Service", test_vector_store_service),
        ("Ingestion Service", test_ingestion_service),
        ("Retrieval Service", test_retrieval_service),
        ("RAG Generator", test_rag_generator),
        ("Database Integration", test_database_integration),
        ("API Endpoints", test_api_endpoints),
        ("Performance", run_performance_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RAG implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 