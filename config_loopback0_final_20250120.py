#!/usr/bin/env python3
"""
Configure Loopback0 on all netsim devices using default authgroup
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

def configure_loopback0():
    """Configure Loopback0 on all netsim devices"""
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
        
        for device_name in devices:
            if device_name not in root.devices.device:
                print(f"⚠️  Device {device_name} not found")
                continue
                
            device = root.devices.device[device_name]
            ip_addr, mask = loopback_ips[device_name]
            
            # Get interfaces
            interfaces = device.config.interface
            
            # Create Loopback0 interface
            if 'Loopback' not in interfaces:
                print(f"⚠️  Loopback interface type not found for {device_name}")
                continue
                
            loopback_interfaces = interfaces.Loopback
            if '0' not in loopback_interfaces:
                loopback_interfaces.create('0')
            
            interface = loopback_interfaces['0']
            
            # Set description
            interface.description = 'Loopback0'
            
            # Configure IPv4 address
            # Calculate dotted decimal mask from CIDR
            mask_int = int(mask)
            mask_bits = (0xFFFFFFFF << (32 - mask_int)) & 0xFFFFFFFF
            mask_dotted = f"{(mask_bits >> 24) & 0xFF}.{(mask_bits >> 16) & 0xFF}.{(mask_bits >> 8) & 0xFF}.{mask_bits & 0xFF}"
            
            # Create IPv4 configuration
            if not hasattr(interface, 'ipv4') or not interface.ipv4.exists():
                interface.ipv4.create()
            
            # Set IP address and mask
            interface.ipv4.address.ip = ip_addr
            interface.ipv4.address.mask = mask_dotted
            
            print(f"✅ Configured Loopback0 on {device_name}: {ip_addr}/{mask}")
        
        t.apply()
        m.end_user_session()
        print("\n✅ All Loopback0 interfaces configured successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("Configuring Loopback0 on all netsim devices")
    print("=" * 70)
    success = configure_loopback0()
    sys.exit(0 if success else 1)
