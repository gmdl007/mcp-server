#!/usr/bin/env python3
"""Create iBGP service between xr9kv-1 and xr9kv-2"""

import os
import sys

# Set NSO environment variables
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

from ncs import maapi, maagic

def create_ibgp_service():
    """Create iBGP service between xr9kv-1 and xr9kv-2"""
    try:
        print("🔧 Setting up iBGP service 'peer1-2' between xr9kv-1 and xr9kv-2")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Validate routers exist
        if 'xr9kv-1' not in root.devices.device:
            print(f"❌ Error: Router 'xr9kv-1' not found in NSO devices")
            m.end_user_session()
            return
        
        if 'xr9kv-2' not in root.devices.device:
            print(f"❌ Error: Router 'xr9kv-2' not found in NSO devices")
            m.end_user_session()
            return
        
        # Access iBGP service
        try:
            services = root.ibgp__ibgp
            print(f"✅ Found iBGP service package")
        except AttributeError:
            print("❌ Error: iBGP service package not loaded. Please reload NSO packages.")
            m.end_user_session()
            return
        
        # Create service instance
        service_name = 'peer1-2'
        if service_name in services:
            svc = services[service_name]
            print(f"ℹ️ Service '{service_name}' already exists, updating...")
        else:
            svc = services.create(service_name)
            print(f"✅ Created new iBGP service instance '{service_name}'")
        
        # Set service parameters
        svc.as_number = 65000
        svc.router1 = 'xr9kv-1'
        svc.router1_lo0_ip = '1.1.1.1'
        svc.router1_router_id = '1.1.1.1'
        svc.router2 = 'xr9kv-2'
        svc.router2_lo0_ip = '1.1.1.2'
        svc.router2_router_id = '1.1.1.2'
        
        # Apply changes
        t.apply()
        print("✅ Changes applied to NSO")
        
        # Show configuration
        print("\n✅ Successfully configured iBGP service 'peer1-2':")
        print(f"  AS Number: 65000")
        print(f"  Router1: xr9kv-1")
        print(f"    - Loopback0 IP: 1.1.1.1")
        print(f"    - Router ID: 1.1.1.1")
        print(f"  Router2: xr9kv-2")
        print(f"    - Loopback0 IP: 1.1.1.2")
        print(f"    - Router ID: 1.1.1.2")
        print(f"\n  Status: ✅ Applied to NSO service database")
        print(f"  Note: Use NSO CLI 'commit' command to push to routers")
        
        m.end_user_session()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        m.end_user_session()

if __name__ == "__main__":
    create_ibgp_service()

