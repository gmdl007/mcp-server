#!/usr/bin/env python3
"""
Backup all device configurations from NSO
Date: 2025-11-18 22:35:34
Tag: dcloud_original_config_20251118_223534

This script uses MCP tools to fetch and save all device configurations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import MCP tools if needed
# For now, this script documents the backup process

BASE_DIR = Path("/Users/gudeng/MCP_Server/backups/nso_configs/dcloud_original_config_20251118_223534")
BASE_DIR.mkdir(parents=True, exist_ok=True)

TIMESTAMP = "20251118_223534"
TAG = "dcloud_original_config"

# List of all devices
DEVICES = [
    'node-1', 'node-2', 'node-3', 'node-4', 'node-5', 'node-6',
    'node-7', 'node-8', 'pce-11', 'xr9kv0', 'xr9kv1', 'xr9kv2'
]

def save_config(device_name, config_content):
    """Save device configuration to file"""
    filename = f"{device_name}_{TAG}_{TIMESTAMP}.cfg"
    filepath = BASE_DIR / filename
    
    # Clean up config content - remove command prompts and timestamps from output
    lines = config_content.split('\n')
    config_lines = []
    skip_until_config = True
    
    for line in lines:
        # Skip until we find the config start
        if skip_until_config:
            if line.strip().startswith('!! Building configuration'):
                skip_until_config = False
                config_lines.append(line)
            continue
        
        # Stop at command prompt
        if line.strip().endswith('#') or (device_name in line and '#' in line):
            break
            
        config_lines.append(line)
    
    config_text = '\n'.join(config_lines)
    
    with open(filepath, 'w') as f:
        f.write(config_text)
    
    print(f"✅ Saved: {filename} ({len(config_text)} bytes)")
    return filepath

def main():
    """Main function"""
    print(f"Backup directory: {BASE_DIR}")
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Tag: {TAG}")
    print(f"Devices: {len(DEVICES)}")
    print()
    
    # Note: This script should be run with MCP tools available
    # For now, it's a template. Configs should be fetched using:
    # execute_device_command(device, 'show running-config')
    
    print("To backup all configs, use MCP tools:")
    print("  execute_device_command(device, 'show running-config')")
    print()
    
    # Check which configs are already saved
    saved = []
    pending = []
    
    for device in DEVICES:
        filename = f"{device}_{TAG}_{TIMESTAMP}.cfg"
        filepath = BASE_DIR / filename
        if filepath.exists():
            saved.append(device)
        else:
            pending.append(device)
    
    print(f"Already saved: {len(saved)}/{len(DEVICES)}")
    if saved:
        print(f"  {', '.join(saved)}")
    print()
    
    if pending:
        print(f"Pending: {len(pending)}")
        print(f"  {', '.join(pending)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

