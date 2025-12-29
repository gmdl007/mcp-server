#!/usr/bin/env python3
"""
Fix Netsim SSH Host Keys
========================

Fetch SSH host keys for netsim devices
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

def fix_ssh_keys():
    """Fetch SSH host keys for netsim devices"""
    
    devices = ['xr9kv0', 'xr9kv1', 'xr9kv2']
    
    print('=' * 70)
    print('Fetching SSH Host Keys for Netsim Devices')
    print('=' * 70)
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('cisco', 'fix_netsim_ssh_keys')
        
        for device_name in devices:
            print(f'Fetching SSH keys for {device_name}...')
            try:
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                if device_name not in root.devices.device:
                    print(f'   ❌ Device not found')
                    t.abort()
                    continue
                
                device = root.devices.device[device_name]
                
                # Fetch SSH host keys
                result = device.ssh.fetch_host_keys()
                if result.result:
                    print(f'   ✅ SSH host keys fetched successfully')
                else:
                    print(f'   ⚠️  Result: {result.result}, info: {result.info}')
                
                t.apply()
                
            except Exception as e:
                print(f'   ❌ Error: {e}')
            
            print()
        
        m.end_user_session()
        
        print('=' * 70)
        print('✅ SSH host keys updated')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_ssh_keys()
    sys.exit(0 if success else 1)

