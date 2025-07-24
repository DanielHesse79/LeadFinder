"""
Unified Search Service for LeadFinder

This service consolidates all search functionality into a single, comprehensive service:
- Web search (Google, Bing, DuckDuckGo)
- Research database search (PubMed, ORCID, Semantic Scholar)
- Funding database search (SweCRIS, CORDIS, NIH, NSF)
- AI-powered analysis and filtering
- Caching and performance optimization
"""

import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from utils.logger import get_logger
    logger = get_logger('unified_search')
except ImportError:
    logger = None

try:
    from utils.cache_manager import get_cache_manager, cached, CacheUtils
except ImportError:
    get_cache_manager = None
    cached = None
    CacheUtils = None

try:
    from utils.error_handler import handle_errors, APIServiceError, AIProcessingError
except ImportError:
    handle_errors = None
    APIServiceError = None
    AIProcessingError = None

# Import search services
try:
    from services.serp_service import serp_service
except ImportError:
    serp_service = None

try:
    from services.pubmed_service import pubmed_service
except ImportError:
    pubmed_service = None

try:
    from services.orcid_service import orcid_service
except ImportError:
    orcid_service = None

try:
    from services.semantic_scholar_service import semantic_scholar_service
except ImportError:
    semantic_scholar_service = None

try:
    from services.swecris_api import SweCRISAPI
except ImportError:
    SweCRISAPI = None

try:
    from services.cordis_api import CORDISAPI
except ImportError:
    CORDISAPI = None

try:
    from services.nih_api import NIHAPI
except ImportError:
    NIHAPI = None

try:
    from services.nsf_api import NSFAPI
except ImportError:
    NSFAPI = None

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

@dataclass
class SearchResult:
    """Standardized search result"""
    title: str
    description: str
    url: str
    source: str
    relevance_score: float = 0.0
    ai_analysis: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SearchQuery:
    """Search query with parameters"""
    query: str
    search_type: str  # 'web', 'research', 'funding', 'unified'
    engines: List[str] = None
    max_results: int = 10
    research_question: str = ""
    filters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.engines is None:
            self.engines = []
        if self.filters is None:
            self.filters = {}

