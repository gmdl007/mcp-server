#!/usr/bin/env python3
"""
MCP Client for NSO Tools
Uses standard MCP client to connect to LlamaIndex NSO MCP Server
"""

import asyncio
import json
import logging
from typing import Any, Dict

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_client():
    """Test MCP client connection to NSO server."""
    
    # Server parameters - this should match your MCP server
    server_params = StdioServerParameters(
        command="/Users/gudeng/MCP_Server/src/mcp_server/start_llama_index_nso_mcp.sh",
        args=[],
        env={
            "NCS_DIR": "/Users/gudeng/NCS-614",
            "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
        }
    )
    
    print("🔧 Testing MCP Client Connection")
    print("="*50)
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                print("✅ Connected to MCP server!")
                
                # List available tools
                tools_result = await session.list_tools()
                print(f"\n📋 Available tools ({len(tools_result.tools)}):")
                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # Test echo_text tool
                print("\n1. Testing echo_text:")
                try:
                    result = await session.call_tool("echo_text", {"text": "Hello from MCP client!"})
                    print(f"   Result: {result.content[0].text}")
                except Exception as e:
                    print(f"   Error: {e}")
                
                # Test show_all_devices tool
                print("\n2. Testing show_all_devices:")
                try:
                    result = await session.call_tool("show_all_devices", {})
                    print(f"   Result: {result.content[0].text}")
                except Exception as e:
                    print(f"   Error: {e}")
                
                # Test get_router_interfaces_config tool
                print("\n3. Testing get_router_interfaces_config:")
                try:
                    result = await session.call_tool("get_router_interfaces_config", {"router_name": "xr9kv-3"})
                    print(f"   Result: {result.content[0].text}")
                except Exception as e:
                    print(f"   Error: {e}")
                
                print("\n✅ MCP client test completed!")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
