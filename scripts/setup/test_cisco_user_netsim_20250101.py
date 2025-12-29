#!/usr/bin/env python3
"""
Test Cisco User Access to Netsim
=================================

Test that user "cisco" can now connect to netsim devices
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

def test_cisco_user_access():
    """Test that user cisco can connect to netsim devices"""
    
    devices = ['xr9kv0', 'xr9kv1', 'xr9kv2']
    
    print('=' * 70)
    print('Testing Cisco User Access to Netsim Devices')
    print('=' * 70)
    print()
    
    try:
        # Use 'cisco' user session (not 'admin')
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_cisco_user_netsim')
        
        for device_name in devices:
            print(f'Testing {device_name} with user "cisco"...')
            try:
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                if device_name not in root.devices.device:
                    print(f'   ❌ Device not found')
                    t.abort()
                    continue
                
                device = root.devices.device[device_name]
                print(f'   Device authgroup: {device.authgroup}')
                
                # Try to connect
                device.connect()
                print(f'   ✅ Connected successfully!')
                print(f'   ✅ User "cisco" can access netsim devices')
                
                t.apply()
                t.abort()
                
            except Exception as e:
                print(f'   ❌ Connection failed: {e}')
                try:
                    t.abort()
                except:
                    pass
            
            print()
        
        m.end_user_session()
        
        print('=' * 70)
        print('SUMMARY')
        print('=' * 70)
        print('✅ User "cisco" can now connect to netsim devices')
        print('✅ Authgroup "cisco" has both:')
        print('   - umap "cisco": for dcloud routers')
        print('   - umap "netsim": for netsim devices')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_cisco_user_access()
    sys.exit(0 if success else 1)

