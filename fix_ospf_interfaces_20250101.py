#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
from ncs import maapi, maagic

def normalize_interface(value):
    """Normalize interface to numeric-only format (0/0/0/0)"""
    if not value:
        return value
    v = str(value).strip()
    # Remove any slash after GigabitEthernet
    v = v.replace('GigabitEthernet/', 'GigabitEthernet')
    # Extract numeric parts
    if v.startswith('GigabitEthernet'):
        v = v[len('GigabitEthernet'):]
    # Normalize numeric parts
    parts = [p for p in v.split('/') if p != '']
    if len(parts) == 3:
        parts = ['0'] + parts
    if len(parts) == 4:
        parts = [str(int(p)) if p.isdigit() else p for p in parts]
        return '/'.join(parts)
    return v

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')
t = m.start_write_trans()
root = maagic.get_root(t)

changes = []

# Fix base service interfaces
if hasattr(root, 'ospf') and hasattr(root.ospf, 'base'):
    for router_name in list(root.ospf.base.keys()):
        base = root.ospf.base[router_name]
        if hasattr(base, 'neighbor'):
            for neighbor_name in list(base.neighbor.keys()):
                nei = base.neighbor[neighbor_name]
                
                # Fix local_interface
                if hasattr(nei, 'local_interface') and nei.local_interface:
                    old = str(nei.local_interface)
                    new = normalize_interface(old)
                    if new != old:
                        nei.local_interface = new
                        changes.append(f"base[{router_name}].neighbor[{neighbor_name}].local-interface: {old} -> {new}")
                
                # Fix remote_interface
                if hasattr(nei, 'remote_interface') and nei.remote_interface:
                    old = str(nei.remote_interface)
                    new = normalize_interface(old)
                    if new != old:
                        nei.remote_interface = new
                        changes.append(f"base[{router_name}].neighbor[{neighbor_name}].remote-interface: {old} -> {new}")

# Fix link service interfaces  
if hasattr(root, 'ospf') and hasattr(root.ospf, 'link'):
    for link_name in list(root.ospf.link.keys()):
        link = root.ospf.link[link_name]
        if hasattr(link, 'device'):
            for device_name in list(link.device.keys()):
                d = link.device[device_name]
                if hasattr(d, 'interface') and d.interface:
                    old = str(d.interface)
                    new = normalize_interface(old)
                    if new != old:
                        d.interface = new
                        changes.append(f"link[{link_name}].device[{device_name}].interface: {old} -> {new}")

if changes:
    print("Changes to apply:")
    for c in changes:
        print(f"  - {c}")
    print(f"\nApplying {len(changes)} changes...")
    t.apply()
    print("✅ Changes applied successfully!")
else:
    print("No changes needed - all interfaces are already normalized")

m.end_user_session()

