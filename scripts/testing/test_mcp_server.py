#!/usr/bin/env python3
"""
Test Script for NSO MCP Server
==============================

This script demonstrates how to test the NSO MCP server functionality
without requiring a full MCP client setup.

Author: AI Assistant
Version: 1.0
Date: 2025-01-16
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from nso_mcp_server import NSOMCPServer, setup_nso_environment, setup_nso_connection

async def test_nso_connection():
    """Test NSO connection and basic functionality."""
    print("🧪 Testing NSO Connection...")
    print("=" * 50)
    
    # Setup NSO environment
    if not setup_nso_environment():
        print("❌ Failed to setup NSO environment")
        return False
    
    # Setup NSO connection
    m, t, root = setup_nso_connection()
    if not root:
        print("❌ Failed to setup NSO connection")
        return False
    
    print("✅ NSO connection established successfully")
    return True

async def test_mcp_server():
    """Test MCP server initialization."""
    print("\n🧪 Testing MCP Server...")
    print("=" * 50)
    
    try:
        # Create MCP server instance
        server = NSOMCPServer()
        print("✅ MCP server created successfully")
        
        # Initialize NSO connection
        if await server.initialize():
            print("✅ MCP server initialized successfully")
            print(f"✅ NSO tools available: {server.nso_tools is not None}")
            return True
        else:
            print("❌ Failed to initialize MCP server")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

async def test_nso_tools():
    """Test NSO tools functionality."""
    print("\n🧪 Testing NSO Tools...")
    print("=" * 50)
    
    try:
        # Setup NSO connection
        if not setup_nso_environment():
            return False
        
        m, t, root = setup_nso_connection()
        if not root:
            return False
        
        # Import NSO tools
        from nso_mcp_server import NSOMCPTools
        nso_tools = NSOMCPTools(root)
        
        # Test device discovery
        print("📱 Testing device discovery...")
        devices = nso_tools.show_all_devices()
        print(f"Found devices: {devices}")
        
        if devices and devices != "No devices found.":
            # Test router version (use first device)
            device_list = devices.split(', ')
            if device_list:
                first_device = device_list[0].strip()
                print(f"\n🔍 Testing router version for {first_device}...")
                version = nso_tools.get_router_version(first_device)
                print(f"Version result: {version[:100]}...")  # Show first 100 chars
                
                print(f"\n🕐 Testing router clock for {first_device}...")
                clock = nso_tools.get_router_clock(first_device)
                print(f"Clock result: {clock[:100]}...")  # Show first 100 chars
        
        print("✅ NSO tools test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing NSO tools: {e}")
        return False

async def test_tool_listing():
    """Test MCP tool listing functionality."""
    print("\n🧪 Testing MCP Tool Listing...")
    print("=" * 50)
    
    try:
        server = NSOMCPServer()
        
        # Test list tools handler
        tools_result = await server.server._handlers['list_tools']()
        tools = tools_result.tools
        
        print(f"✅ Found {len(tools)} MCP tools:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i:2d}. {tool.name}")
            print(f"      {tool.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing tool listing: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 NSO MCP Server Test Suite")
    print("=" * 60)
    
    tests = [
        ("NSO Connection", test_nso_connection),
        ("MCP Server", test_mcp_server),
        ("NSO Tools", test_nso_tools),
        ("Tool Listing", test_tool_listing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! MCP server is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
