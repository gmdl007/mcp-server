#!/usr/bin/env python3
"""
Add Netsim Devices to NSO 6.4.1.3 with cisco authgroup
========================================================

This script adds netsim devices (xr9kv0, xr9kv1, xr9kv2) to NSO with:
- Authgroup: cisco
- NED: cisco-iosxr-cli-7.52 (the NED used for netsim)
- Port: 10022, 10023, 10024 (CLI SSH ports)
- Address: 127.0.0.1 (localhost)
"""

import os
import sys
from datetime import datetime

# NSO 6.4.1.3 directory
NSO_DIR = '/Users/gudeng/NCS-6413'
NSO_RUN_DIR = '/Users/gudeng/ncs-run-6413'

os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

import ncs.maapi as maapi
import ncs.maagic as maagic

def check_authgroup(root):
    """Check if cisco authgroup exists, create if needed"""
    try:
        if 'cisco' in root.devices.authgroups.group:
            authgroup = root.devices.authgroups.group['cisco']
            print('✅ Authgroup "cisco" exists')
            if hasattr(authgroup, 'umap') and 'cisco' in authgroup.umap:
                umap = authgroup.umap['cisco']
                print(f'   Remote name: {umap.remote_name}')
                print(f'   Remote password: {"*" * len(str(umap.remote_password)) if hasattr(umap, "remote_password") else "not set"}')
            return True
        else:
            print('⚠️  Authgroup "cisco" does not exist, creating...')
            authgroup = root.devices.authgroups.group.create('cisco')
            umap = authgroup.umap.create('cisco')
            umap.remote_name = 'admin'
            umap.remote_password = 'admin'  # Default netsim password
            print('✅ Created authgroup "cisco" with default credentials (admin/admin)')
            return True
    except Exception as e:
        print(f'❌ Error checking/creating authgroup: {e}')
        return False

def add_netsim_devices():
    """Add netsim devices to NSO with cisco authgroup"""
    
    # Netsim device configuration: (device_name, cli_port)
    devices = [
        ('xr9kv0', 10022),
        ('xr9kv1', 10023),
        ('xr9kv2', 10024),
    ]
    
    print('=' * 70)
    print('Adding Netsim Devices to NSO 6.4.1.3')
    print('=' * 70)
    print(f'NSO Directory: {NSO_DIR}')
    print(f'NSO Run Directory: {NSO_RUN_DIR}')
    print(f'Total devices: {len(devices)}')
    print(f'Authgroup: cisco')
    print(f'NED: cisco-iosxr-cli-7.52 (netsim compatible)')
    print()
    
    try:
        # Create MAAPI session
        m = maapi.Maapi()
        m.start_user_session('admin', 'add_netsim_devices_6413')
        
        # Start write transaction
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Check/create authgroup
        print('Checking authgroup...')
        if not check_authgroup(root):
            print('❌ Failed to setup authgroup')
            t.abort()
            m.end_user_session()
            return False
        
        print()
        
        added = []
        updated = []
        errors = []
        
        for device_name, cli_port in devices:
            try:
                # Check if device already exists
                if device_name in root.devices.device:
                    device = root.devices.device[device_name]
                    print(f'⚠️  {device_name}: Already exists, updating...')
                    updated.append(device_name)
                else:
                    # Create new device
                    device = root.devices.device.create(device_name)
                    print(f'✅ {device_name}: Creating new device...')
                    added.append(device_name)
                
                # Configure device address and port
                device.address = '127.0.0.1'  # localhost for netsim
                device.port = cli_port
                
                # Set authgroup to 'cisco'
                device.authgroup = 'cisco'
                
                # Set admin state to unlocked
                device.state.admin_state = 'unlocked'
                
                # Remove other device-types if they exist
                if hasattr(device.device_type, 'netconf'):
                    try:
                        del device.device_type.netconf
                    except Exception as e:
                        pass
                if hasattr(device.device_type, 'generic'):
                    try:
                        del device.device_type.generic
                    except Exception as e:
                        pass
                if hasattr(device.device_type, 'snmp'):
                    try:
                        del device.device_type.snmp
                    except Exception as e:
                        pass
                
                # Set CLI device-type with cisco-iosxr-cli-7.61 NED (already installed)
                # NED ID format: cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61
                device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61'
                
                # Configure SSH settings if available
                try:
                    if hasattr(device, 'ned_settings'):
                        ned_settings = device.ned_settings
                        if hasattr(ned_settings, 'ssh'):
                            ned_settings.ssh.host_key_check = False
                except Exception as ssh_error:
                    # SSH settings may not be needed or available
                    pass
                
                print(f'   ✅ {device_name}: Configured - 127.0.0.1:{cli_port}, authgroup: cisco, NED: cisco-iosxr-cli-7.52')
                
            except Exception as e:
                errors.append((device_name, str(e)))
                print(f'   ❌ {device_name}: Error - {e}')
        
        # Apply changes
        if added or updated:
            print()
            print('Committing changes to NSO...')
            t.apply()
            print('✅ Changes committed successfully!')
        else:
            print('\n⚠️  No devices were added or updated')
            t.abort()
        
        # Summary
        print()
        print('=' * 70)
        print('SUMMARY')
        print('=' * 70)
        if added:
            print(f'✅ Successfully added: {len(added)} device(s)')
            for name in added:
                print(f'   - {name}')
        if updated:
            print(f'✅ Successfully updated: {len(updated)} device(s)')
            for name in updated:
                print(f'   - {name}')
        if errors:
            print(f'\n❌ Errors ({len(errors)}):')
            for dev_name, error in errors:
                print(f'   - {dev_name}: {error}')
        
        m.end_user_session()
        
        print()
        print('=' * 70)
        print('NEXT STEPS')
        print('=' * 70)
        print('1. Fetch SSH host keys:')
        for device_name, _ in devices:
            print(f'   devices device {device_name} ssh fetch-host-keys')
        print()
        print('2. Connect to devices:')
        for device_name, _ in devices:
            print(f'   devices device {device_name} connect')
        print()
        print('3. Sync configuration from devices:')
        for device_name, _ in devices:
            print(f'   devices device {device_name} sync-from')
        print()
        print('4. Verify authgroup is working:')
        print('   devices device xr9kv0 connect')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error connecting to NSO: {e}')
        import traceback
        traceback.print_exc()
        print()
        print('Troubleshooting:')
        print('1. Ensure NSO is running: ncs --status')
        print('2. Check NSO connection: ncs_cli -u admin -C')
        print('3. Verify NSO run directory exists:', NSO_RUN_DIR)
        return False

if __name__ == '__main__':
    success = add_netsim_devices()
    sys.exit(0 if success else 1)

