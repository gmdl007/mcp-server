#!/usr/bin/env python3
"""
Sync-from all devices directly
==============================

This script performs sync-from operation for all devices to pull
their running configuration into NSO.
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

def sync_from_all_devices():
    """Perform sync-from operation for all devices"""
    
    devices = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5', 
               'node-6', 'node-7', 'node-8', 'pce-11']
    
    print('=' * 70)
    print('Syncing configuration from all devices')
    print('=' * 70)
    print(f'NSO Directory: {NSO_DIR}')
    print(f'Total devices: {len(devices)}')
    print()
    
    try:
        # Create MAAPI session
        m = maapi.Maapi()
        m.start_user_session('admin', 'sync_from_all_devices')
        
        results = []
        
        for device_name in devices:
            try:
                print(f'Syncing from {device_name}...', end=' ', flush=True)
                
                # Start a write transaction for the sync-from action
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                # Check if device exists
                if device_name not in root.devices.device:
                    print(f'❌ Device not found')
                    results.append((device_name, False, 'Device not found'))
                    t.abort()
                    continue
                
                device = root.devices.device[device_name]
                
                # Perform sync-from action
                # The sync-from is an action, so we need to invoke it
                sync_action = device.sync_from()
                result = sync_action.result
                
                if result:
                    print(f'✅ Success')
                    results.append((device_name, True, 'Success'))
                else:
                    info = sync_action.info if hasattr(sync_action, 'info') else 'Unknown error'
                    print(f'❌ Failed: {info}')
                    results.append((device_name, False, info))
                
                t.abort()  # Actions don't need transaction commit
                
            except Exception as e:
                print(f'❌ Error: {e}')
                results.append((device_name, False, str(e)))
        
        m.end_user_session()
        
        # Summary
        print()
        print('=' * 70)
        print('SUMMARY')
        print('=' * 70)
        successful = [r for r in results if r[1]]
        failed = [r for r in results if not r[1]]
        
        if successful:
            print(f'✅ Successfully synced: {len(successful)} device(s)')
            for name, _, _ in successful:
                print(f'   - {name}')
        
        if failed:
            print(f'\n❌ Failed to sync: {len(failed)} device(s)')
            for name, _, error in failed:
                print(f'   - {name}: {error}')
        
        print('=' * 70)
        
        return len(failed) == 0
        
    except Exception as e:
        print(f'\n❌ Error connecting to NSO: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = sync_from_all_devices()
    sys.exit(0 if success else 1)

