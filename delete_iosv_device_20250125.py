#!/usr/bin/env python3
"""
Delete iosv-dcloud device from NSO
===================================

This script completely removes the iosv-dcloud device from NSO.
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

def delete_iosv_device():
    """Delete iosv-dcloud device from NSO"""
    
    device_name = 'iosv-dcloud'
    
    print('=' * 70)
    print('Deleting iosv-dcloud Device from NSO')
    print('=' * 70)
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'delete_iosv_device')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        if device_name not in root.devices.device:
            print(f'⚠️  Device {device_name} not found in NSO')
            t.abort()
            m.end_user_session()
            return False
        
        device = root.devices.device[device_name]
        
        print(f'✅ Found device: {device_name}')
        print(f'   Address: {device.address}')
        print(f'   Port: {device.port}')
        print()
        
        # Delete the device
        print(f'Deleting device {device_name}...')
        del root.devices.device[device_name]
        print(f'✅ Device {device_name} deleted from configuration')
        
        # Commit changes
        print()
        print('Committing changes...')
        t.apply()
        print('✅ Changes committed successfully!')
        
        m.end_user_session()
        
        print()
        print('=' * 70)
        print('SUMMARY')
        print('=' * 70)
        print(f'✅ Successfully deleted device: {device_name}')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = delete_iosv_device()
    sys.exit(0 if success else 1)
