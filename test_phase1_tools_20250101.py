#!/usr/bin/env python3
"""
Test script for Phase 1 MCP Tools
Tests device connection, commit queue, bulk operations, and other Phase 1 tools
"""

import os
import sys

# Set NSO environment variables
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add NSO Python API to Python path
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

# Import the server module
sys.path.insert(0, '/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp')
from fastmcp_nso_server_auto_generated import (
    connect_device,
    ping_device,
    get_device_connection_status,
    list_commit_queue,
    sync_all_devices,
    get_all_devices_sync_status,
    execute_device_command,
    get_bgp_neighbor_status,
    get_ospf_neighbor_status
)

def test_device_connection():
    """Test device connection tools"""
    print("\n" + "="*60)
    print("TEST 1: Device Connection Management")
    print("="*60)
    
    try:
        # Test get_device_connection_status
        print("\n1. Testing get_device_connection_status('xr9kv-1')...")
        result = get_device_connection_status('xr9kv-1')
        print(result)
        
        # Test ping_device
        print("\n2. Testing ping_device('xr9kv-1')...")
        result = ping_device('xr9kv-1')
        print(result)
        
        print("\n✅ Device connection tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Device connection tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_commit_queue():
    """Test commit queue management"""
    print("\n" + "="*60)
    print("TEST 2: Commit Queue Management")
    print("="*60)
    
    try:
        # Test list_commit_queue
        print("\n1. Testing list_commit_queue(limit=10)...")
        result = list_commit_queue(limit=10)
        print(result)
        
        print("\n✅ Commit queue tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Commit queue tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bulk_operations():
    """Test bulk device operations"""
    print("\n" + "="*60)
    print("TEST 3: Bulk Device Operations")
    print("="*60)
    
    try:
        # Test get_all_devices_sync_status
        print("\n1. Testing get_all_devices_sync_status()...")
        result = get_all_devices_sync_status()
        print(result[:500] + "..." if len(result) > 500 else result)
        
        print("\n✅ Bulk operations tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Bulk operations tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_execution():
    """Test device command execution"""
    print("\n" + "="*60)
    print("TEST 4: Device Command Execution")
    print("="*60)
    
    try:
        # Test execute_device_command
        print("\n1. Testing execute_device_command('xr9kv-1', 'show version')...")
        result = execute_device_command('xr9kv-1', 'show version')
        print(result[:500] + "..." if len(result) > 500 else result)
        
        print("\n✅ Command execution tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Command execution tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_operational_status():
    """Test operational status queries"""
    print("\n" + "="*60)
    print("TEST 5: Operational Status Queries")
    print("="*60)
    
    try:
        # Test get_bgp_neighbor_status
        print("\n1. Testing get_bgp_neighbor_status('xr9kv-1')...")
        result = get_bgp_neighbor_status('xr9kv-1')
        print(result[:500] + "..." if len(result) > 500 else result)
        
        # Test get_ospf_neighbor_status
        print("\n2. Testing get_ospf_neighbor_status('xr9kv-1')...")
        result = get_ospf_neighbor_status('xr9kv-1')
        print(result[:500] + "..." if len(result) > 500 else result)
        
        print("\n✅ Operational status tests passed!")
        return True
    except Exception as e:
        print(f"\n❌ Operational status tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 1 TOOLS TEST SUITE")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Device Connection", test_device_connection()))
    results.append(("Commit Queue", test_commit_queue()))
    results.append(("Bulk Operations", test_bulk_operations()))
    results.append(("Command Execution", test_command_execution()))
    results.append(("Operational Status", test_operational_status()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 1 tools are working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

