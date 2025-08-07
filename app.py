"""
LeadFinder Main Application

This is the main Flask application entry point for LeadFinder.
It provides a web interface for lead discovery and management.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect
import os
import sys
from pathlib import Path

# Import the new configuration system
try:
    from config import config, validate_startup_config, ConfigurationError
except ImportError as e:
    print(f"❌ Configuration import failed: {e}")
    sys.exit(1)

# Import routes with error handling
try:
    from routes.dashboard import dashboard_bp
except ImportError:
    dashboard_bp = None

try:
    from routes.leads import leads_bp
except ImportError:
    leads_bp = None

try:
    from routes.search import search_bp
except ImportError:
    search_bp = None

try:
    from routes.config import config_bp
except ImportError:
    config_bp = None

try:
    from routes.ollama import ollama_bp
except ImportError:
    ollama_bp = None

try:
    from routes.workflow import workflow_bp
except ImportError:
    workflow_bp = None

try:
    from routes.unified_search import unified_search_bp
except ImportError:
    unified_search_bp = None

try:
    from routes.api_keys import api_keys_bp
except ImportError:
    api_keys_bp = None

try:
    from routes.research import research_bp
except ImportError:
    research_bp = None

try:
    from routes.lead_workshop import lead_workshop_bp
except ImportError:
    lead_workshop_bp = None

try:
    from routes.autogpt_control import autogpt_control_bp
except ImportError:
    autogpt_control_bp = None

try:
    from routes.rag_routes import rag_bp
except ImportError:
    rag_bp = None

try:
    from routes.reports import reports_bp
except ImportError:
    reports_bp = None

try:
    from routes.researchers import researchers_bp
except ImportError:
    researchers_bp = None

try:
    from routes.strategic_planning import strategic_bp
except ImportError:
    strategic_bp = None

try:
    from utils.logger import get_logger
    logger = get_logger('app')
except ImportError:
    logger = None

# Import error handling system
try:
    from utils.error_handler import register_flask_error_handlers, get_error_health_status
except ImportError:
    register_flask_error_handlers = None
    get_error_health_status = None

# Import cache manager
try:
    from utils.cache_manager import get_cache_health_status
except ImportError:
    get_cache_health_status = None

# Import unified search service
try:
    from services.unified_search_service import get_unified_search_health_status
except ImportError:
    get_unified_search_health_status = None

# Import health monitoring
try:
    from utils.health_monitor import get_comprehensive_health_status
except ImportError:
    get_comprehensive_health_status = None

# Import improvement systems
try:
    from utils.redis_cache import get_redis_cache_manager, get_redis_cache_health
except ImportError:
    get_redis_cache_manager = None
    get_redis_cache_health = None

try:
    from models.database_indexes import create_standard_indexes, get_database_performance_report
except ImportError:
    create_standard_indexes = None
    get_database_performance_report = None

try:
    from utils.async_service import get_async_manager, get_async_health_status
except ImportError:
    get_async_manager = None
    get_async_health_status = None

try:
    from utils.rate_limiter import get_rate_limiter, get_rate_limit_health
except ImportError:
    get_rate_limiter = None
    get_rate_limit_health = None

try:
    from utils.analytics import get_analytics_manager, get_analytics_health
except ImportError:
    get_analytics_manager = None
    get_analytics_health = None

try:
    from utils.api_docs import generate_api_documentation
except ImportError:
    generate_api_documentation = None

def create_app():
    """Create and configure the Flask application"""
    
    # Validate configuration before starting
    try:
        if not validate_startup_config():
            print("❌ Configuration validation failed. Please check your environment variables and database configuration.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        sys.exit(1)
    
    app = Flask(__name__)
    
    # Configure Flask
    app.config['SECRET_KEY'] = config.get('FLASK_SECRET_KEY', required=True)
    app.config['DEBUG'] = config.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)

    # Configure CSRF settings
    app.config['WTF_CSRF_TIME_LIMIT'] = 24 * 3600  # 24 hours instead of 1 hour
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow HTTP in development
    
    # Initialize database
    try:
        from models.database import db
        # Test database connection
        db.get_lead_count()
        if logger:
            logger.info("Database initialized successfully")
    except Exception as e:
        if logger:
            logger.error(f"Database initialization failed: {e}")
        print(f"⚠️  Database initialization failed: {e}")
    
    # Initialize improvement systems
    try:
        # Initialize Redis cache
        if get_redis_cache_manager:
            redis_cache = get_redis_cache_manager()
            if logger:
                logger.info("Redis cache initialized successfully")
            print("✅ Redis cache ready")
        else:
            print("⚠️  Redis cache not available")
    except Exception as e:
        if logger:
            logger.warning(f"Redis cache initialization failed: {e}")
        print(f"⚠️  Redis cache initialization failed: {e}")
    
    try:
        # Initialize database indexes
        if create_standard_indexes:
            indexes_created = create_standard_indexes()
            if logger:
                logger.info(f"Database indexes initialized: {indexes_created} indexes created")
            print(f"✅ Database indexes ready ({indexes_created} indexes)")
        else:
            print("⚠️  Database indexing not available")
    except Exception as e:
        if logger:
            logger.warning(f"Database indexing initialization failed: {e}")
        print(f"⚠️  Database indexing initialization failed: {e}")
    
    try:
        # Initialize async service manager
        if get_async_manager:
            async_manager = get_async_manager()
            if logger:
                logger.info("Async service manager initialized successfully")
            print("✅ Async service manager ready")
        else:
            print("⚠️  Async service manager not available")
    except Exception as e:
        if logger:
            logger.warning(f"Async service manager initialization failed: {e}")
        print(f"⚠️  Async service manager initialization failed: {e}")
    
    try:
        # Initialize rate limiter
        if get_rate_limiter:
            rate_limiter = get_rate_limiter()
            if logger:
                logger.info("Rate limiter initialized successfully")
            print("✅ Rate limiter ready")
        else:
            print("⚠️  Rate limiter not available")
    except Exception as e:
        if logger:
            logger.warning(f"Rate limiter initialization failed: {e}")
        print(f"⚠️  Rate limiter initialization failed: {e}")
    
    try:
        # Initialize analytics manager
        if get_analytics_manager:
            analytics_manager = get_analytics_manager()
            if logger:
                logger.info("Analytics manager initialized successfully")
            print("✅ Analytics manager ready")
        else:
            print("⚠️  Analytics manager not available")
    except Exception as e:
        if logger:
            logger.warning(f"Analytics manager initialization failed: {e}")
        print(f"⚠️  Analytics manager initialization failed: {e}")
    
    # Initialize AutoGPT integration (skip validation to avoid hanging)
    try:
        from leadfinder_autogpt_integration import LeadfinderAutoGPTIntegration
        autogpt_integration = LeadfinderAutoGPTIntegration("mistral:latest")
        # Skip connection test to avoid hanging
        if logger:
            logger.info("AutoGPT integration initialized (validation skipped)")
        print("✅ AutoGPT integration ready (validation skipped)")
    except Exception as e:
        if logger:
            logger.warning(f"AutoGPT integration not available: {e}")
        print(f"⚠️  AutoGPT integration not available: {e}")
    
    # Register blueprints
    if leads_bp:
        app.register_blueprint(leads_bp)
        if logger:
            logger.info("Leads blueprint registered")
    
    if search_bp:
        app.register_blueprint(search_bp)
        if logger:
            logger.info("Search blueprint registered")
    
    if ollama_bp:
        app.register_blueprint(ollama_bp, url_prefix='/ollama')
        if logger:
            logger.info("Ollama blueprint registered")
    
    if research_bp:
        app.register_blueprint(research_bp)
        if logger:
            logger.info("Research blueprint registered")
    
    if config_bp:
        app.register_blueprint(config_bp)
        if logger:
            logger.info("Config blueprint registered")
    
    if lead_workshop_bp:
        app.register_blueprint(lead_workshop_bp)
        if logger:
            logger.info("Lead Workshop blueprint registered")
    
    if unified_search_bp:
        app.register_blueprint(unified_search_bp)
        if logger:
            logger.info("Unified Search blueprint registered")
    
    if autogpt_control_bp:
        app.register_blueprint(autogpt_control_bp)
        if logger:
            logger.info("AutoGPT Control blueprint registered")
    
    if rag_bp:
        app.register_blueprint(rag_bp)
        if logger:
            logger.info("RAG blueprint registered")
    
    if dashboard_bp:
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        if logger:
            logger.info("Dashboard blueprint registered")
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    if reports_bp:
        app.register_blueprint(reports_bp, url_prefix='/reports')
        if logger:
            logger.info("Reports blueprint registered")
    
    if researchers_bp:
        app.register_blueprint(researchers_bp, url_prefix='/researchers')
        if logger:
            logger.info("Researchers blueprint registered")
    
    if strategic_bp:
        app.register_blueprint(strategic_bp)
        if logger:
            logger.info("Strategic Planning blueprint registered")
    
    if workflow_bp:
        app.register_blueprint(workflow_bp)
        if logger:
            logger.info("Workflow blueprint registered")
    
    if api_keys_bp:
        app.register_blueprint(api_keys_bp, url_prefix='/api_keys')
        if logger:
            logger.info("API Keys blueprint registered")
    
    # Add CSRF exemptions for API endpoints
    csrf.exempt(app.view_functions['rag.rag_search'])
    csrf.exempt(app.view_functions['rag.retrieve_context'])
    csrf.exempt(app.view_functions['rag.generate_with_context'])
    csrf.exempt(app.view_functions['rag.ingest_document'])
    
    # Add CSRF exemptions for workflow API endpoints
    try:
        csrf.exempt(app.view_functions['workflow.quick_search'])
        csrf.exempt(app.view_functions['workflow.research_search'])
        csrf.exempt(app.view_functions['workflow.upload_documents'])
        csrf.exempt(app.view_functions['workflow.ai_research'])
        csrf.exempt(app.view_functions['workflow.web_scraping'])
        csrf.exempt(app.view_functions['workflow.analyze_data'])
        csrf.exempt(app.view_functions['workflow.generate_report'])
        csrf.exempt(app.view_functions['workflow.reset_workflow'])
        csrf.exempt(app.view_functions['workflow.get_available_data'])
        csrf.exempt(app.view_functions['workflow.get_workflow_statistics'])
    except KeyError:
        # Some routes might not be registered yet, ignore errors
        pass
    
    # Add CSRF exemptions for strategic planning API endpoints
    try:
        csrf.exempt(app.view_functions['strategic.create_company_profile'])
        csrf.exempt(app.view_functions['strategic.conduct_market_research'])
        csrf.exempt(app.view_functions['strategic.conduct_swot_analysis'])
        csrf.exempt(app.view_functions['strategic.generate_strategic_plan'])
    except KeyError:
        pass  # Some routes might not exist yet
    
    # Add CSRF exemptions for search and researchers API endpoints
    try:
        csrf.exempt(app.view_functions['search.perform_search'])
        csrf.exempt(app.view_functions['search.perform_search_ajax'])
        csrf.exempt(app.view_functions['search.perform_search_api'])
        csrf.exempt(app.view_functions['search.analyze_lead'])
        csrf.exempt(app.view_functions['search.research_leads'])
        csrf.exempt(app.view_functions['researchers.search_researchers'])
        csrf.exempt(app.view_functions['researchers.researcher_profile'])
    except KeyError:
        pass  # Some routes might not exist yet
    
    # Add CSRF exemptions for lead workshop and other API endpoints
    try:
        csrf.exempt(app.view_functions['lead_workshop.analyze_leads'])
        csrf.exempt(app.view_functions['lead_workshop.get_analysis_status'])
        csrf.exempt(app.view_functions['ollama.ollama_models'])
        csrf.exempt(app.view_functions['ollama.download_model'])
        csrf.exempt(app.view_functions['ollama.delete_model'])
    except KeyError:
        pass  # Some routes might not exist yet
    
    # Register comprehensive error handlers
    if register_flask_error_handlers:
        register_flask_error_handlers(app)
    else:
        # Fallback error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('404.html'), 404
        
        @app.errorhandler(500)
        def internal_error(error):
            return render_template('500.html'), 500
        
        @app.errorhandler(ConfigurationError)
        def configuration_error(error):
            flash(f'Configuration error: {error}', 'error')
            return redirect(url_for('config.config_home'))
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Check database connection
            from models.database import db
            db.get_lead_count()
            
            # Check database connection pool
            db_pool_status = 'unavailable'
            db_pool_stats = {}
            try:
                from models.database_pool import get_db_pool
                pool = get_db_pool()
                db_pool_stats = pool.get_pool_stats()
                db_pool_status = 'ready'
            except Exception as e:
                db_pool_status = f'unavailable: {str(e)}'
            
            # Check configuration
            missing_configs = config.validate_required_configs()
            
            # Check AutoGPT integration (skip test to avoid hanging)
            autogpt_status = 'available (validation skipped)'
            
            # Check improvement systems
            redis_health = get_redis_cache_health() if get_redis_cache_health else {'status': 'unavailable'}
            db_performance = get_database_performance_report() if get_database_performance_report else {'status': 'unavailable'}
            async_health = get_async_health_status() if get_async_health_status else {'status': 'unavailable'}
            rate_limit_health = get_rate_limit_health() if get_rate_limit_health else {'status': 'unavailable'}
            analytics_health = get_analytics_health() if get_analytics_health else {'status': 'unavailable'}
            
            # Use comprehensive health monitoring if available
            if get_comprehensive_health_status:
                health_status = get_comprehensive_health_status()
                # Add improvement systems to comprehensive health
                health_status.update({
                    'improvements': {
                        'redis_cache': redis_health,
                        'database_performance': db_performance,
                        'async_services': async_health,
                        'rate_limiting': rate_limit_health,
                        'analytics': analytics_health
                    }
                })
                return jsonify(health_status)
            else:
                # Fallback to basic health checks
                error_health = get_error_health_status() if get_error_health_status else {'status': 'unavailable'}
                cache_health = get_cache_health_status() if get_cache_health_status else {'status': 'unavailable'}
                search_health = get_unified_search_health_status() if get_unified_search_health_status else {'status': 'unavailable'}
                
                return jsonify({
                    'status': 'healthy',
                    'database': 'connected',
                    'database_pool': db_pool_status,
                    'database_pool_stats': db_pool_stats,
                    'configuration': 'valid' if not missing_configs else 'missing_required',
                    'autogpt': autogpt_status,
                    'error_handling': error_health,
                    'cache': cache_health,
                    'search_services': search_health,
                    'improvements': {
                        'redis_cache': redis_health,
                        'database_performance': db_performance,
                        'async_services': async_health,
                        'rate_limiting': rate_limit_health,
                        'analytics': analytics_health
                    },
                    'missing_configs': missing_configs
                })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500
    
    # API documentation endpoint
    @app.route('/api/docs')
    def api_documentation():
        """Generate and return API documentation"""
        try:
            if generate_api_documentation:
                docs = generate_api_documentation(app)
                return jsonify(docs)
            else:
                return jsonify({
                    'error': 'API documentation generator not available',
                    'status': 'unavailable'
                }), 503
        except Exception as e:
            return jsonify({
                'error': f'Failed to generate API documentation: {str(e)}',
                'status': 'error'
            }), 500
    
    if logger:
        logger.info("Flask application created successfully")
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    host = config.get('FLASK_HOST', '0.0.0.0')
    port = int(config.get('FLASK_PORT', '5051'))
    debug = config.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting LeadFinder on {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    # Check AutoGPT status at startup (skip validation to avoid hanging)
    print("🤖 AutoGPT: Available (validation skipped)")
    
    app.run(host=host, port=port, debug=debug) 