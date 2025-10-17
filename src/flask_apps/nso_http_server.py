#!/usr/bin/env python3
"""
NSO HTTP Server for MCP-like Interface
======================================

A simple HTTP server that exposes NSO network automation capabilities
in a format similar to MCP, making it easy to test and connect to.

Author: AI Assistant
Version: 1.0
Date: 2025-01-16
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

# HTTP server imports
from quart import Quart, request, jsonify
import nest_asyncio

# NSO imports
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# =============================================================================
# CONFIGURATION
# =============================================================================

# NSO Configuration
NSO_DIR = "/Users/gudeng/NCS-614"
NSO_USERNAME = "admin"
NSO_PASSWORD = "admin"

# HTTP Server Configuration
HTTP_HOST = "0.0.0.0"
HTTP_PORT = 5607

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# NSO ENVIRONMENT SETUP
# =============================================================================

def setup_nso_environment():
    """Setup NSO environment variables and Python path."""
    try:
        # Set NSO environment variables
        os.environ['NCS_DIR'] = NSO_DIR
        os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
        os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
        
        # Add NSO Python API to Python path
        nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
        if nso_pyapi_path not in sys.path:
            sys.path.insert(0, nso_pyapi_path)
        
        logger.info(f"✅ NSO environment configured: {NSO_DIR}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to setup NSO environment: {e}")
        return False

def setup_nso_connection():
    """Setup NSO connection and return connection objects."""
    try:
        # Import NSO modules
        import ncs
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        
        logger.info("✅ NSO modules imported successfully")
        
        # Create NSO connection
        m = maapi.Maapi()
        m.start_user_session(NSO_USERNAME, 'http_session')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        logger.info("✅ NSO connection established successfully")
        
        # Test device discovery
        devices = []
        for device in root.devices.device:
            devices.append(device.name)
        
        logger.info(f"📱 Found {len(devices)} devices: {devices}")
        
        return m, t, root
        
    except Exception as e:
        logger.error(f"❌ Failed to setup NSO connection: {e}")
        return None, None, None

# =============================================================================
# NSO FUNCTION TOOLS FOR HTTP
# =============================================================================

class NSOHTTPTools:
    """NSO function tools adapted for HTTP server."""
    
    def __init__(self, root):
        self.root = root
    
    def show_all_devices(self) -> str:
        """Find out all available routers in the lab, return their names."""
        if hasattr(self.root, 'devices') and hasattr(self.root.devices, 'device'):
            router_names = [device.name for device in self.root.devices.device]
            return ', '.join(router_names)
        else:
            return "No devices found."
    
    def execute_command_on_router(self, router_name: str, command: str) -> str:
        """Execute a single command on a specific router using NSO."""
        try:
            with maapi.single_write_trans(NSO_USERNAME, 'python', groups=['ncsadmin']) as t:
                root = maagic.get_root(t)
                device = root.devices.device[router_name]
                show = device.live_status.__getitem__('exec').any
                inp = show.get_input()
                inp.args = [command]
                r = show.request(inp)
                result = f'Result of Show Command "{command}" for Router "{router_name}": {r.result}'
                return result
                
        except KeyError:
            return f"Device '{router_name}' not found in NSO."
        except Exception as e:
            return f"Failed to execute command '{command}' on device '{router_name}': {e}"
    
    def get_router_version(self, router_name: str) -> str:
        """Retrieve router version using 'show version' command."""
        return self.execute_command_on_router(router_name, "show version")
    
    def get_router_clock(self, router_name: str) -> str:
        """Retrieve router current time using 'show clock' command."""
        return self.execute_command_on_router(router_name, "show clock")
    
    def show_router_interfaces(self, router_name: str) -> str:
        """Retrieve router interface status using 'show ipv4 interface brief' command."""
        return self.execute_command_on_router(router_name, "show ipv4 interface brief")
    
    def get_router_bgp_summary(self, router_name: str) -> str:
        """Retrieve BGP summary using 'show bgp ipv4 unicast summary' command."""
        return self.execute_command_on_router(router_name, "show bgp ipv4 unicast summary")
    
    def get_router_isis_neighbors(self, router_name: str) -> str:
        """Retrieve ISIS neighbors using 'show isis neighbors' command."""
        return self.execute_command_on_router(router_name, "show isis neighbors")
    
    def get_router_ospf_neigh(self, router_name: str) -> str:
        """Retrieve OSPF neighbors using 'show ospf neighbor' command."""
        return self.execute_command_on_router(router_name, "show ospf neighbor")
    
    def check_cpu(self, router_name: str) -> str:
        """Retrieve CPU utilization using 'show processes cpu sorted 5min' command."""
        return self.execute_command_on_router(router_name, "show processes cpu sorted 5min")
    
    def check_memory(self, router_name: str) -> str:
        """Retrieve memory summary using 'show memory summary' command."""
        return self.execute_command_on_router(router_name, "show memory summary")
    
    def ping_router(self, router_name: str, ip_address: str) -> str:
        """Ping an IP address from a router."""
        command = f"ping {ip_address} source Loopback 0"
        return self.execute_command_on_router(router_name, command)
    
    def traceroute_router(self, router_name: str, ip_address: str) -> str:
        """Perform traceroute to an IP address from a router."""
        command = f"traceroute {ip_address} source Loopback 0"
        return self.execute_command_on_router(router_name, command)
    
    def lldp_nei(self, router_name: str) -> str:
        """Find connected neighbors using 'show lldp neighbor' command."""
        return self.execute_command_on_router(router_name, "show lldp neighbor")
    
    def check_alarm(self, router_name: str) -> str:
        """Retrieve router alarm information using 'show alarms brief' command."""
        return self.execute_command_on_router(router_name, "show alarms brief")
    
    def iterate(self, cmd: str) -> str:
        """Execute a command on all devices."""
        results = []
        try:
            with maapi.single_write_trans(NSO_USERNAME, 'python', groups=['ncsadmin']) as t:
                root = maagic.get_root(t)
                for box in root.devices.device:
                    try:
                        show = box.live_status.__getitem__('exec').any
                        inp = show.get_input()
                        inp.args = [cmd]
                        r = show.request(inp)
                        show_cmd = f'Result of Show Command "{cmd}" for Router Name {box.name}: {r.result}'
                        results.append(show_cmd)
                    except Exception as e:
                        results.append(f"Failed to execute command '{cmd}' on device {box.name}: {e}")
        except Exception as e:
            results.append(f"Failed to iterate command '{cmd}': {e}")
        
        return '\n'.join(results)

# =============================================================================
# HTTP SERVER IMPLEMENTATION
# =============================================================================

# Global NSO tools instance
nso_tools = None

# Create Quart app
app = Quart(__name__)

@app.route('/')
async def index():
    """Home page with server information."""
    return jsonify({
        "service": "NSO HTTP Server",
        "version": "1.0.0",
        "description": "HTTP server exposing NSO network automation capabilities",
        "endpoints": {
            "/health": "Health check endpoint",
            "/tools": "List all available tools",
            "/tools/<tool_name>": "Execute a specific tool",
            "/mcp/tools/list": "MCP-compatible tools list",
            "/mcp/tools/call": "MCP-compatible tool execution"
        },
        "nso_connected": nso_tools is not None
    })

@app.route('/health')
async def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "nso-http-server",
        "version": "1.0.0",
        "nso_connected": nso_tools is not None
    })

@app.route('/tools')
async def list_tools():
    """List all available tools."""
    tools = [
        {
            "name": "show_all_devices",
            "description": "Find out all available routers in the lab, return their names.",
            "parameters": {}
        },
        {
            "name": "get_router_version",
            "description": "Retrieve router version using 'show version' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "get_router_clock",
            "description": "Retrieve router current time using 'show clock' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "show_router_interfaces",
            "description": "Retrieve router interface status using 'show ipv4 interface brief' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "get_router_bgp_summary",
            "description": "Retrieve BGP summary using 'show bgp ipv4 unicast summary' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "get_router_isis_neighbors",
            "description": "Retrieve ISIS neighbors using 'show isis neighbors' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "get_router_ospf_neigh",
            "description": "Retrieve OSPF neighbors using 'show ospf neighbor' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "check_cpu",
            "description": "Retrieve CPU utilization using 'show processes cpu sorted 5min' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "check_memory",
            "description": "Retrieve memory summary using 'show memory summary' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "ping_router",
            "description": "Ping an IP address from a router.",
            "parameters": {
                "router_name": "string - Name of the router to ping from",
                "ip_address": "string - IP address to ping"
            }
        },
        {
            "name": "traceroute_router",
            "description": "Perform traceroute to an IP address from a router.",
            "parameters": {
                "router_name": "string - Name of the router to traceroute from",
                "ip_address": "string - IP address to traceroute to"
            }
        },
        {
            "name": "lldp_nei",
            "description": "Find connected neighbors using 'show lldp neighbor' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "check_alarm",
            "description": "Retrieve router alarm information using 'show alarms brief' command.",
            "parameters": {
                "router_name": "string - Name of the router to query"
            }
        },
        {
            "name": "iterate",
            "description": "Execute a command on all devices.",
            "parameters": {
                "cmd": "string - Command to execute on all devices"
            }
        }
    ]
    
    return jsonify({
        "tools": tools,
        "count": len(tools)
    })

@app.route('/tools/<tool_name>', methods=['POST'])
async def execute_tool(tool_name: str):
    """Execute a specific tool."""
    global nso_tools
    
    if not nso_tools:
        return jsonify({
            "error": "NSO tools not initialized. Please check NSO connection."
        }), 500
    
    try:
        data = await request.get_json()
        arguments = data.get('arguments', {})
        
        # Route tool calls to appropriate NSO functions
        if tool_name == "show_all_devices":
            result = nso_tools.show_all_devices()
        elif tool_name == "get_router_version":
            result = nso_tools.get_router_version(arguments["router_name"])
        elif tool_name == "get_router_clock":
            result = nso_tools.get_router_clock(arguments["router_name"])
        elif tool_name == "show_router_interfaces":
            result = nso_tools.show_router_interfaces(arguments["router_name"])
        elif tool_name == "get_router_bgp_summary":
            result = nso_tools.get_router_bgp_summary(arguments["router_name"])
        elif tool_name == "get_router_isis_neighbors":
            result = nso_tools.get_router_isis_neighbors(arguments["router_name"])
        elif tool_name == "get_router_ospf_neigh":
            result = nso_tools.get_router_ospf_neigh(arguments["router_name"])
        elif tool_name == "check_cpu":
            result = nso_tools.check_cpu(arguments["router_name"])
        elif tool_name == "check_memory":
            result = nso_tools.check_memory(arguments["router_name"])
        elif tool_name == "ping_router":
            result = nso_tools.ping_router(arguments["router_name"], arguments["ip_address"])
        elif tool_name == "traceroute_router":
            result = nso_tools.traceroute_router(arguments["router_name"], arguments["ip_address"])
        elif tool_name == "lldp_nei":
            result = nso_tools.lldp_nei(arguments["router_name"])
        elif tool_name == "check_alarm":
            result = nso_tools.check_alarm(arguments["router_name"])
        elif tool_name == "iterate":
            result = nso_tools.iterate(arguments["cmd"])
        else:
            return jsonify({
                "error": f"Unknown tool: {tool_name}"
            }), 400
        
        return jsonify({
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
            "success": True
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error executing tool {tool_name}: {str(e)}",
            "success": False
        }), 500

# MCP-compatible endpoints
@app.route('/mcp/tools/list')
async def mcp_list_tools():
    """MCP-compatible tools list endpoint."""
    tools = [
        {
            "name": "show_all_devices",
            "description": "Find out all available routers in the lab, return their names.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_router_version",
            "description": "Retrieve router version using 'show version' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "get_router_clock",
            "description": "Retrieve router current time using 'show clock' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "show_router_interfaces",
            "description": "Retrieve router interface status using 'show ipv4 interface brief' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "get_router_bgp_summary",
            "description": "Retrieve BGP summary using 'show bgp ipv4 unicast summary' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "get_router_isis_neighbors",
            "description": "Retrieve ISIS neighbors using 'show isis neighbors' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "get_router_ospf_neigh",
            "description": "Retrieve OSPF neighbors using 'show ospf neighbor' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "check_cpu",
            "description": "Retrieve CPU utilization using 'show processes cpu sorted 5min' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "check_memory",
            "description": "Retrieve memory summary using 'show memory summary' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "ping_router",
            "description": "Ping an IP address from a router.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to ping from"
                    },
                    "ip_address": {
                        "type": "string",
                        "description": "IP address to ping"
                    }
                },
                "required": ["router_name", "ip_address"]
            }
        },
        {
            "name": "traceroute_router",
            "description": "Perform traceroute to an IP address from a router.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to traceroute from"
                    },
                    "ip_address": {
                        "type": "string",
                        "description": "IP address to traceroute to"
                    }
                },
                "required": ["router_name", "ip_address"]
            }
        },
        {
            "name": "lldp_nei",
            "description": "Find connected neighbors using 'show lldp neighbor' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "check_alarm",
            "description": "Retrieve router alarm information using 'show alarms brief' command.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        },
        {
            "name": "iterate",
            "description": "Execute a command on all devices.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "Command to execute on all devices"
                    }
                },
                "required": ["cmd"]
            }
        }
    ]
    
    return jsonify({
        "tools": tools
    })

@app.route('/mcp/tools/call', methods=['POST'])
async def mcp_call_tool():
    """MCP-compatible tool execution endpoint."""
    global nso_tools
    
    if not nso_tools:
        return jsonify({
            "error": "NSO tools not initialized. Please check NSO connection."
        }), 500
    
    try:
        data = await request.get_json()
        tool_name = data.get('name')
        arguments = data.get('arguments', {})
        
        # Route tool calls to appropriate NSO functions
        if tool_name == "show_all_devices":
            result = nso_tools.show_all_devices()
        elif tool_name == "get_router_version":
            result = nso_tools.get_router_version(arguments["router_name"])
        elif tool_name == "get_router_clock":
            result = nso_tools.get_router_clock(arguments["router_name"])
        elif tool_name == "show_router_interfaces":
            result = nso_tools.show_router_interfaces(arguments["router_name"])
        elif tool_name == "get_router_bgp_summary":
            result = nso_tools.get_router_bgp_summary(arguments["router_name"])
        elif tool_name == "get_router_isis_neighbors":
            result = nso_tools.get_router_isis_neighbors(arguments["router_name"])
        elif tool_name == "get_router_ospf_neigh":
            result = nso_tools.get_router_ospf_neigh(arguments["router_name"])
        elif tool_name == "check_cpu":
            result = nso_tools.check_cpu(arguments["router_name"])
        elif tool_name == "check_memory":
            result = nso_tools.check_memory(arguments["router_name"])
        elif tool_name == "ping_router":
            result = nso_tools.ping_router(arguments["router_name"], arguments["ip_address"])
        elif tool_name == "traceroute_router":
            result = nso_tools.traceroute_router(arguments["router_name"], arguments["ip_address"])
        elif tool_name == "lldp_nei":
            result = nso_tools.lldp_nei(arguments["router_name"])
        elif tool_name == "check_alarm":
            result = nso_tools.check_alarm(arguments["router_name"])
        elif tool_name == "iterate":
            result = nso_tools.iterate(arguments["cmd"])
        else:
            return jsonify({
                "error": f"Unknown tool: {tool_name}"
            }), 400
        
        return jsonify({
            "content": [
                {
                    "type": "text",
                    "text": result
                }
            ]
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error executing tool {tool_name}: {str(e)}"
        }), 500

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for the NSO HTTP Server."""
    global nso_tools
    
    logger.info("🚀 Starting NSO HTTP Server...")
    
    # Setup NSO environment
    if not setup_nso_environment():
        logger.error("❌ Failed to setup NSO environment")
        return
    
    # Setup NSO connection
    m, t, root = setup_nso_connection()
    if not root:
        logger.error("❌ Failed to setup NSO connection")
        return
    
    # Initialize NSO tools
    nso_tools = NSOHTTPTools(root)
    logger.info("✅ NSO HTTP Server initialized successfully")
    
    # Start the server
    logger.info("=" * 60)
    logger.info("🎉 NSO HTTP Server Started Successfully!")
    logger.info(f"🌐 HTTP Interface: http://{HTTP_HOST}:{HTTP_PORT}")
    logger.info(f"🔍 Health Check: http://{HTTP_HOST}:{HTTP_PORT}/health")
    logger.info(f"📋 Tools List: http://{HTTP_HOST}:{HTTP_PORT}/tools")
    logger.info(f"🔧 MCP Tools: http://{HTTP_HOST}:{HTTP_PORT}/mcp/tools/list")
    logger.info("🔒 Press CTRL+C to stop")
    logger.info("=" * 60)
    
    # Run the Quart application
    await app.run_task(host=HTTP_HOST, port=HTTP_PORT, debug=False)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
