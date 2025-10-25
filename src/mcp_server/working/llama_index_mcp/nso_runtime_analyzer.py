#!/usr/bin/env python3
"""
NSO Runtime Model Analyzer

This module analyzes the actual NSO runtime model structure and automatically 
generates MCP tools based on the discovered service models and their parameters.
"""

import ncs.maapi as maapi
import ncs.maagic as maagic
import logging
from typing import Dict, List, Any, Optional
import inspect

logger = logging.getLogger(__name__)

class NSORuntimeModelAnalyzer:
    """Analyzes NSO runtime models and generates MCP tool definitions."""
    
    def __init__(self):
        self.services = {}
        self.device_configs = {}
        
    def analyze_nso_runtime(self) -> Dict[str, Any]:
        """Analyze the actual NSO runtime model structure."""
        try:
            m = maapi.Maapi()
            m.start_user_session('cisco', 'test_context_1')
            t = m.start_read_trans()
            root = maagic.get_root(t)
            
            analysis = {
                'services': {},
                'device_configs': {},
                'root_structure': {}
            }
            
            # Analyze root structure
            for attr in dir(root):
                if not attr.startswith('_') and not callable(getattr(root, attr)):
                    try:
                        value = getattr(root, attr)
                        analysis['root_structure'][attr] = {
                            'type': str(type(value)),
                            'has_keys': hasattr(value, 'keys'),
                            'has_create': hasattr(value, 'create'),
                            'has_delete': hasattr(value, 'delete')
                        }
                        
                        # Check if this looks like a service
                        if hasattr(value, 'keys') and hasattr(value, 'create'):
                            service_info = self._analyze_service_structure(value, attr)
                            if service_info:
                                analysis['services'][attr] = service_info
                        
                        # Check if this looks like device config
                        if 'device' in attr.lower() or 'config' in attr.lower():
                            config_info = self._analyze_config_structure(value, attr)
                            if config_info:
                                analysis['device_configs'][attr] = config_info
                                
                    except Exception as e:
                        logger.debug(f"Error analyzing {attr}: {e}")
            
            m.end_user_session()
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing NSO runtime: {e}")
            return {}
    
    def _analyze_service_structure(self, service_obj, service_name: str) -> Optional[Dict[str, Any]]:
        """Analyze a service structure and extract parameters."""
        try:
            service_info = {
                'name': service_name,
                'type': str(type(service_obj)),
                'parameters': [],
                'operations': []
            }
            
            # Check if service has instances
            if hasattr(service_obj, 'keys'):
                keys = list(service_obj.keys())
                if keys:
                    # Analyze first instance to understand structure
                    first_instance = service_obj[keys[0]]
                    service_info['parameters'] = self._extract_parameters_from_instance(first_instance)
            
            # Check for common service operations
            if hasattr(service_obj, 'create'):
                service_info['operations'].append('create')
            if hasattr(service_obj, 'delete'):
                service_info['operations'].append('delete')
            
            return service_info
            
        except Exception as e:
            logger.debug(f"Error analyzing service {service_name}: {e}")
            return None
    
    def _analyze_config_structure(self, config_obj, config_name: str) -> Optional[Dict[str, Any]]:
        """Analyze a configuration structure and extract parameters."""
        try:
            config_info = {
                'name': config_name,
                'type': str(type(config_obj)),
                'parameters': []
            }
            
            # Extract parameters from config object
            config_info['parameters'] = self._extract_parameters_from_instance(config_obj)
            
            return config_info
            
        except Exception as e:
            logger.debug(f"Error analyzing config {config_name}: {e}")
            return None
    
    def _extract_parameters_from_instance(self, instance) -> List[Dict[str, Any]]:
        """Extract parameters from a model instance."""
        parameters = []
        
        for attr in dir(instance):
            if not attr.startswith('_') and not callable(getattr(instance, attr)):
                try:
                    value = getattr(instance, attr)
                    param_info = {
                        'name': attr,
                        'type': str(type(value)),
                        'value': str(value) if value is not None else None,
                        'has_create': hasattr(value, 'create'),
                        'has_delete': hasattr(value, 'delete'),
                        'has_keys': hasattr(value, 'keys')
                    }
                    parameters.append(param_info)
                except Exception as e:
                    logger.debug(f"Error extracting parameter {attr}: {e}")
        
        return parameters
    
    def generate_mcp_tools_from_analysis(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate MCP tool definitions from analysis."""
        tools = []
        
        # Generate tools for services
        for service_name, service_info in analysis.get('services', {}).items():
            service_tools = self._generate_service_tools(service_name, service_info)
            tools.extend(service_tools)
        
        # Generate tools for device configs
        for config_name, config_info in analysis.get('device_configs', {}).items():
            config_tools = self._generate_config_tools(config_name, config_info)
            tools.extend(config_tools)
        
        return tools
    
    def _generate_service_tools(self, service_name: str, service_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate MCP tools for a service."""
        tools = []
        
        # Get service config tool
        get_tool = {
            'name': f'get_{service_name}_config',
            'description': f'Get {service_name} service configuration',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': f'Router name to get {service_name} configuration for',
                    'required': False
                }
            ],
            'function_name': f'get_{service_name}_config',
            'service_name': service_name
        }
        tools.append(get_tool)
        
        # Create service tool
        create_tool = {
            'name': f'create_{service_name}_service',
            'description': f'Create {service_name} service instance',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': 'Router name to create service for',
                    'required': True
                }
            ],
            'function_name': f'create_{service_name}_service',
            'service_name': service_name
        }
        
        # Add service-specific parameters
        for param in service_info.get('parameters', []):
            if param['name'] not in ['router_name', 'device', 'commit_queue', 'log', 'modified']:
                create_tool['parameters'].append({
                    'name': param['name'],
                    'type': self._map_nso_type_to_python(param['type']),
                    'description': f'{service_name} {param["name"]} parameter',
                    'required': False,
                    'default': param.get('value')
                })
        
        tools.append(create_tool)
        
        # Delete service tool
        delete_tool = {
            'name': f'delete_{service_name}_service',
            'description': f'Delete {service_name} service instance',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': 'Router name to delete service for',
                    'required': True
                },
                {
                    'name': 'confirm',
                    'type': 'boolean',
                    'description': 'Confirmation flag for deletion',
                    'required': True,
                    'default': False
                }
            ],
            'function_name': f'delete_{service_name}_service',
            'service_name': service_name
        }
        tools.append(delete_tool)
        
        return tools
    
    def _generate_config_tools(self, config_name: str, config_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate MCP tools for device configuration."""
        tools = []
        
        # Get config tool
        get_tool = {
            'name': f'get_{config_name}_config',
            'description': f'Get {config_name} device configuration',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': f'Router name to get {config_name} configuration for',
                    'required': True
                }
            ],
            'function_name': f'get_{config_name}_config',
            'config_name': config_name
        }
        tools.append(get_tool)
        
        return tools
    
    def _map_nso_type_to_python(self, nso_type: str) -> str:
        """Map NSO types to Python types."""
        type_mapping = {
            'str': 'string',
            'int': 'integer',
            'bool': 'boolean',
            'float': 'number',
            'list': 'array'
        }
        
        for nso_t, python_t in type_mapping.items():
            if nso_t in nso_type.lower():
                return python_t
        
        return 'string'  # Default to string
    
    def generate_python_code(self, tools: List[Dict[str, Any]]) -> str:
        """Generate Python code for all MCP tools."""
        code_lines = [
            "# Auto-generated MCP tools based on NSO runtime model analysis",
            "# Generated by NSORuntimeModelAnalyzer",
            "",
            "import ncs.maapi as maapi",
            "import ncs.maagic as maagic",
            "import logging",
            "",
            "logger = logging.getLogger(__name__)",
            ""
        ]
        
        for tool in tools:
            function_name = tool['function_name']
            description = tool['description']
            parameters = tool['parameters']
            
            # Generate function signature
            param_list = []
            for param in parameters:
                if param.get('default') is not None:
                    param_list.append(f"{param['name']}: {param['type']} = {repr(param['default'])}")
                else:
                    param_list.append(f"{param['name']}: {param['type']}")
            
            code_lines.extend([
                f'def {function_name}({", ".join(param_list)}) -> str:',
                f'    """{description}',
                f'    ',
                f'    Args:'
            ])
            
            for param in parameters:
                required = "Required" if param.get('required', False) else "Optional"
                code_lines.append(f'        {param["name"]}: {param["description"]} ({required})')
            
            code_lines.extend([
                f'    ',
                f'    Returns:',
                f'        str: Result message',
                f'    """',
                f'    try:',
                f'        logger.info(f"🔧 {description}")',
                f'        ',
                f'        m = maapi.Maapi()',
                f'        m.start_user_session(\'cisco\', \'test_context_1\')',
                f'        ',
                f'        # TODO: Implement actual {function_name} logic',
                f'        # This is a template - implement based on actual NSO model',
                f'        ',
                f'        m.end_user_session()',
                f'        return f"✅ {description} completed"',
                f'        ',
                f'    except Exception as e:',
                f'        logger.exception(f"❌ Error in {function_name}: {{e}}")',
                f'        try:',
                f'            m.end_user_session()',
                f'        except:',
                f'            pass',
                f'        return f"Error in {function_name}: {{e}}"',
                f'',
                f'# Register with FastMCP',
                f'mcp.tool({function_name})',
                f''
            ])
        
        return '\n'.join(code_lines)

def main():
    """Main function to demonstrate NSO runtime model analysis."""
    analyzer = NSORuntimeModelAnalyzer()
    
    print("Analyzing NSO runtime model structure...")
    analysis = analyzer.analyze_nso_runtime()
    
    print(f"Found {len(analysis.get('services', {}))} services:")
    for service_name, service_info in analysis.get('services', {}).items():
        print(f"  - {service_name}: {len(service_info.get('parameters', []))} parameters")
    
    print(f"Found {len(analysis.get('device_configs', {}))} device configs:")
    for config_name, config_info in analysis.get('device_configs', {}).items():
        print(f"  - {config_name}: {len(config_info.get('parameters', []))} parameters")
    
    # Generate MCP tools
    tools = analyzer.generate_mcp_tools_from_analysis(analysis)
    
    print(f"\nGenerated {len(tools)} MCP tools:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Generate Python code
    python_code = analyzer.generate_python_code(tools)
    
    # Save to file
    output_file = "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/auto_generated_nso_tools.py"
    with open(output_file, 'w') as f:
        f.write(python_code)
    
    print(f"\nGenerated Python code saved to: {output_file}")
    
    return analysis, tools

if __name__ == "__main__":
    main()
