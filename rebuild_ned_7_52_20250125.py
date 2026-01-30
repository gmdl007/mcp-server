#!/usr/bin/env python3
"""
Rebuild cisco-iosxr-cli-7.52 NED Package
=========================================

This script rebuilds the cisco-iosxr-cli-7.52 NED package to fix
the "Must be recompiled" error during packages reload.
"""

import os
import subprocess
import sys

NSO_DIR = '/Users/gudeng/NCS-6413'
PACKAGES_DIR = '/Users/gudeng/ncs-run-6413/packages'
PACKAGE_NAME = 'cisco-iosxr-cli-7.52'

def rebuild_ned_package():
    """Rebuild the cisco-iosxr-cli-7.52 NED package"""
    
    print('=' * 70)
    print('Rebuilding cisco-iosxr-cli-7.52 NED Package')
    print('=' * 70)
    print(f'NSO Directory: {NSO_DIR}')
    print(f'Packages Directory: {PACKAGES_DIR}')
    print(f'Package: {PACKAGE_NAME}')
    print()
    
    package_path = os.path.join(PACKAGES_DIR, PACKAGE_NAME)
    src_path = os.path.join(package_path, 'src')
    
    # Check if package exists
    if not os.path.exists(package_path):
        print(f'❌ Error: Package directory not found: {package_path}')
        return False
    
    if not os.path.exists(src_path):
        print(f'❌ Error: Source directory not found: {src_path}')
        return False
    
    print(f'✅ Found package at: {package_path}')
    print(f'✅ Found source directory at: {src_path}')
    print()
    
    # Check for Makefile
    makefile_path = os.path.join(src_path, 'Makefile')
    if not os.path.exists(makefile_path):
        print(f'⚠️  Warning: Makefile not found at {makefile_path}')
        print('   This might be a binary-only NED package')
        print('   You may need to reinstall it from the original package')
        return False
    
    print('Rebuilding package...')
    print('-' * 70)
    
    # Set environment
    env = dict(os.environ)
    env['NCS_DIR'] = NSO_DIR
    env['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
    
    try:
        # Clean first
        print('  Cleaning...', end=' ', flush=True)
        clean_result = subprocess.run(
            ['make', 'clean'],
            cwd=src_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=60
        )
        if clean_result.returncode == 0:
            print('✅')
        else:
            print('⚠️  (clean had warnings but continuing)')
        
        # Build
        print('  Building...', end=' ', flush=True)
        build_result = subprocess.run(
            ['make'],
            cwd=src_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if build_result.returncode == 0:
            print('✅')
            print()
            print('=' * 70)
            print('SUCCESS')
            print('=' * 70)
            print(f'✅ Successfully rebuilt {PACKAGE_NAME}')
            print()
            print('Next steps:')
            print('1. Reload packages in NSO:')
            print('   ncs_cli -u admin -C')
            print('   packages reload')
            print('=' * 70)
            return True
        else:
            print('❌')
            print()
            print('Build failed. Error output:')
            print('-' * 70)
            if build_result.stderr:
                print(build_result.stderr[:500])
            if build_result.stdout:
                print(build_result.stdout[:500])
            print('-' * 70)
            return False
            
    except subprocess.TimeoutExpired:
        print('❌ Timeout')
        print('Build took too long (>5 minutes)')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = rebuild_ned_package()
    sys.exit(0 if success else 1)
