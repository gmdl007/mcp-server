#!/usr/bin/env python3
"""
Add devices to NSO 6.4.1.3 with cisco-iosxr-cli-7.61 NED
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

def add_devices():
    """Add devices to NSO 6.4.1.3"""
    devices = [
        ('node-1', '198.18.1.41'),
        ('node-2', '198.18.1.42'),
        ('node-3', '198.18.1.43'),
        ('node-4', '198.18.1.44'),
        ('node-5', '198.18.1.45'),
        ('node-6', '198.18.1.46'),
        ('node-7', '198.18.1.47'),
        ('node-8', '198.18.1.48'),
        ('pce-11', '198.18.1.51')
    ]
    
    print('Adding devices to NSO 6.4.1.3:')
    print('=' * 60)
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'add_devices_6413')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        added = []
        updated = []
        errors = []
        
        for device_name, ip_address in devices:
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
                
                # Configure device
                device.address = ip_address
                device.port = 22
                device.authgroup = 'cisco-2'
                device.state.admin_state = 'unlocked'
                
                # Set device type to CLI with new NED
                if hasattr(device.device_type, 'netconf'):
                    # Remove netconf if exists
                    try:
                        del device.device_type.netconf
                    except:
                        pass
                
                # Set CLI device-type
                if not hasattr(device.device_type, 'cli'):
                    device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61'
                else:
                    device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61'
                
                # Try to set SSH settings if available
                try:
                    if hasattr(device, 'ned_settings'):
                        ned_settings = device.ned_settings
                        if hasattr(ned_settings, 'ssh'):
                            ned_settings.ssh.host_key_check = False
                except Exception as ssh_error:
                    # SSH settings may not be needed or available
                    pass
                
                print(f'   ✅ {device_name}: Configured - {ip_address}:22, NED: cisco-iosxr-cli-7.61')
                
            except Exception as e:
                errors.append((device_name, str(e)))
                print(f'   ❌ {device_name}: Error - {e}')
        
        if added or updated:
            t.apply()
            print(f'\n✅ Successfully processed {len(added) + len(updated)} devices')
            if added:
                print(f'   Added: {len(added)} devices')
            if updated:
                print(f'   Updated: {len(updated)} devices')
        else:
            print('\n⚠️  No devices were added or updated')
            t.abort()
        
        if errors:
            print(f'\n⚠️  Errors ({len(errors)}):')
            for dev_name, error in errors:
                print(f'   {dev_name}: {error}')
        
        m.end_user_session()
        
        print('\n' + '=' * 60)
        print('Next steps:')
        print('1. Fetch SSH keys: devices device node-* ssh fetch-host-keys')
        print('2. Connect devices: devices device node-* connect')
        print('3. Sync from devices: devices device node-* sync-from')
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = add_devices()
    sys.exit(0 if success else 1)

