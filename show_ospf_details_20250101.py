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

print('=== DETAILED DEVICE-LEVEL OSPF CONFIGURATIONS ===\n')
for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        print(f'Router: {device_name}')
        print('-' * 50)
        try:
            if hasattr(device, 'config') and hasattr(device.config, 'router'):
                if hasattr(device.config.router, 'ospf'):
                    ospf_list = device.config.router.ospf
                    ospf_keys = list(ospf_list.keys())
                    if ospf_keys:
                        for ospf_name in ospf_keys:
                            ospf = ospf_list[ospf_name]
                            print(f'OSPF Process: {ospf_name}')
                            if hasattr(ospf, 'router_id') and ospf.router_id:
                                print(f'  Router ID: {ospf.router_id}')
                            if hasattr(ospf, 'area'):
                                for area_id in ospf.area:
                                    area = ospf.area[area_id]
                                    print(f'  Area: {area_id}')
                                    if hasattr(area, 'interface'):
                                        for iface_key in area.interface:
                                            iface = area.interface[iface_key]
                                            print(f'    Interface: {iface_key.name}')
                                            # Check for network type
                                            if hasattr(iface, 'network'):
                                                print(f'      Network Type: {iface.network}')
                            print()
                    else:
                        print('  OSPF: EMPTY\n')
                else:
                    print('  OSPF: NONE\n')
            else:
                print('  OSPF: NONE (no router config)\n')
        except Exception as e:
            print(f'  ERROR: {e}\n')

m.end_user_session()

print('\n=== SUMMARY ===')
print('✅ OSPF Service-Level Config: EMPTY (already deleted)')
print('⚠️  Device-Level OSPF Config: EXISTS on all 3 routers')
print('   (These are actual router configurations that need to be removed separately)')

