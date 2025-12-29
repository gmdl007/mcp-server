#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/Users/gudeng/NCS-614/src/ncs/pyapi')
os.environ['NCS_DIR'] = '/Users/gudeng/NCS-614'
from ncs import maapi, maagic
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Deleting All Interfaces (including Loopback0) ===")
print(f"Timestamp: {timestamp}\n")

m = maapi.Maapi()
m.start_user_session('cisco', 'test_context_1')
t = m.start_write_trans()
root = maagic.get_root(t)

changes = []
devices = ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']

for device_name in devices:
    if device_name not in root.devices.device:
        print(f"⚠️  Device {device_name} not found, skipping...")
        continue
    
    device = root.devices.device[device_name]
    print(f"\nProcessing {device_name}:")
    
    if hasattr(device, 'config') and hasattr(device.config, 'interface'):
        interfaces = device.config.interface
        
        # Get all interface types
        if_containers = []
        
        # Check for GigabitEthernet
        if hasattr(interfaces, 'GigabitEthernet'):
            if_containers.append(('GigabitEthernet', interfaces.GigabitEthernet))
        
        # Check for Loopback
        if hasattr(interfaces, 'Loopback'):
            if_containers.append(('Loopback', interfaces.Loopback))
        
        # Check for other interface types if they exist
        for attr_name in dir(interfaces):
            if not attr_name.startswith('_') and attr_name not in ['GigabitEthernet', 'Loopback']:
                attr = getattr(interfaces, attr_name)
                if hasattr(attr, 'keys') or hasattr(attr, '__iter__'):
                    if_containers.append((attr_name, attr))
        
        # Delete all interfaces
        for if_type, if_container in if_containers:
            try:
                if hasattr(if_container, 'keys'):
                    keys = list(if_container.keys())
                else:
                    # Try to iterate if it doesn't have keys
                    keys = list(if_container) if hasattr(if_container, '__iter__') else []
                
                for key in keys:
                    try:
                        del if_container[key]
                        changes.append(f"{device_name}: Deleted {if_type}/{key}")
                        print(f"  ✅ Deleted {if_type}/{key}")
                    except Exception as e:
                        print(f"  ⚠️  Error deleting {if_type}/{key}: {e}")
                        changes.append(f"{device_name}: Error deleting {if_type}/{key}: {e}")
            except Exception as e:
                print(f"  ⚠️  Error processing {if_type}: {e}")

print('\n=== Applying Changes ===')
if changes:
    print(f"Total changes: {len(changes)}")
    try:
        t.apply()
        print("✅ All interfaces deleted successfully!")
        print("\nChanges made:")
        for change in changes:
            print(f"  - {change}")
    except Exception as e:
        print(f"❌ Error applying changes: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No interfaces found to delete")

m.end_user_session()
print("\n✅ Cleanup complete!")
print("Note: Use NSO CLI 'commit' to push changes to devices")