class UnifiedSearchService:
    """
    Unified search service that consolidates all search functionality
    """
    
    def __init__(self):
        self.cache = get_cache_manager() if get_cache_manager else None
        self.available_services = self._initialize_services()
        
        if logger:
            logger.info(f"Unified search service initialized with {len(self.available_services)} services")
    
    def _initialize_services(self) -> Dict[str, Any]:
        """Initialize available search services"""
        services = {}
        
        # Web search services
        if serp_service:
            services['serp'] = serp_service
        
        # Research services
        if pubmed_service:
            services['pubmed'] = pubmed_service
        if orcid_service:
            services['orcid'] = orcid_service
        if semantic_scholar_service:
            services['semantic_scholar'] = semantic_scholar_service
        
        # Funding services
        if SweCRISAPI:
            services['swecris'] = SweCRISAPI()
        if CORDISAPI:
            services['cordis'] = CORDISAPI()
        if NIHAPI:
            services['nih'] = NIHAPI()
        if NSFAPI:
            services['nsf'] = NSFAPI()
        
        # AI service
        if ollama_service:
            services['ai'] = ollama_service
        
        return services
    
    def get_available_services(self) -> Dict[str, List[str]]:
        """Get list of available services by category"""
        categories = {
            'web_search': [],
            'research': [],
            'funding': [],
            'ai': []
        }
        
        if 'serp' in self.available_services:
            categories['web_search'].extend(['google', 'bing', 'duckduckgo'])
        
        if 'pubmed' in self.available_services:
            categories['research'].append('pubmed')
        if 'orcid' in self.available_services:
            categories['research'].append('orcid')
        if 'semantic_scholar' in self.available_services:
            categories['research'].append('semantic_scholar')
        
        if 'swecris' in self.available_services:
            categories['funding'].append('swecris')
        if 'cordis' in self.available_services:
            categories['funding'].append('cordis')
        if 'nih' in self.available_services:
            categories['funding'].append('nih')
        if 'nsf' in self.available_services:
            categories['funding'].append('nsf')
        
        if 'ai' in self.available_services:
            categories['ai'].append('ollama')
        
        return categories
    
    @handle_errors if handle_errors else lambda x: x
    def search(self, query: SearchQuery) -> Dict[str, Any]:
        """
        Perform unified search across all available services
        
        Args:
            query: SearchQuery object with search parameters
            
        Returns:
            Dictionary with search results and metadata
        """
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(query)
        
        # Check cache first
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                if logger:
                    logger.info(f"Cache hit for search query: {query.query}")
                return cached_result
        
        # Perform search based on type
        if query.search_type == 'web':
            results = self._web_search(query)
        elif query.search_type == 'research':
            results = self._research_search(query)
        elif query.search_type == 'funding':
            results = self._funding_search(query)
        elif query.search_type == 'unified':
            results = self._unified_search(query)
        else:
            raise ValueError(f"Unknown search type: {query.search_type}")
        
        # AI analysis if requested
        if query.research_question and 'ai' in self.available_services:
            results = self._analyze_results(results, query.research_question)
        
        # Prepare response
        response = {
            'success': True,
            'query': query.query,
            'search_type': query.search_type,
            'results': [self._result_to_dict(result) for result in results],
            'total_results': len(results),
            'search_time': round(time.time() - start_time, 2),
            'services_used': list(self.available_services.keys()),
            'timestamp': time.time()
        }
        
        # Cache the result
        if self.cache:
            self.cache.set(cache_key, response, ttl=300)  # Cache for 5 minutes
        
        return response
    
    def _web_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform web search using SERP API"""
        results = []
        
        if 'serp' not in self.available_services:
            return results
        
        try:
            # Use specified engines or default to Google
            engines = query.engines if query.engines else ['google']
            
            serp_results = self.available_services['serp'].search(
                query.query, 
                engines=engines, 
                num_results=query.max_results
            )
            
            for result in serp_results:
                search_result = SearchResult(
                    title=result.get('title', ''),
                    description=result.get('snippet', ''),
                    url=result.get('link', ''),
                    source='web_search',
                    metadata={
                        'engine': result.get('source', 'unknown'),
                        'position': result.get('position', 0)
                    }
                )
                results.append(search_result)
                
        except Exception as e:
            if logger:
                logger.error(f"Web search error: {e}")
            if APIServiceError:
                raise APIServiceError(f"Web search failed: {e}", "serp", "search")
        
        return results
    
    def _research_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform research database search"""
        results = []
        
        # Search PubMed
        if 'pubmed' in self.available_services:
            try:
                pubmed_results = self.available_services['pubmed'].search_articles(
                    query.query, max_results=query.max_results
                )
                
                for result in pubmed_results:
                    search_result = SearchResult(
                        title=result.get('title', ''),
                        description=result.get('abstract', ''),
                        url=result.get('url', ''),
                        source='pubmed',
                        metadata={
                            'authors': result.get('authors', []),
                            'journal': result.get('journal', ''),
                            'publication_date': result.get('publication_date', ''),
                            'pmid': result.get('pmid', '')
                        }
                    )
                    results.append(search_result)
                    
            except Exception as e:
                if logger:
                    logger.error(f"PubMed search error: {e}")
        
        # Search Semantic Scholar
        if 'semantic_scholar' in self.available_services:
            try:
                scholar_results = self.available_services['semantic_scholar'].search_papers(
                    query.query, max_results=query.max_results
                )
                
                for result in scholar_results:
                    search_result = SearchResult(
                        title=result.get('title', ''),
                        description=result.get('abstract', ''),
                        url=result.get('url', ''),
                        source='semantic_scholar',
                        metadata={
                            'authors': result.get('authors', []),
                            'year': result.get('year', ''),
                            'citations': result.get('citation_count', 0),
                            'paper_id': result.get('paper_id', '')
                        }
                    )
                    results.append(search_result)
                    
            except Exception as e:
                if logger:
                    logger.error(f"Semantic Scholar search error: {e}")
        
        return results
    
    def _funding_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform funding database search"""
        results = []
        
        # Search SweCRIS
        if 'swecris' in self.available_services:
            try:
                swecris_results = self.available_services['swecris'].search_projects(
                    query.query, max_results=query.max_results
                )
                
                for result in swecris_results:
                    search_result = SearchResult(
                        title=result.title,
                        description=result.description,
                        url=result.url,
                        source='swecris',
                        metadata={
                            'principal_investigator': result.principal_investigator,
                            'funding_amount': result.funding_amount,
                            'start_date': result.start_date,
                            'end_date': result.end_date,
                            'organization': result.organization
                        }
                    )
                    results.append(search_result)
                    
            except Exception as e:
                if logger:
                    logger.error(f"SweCRIS search error: {e}")
        
        # Search CORDIS
        if 'cordis' in self.available_services:
            try:
                cordis_results = self.available_services['cordis'].search_projects(
                    query.query, max_results=query.max_results
                )
                
                for result in cordis_results:
                    search_result = SearchResult(
                        title=result.title,
                        description=result.description,
                        url=result.url,
                        source='cordis',
                        metadata={
                            'coordinator': result.coordinator,
                            'funding_amount': result.funding_amount,
                            'start_date': result.start_date,
                            'end_date': result.end_date,
                            'programme': result.programme
                        }
                    )
                    results.append(search_result)
                    
            except Exception as e:
                if logger:
                    logger.error(f"CORDIS search error: {e}")
        
        return results
    
    def _unified_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform search across all available services"""
        all_results = []
        
        # Use ThreadPoolExecutor for concurrent searches
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            # Submit web search
            if 'serp' in self.available_services:
                futures.append(executor.submit(self._web_search, query))
            
            # Submit research search
            if any(service in self.available_services for service in ['pubmed', 'semantic_scholar']):
                futures.append(executor.submit(self._research_search, query))
            
            # Submit funding search
            if any(service in self.available_services for service in ['swecris', 'cordis', 'nih', 'nsf']):
                futures.append(executor.submit(self._funding_search, query))
            
            # Collect results
            for future in as_completed(futures):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    if logger:
                        logger.error(f"Search future error: {e}")
        
        return all_results
    
    def _analyze_results(self, results: List[SearchResult], research_question: str) -> List[SearchResult]:
        """Analyze search results using AI"""
        if 'ai' not in self.available_services:
            return results
        
        analyzed_results = []
        
        for result in results:
            try:
                # Create analysis prompt
                prompt = f"""
                Research Question: {research_question}
                
                Title: {result.title}
                Description: {result.description}
                Source: {result.source}
                
                Please analyze the relevance of this result to the research question and provide:
                1. A relevance score (0-1, where 1 is highly relevant)
                2. A brief analysis explaining why this result is relevant or not
                
                Format your response as:
                SCORE: [score]
                ANALYSIS: [analysis]
                """
                
                # Get AI analysis
                ai_response = self.available_services['ai']._call_ollama(prompt)
                
                if ai_response:
                    # Parse AI response
                    score = self._extract_score(ai_response)
                    analysis = self._extract_analysis(ai_response)
                    
                    result.relevance_score = score
                    result.ai_analysis = analysis
                
                analyzed_results.append(result)
                
            except Exception as e:
                if logger:
                    logger.error(f"AI analysis error for result {result.title}: {e}")
                analyzed_results.append(result)
        
        # Sort by relevance score
        analyzed_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return analyzed_results
    
    def _extract_score(self, ai_response: str) -> float:
        """Extract relevance score from AI response"""
        try:
            import re
            score_match = re.search(r'SCORE:\s*([0-9.]+)', ai_response, re.IGNORECASE)
            if score_match:
                score = float(score_match.group(1))
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
        except:
            pass
        return 0.5  # Default score
    
    def _extract_analysis(self, ai_response: str) -> str:
        """Extract analysis from AI response"""
        try:
            import re
            analysis_match = re.search(r'ANALYSIS:\s*(.+)', ai_response, re.IGNORECASE | re.DOTALL)
            if analysis_match:
                return analysis_match.group(1).strip()
        except:
            pass
        return "Analysis not available"
    
    def _generate_cache_key(self, query: SearchQuery) -> str:
        """Generate cache key for search query"""
        import hashlib
        import json
        
        key_data = {
            'query': query.query,
            'search_type': query.search_type,
            'engines': query.engines,
            'max_results': query.max_results,
            'research_question': query.research_question,
            'filters': query.filters
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"unified_search:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _result_to_dict(self, result: SearchResult) -> Dict[str, Any]:
        """Convert SearchResult to dictionary"""
        return {
            'title': result.title,
            'description': result.description,
            'url': result.url,
            'source': result.source,
            'relevance_score': result.relevance_score,
            'ai_analysis': result.ai_analysis,
            'metadata': result.metadata,
            'timestamp': result.timestamp
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all search services"""
        status = {}
        
        for service_name, service in self.available_services.items():
            try:
                if hasattr(service, 'check_status'):
                    status[service_name] = service.check_status()
                elif hasattr(service, 'get_status'):
                    status[service_name] = service.get_status()
                else:
                    status[service_name] = {'status': 'available'}
            except Exception as e:
                status[service_name] = {'status': 'error', 'error': str(e)}
        
        return status
    
    def clear_cache(self):
        """Clear search cache"""
        if self.cache:
            self.cache.invalidate_pattern("unified_search:")

# Global unified search service instance
_unified_search_service = None

def get_unified_search_service() -> UnifiedSearchService:
    """Get the global unified search service instance"""
    global _unified_search_service
    if _unified_search_service is None:
        _unified_search_service = UnifiedSearchService()
    return _unified_search_service

# Health check for unified search service
def get_unified_search_health_status() -> Dict[str, Any]:
    """Get unified search service health status"""
    try:
        service = get_unified_search_service()
        service_status = service.get_service_status()
        
        # Count available services
        available_count = sum(1 for status in service_status.values() 
                            if status.get('status') in ['available', 'ready'])
        total_count = len(service_status)
        
        # Determine health status
        if available_count == 0:
            status = 'critical'
        elif available_count < total_count * 0.5:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'available_services': available_count,
            'total_services': total_count,
            'service_status': service_status
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        } 