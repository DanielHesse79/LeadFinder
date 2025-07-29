#!/usr/bin/env python3
"""
LeadFinder Deployment Script

This script handles comprehensive deployment of the LeadFinder application:
- Environment setup and validation
- Database initialization and optimization
- Service configuration and startup
- Health checks and monitoring
- Performance optimization
- Documentation generation
"""

import os
import sys
import subprocess
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from utils.logger import get_logger
    logger = get_logger('deploy')
except ImportError:
    logger = None

try:
    from utils.redis_cache import get_redis_cache_manager
    from models.database_indexes import create_standard_indexes, optimize_database_performance
    from utils.async_service import get_async_manager
    from utils.rate_limiter import configure_rate_limits
    from utils.analytics import get_analytics_tracker
    from utils.api_docs import generate_api_docs
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")

class LeadFinderDeployer:
    """
    Comprehensive deployment manager for LeadFinder
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.deployment_status = {
            'started_at': time.time(),
            'steps_completed': [],
            'errors': [],
            'warnings': []
        }
        
    def log_step(self, step: str, status: str = "completed"):
        """Log deployment step"""
        self.deployment_status['steps_completed'].append({
            'step': step,
            'status': status,
            'timestamp': time.time()
        })
        
        if logger:
            logger.info(f"Deployment step: {step} - {status}")
        else:
            print(f"✅ {step} - {status}")
    
    def log_error(self, step: str, error: str):
        """Log deployment error"""
        self.deployment_status['errors'].append({
            'step': step,
            'error': error,
            'timestamp': time.time()
        })
        
        if logger:
            logger.error(f"Deployment error in {step}: {error}")
        else:
            print(f"❌ {step} - Error: {error}")
    
    def log_warning(self, step: str, warning: str):
        """Log deployment warning"""
        self.deployment_status['warnings'].append({
            'step': step,
            'warning': warning,
            'timestamp': time.time()
        })
        
        if logger:
            logger.warning(f"Deployment warning in {step}: {warning}")
        else:
            print(f"⚠️ {step} - Warning: {warning}")
    
    def check_environment(self) -> bool:
        """Check and validate environment"""
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                self.log_error("Environment Check", "Python 3.8+ required")
                return False
            
            # Check required files
            required_files = [
                'app.py',
                'config.py',
                'requirements.txt'
            ]
            
            for file_path in required_files:
                if not Path(file_path).exists():
                    self.log_error("Environment Check", f"Required file missing: {file_path}")
                    return False
            
            # Check environment variables
            env_vars = ['FLASK_ENV', 'DATABASE_URL']
            missing_vars = [var for var in env_vars if not os.getenv(var)]
            
            if missing_vars:
                self.log_warning("Environment Check", f"Missing environment variables: {missing_vars}")
            
            self.log_step("Environment Check")
            return True
            
        except Exception as e:
            self.log_error("Environment Check", str(e))
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        try:
            print("📦 Installing dependencies...")
            
            # Install requirements
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log_error("Dependencies", f"Failed to install requirements: {result.stderr}")
                return False
            
            self.log_step("Dependencies Installation")
            return True
            
        except Exception as e:
            self.log_error("Dependencies", str(e))
            return False
    
    def setup_database(self) -> bool:
        """Setup and optimize database"""
        try:
            print("🗄️ Setting up database...")
            
            # Import database modules
            try:
                from models.database import DatabaseConnection
                from models.database_indexes import create_standard_indexes, optimize_database_performance
            except ImportError as e:
                self.log_error("Database Setup", f"Database modules not available: {e}")
                return False
            
            # Initialize database
            db = DatabaseConnection()
            
            # Create standard indexes
            indexes_created = create_standard_indexes()
            print(f"📊 Created {indexes_created} database indexes")
            
            # Optimize database performance
            optimization_results = optimize_database_performance()
            print(f"⚡ Database optimization completed: {optimization_results}")
            
            self.log_step("Database Setup")
            return True
            
        except Exception as e:
            self.log_error("Database Setup", str(e))
            return False
    
    def setup_redis(self) -> bool:
        """Setup Redis cache"""
        try:
            print("🔴 Setting up Redis cache...")
            
            # Test Redis connection
            redis_cache = get_redis_cache_manager()
            health_status = redis_cache.get_health_status()
            
            if health_status['is_healthy']:
                print("✅ Redis cache is healthy")
            else:
                self.log_warning("Redis Setup", "Redis not available, using fallback cache")
            
            self.log_step("Redis Setup")
            return True
            
        except Exception as e:
            self.log_warning("Redis Setup", f"Redis setup failed: {e}")
            return True  # Continue with fallback
    
    def setup_services(self) -> bool:
        """Setup and initialize services"""
        try:
            print("🔧 Setting up services...")
            
            # Initialize async service manager
            async_manager = get_async_manager()
            print("✅ Async service manager initialized")
            
            # Configure rate limiting
            configure_rate_limits()
            print("✅ Rate limiting configured")
            
            # Initialize analytics tracker
            analytics_tracker = get_analytics_tracker()
            print("✅ Analytics tracker initialized")
            
            self.log_step("Services Setup")
            return True
            
        except Exception as e:
            self.log_error("Services Setup", str(e))
            return False
    
    def generate_documentation(self) -> bool:
        """Generate API documentation"""
        try:
            print("📚 Generating documentation...")
            
            # Import Flask app
            try:
                from app import app
            except ImportError:
                self.log_warning("Documentation", "Flask app not available for documentation generation")
                return True
            
            # Generate documentation
            generator = generate_api_docs(app, "docs")
            
            # Get API summary
            summary = get_api_summary(app)
            print(f"📖 Generated documentation for {summary['total_routes']} routes")
            
            self.log_step("Documentation Generation")
            return True
            
        except Exception as e:
            self.log_warning("Documentation", f"Documentation generation failed: {e}")
            return True  # Continue without documentation
    
    def run_tests(self) -> bool:
        """Run test suite"""
        try:
            print("🧪 Running tests...")
            
            # Run pytest
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log_warning("Tests", f"Some tests failed: {result.stdout}")
                print(result.stdout)
                print(result.stderr)
            else:
                print("✅ All tests passed")
            
            self.log_step("Test Execution")
            return True
            
        except Exception as e:
            self.log_error("Tests", str(e))
            return False
    
    def health_check(self) -> bool:
        """Perform health checks"""
        try:
            print("🏥 Performing health checks...")
            
            checks = []
            
            # Check database
            try:
                from models.database import DatabaseConnection
                db = DatabaseConnection()
                checks.append(("Database", True))
            except Exception as e:
                checks.append(("Database", False, str(e)))
            
            # Check Redis
            try:
                redis_cache = get_redis_cache_manager()
                health = redis_cache.get_health_status()
                checks.append(("Redis", health['is_healthy']))
            except Exception as e:
                checks.append(("Redis", False, str(e)))
            
            # Check async services
            try:
                async_manager = get_async_manager()
                checks.append(("Async Services", async_manager.running))
            except Exception as e:
                checks.append(("Async Services", False, str(e)))
            
            # Report results
            all_healthy = True
            for check_name, is_healthy, *extra in checks:
                status = "✅" if is_healthy else "❌"
                print(f"{status} {check_name}")
                if not is_healthy and extra:
                    print(f"   Error: {extra[0]}")
                all_healthy = all_healthy and is_healthy
            
            if all_healthy:
                self.log_step("Health Checks")
            else:
                self.log_warning("Health Checks", "Some services are not healthy")
            
            return all_healthy
            
        except Exception as e:
            self.log_error("Health Checks", str(e))
            return False
    
    def performance_optimization(self) -> bool:
        """Perform performance optimizations"""
        try:
            print("⚡ Optimizing performance...")
            
            # Database optimization
            try:
                from models.database_indexes import optimize_database_performance
                results = optimize_database_performance()
                print(f"📊 Database optimization: {results}")
            except Exception as e:
                self.log_warning("Performance", f"Database optimization failed: {e}")
            
            # Cache optimization
            try:
                redis_cache = get_redis_cache_manager()
                stats = redis_cache.get_stats()
                print(f"🔴 Cache stats: {stats['hit_rate']}% hit rate")
            except Exception as e:
                self.log_warning("Performance", f"Cache optimization failed: {e}")
            
            self.log_step("Performance Optimization")
            return True
            
        except Exception as e:
            self.log_error("Performance Optimization", str(e))
            return False
    
    def start_application(self) -> bool:
        """Start the application"""
        try:
            print("🚀 Starting LeadFinder application...")
            
            # Check if app.py exists
            if not Path("app.py").exists():
                self.log_error("Application Start", "app.py not found")
                return False
            
            # Start the application
            print("✅ Application is ready to start")
            print("   Run: python app.py")
            print("   Or: flask run")
            
            self.log_step("Application Start")
            return True
            
        except Exception as e:
            self.log_error("Application Start", str(e))
            return False
    
    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment report"""
        duration = time.time() - self.deployment_status['started_at']
        
        report = {
            'deployment_time': duration,
            'steps_completed': len(self.deployment_status['steps_completed']),
            'errors': len(self.deployment_status['errors']),
            'warnings': len(self.deployment_status['warnings']),
            'status': 'success' if not self.deployment_status['errors'] else 'failed',
            'details': self.deployment_status
        }
        
        return report
    
    def deploy(self, skip_tests: bool = False, skip_docs: bool = False) -> bool:
        """
        Perform complete deployment
        
        Args:
            skip_tests: Skip test execution
            skip_docs: Skip documentation generation
            
        Returns:
            True if deployment successful, False otherwise
        """
        print("🚀 Starting LeadFinder deployment...")
        print("=" * 50)
        
        steps = [
            ("Environment Check", self.check_environment),
            ("Dependencies Installation", self.install_dependencies),
            ("Database Setup", self.setup_database),
            ("Redis Setup", self.setup_redis),
            ("Services Setup", self.setup_services),
        ]
        
        if not skip_docs:
            steps.append(("Documentation Generation", self.generate_documentation))
        
        if not skip_tests:
            steps.append(("Test Execution", self.run_tests))
        
        steps.extend([
            ("Health Checks", self.health_check),
            ("Performance Optimization", self.performance_optimization),
            ("Application Start", self.start_application),
        ])
        
        success = True
        for step_name, step_func in steps:
            try:
                if not step_func():
                    success = False
                    break
            except Exception as e:
                self.log_error(step_name, str(e))
                success = False
                break
        
        # Generate final report
        report = self.generate_deployment_report()
        
        print("\n" + "=" * 50)
        print("📊 Deployment Report")
        print("=" * 50)
        print(f"Status: {'✅ Success' if success else '❌ Failed'}")
        print(f"Duration: {report['deployment_time']:.2f} seconds")
        print(f"Steps completed: {report['steps_completed']}")
        print(f"Errors: {report['errors']}")
        print(f"Warnings: {report['warnings']}")
        
        if report['errors']:
            print("\n❌ Errors:")
            for error in report['details']['errors']:
                print(f"  - {error['step']}: {error['error']}")
        
        if report['warnings']:
            print("\n⚠️ Warnings:")
            for warning in report['details']['warnings']:
                print(f"  - {warning['step']}: {warning['warning']}")
        
        return success

def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(description="LeadFinder Deployment Script")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test execution")
    parser.add_argument("--skip-docs", action="store_true", help="Skip documentation generation")
    parser.add_argument("--config", type=str, help="Path to deployment configuration file")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Create deployer and run deployment
    deployer = LeadFinderDeployer(config)
    success = deployer.deploy(skip_tests=args.skip_tests, skip_docs=args.skip_docs)
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print("LeadFinder is ready to use.")
    else:
        print("\n💥 Deployment failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 