#!/usr/bin/env python3
"""
Install NED Package for NSO
============================

This script installs a NED package following NSO best practices:
1. Extracts the NED package (tar.gz or .bin)
2. Places it in packages/neds/
3. Reloads packages in NSO
"""

import os
import sys
import tarfile
import subprocess
import shutil

NSO_DIR = "/Users/gudeng/NCS-614"
PACKAGES_DIR = f"{NSO_DIR}/packages"
NEDS_DIR = f"{PACKAGES_DIR}/neds"

def extract_ned_package(ned_file_path):
    """Extract NED package to packages/neds/"""
    print(f"Extracting NED package: {ned_file_path}")
    print("=" * 60)
    
    if not os.path.exists(ned_file_path):
        print(f"❌ Error: File not found: {ned_file_path}")
        return False
    
    # Determine if it's tar.gz or .bin (which might be tar.gz)
    try:
        with tarfile.open(ned_file_path, 'r:gz') as tar:
            # Get the root directory name
            members = tar.getmembers()
            if members:
                root_dir = members[0].name.split('/')[0]
                print(f"Package root directory: {root_dir}")
                
                # Extract to temporary location first
                temp_dir = f"{PACKAGES_DIR}/temp_extract"
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)
                
                tar.extractall(temp_dir)
                
                # Move to neds directory
                extracted_path = os.path.join(temp_dir, root_dir)
                target_path = os.path.join(NEDS_DIR, root_dir)
                
                if os.path.exists(target_path):
                    print(f"⚠️  NED {root_dir} already exists. Backing up...")
                    backup_path = f"{target_path}.backup"
                    if os.path.exists(backup_path):
                        shutil.rmtree(backup_path)
                    shutil.move(target_path, backup_path)
                
                shutil.move(extracted_path, target_path)
                shutil.rmtree(temp_dir)
                
                print(f"✅ NED extracted to: {target_path}")
                return True
    except Exception as e:
        print(f"❌ Error extracting: {e}")
        return False

def reload_nso_packages():
    """Reload packages in NSO"""
    print("\nReloading NSO packages...")
    print("=" * 60)
    
    try:
        # Use NSO CLI to reload packages
        cmd = f"{NSO_DIR}/bin/ncs_cli -u admin -C -c 'packages reload'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Packages reloaded successfully")
            return True
        else:
            print(f"⚠️  Reload command output: {result.stdout}")
            print(f"⚠️  You may need to reload manually: ncs_cli -u admin -C 'packages reload'")
            return False
    except Exception as e:
        print(f"⚠️  Could not auto-reload: {e}")
        print("   Please reload manually: ncs_cli -u admin -C 'packages reload'")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python install_ned_20250101.py <NED_FILE_PATH>")
        print("\nExample:")
        print("  python install_ned_20250101.py /Users/gudeng/NCS-614/packages/ncs-6.6-cisco-iosxr-7.74.4.signed.bin")
        sys.exit(1)
    
    ned_file = sys.argv[1]
    
    print("=" * 60)
    print("NSO NED Installation Script")
    print("=" * 60)
    print(f"NSO Directory: {NSO_DIR}")
    print(f"Packages Directory: {PACKAGES_DIR}")
    print(f"NEDs Directory: {NEDS_DIR}")
    print()
    
    # Extract the NED
    if extract_ned_package(ned_file):
        # Reload packages
        reload_nso_packages()
        print("\n" + "=" * 60)
        print("✅ NED Installation Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Verify package is loaded: ncs_cli -u admin -C 'show packages package'")
        print("2. Update devices to use new NED")
    else:
        print("\n❌ Installation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

