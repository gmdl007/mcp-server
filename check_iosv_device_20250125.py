#!/usr/bin/env python3
"""
Check and fix iosv-dcloud device configuration
==============================================

This script checks the iosv-dcloud device configuration and attempts
to diagnose SSH connection issues.
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

def check_iosv_device():
    """Check iosv-dcloud device configuration"""
    
    print('=' * 70)
    print('Checking iosv-dcloud Device Configuration')
    print('=' * 70)
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'check_iosv_device')
        
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        if 'iosv-dcloud' not in root.devices.device:
            print('❌ Device iosv-dcloud not found in NSO')
            m.end_user_session()
            return False
        
        device = root.devices.device['iosv-dcloud']
        
        print('Device Configuration:')
        print('-' * 70)
        print(f'Name: iosv-dcloud')
        print(f'Address: {device.address}')
        print(f'Port: {device.port}')
        print(f'Authgroup: {device.authgroup}')
        print(f'Admin State: {device.state.admin_state}')
        
        # Check device type
        if hasattr(device.device_type, 'cli'):
            ned_id = device.device_type.cli.ned_id
            print(f'Device Type: {ned_id}')
        elif hasattr(device.device_type, 'netconf'):
            ned_id = device.device_type.netconf.ned_id
            print(f'Device Type: {ned_id}')
        else:
            print('Device Type: Not configured')
        
        # Check state
        print()
        print('Device State:')
        print('-' * 70)
        state = device.state
        print(f'Reached: {state.reached}')
        print(f'Last Connect: {state.last_connect}')
        print(f'Last Disconnect: {state.last_disconnect}')
        if hasattr(state, 'last_connect_result'):
            print(f'Last Connect Result: {state.last_connect_result}')
        
        # Check SSH host keys
        print()
        print('SSH Host Keys:')
        print('-' * 70)
        if hasattr(device, 'ssh') and hasattr(device.ssh, 'host_key'):
            host_keys = device.ssh.host_key
            if len(host_keys) > 0:
                print(f'✅ Found {len(host_keys)} SSH host key(s)')
                for i, key in enumerate(host_keys, 1):
                    if hasattr(key, 'algorithm'):
                        print(f'   {i}. Algorithm: {key.algorithm}')
            else:
                print('⚠️  No SSH host keys stored')
        else:
            print('⚠️  No SSH host keys stored')
        
        t.finish()
        m.end_user_session()
        
        print()
        print('=' * 70)
        print('DIAGNOSIS')
        print('=' * 70)
        print('The device is configured with IOS-XR NED, but "iosv" suggests')
        print('it might be an IOS device. The SSH connection failure could be due to:')
        print('1. Wrong NED type (IOS device using IOS-XR NED)')
        print('2. SSH service not properly configured on the device')
        print('3. Device not ready or SSH not enabled')
        print()
        print('RECOMMENDATIONS:')
        print('1. Verify the device type (IOS vs IOS-XR)')
        print('2. Check if SSH is enabled on the device')
        print('3. Try connecting manually: ssh cisco@198.18.1.11')
        print('4. If it\'s IOS, you may need to change the NED type')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_iosv_device()
    sys.exit(0 if success else 1)
