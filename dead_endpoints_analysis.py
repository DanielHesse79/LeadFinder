#!/usr/bin/env python3
"""
Dead Endpoints and Empty Functions Analysis

This script analyzes the LeadFinder codebase to identify:
1. Dead endpoints (defined but not used)
2. Empty functions in UI
3. Unused route definitions
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple

class CodebaseAnalyzer:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.routes = {}
        self.template_references = set()
        self.js_references = set()
        self.dead_endpoints = []
        self.empty_functions = []
        
    def analyze_routes(self) -> Dict[str, List[str]]:
        """Analyze all route definitions in the codebase"""
        routes = {}
        
        # Find all Python files in routes directory
        routes_dir = self.root_dir / "routes"
        if routes_dir.exists():
            for py_file in routes_dir.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue
                    
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract route definitions
                route_pattern = r'@(\w+_bp)\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)\s*\n\s*def\s+(\w+)'
                matches = re.findall(route_pattern, content)
                
                for blueprint, path, methods, func_name in matches:
                    if blueprint not in routes:
                        routes[blueprint] = []
                    routes[blueprint].append({
                        'path': path,
                        'methods': methods,
                        'function': func_name,
                        'file': str(py_file)
                    })
        
        return routes
    
    def analyze_template_references(self) -> Set[str]:
        """Find all url_for references in templates"""
        references = set()
        
        templates_dir = self.root_dir / "templates"
        if templates_dir.exists():
            for html_file in templates_dir.glob("*.html"):
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find url_for references
                url_pattern = r'url_for\([\'"]([^\'"]+\.[^\'"]+)[\'"]'
                matches = re.findall(url_pattern, content)
                references.update(matches)
        
        return references
    
    def analyze_js_references(self) -> Set[str]:
        """Find all route references in JavaScript files"""
        references = set()
        
        static_dir = self.root_dir / "static"
        if static_dir.exists():
            for js_file in static_dir.rglob("*.js"):
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find fetch/axios calls to routes
                fetch_pattern = r'fetch\([\'"`]([^\'"`]+)[\'"`]'
                matches = re.findall(fetch_pattern, content)
                references.update(matches)
        
        return references
    
    def find_empty_functions(self) -> List[Dict]:
        """Find empty or stub functions"""
        empty_functions = []
        
        for py_file in self.root_dir.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to find function definitions
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if function body is empty or just pass/return
                        if not node.body or (
                            len(node.body) == 1 and 
                            isinstance(node.body[0], (ast.Pass, ast.Return))
                        ):
                            empty_functions.append({
                                'file': str(py_file),
                                'function': node.name,
                                'line': node.lineno,
                                'type': 'empty'
                            })
                        elif len(node.body) == 1 and isinstance(node.body[0], ast.Expr):
                            # Check for TODO comments or simple returns
                            if hasattr(node.body[0], 'value') and isinstance(node.body[0].value, ast.Str):
                                if 'TODO' in node.body[0].value.s or 'pass' in node.body[0].value.s.lower():
                                    empty_functions.append({
                                        'file': str(py_file),
                                        'function': node.name,
                                        'line': node.lineno,
                                        'type': 'todo'
                                    })
            except Exception as e:
                print(f"Error parsing {py_file}: {e}")
        
        return empty_functions
    
    def find_js_empty_functions(self) -> List[Dict]:
        """Find empty JavaScript functions"""
        empty_functions = []
        
        for js_file in self.root_dir.rglob("*.js"):
            if "venv" in str(js_file) or "__pycache__" in str(js_file):
                continue
                
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find empty function definitions
                func_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*\{\s*\}'
                matches = re.finditer(func_pattern, content)
                
                for match in matches:
                    empty_functions.append({
                        'file': str(js_file),
                        'function': match.group(1),
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'empty_js'
                    })
                
                # Find arrow functions
                arrow_pattern = r'(\w+)\s*=\s*\([^)]*\)\s*=>\s*\{\s*\}'
                matches = re.finditer(arrow_pattern, content)
                
                for match in matches:
                    empty_functions.append({
                        'file': str(js_file),
                        'function': match.group(1),
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'empty_arrow'
                    })
                    
            except Exception as e:
                print(f"Error parsing {js_file}: {e}")
        
        return empty_functions
    
    def analyze(self) -> Dict:
        """Perform comprehensive analysis"""
        print("🔍 Analyzing codebase for dead endpoints and empty functions...")
        
        # Analyze routes
        self.routes = self.analyze_routes()
        print(f"📊 Found {sum(len(routes) for routes in self.routes.values())} route definitions")
        
        # Analyze template references
        self.template_references = self.analyze_template_references()
        print(f"📄 Found {len(self.template_references)} template references")
        
        # Analyze JS references
        self.js_references = self.analyze_js_references()
        print(f"📜 Found {len(self.js_references)} JavaScript references")
        
        # Find empty functions
        self.empty_functions = self.find_empty_functions()
        js_empty = self.find_js_empty_functions()
        self.empty_functions.extend(js_empty)
        print(f"🔍 Found {len(self.empty_functions)} empty/stub functions")
        
        # Identify dead endpoints
        self.dead_endpoints = self.identify_dead_endpoints()
        print(f"💀 Found {len(self.dead_endpoints)} dead endpoints")
        
        return {
            'routes': self.routes,
            'template_references': self.template_references,
            'js_references': self.js_references,
            'empty_functions': self.empty_functions,
            'dead_endpoints': self.dead_endpoints
        }
    
    def identify_dead_endpoints(self) -> List[Dict]:
        """Identify endpoints that are defined but not referenced"""
        dead_endpoints = []
        all_references = self.template_references.union(self.js_references)
        
        for blueprint, routes in self.routes.items():
            for route in routes:
                # Create the full route name
                route_name = f"{blueprint.replace('_bp', '')}.{route['function']}"
                
                # Check if this route is referenced anywhere
                is_referenced = False
                for ref in all_references:
                    if route_name in ref or route['path'] in ref:
                        is_referenced = True
                        break
                
                if not is_referenced:
                    dead_endpoints.append({
                        'blueprint': blueprint,
                        'route': route,
                        'route_name': route_name,
                        'reason': 'not_referenced'
                    })
        
        return dead_endpoints
    
    def generate_report(self) -> str:
        """Generate a comprehensive report"""
        report = []
        report.append("# 🧹 Dead Endpoints and Empty Functions Analysis")
        report.append("")
        report.append("## 📊 Summary")
        report.append("")
        report.append(f"- **Total Routes**: {sum(len(routes) for routes in self.routes.values())}")
        report.append(f"- **Template References**: {len(self.template_references)}")
        report.append(f"- **JavaScript References**: {len(self.js_references)}")
        report.append(f"- **Empty Functions**: {len(self.empty_functions)}")
        report.append(f"- **Dead Endpoints**: {len(self.dead_endpoints)}")
        report.append("")
        
        # Dead Endpoints Section
        if self.dead_endpoints:
            report.append("## 💀 Dead Endpoints")
            report.append("")
            report.append("These endpoints are defined but not referenced in templates or JavaScript:")
            report.append("")
            
            for endpoint in self.dead_endpoints:
                route = endpoint['route']
                report.append(f"### {endpoint['route_name']}")
                report.append(f"- **File**: {route['file']}")
                report.append(f"- **Path**: `{route['path']}`")
                report.append(f"- **Methods**: {route['methods'] or 'GET'}")
                report.append(f"- **Function**: `{route['function']}`")
                report.append("")
        else:
            report.append("## ✅ No Dead Endpoints Found")
            report.append("All defined routes appear to be referenced in templates or JavaScript.")
            report.append("")
        
        # Empty Functions Section
        if self.empty_functions:
            report.append("## 🔍 Empty/Stub Functions")
            report.append("")
            report.append("These functions are empty or contain only TODO comments:")
            report.append("")
            
            by_type = {}
            for func in self.empty_functions:
                func_type = func['type']
                if func_type not in by_type:
                    by_type[func_type] = []
                by_type[func_type].append(func)
            
            for func_type, functions in by_type.items():
                report.append(f"### {func_type.upper()} Functions")
                report.append("")
                
                for func in functions:
                    report.append(f"- **{func['function']}** in `{func['file']}:{func['line']}`")
                
                report.append("")
        else:
            report.append("## ✅ No Empty Functions Found")
            report.append("All functions appear to have proper implementations.")
            report.append("")
        
        # Route Analysis
        report.append("## 📊 Route Analysis by Blueprint")
        report.append("")
        
        for blueprint, routes in self.routes.items():
            report.append(f"### {blueprint}")
            report.append(f"- **Total Routes**: {len(routes)}")
            report.append("")
            
            for route in routes:
                status = "✅" if any(route['function'] in ref for ref in self.template_references) else "💀"
                report.append(f"{status} `{route['function']}` - `{route['path']}`")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Main analysis function"""
    analyzer = CodebaseAnalyzer()
    results = analyzer.analyze()
    
    # Generate report
    report = analyzer.generate_report()
    
    # Save report
    with open("DEAD_ENDPOINTS_ANALYSIS_REPORT.md", "w") as f:
        f.write(report)
    
    # Print summary
    print("\n" + "="*60)
    print("🔍 ANALYSIS COMPLETE")
    print("="*60)
    print(f"📊 Total Routes: {sum(len(routes) for routes in results['routes'].values())}")
    print(f"💀 Dead Endpoints: {len(results['dead_endpoints'])}")
    print(f"🔍 Empty Functions: {len(results['empty_functions'])}")
    print(f"📄 Template References: {len(results['template_references'])}")
    print(f"📜 JavaScript References: {len(results['js_references'])}")
    print("="*60)
    print("📋 Detailed report saved to: DEAD_ENDPOINTS_ANALYSIS_REPORT.md")

if __name__ == "__main__":
    main()