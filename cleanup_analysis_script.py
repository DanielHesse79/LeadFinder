#!/usr/bin/env python3
"""
LeadFinder Codebase Cleanup Analysis Script

This script analyzes the codebase to identify:
1. Unused functions (especially those replaced by RAG)
2. Duplicate services
3. Unused files
4. Functions that may be deprecated
"""

import os
import re
import ast
import glob
from typing import List, Dict, Set, Tuple
from pathlib import Path
import json

class CodebaseAnalyzer:
    """Analyzes the codebase for unused functions and files"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.python_files = []
        self.function_definitions = {}  # file -> [function_names]
        self.function_calls = {}        # file -> [function_calls]
        self.imports = {}               # file -> [imports]
        self.unused_functions = set()
        self.rag_replaced_functions = set()
        
    def scan_python_files(self):
        """Scan all Python files in the codebase, excluding venv"""
        # Exclude venv and other non-project directories
        exclude_dirs = {'venv', '__pycache__', '.git', '.pytest_cache'}
        
        self.python_files = []
        for file_path in self.root_dir.rglob("*.py"):
            # Skip files in excluded directories
            if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                continue
            self.python_files.append(file_path)
        
        print(f"Found {len(self.python_files)} Python files (excluding venv)")
        
    def extract_function_definitions(self, file_path: Path) -> List[str]:
        """Extract function definitions from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    functions.append(node.name)
            
            return functions
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def extract_function_calls(self, file_path: Path) -> List[str]:
        """Extract function calls from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            calls = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        calls.append(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        calls.append(node.func.attr)
            
            return calls
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def extract_imports(self, file_path: Path) -> List[str]:
        """Extract imports from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            return imports
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def analyze_codebase(self):
        """Analyze the entire codebase"""
        print("🔍 Analyzing codebase...")
        
        # Extract function definitions
        for file_path in self.python_files:
            relative_path = file_path.relative_to(self.root_dir)
            self.function_definitions[str(relative_path)] = self.extract_function_definitions(file_path)
            self.function_calls[str(relative_path)] = self.extract_function_calls(file_path)
            self.imports[str(relative_path)] = self.extract_imports(file_path)
        
        # Find unused functions
        self.find_unused_functions()
        
        # Find RAG-replaced functions
        self.find_rag_replaced_functions()
        
        # Find duplicate services
        self.find_duplicate_services()
    
    def find_unused_functions(self):
        """Find functions that are defined but never called"""
        all_definitions = set()
        all_calls = set()
        
        # Collect all function definitions
        for file_path, functions in self.function_definitions.items():
            for func in functions:
                all_definitions.add(func)
        
        # Collect all function calls
        for file_path, calls in self.function_calls.items():
            for call in calls:
                all_calls.add(call)
        
        # Find unused functions
        self.unused_functions = all_definitions - all_calls
        
        print(f"Found {len(self.unused_functions)} potentially unused functions")
    
    def find_rag_replaced_functions(self):
        """Find functions that may have been replaced by RAG"""
        rag_replaced_patterns = [
            'analyze_leads_with_ai',
            'batch_analyze_relevance', 
            'analyze_lead',
            'process_lead',
            'search_leads',
            'analyze_relevance',
            'simple_analysis',
            'basic_analysis'
        ]
        
        for pattern in rag_replaced_patterns:
            for file_path, functions in self.function_definitions.items():
                for func in functions:
                    if pattern.lower() in func.lower():
                        self.rag_replaced_functions.add(f"{file_path}:{func}")
        
        print(f"Found {len(self.rag_replaced_functions)} potentially RAG-replaced functions")
    
    def find_duplicate_services(self):
        """Find duplicate service implementations"""
        service_files = []
        
        for file_path in self.python_files:
            if 'service' in file_path.name.lower():
                service_files.append(file_path)
        
        print(f"Found {len(service_files)} service files")
        
        # Check for duplicate service names
        service_names = {}
        for file_path in service_files:
            name = file_path.stem
            if name in service_names:
                print(f"⚠️  Duplicate service: {name}")
                print(f"   - {service_names[name]}")
                print(f"   - {file_path}")
            else:
                service_names[name] = file_path
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive analysis report"""
        report = {
            'summary': {
                'total_files': len(self.python_files),
                'unused_functions': len(self.unused_functions),
                'rag_replaced_functions': len(self.rag_replaced_functions)
            },
            'unused_functions': list(self.unused_functions),
            'rag_replaced_functions': list(self.rag_replaced_functions),
            'duplicate_services': self.find_duplicate_services_detailed(),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def find_duplicate_services_detailed(self) -> List[Dict]:
        """Find detailed information about duplicate services"""
        duplicates = []
        
        # Check for UnifiedSearchService specifically
        unified_search_files = []
        for file_path in self.python_files:
            if 'unified_search' in file_path.name:
                unified_search_files.append(file_path)
        
        if len(unified_search_files) > 1:
            duplicates.append({
                'service_name': 'UnifiedSearchService',
                'files': [str(f) for f in unified_search_files],
                'priority': 'HIGH',
                'description': 'Multiple UnifiedSearchService implementations found'
            })
        
        return duplicates
    
    def generate_recommendations(self) -> List[str]:
        """Generate cleanup recommendations"""
        recommendations = []
        
        if self.unused_functions:
            recommendations.append(f"Review {len(self.unused_functions)} potentially unused functions")
        
        if self.rag_replaced_functions:
            recommendations.append(f"Audit {len(self.rag_replaced_functions)} potentially RAG-replaced functions")
        
        # Check for test files in root directory
        test_files = list(self.root_dir.glob("test_*.py"))
        if test_files:
            recommendations.append(f"Move {len(test_files)} test files to tests/ directory")
        
        # Check for large HTML files
        html_files = list(self.root_dir.glob("*.html"))
        large_html = [f for f in html_files if f.stat().st_size > 10000]  # > 10KB
        if large_html:
            recommendations.append(f"Review {len(large_html)} large HTML files for cleanup")
        
        return recommendations
    
    def print_report(self):
        """Print a formatted analysis report"""
        print("\n" + "="*60)
        print("🔍 LEADFINDER CODEBASE CLEANUP ANALYSIS")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"   Total Python files: {len(self.python_files)}")
        print(f"   Potentially unused functions: {len(self.unused_functions)}")
        print(f"   Potentially RAG-replaced functions: {len(self.rag_replaced_functions)}")
        
        if self.rag_replaced_functions:
            print(f"\n🔄 RAG-Replaced Functions:")
            for func in sorted(self.rag_replaced_functions):
                print(f"   - {func}")
        
        if self.unused_functions:
            print(f"\n🗑️  Potentially Unused Functions (top 20):")
            for func in sorted(list(self.unused_functions))[:20]:
                print(f"   - {func}")
        
        # Check for specific issues
        print(f"\n⚠️  Specific Issues:")
        
        # Check for duplicate services
        unified_search_files = [f for f in self.python_files if 'unified_search' in f.name]
        if len(unified_search_files) > 1:
            print(f"   - Duplicate UnifiedSearchService: {len(unified_search_files)} files")
            for f in unified_search_files:
                print(f"     * {f}")
        
        # Check for test files in root
        test_files = list(self.root_dir.glob("test_*.py"))
        if test_files:
            print(f"   - Test files in root directory: {len(test_files)} files")
            for f in test_files:
                print(f"     * {f}")
        
        # Check for large files (only project files)
        large_files = []
        for file_path in self.python_files:
            if file_path.stat().st_size > 50000:  # > 50KB
                large_files.append((file_path, file_path.stat().st_size))
        
        if large_files:
            print(f"   - Large Python files (>50KB): {len(large_files)} files")
            for file_path, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
                print(f"     * {file_path} ({size/1024:.1f}KB)")
        
        print(f"\n📋 Recommendations:")
        recommendations = self.generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "="*60)

def main():
    """Main analysis function"""
    analyzer = CodebaseAnalyzer()
    
    print("🚀 Starting LeadFinder codebase analysis...")
    
    # Scan files
    analyzer.scan_python_files()
    
    # Analyze codebase
    analyzer.analyze_codebase()
    
    # Generate and print report
    analyzer.print_report()
    
    # Save detailed report
    report = analyzer.generate_report()
    with open('cleanup_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis complete! Detailed report saved to cleanup_analysis_report.json")

if __name__ == "__main__":
    main()