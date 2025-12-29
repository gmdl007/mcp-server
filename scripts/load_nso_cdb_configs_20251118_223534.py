#!/usr/bin/env python3
"""
Load device configurations from backup files into NSO CDB
Date: 2025-11-18 22:35:34
Tag: dcloud_original_config_20251118_223534

This script loads the backed-up device configurations back into NSO's CDB.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Set NSO environment variables
NSO_DIR = "/Users/gudeng/NCS-6413"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Configuration
BACKUP_DIR = Path("/Users/gudeng/MCP_Server/backups/nso_configs/dcloud_original_config_20251118_223534")
TIMESTAMP = "20251118_223534"
TAG = "dcloud_original_config"

# List of all devices
DEVICES = [
    'node-1', 'node-2', 'node-3', 'node-4', 'node-5', 'node-6',
    'node-7', 'node-8', 'pce-11', 'xr9kv0', 'xr9kv1', 'xr9kv2'
]

def clean_config_file(filepath):
    """Remove header comments from XML config file, keep only the XML content"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # For XML format, remove XML comments that are metadata headers
        # Use regex to remove the entire header comment block
        import re
        # Remove XML comment block that contains backup metadata
        # Pattern: <!-- ... --> (multiline, non-greedy)
        pattern = r'<!--\s*Configuration backup.*?-->\s*\n?'
        result = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up any extra whitespace
        result = result.strip()
        
        # Ensure we have valid XML
        if not result.startswith('<?xml') and not result.startswith('<config'):
            return None
        
        return result
    except Exception as e:
        return None

def load_config_to_nso(device_name, config_content, mode='merge', dry_run=False):
    """Load configuration into NSO CDB using ncs_load tool"""
    try:
        ncs_load_path = f'{NSO_DIR}/bin/ncs_load'
        ncs_cli_path = f'{NSO_DIR}/bin/ncs_cli'
        
        # Create a temporary file with the cleaned config (XML format)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp_file:
            tmp_file.write(config_content)
            tmp_file_path = tmp_file.name
        
        try:
            abs_file_path = os.path.abspath(tmp_file_path)
            
            # Use ncs_load to load the config
            # -l: load mode
            # -m: merge mode (default when multiple files, but we use it explicitly)
            # -r: replace mode (if specified)
            # -F x: XML format (NSO's internal format)
            # -n: no-networking (load to CDB only, don't push to devices) - used for dry-run
            # Note: No -p flag needed since XML already contains full path structure
            load_flags = ['-l', '-m', '-F', 'x']
            if mode == 'replace':
                load_flags.remove('-m')  # Remove merge flag
                load_flags.append('-r')  # Add replace flag
            if dry_run:
                load_flags.append('-n')  # no-networking (load to CDB only)
            
            load_flags.append(abs_file_path)
            
            result = subprocess.run(
                [ncs_load_path] + load_flags,
                capture_output=True,
                text=True,
                timeout=120,
                env=os.environ.copy()
            )
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            if result.returncode != 0:
                return False, f"ncs_load error: {result.stderr or result.stdout}"
            
            output = result.stdout + result.stderr
            
            # Check for errors
            if 'Error' in output or 'error' in output or 'failed' in output.lower():
                return False, f"Error in output: {output}"
            
            # If dry-run, return the output
            if dry_run:
                return True, output if output.strip() else "Dry-run successful (no changes or no output)"
            
            return True, None
            
        except FileNotFoundError:
            # Fallback to NSO CLI if ncs_load not available
            return load_config_to_nso_cli(device_name, config_content, mode, dry_run, tmp_file_path)
        except Exception as e:
            # Clean up temp file on error
            try:
                os.unlink(tmp_file_path)
            except:
                pass
            return False, str(e)
            
    except Exception as e:
        return False, str(e)

