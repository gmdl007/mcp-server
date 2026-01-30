#!/usr/bin/env python3
"""
Update iosv-dcloud device to use IOS NED
=======================================

This script updates the iosv-dcloud device to use cisco-ios-cli-3.8 NED
instead of cisco-iosxr-cli-7.61 NED.
"""

import os
import sys

NSO_DIR = '/Users/gudeng/NCS-6413'
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

import ncs.maapi as maapi
import ncs.maagic as maagic

def update_iosv_device():
    """Update iosv-dcloud to use IOS NED"""
    
    device_name = 'iosv-dcloud'
    ios_ned_id = 'cisco-ios-cli-3.8:cisco-ios-cli-3.8'
    
    print('=' * 70)
    print('Updating iosv-dcloud Device to Use IOS NED')
    print('=' * 70)
    print(f'Device: {device_name}')
    print(f'New NED: {ios_ned_id}')
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'update_iosv_device')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        if device_name not in root.devices.device:
            print(f'❌ Device {device_name} not found in NSO')
            t.abort()
            m.end_user_session()
            return False
        
        device = root.devices.device[device_name]
        
        print(f'✅ Found device: {device_name}')
        print(f'   Current address: {device.address}')
        print(f'   Current port: {device.port}')
        print(f'   Current authgroup: {device.authgroup}')
        
        # Check current device type
        if hasattr(device.device_type, 'cli'):
            current_ned = device.device_type.cli.ned_id
            print(f'   Current NED: {current_ned}')
        else:
            print('   Current NED: Not configured')
            current_ned = None
        
        # Remove other device-types if they exist
        if hasattr(device.device_type, 'netconf'):
            try:
                del device.device_type.netconf
                print('   ✅ Removed netconf device-type')
            except Exception as e:
                pass
        
        if hasattr(device.device_type, 'generic'):
            try:
                del device.device_type.generic
                print('   ✅ Removed generic device-type')
            except Exception as e:
                pass
        
        if hasattr(device.device_type, 'snmp'):
            try:
                del device.device_type.snmp
                print('   ✅ Removed snmp device-type')
            except Exception as e:
                pass
        
        # Set CLI device-type to IOS NED
        if not hasattr(device.device_type, 'cli'):
            device.device_type.cli.ned_id = ios_ned_id
        else:
            device.device_type.cli.ned_id = ios_ned_id
        
        print(f'   ✅ Updated NED to: {ios_ned_id}')
        
        # Commit changes
        print()
        print('Committing changes...')
        t.apply()
        print('✅ Changes committed successfully!')
        
        m.end_user_session()
        
        # Summary
        print()
        print('=' * 70)
        print('SUMMARY')
        print('=' * 70)
        print(f'✅ Successfully updated {device_name} to use IOS NED')
        print(f'   Old NED: {current_ned}')
        print(f'   New NED: {ios_ned_id}')
        print()
        print('Next steps:')
        print('1. Disconnect and reconnect the device:')
        print(f'   devices device {device_name} disconnect')
        print(f'   devices device {device_name} connect')
        print()
        print('2. Fetch SSH host keys:')
        print(f'   devices device {device_name} ssh fetch-host-keys')
        print()
        print('3. Sync configuration:')
        print(f'   devices device {device_name} sync-from')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = update_iosv_device()
    sys.exit(0 if success else 1)
