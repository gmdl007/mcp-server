#!/usr/bin/env python3
"""Verify and print actual device configurations"""

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

# Import NSO modules
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

def print_config(router_name):
    """Print actual device configuration for a router"""
    print("=" * 80)
    print(f"ROUTER: {router_name}")
    print("=" * 80)
    
    try:
        device = root.devices.device[router_name]
        config = device.config
        
        # Print Interface Configuration
        print("\n📍 INTERFACE CONFIGURATION:")
        print("-" * 80)
        
        # Use exec command to get running config for interfaces
        try:
            show = device.live_status.__getitem__('exec').any
            inp = show.get_input()
            inp.args = ['show running-config interface']
            result = show.request(inp)
            if hasattr(result, 'result') and result.result:
                print(result.result)
            else:
                print("  No interface configuration output")
        except Exception as e:
            print(f"  Error getting interface config via exec: {e}")
            # Fallback: try to read from config tree
            if hasattr(config, 'interface'):
                print("  (Config tree access attempted but not fully implemented)")
        
        # Print OSPF Configuration
        print("\n📍 OSPF CONFIGURATION:")
        print("-" * 80)
        try:
            show = device.live_status.__getitem__('exec').any
            inp = show.get_input()
            inp.args = ['show running-config router ospf']
            result = show.request(inp)
            if hasattr(result, 'result') and result.result:
                print(result.result)
            else:
                print("  No OSPF configuration found")
        except Exception as e:
            print(f"  Error getting OSPF config: {e}")
            print("  No OSPF configuration found")
        
        # Print BGP Configuration
        print("\n📍 BGP CONFIGURATION:")
        print("-" * 80)
        try:
            show = device.live_status.__getitem__('exec').any
            inp = show.get_input()
            inp.args = ['show running-config router bgp']
            result = show.request(inp)
            if hasattr(result, 'result') and result.result:
                print(result.result)
            else:
                print("  No BGP configuration found")
        except Exception as e:
            print(f"  Error getting BGP config: {e}")
            print("  No BGP configuration found")
        
        print("\n")
        
    except Exception as e:
        print(f"❌ Error reading config for {router_name}: {e}")
        import traceback
        traceback.print_exc()

def main():
    global root
    print("=" * 80)
    print("ACTUAL DEVICE CONFIGURATION VERIFICATION")
    print("=" * 80)
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_write_trans()  # Use write trans for exec commands
        root = maagic.get_root(t)
        
        # Print configs for all routers
        for router_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
            if router_name in root.devices.device:
                print_config(router_name)
            else:
                print(f"❌ Router {router_name} not found")
        
        m.end_user_session()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            m.end_user_session()
        except:
            pass

if __name__ == "__main__":
    main()
