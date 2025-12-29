#!/usr/bin/env python3
"""
Check Sync Status for All Devices
==================================

This script checks the sync status of all devices in NSO.
"""

import os
import sys
import subprocess

NSO_DIR = '/Users/gudeng/NCS-6413'
DEVICES = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5', 
           'node-6', 'node-7', 'node-8', 'pce-11']

def check_device_status(device_name):
    """Check status of a single device"""
    ncs_cli = os.path.join(NSO_DIR, 'bin', 'ncs_cli')
    
    # Get device state
    cmd = f'{ncs_cli} -u cisco -C -c "show devices device {device_name} state"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    state_info = {}
    for line in result.stdout.split('\n'):
        if 'oper-state' in line:
            state_info['oper-state'] = line.split()[-1]
        elif 'oper-state-error-tag' in line:
            state_info['error-tag'] = line.split()[-1]
        elif 'admin-state' in line:
            state_info['admin-state'] = line.split()[-1]
    
    # Get device config
    cmd = f'{ncs_cli} -u cisco -C -c "show devices device {device_name} config"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    config_info = {}
    for line in result.stdout.split('\n'):
        if 'address' in line and 'address' not in config_info:
            parts = line.split()
            if len(parts) >= 2:
                config_info['address'] = parts[-1]
        elif 'authgroup' in line:
            parts = line.split()
            if len(parts) >= 2:
                config_info['authgroup'] = parts[-1]
    
    return state_info, config_info

def main():
    print('=' * 80)
    print('Device Sync Status Report')
    print('=' * 80)
    print()
    
    results = []
    
    for device_name in DEVICES:
        state_info, config_info = check_device_status(device_name)
        results.append((device_name, state_info, config_info))
    
    # Print summary table
    print(f'{"Device":<12} {"IP Address":<18} {"Authgroup":<12} {"Oper State":<15} {"Error":<20}')
    print('-' * 80)
    
    for device_name, state_info, config_info in results:
        ip = config_info.get('address', 'N/A')
        auth = config_info.get('authgroup', 'N/A')
        oper_state = state_info.get('oper-state', 'unknown')
        error = state_info.get('error-tag', 'none')
        
        print(f'{device_name:<12} {ip:<18} {auth:<12} {oper_state:<15} {error:<20}')
    
    print()
    print('=' * 80)
    print('Detailed Status:')
    print('=' * 80)
    
    for device_name, state_info, config_info in results:
        print(f'\n{device_name}:')
        print(f'  IP Address: {config_info.get("address", "N/A")}')
        print(f'  Authgroup: {config_info.get("authgroup", "N/A")}')
        print(f'  Oper State: {state_info.get("oper-state", "unknown")}')
        print(f'  Error Tag: {state_info.get("error-tag", "none")}')
        
        if state_info.get('error-tag') == 'noconnection':
            print(f'  ⚠️  Device is not connected')
            print(f'     To connect: devices device {device_name} connect')
    
    print()
    print('=' * 80)
    print('Note: Sync status can only be checked when devices are connected.')
    print('=' * 80)

if __name__ == '__main__':
    main()

