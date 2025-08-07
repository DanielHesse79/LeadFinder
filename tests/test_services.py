"""
Comprehensive unit tests for LeadFinder services
"""
import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import services to test
try:
    from services.ollama_service import OllamaService
    from services.unified_search_service import UnifiedSearchService, SearchQuery, SearchResult
    from services.rag_generator import RAGGenerator, RAGGenerationResult
    from services.retrieval_service import RetrievalService, RetrievalResult
    from services.vector_store_service import VectorStoreService, VectorSearchResult
    from services.embedding_service import EmbeddingService
    from services.serp_service import SerpService
    from services.pubmed_service import PubMedService
    from services.orcid_service import OrcidService
    from services.semantic_scholar_service import SemanticScholarService
    from services.swecris_api import SweCRISAPI
    from services.cordis_api import CORDISAPI
    from services.nih_api import NIHAPI
    from services.nsf_api import NSFAPI
    from services.webscraper_service import WebScraperService
    from services.pdf_service import PDFService
    from services.markdown_service import MarkdownService
    from services.langchain_analyzer import LangChainAnalyzer
    from services.scihub_service import SciHubService
    from services.scihub_enhanced_service import SciHubEnhancedService
    from services.runpod_service import RunPodService
    from services.name_extraction_service import NameExtractionService
    from services.suppai_service import SuppAIService
except ImportError as e:
    pytest.skip(f"Services not available: {e}", allow_module_level=True)

# Import utilities
try:
    from utils.error_handler import LeadFinderError, APIServiceError, AIProcessingError
    from utils.cache_manager import CacheManager
    from utils.health_monitor import HealthMonitor
    from utils.progress_manager import ProgressManager
except ImportError as e:
    pytest.skip(f"Utilities not available: {e}", allow_module_level=True)

