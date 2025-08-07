"""
API Documentation Generator for LeadFinder

This module provides automated API documentation generation:
- Route discovery and analysis
- Parameter extraction and validation
- Response schema generation
- Interactive documentation
- OpenAPI/Swagger specification generation
"""

import inspect
import re
import ast
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass
from pathlib import Path
import json

try:
    from flask import Flask, Blueprint
except ImportError:
    Flask = None
    Blueprint = None

try:
    from utils.logger import get_logger
    logger = get_logger('api_docs')
except ImportError:
    logger = None

@dataclass
class RouteInfo:
    """Information about a Flask route"""
    endpoint: str
    methods: List[str]
    rule: str
    function_name: str
    module: str
    docstring: str
    parameters: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]
    decorators: List[str]

@dataclass
class ParameterInfo:
    """Information about a function parameter"""
    name: str
    type: str
    required: bool
    default: Any
    description: str

@dataclass
class ResponseInfo:
    """Information about a response"""
    status_code: int
    description: str
    schema: Dict[str, Any]

class APIDocumentationGenerator:
    """
    Automated API documentation generator
    """
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.routes = []
        self.blueprints = {}
        self.schemas = {}
        
    def analyze_app(self, app: Flask):
        """
        Analyze Flask application and extract route information
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        for rule in app.url_map.iter_rules():
            endpoint = rule.endpoint
            methods = list(rule.methods - {'HEAD', 'OPTIONS'})
            
            if endpoint == 'static':
                continue
            
            # Get view function
            view_func = app.view_functions.get(endpoint)
            if not view_func:
                continue
            
            # Extract route information
            route_info = self._extract_route_info(rule, view_func, methods)
            self.routes.append(route_info)
            
            # Group by blueprint
            blueprint_name = endpoint.split('.')[0] if '.' in endpoint else 'main'
            if blueprint_name not in self.blueprints:
                self.blueprints[blueprint_name] = []
            self.blueprints[blueprint_name].append(route_info)
    
    def _extract_route_info(self, rule, view_func, methods) -> RouteInfo:
        """Extract information from a route"""
        # Get function source
        try:
            source = inspect.getsource(view_func)
        except (OSError, TypeError):
            source = ""
        
        # Parse docstring
        docstring = inspect.getdoc(view_func) or ""
        
        # Extract parameters
        parameters = self._extract_parameters(view_func)
        
        # Extract responses
        responses = self._extract_responses(docstring)
        
        # Extract decorators
        decorators = self._extract_decorators(source)
        
        return RouteInfo(
            endpoint=rule.endpoint,
            methods=methods,
            rule=str(rule),
            function_name=view_func.__name__,
            module=view_func.__module__,
            docstring=docstring,
            parameters=parameters,
            responses=responses,
            decorators=decorators
        )
    
    def _extract_parameters(self, view_func) -> List[Dict[str, Any]]:
        """Extract parameter information from function"""
        parameters = []
        
        try:
            sig = inspect.signature(view_func)
            for name, param in sig.parameters.items():
                if name in ['self', 'cls']:
                    continue
                
                param_info = {
                    'name': name,
                    'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
                    'required': param.default == inspect.Parameter.empty,
                    'default': param.default if param.default != inspect.Parameter.empty else None,
                    'description': self._extract_parameter_description(name, inspect.getdoc(view_func) or "")
                }
                parameters.append(param_info)
        except Exception as e:
            if logger:
                logger.warning(f"Error extracting parameters from {view_func.__name__}: {e}")
        
        return parameters
    
    def _extract_parameter_description(self, param_name: str, docstring: str) -> str:
        """Extract parameter description from docstring"""
        # Look for parameter documentation in docstring
        param_pattern = rf":param {param_name}:(.*?)(?=:param|:return|$)"
        match = re.search(param_pattern, docstring, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_responses(self, docstring: str) -> List[Dict[str, Any]]:
        """Extract response information from docstring"""
        responses = []
        
        # Look for response documentation
        response_pattern = r":return:(.*?)(?=:param|$)"
        match = re.search(response_pattern, docstring, re.DOTALL)
        if match:
            response_text = match.group(1).strip()
            
            # Try to parse JSON response
            try:
                # Look for JSON examples in docstring
                json_pattern = r'\{.*?\}'
                json_matches = re.findall(json_pattern, response_text, re.DOTALL)
                for json_str in json_matches:
                    try:
                        schema = json.loads(json_str)
                        responses.append({
                            'status_code': 200,
                            'description': 'Success response',
                            'schema': schema
                        })
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass
        
        # Add default responses
        if not responses:
            responses.append({
                'status_code': 200,
                'description': 'Success response',
                'schema': {'message': 'Success'}
            })
        
        return responses
    
    def _extract_decorators(self, source: str) -> List[str]:
        """Extract decorators from function source"""
        decorators = []
        
        try:
            # Parse source code
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name):
                            decorators.append(decorator.id)
                        elif isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Name):
                                decorators.append(decorator.func.id)
        except Exception as e:
            if logger:
                logger.warning(f"Error extracting decorators: {e}")
        
        return decorators
    
    def generate_markdown_docs(self) -> str:
        """Generate Markdown documentation"""
        docs = []
        
        # Title
        docs.append("# LeadFinder API Documentation\n")
        docs.append("This document provides comprehensive API documentation for the LeadFinder platform.\n")
        
        # Table of Contents
        docs.append("## Table of Contents\n")
        for blueprint_name, routes in self.blueprints.items():
            docs.append(f"- [{blueprint_name.title()}](#{blueprint_name.lower()})\n")
        
        # Generate documentation for each blueprint
        for blueprint_name, routes in self.blueprints.items():
            docs.append(f"## {blueprint_name.title()}\n")
            
            for route in routes:
                docs.append(self._generate_route_docs(route))
                docs.append("\n")
        
        return "\n".join(docs)
    
    def _generate_route_docs(self, route: RouteInfo) -> str:
        """Generate documentation for a single route"""
        docs = []
        
        # Route header
        methods_str = ", ".join(route.methods)
        docs.append(f"### {route.function_name}\n")
        docs.append(f"**Endpoint:** `{route.rule}`  \n")
        docs.append(f"**Methods:** `{methods_str}`\n")
        
        # Description
        if route.docstring:
            docs.append(f"**Description:** {route.docstring.split('.')[0]}.\n")
        
        # Parameters
        if route.parameters:
            docs.append("**Parameters:**\n")
            docs.append("| Name | Type | Required | Default | Description |\n")
            docs.append("|------|------|----------|---------|-------------|\n")
            
            for param in route.parameters:
                required = "Yes" if param['required'] else "No"
                default = str(param['default']) if param['default'] is not None else "-"
                docs.append(f"| {param['name']} | {param['type']} | {required} | {default} | {param['description']} |\n")
        
        # Responses
        if route.responses:
            docs.append("**Responses:**\n")
            for response in route.responses:
                docs.append(f"- **{response['status_code']}:** {response['description']}\n")
                if 'schema' in response:
                    docs.append(f"  ```json\n{json.dumps(response['schema'], indent=2)}\n  ```\n")
        
        # Decorators
        if route.decorators:
            docs.append(f"**Decorators:** {', '.join(route.decorators)}\n")
        
        return "\n".join(docs)
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI/Swagger specification"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "LeadFinder API",
                "description": "Comprehensive API for lead discovery and research",
                "version": "1.0.0"
            },
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            }
        }
        
        # Generate paths
        for route in self.routes:
            path = self._convert_rule_to_openapi_path(route.rule)
            
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            
            for method in route.methods:
                method_lower = method.lower()
                spec["paths"][path][method_lower] = {
                    "summary": route.function_name,
                    "description": route.docstring or "",
                    "parameters": self._convert_parameters_to_openapi(route.parameters),
                    "responses": self._convert_responses_to_openapi(route.responses),
                    "tags": [route.endpoint.split('.')[0]]
                }
        
        return spec
    
    def _convert_rule_to_openapi_path(self, rule: str) -> str:
        """Convert Flask rule to OpenAPI path"""
        # Convert Flask URL parameters to OpenAPI format
        path = re.sub(r'<([^:>]+):([^>]+)>', r'{\2}', rule)
        return path
    
    def _convert_parameters_to_openapi(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert parameters to OpenAPI format"""
        openapi_params = []
        
        for param in parameters:
            openapi_param = {
                "name": param['name'],
                "in": "query" if param['name'] in ['q', 'query', 'search'] else "path",
                "required": param['required'],
                "schema": {
                    "type": self._convert_type_to_openapi(param['type'])
                },
                "description": param['description']
            }
            
            if param['default'] is not None:
                openapi_param["schema"]["default"] = param['default']
            
            openapi_params.append(openapi_param)
        
        return openapi_params
    
    def _convert_type_to_openapi(self, type_str: str) -> str:
        """Convert Python type to OpenAPI type"""
        type_mapping = {
            'str': 'string',
            'int': 'integer',
            'float': 'number',
            'bool': 'boolean',
            'list': 'array',
            'dict': 'object'
        }
        
        for py_type, openapi_type in type_mapping.items():
            if py_type in type_str.lower():
                return openapi_type
        
        return 'string'
    
    def _convert_responses_to_openapi(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert responses to OpenAPI format"""
        openapi_responses = {}
        
        for response in responses:
            status_code = str(response['status_code'])
            openapi_responses[status_code] = {
                "description": response['description'],
                "content": {
                    "application/json": {
                        "schema": response.get('schema', {})
                    }
                }
            }
        
        return openapi_responses
    
    def generate_html_docs(self) -> str:
        """Generate HTML documentation"""
        # This would generate interactive HTML documentation
        # For now, return a simple HTML wrapper around markdown
        markdown = self.generate_markdown_docs()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LeadFinder API Documentation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
{markdown.replace('\\n', '<br>')}
</body>
</html>
"""
        return html
    
    def save_documentation(self, output_dir: str = "docs"):
        """Save documentation to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save Markdown documentation
        markdown_docs = self.generate_markdown_docs()
        with open(output_path / "api_documentation.md", "w") as f:
            f.write(markdown_docs)
        
        # Save OpenAPI specification
        openapi_spec = self.generate_openapi_spec()
        with open(output_path / "openapi.json", "w") as f:
            json.dump(openapi_spec, f, indent=2)
        
        # Save HTML documentation
        html_docs = self.generate_html_docs()
        with open(output_path / "api_documentation.html", "w") as f:
            f.write(html_docs)
        
        if logger:
            logger.info(f"Documentation saved to {output_path}")

def generate_api_docs(app: Flask, output_dir: str = "docs"):
    """
    Generate comprehensive API documentation for a Flask app
    
    Args:
        app: Flask application
        output_dir: Output directory for documentation
    """
    generator = APIDocumentationGenerator()
    generator.analyze_app(app)
    generator.save_documentation(output_dir)
    
    return generator

def get_api_summary(app: Flask) -> Dict[str, Any]:
    """
    Get API summary information
    
    Args:
        app: Flask application
        
    Returns:
        Dictionary with API summary
    """
    generator = APIDocumentationGenerator()
    generator.analyze_app(app)
    
    summary = {
        'total_routes': len(generator.routes),
        'blueprints': {},
        'methods_used': set(),
        'endpoints': []
    }
    
    for blueprint_name, routes in generator.blueprints.items():
        summary['blueprints'][blueprint_name] = {
            'route_count': len(routes),
            'methods': list(set(method for route in routes for method in route.methods))
        }
        
        for route in routes:
            summary['methods_used'].update(route.methods)
            summary['endpoints'].append({
                'endpoint': route.endpoint,
                'rule': route.rule,
                'methods': route.methods
            })
    
    summary['methods_used'] = list(summary['methods_used'])
    
    return summary 