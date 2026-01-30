#!/usr/bin/env python3
"""
Fix authgroup and configure Loopback0 on netsim devices
"""

import sys
import os

NSO_DIR = '/Users/gudeng/NCS-6413'
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

import ncs.maapi as maapi
import ncs.maagic as maagic

def setup_authgroup_and_config_loopback():
    """Create cisco authgroup and configure Loopback0"""
    devices = ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']
    loopback_ips = {
        'xr9kv-1': ('1.1.1.1', '32'),
        'xr9kv-2': ('2.2.2.2', '32'),
        'xr9kv-3': ('3.3.3.3', '32'),
    }
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'python')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Create cisco authgroup if it doesn't exist
        if 'cisco' not in root.devices.authgroups.group:
            authgroup = root.devices.authgroups.group.create('cisco')
            umap = authgroup.umap.create('cisco')
            umap.remote_name = 'admin'
            umap.remote_password = 'admin'
            print("✅ Created cisco authgroup")
        else:
            print("✅ cisco authgroup already exists")
        
        # Update devices to use cisco authgroup
        for device_name in devices:
            if device_name in root.devices.device:
                device = root.devices.device[device_name]
                device.authgroup = 'cisco'
                print(f"✅ Updated {device_name} to use cisco authgroup")
        
        # Configure Loopback0
        for device_name in devices:
            if device_name not in root.devices.device:
                print(f"⚠️  Device {device_name} not found")
                continue
                
            device = root.devices.device[device_name]
            ip_addr, netmask = loopback_ips[device_name]
            
            # Create Loopback0 interface
            interface = device.config.interface.Loopback.create('0')
            interface.description = 'Loopback0'
            
            # Configure IPv4 address
            ipv4_addr = interface.ipv4.address.ip.create(ip_addr)
            ipv4_addr.netmask = netmask
            
            print(f"✅ Configured Loopback0 on {device_name}: {ip_addr}/{netmask}")
        
        t.apply()
        m.end_user_session()
        print("\n✅ All configurations applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("Setting up authgroup and configuring Loopback0")
    print("=" * 70)
    success = setup_authgroup_and_config_loopback()
    sys.exit(0 if success else 1)
