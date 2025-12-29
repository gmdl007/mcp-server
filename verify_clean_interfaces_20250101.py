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

print('=' * 70)
print('INTERFACE CLEANUP VERIFICATION')
print('=' * 70)

for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    print(f'\n{"=" * 70}')
    print(f'DEVICE: {device_name}')
    print('=' * 70)
    
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        
        if hasattr(device, 'config') and hasattr(device.config, 'interface'):
            interfaces = device.config.interface
            
            # Check GigabitEthernet interfaces
            if hasattr(interfaces, 'GigabitEthernet'):
                ge_interfaces = list(interfaces.GigabitEthernet.keys())
                physical = []
                subinterfaces = []
                
                for ge_key in ge_interfaces:
                    ge_key_str = str(ge_key)
                    if '.' in ge_key_str:
                        subinterfaces.append(ge_key_str)
                    else:
                        physical.append(ge_key_str)
                
                print(f'\n📡 GigabitEthernet Interfaces:')
                if physical:
                    print(f'  ✅ Physical interfaces ({len(physical)}):')
                    for p in sorted(physical):
                        print(f'    - GigabitEthernet/{p}')
                if subinterfaces:
                    print(f'  ⚠️  Sub-interfaces found ({len(subinterfaces)}):')
                    for s in sorted(subinterfaces):
                        print(f'    - GigabitEthernet/{s}')
                elif not physical and not subinterfaces:
                    print(f'  ℹ️  No GigabitEthernet interfaces')
            
            # Check Loopback interfaces
            if hasattr(interfaces, 'Loopback'):
                loopbacks = list(interfaces.Loopback.keys())
                if loopbacks:
                    print(f'\n🔁 Loopback Interfaces ({len(loopbacks)}):')
                    for lo in sorted([str(l) for l in loopbacks]):
                        print(f'    - Loopback/{lo}')
                else:
                    print(f'\n🔁 Loopback Interfaces: None')

m.end_user_session()

print('\n' + '=' * 70)
print('VERIFICATION COMPLETE')
print('=' * 70)

