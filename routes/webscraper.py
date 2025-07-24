"""
WebScraper Routes for LeadFinder

This module provides web scraping endpoints for scientific information
that can be integrated with General Search and Lead Workshop.
"""

from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

# Import services
try:
    from services.webscraper_service import webscraper_service
except ImportError:
    webscraper_service = None

try:
    from services.langchain_analyzer import langchain_analyzer
except ImportError:
    langchain_analyzer = None

try:
    from models.database import db
except ImportError:
    db = None

try:
    from utils.logger import get_logger
    logger = get_logger('webscraper_routes')
except ImportError:
    logger = None

webscraper_bp = Blueprint('webscraper', __name__)

@webscraper_bp.route('/webscraper')
def webscraper_home():
    """WebScraper home page"""
    # Get service status
    webscraper_status = webscraper_service.get_status() if webscraper_service else {}
    langchain_status = langchain_analyzer.get_status() if langchain_analyzer else {}
    
    return render_template('webscraper.html',
                         webscraper_status=webscraper_status,
                         langchain_status=langchain_status)

@webscraper_bp.route('/webscraper/scrape', methods=['POST'])
def scrape_urls():
    """Scrape multiple URLs and analyze content"""
    try:
        # Get form data
        urls_text = request.form.get('urls', '').strip()
        content_type = request.form.get('content_type', 'scientific_paper')
        research_context = request.form.get('research_context', '').strip()
        use_ai_analysis = request.form.get('use_ai_analysis') == 'on'
        
        if not urls_text:
            return jsonify({
                'success': False,
                'error': 'URLs are required'
            }), 400
        
        # Parse URLs
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if not urls:
            return jsonify({
                'success': False,
                'error': 'No valid URLs provided'
            }), 400
        
        if logger:
            logger.info(f"Scraping {len(urls)} URLs with content type: {content_type}")
        
        # Check if webscraper service is available
        if not webscraper_service or not webscraper_service.is_available():
            return jsonify({
                'success': False,
                'error': 'WebScraper service not available'
            }), 500
        
        # Run scraping asynchronously
        try:
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Initialize webscraper if needed
            if not webscraper_service._initialized:
                init_success = loop.run_until_complete(webscraper_service.initialize())
                if not init_success:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to initialize WebScraper browser'
                    }), 500
            
            # Run scraping
            scraping_results = loop.run_until_complete(
                webscraper_service.scrape_multiple_urls(urls, [content_type] * len(urls))
            )
        except Exception as e:
            if logger:
                logger.error(f"Scraping error: {e}")
            return jsonify({
                'success': False,
                'error': f'Scraping failed: {str(e)}'
            }), 500
        
        # Process results
        processed_results = []
        for result in scraping_results:
            if result.success and result.content:
                processed_result = {
                    'url': result.content.url,
                    'title': result.content.title,
                    'content': result.content.content[:1000],  # Limit content length
                    'metadata': result.content.metadata,
                    'processing_time': result.processing_time,
                    'source_type': result.content.source_type
                }
                
                # Add AI analysis if requested
                if use_ai_analysis and langchain_analyzer and langchain_analyzer.is_available():
                    try:
                        if content_type == 'scientific_paper':
                            analysis = langchain_analyzer.analyze_scientific_paper(
                                result.content.content,
                                result.content.url,
                                research_context
                            )
                        elif content_type == 'research_profile':
                            analysis = langchain_analyzer.analyze_research_profile(
                                result.content.content,
                                result.content.url,
                                research_context
                            )
                        elif content_type == 'institution':
                            analysis = langchain_analyzer.analyze_institution(
                                result.content.content,
                                result.content.url,
                                research_context
                            )
                        else:
                            analysis = langchain_analyzer.analyze_scientific_paper(
                                result.content.content,
                                result.content.url,
                                research_context
                            )
                        
                        if analysis.success:
                            processed_result['ai_analysis'] = {
                                'summary': analysis.summary,
                                'insights': analysis.insights,
                                'structured_data': analysis.structured_data.dict() if analysis.structured_data else None,
                                'processing_time': analysis.processing_time,
                                'model_used': analysis.model_used
                            }
                        else:
                            processed_result['ai_analysis'] = {
                                'error': analysis.error,
                                'summary': 'AI analysis failed'
                            }
                    except Exception as e:
                        if logger:
                            logger.error(f"AI analysis failed for {result.content.url}: {e}")
                        processed_result['ai_analysis'] = {
                            'error': str(e),
                            'summary': 'AI analysis failed'
                        }
                else:
                    processed_result['ai_analysis'] = {
                        'summary': 'AI analysis not requested or not available'
                    }
                
                processed_results.append(processed_result)
            else:
                processed_results.append({
                    'url': result.source_url,
                    'error': result.error,
                    'success': False
                })
        
        # Save to database if available
        saved_count = 0
        if db:
            for result in processed_results:
                if result.get('success', True) and 'title' in result:
                    try:
                        # Create lead description
                        description = result.get('content', '')
                        if result.get('ai_analysis', {}).get('summary'):
                            description = f"AI Summary: {result['ai_analysis']['summary']}\n\nContent: {description}"
                        
                        success = db.save_lead(
                            result['title'],
                            description,
                            result['url'],
                            f"WebScraper: {content_type}",
                            source='webscraper'
                        )
                        if success:
                            saved_count += 1
                    except Exception as e:
                        if logger:
                            logger.error(f"Failed to save scraped content: {e}")
        
        return jsonify({
            'success': True,
            'results': processed_results,
            'total_urls': len(urls),
            'successful_scrapes': len([r for r in scraping_results if r.success]),
            'saved_to_db': saved_count,
            'content_type': content_type
        })
        
    except Exception as e:
        if logger:
            logger.error(f"WebScraper error: {e}")
        
        return jsonify({
            'success': False,
            'error': f'Scraping failed: {str(e)}'
        }), 500

