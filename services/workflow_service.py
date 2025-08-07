"""
Unified Workflow Service

This module provides a lean, 3-phase data workflow system:
1. Data In - Collect and ingest data from various sources
2. Data Process - Analyze and transform the data with AI
3. Data Out - Generate reports and insights
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime

try:
    from models.database import db
except ImportError:
    db = None

try:
    from services.serp_service import serp_service
except ImportError:
    serp_service = None

try:
    from services.ollama_service import ollama_service
except ImportError:
    ollama_service = None

try:
    from services.research_service import research_service
except ImportError:
    research_service = None

try:
    from models.strategic_planning import get_strategic_db
except ImportError:
    get_strategic_db = None

try:
    from utils.logger import get_logger
    logger = get_logger('workflow_service')
except ImportError:
    logger = None

class DataInService:
    """Phase 1: Data collection and ingestion"""
    
    def __init__(self):
        self.sources = {
            'web_search': serp_service,
            'research_apis': research_service,
            'ollama': ollama_service
        }
    
    def quick_search(self, query: str, engines: List[str] = None) -> Dict[str, Any]:
        """Quick web search across multiple engines"""
        try:
            if not engines:
                engines = ['google', 'bing', 'duckduckgo']
            
            results = []
            for engine in engines:
                if serp_service:
                    engine_results = serp_service.search(query, engine=engine)
                    results.extend(engine_results.get('results', []))
            
            # Save to database
            if db:
                for result in results:
                    db.save_lead({
                        'title': result.get('title', ''),
                        'description': result.get('snippet', ''),
                        'link': result.get('link', ''),
                        'source': 'web_search',
                        'ai_summary': self._generate_ai_summary(result)
                    })
            
            return {
                'success': True,
                'results': results,
                'count': len(results),
                'query': query,
                'engines': engines
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Quick search error: {e}")
            return {'success': False, 'error': str(e)}
    
    def research_search(self, query: str, research_type: str) -> Dict[str, Any]:
        """Search research APIs (PubMed, ORCID, Funding)"""
        try:
            if not research_service:
                return {'success': False, 'error': 'Research service not available'}
            
            results = research_service.search(query, research_type)
            
            # Save to database
            if db and results.get('success'):
                for result in results.get('results', []):
                    db.save_lead({
                        'title': result.get('title', ''),
                        'description': result.get('description', ''),
                        'link': result.get('link', ''),
                        'source': f'research_{research_type}',
                        'ai_summary': self._generate_ai_summary(result)
                    })
            
            return results
            
        except Exception as e:
            if logger:
                logger.error(f"Research search error: {e}")
            return {'success': False, 'error': str(e)}
    
    def upload_documents(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upload and process documents"""
        try:
            processed_files = []
            
            for file_info in files:
                # Process different file types
                if file_info.get('type') == 'pdf':
                    content = self._extract_pdf_content(file_info)
                elif file_info.get('type') == 'text':
                    content = file_info.get('content', '')
                elif file_info.get('type') == 'csv':
                    content = self._parse_csv_content(file_info)
                else:
                    content = file_info.get('content', '')
                
                # Save to database
                if db:
                    db.save_lead({
                        'title': file_info.get('name', 'Uploaded Document'),
                        'description': content[:500] + '...' if len(content) > 500 else content,
                        'link': '',
                        'source': 'document_upload',
                        'ai_summary': self._generate_ai_summary({'content': content})
                    })
                
                processed_files.append({
                    'name': file_info.get('name'),
                    'type': file_info.get('type'),
                    'size': len(content),
                    'processed': True
                })
            
            return {
                'success': True,
                'files': processed_files,
                'count': len(processed_files)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Document upload error: {e}")
            return {'success': False, 'error': str(e)}
    
    def ai_research(self, topic: str, depth: str = 'medium') -> Dict[str, Any]:
        """AI-powered research using AutoGPT"""
        try:
            if not ollama_service:
                return {'success': False, 'error': 'AI service not available'}
            
            # Generate research prompt
            prompt = f"""
            Conduct comprehensive research on: {topic}
            
            Please provide:
            1. Key companies and organizations
            2. Important people and contacts
            3. Market trends and insights
            4. Opportunities and challenges
            5. Recommended next steps
            
            Research depth: {depth}
            """
            
            # Get AI research results
            research_results = ollama_service.generate_text(prompt)
            
            # Parse and structure results
            structured_results = self._parse_ai_research(research_results)
            
            # Save to database
            if db:
                for result in structured_results:
                    db.save_lead({
                        'title': result.get('title', ''),
                        'description': result.get('description', ''),
                        'link': result.get('link', ''),
                        'source': 'ai_research',
                        'ai_summary': result.get('summary', '')
                    })
            
            return {
                'success': True,
                'results': structured_results,
                'count': len(structured_results),
                'topic': topic,
                'depth': depth
            }
            
        except Exception as e:
            if logger:
                logger.error(f"AI research error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_ai_summary(self, result: Dict[str, Any]) -> str:
        """Generate AI summary for a result"""
        try:
            if not ollama_service:
                return ''
            
            content = f"{result.get('title', '')} {result.get('description', '')} {result.get('content', '')}"
            prompt = f"Summarize this content in 2-3 sentences: {content[:1000]}"
            
            return ollama_service.generate_text(prompt)
            
        except Exception as e:
            if logger:
                logger.error(f"AI summary generation error: {e}")
            return ''
    
    def _extract_pdf_content(self, file_info: Dict[str, Any]) -> str:
        """Extract text content from PDF"""
        # Placeholder - would implement PDF text extraction
        return file_info.get('content', '')
    
    def _parse_csv_content(self, file_info: Dict[str, Any]) -> str:
        """Parse CSV content into structured text"""
        # Placeholder - would implement CSV parsing
        return file_info.get('content', '')
    
    def _parse_ai_research(self, research_text: str) -> List[Dict[str, Any]]:
        """Parse AI research results into structured format"""
        # Placeholder - would implement intelligent parsing
        return [{
            'title': 'AI Research Result',
            'description': research_text[:200] + '...' if len(research_text) > 200 else research_text,
            'link': '',
            'summary': research_text
        }]

class DataProcessService:
    """Phase 2: Data analysis and processing"""
    
    def __init__(self):
        self.analysis_types = {
            'rag_analysis': self._rag_analysis,
            'lead_analysis': self._lead_analysis,
            'market_research': self._market_research,
            'strategic_planning': self._strategic_planning
        }
    
    def analyze_data(self, data_ids: List[int], analysis_type: str) -> Dict[str, Any]:
        """Analyze collected data"""
        try:
            if analysis_type not in self.analysis_types:
                return {'success': False, 'error': f'Unknown analysis type: {analysis_type}'}
            
            # Get data from database
            if not db:
                return {'success': False, 'error': 'Database not available'}
            
            data_items = []
            for data_id in data_ids:
                item = db.get_lead_by_id(data_id)
                if item:
                    data_items.append(item)
            
            # Perform analysis
            analysis_function = self.analysis_types[analysis_type]
            results = analysis_function(data_items)
            
            return {
                'success': True,
                'analysis_type': analysis_type,
                'results': results,
                'data_count': len(data_items)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Data analysis error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _rag_analysis(self, data_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """RAG analysis of collected data"""
        try:
            # Combine all data for context
            context = "\n\n".join([
                f"{item.get('title', '')}: {item.get('description', '')}"
                for item in data_items
            ])
            
            # Generate insights
            prompt = f"""
            Analyze this data and provide insights:
            
            {context}
            
            Please provide:
            1. Key themes and patterns
            2. Important opportunities
            3. Notable contacts and companies
            4. Market trends
            5. Recommended actions
            """
            
            if ollama_service:
                insights = ollama_service.generate_text(prompt)
            else:
                # Fallback analysis without AI
                insights = self._fallback_analysis(data_items, "RAG")
            
            return {
                'insights': insights,
                'data_count': len(data_items),
                'analysis_type': 'rag'
            }
            
        except Exception as e:
            if logger:
                logger.error(f"RAG analysis error: {e}")
            return {'error': str(e)}
    
    def _lead_analysis(self, data_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Lead analysis and scoring"""
        try:
            scored_leads = []
            
            for item in data_items:
                # Score each lead
                prompt = f"""
                Analyze this lead and provide a score (1-10) and insights:
                
                Title: {item.get('title', '')}
                Description: {item.get('description', '')}
                
                Please provide:
                1. Relevance score (1-10)
                2. Opportunity assessment
                3. Contact strategy
                4. Next steps
                """
                
                if ollama_service:
                    analysis = ollama_service.generate_text(prompt)
                else:
                    # Fallback analysis without AI
                    analysis = self._fallback_lead_analysis(item)
                
                scored_leads.append({
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'analysis': analysis,
                    'score': self._extract_score(analysis),
                    'recommendations': self._extract_recommendations(analysis)
                })
            
            return {
                'leads': scored_leads,
                'total_leads': len(scored_leads),
                'average_score': sum(lead['score'] for lead in scored_leads) / len(scored_leads) if scored_leads else 0
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Lead analysis error: {e}")
            return {'error': str(e)}
    
    def _market_research(self, data_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Market research analysis"""
        try:
            # Combine data for market analysis
            market_data = "\n\n".join([
                f"{item.get('title', '')}: {item.get('description', '')}"
                for item in data_items
            ])
            
            prompt = f"""
            Perform market research analysis on this data:
            
            {market_data}
            
            Please provide:
            1. Market trends and patterns
            2. Competitive landscape
            3. Market opportunities
            4. Risk factors
            5. Strategic recommendations
            """
            
            if ollama_service:
                market_analysis = ollama_service.generate_text(prompt)
            else:
                # Fallback analysis without AI
                market_analysis = self._fallback_analysis(data_items, "Market Research")
            
            return {
                'market_analysis': market_analysis,
                'data_count': len(data_items),
                'analysis_type': 'market_research'
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Market research error: {e}")
            return {'error': str(e)}
    
    def _strategic_planning(self, data_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Strategic planning analysis"""
        try:
            # Combine data for strategic analysis
            strategic_data = "\n\n".join([
                f"{item.get('title', '')}: {item.get('description', '')}"
                for item in data_items
            ])
            
            prompt = f"""
            Generate strategic planning insights from this data:
            
            {strategic_data}
            
            Please provide:
            1. Strategic objectives
            2. Key initiatives
            3. Resource requirements
            4. Timeline recommendations
            5. Success metrics
            """
            
            if ollama_service:
                strategic_plan = ollama_service.generate_text(prompt)
            else:
                # Fallback analysis without AI
                strategic_plan = self._fallback_analysis(data_items, "Strategic Planning")
            
            return {
                'strategic_plan': strategic_plan,
                'data_count': len(data_items),
                'analysis_type': 'strategic_planning'
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Strategic planning error: {e}")
            return {'error': str(e)}
    
    def _fallback_analysis(self, data_items: List[Dict[str, Any]], analysis_type: str) -> str:
        """Fallback analysis when AI service is not available"""
        try:
            # Simple text-based analysis
            titles = [item.get('title', '') for item in data_items]
            descriptions = [item.get('description', '') for item in data_items]
            sources = [item.get('source', '') for item in data_items]
            
            analysis = f"""
            {analysis_type} Results:
            
            Data Summary:
            - Total items analyzed: {len(data_items)}
            - Sources: {', '.join(set(sources))}
            
            Key Findings:
            - Analyzed {len(titles)} data items
            - Found {len(set(titles))} unique titles
            - Data from {len(set(sources))} different sources
            
            Recommendations:
            1. Review all {len(data_items)} items for relevance
            2. Focus on items from {', '.join(set(sources))} sources
            3. Consider manual review of top items
            4. Export results for further analysis
            
            Note: This is a basic analysis. For AI-powered insights, ensure Ollama service is available.
            """
            
            return analysis
            
        except Exception as e:
            return f"Error in fallback analysis: {str(e)}"
    
    def _fallback_lead_analysis(self, item: Dict[str, Any]) -> str:
        """Fallback lead analysis when AI service is not available"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            source = item.get('source', '')
            
            # Simple scoring based on content length and keywords
            score = 5  # Default score
            if len(title) > 20 and len(description) > 50:
                score += 2
            if any(keyword in title.lower() or keyword in description.lower() 
                   for keyword in ['research', 'study', 'analysis', 'report']):
                score += 1
            
            analysis = f"""
            Lead Analysis:
            
            Title: {title}
            Description: {description}
            Source: {source}
            
            Basic Score: {score}/10
            
            Assessment:
            - Content length: {'Good' if len(description) > 50 else 'Limited'}
            - Source quality: {source}
            - Relevance indicators: {'Present' if score > 5 else 'Limited'}
            
            Recommendations:
            1. Manual review recommended
            2. Consider follow-up research
            3. Validate source credibility
            
            Note: This is a basic analysis. For AI-powered insights, ensure Ollama service is available.
            """
            
            return analysis
            
        except Exception as e:
            return f"Error in lead analysis: {str(e)}"
    
    def _extract_score(self, analysis: str) -> int:
        """Extract numerical score from analysis text"""
        try:
            # Simple extraction - would use more sophisticated parsing
            if 'score' in analysis.lower():
                for line in analysis.split('\n'):
                    if 'score' in line.lower():
                        # Extract number from line
                        import re
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            return min(int(numbers[0]), 10)
            return 5  # Default score
        except:
            return 5
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract recommendations from analysis text"""
        try:
            recommendations = []
            lines = analysis.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'next step', 'action']):
                    recommendations.append(line.strip())
            return recommendations[:3]  # Top 3 recommendations
        except:
            return []

class DataOutService:
    """Phase 3: Report generation and output"""
    
    def __init__(self):
        self.report_types = {
            'lead_report': self._generate_lead_report,
            'market_report': self._generate_market_report,
            'strategic_report': self._generate_strategic_report,
            'action_items': self._generate_action_items
        }
    
    def generate_report(self, processed_data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate reports from processed data"""
        try:
            if report_type not in self.report_types:
                return {'success': False, 'error': f'Unknown report type: {report_type}'}
            
            report_function = self.report_types[report_type]
            report = report_function(processed_data)
            
            return {
                'success': True,
                'report_type': report_type,
                'report': report,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Report generation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_lead_report(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lead analysis report"""
        try:
            leads = processed_data.get('leads', [])
            
            report = {
                'title': 'Lead Analysis Report',
                'summary': f'Analysis of {len(leads)} leads',
                'top_leads': leads[:10],
                'statistics': {
                    'total_leads': len(leads),
                    'high_priority': len([l for l in leads if l.get('score', 0) >= 8]),
                    'medium_priority': len([l for l in leads if 5 <= l.get('score', 0) < 8]),
                    'low_priority': len([l for l in leads if l.get('score', 0) < 5])
                },
                'recommendations': self._extract_top_recommendations(leads)
            }
            
            return report
            
        except Exception as e:
            if logger:
                logger.error(f"Lead report generation error: {e}")
            return {'error': str(e)}
    
    def _generate_market_report(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market research report"""
        try:
            market_analysis = processed_data.get('market_analysis', '')
            
            report = {
                'title': 'Market Research Report',
                'analysis': market_analysis,
                'sections': [
                    'Market Size and Opportunities',
                    'Competitive Landscape',
                    'Industry Trends',
                    'Customer Insights',
                    'Market Entry Strategies'
                ]
            }
            
            return report
            
        except Exception as e:
            if logger:
                logger.error(f"Market report generation error: {e}")
            return {'error': str(e)}
    
    def _generate_strategic_report(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic planning report"""
        try:
            strategic_insights = processed_data.get('strategic_insights', '')
            
            report = {
                'title': 'Strategic Planning Report',
                'insights': strategic_insights,
                'sections': [
                    'SWOT Analysis',
                    'Competitive Positioning',
                    'Market Entry Strategy',
                    'Financial Projections',
                    'Implementation Plan'
                ]
            }
            
            return report
            
        except Exception as e:
            if logger:
                logger.error(f"Strategic report generation error: {e}")
            return {'error': str(e)}
    
    def _generate_action_items(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate action items from processed data"""
        try:
            action_items = []
            
            # Extract action items from various analysis types
            if 'leads' in processed_data:
                for lead in processed_data['leads'][:5]:  # Top 5 leads
                    recommendations = lead.get('recommendations', [])
                    for rec in recommendations:
                        action_items.append({
                            'type': 'lead_followup',
                            'priority': lead.get('score', 5),
                            'action': rec,
                            'lead': lead.get('title', '')
                        })
            
            # Sort by priority
            action_items.sort(key=lambda x: x.get('priority', 0), reverse=True)
            
            return {
                'title': 'Action Items',
                'items': action_items[:10],  # Top 10 action items
                'total_items': len(action_items)
            }
            
        except Exception as e:
            if logger:
                logger.error(f"Action items generation error: {e}")
            return {'error': str(e)}
    
    def _extract_top_recommendations(self, leads: List[Dict[str, Any]]) -> List[str]:
        """Extract top recommendations from leads"""
        try:
            all_recommendations = []
            for lead in leads:
                recommendations = lead.get('recommendations', [])
                all_recommendations.extend(recommendations)
            
            # Return unique recommendations
            return list(set(all_recommendations))[:5]
        except:
            return []

class DataWorkflow:
    """Unified data workflow manager"""
    
    def __init__(self):
        self.data_in = DataInService()
        self.data_process = DataProcessService()
        self.data_out = DataOutService()
        self.progress = {
            'data_in': {'status': 'pending', 'progress': 0},
            'data_process': {'status': 'pending', 'progress': 0},
            'data_out': {'status': 'pending', 'progress': 0}
        }
    
    def collect_data(self, source: str, query: str, **kwargs) -> Dict[str, Any]:
        """Phase 1: Collect data from various sources"""
        try:
            if source == 'web_search':
                result = self.data_in.quick_search(query, **kwargs)
            elif source == 'research_apis':
                result = self.data_in.research_search(query, **kwargs)
            elif source == 'document_upload':
                result = self.data_in.upload_documents(**kwargs)
            elif source == 'ai_research':
                result = self.data_in.ai_research(query, **kwargs)
            else:
                return {'success': False, 'error': f'Unknown source: {source}'}
            
            if result.get('success'):
                self.progress['data_in'] = {'status': 'completed', 'progress': 100}
            
            return result
            
        except Exception as e:
            if logger:
                logger.error(f"Data collection error: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_data(self, data_ids: List[int], analysis_type: str) -> Dict[str, Any]:
        """Phase 2: Process collected data"""
        try:
            result = self.data_process.analyze_data(data_ids, analysis_type)
            
            if result.get('success'):
                self.progress['data_process'] = {'status': 'completed', 'progress': 100}
            
            return result
            
        except Exception as e:
            if logger:
                logger.error(f"Data processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_output(self, processed_data: Dict[str, Any], output_type: str) -> Dict[str, Any]:
        """Phase 3: Generate reports and insights"""
        try:
            result = self.data_out.generate_report(processed_data, output_type)
            
            if result.get('success'):
                self.progress['data_out'] = {'status': 'completed', 'progress': 100}
            
            return result
            
        except Exception as e:
            if logger:
                logger.error(f"Output generation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current workflow progress"""
        return self.progress
    
    def reset_progress(self):
        """Reset workflow progress"""
        self.progress = {
            'data_in': {'status': 'pending', 'progress': 0},
            'data_process': {'status': 'pending', 'progress': 0},
            'data_out': {'status': 'pending', 'progress': 0}
        }

# Global workflow instance
_workflow = None

def get_workflow() -> DataWorkflow:
    """Get the global workflow instance"""
    global _workflow
    if _workflow is None:
        _workflow = DataWorkflow()
    return _workflow