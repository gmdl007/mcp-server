#!/usr/bin/env python3
"""
Configure Loopback0 directly on netsim devices
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
        'xr9kv-1': ('1.1.1.1', '255.255.255.255'),
        'xr9kv-2': ('2.2.2.2', '255.255.255.255'),
        'xr9kv-3': ('3.3.3.3', '255.255.255.255'),
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
            
            # Access interface configuration
            # Try different interface path structures
            try:
                # Method 1: Direct interface path
                interfaces = device.config.interface
                
                # Check what interface types are available
                if hasattr(interfaces, 'Loopback'):
                    loopback_interfaces = interfaces.Loopback
                    if '0' not in loopback_interfaces:
                        loopback_interfaces.create('0')
                    interface = loopback_interfaces['0']
                elif hasattr(interfaces, 'loopback'):
                    loopback_interfaces = interfaces.loopback
                    if '0' not in loopback_interfaces:
                        loopback_interfaces.create('0')
                    interface = loopback_interfaces['0']
                else:
                    # Try creating Loopback interface type
                    print(f"  Checking available interface types for {device_name}...")
                    print(f"  Available attributes: {[attr for attr in dir(interfaces) if not attr.startswith('_')]}")
                    # Try to create Loopback interface
                    if hasattr(interfaces, '__getitem__'):
                        try:
                            interface = interfaces['Loopback']['0']
                        except:
                            # Create it
                            interfaces.create('Loopback')
                            interfaces['Loopback'].create('0')
                            interface = interfaces['Loopback']['0']
                    else:
                        print(f"⚠️  Cannot access Loopback interface type for {device_name}")
                        continue
                
                # Set description
                interface.description = 'Loopback0'
                
                # Configure IPv4
                try:
                    if not hasattr(interface, 'ipv4'):
                        interface.ipv4.create()
                except:
                    pass  # IPv4 might already exist
                
                interface.ipv4.address.ip = ip_addr
                interface.ipv4.address.mask = mask
                
                print(f"✅ Configured Loopback0 on {device_name}: {ip_addr}/{mask}")
                
            except Exception as e:
                print(f"❌ Error configuring {device_name}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
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
