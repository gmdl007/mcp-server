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

print('=== DEVICE-LEVEL OSPF CONFIGURATIONS ===\n')
for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        print(f'Router: {device_name}')
        if hasattr(device, 'config') and hasattr(device.config, 'router'):
            if hasattr(device.config.router, 'ospf'):
                ospf_config = device.config.router.ospf
                print(f'  OSPF Config: EXISTS')
                # Try to get OSPF details
                try:
                    for ospf_name in ospf_config:
                        ospf = ospf_config[ospf_name]
                        print(f'    OSPF Process: {ospf_name}')
                        if hasattr(ospf, 'router_id'):
                            print(f'      Router ID: {ospf.router_id}')
                        if hasattr(ospf, 'area'):
                            for area_id in ospf.area:
                                area = ospf.area[area_id]
                                print(f'      Area: {area_id}')
                                if hasattr(area, 'interface'):
                                    for interface in area.interface:
                                        print(f'        Interface: {interface.name}')
                except Exception as e:
                    print(f'    (Error reading OSPF details: {e})')
            else:
                print(f'  OSPF Config: NONE')
        else:
            print(f'  OSPF Config: NONE (no router config section)')
        print()

m.end_user_session()

