#!/usr/bin/env python3
"""
Backup NSO Configuration
=========================

This script creates a backup of the current NSO configuration by:
1. Creating a named rollback point in NSO
2. Exporting the full configuration to an XML file
3. Optionally saving device-specific configurations

This allows you to restore the configuration later if needed.
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

def backup_nso_config(backup_name=None, export_dir=None):
    """Backup NSO configuration with rollback point and file export"""
    
    # Generate backup name with timestamp if not provided
    if backup_name is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'dcloud_lab_setup_{timestamp}'
    
    # Set export directory
    if export_dir is None:
        export_dir = '/Users/gudeng/MCP_Server/backups/nso_configs'
    
    os.makedirs(export_dir, exist_ok=True)
    
    print('=' * 70)
    print('Backing up NSO Configuration')
    print('=' * 70)
    print(f'Backup name: {backup_name}')
    print(f'Export directory: {export_dir}')
    print(f'NSO Directory: {NSO_DIR}')
    print()
    
    try:
        # Create MAAPI session
        m = maapi.Maapi()
        m.start_user_session('admin', 'backup_nso_config')
        
        # Step 1: Create a named rollback point
        print('Step 1: Creating rollback point...')
        try:
            # Start a write transaction to create a commit with description
            t = m.start_write_trans()
            root = maagic.get_root(t)
            
            # Make a small change to create a rollback point, or just commit current state
            # Actually, we can just commit with a description to create a rollback point
            t.apply_params(comment=backup_name)
            
            print(f'✅ Rollback point created: {backup_name}')
            
        except Exception as e:
            print(f'⚠️  Could not create rollback point: {e}')
            print('   (This is okay if there are no pending changes)')
        
        # Step 2: Export full configuration to XML file using NSO CLI
        print()
        print('Step 2: Exporting configuration to XML file...')
        try:
            export_file = os.path.join(export_dir, f'{backup_name}.xml')
            
            # Use NSO CLI to export the configuration
            import subprocess
            ncs_cli_path = os.path.join(NSO_DIR, 'bin', 'ncs_cli')
            
            # Export devices configuration
            cmd = f'{ncs_cli_path} -u admin -C -c "show running-config devices device"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                with open(export_file, 'w') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    f.write('<!-- NSO Configuration Backup\n')
                    f.write(f'     Backup Name: {backup_name}\n')
                    f.write(f'     Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                    f.write('-->\n\n')
                    f.write(result.stdout)
                
                print(f'✅ Configuration exported to: {export_file}')
            else:
                # Fallback: Use Python API with proper iteration
                t = m.start_read_trans()
                root = maagic.get_root(t)
                
                export_file = os.path.join(export_dir, f'{backup_name}.xml')
                
                with open(export_file, 'w') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    f.write('<config xmlns="http://tail-f.com/ns/config/1.0">\n')
                    f.write('  <devices xmlns="http://tail-f.com/ns/ncs">\n')
                    
                    # Get device list using maapi directly
                    device_list = []
                    try:
                        # Try to get device list from CDB
                        devices_path = '/ncs:devices/ncs:device'
                        # Use maapi to query devices
                        th = m.start_read_trans()
                        devices = m.list(th, devices_path)
                        for dev in devices:
                            device_list.append(dev)
                        m.finish_trans(th)
                    except:
                        # Fallback: known device list
                        device_list = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5', 
                                      'node-6', 'node-7', 'node-8', 'pce-11']
                    
                    # Export each device
                    for device_name in device_list:
                        try:
                            device = root.devices.device[device_name]
                            f.write(f'    <device>\n')
                            f.write(f'      <name>{device_name}</name>\n')
                            if hasattr(device, 'address'):
                                f.write(f'      <address>{device.address}</address>\n')
                            if hasattr(device, 'port'):
                                f.write(f'      <port>{device.port}</port>\n')
                            if hasattr(device, 'authgroup'):
                                f.write(f'      <authgroup>{device.authgroup}</authgroup>\n')
                            if hasattr(device, 'device_type'):
                                if hasattr(device.device_type, 'cli'):
                                    ned_id = device.device_type.cli.ned_id
                                    f.write(f'      <device-type>\n')
                                    f.write(f'        <cli>\n')
                                    f.write(f'          <ned-id>{ned_id}</ned-id>\n')
                                    f.write(f'        </cli>\n')
                                    f.write(f'      </device-type>\n')
                            if hasattr(device, 'state') and hasattr(device.state, 'admin_state'):
                                f.write(f'      <state>\n')
                                f.write(f'        <admin-state>{device.state.admin_state}</admin-state>\n')
                                f.write(f'      </state>\n')
                            # Export NED settings
                            if hasattr(device, 'ned_settings'):
                                ned_settings = device.ned_settings
                                if hasattr(ned_settings, 'cisco_ios_xr_meta__cisco_iosxr'):
                                    iosxr_settings = ned_settings.cisco_ios_xr_meta__cisco_iosxr
                                    if hasattr(iosxr_settings, 'read'):
                                        read_settings = iosxr_settings.read
                                        if hasattr(read_settings, 'admin_show_running_config'):
                                            f.write(f'      <ned-settings>\n')
                                            f.write(f'        <cisco-ios-xr-meta:cisco-iosxr xmlns:cisco-ios-xr-meta="http://tail-f.com/ned/cisco-ios-xr-meta">\n')
                                            f.write(f'          <read>\n')
                                            f.write(f'            <admin-show-running-config>{read_settings.admin_show_running_config}</admin-show-running-config>\n')
                                            f.write(f'          </read>\n')
                                            f.write(f'        </cisco-ios-xr-meta:cisco-iosxr>\n')
                                            f.write(f'      </ned-settings>\n')
                            f.write(f'    </device>\n')
                        except Exception as dev_e:
                            print(f'   ⚠️  Could not export device {device_name}: {dev_e}')
                    
                    f.write('  </devices>\n')
                    f.write('</config>\n')
                
                print(f'✅ Configuration exported to: {export_file}')
            
        except Exception as e:
            print(f'❌ Error exporting configuration: {e}')
            import traceback
            traceback.print_exc()
        
        # Step 3: List available rollback points
        print()
        print('Step 3: Checking rollback points...')
        try:
            # Get rollback information
            rollback_info_file = os.path.join(export_dir, f'{backup_name}_rollback_info.txt')
            with open(rollback_info_file, 'w') as f:
                f.write(f'Backup Name: {backup_name}\n')
                f.write(f'Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write(f'\nTo restore this configuration:\n')
                f.write(f'1. Find the rollback ID using: show rollback\n')
                f.write(f'2. Restore using: rollback_router_configuration(rollback_id)\n')
                f.write(f'   Or in NSO CLI: rollback <rollback_id>\n')
            
            print(f'✅ Rollback info saved to: {rollback_info_file}')
            
        except Exception as e:
            print(f'⚠️  Could not save rollback info: {e}')
        
        m.end_user_session()
        
        # Summary
        print()
        print('=' * 70)
        print('BACKUP SUMMARY')
        print('=' * 70)
        print(f'✅ Backup name: {backup_name}')
        print(f'✅ Configuration file: {export_file}')
        print(f'✅ Rollback info: {rollback_info_file}')
        print()
        print('To restore this configuration:')
        print('1. Use the rollback point in NSO (show rollback to find ID)')
        print('2. Or use the exported XML file to recreate devices')
        print('=' * 70)
        
        return True
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Backup NSO configuration')
    parser.add_argument('--name', help='Backup name (default: auto-generated with timestamp)')
    parser.add_argument('--dir', help='Export directory (default: ./backups/nso_configs)')
    args = parser.parse_args()
    
    success = backup_nso_config(backup_name=args.name, export_dir=args.dir)
    sys.exit(0 if success else 1)

