#!/usr/bin/env python3
"""
Simple MCP Test with Debug
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_debug():
    """Test MCP with debug output."""
    
    server_params = StdioServerParameters(
        command="/Users/gudeng/MCP_Server/src/mcp_server/start_llama_index_nso_mcp.sh",
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
                
                # Test list_tools to see debug output
                print("\n📋 Testing list_tools:")
                tools_result = await session.list_tools()
                
                print(f"Found {len(tools_result.tools)} tools:")
                for tool in tools_result.tools:
                    print(f"  • {tool.name}: {tool.description}")
                    print(f"    Schema: {tool.inputSchema}")
                
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_debug())
