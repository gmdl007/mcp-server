#!/usr/bin/env python3
"""
YANG Model Analyzer for NSO Service Models

This module analyzes YANG models and automatically generates MCP tools
based on the model structure and configuration parameters.
"""

import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class YangModelAnalyzer:
    """Analyzes YANG models and generates MCP tool definitions."""
    
    def __init__(self):
        self.yang_models = {}
        self.service_models = {}
        
    def find_yang_models(self, ncs_path: str = None) -> Dict[str, str]:
        """Find all YANG models in NSO installation."""
        if not ncs_path:
            ncs_path = os.path.expanduser("~/NCS-614")
        
        yang_files = {}
        
        # Search for YANG files
        for root, dirs, files in os.walk(ncs_path):
            for file in files:
                if file.endswith('.yang'):
                    full_path = os.path.join(root, file)
                    yang_files[file] = full_path
                    
        logger.info(f"Found {len(yang_files)} YANG models")
        return yang_files
    
    def parse_yang_model(self, yang_file_path: str) -> Dict[str, Any]:
        """Parse a YANG model file and extract structure."""
        try:
            with open(yang_file_path, 'r') as f:
                content = f.read()
            
            model_info = {
                'file_path': yang_file_path,
                'file_name': os.path.basename(yang_file_path),
                'content': content,
                'containers': [],
                'lists': [],
                'leafs': [],
                'services': [],
                'groupings': []
            }
            
            # Extract module name
            module_match = re.search(r'module\s+(\S+)', content)
            if module_match:
                model_info['module_name'] = module_match.group(1)
            
            # Extract namespace
            namespace_match = re.search(r'namespace\s+"([^"]+)"', content)
            if namespace_match:
                model_info['namespace'] = namespace_match.group(1)
            
            # Extract prefix
            prefix_match = re.search(r'prefix\s+(\S+)', content)
            if prefix_match:
                model_info['prefix'] = prefix_match.group(1)
            
            # Extract containers
            container_matches = re.finditer(r'container\s+(\S+)\s*{([^}]+)}', content, re.DOTALL)
            for match in container_matches:
                container_name = match.group(1)
                container_content = match.group(2)
                model_info['containers'].append({
                    'name': container_name,
                    'content': container_content
                })
            
            # Extract lists
            list_matches = re.finditer(r'list\s+(\S+)\s*{([^}]+)}', content, re.DOTALL)
            for match in list_matches:
                list_name = match.group(1)
                list_content = match.group(2)
                model_info['lists'].append({
                    'name': list_name,
                    'content': list_content
                })
            
            # Extract leafs
            leaf_matches = re.finditer(r'leaf\s+(\S+)\s*{([^}]+)}', content, re.DOTALL)
            for match in leaf_matches:
                leaf_name = match.group(1)
                leaf_content = match.group(2)
                model_info['leafs'].append({
                    'name': leaf_name,
                    'content': leaf_content
                })
            
            # Extract groupings
            grouping_matches = re.finditer(r'grouping\s+(\S+)\s*{([^}]+)}', content, re.DOTALL)
            for match in grouping_matches:
                grouping_name = match.group(1)
                grouping_content = match.group(2)
                model_info['groupings'].append({
                    'name': grouping_name,
                    'content': grouping_content
                })
            
            # Check if this is a service model
            if 'service' in model_info['file_name'].lower() or 'service' in content.lower():
                model_info['is_service'] = True
                self.service_models[model_info['module_name']] = model_info
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error parsing YANG model {yang_file_path}: {e}")
            return {}
    
    def analyze_service_model(self, model_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a service model and extract configuration parameters."""
        service_analysis = {
            'service_name': model_info.get('module_name', 'unknown'),
            'configuration_parameters': [],
            'operations': [],
            'notifications': [],
            'rpcs': []
        }
        
        # Extract configuration parameters from containers and lists
        for container in model_info.get('containers', []):
            params = self._extract_parameters_from_content(container['content'])
            service_analysis['configuration_parameters'].extend(params)
        
        for list_item in model_info.get('lists', []):
            params = self._extract_parameters_from_content(list_item['content'])
            service_analysis['configuration_parameters'].extend(params)
        
        # Extract RPCs (Remote Procedure Calls)
        rpc_matches = re.finditer(r'rpc\s+(\S+)\s*{([^}]+)}', model_info['content'], re.DOTALL)
        for match in rpc_matches:
            rpc_name = match.group(1)
            rpc_content = match.group(2)
            service_analysis['rpcs'].append({
                'name': rpc_name,
                'content': rpc_content
            })
        
        return service_analysis
    
    def _extract_parameters_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Extract parameters from YANG content."""
        parameters = []
        
        # Extract leaf parameters
        leaf_matches = re.finditer(r'leaf\s+(\S+)\s*{([^}]+)}', content, re.DOTALL)
        for match in leaf_matches:
            leaf_name = match.group(1)
            leaf_content = match.group(2)
            
            param_info = {
                'name': leaf_name,
                'type': 'leaf',
                'description': self._extract_description(leaf_content),
                'type_info': self._extract_type_info(leaf_content),
                'default': self._extract_default(leaf_content),
                'mandatory': 'mandatory' in leaf_content
            }
            parameters.append(param_info)
        
        return parameters
    
    def _extract_description(self, content: str) -> str:
        """Extract description from YANG content."""
        desc_match = re.search(r'description\s+"([^"]+)"', content)
        return desc_match.group(1) if desc_match else ""
    
    def _extract_type_info(self, content: str) -> str:
        """Extract type information from YANG content."""
        type_match = re.search(r'type\s+(\S+)', content)
        return type_match.group(1) if type_match else "string"
    
    def _extract_default(self, content: str) -> Optional[str]:
        """Extract default value from YANG content."""
        default_match = re.search(r'default\s+"([^"]+)"', content)
        return default_match.group(1) if default_match else None
    
    def generate_mcp_tools(self, service_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate MCP tool definitions based on service analysis."""
        tools = []
        service_name = service_analysis['service_name']
        
        # Generate get service config tool
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
            'function_name': f'get_{service_name}_config'
        }
        tools.append(get_tool)
        
        # Generate create service tool
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
            'function_name': f'create_{service_name}_service'
        }
        
        # Add configuration parameters
        for param in service_analysis['configuration_parameters']:
            if param['name'] not in ['router_name', 'device']:  # Skip common parameters
                create_tool['parameters'].append({
                    'name': param['name'],
                    'type': param['type_info'],
                    'description': param['description'],
                    'required': param['mandatory'],
                    'default': param['default']
                })
        
        tools.append(create_tool)
        
        # Generate delete service tool
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
            'function_name': f'delete_{service_name}_service'
        }
        tools.append(delete_tool)
        
        # Generate RPC tools
        for rpc in service_analysis['rpcs']:
            rpc_tool = {
                'name': f'{service_name}_{rpc["name"]}',
                'description': f'Execute {rpc["name"]} RPC for {service_name} service',
                'parameters': [
                    {
                        'name': 'router_name',
                        'type': 'string',
                        'description': 'Router name to execute RPC on',
                        'required': True
                    }
                ],
                'function_name': f'{service_name}_{rpc["name"]}'
            }
            tools.append(rpc_tool)
        
        return tools
    
    def generate_python_code(self, tools: List[Dict[str, Any]], service_name: str) -> str:
        """Generate Python code for MCP tools."""
        code_lines = [
            f"# Auto-generated MCP tools for {service_name} service",
            f"# Generated by YangModelAnalyzer",
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
            
            function_sig = f"def {function_name}({', '.join(param_list)}) -> str:"
            
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
                f'        # TODO: Implement actual {service_name} service logic',
                f'        # This is a template - implement based on actual service model',
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
    """Main function to demonstrate YANG model analysis."""
    analyzer = YangModelAnalyzer()
    
    # Find YANG models
    yang_files = analyzer.find_yang_models()
    
    print(f"Found {len(yang_files)} YANG models")
    
    # Analyze service models
    service_models = {}
    for file_name, file_path in yang_files.items():
        if 'service' in file_name.lower():
            print(f"Analyzing service model: {file_name}")
            model_info = analyzer.parse_yang_model(file_path)
            if model_info:
                service_analysis = analyzer.analyze_service_model(model_info)
                service_models[model_info['module_name']] = service_analysis
    
    print(f"Found {len(service_models)} service models")
    
    # Generate MCP tools for each service
    for service_name, analysis in service_models.items():
        print(f"\nGenerating MCP tools for {service_name}:")
        tools = analyzer.generate_mcp_tools(analysis)
        
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # Generate Python code
        python_code = analyzer.generate_python_code(tools, service_name)
        
        # Save to file
        output_file = f"/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/auto_generated_{service_name}_tools.py"
        with open(output_file, 'w') as f:
            f.write(python_code)
        
        print(f"  Generated Python code saved to: {output_file}")

if __name__ == "__main__":
    main()
