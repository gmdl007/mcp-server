#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
os.environ['NCS_DIR'] = '/Users/gudeng/NCS-614'
from ncs import maapi, maagic

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')
t = m.start_read_trans()
root = maagic.get_root(t)

print('=== FINAL VERIFICATION ===\n')

print('Interface Configuration:')
print('-' * 50)
for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        print(f'\n{device_name}:')
        if hasattr(device, 'config') and hasattr(device.config, 'interface'):
            interfaces = device.config.interface
            total = 0
            if hasattr(interfaces, 'Loopback'):
                loopbacks = list(interfaces.Loopback.keys())
                if '0' in loopbacks:
                    print(f'  ✅ Loopback/0: EXISTS')
                    total += 1
                other_lbs = [lb for lb in loopbacks if lb != '0']
                if other_lbs:
                    print(f'  ⚠️  Other Loopbacks: {other_lbs}')
                    total += len(other_lbs)
            if hasattr(interfaces, 'GigabitEthernet'):
                ge_interfaces = list(interfaces.GigabitEthernet.keys())
                if ge_interfaces:
                    print(f'  ⚠️  GigabitEthernet interfaces: {ge_interfaces}')
                    total += len(ge_interfaces)
            if total == 0:
                print(f'  ❌ No interfaces found')
            elif total == 1 and 'Loopback' in str(interfaces):
                print(f'  ✅ Only Loopback/0 exists')
        else:
            print(f'  ❌ No interface configuration')

print('\n\nOSPF Configuration:')
print('-' * 50)
for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        print(f'\n{device_name}:')
        if hasattr(device, 'config') and hasattr(device.config, 'router'):
            if hasattr(device.config.router, 'ospf'):
                ospf_list = device.config.router.ospf
                ospf_keys = list(ospf_list.keys())
                if ospf_keys:
                    print(f'  ⚠️  OSPF processes: {ospf_keys}')
                else:
                    print(f'  ✅ OSPF container exists but EMPTY (no processes)')
            else:
                print(f'  ✅ No OSPF configuration')
        else:
            print(f'  ✅ No router configuration (no OSPF)')

m.end_user_session()
print('\n=== SUMMARY ===')
print('✅ Only Loopback/0 should exist on all routers')
print('✅ OSPF should be empty or not exist')

