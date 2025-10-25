#!/usr/bin/env python3
"""
OSPF Service Tool Generator

This module generates comprehensive MCP tools for OSPF service management
based on the actual NSO OSPF service model structure.
"""

import ncs.maapi as maapi
import ncs.maagic as maagic
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def generate_ospf_service_tools():
    """Generate comprehensive OSPF service MCP tools."""
    
    # OSPF Service Configuration Parameters (based on runtime analysis)
    ospf_parameters = [
        {
            'name': 'router_id',
            'type': 'string',
            'description': 'OSPF Router ID in IPv4 format (e.g., 1.1.1.1)',
            'required': True,
            'example': '1.1.1.1'
        },
        {
            'name': 'area',
            'type': 'string', 
            'description': 'OSPF Area ID (e.g., 0, 1, 2)',
            'required': True,
            'default': '0',
            'example': '0'
        }
    ]
    
    # OSPF Neighbor Parameters (based on runtime analysis)
    neighbor_parameters = [
        {
            'name': 'neighbor_ip',
            'type': 'string',
            'description': 'Neighbor IP address',
            'required': True,
            'example': '192.168.1.2'
        },
        {
            'name': 'neighbor_area',
            'type': 'string',
            'description': 'Neighbor area ID',
            'required': True,
            'example': '0'
        }
    ]
    
    tools = []
    
    # 1. Get OSPF Service Configuration
    tools.append({
        'name': 'get_ospf_service_config',
        'description': 'Get OSPF service configuration for a router or all routers',
        'parameters': [
            {
                'name': 'router_name',
                'type': 'string',
                'description': 'Router name to get OSPF config for (optional - shows all if not specified)',
                'required': False,
                'example': 'xr9kv-1'
            }
        ],
        'function_name': 'get_ospf_service_config'
    })
    
    # 2. Create OSPF Service Instance
    tools.append({
        'name': 'create_ospf_service',
        'description': 'Create OSPF service instance for a router',
        'parameters': [
            {
                'name': 'router_name',
                'type': 'string',
                'description': 'Router name to create OSPF service for',
                'required': True,
                'example': 'xr9kv-1'
            }
        ] + ospf_parameters,
        'function_name': 'create_ospf_service'
    })
    
    # 3. Update OSPF Service Configuration
    tools.append({
        'name': 'update_ospf_service',
        'description': 'Update OSPF service configuration for a router',
        'parameters': [
            {
                'name': 'router_name',
                'type': 'string',
                'description': 'Router name to update OSPF service for',
                'required': True,
                'example': 'xr9kv-1'
            }
        ] + ospf_parameters,
        'function_name': 'update_ospf_service'
    })
    
    # 4. Delete OSPF Service Instance
    tools.append({
        'name': 'delete_ospf_service',
        'description': 'Delete OSPF service instance for a router',
        'parameters': [
            {
                'name': 'router_name',
                'type': 'string',
                'description': 'Router name to delete OSPF service for',
                'required': True,
                'example': 'xr9kv-1'
            },
            {
                'name': 'confirm',
                'type': 'boolean',
                'description': 'Confirmation flag for deletion (must be True)',
                'required': True,
                'default': False
            }
        ],
        'function_name': 'delete_ospf_service'
    })
    
    # 5. Add OSPF Neighbor
    tools.append({
        'name': 'add_ospf_neighbor',
        'description': 'Add OSPF neighbor to a router\'s service',
        'parameters': [
            {
                'name': 'router_name',
                'type': 'string',
                'description': 'Router name to add neighbor to',
                'required': True,
                'example': 'xr9kv-1'
            }
        ] + neighbor_parameters,
        'function_name': 'add_ospf_neighbor'
    })
    
    # 6. Remove OSPF Neighbor
    tools.append({
        'name': 'remove_ospf_neighbor',
        'description': 'Remove OSPF neighbor from a router\'s service',
        'parameters': [
            {
                'name': 'router_name',
                'type': 'string',
                'description': 'Router name to remove neighbor from',
                'required': True,
                'example': 'xr9kv-1'
            },
            {
                'name': 'neighbor_ip',
                'type': 'string',
                'description': 'Neighbor IP address to remove',
                'required': True,
                'example': '192.168.1.2'
            },
            {
                'name': 'confirm',
                'type': 'boolean',
                'description': 'Confirmation flag for removal (must be True)',
                'required': True,
                'default': False
            }
        ],
        'function_name': 'remove_ospf_neighbor'
    })
    
    # 7. List OSPF Neighbors
    tools.append({
        'name': 'list_ospf_neighbors',
        'description': 'List OSPF neighbors for a router',
        'parameters': [
            {
                'name': 'router_name',
                'type': 'string',
                'description': 'Router name to list neighbors for',
                'required': True,
                'example': 'xr9kv-1'
            }
        ],
        'function_name': 'list_ospf_neighbors'
    })
    
    # 8. Get OSPF Service Status
    tools.append({
        'name': 'get_ospf_service_status',
        'description': 'Get OSPF service status and operational information',
        'parameters': [
            {
                'name': 'router_name',
                'type': 'string',
                'description': 'Router name to get status for',
                'required': True,
                'example': 'xr9kv-1'
            }
        ],
        'function_name': 'get_ospf_service_status'
    })
    
    return tools

def generate_python_code_for_ospf_tools(tools: List[Dict[str, Any]]) -> str:
    """Generate Python code for OSPF service MCP tools."""
    
    code_lines = [
        "# Auto-generated OSPF Service MCP Tools",
        "# Generated based on NSO OSPF service model analysis",
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
            example = f" (e.g., {param['example']})" if param.get('example') else ""
            code_lines.append(f'        {param["name"]}: {param["description"]} ({required}){example}')
        
        code_lines.extend([
            f'    ',
            f'    Returns:',
            f'        str: Detailed result message',
            f'    """',
            f'    try:',
            f'        logger.info(f"🔧 {description}")',
            f'        ',
            f'        m = maapi.Maapi()',
            f'        m.start_user_session(\'cisco\', \'test_context_1\')',
            f'        ',
            f'        # TODO: Implement actual {function_name} logic',
            f'        # This is a template - implement based on actual OSPF service model',
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
    """Main function to generate OSPF service tools."""
    print("Generating OSPF Service MCP Tools...")
    print("=" * 50)
    
    # Generate tools
    tools = generate_ospf_service_tools()
    
    print(f"Generated {len(tools)} OSPF service tools:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
        print(f"    Parameters: {len(tool['parameters'])}")
    
    # Generate Python code
    python_code = generate_python_code_for_ospf_tools(tools)
    
    # Save to file
    output_file = "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/auto_generated_ospf_tools.py"
    with open(output_file, 'w') as f:
        f.write(python_code)
    
    print(f"\nGenerated Python code saved to: {output_file}")
    
    return tools

if __name__ == "__main__":
    main()
