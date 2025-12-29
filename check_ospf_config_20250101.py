#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
from ncs import maapi, maagic

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')
t = m.start_read_trans()
root = maagic.get_root(t)

print('=== OSPF BASE CONFIGURATIONS ===')
if hasattr(root, 'ospf') and hasattr(root.ospf, 'base'):
    for router in root.ospf.base:
        print(f'\nRouter: {router.device}')
        print(f'  Router ID: {router.router_id}')
        print(f'  Area: {router.area}')
        if hasattr(router, 'neighbor'):
            for neighbor in router.neighbor:
                print(f'  Neighbor: {neighbor.device}')
                if hasattr(neighbor, 'local_interface'):
                    print(f'    Local Interface: {neighbor.local_interface}')
                if hasattr(neighbor, 'local_ip'):
                    print(f'    Local IP: {neighbor.local_ip}')
                if hasattr(neighbor, 'remote_interface'):
                    print(f'    Remote Interface: {neighbor.remote_interface}')
                if hasattr(neighbor, 'remote_ip'):
                    print(f'    Remote IP: {neighbor.remote_ip}')
else:
    print('No OSPF base configurations found')

print('\n\n=== OSPF LINK CONFIGURATIONS ===')
if hasattr(root, 'ospf') and hasattr(root.ospf, 'link'):
    for link in root.ospf.link:
        print(f'\nLink: {link.name}')
        print(f'  Area: {link.area}')
        if hasattr(link, 'device'):
            for device in link.device:
                print(f'  Device: {device.name}')
                if hasattr(device, 'interface'):
                    print(f'    Interface: {device.interface}')
                if hasattr(device, 'ip'):
                    print(f'    IP: {device.ip}')
                if hasattr(device, 'router_id'):
                    print(f'    Router ID: {device.router_id}')
                if hasattr(device, 'description'):
                    print(f'    Description: {device.description}')
else:
    print('No OSPF link configurations found')

m.end_user_session()

