#!/usr/bin/env python3
"""
Compare NSO Packages Between Two Installations
===============================================

This script compares packages between:
- Old installation: /Users/gudeng/ncs-run/packages
- New installation: /Users/gudeng/ncs-run-6413/packages
"""

import os
from pathlib import Path

OLD_INSTALL = '/Users/gudeng/ncs-run/packages'
NEW_INSTALL = '/Users/gudeng/ncs-run-6413/packages'

def get_packages(directory):
    """Get list of packages in a directory"""
    packages = []
    if os.path.exists(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                # Check if it's a package (has package-meta-data.xml or src directory)
                if (os.path.exists(os.path.join(item_path, 'package-meta-data.xml')) or
                    os.path.exists(os.path.join(item_path, 'src'))):
                    packages.append(item)
    return sorted(packages)

def compare_packages():
    """Compare packages between old and new installations"""
    
    print('=' * 70)
    print('NSO Packages Comparison')
    print('=' * 70)
    print(f'Old Installation: {OLD_INSTALL}')
    print(f'New Installation: {NEW_INSTALL}')
    print()
    
    old_packages = get_packages(OLD_INSTALL)
    new_packages = get_packages(NEW_INSTALL)
    
    print(f'Old Installation Packages ({len(old_packages)}):')
    print('-' * 70)
    for pkg in old_packages:
        pkg_type = 'NED' if 'cli' in pkg or 'nc' in pkg else 'SERVICE'
        print(f'  [{pkg_type:7}] {pkg}')
    print()
    
    print(f'New Installation Packages ({len(new_packages)}):')
    print('-' * 70)
    for pkg in new_packages:
        pkg_type = 'NED' if 'cli' in pkg or 'nc' in pkg else 'SERVICE'
        print(f'  [{pkg_type:7}] {pkg}')
    print()
    
    # Find packages in old but not in new
    missing_packages = [pkg for pkg in old_packages if pkg not in new_packages]
    
    # Separate NEDs and Services
    missing_neds = [pkg for pkg in missing_packages if 'cli' in pkg or 'nc' in pkg]
    missing_services = [pkg for pkg in missing_packages if pkg not in missing_neds]
    
    print('=' * 70)
    print('Packages Missing in New Installation')
    print('=' * 70)
    
    if missing_services:
        print(f'\nService Packages ({len(missing_services)}):')
        print('-' * 70)
        for pkg in missing_services:
            pkg_path = os.path.join(OLD_INSTALL, pkg)
            size = get_dir_size(pkg_path)
            print(f'  {pkg:30} ({size})')
    
    if missing_neds:
        print(f'\nNED Packages ({len(missing_neds)}):')
        print('-' * 70)
        for pkg in missing_neds:
            pkg_path = os.path.join(OLD_INSTALL, pkg)
            size = get_dir_size(pkg_path)
            print(f'  {pkg:30} ({size})')
    
    if not missing_packages:
        print('\n✅ All packages are present in new installation!')
    
    # Packages in new but not in old
    new_only = [pkg for pkg in new_packages if pkg not in old_packages]
    if new_only:
        print(f'\nPackages Only in New Installation ({len(new_only)}):')
        print('-' * 70)
        for pkg in new_only:
            print(f'  {pkg}')
    
    print()
    print('=' * 70)
    
    return missing_services, missing_neds

def get_dir_size(path):
    """Get human-readable directory size"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except:
        pass
    
    # Convert to human readable
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total < 1024.0:
            return f'{total:.1f} {unit}'
        total /= 1024.0
    return f'{total:.1f} TB'

if __name__ == '__main__':
    missing_services, missing_neds = compare_packages()
    
    print('\nNext Steps:')
    print('To restore service packages, use the restore script:')
    print('  python3 scripts/setup/restore_nso_packages_20250101.py')

