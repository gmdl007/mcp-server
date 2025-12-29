#!/usr/bin/env python3
"""
Recreate Netsim with NCS 6.4.1.3
==================================

This script recreates netsim using NCS-6413 with the old NED package
that has netsim support.
"""

import os
import subprocess
import shutil
import time
import sys

NSO_614_DIR = '/Users/gudeng/NCS-614'
NSO_6413_DIR = '/Users/gudeng/NCS-6413'
NETSIM_DIR = '/Users/gudeng/MCP_Server/netsim'
OLD_NED_PATH = '/Users/gudeng/ncs-run/packages/cisco-iosxr-cli-7.52'

def recreate_netsim():
    """Recreate netsim with NCS-6413"""
    
    print('=' * 70)
    print('Recreating Netsim with NCS 6.4.1.3')
    print('=' * 70)
    print(f'NSO 6.4.1.3 Directory: {NSO_6413_DIR}')
    print(f'Netsim Directory: {NETSIM_DIR}')
    print(f'Using NED: {OLD_NED_PATH}')
    print()
    
    # Check if old netsim exists and stop it
    if os.path.exists(NETSIM_DIR):
        print('Stopping old netsim...')
        try:
            ncs_netsim_614 = os.path.join(NSO_614_DIR, 'bin', 'ncs-netsim')
            result = subprocess.run([ncs_netsim_614, 'stop'], 
                                  cwd=NETSIM_DIR,
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            if result.returncode == 0:
                print('✅ Old netsim stopped')
            else:
                print('⚠️  Old netsim may already be stopped')
        except Exception as e:
            print(f'⚠️  Could not stop old netsim: {e}')
        
        # Backup old netsim
        backup_dir = f'{NETSIM_DIR}_old_614_backup'
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.move(NETSIM_DIR, backup_dir)
        print(f'✅ Backed up old netsim to: {backup_dir}')
        print()
    
    # Verify NED has netsim support
    ned_netsim_dir = os.path.join(OLD_NED_PATH, 'netsim')
    if not os.path.exists(ned_netsim_dir):
        print(f'❌ Error: NED package does not have netsim directory: {ned_netsim_dir}')
        return False
    
    # Create new netsim
    print('Creating new netsim with NCS-6413...')
    ncs_netsim_6413 = os.path.join(NSO_6413_DIR, 'bin', 'ncs-netsim')
    
    cmd = [ncs_netsim_6413, 'create-network', OLD_NED_PATH, '3', 'xr9kv', '--dir', NETSIM_DIR]
    
    # Set NCS_DIR environment variable
    env = os.environ.copy()
    env['NCS_DIR'] = NSO_6413_DIR
    
    print(f'Running: {" ".join(cmd)}')
    print(f'With NCS_DIR={NSO_6413_DIR}')
    result = subprocess.run(cmd, 
                          cwd='/Users/gudeng/MCP_Server',
                          env=env,
                          capture_output=True, 
                          text=True, 
                          timeout=120)
    
    if result.returncode == 0:
        print('✅ Netsim created successfully')
        if result.stdout:
            print(result.stdout)
    else:
        print('❌ Failed to create netsim')
        print('STDERR:', result.stderr)
        return False
    
    # Start netsim
    print()
    print('Starting netsim...')
    cmd = [ncs_netsim_6413, 'start']
    env = os.environ.copy()
    env['NCS_DIR'] = NSO_6413_DIR
    result = subprocess.run(cmd, 
                          cwd=NETSIM_DIR,
                          env=env,
                          capture_output=True, 
                          text=True, 
                          timeout=60)
    
    if result.returncode == 0:
        print('✅ Netsim started successfully')
        if result.stdout:
            print(result.stdout)
    else:
        print('⚠️  Netsim start had issues:')
        print(result.stderr)
    
    # Wait for devices to start
    print()
    print('Waiting for devices to start...')
    time.sleep(5)
    
    # List devices
    print()
    print('Netsim devices:')
    cmd = [ncs_netsim_6413, 'list']
    env = os.environ.copy()
    env['NCS_DIR'] = NSO_6413_DIR
    result = subprocess.run(cmd, 
                          cwd=NETSIM_DIR,
                          env=env,
                          capture_output=True, 
                          text=True, 
                          timeout=30)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print('Could not list devices')
    
    # Check status
    print()
    print('Netsim status:')
    cmd = [ncs_netsim_6413, 'status']
    env = os.environ.copy()
    env['NCS_DIR'] = NSO_6413_DIR
    result = subprocess.run(cmd, 
                          cwd=NETSIM_DIR,
                          env=env,
                          capture_output=True, 
                          text=True, 
                          timeout=30)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print('Could not get status')
    
    print()
    print('=' * 70)
    print('Netsim Recreation Complete')
    print('=' * 70)
    print()
    print('Devices are available on:')
    print('  xr9kv0: CLI SSH port 10022, NETCONF port 12022')
    print('  xr9kv1: CLI SSH port 10023, NETCONF port 12023')
    print('  xr9kv2: CLI SSH port 10024, NETCONF port 12024')
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = recreate_netsim()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print('\n\nOperation cancelled by user')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
