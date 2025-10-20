#!/usr/bin/env python3
"""
Simple MCP Tool Call Test
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_simple_call():
    """Test a simple MCP tool call."""
    
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
                
                # Test echo_text
                print("\n🔧 Testing echo_text:")
                result = await session.call_tool("echo_text", {"text": "Hello MCP!"})
                print(f"Raw result: {result}")
                print(f"Result type: {type(result)}")
                print(f"Content: {result.content}")
                if result.content:
                    print(f"First content: {result.content[0]}")
                    print(f"First content type: {type(result.content[0])}")
                    if hasattr(result.content[0], 'text'):
                        print(f"Text: {result.content[0].text}")
                
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_simple_call())
