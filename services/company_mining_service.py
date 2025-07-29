"""
Company Mining Service

This service integrates with our data mining capabilities to provide
comprehensive company profiling and intelligence gathering.
"""

from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime

try:
    from services.serpapi_service import serpapi_service
except ImportError:
    serpapi_service = None

try:
    from services.semantic_scholar_service import semantic_scholar_service
except ImportError:
    semantic_scholar_service = None

try:
    from services.nih_service import nih_service
except ImportError:
    nih_service = None

try:
    from services.orcid_service import orcid_service
except ImportError:
    orcid_service = None

try:
    from utils.logger import get_logger
    logger = get_logger('company_mining_service')
except ImportError:
    logger = None

class CompanyMiningService:
    """Service for mining comprehensive company data from multiple sources"""
    
    def __init__(self):
        self.serpapi_service = serpapi_service
        self.semantic_scholar_service = semantic_scholar_service
        self.nih_service = nih_service
        self.orcid_service = orcid_service
    
    def mine_company_data(self, company_name: str) -> Dict[str, Any]:
        """
        Mine comprehensive company data from multiple sources
        
        Args:
            company_name: Name of the company to analyze
            
        Returns:
            Dictionary containing comprehensive company data
        """
        try:
            if logger:
                logger.info(f"Starting comprehensive data mining for company: {company_name}")
            
            # Phase 1: Basic company information
            basic_info = self._search_company_web(company_name)
            
            # Phase 2: News and social media analysis
            news_data = self._analyze_company_news(company_name)
            
            # Phase 3: Financial data collection
            financial_data = self._gather_financial_data(company_name)
            
            # Phase 4: Patent and IP analysis
            patent_data = self._analyze_patents(company_name)
            
            # Phase 5: Industry research
            industry_data = self._get_industry_research(basic_info.get('industry', ''))
            
            # Phase 6: Talent and expertise mapping
            talent_data = self._map_company_talent(company_name)
            
            return {
                'company_name': company_name,
                'basic_info': basic_info,
                'news_analysis': news_data,
                'financial_intelligence': financial_data,
                'ip_landscape': patent_data,
                'industry_research': industry_data,
                'talent_mapping': talent_data,
                'mining_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error mining company data for {company_name}: {e}")
            return {
                'company_name': company_name,
                'error': str(e),
                'mining_timestamp': datetime.now().isoformat()
            }
    
    def _search_company_web(self, company_name: str) -> Dict[str, Any]:
        """Search for basic company information on the web"""
        try:
            if not self.serpapi_service:
                return {'error': 'SerpAPI service not available'}
            
            # Search for company website and basic info
            search_query = f"{company_name} company website about us"
            web_results = self.serpapi_service.search_web_results(search_query, num_results=10)
            
            # Extract company information
            company_info = self._extract_company_info(web_results, company_name)
            
            return {
                'website': company_info.get('website'),
                'description': company_info.get('description'),
                'industry': company_info.get('industry'),
                'location': company_info.get('location'),
                'founded': company_info.get('founded'),
                'size': company_info.get('size'),
                'products': company_info.get('products', []),
                'services': company_info.get('services', []),
                'leadership': company_info.get('leadership', []),
                'web_results': web_results[:5]  # Top 5 results
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error searching company web: {e}")
            return {'error': str(e)}
    
    def _analyze_company_news(self, company_name: str) -> Dict[str, Any]:
        """Analyze company news and social media presence"""
        try:
            if not self.serpapi_service:
                return {'error': 'SerpAPI service not available'}
            
            # Search for recent news
            news_query = f"{company_name} news press release 2024 2025"
            news_results = self.serpapi_service.search_web_results(news_query, num_results=20)
            
            # Search for social media mentions
            social_query = f"{company_name} LinkedIn Twitter social media"
            social_results = self.serpapi_service.search_web_results(social_query, num_results=10)
            
            # Analyze sentiment and key topics
            news_analysis = self._analyze_news_sentiment(news_results)
            
            return {
                'recent_news': news_results[:10],
                'social_media_presence': social_results[:5],
                'sentiment_analysis': news_analysis.get('sentiment'),
                'key_topics': news_analysis.get('topics', []),
                'media_coverage': news_analysis.get('coverage', {}),
                'news_count': len(news_results)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error analyzing company news: {e}")
            return {'error': str(e)}
    
    def _gather_financial_data(self, company_name: str) -> Dict[str, Any]:
        """Gather financial intelligence data"""
        try:
            financial_data = {}
            
            # Search for funding information
            funding_query = f"{company_name} funding investment venture capital"
            funding_results = self.serpapi_service.search_web_results(funding_query, num_results=15)
            
            # Search for financial performance
            financial_query = f"{company_name} revenue profit financial performance"
            financial_results = self.serpapi_service.search_web_results(financial_query, num_results=10)
            
            # Extract funding information
            funding_info = self._extract_funding_info(funding_results)
            
            # Extract financial metrics
            financial_metrics = self._extract_financial_metrics(financial_results)
            
            return {
                'funding_history': funding_info,
                'financial_metrics': financial_metrics,
                'funding_sources': funding_results[:5],
                'financial_reports': financial_results[:5],
                'valuation_estimates': self._estimate_valuation(funding_info, financial_metrics)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error gathering financial data: {e}")
            return {'error': str(e)}
    
    def _analyze_patents(self, company_name: str) -> Dict[str, Any]:
        """Analyze company patent portfolio and IP landscape"""
        try:
            if not self.semantic_scholar_service:
                return {'error': 'Semantic Scholar service not available'}
            
            # Search for patents and IP
            patent_query = f"{company_name} patents intellectual property"
            patent_results = self.semantic_scholar_service.search_papers(patent_query, max_results=20)
            
            # Search for technology publications
            tech_query = f"{company_name} technology innovation research"
            tech_results = self.semantic_scholar_service.search_papers(tech_query, max_results=15)
            
            return {
                'patent_portfolio': patent_results[:10],
                'technology_publications': tech_results[:10],
                'ip_landscape': self._analyze_ip_landscape(patent_results),
                'technology_focus': self._analyze_technology_focus(tech_results),
                'innovation_indicators': self._calculate_innovation_indicators(patent_results, tech_results)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error analyzing patents: {e}")
            return {'error': str(e)}
    
    def _get_industry_research(self, industry: str) -> Dict[str, Any]:
        """Get industry research and market analysis"""
        try:
            if not industry:
                return {'error': 'No industry specified'}
            
            if not self.semantic_scholar_service:
                return {'error': 'Semantic Scholar service not available'}
            
            # Search for industry research papers
            research_query = f"{industry} market analysis industry trends 2024"
            research_results = self.semantic_scholar_service.search_papers(research_query, max_results=20)
            
            # Search for market reports
            market_query = f"{industry} market size growth projections"
            market_results = self.semantic_scholar_service.search_papers(market_query, max_results=15)
            
            return {
                'industry_research': research_results[:10],
                'market_analysis': market_results[:10],
                'industry_trends': self._extract_industry_trends(research_results),
                'market_size_data': self._extract_market_size_data(market_results),
                'growth_projections': self._extract_growth_projections(market_results)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error getting industry research: {e}")
            return {'error': str(e)}
    
    def _map_company_talent(self, company_name: str) -> Dict[str, Any]:
        """Map company talent and expertise"""
        try:
            talent_data = {}
            
            # Search for company employees on professional networks
            talent_query = f"{company_name} employees LinkedIn professionals"
            talent_results = self.serpapi_service.search_web_results(talent_query, num_results=10)
            
            # Search for company research and publications
            if self.semantic_scholar_service:
                research_query = f"{company_name} authors researchers"
                research_results = self.semantic_scholar_service.search_papers(research_query, max_results=15)
                talent_data['research_publications'] = research_results[:10]
            
            return {
                'professional_networks': talent_results[:5],
                'research_publications': talent_data.get('research_publications', []),
                'expertise_areas': self._extract_expertise_areas(talent_results),
                'key_personnel': self._extract_key_personnel(talent_results),
                'talent_indicators': self._calculate_talent_indicators(talent_results)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Error mapping company talent: {e}")
            return {'error': str(e)}
    
    def _extract_company_info(self, web_results: List[Dict], company_name: str) -> Dict[str, Any]:
        """Extract company information from web search results"""
        company_info = {}
        
        for result in web_results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            # Extract website
            if 'website' in title or 'website' in snippet:
                company_info['website'] = result.get('link')
            
            # Extract industry
            if 'industry' in snippet:
                industry_match = re.search(r'industry[:\s]+([^,\.]+)', snippet)
                if industry_match:
                    company_info['industry'] = industry_match.group(1).strip()
            
            # Extract location
            if 'location' in snippet or 'headquarters' in snippet:
                location_match = re.search(r'(headquarters|location|based)[:\s]+([^,\.]+)', snippet)
                if location_match:
                    company_info['location'] = location_match.group(2).strip()
            
            # Extract description
            if not company_info.get('description'):
                company_info['description'] = result.get('snippet', '')[:200]
        
        return company_info
    
    def _analyze_news_sentiment(self, news_results: List[Dict]) -> Dict[str, Any]:
        """Analyze news sentiment and extract key topics"""
        positive_keywords = ['growth', 'success', 'expansion', 'profit', 'innovation', 'award']
        negative_keywords = ['loss', 'decline', 'layoff', 'bankruptcy', 'failure', 'crisis']
        
        positive_count = 0
        negative_count = 0
        topics = []
        
        for result in news_results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            # Count sentiment keywords
            for keyword in positive_keywords:
                if keyword in title or keyword in snippet:
                    positive_count += 1
            
            for keyword in negative_keywords:
                if keyword in title or keyword in snippet:
                    negative_count += 1
            
            # Extract topics
            topic_keywords = ['funding', 'acquisition', 'partnership', 'product', 'technology', 'market']
            for keyword in topic_keywords:
                if keyword in title or keyword in snippet:
                    topics.append(keyword)
        
        sentiment = 'positive' if positive_count > negative_count else 'negative' if negative_count > positive_count else 'neutral'
        
        return {
            'sentiment': sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'topics': list(set(topics))
        }
    
    def _extract_funding_info(self, funding_results: List[Dict]) -> Dict[str, Any]:
        """Extract funding information from search results"""
        funding_info = {
            'total_funding': 0,
            'funding_rounds': [],
            'investors': [],
            'latest_round': None
        }
        
        for result in funding_results:
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            # Extract funding amounts
            amount_match = re.search(r'\$?(\d+(?:\.\d+)?)\s*(?:million|billion|k|m|b)', snippet)
            if amount_match:
                amount = float(amount_match.group(1))
                if 'million' in snippet or 'm' in snippet:
                    amount *= 1000000
                elif 'billion' in snippet or 'b' in snippet:
                    amount *= 1000000000
                elif 'k' in snippet:
                    amount *= 1000
                
                funding_info['total_funding'] += amount
                funding_info['funding_rounds'].append({
                    'amount': amount,
                    'date': 'Recent',
                    'source': result.get('title', 'Unknown')
                })
        
        return funding_info
    
    def _extract_financial_metrics(self, financial_results: List[Dict]) -> Dict[str, Any]:
        """Extract financial metrics from search results"""
        metrics = {
            'revenue': None,
            'profit': None,
            'growth_rate': None,
            'valuation': None
        }
        
        for result in financial_results:
            snippet = result.get('snippet', '').lower()
            
            # Extract revenue
            revenue_match = re.search(r'revenue[:\s]*\$?(\d+(?:\.\d+)?)\s*(?:million|billion)', snippet)
            if revenue_match:
                metrics['revenue'] = float(revenue_match.group(1))
            
            # Extract valuation
            valuation_match = re.search(r'valuation[:\s]*\$?(\d+(?:\.\d+)?)\s*(?:million|billion)', snippet)
            if valuation_match:
                metrics['valuation'] = float(valuation_match.group(1))
        
        return metrics
    
    def _estimate_valuation(self, funding_info: Dict, financial_metrics: Dict) -> Dict[str, Any]:
        """Estimate company valuation based on available data"""
        valuation = {}
        
        if financial_metrics.get('valuation'):
            valuation['estimated_valuation'] = financial_metrics['valuation']
        elif funding_info.get('total_funding'):
            # Rough estimate: valuation = 3-5x total funding
            valuation['estimated_valuation'] = funding_info['total_funding'] * 4
        
        return valuation
    
    def _analyze_ip_landscape(self, patent_results: List[Dict]) -> Dict[str, Any]:
        """Analyze intellectual property landscape"""
        return {
            'patent_count': len(patent_results),
            'technology_areas': self._extract_technology_areas(patent_results),
            'ip_strength': self._calculate_ip_strength(patent_results)
        }
    
    def _analyze_technology_focus(self, tech_results: List[Dict]) -> Dict[str, Any]:
        """Analyze company technology focus areas"""
        return {
            'technology_areas': self._extract_technology_areas(tech_results),
            'innovation_score': self._calculate_innovation_score(tech_results),
            'research_focus': self._extract_research_focus(tech_results)
        }
    
    def _calculate_innovation_indicators(self, patent_results: List[Dict], tech_results: List[Dict]) -> Dict[str, Any]:
        """Calculate innovation indicators"""
        return {
            'patent_activity': len(patent_results),
            'research_activity': len(tech_results),
            'innovation_score': (len(patent_results) + len(tech_results)) / 2,
            'technology_maturity': self._assess_technology_maturity(patent_results, tech_results)
        }
    
    def _extract_industry_trends(self, research_results: List[Dict]) -> List[str]:
        """Extract industry trends from research papers"""
        trends = []
        for result in research_results:
            title = result.get('title', '').lower()
            if any(keyword in title for keyword in ['trend', 'growth', 'emerging', 'future']):
                trends.append(result.get('title', ''))
        return trends[:5]
    
    def _extract_market_size_data(self, market_results: List[Dict]) -> Dict[str, Any]:
        """Extract market size data from research papers"""
        return {
            'market_size_estimates': [result.get('title', '') for result in market_results[:3]],
            'growth_projections': [result.get('title', '') for result in market_results[3:6]]
        }
    
    def _extract_growth_projections(self, market_results: List[Dict]) -> List[str]:
        """Extract growth projections from market research"""
        projections = []
        for result in market_results:
            title = result.get('title', '').lower()
            if any(keyword in title for keyword in ['growth', 'projection', 'forecast', 'cagr']):
                projections.append(result.get('title', ''))
        return projections[:5]
    
    def _extract_expertise_areas(self, talent_results: List[Dict]) -> List[str]:
        """Extract expertise areas from talent search results"""
        expertise_keywords = ['technology', 'engineering', 'research', 'development', 'innovation', 'data', 'ai', 'machine learning']
        expertise_areas = []
        
        for result in talent_results:
            snippet = result.get('snippet', '').lower()
            for keyword in expertise_keywords:
                if keyword in snippet and keyword not in expertise_areas:
                    expertise_areas.append(keyword)
        
        return expertise_areas
    
    def _extract_key_personnel(self, talent_results: List[Dict]) -> List[Dict]:
        """Extract key personnel information"""
        personnel = []
        for result in talent_results[:5]:
            personnel.append({
                'name': result.get('title', '').split('-')[0].strip(),
                'role': 'Professional',
                'source': result.get('link', '')
            })
        return personnel
    
    def _calculate_talent_indicators(self, talent_results: List[Dict]) -> Dict[str, Any]:
        """Calculate talent and expertise indicators"""
        return {
            'professional_network_size': len(talent_results),
            'expertise_diversity': len(self._extract_expertise_areas(talent_results)),
            'talent_quality_score': min(len(talent_results) / 10, 1.0)  # Normalized score
        }
    
    def _extract_technology_areas(self, results: List[Dict]) -> List[str]:
        """Extract technology areas from research results"""
        tech_areas = []
        for result in results:
            title = result.get('title', '').lower()
            if any(keyword in title for keyword in ['ai', 'machine learning', 'data', 'cloud', 'blockchain', 'iot']):
                tech_areas.append(result.get('title', ''))
        return tech_areas[:5]
    
    def _calculate_ip_strength(self, patent_results: List[Dict]) -> float:
        """Calculate IP strength score"""
        return min(len(patent_results) / 20, 1.0)  # Normalized score
    
    def _calculate_innovation_score(self, tech_results: List[Dict]) -> float:
        """Calculate innovation score"""
        return min(len(tech_results) / 15, 1.0)  # Normalized score
    
    def _extract_research_focus(self, tech_results: List[Dict]) -> List[str]:
        """Extract research focus areas"""
        focus_areas = []
        for result in tech_results:
            title = result.get('title', '').lower()
            if any(keyword in title for keyword in ['research', 'development', 'innovation', 'technology']):
                focus_areas.append(result.get('title', ''))
        return focus_areas[:5]
    
    def _assess_technology_maturity(self, patent_results: List[Dict], tech_results: List[Dict]) -> str:
        """Assess technology maturity level"""
        total_activity = len(patent_results) + len(tech_results)
        
        if total_activity > 30:
            return 'Advanced'
        elif total_activity > 15:
            return 'Developing'
        else:
            return 'Emerging'