#!/usr/bin/env python3
"""
Add gudeng user to cisco authgroup
===================================

This script adds a umap entry for user 'gudeng' to the 'cisco' authgroup
so that user 'gudeng' can access devices using the 'cisco' authgroup.
"""

import os
import sys
from datetime import datetime

# NSO 6.4.1.3 directory
NSO_DIR = '/Users/gudeng/NCS-6413'

os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

import ncs.maapi as maapi
import ncs.maagic as maagic

def add_gudeng_to_cisco_authgroup():
    """Add umap entry for gudeng user to cisco authgroup"""
    
    print('=' * 70)
    print('Adding gudeng user to cisco authgroup')
    print('=' * 70)
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'add_gudeng_authgroup')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Check if cisco authgroup exists
        if 'cisco' not in root.devices.authgroups.group:
            print('❌ Authgroup "cisco" does not exist')
            print('   Please create it first')
            t.abort()
            m.end_user_session()
            return False
        
        authgroup = root.devices.authgroups.group['cisco']
        print('✅ Authgroup "cisco" exists')
        
        # Check if umap for 'cisco' exists to get the credentials
        if 'cisco' in authgroup.umap:
            cisco_umap = authgroup.umap['cisco']
            remote_name = cisco_umap.remote_name
            remote_password = cisco_umap.remote_password
            print(f'✅ Found existing umap "cisco"')
            print(f'   Remote name: {remote_name}')
            print(f'   Remote password: {"*" * len(str(remote_password))}')
        else:
            print('⚠️  No umap "cisco" found, using default values')
            remote_name = 'cisco'
            # We'll need to prompt or use existing password
            # For now, let's check if there's a default-map
            if hasattr(authgroup, 'default_map') and hasattr(authgroup.default_map, 'remote_name'):
                remote_name = authgroup.default_map.remote_name
                remote_password = authgroup.default_map.remote_password
            else:
                print('❌ No credentials found in cisco authgroup')
                print('   Cannot determine what credentials to use')
                t.abort()
                m.end_user_session()
                return False
        
        # Add umap for 'gudeng' user
        if 'gudeng' in authgroup.umap:
            print('⚠️  umap "gudeng" already exists, updating...')
            gudeng_umap = authgroup.umap['gudeng']
        else:
            print('✅ Creating umap "gudeng"...')
            gudeng_umap = authgroup.umap.create('gudeng')
        
        # Set credentials (same as cisco user)
        gudeng_umap.remote_name = remote_name
        gudeng_umap.remote_password = remote_password
        print(f'✅ Configured umap "gudeng" with remote-name: {remote_name}')
        
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
        print('✅ Added umap "gudeng" to authgroup "cisco"')
        print('✅ User "gudeng" can now access devices using "cisco" authgroup')
        print()
        print('Authgroup "cisco" now has:')
        if 'cisco' in authgroup.umap:
            print('  - umap "cisco": for cisco user')
        print('  - umap "gudeng": for gudeng user (NEW)')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = add_gudeng_to_cisco_authgroup()
    sys.exit(0 if success else 1)
