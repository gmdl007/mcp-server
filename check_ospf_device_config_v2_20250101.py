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
        try:
            if hasattr(device, 'config') and hasattr(device.config, 'router'):
                if hasattr(device.config.router, 'ospf'):
                    ospf_list = device.config.router.ospf
                    # Check if list has any entries
                    ospf_keys = list(ospf_list.keys())
                    if ospf_keys:
                        print(f'  OSPF Config: EXISTS - {len(ospf_keys)} OSPF process(es)')
                        for ospf_name in ospf_keys:
                            ospf = ospf_list[ospf_name]
                            print(f'    Process: {ospf_name}')
                            # Check for router-id
                            if hasattr(ospf, 'router_id') and ospf.router_id:
                                print(f'      Router ID: {ospf.router_id}')
                            # Check for areas and interfaces
                            if hasattr(ospf, 'area'):
                                areas = list(ospf.area.keys())
                                if areas:
                                    for area_id in areas:
                                        area = ospf.area[area_id]
                                        print(f' podle      Area: {area_id}')
                                        if hasattr(area, 'interface'):
                                            interfaces = list(area.interface.keys())
                                            if interfaces:
                                                print(f'          Interfaces in OSPF: {interfaces}')
                                            else:
                                                print(f'          Interfaces in OSPF: NONE')
                                else:
                                    print(f'      Areas: NONE')
                            else:
                                print(f'      Areas: NONE')
                    else:
                        print(f'  OSPF Config: EXISTS but EMPTY (no processes)')
                else:
                    print(f'  OSPF Config: NONE')
            else:
                print(f'  OSPF Config: NONE (no router config)')
        except Exception as e:
            print(f'  OSPF Config: ERROR - {e}')
        print()

m.end_user_session()