@webscraper_bp.route('/webscraper/analyze', methods=['POST'])
def analyze_scraped_content():
    """Analyze already scraped content with LangChain"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        url = data.get('url', '')
        content_type = data.get('content_type', 'scientific_paper')
        research_context = data.get('research_context', '')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        if not langchain_analyzer or not langchain_analyzer.is_available():
            return jsonify({
                'success': False,
                'error': 'LangChain analyzer not available'
            }), 500
        
        # Analyze content
        if content_type == 'scientific_paper':
            analysis = langchain_analyzer.analyze_scientific_paper(
                content, url, research_context
            )
        elif content_type == 'research_profile':
            analysis = langchain_analyzer.analyze_research_profile(
                content, url, research_context
            )
        elif content_type == 'institution':
            analysis = langchain_analyzer.analyze_institution(
                content, url, research_context
            )
        else:
            analysis = langchain_analyzer.analyze_scientific_paper(
                content, url, research_context
            )
        
        if analysis.success:
            return jsonify({
                'success': True,
                'analysis': {
                    'summary': analysis.summary,
                    'insights': analysis.insights,
                    'structured_data': analysis.structured_data.dict() if analysis.structured_data else None,
                    'processing_time': analysis.processing_time,
                    'model_used': analysis.model_used
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': analysis.error
            }), 500
            
    except Exception as e:
        if logger:
            logger.error(f"Content analysis error: {e}")
        
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@webscraper_bp.route('/webscraper/status')
def get_status():
    """Get WebScraper and LangChain status"""
    webscraper_status = webscraper_service.get_status() if webscraper_service else {}
    langchain_status = langchain_analyzer.get_status() if langchain_analyzer else {}
    
    return jsonify({
        'webscraper': webscraper_status,
        'langchain': langchain_status,
        'overall_available': (
            webscraper_service and webscraper_service.is_available() and
            langchain_analyzer and langchain_analyzer.is_available()
        )
    })

@webscraper_bp.route('/webscraper/test')
def test_scraping():
    """Test scraping with a sample URL"""
    try:
        test_url = "https://example.com"
        
        if not webscraper_service or not webscraper_service.is_available():
            return jsonify({
                'success': False,
                'error': 'WebScraper service not available'
            }), 500
        
        # Run test scraping
        try:
            # Create new event loop for async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize webscraper if needed
            if not webscraper_service._initialized:
                init_success = loop.run_until_complete(webscraper_service.initialize())
                if not init_success:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to initialize WebScraper browser'
                    }), 500
            
            # Run test scraping
            result = loop.run_until_complete(
                webscraper_service.scrape_url(test_url, "general")
            )
        except Exception as e:
            if logger:
                logger.error(f"Test scraping error: {e}")
            return jsonify({
                'success': False,
                'error': f'Test failed: {str(e)}'
            }), 500
        finally:
            try:
                loop.close()
            except:
                pass
        
        if result.success:
            return jsonify({
                'success': True,
                'message': 'WebScraper test successful',
                'test_url': test_url,
                'processing_time': result.processing_time
            })
        else:
            return jsonify({
                'success': False,
                'error': result.error,
                'test_url': test_url
            }), 500
            
    except Exception as e:
        if logger:
            logger.error(f"WebScraper test error: {e}")
        
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        }), 500

@webscraper_bp.route('/webscraper/batch', methods=['POST'])
def batch_scraping():
    """Batch scraping with progress tracking"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        content_types = data.get('content_types', [])
        research_context = data.get('research_context', '')
        use_ai_analysis = data.get('use_ai_analysis', True)
        
        if not urls:
            return jsonify({
                'success': False,
                'error': 'URLs are required'
            }), 400
        
        # Ensure we have content types for all URLs
        if len(content_types) != len(urls):
            content_types = content_types + ['scientific_paper'] * (len(urls) - len(content_types))
        
        if logger:
            logger.info(f"Batch scraping {len(urls)} URLs")
        
        # Check services
        if not webscraper_service or not webscraper_service.is_available():
            return jsonify({
                'success': False,
                'error': 'WebScraper service not available'
            }), 500
        
        # Run batch scraping
        try:
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Initialize webscraper if needed
            if not webscraper_service._initialized:
                init_success = loop.run_until_complete(webscraper_service.initialize())
                if not init_success:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to initialize WebScraper browser'
                    }), 500
        
            # Run batch scraping
            scraping_results = loop.run_until_complete(
                webscraper_service.scrape_multiple_urls(urls, content_types)
            )
        except Exception as e:
            if logger:
                logger.error(f"Batch scraping error: {e}")
            return jsonify({
                'success': False,
                'error': f'Batch scraping failed: {str(e)}'
            }), 500
        
        # Process results
        processed_results = []
        for i, result in enumerate(scraping_results):
            if result.success and result.content:
                processed_result = {
                    'index': i,
                    'url': result.content.url,
                    'title': result.content.title,
                    'content_length': len(result.content.content),
                    'processing_time': result.processing_time,
                    'content_type': content_types[i] if i < len(content_types) else 'scientific_paper'
                }
                
                # Add AI analysis if requested
                if use_ai_analysis and langchain_analyzer and langchain_analyzer.is_available():
                    try:
                        content_type = content_types[i] if i < len(content_types) else 'scientific_paper'
                        
                        if content_type == 'scientific_paper':
                            analysis = langchain_analyzer.analyze_scientific_paper(
                                result.content.content,
                                result.content.url,
                                research_context
                            )
                        elif content_type == 'research_profile':
                            analysis = langchain_analyzer.analyze_research_profile(
                                result.content.content,
                                result.content.url,
                                research_context
                            )
                        elif content_type == 'institution':
                            analysis = langchain_analyzer.analyze_institution(
                                result.content.content,
                                result.content.url,
                                research_context
                            )
                        else:
                            analysis = langchain_analyzer.analyze_scientific_paper(
                                result.content.content,
                                result.content.url,
                                research_context
                            )
                        
                        if analysis.success:
                            processed_result['ai_analysis'] = {
                                'summary': analysis.summary,
                                'insights': analysis.insights,
                                'relevance_score': analysis.structured_data.relevance_score if analysis.structured_data else 3,
                                'processing_time': analysis.processing_time
                            }
                        else:
                            processed_result['ai_analysis'] = {
                                'error': analysis.error
                            }
                    except Exception as e:
                        processed_result['ai_analysis'] = {
                            'error': str(e)
                        }
                
                processed_results.append(processed_result)
            else:
                processed_results.append({
                    'index': i,
                    'url': result.source_url,
                    'error': result.error,
                    'success': False
                })
        
        return jsonify({
            'success': True,
            'results': processed_results,
            'total_urls': len(urls),
            'successful_scrapes': len([r for r in scraping_results if r.success]),
            'content_types': content_types
        })
        
    except Exception as e:
        if logger:
            logger.error(f"Batch scraping error: {e}")
        
        return jsonify({
            'success': False,
            'error': f'Batch scraping failed: {str(e)}'
        }), 500 