#!/usr/bin/env python3
"""
Universal YANG Model Analyzer and MCP Tool Generator

This module can analyze any YANG model and automatically generate MCP tools
based on the model structure and configuration parameters.
"""

import re
import os
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class YangParameter:
    """Represents a YANG parameter."""
    name: str
    type: str
    description: str
    required: bool = False
    default: Optional[str] = None
    example: Optional[str] = None
    choices: List[str] = None
    range: Optional[str] = None

@dataclass
class YangContainer:
    """Represents a YANG container."""
    name: str
    description: str
    parameters: List[YangParameter]
    containers: List['YangContainer'] = None
    lists: List['YangList'] = None

@dataclass
class YangList:
    """Represents a YANG list."""
    name: str
    description: str
    key: Optional[str] = None
    parameters: List[YangParameter] = None
    containers: List[YangContainer] = None

@dataclass
class YangRPC:
    """Represents a YANG RPC."""
    name: str
    description: str
    input_parameters: List[YangParameter]
    output_parameters: List[YangParameter] = None

@dataclass
class YangModel:
    """Represents a complete YANG model."""
    name: str
    namespace: str
    prefix: str
    description: str
    containers: List[YangContainer]
    lists: List[YangList]
    rpcs: List[YangRPC]
    parameters: List[YangParameter]

