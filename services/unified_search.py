"""
Unified Search Service for LeadFinder

This service combines standard search and AutoGPT research functionality
into a single, efficient service with caching and unified data handling.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Import existing services
try:
    from services.serp_service import serp_service
except ImportError:
    serp_service = None

try:
    from autogpt_client import LocalAutoGPTClient, AutoGPTConfig
except ImportError:
    LocalAutoGPTClient = None
    AutoGPTConfig = None

try:
    from models.database import db
except ImportError:
    db = None

try:
    from utils.logger import get_logger
    logger = get_logger('unified_search')
except ImportError:
    logger = None


class SearchCache:
    """Simple in-memory cache for search results"""
    
    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if not expired"""
        if key in self.cache:
            timestamp = self.timestamps.get(key)
            if timestamp and datetime.now() - timestamp < timedelta(hours=self.ttl_hours):
                return self.cache[key]
            else:
                # Remove expired entry
                self._remove(key)
        return None
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Cache a result"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
            self._remove(oldest_key)
        
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
    
    def _remove(self, key: str) -> None:
        """Remove entry from cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        self.timestamps.clear()


class UnifiedSearchService:
    """
    Unified search service that combines standard search and AutoGPT research
    """
    
    def __init__(self):
        self.serp_service = serp_service
        self.cache = SearchCache()
        
        # Initialize AutoGPT client if available
        if LocalAutoGPTClient and AutoGPTConfig:
            try:
                config = AutoGPTConfig(
                    model="mistral:latest",
                    timeout=1800,  # 30 minutes for comprehensive research
                    base_url="http://localhost:11434"
                )
                self.autogpt_client = LocalAutoGPTClient(config)
                self.autogpt_available = True
                if logger:
                    logger.info("AutoGPT client initialized successfully")
            except Exception as e:
                self.autogpt_client = None
                self.autogpt_available = False
                if logger:
                    logger.warning(f"AutoGPT client initialization failed: {e}")
        else:
            self.autogpt_client = None
            self.autogpt_available = False
    
    def search(self, query: str, mode: str = 'quick', **kwargs) -> Dict[str, Any]:
        """
        Unified search method
        
        Args:
            query: Search query
            mode: 'quick' for standard search, 'research' for comprehensive research
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with search results and metadata
        """
        if mode == 'quick':
            return self.quick_search(query, **kwargs)
        elif mode == 'research':
            return self.comprehensive_research(query, **kwargs)
        else:
            return {
                'success': False,
                'error': f'Unknown search mode: {mode}'
            }
    
    def quick_search(self, query: str, engines: List[str] = None, 
                    use_ai_analysis: bool = False, max_results: int = 10,
                    research_question: str = None) -> Dict[str, Any]:
        """
        Quick search with optional AI analysis
        
        Args:
            query: Search query
            engines: List of search engines to use
            use_ai_analysis: Whether to use AI analysis
            max_results: Maximum number of results
            research_question: Research question for AI analysis
            
        Returns:
            Dictionary with search results
        """
        if not self.serp_service:
            return {
                'success': False,
                'error': 'Search service not available'
            }
        
        if engines is None:
            engines = ['google']
        
        # Check cache first
        cache_key = f"quick_{query}_{','.join(engines)}_{max_results}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            if logger:
                logger.info(f"Using cached result for query: {query}")
            return cached_result
        
        try:
            if logger:
                logger.info(f"Quick search: {query} with engines {engines}")
            
            # Perform search
            search_results = self.serp_service.search(query, engines, num_results=max_results)
            
            if not search_results:
                return {
                    'success': False,
                    'error': 'No results found'
                }
            
            # Convert to leads format
            leads = []
            for result in search_results:
                lead = {
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'link': result.get('link', ''),
                    'source': 'serp'
                }
                
                # Add AI analysis if requested
                if use_ai_analysis and self.autogpt_available:
                    try:
                        ai_summary = self._analyze_lead_with_ai(lead, research_question or query)
                        lead['ai_summary'] = ai_summary
                    except Exception as e:
                        if logger:
                            logger.warning(f"AI analysis failed for lead: {e}")
                        lead['ai_summary'] = "AI analysis failed"
                else:
                    lead['ai_summary'] = "Manual review required"
                
                leads.append(lead)
            
            # Save to database
            saved_count = 0
            if db:
                for lead in leads:
                    try:
                        success = db.save_lead(
                            lead['title'],
                            lead['snippet'],
                            lead['link'],
                            lead.get('ai_summary', ''),
                            source=lead['source']
                        )
                        if success:
                            saved_count += 1
                    except Exception as e:
                        if logger:
                            logger.error(f"Failed to save lead: {e}")
                        continue
            
            # Save search history
            if db:
                engines_str = ','.join(engines)
                db.save_search_history(query, research_question or 'quick search', engines_str, saved_count)
            
            result = {
                'success': True,
                'mode': 'quick',
                'query': query,
                'leads': leads,
                'total_results': len(leads),
                'saved_count': saved_count,
                'metadata': {
                    'engines_used': engines,
                    'ai_analysis': use_ai_analysis,
                    'cache_hit': False
                }
            }
            
            # Cache the result
            self.cache.set(cache_key, result)
            
            return result
            
        except Exception as e:
            if logger:
                logger.error(f"Quick search failed: {e}")
            return {
                'success': False,
                'error': f'Search failed: {str(e)}'
            }
    
    def comprehensive_research(self, company_name: str, industry: str) -> Dict[str, Any]:
        """
        Comprehensive lead research using AutoGPT
        
        Args:
            company_name: Name of the company doing research
            industry: Target industry for research
            
        Returns:
            Dictionary with comprehensive research results
        """
        if not self.autogpt_available or not self.autogpt_client:
            return {
                'success': False,
                'error': 'AutoGPT not available for comprehensive research'
            }
        
        # Check cache first
        cache_key = f"research_{company_name}_{industry}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            if logger:
                logger.info(f"Using cached research result for {company_name} in {industry}")
            return cached_result
        
        try:
            if logger:
                logger.info(f"Starting comprehensive research for {company_name} in {industry}")
            
            # Perform comprehensive research
            research_result = self.autogpt_client.execute_comprehensive_lead_research(company_name, industry)
            
            if research_result.get('status') != 'COMPLETED':
                return {
                    'success': False,
                    'error': research_result.get('error', 'Research failed')
                }
            
            # Extract results
            research_output = research_result.get('output', '')
            
            # Save research results to database if available
            saved_count = 0
            if db:
                try:
                    # Save as a special research entry
                    success = db.save_lead(
                        f"Research: {company_name} in {industry}",
                        f"Comprehensive lead research completed",
                        f"research://{company_name}/{industry}",
                        research_output,
                        source="autogpt_research"
                    )
                    if success:
                        saved_count += 1
                except Exception as e:
                    if logger:
                        logger.error(f"Failed to save research result: {e}")
            
            result = {
                'success': True,
                'mode': 'research',
                'company_name': company_name,
                'industry': industry,
                'research_output': research_output,
                'saved_count': saved_count,
                'metadata': {
                    'research_time': research_result.get('research_time'),
                    'web_results_count': research_result.get('web_results_count', 0),
                    'companies_identified': research_result.get('companies_identified', 0),
                    'steps_completed': research_result.get('steps_completed', 0),
                    'cache_hit': False
                }
            }
            
            # Cache the result
            self.cache.set(cache_key, result)
            
            return result
            
        except Exception as e:
            if logger:
                logger.error(f"Comprehensive research failed: {e}")
            return {
                'success': False,
                'error': f'Research failed: {str(e)}'
            }
    
    def _analyze_lead_with_ai(self, lead: Dict[str, Any], research_question: str) -> str:
        """
        Analyze a single lead with AI
        
        Args:
            lead: Lead data to analyze
            research_question: Research question for context
            
        Returns:
            AI analysis summary
        """
        if not self.autogpt_available:
            return "AI analysis not available"
        
        try:
            prompt = f"""
            Analyze this lead for relevance to: {research_question}
            
            Lead Information:
            Title: {lead.get('title', 'N/A')}
            Description: {lead.get('snippet', 'N/A')}
            URL: {lead.get('link', 'N/A')}
            
            Please provide:
            1. Relevance score (1-10)
            2. Key insights
            3. Potential opportunities
            4. Recommended next steps
            
            Keep the analysis concise and actionable.
            """
            
            result = self.autogpt_client.execute_text_generation(prompt, timeout=60)
            if result.get('status') == 'COMPLETED':
                return result.get('output', 'AI analysis completed')
            else:
                return f"AI analysis failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            if logger:
                logger.error(f"AI analysis failed: {e}")
            return f"AI analysis failed: {str(e)}"
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.cache.cache),
            'max_size': self.cache.max_size,
            'ttl_hours': self.cache.ttl_hours
        }
    
    def clear_cache(self) -> None:
        """Clear the search cache"""
        self.cache.clear()
        if logger:
            logger.info("Search cache cleared")
    
    def is_autogpt_available(self) -> bool:
        """Check if AutoGPT is available"""
        return self.autogpt_available


# Global instance
unified_search_service = UnifiedSearchService() 