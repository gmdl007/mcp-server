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
print('COMPLETE DEVICE CONFIGURATION VERIFICATION')
print('=' * 70)

for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    print(f'\n{"=" * 70}')
    print(f'DEVICE: {device_name}')
    print('=' * 70)
    
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        
        # Check interfaces
        print('\n📡 INTERFACES:')
        print('-' * 70)
        if hasattr(device, 'config') and hasattr(device.config, 'interface'):
            interfaces = device.config.interface
            
            # Loopback interfaces
            if hasattr(interfaces, 'Loopback'):
                loopbacks = list(interfaces.Loopback.keys())
                if loopbacks:
                    for lo_id in loopbacks:
                        lo = interfaces.Loopback[lo_id]
                        print(f'  Loopback/{lo_id}:')
                        if hasattr(lo, 'ipv4') and hasattr(lo.ipv4, 'address'):
                            try:
                                # address is a list
                                for addr in lo.ipv4.address:
                                    ip = getattr(addr, 'ip', 'N/A')
                                    mask = getattr(addr, 'mask', 'N/A')
                                    print(f'    IPv4: {ip}/{mask}')
                            except:
                                print(f'    IPv4: (error reading)')
                        if hasattr(lo, 'description') and lo.description:
                            print(f'    Description: {lo.description}')
                        shutdown = getattr(lo, 'shutdown', None)
                        if shutdown is not None:
                            print(f'    Status: {"shutdown" if shutdown else "no shutdown"}')
                        print()
                else:
                    print('  ❌ No Loopback interfaces')
            else:
                print('  ❌ No Loopback interfaces')
            
            # GigabitEthernet interfaces
            if hasattr(interfaces, 'GigabitEthernet'):
                ge_interfaces = list(interfaces.GigabitEthernet.keys())
                if ge_interfaces:
                    print(f'  ⚠️  GigabitEthernet interfaces found: {len(ge_interfaces)}')
                    for ge_id in ge_interfaces:
                        ge = interfaces.GigabitEthernet[ge_id]
                        print(f'    GigabitEthernet/{ge_id}:')
                        if hasattr(ge, 'ipv4') and hasattr(ge.ipv4, 'address'):
                            try:
                                # address is a list
                                for addr in ge.ipv4.address:
                                    ip = getattr(addr, 'ip', 'N/A')
                                    mask = getattr(addr, 'mask', 'N/A')
                                    print(f'      IPv4: {ip}/{mask}')
                            except:
                                print(f'      IPv4: (error reading)')
                        if hasattr(ge, 'description') and ge.description:
                            print(f'      Description: {ge.description}')
                        shutdown = getattr(ge, 'shutdown', None)
                        if shutdown is not None:
                            print(f'      Status: {"shutdown" if shutdown else "no shutdown"}')
                else:
                    print('  ✅ No GigabitEthernet interfaces')
            else:
                print('  ✅ No GigabitEthernet interfaces')
        else:
            print('  ❌ No interface configuration section')
        
        # Check OSPF
        print('\n🔀 OSPF CONFIGURATION:')
        print('-' * 70)
        if hasattr(device, 'config') and hasattr(device.config, 'router'):
            if hasattr(device.config.router, 'ospf'):
                ospf_list = device.config.router.ospf
                ospf_keys = list(ospf_list.keys())
                if ospf_keys:
                    print(f'  ⚠️  OSPF processes found: {ospf_keys}')
                    for ospf_name in ospf_keys:
                        print(f'    Process {ospf_name}: EXISTS')
                else:
                    print('  ✅ OSPF: Container exists but EMPTY (no processes)')
            else:
                print('  ✅ OSPF: No configuration')
        else:
            print('  ✅ OSPF: No router configuration')
        
        # Count total interfaces
        total_interfaces = 0
        if hasattr(device, 'config') and hasattr(device.config, 'interface'):
            interfaces = device.config.interface
            if hasattr(interfaces, 'Loopback'):
                total_interfaces += len(list(interfaces.Loopback.keys()))
            if hasattr(interfaces, 'GigabitEthernet'):
                total_interfaces += len(list(interfaces.GigabitEthernet.keys()))
        
        print(f'\n📊 SUMMARY:')
        print(f'  Total Interfaces: {total_interfaces}')
        if total_interfaces == 1:
            print(f'  ✅ Status: CLEAN - Only Loopback/0 exists')
        elif total_interfaces == 0:
            print(f'  ⚠️  Status: No interfaces found')
        else:
            print(f'  ⚠️  Status: {total_interfaces} interfaces found (should be only Loopback/0)')

m.end_user_session()

print('\n' + '=' * 70)
print('VERIFICATION COMPLETE')
print('=' * 70)

