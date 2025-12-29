#!/usr/bin/env python3
"""
Restore NSO Service Packages
=============================

This script copies service packages from old installation to new installation:
- Source: /Users/gudeng/ncs-run/packages
- Destination: /Users/gudeng/ncs-run-6413/packages
"""

import os
import shutil
from pathlib import Path

OLD_INSTALL = '/Users/gudeng/ncs-run/packages'
NEW_INSTALL = '/Users/gudeng/ncs-run-6413/packages'

# Service packages to restore (based on user's selection: 1, 2, 4, 5, 6, 7, 8, 9)
PACKAGES_TO_RESTORE = [
    'BGP-GRP',           # 1
    'L3VPN',             # 2
    'RASS',              # 4
    'ds_select_ring_1',  # 5
    'ibgp',              # 6
    'ospf',              # 7
    'peering',           # 8
    'router',            # 9
]

def copy_package(source_dir, dest_dir, package_name):
    """Copy a package directory from source to destination"""
    source_path = os.path.join(source_dir, package_name)
    dest_path = os.path.join(dest_dir, package_name)
    
    if not os.path.exists(source_path):
        return False, f"Source package '{package_name}' not found"
    
    if os.path.exists(dest_path):
        return False, f"Destination package '{package_name}' already exists"
    
    try:
        print(f'  Copying {package_name}...', end=' ', flush=True)
        shutil.copytree(source_path, dest_path)
        
        # Get size for confirmation
        total_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(dest_path)
            for filename in filenames
        )
        size_mb = total_size / (1024 * 1024)
        print(f'✅ ({size_mb:.1f} MB)')
        return True, f"Successfully copied ({size_mb:.1f} MB)"
    except Exception as e:
        print(f'❌ Error: {e}')
        return False, str(e)

def restore_packages():
    """Restore service packages to new installation"""
    
    print('=' * 70)
    print('Restoring NSO Service Packages')
    print('=' * 70)
    print(f'Source: {OLD_INSTALL}')
    print(f'Destination: {NEW_INSTALL}')
    print()
    print(f'Packages to restore ({len(PACKAGES_TO_RESTORE)}):')
    for i, pkg in enumerate(PACKAGES_TO_RESTORE, 1):
        print(f'  {i}. {pkg}')
    print()
    
    # Verify source and destination exist
    if not os.path.exists(OLD_INSTALL):
        print(f'❌ Error: Source directory does not exist: {OLD_INSTALL}')
        return False
    
    if not os.path.exists(NEW_INSTALL):
        print(f'❌ Error: Destination directory does not exist: {NEW_INSTALL}')
        return False
    
    # Create destination if needed
    os.makedirs(NEW_INSTALL, exist_ok=True)
    
    # Copy packages
    print('Copying packages...')
    print('-' * 70)
    
    successful = []
    failed = []
    
    for package_name in PACKAGES_TO_RESTORE:
        success, message = copy_package(OLD_INSTALL, NEW_INSTALL, package_name)
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
        print(f'✅ Successfully copied: {len(successful)} package(s)')
        for pkg, msg in successful:
            print(f'   - {pkg}')
    
    if failed:
        print(f'\n❌ Failed to copy: {len(failed)} package(s)')
        for pkg, msg in failed:
            print(f'   - {pkg}: {msg}')
    
    print()
    print('=' * 70)
    print('NEXT STEPS')
    print('=' * 70)
    print('After copying packages, you need to:')
    print('1. Reload packages in NSO:')
    print('   ncs_cli -u admin -C')
    print('   packages reload')
    print()
    print('2. Or use the MCP tool:')
    print('   reload_nso_packages()')
    print('=' * 70)
    
    return len(failed) == 0

if __name__ == '__main__':
    success = restore_packages()
    exit(0 if success else 1)

