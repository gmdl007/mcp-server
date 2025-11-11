#!/usr/bin/env python3
"""
Add devices to NSO with cisco authgroup and cisco-iosxr-cli-7.61 NED
=====================================================================

This script adds devices (node-1 through node-8, pce-11) to NSO with:
- Authgroup: cisco
- NED: cisco-iosxr-cli-7.61
- Port: 22 (SSH)
"""

import os
import sys
from datetime import datetime

# Determine NSO directory (prefer NCS-6413)
NSO_DIR = '/Users/gudeng/NCS-6413'
if not os.path.exists(NSO_DIR):
    NSO_DIR = '/Users/gudeng/NCS-614'

os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

import ncs.maapi as maapi
import ncs.maagic as maagic

def add_devices_with_cisco_auth():
    """Add devices to NSO with cisco authgroup and cisco-iosxr-cli-7.61 NED"""
    
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
    
    print('=' * 70)
    print('Adding Devices to NSO with cisco authgroup and cisco-iosxr-cli-7.61 NED')
    print('=' * 70)
    print(f'NSO Directory: {NSO_DIR}')
    print(f'Total devices: {len(devices)}')
    print(f'Authgroup: cisco')
    print(f'NED: cisco-iosxr-cli-7.61')
    print()
    
    try:
        # Create MAAPI session
        m = maapi.Maapi()
        m.start_user_session('admin', 'add_devices_cisco_auth')
        
        # Start write transaction
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        added = []
        updated = []
        errors = []
        
        for device_name, ip_address in devices:
            try:
                # Check if device already exists
                if device_name in root.devices.device:
                    device = root.devices.device[device_name]
                    print(f'⚠️  {device_name}: Already exists, updating...')
                    updated.append(device_name)
                else:
                    # Create new device
                    device = root.devices.device.create(device_name)
                    print(f'✅ {device_name}: Creating new device...')
                    added.append(device_name)
                
                # Configure device address and port
                device.address = ip_address
                device.port = 22
                
                # Set authgroup to 'cisco'
                device.authgroup = 'cisco'
                
                # Set admin state to unlocked
                device.state.admin_state = 'unlocked'
                
                # Remove netconf device-type if exists
                if hasattr(device.device_type, 'netconf'):
                    try:
                        del device.device_type.netconf
                    except Exception as e:
                        pass
                
                # Set CLI device-type with cisco-iosxr-cli-7.61 NED
                if not hasattr(device.device_type, 'cli'):
                    device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61'
                else:
                    device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61'
                
                # Configure SSH settings if available
                try:
                    if hasattr(device, 'ned_settings'):
                        ned_settings = device.ned_settings
                        if hasattr(ned_settings, 'ssh'):
                            ned_settings.ssh.host_key_check = False
                except Exception as ssh_error:
                    # SSH settings may not be needed or available
                    pass
                
                print(f'   ✅ {device_name}: Configured - {ip_address}:22, authgroup: cisco, NED: cisco-iosxr-cli-7.61')
                
            except Exception as e:
                errors.append((device_name, str(e)))
                print(f'   ❌ {device_name}: Error - {e}')
        
        # Apply changes
        if added or updated:
            print()
            print('Committing changes to NSO...')
            t.apply()
            print('✅ Changes committed successfully!')
        else:
            print('\n⚠️  No devices were added or updated')
            t.abort()
        
        # Summary
        print()
        print('=' * 70)
        print('SUMMARY')
        print('=' * 70)
        if added:
            print(f'✅ Successfully added: {len(added)} device(s)')
            for name in added:
                print(f'   - {name}')
        if updated:
            print(f'✅ Successfully updated: {len(updated)} device(s)')
            for name in updated:
                print(f'   - {name}')
        if errors:
            print(f'\n❌ Errors ({len(errors)}):')
            for dev_name, error in errors:
                print(f'   - {dev_name}: {error}')
        
        m.end_user_session()
        
        print()
        print('=' * 70)
        print('NEXT STEPS')
        print('=' * 70)
        print('1. Fetch SSH host keys:')
        for device_name, _ in devices:
            print(f'   devices device {device_name} ssh fetch-host-keys')
        print()
        print('2. Connect to devices:')
        for device_name, _ in devices:
            print(f'   devices device {device_name} connect')
        print()
        print('3. Sync configuration from devices:')
        for device_name, _ in devices:
            print(f'   devices device {device_name} sync-from')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error connecting to NSO: {e}')
        import traceback
        traceback.print_exc()
        print()
        print('Troubleshooting:')
        print('1. Ensure NSO is running: ncs --status')
        print('2. Check NSO connection: ncs_cli -u admin -C')
        print('3. Verify authgroup exists: show running-config devices authgroups group cisco')
        return False

if __name__ == '__main__':
    success = add_devices_with_cisco_auth()
    sys.exit(0 if success else 1)

