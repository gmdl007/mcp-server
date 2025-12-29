#!/usr/bin/env python3
"""
Update YANG Imports in Service Packages
=======================================

This script updates YANG imports from old NED to new NED:
- Old: tailf-ned-cisco-ios-xr
- New: (to be determined from cisco-iosxr-cli-7.61)
"""

import os
import re

PACKAGES_DIR = '/Users/gudeng/ncs-run-6413/packages'
PACKAGES_TO_UPDATE = [
    'BGP-GRP',
    'L3VPN',
    'RASS',
    'ds_select_ring_1',
    'ibgp',
    'ospf',
    'peering',
]

def find_new_ned_module():
    """Find the correct NED module name from cisco-iosxr-cli-7.61"""
    ned_dir = os.path.join(PACKAGES_DIR, 'cisco-iosxr-cli-7.61')
    yang_dir = os.path.join(ned_dir, 'src/ncsc-out/modules/yang')
    
    if not os.path.exists(yang_dir):
        return None
    
    # Look for IOS-XR NED yang files
    for file in os.listdir(yang_dir):
        if 'iosxr' in file.lower() and file.endswith('.yang'):
            filepath = os.path.join(yang_dir, file)
            with open(filepath, 'r') as f:
                content = f.read()
                # Find module name
                match = re.search(r'module\s+([^\s{]+)', content)
                if match:
                    return match.group(1)
    return None

def update_yang_file(filepath, old_import, new_import):
    """Update YANG import in a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        if old_import not in content:
            return False, "Import not found"
        
        # Replace the import
        new_content = content.replace(old_import, new_import)
        
        if new_content == content:
            return False, "No changes made"
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        return True, "Updated"
    except Exception as e:
        return False, str(e)

def update_package_yang_imports(package_name, old_import, new_import):
    """Update all YANG files in a package"""
    package_dir = os.path.join(PACKAGES_DIR, package_name)
    yang_dir = os.path.join(package_dir, 'src/yang')
    
    if not os.path.exists(yang_dir):
        return [], []
    
    updated = []
    failed = []
    
    for file in os.listdir(yang_dir):
        if file.endswith('.yang'):
            filepath = os.path.join(yang_dir, file)
            success, message = update_yang_file(filepath, old_import, new_import)
            if success:
                updated.append(file)
            else:
                if "Import not found" not in message:
                    failed.append((file, message))
    
    return updated, failed

def main():
    print('=' * 70)
    print('Updating YANG Imports in Service Packages')
    print('=' * 70)
    
    # Find new NED module name
    print('Finding new NED module name...')
    new_ned_module = find_new_ned_module()
    
    if not new_ned_module:
        print('❌ Could not find new NED module name')
        print('   Trying common alternatives...')
        # Try common names
        new_ned_module = 'tailf-ned-cisco-ios-xr'  # Might be the same
    else:
        print(f'✅ Found new NED module: {new_ned_module}')
    
    old_import = 'tailf-ned-cisco-ios-xr'
    new_import = new_ned_module
    
    print(f'\nUpdating imports:')
    print(f'  Old: {old_import}')
    print(f'  New: {new_import}')
    print()
    
    # Update each package
    print('Updating packages...')
    print('-' * 70)
    
    all_updated = []
    all_failed = []
    
    for package_name in PACKAGES_TO_UPDATE:
        print(f'\n{package_name}:')
        updated, failed = update_package_yang_imports(package_name, old_import, new_import)
        
        if updated:
            print(f'  ✅ Updated {len(updated)} file(s): {", ".join(updated)}')
            all_updated.extend([(package_name, f) for f in updated])
        else:
            print(f'  ⚠️  No files updated (import may not be used)')
        
        if failed:
            print(f'  ❌ Failed: {failed}')
            all_failed.extend([(package_name, f, msg) for f, msg in failed])
    
    # Summary
    print()
    print('=' * 70)
    print('SUMMARY')
    print('=' * 70)
    print(f'✅ Updated: {len(all_updated)} file(s)')
    if all_failed:
        print(f'❌ Failed: {len(all_failed)} file(s)')
    print()
    print('Next: Rebuild packages with:')
    print('  python3 scripts/setup/rebuild_nso_packages_20250101.py')
    print('=' * 70)

if __name__ == '__main__':
    main()

