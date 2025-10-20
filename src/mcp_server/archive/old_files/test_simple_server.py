#!/usr/bin/env python3
"""
Test Simple MCP Server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_simple_server():
    """Test the simple MCP server."""
    
    server_params = StdioServerParameters(
        command="python",
        args=["/Users/gudeng/MCP_Server/src/mcp_server/simple_mcp_test.py"],
        env={}
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("✅ Connected to Simple MCP Server!")
                
                # Test list_tools
                print("\n📋 Testing list_tools:")
                tools_result = await session.list_tools()
                print(f"Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    print(f"  • {tool.name}: {tool.description}")
                
                # Test echo tool
                print("\n🔧 Testing echo tool:")
                result = await session.call_tool("echo", {"text": "Hello Simple MCP!"})
                print(f"Raw result: {result}")
                print(f"Content: {result.content}")
                if result.content:
                    print(f"Text: {result.content[0].text}")
                
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_simple_server())
