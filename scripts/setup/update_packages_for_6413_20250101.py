#!/usr/bin/env python3
"""
Update Service Packages for NSO 6.4.1.3
========================================

This script updates service packages to use the new NED (cisco-iosxr-cli-7.61)
instead of the old one (cisco-iosxr-cli-7.52).
"""

import os
import re
import subprocess

NSO_DIR = '/Users/gudeng/NCS-6413'
PACKAGES_DIR = '/Users/gudeng/ncs-run-6413/packages'
OLD_NED = 'cisco-iosxr-cli-7.52'
NEW_NED = 'cisco-iosxr-cli-7.61'

PACKAGES_TO_UPDATE = [
    'BGP-GRP',
    'L3VPN',
    'RASS',
    'ds_select_ring_1',
    'ibgp',
    'ospf',
    'peering',
]

def update_makefile(package_name):
    """Update Makefile to use new NED yangpath"""
    package_dir = os.path.join(PACKAGES_DIR, package_name)
    makefile_path = os.path.join(package_dir, 'src/Makefile')
    
    if not os.path.exists(makefile_path):
        return False, "Makefile not found"
    
    try:
        with open(makefile_path, 'r') as f:
            content = f.read()
        
        # Replace old NED path with new NED path
        old_pattern = f'../../{OLD_NED}/src/ncsc-out/modules/yang'
        new_pattern = f'../../{NEW_NED}/src/ncsc-out/modules/yang'
        
        if old_pattern in content:
            new_content = content.replace(old_pattern, new_pattern)
            
            with open(makefile_path, 'w') as f:
                f.write(new_content)
            
            return True, "Updated Makefile"
        else:
            # Check if it already uses new NED or different pattern
            if NEW_NED in content:
                return True, "Already using new NED"
            else:
                return False, f"Could not find NED path pattern in Makefile"
    
    except Exception as e:
        return False, str(e)

def rebuild_package(package_name):
    """Rebuild a package"""
    package_dir = os.path.join(PACKAGES_DIR, package_name)
    src_dir = os.path.join(package_dir, 'src')
    
    if not os.path.exists(src_dir):
        return False, "src directory not found"
    
    try:
        # Clean first
        subprocess.run(
            ['make', 'clean'],
            cwd=src_dir,
            env=dict(os.environ, NCS_DIR=NSO_DIR),
            capture_output=True,
            timeout=60
        )
        
        # Build
        result = subprocess.run(
            ['make'],
            cwd=src_dir,
            env=dict(os.environ, NCS_DIR=NSO_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            return True, "Rebuilt successfully"
        else:
            error_msg = result.stderr[:200] if result.stderr else result.stdout[:200]
            return False, f"Build failed: {error_msg}"
    
    except subprocess.TimeoutExpired:
        return False, "Build timeout"
    except Exception as e:
        return False, str(e)

def update_all_packages():
    """Update all packages"""
    
    print('=' * 70)
    print('Updating Service Packages for NSO 6.4.1.3')
    print('=' * 70)
    print(f'NSO Directory: {NSO_DIR}')
    print(f'Old NED: {OLD_NED}')
    print(f'New NED: {NEW_NED}')
    print()
    print(f'Packages to update ({len(PACKAGES_TO_UPDATE)}):')
    for pkg in PACKAGES_TO_UPDATE:
        print(f'  - {pkg}')
    print()
    
    # Verify new NED exists
    new_ned_path = os.path.join(PACKAGES_DIR, NEW_NED)
    if not os.path.exists(new_ned_path):
        print(f'❌ Error: New NED not found: {new_ned_path}')
        return False
    
    # Remove old NED if it exists
    old_ned_path = os.path.join(PACKAGES_DIR, OLD_NED)
    if os.path.exists(old_ned_path):
        print(f'Removing old NED ({OLD_NED})...')
        import shutil
        shutil.rmtree(old_ned_path)
        print('✅ Removed old NED')
        print()
    
    # Update and rebuild each package
    print('Updating packages...')
    print('-' * 70)
    
    updated = []
    failed = []
    
    for package_name in PACKAGES_TO_UPDATE:
        print(f'\n{package_name}:')
        
        # Update Makefile
        success, msg = update_makefile(package_name)
        if success:
            print(f'  ✅ {msg}')
        else:
            print(f'  ❌ {msg}')
            failed.append((package_name, msg))
            continue
        
        # Rebuild package
        print(f'  Rebuilding...', end=' ', flush=True)
        success, msg = rebuild_package(package_name)
        if success:
            print(f'✅')
            updated.append((package_name, msg))
        else:
            print(f'❌')
            print(f'     {msg}')
            failed.append((package_name, msg))
    
    # Summary
    print()
    print('=' * 70)
    print('SUMMARY')
    print('=' * 70)
    
    if updated:
        print(f'✅ Successfully updated: {len(updated)} package(s)')
        for pkg, _ in updated:
            print(f'   - {pkg}')
    
    if failed:
        print(f'\n❌ Failed: {len(failed)} package(s)')
        for pkg, msg in failed:
            print(f'   - {pkg}: {msg[:100]}')
    
    print()
    print('=' * 70)
    print('NEXT STEPS')
    print('=' * 70)
    if updated:
        print('Reload packages in NSO:')
        print('   ncs_cli -u admin -C')
        print('   packages reload')
    print('=' * 70)
    
    return len(failed) == 0

if __name__ == '__main__':
    success = update_all_packages()
    exit(0 if success else 1)

