#!/usr/bin/env python3
"""
Fix admin mode sync-from error for IOS-XR devices
==================================================

This script sets the NED setting read/admin-show-running-config to false
to resolve the "failed to enter admin mode" error during sync-from operations.

Error message:
  "failed to enter admin mode: ..."
  "Set ned-setting read/admin-show-running-config to false"
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

def fix_admin_mode_sync():
    """Set read/admin-show-running-config to false for all devices"""
    
    devices = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5', 
               'node-6', 'node-7', 'node-8', 'pce-11']
    
    print('=' * 70)
    print('Fixing admin mode sync-from error')
    print('=' * 70)
    print('Setting ned-setting: read/admin-show-running-config = false')
    print(f'NSO Directory: {NSO_DIR}')
    print(f'Total devices: {len(devices)}')
    print()
    
    try:
        # Create MAAPI session
        m = maapi.Maapi()
        m.start_user_session('admin', 'fix_admin_mode_sync')
        
        # Start write transaction
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        updated = []
        not_found = []
        errors = []
        
        for device_name in devices:
            try:
                # Check if device exists
                if device_name not in root.devices.device:
                    not_found.append(device_name)
                    print(f'⚠️  {device_name}: Device not found')
                    continue
                
                device = root.devices.device[device_name]
                
                # Access NED settings for cisco-iosxr-cli-7.61
                # The path is: ned-settings.cisco_ios_xr_meta__cisco_iosxr.read.admin_show_running_config
                try:
                    # Get ned-settings
                    if not hasattr(device, 'ned_settings'):
                        print(f'⚠️  {device_name}: ned-settings not available')
                        errors.append((device_name, 'ned-settings not available'))
                        continue
                    
                    ned_settings = device.ned_settings
                    
                    # Access the IOS-XR specific settings
                    # Path: ned-settings.cisco_ios_xr_meta__cisco_iosxr.read.admin_show_running_config
                    if hasattr(ned_settings, 'cisco_ios_xr_meta__cisco_iosxr'):
                        iosxr_settings = ned_settings.cisco_ios_xr_meta__cisco_iosxr
                        if hasattr(iosxr_settings, 'read'):
                            read_settings = iosxr_settings.read
                            if hasattr(read_settings, 'admin_show_running_config'):
                                read_settings.admin_show_running_config = False
                                print(f'✅ {device_name}: Set admin-show-running-config = false')
                                updated.append(device_name)
                            else:
                                errors.append((device_name, 'admin_show_running_config attribute not found'))
                                print(f'❌ {device_name}: admin_show_running_config attribute not found')
                        else:
                            errors.append((device_name, 'read settings not found'))
                            print(f'❌ {device_name}: read settings not found')
                    else:
                        errors.append((device_name, 'cisco_ios_xr_meta__cisco_iosxr settings not found'))
                        print(f'❌ {device_name}: cisco_ios_xr_meta__cisco_iosxr settings not found')
                    
                except Exception as e:
                    errors.append((device_name, str(e)))
                    print(f'❌ {device_name}: Error setting NED setting - {e}')
                
            except Exception as e:
                errors.append((device_name, str(e)))
                print(f'❌ {device_name}: Error - {e}')
        
        # Apply changes if any were made
        if updated:
            print()
            print('Committing changes to NSO...')
            t.apply()
            print('✅ Changes committed successfully!')
        else:
            print('\n⚠️  No devices were updated programmatically')
            if errors:
                print('\n⚠️  Manual configuration may be required')
            t.abort()
        
        # Summary
        print()
        print('=' * 70)
        print('SUMMARY')
        print('=' * 70)
        if updated:
            print(f'✅ Successfully updated: {len(updated)} device(s)')
            for name in updated:
                print(f'   - {name}')
        if not_found:
            print(f'\n⚠️  Devices not found: {len(not_found)} device(s)')
            for name in not_found:
                print(f'   - {name}')
        if errors:
            print(f'\n⚠️  Devices requiring manual configuration: {len(errors)} device(s)')
            for name, error in errors:
                print(f'   - {name}: {error}')
        
        m.end_user_session()
        
        # Provide manual configuration instructions
        if errors or not updated:
            print()
            print('=' * 70)
            print('MANUAL CONFIGURATION INSTRUCTIONS')
            print('=' * 70)
            print('If automatic configuration failed, set the NED setting manually:')
            print()
            print('In NSO CLI (ncs_cli -C -u admin):')
            print('  configure')
            for device_name in devices:
                print(f'  devices device {device_name} ned-settings cisco-iosxr-cli-7.61 read admin-show-running-config false')
            print('  commit')
            print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error connecting to NSO: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_admin_mode_sync()
    sys.exit(0 if success else 1)

