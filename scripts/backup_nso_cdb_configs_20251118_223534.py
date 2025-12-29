#!/usr/bin/env python3
"""
Backup all device configurations from NSO CDB (Configuration Database)
Date: 2025-11-18 22:35:34
Tag: dcloud_original_config_20251118_223534

This script reads device configurations directly from NSO's CDB and saves them to files.
No need to connect to devices - NSO already has the configs synced in its CDB.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Set NSO environment variables
NSO_DIR = "/Users/gudeng/NCS-6413"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add NSO Python API to Python path
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

# Import NSO modules
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

# Configuration
BASE_DIR = Path("/Users/gudeng/MCP_Server/backups/nso_configs/dcloud_original_config_20251118_223534")
BASE_DIR.mkdir(parents=True, exist_ok=True)

TIMESTAMP = "20251118_223534"
TAG = "dcloud_original_config"

# List of all devices
DEVICES = [
    'node-1', 'node-2', 'node-3', 'node-4', 'node-5', 'node-6',
    'node-7', 'node-8', 'pce-11', 'xr9kv0', 'xr9kv1', 'xr9kv2'
]

def get_device_config_from_cdb(device_name):
    """Get full device configuration from NSO CDB using NSO CLI via subprocess"""
    try:
        import subprocess
        
        # Use NSO CLI with stdin to execute the command
        # NSO CLI command: show full-configuration devices device {name} config | display xml
        # This gets NSO's internal XML format, not device-native CLI format
        ncs_cli_path = f'{NSO_DIR}/bin/ncs_cli'
        
        if not os.path.exists(ncs_cli_path):
            # Fallback to Python API if CLI not available
            return get_device_config_from_cdb_api(device_name)
        
        # Prepare command input - use running-config with XML display
        cmd_input = f'show running-config devices device {device_name} config | display xml\n'
        
        # Run NSO CLI
        result = subprocess.run(
            [ncs_cli_path, '-u', 'cisco', '-C'],
            input=cmd_input,
            capture_output=True,
            text=True,
            timeout=60,
            env=os.environ.copy()
        )
        
        if result.returncode != 0:
            # Try API fallback
            return get_device_config_from_cdb_api(device_name)
        
        config_str = result.stdout.strip()
        
        # Remove command echo and prompt
        # For XML format, look for XML declaration or root element
        lines = config_str.split('\n')
        config_lines = []
        skip_until_config = True
        
        for line in lines:
            # Skip until we find actual XML output
            if skip_until_config:
                # XML starts with <?xml or <config
                if line.strip().startswith('<?xml') or line.strip().startswith('<config'):
                    skip_until_config = False
                    config_lines.append(line)
                continue
            
            # Stop at prompt
            if line.strip().endswith('>') and not line.strip().startswith('<') and not line.strip().startswith('</'):
                # This is a prompt, not XML tag
                if device_name in line or 'ncs#' in line or 'admin@' in line:
                    break
            
            config_lines.append(line)
        
        config_str = '\n'.join(config_lines)
        
        if not config_str or len(config_str) < 50:
            # Try API fallback
            return get_device_config_from_cdb_api(device_name)
        
        return config_str, None
        
    except subprocess.TimeoutExpired:
        return get_device_config_from_cdb_api(device_name)
    except Exception as e:
        return get_device_config_from_cdb_api(device_name)

def get_device_config_from_cdb_api(device_name):
    """Fallback: Get device config using Python API - returns XML format"""
    try:
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        if device_name not in root.devices.device:
            m.end_user_session()
            return None, f"Device '{device_name}' not found in NSO CDB"
        
        config_path = f'/devices/device{{{device_name}}}/config'
        
        # Use maapi.save_config to get XML representation
        # This requires stream connection, so use a simpler approach
        # Just return a note that CLI method should be used
        m.end_user_session()
        return None, "Python API fallback not fully implemented - use NSO CLI method instead"
        
    except Exception as e:
        try:
            m.end_user_session()
        except:
            pass
        return None, str(e)

def save_config(device_name, config_content):
    """Save device configuration to file in XML format"""
    filename = f"{device_name}_{TAG}_{TIMESTAMP}.xml"
    filepath = BASE_DIR / filename
    
    # Add XML comment header with metadata (if not already XML)
    if config_content.strip().startswith('<?xml'):
        # Already has XML declaration, add comment after it
        lines = config_content.split('\n')
        xml_decl = lines[0] if lines else '<?xml version="1.0" encoding="UTF-8"?>'
        rest = '\n'.join(lines[1:]) if len(lines) > 1 else ''
        
        header_comment = f"""<!--
  Configuration backup from NSO CDB
  Device: {device_name}
  Backup Date: 2025-11-18 22:35:34 UTC
  Tag: {TAG}
  Source: NSO Configuration Database (CDB)
  Format: NSO XML (loadable back into NSO CDB)
