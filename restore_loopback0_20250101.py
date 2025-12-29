#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
os.environ['NCS_DIR'] = '/Users/gudeng/NCS-614'
from ncs import maapi, maagic

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')
t = m.start_write_trans()
root = maagic.get_root(t)

# Router IDs for Loopback0
router_ids = {
    'xr9kv-1': '1.1.1.1',
    'xr9kv-2': '1.1.1.2',
    'xr9kv-3': '1.1.1.3'
}

print('=== Restoring Loopback0 on all routers ===\n')
for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        router_id = router_ids[device_name]
        
        if hasattr(device, 'config') and hasattr(device.config, 'interface'):
            interfaces = device.config.interface
            if not hasattr(interfaces, 'Loopback') or '0' not in interfaces.Loopback:
                # Create Loopback0
                lo0 = interfaces.Loopback.create('0')
                addr = lo0.ipv4.address.create(router_id)
                addr.mask = '255.255.255.255'
                print(f"✅ Restored Loopback0 on {device_name} with IP {router_id}")
            else:
                lo0 = interfaces.Loopback['0']
                # Ensure IP is set
                if hasattr(lo0, 'ipv4') and hasattr(lo0.ipv4, 'address'):
                    addrs = list(lo0.ipv4.address.keys())
                    if router_id not in addrs:
                        addr = lo0.ipv4.address.create(router_id)
                        addr.mask = '255.255.255.255'
                        print(f"✅ Updated Loopback0 on {device_name} with IP {router_id}")
                    else:
                        print(f"ℹ️  Loopback0 already has IP {router_id} on {device_name}")
                else:
                    addr = lo0.ipv4.address.create(router_id)
                    addr.mask = '255.255.255.255'
                    print(f"✅ Added IP to Loopback0 on {device_name}")

print('\n=== Applying changes ===')
try:
    t.apply()
    print("✅ Loopback0 restored on all routers!")
except Exception as e:
    print(f"❌ Error: {e}")

m.end_user_session()

