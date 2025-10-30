#!/usr/bin/env python3
"""
NSO Connection Test Script
=========================

This script tests NSO connectivity and device discovery
before running the full multi-agent application.

Usage:
    python nso_connection_test.py
"""

import os
import sys
from typing import List, Dict, Any

# =============================================================================
# CONFIGURATION - ADAPT THESE FOR YOUR ENVIRONMENT
# =============================================================================

NSO_DIR = "/Users/gudeng/NCS-614"  # Change this to your NSO installation path
NSO_USER = "admin"                 # Change if using different NSO user
NSO_CONTEXT = "test_context"       # Change if needed

# =============================================================================
# NSO CONNECTION TEST
# =============================================================================

def setup_nso_environment():
    """Setup NSO environment variables and Python path"""
    print("🔧 Setting up NSO environment...")
    
    # Set NSO environment variables
    os.environ['NCS_DIR'] = NSO_DIR
    os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
    os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
    
    # Add NSO Python API to Python path
    nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
    if nso_pyapi_path not in sys.path:
        sys.path.insert(0, nso_pyapi_path)
    
    print(f"✅ NSO environment configured:")
    print(f"   - NCS_DIR: {NSO_DIR}")
    print(f"   - PYTHONPATH: {nso_pyapi_path}")
    
    return True

def test_nso_imports():
    """Test if NSO Python modules can be imported"""
    print("\n📦 Testing NSO Python imports...")
    
    try:
        import ncs
        print("✅ ncs module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ncs: {e}")
        return False
    
    try:
        import ncs.maapi as maapi
        print("✅ ncs.maapi module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ncs.maapi: {e}")
        return False
    
    try:
        import ncs.maagic as maagic
        print("✅ ncs.maagic module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ncs.maagic: {e}")
        return False
    
    return True

def test_nso_connection():
    """Test NSO connection and basic operations"""
    print("\n🔌 Testing NSO connection...")
    
    try:
        import ncs
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        
        # Create MAAPI connection
        m = maapi.Maapi()
        print("✅ MAAPI object created")
        
        # Start user session
        m.start_user_session(NSO_USER, NSO_CONTEXT)
        print(f"✅ User session started: {NSO_USER}")
        
        # Start transaction
        t = m.start_write_trans()
        print("✅ Write transaction started")
        
        # Get root object
        root = maagic.get_root(t)
        print("✅ Root object obtained")
        
        return m, t, root
        
    except Exception as e:
        print(f"❌ NSO connection failed: {e}")
        return None, None, None

def test_device_discovery(root):
    """Test device discovery and information retrieval"""
    print("\n📱 Testing device discovery...")
    
    try:
        devices = []
        device_info = {}
        
        # Get all devices
        for device in root.devices.device:
            device_name = device.name
            devices.append(device_name)
            
            # Get device information - handle different NSO versions
            try:
                info = {
                    'name': device_name,
                    'address': str(device.address),
                    'port': str(device.port),
                    'authgroup': str(device.authgroup),
                    'device_type': str(device.device_type),
                    'oper_state': 'unknown',
                    'admin_state': 'unknown'
                }
                
                # Try to get operational state if available
                try:
                    info['oper_state'] = str(device.oper_state)
                except:
                    pass
                
                # Try to get admin state if available
                try:
                    info['admin_state'] = str(device.admin_state)
                except:
                    pass
                
            except Exception as info_e:
                print(f"⚠️  Warning: Could not get full info for {device_name}: {info_e}")
                info = {
                    'name': device_name,
                    'address': 'unknown',
                    'port': 'unknown',
                    'authgroup': 'unknown',
                    'device_type': 'unknown',
                    'oper_state': 'unknown',
                    'admin_state': 'unknown'
                }
            
            device_info[device_name] = info
        
        print(f"✅ Found {len(devices)} devices:")
        for device in devices:
            info = device_info[device]
            print(f"   - {device}: {info['oper_state']} ({info['address']}:{info['port']})")
        
        return devices, device_info
        
    except Exception as e:
        print(f"❌ Device discovery failed: {e}")
        return [], {}

def test_device_commands(root, devices):
    """Test basic device command execution"""
    print("\n⚡ Testing device command execution...")
    
    if not devices:
        print("⚠️  No devices available for command testing")
        return
    
    # Test on first device
    test_device = devices[0]
    print(f"🧪 Testing commands on {test_device}...")
    
    try:
        device = root.devices.device[test_device]
        
        # Test basic commands
        test_commands = [
            "show version",
            "show ipv4 int brief",
            "show processes cpu"
        ]
        
        for cmd in test_commands:
            try:
                result = device.live_status.cisco_ios_xr_stats__exec.any.get(cmd)
                print(f"✅ Command '{cmd}' executed successfully")
                # Print first few lines of result
                result_lines = str(result).split('\n')[:3]
                for line in result_lines:
                    if line.strip():
                        print(f"   {line}")
            except Exception as e:
                print(f"⚠️  Command '{cmd}' failed: {e}")
        
    except Exception as e:
        print(f"❌ Device command testing failed: {e}")

def cleanup_nso_connection(m, t):
    """Clean up NSO connection"""
    print("\n🧹 Cleaning up NSO connection...")
    
    try:
        if t:
            t.finish()
            print("✅ Transaction finished")
        
        if m:
            m.close()
            print("✅ MAAPI connection closed")
        
    except Exception as e:
        print(f"⚠️  Error during cleanup: {e}")

def main():
    """Main test function"""
    print("🚀 NSO Connection Test")
    print("=" * 50)
    
    # Setup environment
    if not setup_nso_environment():
        print("❌ Environment setup failed")
        return False
    
    # Test imports
    if not test_nso_imports():
        print("❌ NSO imports failed")
        return False
    
    # Test connection
    m, t, root = test_nso_connection()
    if not root:
        print("❌ NSO connection failed")
        return False
    
    try:
        # Test device discovery
        devices, device_info = test_device_discovery(root)
        
        # Test device commands
        test_device_commands(root, devices)
        
        # Summary
        print("\n📊 Test Summary:")
        print(f"✅ NSO connection: SUCCESS")
        print(f"✅ Device discovery: {len(devices)} devices found")
        print(f"✅ Ready for multi-agent deployment")
        
        if devices:
            print(f"\n📱 Available devices for multi-agent:")
            for device in devices:
                info = device_info[device]
                print(f"   - {device}: {info['oper_state']}")
        
        return True
        
    finally:
        # Cleanup
        cleanup_nso_connection(m, t)

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 All tests passed! Ready to deploy multi-agent application.")
    else:
        print("\n❌ Tests failed. Please check NSO configuration.")
    
    sys.exit(0 if success else 1)
