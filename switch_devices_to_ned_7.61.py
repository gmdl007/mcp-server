#!/usr/bin/env python3
"""
Switch all node-* and pce-11 devices to use cisco-iosxr-cli-7.61 NED
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

def switch_devices_to_ned():
    """Switch devices to cisco-iosxr-cli-7.61 NED"""
    print('Switching devices to cisco-iosxr-cli-7.61 NED')
    print('=' * 60)
    
    devices = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5', 
               'node-6', 'node-7', 'node-8', 'pce-11']
    
    try:
        m = maapi.Maapi()
        m.start_user_session('admin', 'switch_to_7.61_ned')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        updated = []
        not_found = []
        
        for dev_name in devices:
            try:
                device = root.devices.device[dev_name]
                
                # Remove netconf if exists
                if hasattr(device.device_type, 'netconf'):
                    try:
                        del device.device_type.netconf
                    except:
                        pass
                
                # Ensure CLI device-type exists
                if not hasattr(device.device_type, 'cli'):
                    # Create CLI device-type
                    device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61'
                else:
                    # Update NED ID
                    device.device_type.cli.ned_id = 'cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61'
                
                # Set port to 22
                device.port = 22
                
                updated.append(dev_name)
                print(f'✅ {dev_name}: Updated to cisco-iosxr-cli-7.61, port 22')
                
            except KeyError:
                not_found.append(dev_name)
                print(f'⚠️  {dev_name}: Device not found in NSO')
            except Exception as e:
                print(f'❌ {dev_name}: Error - {e}')
        
        if updated:
            t.apply()
            print(f'\n✅ Successfully updated {len(updated)} devices')
        else:
            print('\n⚠️  No devices were updated')
            t.abort()
        
        if not_found:
            print(f'\n⚠️  Devices not found: {not_found}')
            print('   These devices may need to be added to NSO first')
        
        m.end_user_session()
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = switch_devices_to_ned()
    sys.exit(0 if success else 1)

