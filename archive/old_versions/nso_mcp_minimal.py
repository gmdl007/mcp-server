#!/usr/bin/env python3
"""
NSO MCP Server - Minimal Version for Cursor
===========================================

A minimal MCP server that should work reliably with Cursor's MCP integration.

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

# MCP Server imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

# NSO Configuration
NSO_DIR = "/Users/gudeng/NCS-614"
NSO_USERNAME = "admin"
NSO_PASSWORD = "admin"

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
        m.start_user_session(NSO_USERNAME, 'mcp_session')
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
# NSO FUNCTION TOOLS FOR MCP
# =============================================================================

class NSOMCPTools:
    """NSO function tools adapted for MCP server."""
    
    def __init__(self, root=None):
        self.root = root
        self.connected = root is not None
    
    def show_all_devices(self) -> str:
        """Find out all available routers in the lab, return their names."""
        if not self.connected:
            return "❌ NSO not connected. Please check NSO status."
        
        if hasattr(self.root, 'devices') and hasattr(self.root.devices, 'device'):
            router_names = [device.name for device in self.root.devices.device]
            return ', '.join(router_names)
        else:
            return "No devices found."
    
    def execute_command_on_router(self, router_name: str, command: str) -> str:
        """Execute a single command on a specific router using NSO."""
        if not self.connected:
            return "❌ NSO not connected. Please check NSO status."
        
        try:
            import ncs.maapi as maapi
            import ncs.maagic as maagic
            
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
        if not self.connected:
            return "❌ NSO not connected. Please check NSO status."
        
        results = []
        try:
            import ncs.maapi as maapi
            import ncs.maagic as maagic
            
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
# MCP SERVER IMPLEMENTATION
# =============================================================================

# Global NSO tools instance
nso_tools = None

# Create MCP server
server = Server("nso-mcp-server")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List all available NSO tools."""
    tools = [
        Tool(
            name="show_all_devices",
            description="Find out all available routers in the lab, return their names.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_router_version",
            description="Retrieve router version using 'show version' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="get_router_clock",
            description="Retrieve router current time using 'show clock' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="show_router_interfaces",
            description="Retrieve router interface status using 'show ipv4 interface brief' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="get_router_bgp_summary",
            description="Retrieve BGP summary using 'show bgp ipv4 unicast summary' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="get_router_isis_neighbors",
            description="Retrieve ISIS neighbors using 'show isis neighbors' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="get_router_ospf_neigh",
            description="Retrieve OSPF neighbors using 'show ospf neighbor' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="check_cpu",
            description="Retrieve CPU utilization using 'show processes cpu sorted 5min' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="check_memory",
            description="Retrieve memory summary using 'show memory summary' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="ping_router",
            description="Ping an IP address from a router.",
            inputSchema={
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
        ),
        Tool(
            name="traceroute_router",
            description="Perform traceroute to an IP address from a router.",
            inputSchema={
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
        ),
        Tool(
            name="lldp_nei",
            description="Find connected neighbors using 'show lldp neighbor' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="check_alarm",
            description="Retrieve router alarm information using 'show alarms brief' command.",
            inputSchema={
                "type": "object",
                "properties": {
                    "router_name": {
                        "type": "string",
                        "description": "Name of the router to query"
                    }
                },
                "required": ["router_name"]
            }
        ),
        Tool(
            name="iterate",
            description="Execute a command on all devices.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "Command to execute on all devices"
                    }
                },
                "required": ["cmd"]
            }
        )
    ]
    
    return ListToolsResult(tools=tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    global nso_tools
    
    if not nso_tools:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="❌ NSO tools not initialized. Please check NSO connection."
            )]
        )
    
    try:
        # Route tool calls to appropriate NSO functions
        if name == "show_all_devices":
            result = nso_tools.show_all_devices()
        elif name == "get_router_version":
            result = nso_tools.get_router_version(arguments["router_name"])
        elif name == "get_router_clock":
            result = nso_tools.get_router_clock(arguments["router_name"])
        elif name == "show_router_interfaces":
            result = nso_tools.show_router_interfaces(arguments["router_name"])
        elif name == "get_router_bgp_summary":
            result = nso_tools.get_router_bgp_summary(arguments["router_name"])
        elif name == "get_router_isis_neighbors":
            result = nso_tools.get_router_isis_neighbors(arguments["router_name"])
        elif name == "get_router_ospf_neigh":
            result = nso_tools.get_router_ospf_neigh(arguments["router_name"])
        elif name == "check_cpu":
            result = nso_tools.check_cpu(arguments["router_name"])
        elif name == "check_memory":
            result = nso_tools.check_memory(arguments["router_name"])
        elif name == "ping_router":
            result = nso_tools.ping_router(arguments["router_name"], arguments["ip_address"])
        elif name == "traceroute_router":
            result = nso_tools.traceroute_router(arguments["router_name"], arguments["ip_address"])
        elif name == "lldp_nei":
            result = nso_tools.lldp_nei(arguments["router_name"])
        elif name == "check_alarm":
            result = nso_tools.check_alarm(arguments["router_name"])
        elif name == "iterate":
            result = nso_tools.iterate(arguments["cmd"])
        else:
            result = f"❌ Unknown tool: {name}"
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=result
            )]
        )
        
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"❌ Error executing tool {name}: {str(e)}"
            )]
        )

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for the NSO MCP Server."""
    global nso_tools
    
    logger.info("🚀 Starting NSO MCP Server for Cursor...")
    
    # Setup NSO environment
    if not setup_nso_environment():
        logger.error("❌ Failed to setup NSO environment")
        return
    
    # Try to setup NSO connection
    m, t, root = setup_nso_connection()
    if root:
        # Initialize NSO tools with connection
        nso_tools = NSOMCPTools(root)
        logger.info("✅ NSO MCP Server initialized successfully")
    else:
        # Initialize NSO tools without connection
        nso_tools = NSOMCPTools()
        logger.warning("⚠️ NSO MCP Server initialized without NSO connection")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nso-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())

