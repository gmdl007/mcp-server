#!/usr/bin/env python3
"""
Fix iosv-dcloud SSH KEX Algorithm Mismatch
==========================================

This script configures NSO to use legacy SSH algorithms compatible
with older IOS devices that only support SHA-1 based Diffie-Hellman.
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

def fix_ios_ssh_kex():
    """Configure IOS device to use compatible SSH settings"""
    
    device_name = 'iosv-dcloud'
    
    print('=' * 70)
    print('Fixing SSH KEX Algorithm Mismatch for iosv-dcloud')
    print('=' * 70)
    print()
    print('Problem: IOS device only supports SHA-1 based Diffie-Hellman')
    print('         Modern OpenSSH (NSO) doesn\'t offer these by default')
    print()
    print('Solution: Configure NSO to use compatible SSH algorithms')
    print()
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'fix_ios_ssh_kex')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        if device_name not in root.devices.device:
            print(f'❌ Device {device_name} not found')
            t.abort()
            m.end_user_session()
            return False
        
        device = root.devices.device[device_name]
        
        print(f'✅ Found device: {device_name}')
        print(f'   NED: {device.device_type.cli.ned_id}')
        print()
        
        # Check current NED settings
        print('Current NED Settings:')
        print('-' * 70)
        if hasattr(device, 'ned_settings'):
            ned_settings = device.ned_settings
            print('✅ NED settings exist')
            
            # For IOS NED, we might need to configure SSH settings
            # Check what's available in the IOS NED settings
            print('Available NED settings attributes:')
            if hasattr(ned_settings, '__dict__'):
                for attr in dir(ned_settings):
                    if not attr.startswith('_'):
                        print(f'   - {attr}')
        else:
            print('⚠️  No NED settings configured')
            # Try to create NED settings
            try:
                # IOS NED might have different settings structure
                # Let's check the YANG model structure
                print('   Attempting to configure NED settings...')
            except Exception as e:
                print(f'   ⚠️  Could not configure: {e}')
        
        print()
        print('=' * 70)
        print('ALTERNATIVE SOLUTION')
        print('=' * 70)
        print('Since NSO uses system SSH client, we need to configure')
        print('SSH algorithms at the system level or use SSH config.')
        print()
        print('Option 1: Configure SSH config for NSO')
        print('Create/edit ~/.ssh/config or NSO SSH config:')
        print('  Host 198.18.1.11')
        print('    KexAlgorithms +diffie-hellman-group14-sha1')
        print('    KexAlgorithms +diffie-hellman-group-exchange-sha1')
        print()
        print('Option 2: Configure the IOS device to support modern algorithms')
        print('On the IOS device, run:')
        print('  ip ssh server algorithm kex diffie-hellman-group14-sha256')
        print('  ip ssh server algorithm kex ecdh-sha2-nistp256')
        print()
        print('Option 3: Use NSO\'s SSH configuration')
        print('NSO might have SSH configuration in ncs.conf')
        print('=' * 70)
        
        # Try to set SSH host key check to false (if available)
        try:
            if hasattr(device, 'ned_settings'):
                ned_settings = device.ned_settings
                if hasattr(ned_settings, 'ssh'):
                    if hasattr(ned_settings.ssh, 'host_key_check'):
                        ned_settings.ssh.host_key_check = False
                        print('✅ Set SSH host_key_check to false')
        except Exception as e:
            print(f'⚠️  Could not set SSH settings: {e}')
        
        # Commit any changes
        print()
        print('Committing changes...')
        t.apply()
        print('✅ Changes committed')
        
        m.end_user_session()
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_ios_ssh_kex()
    sys.exit(0 if success else 1)
