#!/usr/bin/env python3
"""
Test LlamaIndex NSO MCP Server
Tests the new LlamaIndex-based MCP server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_llama_index_mcp_server():
    """Test the LlamaIndex NSO MCP server."""
    
    server_params = StdioServerParameters(
        command="/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/start_llama_index_nso_mcp.sh",
        args=[],
        env={
            "NCS_DIR": "/Users/gudeng/NCS-614",
            "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
        }
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("✅ Connected to LlamaIndex NSO MCP Server!")
                
                # Test list_tools
                print("\n📋 Testing list_tools:")
                tools_result = await session.list_tools()
                print(f"Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    print(f"  • {tool.name}: {tool.description}")
                
                # Test echo_text tool
                print("\n🔧 Testing echo_text:")
                result = await session.call_tool("echo_text", {"text": "Hello LlamaIndex MCP!"})
                print(f"Result: {result.content[0].text}")
                
                # Test show_all_devices tool
                print("\n🔧 Testing show_all_devices:")
                result = await session.call_tool("show_all_devices", {})
                print(f"Result: {result.content[0].text}")
                
                # Test get_router_interfaces_config tool
                print("\n🔧 Testing get_router_interfaces_config:")
                result = await session.call_tool("get_router_interfaces_config", {"router_name": "xr9kv-3"})
                print(f"Result: {result.content[0].text}")
                
                print("\n✅ All tests completed successfully!")
                print("🎉 LlamaIndex NSO MCP Server is working!")
                
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_llama_index_mcp_server())
