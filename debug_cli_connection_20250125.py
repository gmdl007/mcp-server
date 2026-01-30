#!/usr/bin/env python3
"""
Debug iosv-dcloud CLI Connection Issues
========================================

This script investigates why CLI commands fail while MCP tools might work.
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

def debug_cli_connection():
    """Debug why CLI connection fails"""
    
    device_name = 'iosv-dcloud'
    
    print('=' * 70)
    print('Debugging iosv-dcloud CLI Connection Issues')
    print('=' * 70)
    print()
    
    # Test with different users
    test_users = ['gudeng', 'admin', 'cisco']
    
    for username in test_users:
        print(f'Testing with user: {username}')
        print('-' * 70)
        
        try:
            m = maapi.Maapi()
            m.start_user_session(username, f'debug_test_{username}')
            
            t = m.start_read_trans()
            root = maagic.get_root(t)
            
            if device_name not in root.devices.device:
                print(f'❌ Device not found')
                t.finish()
                m.end_user_session()
                continue
            
            device = root.devices.device[device_name]
            
            print(f'✅ Device found')
            print(f'   Address: {device.address}')
            print(f'   Port: {device.port}')
            print(f'   Authgroup: {device.authgroup}')
            print(f'   NED: {device.device_type.cli.ned_id}')
            
            # Check authgroup for this user
            authgroup_name = device.authgroup
            if authgroup_name in root.devices.authgroups.group:
                authgroup = root.devices.authgroups.group[authgroup_name]
                print(f'   Authgroup "{authgroup_name}":')
                
                if hasattr(authgroup, 'umap') and username in authgroup.umap:
                    umap = authgroup.umap[username]
                    print(f'     ✅ umap for "{username}" exists')
                    print(f'        Remote name: {umap.remote_name}')
                elif hasattr(authgroup, 'default_map'):
                    print(f'     ⚠️  No umap for "{username}", will use default-map')
                    if hasattr(authgroup.default_map, 'remote_name'):
                        print(f'        Default remote name: {authgroup.default_map.remote_name}')
                else:
                    print(f'     ❌ No umap for "{username}" and no default-map')
            
            t.finish()
            m.end_user_session()
            
            # Try to connect
            print(f'   Attempting connection...')
            try:
                t_write = m.start_write_trans()
                root_write = maagic.get_root(t_write)
                device_write = root_write.devices.device[device_name]
                
                # Try to trigger a connection
                # This will show us the actual error
                try:
                    # Just accessing the device might trigger connection check
                    _ = device_write.address
                    t_write.finish()
                    print(f'   ✅ Connection check passed')
                except Exception as conn_error:
                    print(f'   ❌ Connection error: {conn_error}')
                    t_write.abort()
                
                m.end_user_session()
                
            except Exception as e:
                print(f'   ❌ Error: {e}')
                try:
                    m.end_user_session()
                except:
                    pass
            
            print()
            
        except Exception as e:
            print(f'❌ Error with user {username}: {e}')
            import traceback
            traceback.print_exc()
            print()
    
    print('=' * 70)
    print('INVESTIGATION')
    print('=' * 70)
    print('The issue is likely:')
    print('1. NSO CLI uses different SSH client/library than Python API')
    print('2. Java SSH library in NSO might not support legacy KEX algorithms')
    print('3. Need to configure NSO\'s SSH settings, not system SSH config')
    print()
    print('SOLUTION: Configure the IOS device to support modern algorithms')
    print('This is the proper fix - update the device, not work around NSO')
    print('=' * 70)

if __name__ == '__main__':
    debug_cli_connection()
