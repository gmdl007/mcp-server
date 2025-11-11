#!/usr/bin/env python3
"""
Fix Netsim Authgroup Configuration
===================================

Netsim devices use admin/admin credentials.
This script creates a "netsim" authgroup with admin/admin using default-map.

IMPORTANT: For netsim devices, use "default-map" (not "umap default").
The default-map is the default authentication mapping used when no specific
umap matches. The umap entries are for user-specific mappings.

Configuration:
  devices authgroups group netsim
    default-map remote-name admin
    default-map remote-password admin
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

def fix_netsim_authgroup():
    """Create netsim authgroup and update devices"""
    
    devices = ['xr9kv0', 'xr9kv1', 'xr9kv2']
    
    print('=' * 70)
    print('Fixing Netsim Authgroup Configuration')
    print('=' * 70)
    print()
    print('Netsim devices use admin/admin credentials')
    print('Creating "netsim" authgroup with admin/admin')
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'fix_netsim_authgroup')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Create or update netsim authgroup
        if 'netsim' in root.devices.authgroups.group:
            authgroup = root.devices.authgroups.group['netsim']
            print('⚠️  Authgroup "netsim" already exists, updating...')
        else:
            authgroup = root.devices.authgroups.group.create('netsim')
            print('✅ Creating authgroup "netsim"...')
        
        # Set default-map with admin/admin
        # For netsim devices, use default-map (not umap default)
        if hasattr(authgroup, 'default_map'):
            authgroup.default_map.remote_name = 'admin'
            authgroup.default_map.remote_password = 'admin'
        else:
            # Create default-map if it doesn't exist
            # Note: default-map is created automatically when we set its values
            authgroup.default_map.remote_name = 'admin'
            authgroup.default_map.remote_password = 'admin'
        
        print('   ✅ Configured default-map: remote-name=admin, remote-password=admin')
        
        # Update devices to use netsim authgroup
        print()
        print('Updating devices to use "netsim" authgroup...')
        for device_name in devices:
            if device_name in root.devices.device:
                device = root.devices.device[device_name]
                device.authgroup = 'netsim'
                print(f'   ✅ {device_name}: Updated to use "netsim" authgroup')
            else:
                print(f'   ⚠️  {device_name}: Device not found')
        
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
        print('✅ Created/updated authgroup "netsim" with admin/admin')
        print('✅ Updated all netsim devices to use "netsim" authgroup')
        print()
        print('You can now test the connection:')
        print('  devices device xr9kv0 connect')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_netsim_authgroup()
    sys.exit(0 if success else 1)

