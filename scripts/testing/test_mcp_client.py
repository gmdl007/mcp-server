#!/usr/bin/env python3
"""
Test MCP Client for NSO MCP Server
==================================

A simple test client to verify the NSO MCP server is working correctly.

Author: AI Assistant
Version: 1.0
Date: 2025-01-16
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by sending requests."""
    print("🧪 Testing NSO MCP Server...")
    print("=" * 50)
    
    # Start the MCP server process
    server_process = subprocess.Popen([
        sys.executable, 
        str(Path(__file__).parent / "nso_mcp_server_simple.py")
    ], 
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
    )
    
    try:
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 Received response: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # Send list tools request
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("📤 Sending list tools request...")
        server_process.stdin.write(json.dumps(list_tools_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get('result', {}).get('tools', [])
            print(f"📥 Found {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                print(f"  {i:2d}. {tool['name']}")
        
        # Test a simple tool call
        call_tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "show_all_devices",
                "arguments": {}
            }
        }
        
        print("📤 Sending show_all_devices request...")
        server_process.stdin.write(json.dumps(call_tool_request) + "\n")
        server_process.stdin.flush()
        
        # Read response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            result = response.get('result', {}).get('content', [{}])[0].get('text', 'No result')
            print(f"📥 Devices found: {result}")
        
        print("✅ MCP server test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
    
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
