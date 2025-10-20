#!/usr/bin/env python3
"""
Simple LlamaIndex MCP Client Demo
Shows how to use LlamaIndex MCP tools directly
"""

import asyncio
import logging
from llama_index.mcp import McpTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_mcp_tools():
    """Demonstrate using MCP tools directly."""
    
    # Create MCP tool instances
    echo_tool = McpTool(
        name="echo_text",
        description="Echo back the provided text",
        mcp_server_name="nso-network-automation"
    )
    
    devices_tool = McpTool(
        name="show_all_devices", 
        description="Get all available routers",
        mcp_server_name="nso-network-automation"
    )
    
    interfaces_tool = McpTool(
        name="get_router_interfaces_config",
        description="Get interface config for a router", 
        mcp_server_name="nso-network-automation"
    )
    
    print("🔧 Testing MCP Tools Directly")
    print("="*50)
    
    try:
        # Test echo tool
        print("\n1. Testing echo_text:")
        result1 = await echo_tool.acall(text="Hello from LlamaIndex!")
        print(f"   Result: {result1}")
        
        # Test devices tool
        print("\n2. Testing show_all_devices:")
        result2 = await devices_tool.acall()
        print(f"   Result: {result2}")
        
        # Test interfaces tool
        print("\n3. Testing get_router_interfaces_config:")
        result3 = await interfaces_tool.acall(router_name="xr9kv-3")
        print(f"   Result: {result3}")
        
        print("\n✅ All MCP tools working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(demo_mcp_tools())
