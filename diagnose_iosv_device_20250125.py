#!/usr/bin/env python3
"""
Diagnose iosv-dcloud connection issues
======================================

This script checks the iosv-dcloud device configuration step-by-step
to identify connection issues.
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

def diagnose_iosv_device():
    """Step-by-step diagnosis of iosv-dcloud"""
    
    device_name = 'iosv-dcloud'
    
    print('=' * 70)
    print('Step-by-Step Diagnosis: iosv-dcloud')
    print('=' * 70)
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'diagnose_iosv')
        
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        if device_name not in root.devices.device:
            print(f'❌ Step 1: Device {device_name} not found in NSO')
            m.end_user_session()
            return False
        
        device = root.devices.device[device_name]
        
        # Step 1: Basic Configuration
        print('Step 1: Basic Device Configuration')
        print('-' * 70)
        print(f'✅ Device exists: {device_name}')
        print(f'   Address: {device.address}')
        print(f'   Port: {device.port}')
        print(f'   Authgroup: {device.authgroup}')
        print(f'   Admin State: {device.state.admin_state}')
        print()
        
        # Step 2: Device Type
        print('Step 2: Device Type Configuration')
        print('-' * 70)
        if hasattr(device.device_type, 'cli'):
            ned_id = device.device_type.cli.ned_id
            print(f'✅ Device Type: CLI')
            print(f'   NED ID: {ned_id}')
        elif hasattr(device.device_type, 'netconf'):
            ned_id = device.device_type.netconf.ned_id
            print(f'⚠️  Device Type: NETCONF')
            print(f'   NED ID: {ned_id}')
        else:
            print('❌ Device Type: Not configured')
        print()
        
        # Step 3: Authgroup Details
        print('Step 3: Authgroup Configuration')
        print('-' * 70)
        authgroup_name = device.authgroup
        if authgroup_name in root.devices.authgroups.group:
            authgroup = root.devices.authgroups.group[authgroup_name]
            print(f'✅ Authgroup "{authgroup_name}" exists')
            
            # Check for gudeng umap
            if hasattr(authgroup, 'umap') and 'gudeng' in authgroup.umap:
                umap = authgroup.umap['gudeng']
                print(f'✅ Found umap for user "gudeng"')
                print(f'   Remote name: {umap.remote_name}')
            else:
                print(f'⚠️  No umap found for user "gudeng"')
            
            # Check for cisco umap
            if hasattr(authgroup, 'umap') and 'cisco' in authgroup.umap:
                umap = authgroup.umap['cisco']
                print(f'✅ Found umap for user "cisco"')
                print(f'   Remote name: {umap.remote_name}')
            
            # Check default-map
            if hasattr(authgroup, 'default_map'):
                if hasattr(authgroup.default_map, 'remote_name'):
                    print(f'✅ Default-map configured')
                    print(f'   Remote name: {authgroup.default_map.remote_name}')
        else:
            print(f'❌ Authgroup "{authgroup_name}" not found')
        print()
        
        # Step 4: SSH Configuration
        print('Step 4: SSH Configuration')
        print('-' * 70)
        if hasattr(device, 'ssh') and hasattr(device.ssh, 'host_key'):
            host_keys = device.ssh.host_key
            if len(host_keys) > 0:
                print(f'✅ SSH host keys stored: {len(host_keys)} key(s)')
                for i, key in enumerate(host_keys, 1):
                    if hasattr(key, 'algorithm'):
                        print(f'   {i}. Algorithm: {key.algorithm}')
            else:
                print('⚠️  No SSH host keys stored')
        else:
            print('⚠️  No SSH host keys stored')
        print()
        
        # Step 5: NED Settings
        print('Step 5: NED Settings')
        print('-' * 70)
        if hasattr(device, 'ned_settings'):
            ned_settings = device.ned_settings
            print('✅ NED settings exist')
            if hasattr(ned_settings, 'ssh'):
                if hasattr(ned_settings.ssh, 'host_key_check'):
                    print(f'   SSH host_key_check: {ned_settings.ssh.host_key_check}')
        else:
            print('⚠️  No NED settings configured')
        print()
        
        # Step 6: Device State
        print('Step 6: Device Connection State')
        print('-' * 70)
        state = device.state
        print(f'Reached: {state.reached}')
        print(f'Last Connect: {state.last_connect}')
        print(f'Last Disconnect: {state.last_disconnect}')
        if hasattr(state, 'last_connect_result'):
            print(f'Last Connect Result: {state.last_connect_result}')
        print()
        
        t.finish()
        m.end_user_session()
        
        # Recommendations
        print('=' * 70)
        print('DIAGNOSIS SUMMARY')
        print('=' * 70)
        print('The SSH connection is being closed during key exchange.')
        print('This could be due to:')
        print('1. SSH service not properly configured on the device')
        print('2. Device rejecting SSH connections')
        print('3. Authentication mismatch')
        print('4. IOS device needing different connection parameters')
        print()
        print('RECOMMENDATIONS:')
        print('1. Verify SSH is enabled on the device:')
        print('   - Check: ip ssh version 2')
        print('   - Check: line vty configuration')
        print('2. Try connecting manually:')
        print('   ssh cisco@198.18.1.11')
        print('3. Check if device requires different credentials')
        print('4. Verify the device is actually an IOS device (not IOS-XE)')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = diagnose_iosv_device()
    sys.exit(0 if success else 1)
