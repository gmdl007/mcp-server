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

print('=== Cleaning up sub-interfaces ===\n')

for device_name in ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']:
    if device_name in root.devices.device:
        device = root.devices.device[device_name]
        print(f'Processing {device_name}:')
        
        if hasattr(device, 'config') and hasattr(device.config, 'interface'):
            interfaces = device.config.interface
            
            # Delete GigabitEthernet subinterfaces (those with dots in the key)
            if hasattr(interfaces, 'GigabitEthernet'):
                ge_interfaces = list(interfaces.GigabitEthernet.keys())
                subifs_to_delete = []
                for ge_key in ge_interfaces:
                    ge_key_str = str(ge_key)
                    # Check if key contains a dot (subinterface notation like "0/0/0/0.100")
                    if '.' in ge_key_str:
                        subifs_to_delete.append(ge_key)
                
                if subifs_to_delete:
                    for ge_key in subifs_to_delete:
                        try:
                            del interfaces.GigabitEthernet[ge_key]
                            changes.append(f"{device_name}: Deleted GigabitEthernet/{ge_key}")
                            print(f"  ✅ Deleted GigabitEthernet/{ge_key}")
                        except Exception as e:
                            print(f"  ⚠️  Error deleting GigabitEthernet/{ge_key}: {e}")
                else:
                    print(f"  ℹ️  No subinterfaces found in GigabitEthernet")
            
            # Also check GigabitEthernet-subinterface container
            if hasattr(interfaces, 'GigabitEthernet_subinterface'):
                try:
                    # Iterate through the container to find subinterfaces
                    subif_container = interfaces.GigabitEthernet_subinterface
                    if hasattr(subif_container, 'GigabitEthernet'):
                        ge_subifs = list(subif_container.GigabitEthernet.keys())
                        for subif_key in ge_subifs:
                            try:
                                del subif_container.GigabitEthernet[subif_key]
                                changes.append(f"{device_name}: Deleted GigabitEthernet-subinterface/{subif_key}")
                                print(f"  ✅ Deleted GigabitEthernet-subinterface/{subif_key}")
                            except Exception as e:
                                print(f"  ⚠️  Error deleting subinterface {subif_key}: {e}")
                except Exception as e:
                    print(f"  ℹ️  Could not access subinterface container: {e}")

print('\n=== Applying Changes ===')
if changes:
    print(f"Total changes: {len(changes)}")
    try:
        t.apply()
        print("✅ All sub-interfaces deleted successfully!")
        print("\nChanges made:")
        for change in changes:
            print(f"  - {change}")
    except Exception as e:
        print(f"❌ Error applying changes: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No sub-interfaces found to delete")

m.end_user_session()
print("\n✅ Cleanup complete!")
print("Note: Use NSO CLI 'commit' to push changes to devices")

