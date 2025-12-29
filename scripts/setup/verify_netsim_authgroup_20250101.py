#!/usr/bin/env python3
"""
Verify Netsim Devices Authgroup
================================

This script verifies that the authgroup is working by:
1. Fetching SSH host keys
2. Connecting to devices
3. Performing sync-from
"""

import os
import sys

NSO_DIR = '/Users/gudeng/NCS-6413'
NSO_RUN_DIR = '/Users/gudeng/ncs-run-6413'

os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

import ncs.maapi as maapi
import ncs.maagic as maagic

def verify_authgroup():
    """Verify authgroup is working for netsim devices"""
    
    devices = ['xr9kv0', 'xr9kv1', 'xr9kv2']
    
    print('=' * 70)
    print('Verifying Netsim Devices Authgroup')
    print('=' * 70)
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'verify_netsim_authgroup')
        
        results = {}
        
        for device_name in devices:
            print(f'Testing {device_name}...')
            try:
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                if device_name not in root.devices.device:
                    print(f'   ❌ Device {device_name} not found')
                    results[device_name] = 'not_found'
                    t.abort()
                    continue
                
                device = root.devices.device[device_name]
                
                # Check authgroup
                authgroup = device.authgroup
                print(f'   Authgroup: {authgroup}')
                
                # Fetch SSH host keys
                print(f'   Fetching SSH host keys...')
                try:
                    device.ssh.fetch_host_keys()
                    print(f'   ✅ SSH host keys fetched')
                except Exception as e:
                    print(f'   ⚠️  SSH host keys: {e}')
                
                t.apply()
                
                # Connect to device
                print(f'   Connecting to device...')
                try:
                    t = m.start_write_trans()
                    root = maagic.get_root(t)
                    device = root.devices.device[device_name]
                    device.connect()
                    print(f'   ✅ Connected successfully')
                    t.apply()
                    results[device_name] = 'connected'
                except Exception as e:
                    print(f'   ❌ Connection failed: {e}')
                    results[device_name] = f'connection_error: {e}'
                    t.abort()
                
                # Try sync-from
                print(f'   Performing sync-from...')
                try:
                    t = m.start_write_trans()
                    root = maagic.get_root(t)
                    device = root.devices.device[device_name]
                    result = device.sync_from()
                    if result.result:
                        print(f'   ✅ Sync-from successful')
                        results[device_name] = 'sync_success'
                    else:
                        print(f'   ⚠️  Sync-from result: {result.result}, info: {result.info}')
                        results[device_name] = f'sync_warning: {result.info}'
                    t.apply()
                except Exception as e:
                    print(f'   ⚠️  Sync-from error: {e}')
                    results[device_name] = f'sync_error: {e}'
                    try:
                        t.abort()
                    except:
                        pass
                
            except Exception as e:
                print(f'   ❌ Error: {e}')
                results[device_name] = f'error: {e}'
            
            print()
        
        m.end_user_session()
        
        # Summary
        print('=' * 70)
        print('SUMMARY')
        print('=' * 70)
        for device_name, result in results.items():
            if 'success' in result or 'connected' in result:
                print(f'✅ {device_name}: {result}')
            else:
                print(f'⚠️  {device_name}: {result}')
        
        print()
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_authgroup()
    sys.exit(0 if success else 1)