def load_config_to_nso_cli(device_name, config_content, mode, dry_run, tmp_file_path):
    """Fallback: Load using NSO CLI (may not work for all config formats)"""
    try:
        ncs_cli_path = f'{NSO_DIR}/bin/ncs_cli'
        abs_file_path = os.path.abspath(tmp_file_path)
        
        if dry_run:
            cmd_script = f"""config
devices device {device_name} config
load {mode} {abs_file_path}
commit dry-run
top
"""
        else:
            cmd_script = f"""config
devices device {device_name} config
load {mode} {abs_file_path}
commit
top
"""
        
        result = subprocess.run(
            [ncs_cli_path, '-u', 'cisco', '-C'],
            input=cmd_script,
            capture_output=True,
            text=True,
            timeout=120,
            env=os.environ.copy()
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode != 0 or 'Error' in output:
            return False, f"NSO CLI error: {output}"
        
        if dry_run:
            return True, output if output.strip() else None
        
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load NSO CDB configuration backups')
    parser.add_argument('--dry-run', action='store_true', help='Dry-run mode: preview changes without applying')
    args = parser.parse_args()
    
    dry_run = args.dry_run
    
    print("=" * 80)
    if dry_run:
        print("DRY-RUN: Load NSO CDB Configuration Backup (Preview Only)")
    else:
        print("Load NSO CDB Configuration Backup")
    print("=" * 80)
    print(f"Backup directory: {BACKUP_DIR}")
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Tag: {TAG}")
    print(f"Total devices: {len(DEVICES)}")
    print()
    print("ℹ️  NOTE: These configs are in NSO XML format (loadable into NSO CDB)")
    print()
    
    if dry_run:
        print("🔍 DRY-RUN MODE: No changes will be applied to NSO CDB")
        print("   This will show what would be loaded and committed.")
    else:
        print("⚠️  WARNING: This will attempt to load configurations into NSO CDB!")
        print("   Make sure you want to restore these configs.")
        print()
        # Ask for confirmation
        response = input("Do you want to continue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Aborted.")
            return 1
    
    print()
    if dry_run:
        print("Previewing configuration loads (dry-run)...")
    else:
        print("Loading configurations...")
    print()
    
    results = {
        'success': [],
        'failed': []
    }
    
    for i, device in enumerate(DEVICES, 1):
        print(f"[{i}/{len(DEVICES)}] Loading {device}...", end=' ', flush=True)
        
        # Find config file (XML format)
        config_file = BACKUP_DIR / f"{device}_{TAG}_{TIMESTAMP}.xml"
        
        if not config_file.exists():
            print(f"❌ FILE NOT FOUND")
            results['failed'].append((device, f"Config file not found: {config_file.name}"))
            continue
        
        # Clean config file (remove headers)
        config_content = clean_config_file(config_file)
        if config_content is None or not config_content.strip():
            print(f"❌ EMPTY CONFIG")
            results['failed'].append((device, "Config file is empty or could not be read"))
            continue
        
        # Load config into NSO
        success, error = load_config_to_nso(device, config_content, mode='merge', dry_run=dry_run)
        
        if success:
            if dry_run:
                print(f"✅ Would load (dry-run OK)")
            else:
                print(f"✅ Loaded")
            results['success'].append(device)
        else:
            print(f"❌ ERROR: {error}")
            results['failed'].append((device, error))
    
    # Print summary
    print()
    print("=" * 80)
    if dry_run:
        print("DRY-RUN SUMMARY")
    else:
        print("LOAD SUMMARY")
    print("=" * 80)
    if dry_run:
        print(f"✅ Would successfully load: {len(results['success'])}/{len(DEVICES)}")
    else:
        print(f"✅ Successfully loaded: {len(results['success'])}/{len(DEVICES)}")
    print(f"❌ Failed: {len(results['failed'])}")
    print()
    
    if results['success']:
        if dry_run:
            print("Would successfully load:")
        else:
            print("Successfully loaded:")
        for device in results['success']:
            print(f"  ✅ {device}")
        print()
    
    if results['failed']:
        print("Failed:")
        for device, error in results['failed']:
            print(f"  ❌ {device}: {error}")
        print()
    
    return 0 if len(results['failed']) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

