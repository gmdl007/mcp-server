#!/usr/bin/env python3
"""
Test MCP Server Communication
============================

This script tests if the MCP server can start and respond to basic requests.

Author: AI Assistant
Version: 1.0
Date: 2025-01-16
"""

import subprocess
import json
import time
import sys
import os

def test_mcp_server():
    """Test MCP server communication."""
    print("🧪 Testing MCP Server Communication")
    print("=" * 50)
    
    try:
        # Start MCP server
        print("🚀 Starting MCP server...")
        process = subprocess.Popen(
            ["/Users/gudeng/MCP_Server/start_mcp_server.sh"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Give server time to start
        time.sleep(2)
        
        # Send initialization request
        print("📤 Sending initialization request...")
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
        
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read response with timeout
        print("📥 Waiting for response...")
        try:
            response_line = process.stdout.readline()
            if response_line:
                print(f"✅ MCP Response: {response_line.strip()}")
                
                # Try to parse JSON response
                try:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        print("✅ MCP server responded successfully!")
                        return True
                    else:
                        print("⚠️ Unexpected response format")
                        return False
                except json.JSONDecodeError:
                    print("⚠️ Response is not valid JSON")
                    return False
            else:
                print("❌ No response received")
                return False
                
        except Exception as e:
            print(f"❌ Error reading response: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False
    
    finally:
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

def test_mcp_server_simple():
    """Simple test - just check if server starts without errors."""
    print("🧪 Simple MCP Server Test")
    print("=" * 30)
    
    try:
        # Start MCP server and capture initial output
        process = subprocess.Popen(
            ["/Users/gudeng/MCP_Server/start_mcp_server.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ MCP server started successfully and is running")
            
            # Get any output
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stdout:
                    print(f"📤 Server output: {stdout[:200]}...")
                if stderr:
                    print(f"⚠️ Server errors: {stderr[:200]}...")
            except subprocess.TimeoutExpired:
                print("⏱️ Server is running (no immediate output)")
            
            process.terminate()
            return True
        else:
            print("❌ MCP server failed to start")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Error output: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error in simple test: {e}")
        return False

def main():
    """Main test function."""
    print("🔍 MCP Server Communication Test")
    print("=" * 40)
    
    # Test 1: Simple startup test
    print("\n1️⃣ Testing server startup...")
    if test_mcp_server_simple():
        print("✅ Server startup test passed")
    else:
        print("❌ Server startup test failed")
        return
    
    # Test 2: Communication test
    print("\n2️⃣ Testing server communication...")
    if test_mcp_server():
        print("✅ Communication test passed")
    else:
        print("❌ Communication test failed")
        return
    
    print("\n🎉 All tests passed! MCP server should work with Cursor.")
    print("\n📋 Next steps:")
    print("1. Restart Cursor completely")
    print("2. Check if MCP server appears in Cursor")
    print("3. If not, check Cursor's developer console for errors")

if __name__ == "__main__":
    main()

