#!/usr/bin/env python3
"""
Add New Devices to NSO
=======================

This script adds new IOS-XR devices to NSO configuration database.
Devices: node-1 to node-8, pce-11
All devices use cisco/cisco authentication.
"""

import os
import sys

# Set NSO environment variables
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add NSO Python API to Python path
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

# Import NSO modules
import ncs.maapi as maapi
import ncs.maagic as maagic

def add_devices_to_nso():
    """Add new devices to NSO configuration database."""
    
    # Device configuration: (device_name, ip_address)
    devices = [
        ('node-1', '198.18.1.41'),
        ('node-2', '198.18.1.42'),
        ('node-3', '198.18.1.43'),
        ('node-4', '198.18.1.44'),
        ('node-5', '198.18.1.45'),
        ('node-6', '198.18.1.46'),
        ('node-7', '198.18.1.47'),
        ('node-8', '198.18.1.48'),
        ('pce-11', '198.18.1.51'),
    ]
    
    print("=" * 60)
    print("Adding Devices to NSO")
    print("=" * 60)
    print(f"Total devices to add: {len(devices)}")
    print()
    
    try:
        # Create MAAPI session
        m = maapi.Maapi()
        m.start_user_session('cisco', 'add_devices_context')
        
        # Start write transaction
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        added_devices = []
        skipped_devices = []
        
        for device_name, ip_address in devices:
            try:
                # Check if device already exists
                if device_name in root.devices.device:
                    print(f"⚠️  Device '{device_name}' already exists, skipping...")
                    skipped_devices.append(device_name)
                    continue
                
                # Create device
                device = root.devices.device.create(device_name)
                
                # Set device type to IOS-XR CLI
                device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.52:cisco-iosxr-cli-7.52'
                
                # Set admin state to unlocked
                device.state.admin_state = 'unlocked'
                
                # Set authentication group (will use default authgroup with cisco/cisco)
                # Note: You may need to create/configure authgroup separately
                device.authgroup = 'default'
                
                # Configure SSH settings (if available)
                try:
                    # Try to set SSH host key check
                    if hasattr(device, 'ned_settings'):
                        ned_settings = device.ned_settings
                        if hasattr(ned_settings, 'ssh'):
                            ned_settings.ssh.host_key_check = False
                        elif hasattr(ned_settings, 'netconf'):
                            # For NETCONF devices, might use netconf settings
                            pass
                except Exception as ssh_error:
                    print(f"   ⚠️  Could not set SSH settings (may not be needed): {ssh_error}")
                
                # Set device address and port
                # For IOS-XR CLI devices, typically use port 22 (SSH)
                # For NETCONF, use port 830
                device.address = ip_address
                device.port = 22  # SSH port for CLI access
                
                # Alternative: If using NETCONF, use port 830
                # device.port = 830
                
                added_devices.append((device_name, ip_address))
                print(f"✅ Added device: {device_name} ({ip_address})")
                
            except Exception as e:
                print(f"❌ Error adding device '{device_name}': {e}")
                continue
        
        # Apply changes
        if added_devices:
            print()
            print("Committing changes to NSO...")
            t.apply()
            print("✅ Changes committed successfully!")
        else:
            print("No new devices to add.")
            t.abort()
        
        m.end_user_session()
        
        # Summary
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully added: {len(added_devices)} device(s)")
        for name, ip in added_devices:
            print(f"   - {name}: {ip}")
        
        if skipped_devices:
            print(f"\n⚠️  Skipped (already exist): {len(skipped_devices)} device(s)")
            for name in skipped_devices:
                print(f"   - {name}")
        
        print()
        print("Next steps:")
        print("1. Verify devices: ncs_cli -u admin -C 'show devices device *'")
        print("2. Connect to devices: Use 'connect_device' MCP tool")
        print("3. Sync from devices: Use 'sync_from_device' MCP tool")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to NSO: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure NSO is running: ncs --status")
        print("2. Check NSO connection: ncs_cli -u admin -C")
        return False

if __name__ == "__main__":
    success = add_devices_to_nso()
    sys.exit(0 if success else 1)

