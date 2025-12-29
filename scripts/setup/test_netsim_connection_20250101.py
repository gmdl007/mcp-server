#!/usr/bin/env python3
"""
Test Netsim Connection
======================

Quick test to verify netsim devices are accessible
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

def test_connection():
    """Test connection to netsim devices"""
    
    devices = ['xr9kv0', 'xr9kv1', 'xr9kv2']
    
    print('=' * 70)
    print('Testing Netsim Device Connections')
    print('=' * 70)
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_netsim_connection')
        
        for device_name in devices:
            print(f'Testing {device_name}...')
            try:
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                if device_name not in root.devices.device:
                    print(f'   ❌ Device not found in NSO')
                    t.abort()
                    continue
                
                device = root.devices.device[device_name]
                print(f'   Address: {device.address}:{device.port}')
                print(f'   Authgroup: {device.authgroup}')
                
                # Try connect
                print(f'   Connecting...')
                device.connect()
                print(f'   ✅ Connected successfully!')
                t.apply()
                t.abort()
                
                # Try check-sync
                print(f'   Checking sync...')
                t = m.start_write_trans()
                root = maagic.get_root(t)
                device = root.devices.device[device_name]
                result = device.check_sync()
                if result.result:
                    print(f'   ✅ Check-sync: {result.result}')
                else:
                    print(f'   ⚠️  Check-sync: {result.result}, info: {result.info}')
                t.abort()
                
            except Exception as e:
                print(f'   ❌ Error: {e}')
            
            print()
        
        m.end_user_session()
        
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)

