#!/usr/bin/env python3
"""
Rebuild NSO Service Packages
============================

This script rebuilds service packages for NSO 6.4.1.3
"""

import os
import subprocess
import sys

NSO_DIR = '/Users/gudeng/NCS-6413'
PACKAGES_DIR = '/Users/gudeng/ncs-run-6413/packages'

PACKAGES_TO_REBUILD = [
    'BGP-GRP',
    'L3VPN',
    'RASS',
    'ds_select_ring_1',
    'ibgp',
    'ospf',
    'peering',
    'router',
]

def rebuild_package(package_name):
    """Rebuild a single package"""
    package_path = os.path.join(PACKAGES_DIR, package_name)
    
    if not os.path.exists(package_path):
        return False, f"Package directory not found: {package_name}"
    
    src_path = os.path.join(package_path, 'src')
    if not os.path.exists(src_path):
        return False, f"No src directory in package: {package_name}"
    
    print(f'  Rebuilding {package_name}...', end=' ', flush=True)
    
    try:
        # Change to package src directory and run make
        result = subprocess.run(
            ['make', 'clean', 'all'],
            cwd=src_path,
            env=dict(os.environ, NCS_DIR=NSO_DIR),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print('✅')
            return True, "Success"
        else:
            print(f'❌')
            print(f'     Error: {result.stderr[:200]}')
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print('❌ Timeout')
        return False, "Build timeout"
    except Exception as e:
        print(f'❌ Error: {e}')
        return False, str(e)

def rebuild_all_packages():
    """Rebuild all packages"""
    
    print('=' * 70)
    print('Rebuilding NSO Service Packages for NSO 6.4.1.3')
    print('=' * 70)
    print(f'NSO Directory: {NSO_DIR}')
    print(f'Packages Directory: {PACKAGES_DIR}')
    print()
    print(f'Packages to rebuild ({len(PACKAGES_TO_REBUILD)}):')
    for pkg in PACKAGES_TO_REBUILD:
        print(f'  - {pkg}')
    print()
    
    # Verify NSO directory
    if not os.path.exists(NSO_DIR):
        print(f'❌ Error: NSO directory does not exist: {NSO_DIR}')
        return False
    
    # Rebuild packages
    print('Rebuilding packages...')
    print('-' * 70)
    
    successful = []
    failed = []
    
    for package_name in PACKAGES_TO_REBUILD:
        success, message = rebuild_package(package_name)
        if success:
            successful.append((package_name, message))
        else:
            failed.append((package_name, message))
    
    # Summary
    print()
    print('=' * 70)
    print('SUMMARY')
    print('=' * 70)
    
    if successful:
        print(f'✅ Successfully rebuilt: {len(successful)} package(s)')
        for pkg, _ in successful:
            print(f'   - {pkg}')
    
    if failed:
        print(f'\n❌ Failed to rebuild: {len(failed)} package(s)')
        for pkg, msg in failed:
            print(f'   - {pkg}: {msg[:100]}')
    
    print()
    print('=' * 70)
    print('NEXT STEPS')
    print('=' * 70)
    if successful:
        print('After rebuilding, reload packages in NSO:')
        print('   ncs_cli -u admin -C')
        print('   packages reload')
    print('=' * 70)
    
    return len(failed) == 0

if __name__ == '__main__':
    success = rebuild_all_packages()
    sys.exit(0 if success else 1)

