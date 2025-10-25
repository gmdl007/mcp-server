#!/usr/bin/env python3
"""
Test Auto-Generated FastMCP NSO Tools

This script tests the automatically generated tools from YANG model analysis.
"""

import asyncio
import sys
import os
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

async def test_auto_generated_tools():
    """Test the auto-generated tools."""
    
    print("🧪 Testing Auto-Generated FastMCP NSO Tools")
    print("=" * 60)
    
    try:
        # Connect to the auto-generated tools server
        print("🔌 Connecting to auto-generated tools server...")
        mcp_client = BasicMCPClient(
            "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/start_fastmcp_nso_server_auto_generated.sh",
            args=[]
        )
        
        # List available tools
        print("\n📋 Available Auto-Generated Tools:")
        tools = await mcp_client.list_tools()
        
        tool_names = []
        for tool in tools:
            if isinstance(tool, tuple):
                tool_name = tool[0] if len(tool) > 0 else "unknown"
                tool_description = tool[1] if len(tool) > 1 else "No description"
            else:
                tool_name = getattr(tool, 'name', 'unknown')
                tool_description = getattr(tool, 'description', 'No description')
            tool_names.append(tool_name)
            print(f"  - {tool_name}: {tool_description}")
        
        print(f"\n✅ Found {len(tool_names)} auto-generated tools")
        
        # Test basic tools
        print("\n🔧 Testing Basic Tools:")
        
        # Test echo_text
        print("\n1. Testing echo_text:")
        try:
            result = await mcp_client.call_tool("echo_text", {"text": "Hello Auto-Generated Tools!"})
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test show_all_devices
        print("\n2. Testing show_all_devices:")
        try:
            result = await mcp_client.call_tool("show_all_devices", {})
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test OSPF Service Tools
        print("\n🔧 Testing OSPF Service Tools:")
        
        # Test get_ospf_service_config
        print("\n3. Testing get_ospf_service_config:")
        try:
            result = await mcp_client.call_tool("get_ospf_service_config", {"router_name": "xr9kv-1"})
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test create_ospf_service
        print("\n4. Testing create_ospf_service:")
        try:
            result = await mcp_client.call_tool("create_ospf_service", {
                "router_name": "xr9kv-1",
                "router_id": "1.1.1.1",
                "area": "0"
            })
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test get_ospf_service_status
        print("\n5. Testing get_ospf_service_status:")
        try:
            result = await mcp_client.call_tool("get_ospf_service_status", {"router_name": "xr9kv-1"})
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test add_ospf_neighbor
        print("\n6. Testing add_ospf_neighbor:")
        try:
            result = await mcp_client.call_tool("add_ospf_neighbor", {
                "router_name": "xr9kv-1",
                "neighbor_ip": "192.168.1.2",
                "neighbor_area": "0"
            })
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test list_ospf_neighbors
        print("\n7. Testing list_ospf_neighbors:")
        try:
            result = await mcp_client.call_tool("list_ospf_neighbors", {"router_name": "xr9kv-1"})
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test NSO Runtime Service Tools
        print("\n🔧 Testing NSO Runtime Service Tools:")
        
        # Test get_BGP_GRP__BGP_GRP_config
        print("\n8. Testing get_BGP_GRP__BGP_GRP_config:")
        try:
            result = await mcp_client.call_tool("get_BGP_GRP__BGP_GRP_config", {"router_name": "xr9kv-1"})
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test create_BGP_GRP__BGP_GRP_service
        print("\n9. Testing create_BGP_GRP__BGP_GRP_service:")
        try:
            result = await mcp_client.call_tool("create_BGP_GRP__BGP_GRP_service", {"router_name": "xr9kv-1"})
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n🎉 Auto-Generated Tools Testing Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error testing auto-generated tools: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    print("Starting auto-generated tools test...")
    asyncio.run(test_auto_generated_tools())

if __name__ == "__main__":
    main()
