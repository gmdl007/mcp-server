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

changes = []

for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        print(f'\n=== Processing {device_name} ===')
        
        # Delete OSPF configuration
        if hasattr(device, 'config') and hasattr(device.config, 'router'):
            if hasattr(device.config.router, 'ospf'):
                try:
                    device.config.router.ospf.delete()
                    changes.append(f"{device_name}: Deleted OSPF configuration")
                    print(f"  ✅ Deleted OSPF configuration")
                except Exception as e:
                    print(f"  ⚠️  Error deleting OSPF: {e}")
        
        # Delete interfaces (except Loopback0)
        if hasattr(device, 'config') and hasattr(device.config, 'interface'):
            interfaces = device.config.interface
            
            # Delete all GigabitEthernet interfaces
            if hasattr(interfaces, 'GigabitEthernet'):
                ge_interfaces = list(interfaces.GigabitEthernet.keys())
                for ge_id in ge_interfaces:
                    try:
                        del interfaces.GigabitEthernet[ge_id]
                        changes.append(f"{device_name}: Deleted GigabitEthernet/{ge_id}")
                        print(f"  ✅ Deleted GigabitEthernet/{ge_id}")
                    except Exception as e:
                        print(f"  ⚠️  Error deleting GigabitEthernet/{ge_id}: {e}")
            
            # Delete all Loopback interfaces except Loopback0
            if hasattr(interfaces, 'Loopback'):
                loopback_interfaces = list(interfaces.Loopback.keys())
                for lo_id in loopback_interfaces:
                    if lo_id != '0':  # Keep Loopback0
                        try:
                            del interfaces.Loopback[lo_id]
                            changes.append(f"{device_name}: Deleted Loopback/{lo_id}")
                            print(f"  ✅ Deleted Loopback/{lo_id}")
                        except Exception as e:
                            print(f"  ⚠️  Error deleting Loopback/{lo_id}: {e}")
                    else:
                        print(f"  ℹ️  Kept Loopback/0")

print('\n=== Applying Changes ===')
if changes:
    print(f"Total changes: {len(changes)}")
    try:
        t.apply()
        print("✅ All changes applied successfully!")
        print("\nChanges made:")
        for change in changes:
            print(f"  - {change}")
    except Exception as e:
        print(f"❌ Error applying changes: {e}")
else:
    print("No changes to apply")

m.end_user_session()
print("\n✅ Cleanup complete!")
print("Note: Use NSO CLI 'commit' to push changes to devices")

