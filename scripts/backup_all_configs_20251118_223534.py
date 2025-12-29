#!/usr/bin/env python3
"""
Backup all device configurations with timestamp and tag
Created: 2025-11-18 22:35:34
Tag: dcloud_original_config
"""

import os
from pathlib import Path

# Base directory for backups
BASE_DIR = Path("/Users/gudeng/MCP_Server/backups/nso_configs/dcloud_original_config_20251118_223534")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Note: This script is a placeholder. The actual configs should be saved via MCP tools
# or by reading from the tool outputs. For now, we'll create a README in the backup directory
# indicating that configs should be saved here.

README_CONTENT = """# Device Configuration Backups

**Backup Date:** 2025-11-18 22:35:34 UTC
**Tag:** dcloud_original_config
**Purpose:** Original dCloud lab configuration backup

## Devices to Backup

- node-1
- node-2
- node-3
- node-4
- node-5
- node-6
- node-7
- node-8
- pce-11
- xr9kv0
- xr9kv1
- xr9kv2

## File Naming Convention

Each config file should be named: `{device_name}_dcloud_original_config_20251118_223534.cfg`

Example: `node-1_dcloud_original_config_20251118_223534.cfg`

## Status

Configurations are being saved via MCP tools. Check individual .cfg files for device configurations.
"""

# Create README
readme_path = BASE_DIR / "README.md"
with open(readme_path, 'w') as f:
    f.write(README_CONTENT)

print(f"Backup directory created: {BASE_DIR}")
print(f"README created: {readme_path}")

