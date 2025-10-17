#!/usr/bin/env python3
"""
MCP Server Diagnostic Tool
==========================

This script helps diagnose MCP server issues for Cursor integration.
"""

import os
import sys
import json
from pathlib import Path

def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Environment Check")
    print("=" * 30)
    
    # Check NSO environment
    nso_dir = "/Users/gudeng/NCS-614"
    if os.path.exists(nso_dir):
        print(f"✅ NSO directory exists: {nso_dir}")
    else:
        print(f"❌ NSO directory missing: {nso_dir}")
        return False
    
    # Check MCP virtual environment
    mcp_venv = "/Users/gudeng/MCP_Server/mcp_venv"
    if os.path.exists(mcp_venv):
        print(f"✅ MCP virtual environment exists: {mcp_venv}")
    else:
        print(f"❌ MCP virtual environment missing: {mcp_venv}")
        return False
    
    # Check MCP server file
    server_file = "/Users/gudeng/MCP_Server/src/mcp_server/nso_mcp_simple_fixed.py"
    if os.path.exists(server_file):
        print(f"✅ MCP server file exists: {server_file}")
    else:
        print(f"❌ MCP server file missing: {server_file}")
        return False
    
    # Check wrapper script
    wrapper_script = "/Users/gudeng/MCP_Server/src/mcp_server/start_nso_mcp.sh"
    if os.path.exists(wrapper_script):
        print(f"✅ Wrapper script exists: {wrapper_script}")
        if os.access(wrapper_script, os.X_OK):
            print(f"✅ Wrapper script is executable")
        else:
            print(f"❌ Wrapper script is not executable")
            return False
    else:
        print(f"❌ Wrapper script missing: {wrapper_script}")
        return False
    
    return True

def check_configuration():
    """Check the Cursor MCP configuration."""
    print("\n🔧 Configuration Check")
    print("=" * 30)
    
    # Check multiple possible configuration locations
    config_locations = [
        "/Users/gudeng/MCP_Server/.cursor/mcp.json",
        "/Users/gudeng/.cursor/mcp.json",
        "/Users/gudeng/MCP_Server/cursor_mcp_config.json"
    ]
    
    config_file = None
    for location in config_locations:
        if os.path.exists(location):
            config_file = location
            print(f"✅ Found configuration file: {location}")
            break
    
    if not config_file:
        print("❌ No configuration file found in any expected location:")
        for location in config_locations:
            print(f"   - {location}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Configuration file exists: {config_file}")
        
        if "mcpServers" in config:
            servers = config["mcpServers"]
            print(f"✅ Found {len(servers)} MCP server(s) configured")
            
            for server_name, server_config in servers.items():
                print(f"  📡 Server: {server_name}")
                print(f"    Command: {server_config.get('command', 'Not specified')}")
                print(f"    Args: {server_config.get('args', [])}")
                
                # Check if command exists
                command = server_config.get('command', '')
                if command and os.path.exists(command):
                    print(f"    ✅ Command exists: {command}")
                elif command:
                    print(f"    ❌ Command missing: {command}")
        else:
            print("❌ No mcpServers section found in configuration")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are available."""
    print("\n📦 Dependencies Check")
    print("=" * 30)
    
    # Check MCP library
    try:
        import mcp
        print(f"✅ MCP library available: {mcp.__version__ if hasattr(mcp, '__version__') else 'Unknown version'}")
    except ImportError:
        print("❌ MCP library not available")
        return False
    
    # Check NSO Python API
    try:
        # Set up NSO environment
        os.environ['NCS_DIR'] = '/Users/gudeng/NCS-614'
        os.environ['DYLD_LIBRARY_PATH'] = '/Users/gudeng/NCS-614/lib'
        os.environ['PYTHONPATH'] = '/Users/gudeng/NCS-614/src/ncs/pyapi'
        sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
        
        import ncs
        print("✅ NSO Python API available")
    except ImportError as e:
        print(f"❌ NSO Python API not available: {e}")
        return False
    
    return True

def main():
    """Run all diagnostic checks."""
    print("🩺 MCP Server Diagnostic Tool")
    print("=" * 40)
    
    checks = [
        ("Environment", check_environment),
        ("Configuration", check_configuration),
        ("Dependencies", check_dependencies)
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! MCP server should work with Cursor.")
        print("\nNext steps:")
        print("1. Restart Cursor")
        print("2. Check Tools & MCP settings")
        print("3. The server should show '14 tools available'")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nTroubleshooting tips:")
        print("1. Make sure NSO is running")
        print("2. Verify the MCP virtual environment is activated")
        print("3. Check file permissions on the wrapper script")
        print("4. Ensure all paths in the configuration are correct")

if __name__ == "__main__":
    main()
