#!/usr/bin/env python3
"""
Add netsim devices to NSO 6.4.1.3 and configure Loopback0
"""

import sys
import os

# NSO 6.4.1.3 directory
NSO_DIR = '/Users/gudeng/NCS-6413'
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

import ncs.maapi as maapi
import ncs.maagic as maagic

def add_netsim_devices():
    """Add netsim devices to NSO"""
    devices = [
        ('xr9kv-1', '127.0.0.1', 10022),
        ('xr9kv-2', '127.0.0.1', 10023),
        ('xr9kv-3', '127.0.0.1', 10024),
    ]
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'python')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Check/create default authgroup if needed
        if 'default' not in root.devices.authgroups.group:
            authgroup = root.devices.authgroups.group.create('default')
            umap = authgroup.umap.create('default')
            umap.remote_name = 'admin'
            umap.remote_password = 'admin'
            print("✅ Created default authgroup")
        
        for device_name, address, port in devices:
            # Check if device already exists
            if device_name in root.devices.device:
                print(f"⚠️  Device {device_name} already exists, updating...")
                device = root.devices.device[device_name]
            else:
                device = root.devices.device.create(device_name)
                print(f"✅ Creating device {device_name}...")
            
            device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61'
            device.state.admin_state = 'unlocked'
            device.authgroup = 'default'
            device.address = address
            device.port = port
            
            # Configure SSH settings if available
            try:
                if hasattr(device, 'ned_settings') and hasattr(device.ned_settings, 'ssh'):
                    device.ned_settings.ssh.host_key_check = False
            except Exception:
                pass  # SSH settings may not be available
            
            print(f"   ✅ {device_name}: Configured - {address}:{port}")
        
        t.apply()
        m.end_user_session()
        print("\n✅ All devices added to NSO")
        return True
        
    except Exception as e:
        print(f"❌ Error adding devices: {e}")
        import traceback
        traceback.print_exc()
        return False

def configure_loopback0():
    """Configure Loopback0 on all netsim devices"""
    devices = ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']
    loopback_ips = {
        'xr9kv-1': '1.1.1.1/32',
        'xr9kv-2': '2.2.2.2/32',
        'xr9kv-3': '3.3.3.3/32',
    }
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'python')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        for device_name in devices:
            if device_name not in root.devices.device:
                print(f"⚠️  Device {device_name} not found, skipping Loopback0 config...")
                continue
                
            device = root.devices.device[device_name]
            
            # Configure Loopback0
            ip_addr, netmask = loopback_ips[device_name].split('/')
            interface = device.config.interface.Loopback.create('0')
            interface.description = 'Loopback0'
            interface.ipv4.address.ip.create(ip_addr)
            interface.ipv4.address.ip[ip_addr].netmask = netmask
            
            print(f"✅ Configured Loopback0 on {device_name}: {loopback_ips[device_name]}")
        
        t.apply()
        m.end_user_session()
        print("\n✅ All Loopback0 interfaces configured")
        return True
        
    except Exception as e:
        print(f"❌ Error configuring Loopback0: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("Adding Netsim Devices and Configuring Loopback0")
    print("=" * 70)
    
    # Step 1: Add devices
    print("\n📋 Step 1: Adding netsim devices to NSO...")
    if not add_netsim_devices():
        print("❌ Failed to add devices")
        return 1
    
    # Step 2: Configure Loopback0
    print("\n📋 Step 2: Configuring Loopback0 on all devices...")
    if not configure_loopback0():
        print("❌ Failed to configure Loopback0")
        return 1
    
    print("\n" + "=" * 70)
    print("✅ Successfully completed!")
    print("=" * 70)
    return 0

if __name__ == '__main__':
    sys.exit(main())