-->
"""
        full_content = xml_decl + '\n' + header_comment + rest
    else:
        # Not XML format, wrap it
        header = f"""<?xml version="1.0" encoding="UTF-8"?>
<!--
  Configuration backup from NSO CDB
  Device: {device_name}
  Backup Date: 2025-11-18 22:35:34 UTC
  Tag: {TAG}
  Source: NSO Configuration Database (CDB)
  Format: NSO XML (loadable back into NSO CDB)
-->
"""
        full_content = header + config_content
    
    with open(filepath, 'w') as f:
        f.write(full_content)
    
    size = len(full_content)
    return filepath, size

def main():
    """Main function"""
    print("=" * 80)
    print("NSO CDB Configuration Backup")
    print("=" * 80)
    print(f"Backup directory: {BASE_DIR}")
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Tag: {TAG}")
    print(f"Total devices: {len(DEVICES)}")
    print()
    
    results = {
        'success': [],
        'failed': [],
        'not_found': []
    }
    
    for i, device in enumerate(DEVICES, 1):
        print(f"[{i}/{len(DEVICES)}] Processing {device}...", end=' ', flush=True)
        
        config_content, error = get_device_config_from_cdb(device)
        
        if error:
            if 'not found' in error.lower():
                print(f"❌ NOT FOUND")
                results['not_found'].append((device, error))
            else:
                print(f"❌ ERROR: {error}")
                results['failed'].append((device, error))
            continue
        
        if not config_content:
            print(f"❌ NO CONFIG")
            results['failed'].append((device, "No configuration data returned"))
            continue
        
        # Save config to file
        try:
            filepath, size = save_config(device, config_content)
            print(f"✅ Saved ({size:,} bytes)")
            results['success'].append((device, filepath, size))
        except Exception as e:
            print(f"❌ SAVE ERROR: {e}")
            results['failed'].append((device, f"Save error: {e}"))
    
    # Print summary
    print()
    print("=" * 80)
    print("BACKUP SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully saved: {len(results['success'])}/{len(DEVICES)}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⚠️  Not found: {len(results['not_found'])}")
    print()
    
    if results['success']:
        print("Successfully backed up:")
        for device, filepath, size in results['success']:
            print(f"  ✅ {device}: {filepath.name} ({size:,} bytes)")
        print()
    
    if results['failed']:
        print("Failed:")
        for device, error in results['failed']:
            print(f"  ❌ {device}: {error}")
        print()
    
    if results['not_found']:
        print("Not found in NSO CDB:")
        for device, error in results['not_found']:
            print(f"  ⚠️  {device}: {error}")
        print()
    
    # Create summary file
    summary_path = BASE_DIR / "BACKUP_SUMMARY.md"
    with open(summary_path, 'w') as f:
        f.write(f"""# Configuration Backup Summary

**Backup Date:** 2025-11-18 22:35:34 UTC
**Tag:** {TAG}
**Source:** NSO Configuration Database (CDB)
**Format:** NSO XML (loadable back into NSO CDB)
**Total Devices:** {len(DEVICES)}

## Results

- ✅ Successfully saved: {len(results['success'])}/{len(DEVICES)}
- ❌ Failed: {len(results['failed'])}
- ⚠️  Not found: {len(results['not_found'])}

## Successfully Backed Up

""")
        for device, filepath, size in results['success']:
            f.write(f"- ✅ **{device}**: `{filepath.name}` ({size:,} bytes)\n")
        
        if results['failed']:
            f.write("\n## Failed\n\n")
            for device, error in results['failed']:
                f.write(f"- ❌ **{device}**: {error}\n")
        
        if results['not_found']:
            f.write("\n## Not Found in NSO CDB\n\n")
            for device, error in results['not_found']:
                f.write(f"- ⚠️  **{device}**: {error}\n")
    
    print(f"Summary saved to: {summary_path}")
    return 0 if len(results['failed']) == 0 and len(results['not_found']) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

