#!/usr/bin/env python3
"""
Configuration Migration Script for LeadFinder

This script helps migrate existing configurations to the new hierarchical
configuration system. It will:

1. Detect existing configurations from environment files and database
2. Validate the new configuration system
3. Provide a summary of what needs to be configured
4. Optionally migrate existing values

Usage:
    python migrate_config.py [--migrate] [--validate-only]
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title: str):
    """Print a formatted section"""
    print(f"\n--- {title} ---")

def load_old_environment_config() -> Dict[str, str]:
    """Load configuration from old environment files"""
    config = {}
    base_dir = Path(__file__).parent
    
    # Check for environment files
    env_files = ['env.development', 'env.production', 'env.testing', 'env.example']
    
    for env_file in env_files:
        env_path = base_dir / env_file
        if env_path.exists():
            print_section(f"Found environment file: {env_file}")
            
            with open(env_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        try:
                            key, value = line.split('=', 1)
                            config[key] = value
                            print(f"  {key} = {value[:20]}{'...' if len(value) > 20 else ''}")
                        except ValueError:
                            print(f"  Warning: Invalid line {line_num}: {line}")
    
    return config

def check_database_config() -> Dict[str, str]:
    """Check for existing database configurations"""
    config = {}
    
    try:
        # Try to import the old config manager
        sys.path.insert(0, str(Path(__file__).parent))
        from models.config import ConfigManager
        
        cm = ConfigManager()
        db_configs = cm.get_all_configs(include_secrets=True)
        
        if db_configs:
            print_section("Found database configurations")
            for key, config_info in db_configs.items():
                value = config_info.get('value', '')
                config[key] = value
                print(f"  {key} = {value[:20]}{'...' if len(value) > 20 else ''}")
        
    except ImportError:
        print_section("Database configuration not available")
    except Exception as e:
        print_section(f"Error reading database configuration: {e}")
    
    return config

def validate_new_config_system() -> bool:
    """Validate the new configuration system"""
    try:
        from config import config, CONFIG_DEFINITIONS, validate_startup_config
        
        print_section("New Configuration System Validation")
        
        # Check if all required configs are defined
        required_configs = [key for key, info in CONFIG_DEFINITIONS.items() if info.get('required', False)]
        print(f"✅ Required configurations defined: {len(required_configs)}")
        
        # Check current configuration status
        missing_configs = config.validate_required_configs()
        if missing_configs:
            print(f"❌ Missing required configurations: {len(missing_configs)}")
            for missing in missing_configs:
                print(f"   - {missing}")
        else:
            print("✅ All required configurations are present")
        
        return len(missing_configs) == 0
        
    except ImportError as e:
        print(f"❌ New configuration system not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def analyze_migration_needs(old_env_config: Dict[str, str], old_db_config: Dict[str, str]) -> Dict[str, Any]:
    """Analyze what needs to be migrated"""
    analysis = {
        'env_configs': old_env_config,
        'db_configs': old_db_config,
        'missing_required': [],
        'can_migrate': [],
        'conflicts': [],
        'recommendations': []
    }
    
    try:
        from config import CONFIG_DEFINITIONS, config
        
        # Check for missing required configurations
        missing_configs = config.validate_required_configs()
        analysis['missing_required'] = missing_configs
        
        # Check what can be migrated
        for key in CONFIG_DEFINITIONS.keys():
            current_value = config.get(key)
            
            # Check if we have a value in old configs
            env_value = old_env_config.get(key)
            db_value = old_db_config.get(key)
            
            if not current_value and (env_value or db_value):
                analysis['can_migrate'].append({
                    'key': key,
                    'env_value': env_value,
                    'db_value': db_value,
                    'recommended_value': env_value or db_value
                })
            
            # Check for conflicts
            if env_value and db_value and env_value != db_value:
                analysis['conflicts'].append({
                    'key': key,
                    'env_value': env_value,
                    'db_value': db_value
                })
        
        # Generate recommendations
        if analysis['missing_required']:
            analysis['recommendations'].append(
                "Set required environment variables before starting the application"
            )
        
        if analysis['can_migrate']:
            analysis['recommendations'].append(
                "Run with --migrate to automatically migrate existing configurations"
            )
        
        if analysis['conflicts']:
            analysis['recommendations'].append(
                "Resolve configuration conflicts between environment and database values"
            )
        
    except ImportError:
        analysis['recommendations'].append("New configuration system not available")
    
    return analysis

def perform_migration(analysis: Dict[str, Any]) -> bool:
    """Perform the actual migration"""
    if not analysis['can_migrate']:
        print("No configurations to migrate")
        return True
    
    try:
        from config import config
        
        print_section("Migrating Configurations")
        
        migrated_count = 0
        for migration in analysis['can_migrate']:
            key = migration['key']
            value = migration['recommended_value']
            
            try:
                success = config.set(key, value, f"Migrated from old config", False)
                if success:
                    print(f"✅ Migrated {key}")
                    migrated_count += 1
                else:
                    print(f"❌ Failed to migrate {key}")
            except Exception as e:
                print(f"❌ Error migrating {key}: {e}")
        
        print(f"\nMigration complete: {migrated_count}/{len(analysis['can_migrate'])} configurations migrated")
        return migrated_count == len(analysis['can_migrate'])
        
    except ImportError as e:
        print(f"❌ Cannot perform migration: {e}")
        return False

def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LeadFinder Configuration Migration')
    parser.add_argument('--migrate', action='store_true', help='Perform migration')
    parser.add_argument('--validate-only', action='store_true', help='Only validate, do not migrate')
    
    args = parser.parse_args()
    
    print_header("LeadFinder Configuration Migration")
    
    # Step 1: Load old configurations
    print_section("Step 1: Loading Existing Configurations")
    old_env_config = load_old_environment_config()
    old_db_config = check_database_config()
    
    print(f"\nFound {len(old_env_config)} environment configurations")
    print(f"Found {len(old_db_config)} database configurations")
    
    # Step 2: Validate new system
    print_section("Step 2: Validating New Configuration System")
    new_system_valid = validate_new_config_system()
    
    # Step 3: Analyze migration needs
    print_section("Step 3: Analyzing Migration Needs")
    analysis = analyze_migration_needs(old_env_config, old_db_config)
    
    # Display analysis results
    if analysis['missing_required']:
        print(f"\n❌ Missing Required Configurations ({len(analysis['missing_required'])}):")
        for missing in analysis['missing_required']:
            print(f"   - {missing}")
    
    if analysis['can_migrate']:
        print(f"\n🔄 Configurations Available for Migration ({len(analysis['can_migrate'])}):")
        for migration in analysis['can_migrate']:
            print(f"   - {migration['key']}: {migration['recommended_value'][:30]}{'...' if len(migration['recommended_value']) > 30 else ''}")
    
    if analysis['conflicts']:
        print(f"\n⚠️  Configuration Conflicts ({len(analysis['conflicts'])}):")
        for conflict in analysis['conflicts']:
            print(f"   - {conflict['key']}:")
            print(f"     Environment: {conflict['env_value']}")
            print(f"     Database: {conflict['db_value']}")
    
    # Step 4: Display recommendations
    if analysis['recommendations']:
        print_section("Recommendations")
        for i, recommendation in enumerate(analysis['recommendations'], 1):
            print(f"{i}. {recommendation}")
    
    # Step 5: Perform migration if requested
    if args.migrate and not args.validate_only:
        print_section("Step 4: Performing Migration")
        if analysis['can_migrate']:
            success = perform_migration(analysis)
            if success:
                print("\n✅ Migration completed successfully!")
            else:
                print("\n❌ Migration completed with errors")
        else:
            print("No configurations to migrate")
    
    # Final status
    print_section("Migration Summary")
    if new_system_valid:
        print("✅ New configuration system is valid")
    else:
        print("❌ New configuration system has issues")
    
    if analysis['missing_required']:
        print(f"❌ {len(analysis['missing_required'])} required configurations missing")
    else:
        print("✅ All required configurations are present")
    
    if args.migrate and analysis['can_migrate']:
        print(f"🔄 {len(analysis['can_migrate'])} configurations were available for migration")
    
    print("\nMigration analysis complete!")

if __name__ == '__main__':
    main() 