class YangModelAnalyzer:
    """Analyzes YANG models and generates MCP tool definitions."""
    
    def __init__(self):
        self.models = {}
        
    def parse_yang_model(self, yang_content: str, model_name: str = None) -> YangModel:
        """Parse a YANG model from content string."""
        try:
            # Extract basic model information
            module_match = re.search(r'module\s+(\S+)', yang_content)
            module_name = module_match.group(1) if module_match else (model_name or "unknown")
            
            namespace_match = re.search(r'namespace\s+"([^"]+)"', yang_content)
            namespace = namespace_match.group(1) if namespace_match else ""
            
            prefix_match = re.search(r'prefix\s+(\S+)', yang_content)
            prefix = prefix_match.group(1) if prefix_match else ""
            
            description_match = re.search(r'description\s+"([^"]+)"', yang_content)
            description = description_match.group(1) if description_match else f"YANG model for {module_name}"
            
            # Extract containers
            containers = self._extract_containers(yang_content)
            
            # Extract lists
            lists = self._extract_lists(yang_content)
            
            # Extract RPCs
            rpcs = self._extract_rpcs(yang_content)
            
            # Extract top-level parameters
            parameters = self._extract_top_level_parameters(yang_content)
            
            return YangModel(
                name=module_name,
                namespace=namespace,
                prefix=prefix,
                description=description,
                containers=containers,
                lists=lists,
                rpcs=rpcs,
                parameters=parameters
            )
            
        except Exception as e:
            logger.error(f"Error parsing YANG model: {e}")
            return None
    
    def _extract_containers(self, content: str) -> List[YangContainer]:
        """Extract containers from YANG content."""
        containers = []
        
        # Find all container definitions
        container_pattern = r'container\s+(\S+)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}'
        matches = re.finditer(container_pattern, content, re.DOTALL)
        
        for match in matches:
            container_name = match.group(1)
            container_content = match.group(2)
            
            # Extract description
            description = self._extract_description(container_content)
            
            # Extract parameters within container
            parameters = self._extract_parameters_from_content(container_content)
            
            # Extract nested containers
            nested_containers = self._extract_containers(container_content)
            
            # Extract nested lists
            nested_lists = self._extract_lists(container_content)
            
            containers.append(YangContainer(
                name=container_name,
                description=description,
                parameters=parameters,
                containers=nested_containers,
                lists=nested_lists
            ))
        
        return containers
    
    def _extract_lists(self, content: str) -> List[YangList]:
        """Extract lists from YANG content."""
        lists = []
        
        # Find all list definitions
        list_pattern = r'list\s+(\S+)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}'
        matches = re.finditer(list_pattern, content, re.DOTALL)
        
        for match in matches:
            list_name = match.group(1)
            list_content = match.group(2)
            
            # Extract description
            description = self._extract_description(list_content)
            
            # Extract key
            key_match = re.search(r'key\s+"([^"]+)"', list_content)
            key = key_match.group(1) if key_match else None
            
            # Extract parameters within list
            parameters = self._extract_parameters_from_content(list_content)
            
            # Extract nested containers
            nested_containers = self._extract_containers(list_content)
            
            lists.append(YangList(
                name=list_name,
                description=description,
                key=key,
                parameters=parameters,
                containers=nested_containers
            ))
        
        return lists
    
    def _extract_rpcs(self, content: str) -> List[YangRPC]:
        """Extract RPCs from YANG content."""
        rpcs = []
        
        # Find all RPC definitions
        rpc_pattern = r'rpc\s+(\S+)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}'
        matches = re.finditer(rpc_pattern, content, re.DOTALL)
        
        for match in matches:
            rpc_name = match.group(1)
            rpc_content = match.group(2)
            
            # Extract description
            description = self._extract_description(rpc_content)
            
            # Extract input parameters
            input_match = re.search(r'input\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', rpc_content, re.DOTALL)
            input_parameters = []
            if input_match:
                input_content = input_match.group(1)
                input_parameters = self._extract_parameters_from_content(input_content)
            
            # Extract output parameters
            output_match = re.search(r'output\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}', rpc_content, re.DOTALL)
            output_parameters = []
            if output_match:
                output_content = output_match.group(1)
                output_parameters = self._extract_parameters_from_content(output_content)
            
            rpcs.append(YangRPC(
                name=rpc_name,
                description=description,
                input_parameters=input_parameters,
                output_parameters=output_parameters
            ))
        
        return rpcs
    
    def _extract_top_level_parameters(self, content: str) -> List[YangParameter]:
        """Extract top-level parameters from YANG content."""
        return self._extract_parameters_from_content(content)
    
    def _extract_parameters_from_content(self, content: str) -> List[YangParameter]:
        """Extract parameters from YANG content."""
        parameters = []
        
        # Extract leaf parameters
        leaf_pattern = r'leaf\s+(\S+)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}'
        leaf_matches = re.finditer(leaf_pattern, content, re.DOTALL)
        
        for match in leaf_matches:
            leaf_name = match.group(1)
            leaf_content = match.group(2)
            
            parameter = self._parse_parameter(leaf_name, leaf_content)
            if parameter:
                parameters.append(parameter)
        
        # Extract leaf-list parameters
        leaflist_pattern = r'leaf-list\s+(\S+)\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}'
        leaflist_matches = re.finditer(leaflist_pattern, content, re.DOTALL)
        
        for match in leaflist_matches:
            leaflist_name = match.group(1)
            leaflist_content = match.group(2)
            
            parameter = self._parse_parameter(leaflist_name, leaflist_content)
            if parameter:
                parameter.type = "array"
                parameters.append(parameter)
        
        return parameters
    
    def _parse_parameter(self, name: str, content: str) -> Optional[YangParameter]:
        """Parse a single parameter from YANG content."""
        try:
            # Extract description
            description = self._extract_description(content)
            
            # Extract type
            type_info = self._extract_type_info(content)
            
            # Extract default value
            default = self._extract_default(content)
            
            # Check if mandatory
            mandatory = 'mandatory true' in content
            
            # Extract choices
            choices = self._extract_choices(content)
            
            # Extract range
            range_info = self._extract_range(content)
            
            return YangParameter(
                name=name,
                type=type_info,
                description=description,
                required=mandatory,
                default=default,
                choices=choices,
                range=range_info
            )
            
        except Exception as e:
            logger.debug(f"Error parsing parameter {name}: {e}")
            return None
    
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
    
    def _extract_choices(self, content: str) -> List[str]:
        """Extract choices from YANG content."""
        choices = []
        choice_pattern = r'enum\s+"([^"]+)"'
        matches = re.finditer(choice_pattern, content)
        for match in matches:
            choices.append(match.group(1))
        return choices
    
    def _extract_range(self, content: str) -> Optional[str]:
        """Extract range from YANG content."""
        range_match = re.search(r'range\s+"([^"]+)"', content)
        return range_match.group(1) if range_match else None
    
    def generate_mcp_tools_from_model(self, model: YangModel) -> List[Dict[str, Any]]:
        """Generate MCP tool definitions from a YANG model."""
        tools = []
        
        # Generate tools for top-level containers
        for container in model.containers:
            container_tools = self._generate_container_tools(model.name, container)
            tools.extend(container_tools)
        
        # Generate tools for top-level lists
        for list_item in model.lists:
            list_tools = self._generate_list_tools(model.name, list_item)
            tools.extend(list_tools)
        
        # Generate tools for RPCs
        for rpc in model.rpcs:
            rpc_tool = self._generate_rpc_tool(model.name, rpc)
            tools.append(rpc_tool)
        
        return tools
    
    def _generate_container_tools(self, model_name: str, container: YangContainer) -> List[Dict[str, Any]]:
        """Generate MCP tools for a container."""
        tools = []
        
        # Get container tool
        get_tool = {
            'name': f'get_{model_name}_{container.name}',
            'description': f'Get {container.description}',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': 'Router name to get configuration for',
                    'required': False
                }
            ],
            'function_name': f'get_{model_name}_{container.name}',
            'model_name': model_name,
            'container_name': container.name
        }
        tools.append(get_tool)
        
        # Create container tool
        create_tool = {
            'name': f'create_{model_name}_{container.name}',
            'description': f'Create {container.description}',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': 'Router name to create configuration for',
                    'required': True
                }
            ],
            'function_name': f'create_{model_name}_{container.name}',
            'model_name': model_name,
            'container_name': container.name
        }
        
        # Add container parameters
        for param in container.parameters:
            create_tool['parameters'].append({
                'name': param.name,
                'type': self._map_yang_type_to_python(param.type),
                'description': param.description,
                'required': param.required,
                'default': param.default,
                'choices': param.choices,
                'range': param.range
            })
        
        tools.append(create_tool)
        
        return tools
    
    def _generate_list_tools(self, model_name: str, list_item: YangList) -> List[Dict[str, Any]]:
        """Generate MCP tools for a list."""
        tools = []
        
        # Get list tool
        get_tool = {
            'name': f'get_{model_name}_{list_item.name}',
            'description': f'Get {list_item.description}',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': 'Router name to get list for',
                    'required': False
                }
            ],
            'function_name': f'get_{model_name}_{list_item.name}',
            'model_name': model_name,
            'list_name': list_item.name
        }
        tools.append(get_tool)
        
        # Add list item tool
        add_tool = {
            'name': f'add_{model_name}_{list_item.name}_item',
            'description': f'Add item to {list_item.description}',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': 'Router name to add item to',
                    'required': True
                }
            ],
            'function_name': f'add_{model_name}_{list_item.name}_item',
            'model_name': model_name,
            'list_name': list_item.name
        }
        
        # Add list parameters
        if list_item.parameters:
            for param in list_item.parameters:
                add_tool['parameters'].append({
                    'name': param.name,
                    'type': self._map_yang_type_to_python(param.type),
                    'description': param.description,
                    'required': param.required,
                    'default': param.default,
                    'choices': param.choices,
                    'range': param.range
                })
        
        tools.append(add_tool)
        
        return tools
    
    def _generate_rpc_tool(self, model_name: str, rpc: YangRPC) -> Dict[str, Any]:
        """Generate MCP tool for an RPC."""
        tool = {
            'name': f'{model_name}_{rpc.name}',
            'description': f'Execute {rpc.description}',
            'parameters': [
                {
                    'name': 'router_name',
                    'type': 'string',
                    'description': 'Router name to execute RPC on',
                    'required': True
                }
            ],
            'function_name': f'{model_name}_{rpc.name}',
            'model_name': model_name,
            'rpc_name': rpc.name
        }
        
        # Add input parameters
        for param in rpc.input_parameters:
            tool['parameters'].append({
                'name': param.name,
                'type': self._map_yang_type_to_python(param.type),
                'description': param.description,
                'required': param.required,
                'default': param.default,
                'choices': param.choices,
                'range': param.range
            })
        
        return tool
    
    def _map_yang_type_to_python(self, yang_type: str) -> str:
        """Map YANG types to Python types."""
        type_mapping = {
            'string': 'string',
            'int8': 'integer',
            'int16': 'integer',
            'int32': 'integer',
            'int64': 'integer',
            'uint8': 'integer',
            'uint16': 'integer',
            'uint32': 'integer',
            'uint64': 'integer',
            'boolean': 'boolean',
            'decimal64': 'number',
            'binary': 'string',
            'bits': 'string',
            'enumeration': 'string',
            'union': 'string',
            'identityref': 'string',
            'instance-identifier': 'string',
            'leafref': 'string'
        }
        
        return type_mapping.get(yang_type, 'string')
    
    def generate_python_code(self, tools: List[Dict[str, Any]], model_name: str) -> str:
        """Generate Python code for MCP tools."""
        code_lines = [
            f"# Auto-generated MCP tools for {model_name} YANG model",
            f"# Generated by Universal YANG Model Analyzer",
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
                choices = f" (choices: {param['choices']})" if param.get('choices') else ""
                range_info = f" (range: {param['range']})" if param.get('range') else ""
                code_lines.append(f'        {param["name"]}: {param["description"]} ({required}){choices}{range_info}')
            
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
                f'        # This is a template - implement based on actual YANG model',
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

def analyze_yang_model_from_file(yang_file_path: str) -> Dict[str, Any]:
    """Analyze a YANG model from file and generate MCP tools."""
    try:
        with open(yang_file_path, 'r') as f:
            yang_content = f.read()
        
        analyzer = YangModelAnalyzer()
        model = analyzer.parse_yang_model(yang_content, os.path.basename(yang_file_path))
        
        if model:
            tools = analyzer.generate_mcp_tools_from_model(model)
            python_code = analyzer.generate_python_code(tools, model.name)
            
            return {
                'model': model,
                'tools': tools,
                'python_code': python_code
            }
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error analyzing YANG model from file {yang_file_path}: {e}")
        return None

def main():
    """Main function to demonstrate YANG model analysis."""
    print("Universal YANG Model Analyzer")
    print("=" * 50)
    
    # Example: Analyze a YANG model
    yang_file = "/Users/gudeng/NCS-614/packages/neds/cisco-nx-cli-3.0/src/yang/tailf-ned-cisco-nx-router-ospf.yang"
    
    if os.path.exists(yang_file):
        print(f"Analyzing YANG model: {yang_file}")
        result = analyze_yang_model_from_file(yang_file)
        
        if result:
            model = result['model']
            tools = result['tools']
            
            print(f"Model: {model.name}")
            print(f"Namespace: {model.namespace}")
            print(f"Description: {model.description}")
            print(f"Containers: {len(model.containers)}")
            print(f"Lists: {len(model.lists)}")
            print(f"RPCs: {len(model.rpcs)}")
            print(f"Generated {len(tools)} MCP tools")
            
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            
            # Save generated code
            output_file = f"/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/auto_generated_{model.name}_tools.py"
            with open(output_file, 'w') as f:
                f.write(result['python_code'])
            
            print(f"\nGenerated Python code saved to: {output_file}")
        else:
            print("Failed to analyze YANG model")
    else:
        print(f"YANG file not found: {yang_file}")

if __name__ == "__main__":
    main()