class TestOllamaService:
    """Test Ollama service functionality"""
    
    @pytest.fixture
    def ollama_service(self):
        """Create Ollama service instance"""
        with patch('services.ollama_service.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'models': [
                    {'name': 'mistral:latest'},
                    {'name': 'deepseek-coder:latest'}
                ]
            }
            return OllamaService(base_url="http://localhost:11434")
    
    def test_initialization(self, ollama_service):
        """Test service initialization"""
        assert ollama_service.base_url == "http://localhost:11434"
        assert ollama_service.api_url == "http://localhost:11434/api/generate"
        assert ollama_service.tags_url == "http://localhost:11434/api/tags"
    
    def test_get_available_models(self, ollama_service):
        """Test getting available models"""
        models = ollama_service.get_available_models()
        assert isinstance(models, list)
        assert 'mistral:latest' in models
    
    def test_set_preferred_model(self, ollama_service):
        """Test setting preferred model"""
        # Test successful model setting
        result = ollama_service.set_preferred_model('mistral:latest')
        assert result is True
        assert ollama_service.selected_model == 'mistral:latest'
        
        # Test setting non-existent model
        result = ollama_service.set_preferred_model('non-existent-model')
        assert result is False
    
    @patch('services.ollama_service.requests.post')
    def test_call_ollama(self, mock_post, ollama_service):
        """Test calling Ollama API"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'response': 'Test response',
            'done': True
        }
        
        response = ollama_service._call_ollama("Test prompt")
        assert response == "Test response"
    
    def test_analyze_relevance(self, ollama_service):
        """Test relevance analysis"""
        with patch.object(ollama_service, '_call_ollama') as mock_call:
            mock_call.return_value = "This is relevant to epigenetics research."
            
            result = ollama_service.analyze_relevance(
                title="Epigenetics Study",
                snippet="Research on DNA methylation",
                link="https://example.com",
                research_question="epigenetics and diabetes"
            )
            
            assert result is not None
            assert "relevant" in result.lower()

class TestUnifiedSearchService:
    """Test unified search service functionality"""
    
    @pytest.fixture
    def search_service(self):
        """Create unified search service instance"""
        return UnifiedSearchService()
    
    def test_search_query_creation(self):
        """Test SearchQuery dataclass"""
        query = SearchQuery(
            query="epigenetics",
            search_type="unified",
            engines=["google", "pubmed"],
            max_results=10,
            research_question="epigenetics and diabetes"
        )
        
        assert query.query == "epigenetics"
        assert query.search_type == "unified"
        assert "google" in query.engines
        assert query.max_results == 10
    
    def test_search_result_creation(self):
        """Test SearchResult dataclass"""
        result = SearchResult(
            title="Test Title",
            description="Test description",
            url="https://example.com",
            source="google",
            relevance_score=0.85
        )
        
        assert result.title == "Test Title"
        assert result.relevance_score == 0.85
        assert result.timestamp is not None
    
    @patch('services.unified_search_service.serp_service')
    @patch('services.unified_search_service.pubmed_service')
    def test_web_search(self, mock_pubmed, mock_serp, search_service):
        """Test web search functionality"""
        # Mock serp service response
        mock_serp.search.return_value = [
            {
                'title': 'Test Result',
                'snippet': 'Test snippet',
                'link': 'https://example.com'
            }
        ]
        
        query = SearchQuery(
            query="epigenetics",
            search_type="web",
            engines=["google"],
            max_results=5
        )
        
        results = search_service._web_search(query)
        assert len(results) > 0
        assert isinstance(results[0], SearchResult)
    
    @patch('services.unified_search_service.ollama_service')
    def test_analyze_results(self, mock_ollama, search_service):
        """Test AI analysis of search results"""
        mock_ollama.analyze_relevance.return_value = "This is relevant."
        
        results = [
            SearchResult(
                title="Test Result",
                description="Test description",
                url="https://example.com",
                source="google",
                relevance_score=0.0
            )
        ]
        
        analyzed_results = search_service._analyze_results(
            results, 
            research_question="epigenetics"
        )
        
        assert len(analyzed_results) == 1
        assert analyzed_results[0].relevance_score > 0.0

class TestRAGGenerator:
    """Test RAG generator functionality"""
    
    @pytest.fixture
    def rag_generator(self):
        """Create RAG generator instance"""
        with patch('services.rag_generator.get_retrieval_service') as mock_retrieval:
            with patch('services.rag_generator.ollama_service') as mock_ollama:
                mock_retrieval.return_value = Mock()
                mock_ollama.return_value = Mock()
                return RAGGenerator()
    
    def test_rag_generation_result(self):
        """Test RAGGenerationResult dataclass"""
        result = RAGGenerationResult(
            query="test query",
            generated_response="test response",
            retrieved_context=[],
            processing_time=1.5,
            confidence_score=0.85,
            model_used="mistral:latest",
            retrieval_method="vector"
        )
        
        assert result.query == "test query"
        assert result.confidence_score == 0.85
        assert result.model_used == "mistral:latest"
    
    def test_build_context(self, rag_generator):
        """Test context building"""
        mock_chunks = [
            Mock(content="Chunk 1", metadata={'source': 'test'}),
            Mock(content="Chunk 2", metadata={'source': 'test'})
        ]
        
        context = rag_generator._build_context(mock_chunks)
        assert "Chunk 1" in context
        assert "Chunk 2" in context
    
    @patch.object(RAGGenerator, '_generate_response')
    def test_generate_with_context(self, mock_generate, rag_generator):
        """Test RAG generation with context"""
        mock_generate.return_value = "Generated response"
        
        # Mock retrieval service
        mock_retrieval = Mock()
        mock_retrieval.retrieve.return_value = Mock(
            retrieved_chunks=[Mock(content="Test chunk")]
        )
        rag_generator.retrieval_service = mock_retrieval
        
        result = rag_generator.generate_with_context("test query")
        
        assert isinstance(result, RAGGenerationResult)
        assert result.generated_response == "Generated response"

class TestRetrievalService:
    """Test retrieval service functionality"""
    
    @pytest.fixture
    def retrieval_service(self):
        """Create retrieval service instance"""
        with patch('services.retrieval_service.get_embedding_service') as mock_embedding:
            with patch('services.retrieval_service.get_vector_store_service') as mock_vector:
                with patch('services.retrieval_service.get_unified_search_service') as mock_search:
                    mock_embedding.return_value = Mock()
                    mock_vector.return_value = Mock()
                    mock_search.return_value = Mock()
                    return RetrievalService()
    
    def test_retrieval_result(self):
        """Test RetrievalResult dataclass"""
        result = RetrievalResult(
            query="test query",
            retrieved_chunks=[],
            fallback_results=[],
            processing_time=1.0,
            retrieval_method="vector",
            total_results=0,
            confidence_score=0.8
        )
        
        assert result.query == "test query"
        assert result.retrieval_method == "vector"
        assert result.confidence_score == 0.8
    
    def test_process_query(self, retrieval_service):
        """Test query processing"""
        query_context = retrieval_service._process_query(
            "test query", 
            top_k=5, 
            filters={'source': 'test'}
        )
        
        assert query_context.original_query == "test query"
        assert query_context.top_k == 5
        assert query_context.filters['source'] == 'test'
    
    @patch.object(RetrievalService, '_vector_search')
    def test_retrieve_vector_success(self, mock_vector_search, retrieval_service):
        """Test successful vector retrieval"""
        mock_vector_search.return_value = [Mock()]
        
        result = retrieval_service.retrieve("test query")
        
        assert result.retrieval_method == "vector"
        assert len(result.retrieved_chunks) > 0
    
    @patch.object(RetrievalService, '_vector_search')
    @patch.object(RetrievalService, '_fallback_search')
    def test_retrieve_with_fallback(self, mock_fallback, mock_vector_search, retrieval_service):
        """Test retrieval with fallback"""
        mock_vector_search.return_value = []
        mock_fallback.return_value = [{'title': 'Test result'}]
        
        result = retrieval_service.retrieve("test query", use_fallback=True)
        
        assert result.retrieval_method == "fallback"
        assert len(result.fallback_results) > 0

class TestVectorStoreService:
    """Test vector store service functionality"""
    
    @pytest.fixture
    def vector_service(self):
        """Create vector store service instance"""
        with patch('services.vector_store_service.chromadb') as mock_chroma:
            mock_client = Mock()
            mock_collection = Mock()
            mock_client.get_or_create_collection.return_value = mock_collection
            mock_chroma.Client.return_value = mock_client
            return VectorStoreService()
    
    def test_vector_search_result(self):
        """Test VectorSearchResult dataclass"""
        result = VectorSearchResult(
            id="test_id",
            content="test content",
            metadata={'source': 'test'},
            similarity_score=0.85
        )
        
        assert result.id == "test_id"
        assert result.similarity_score == 0.85
    
    def test_add_documents(self, vector_service):
        """Test adding documents to vector store"""
        documents = [
            {
                'id': 'doc1',
                'content': 'Test content 1',
                'metadata': {'source': 'test'}
            },
            {
                'id': 'doc2',
                'content': 'Test content 2',
                'metadata': {'source': 'test'}
            }
        ]
        
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        result = vector_service.add_documents(documents, embeddings)
        assert result is True

class TestEmbeddingService:
    """Test embedding service functionality"""
    
    @pytest.fixture
    def embedding_service(self):
        """Create embedding service instance"""
        with patch('services.embedding_service.SentenceTransformer') as mock_transformer:
            mock_model = Mock()
            mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
            mock_transformer.return_value = mock_model
            return EmbeddingService()
    
    def test_embed_text(self, embedding_service):
        """Test text embedding"""
        embedding = embedding_service.embed_text("Test text")
        assert isinstance(embedding, list)
        assert len(embedding) > 0
    
    def test_embed_batch(self, embedding_service):
        """Test batch embedding"""
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = embedding_service.embed_batch(texts)
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)

class TestAPIServices:
    """Test various API services"""
    
    @pytest.fixture
    def serp_service(self):
        """Create SerpAPI service instance"""
        return SerpService()
    
    @pytest.fixture
    def pubmed_service(self):
        """Create PubMed service instance"""
        return PubMedService()
    
    @pytest.fixture
    def orcid_service(self):
        """Create ORCID service instance"""
        return OrcidService()
    
    def test_serp_service_initialization(self, serp_service):
        """Test SerpAPI service initialization"""
        assert hasattr(serp_service, 'api_key')
        assert hasattr(serp_service, 'base_url')
    
    @patch('services.serp_service.requests.get')
    def test_serp_search(self, mock_get, serp_service):
        """Test SerpAPI search"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'organic_results': [
                {
                    'title': 'Test Result',
                    'snippet': 'Test snippet',
                    'link': 'https://example.com'
                }
            ]
        }
        
        results = serp_service.search("test query", ["google"], num_results=1)
        assert len(results) > 0
        assert results[0]['title'] == 'Test Result'
    
    def test_pubmed_service_initialization(self, pubmed_service):
        """Test PubMed service initialization"""
        assert hasattr(pubmed_service, 'base_url')
        assert pubmed_service.base_url == 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    
    @patch('services.pubmed_service.requests.get')
    def test_pubmed_search(self, mock_get, pubmed_service):
        """Test PubMed search"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '''
        <eSearchResult>
            <IdList>
                <Id>12345</Id>
            </IdList>
        </eSearchResult>
        '''
        
        results = pubmed_service.search_articles("epigenetics", max_results=1)
        assert isinstance(results, list)

class TestUtilityServices:
    """Test utility services"""
    
    @pytest.fixture
    def cache_manager(self):
        """Create cache manager instance"""
        return CacheManager()
    
    @pytest.fixture
    def health_monitor(self):
        """Create health monitor instance"""
        return HealthMonitor()
    
    @pytest.fixture
    def progress_manager(self):
        """Create progress manager instance"""
        return ProgressManager()
    
    def test_cache_manager(self, cache_manager):
        """Test cache manager functionality"""
        # Test setting and getting cache
        cache_manager.set("test_key", "test_value", ttl=60)
        value = cache_manager.get("test_key")
        assert value == "test_value"
        
        # Test cache expiration
        cache_manager.set("expire_key", "expire_value", ttl=0)
        value = cache_manager.get("expire_key")
        assert value is None
    
    def test_health_monitor(self, health_monitor):
        """Test health monitor functionality"""
        status = health_monitor.get_health_status()
        assert isinstance(status, dict)
        assert 'system' in status
        assert 'services' in status
    
    def test_progress_manager(self, progress_manager):
        """Test progress manager functionality"""
        # Test creating progress context
        with progress_manager.create_context("test_task") as ctx:
            ctx.update_progress(50, "Halfway done")
            assert ctx.get_progress() == 50
        
        # Test getting progress
        progress = progress_manager.get_progress("test_task")
        assert progress is not None

class TestErrorHandling:
    """Test error handling functionality"""
    
    def test_custom_exceptions(self):
        """Test custom exception classes"""
        # Test LeadFinderError
        error = LeadFinderError("Test error", "TEST_ERROR")
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        
        # Test APIServiceError
        api_error = APIServiceError("API error", "test_service", "/test")
        assert api_error.service == "test_service"
        assert api_error.endpoint == "/test"
        
        # Test AIProcessingError
        ai_error = AIProcessingError("AI error", "mistral", "analysis")
        assert ai_error.model == "mistral"
        assert ai_error.operation == "analysis"
    
    def test_error_context_manager(self):
        """Test error context manager"""
        from utils.error_handler import ErrorContext
        
        with ErrorContext({'operation': 'test'}) as ctx:
            assert ctx.context['operation'] == 'test'
    
    def test_error_decorator(self):
        """Test error handling decorator"""
        from utils.error_handler import handle_errors
        
        @handle_errors
        def test_function():
            raise LeadFinderError("Test error")
        
        # Should not raise exception, should return error dict
        result = test_function()
        assert isinstance(result, dict)
        assert 'error' in result

if __name__ == "__main__":
    pytest.main([__file__]) 