# Migrating NSO Configuration from 6.1.4 to 6.4.1.3

This guide explains how to copy the old NSO 6.1.4 configuration to the new NSO 6.4.1.3 instance.

## Overview

The old NSO 6.1.4 configuration is stored in:
- **Backup file**: `/Users/gudeng/MCP_Server/backups/nso_configs/ncs_complete_backup_20251119_000310.xml`

This backup contains:
- Device configurations (xr9kv-*, node-*, pce-11)
- Authgroups (cisco, default, netsim, cisco-2)
- Services (OSPF, iBGP)
- AAA configuration

## Method 1: Using Python Script (Recommended)

### Prerequisites

1. **Start NSO 6.4.1.3**:
   ```bash
   ncs-start
   # Or manually:
   export JAVA_HOME=$(/usr/libexec/java_home -v 17)
   export PATH=$JAVA_HOME/bin:$PATH
   source /Users/gudeng/NCS-6413/ncsrc
   cd /Users/gudeng/ncs-run-6413
   ncs
   ```

2. **Run the migration script**:
   ```bash
   cd /Users/gudeng/MCP_Server
   python3 load_old_nso_config_20250101.py
   ```

The script will:
- Read the backup XML file
- Update NED IDs to be compatible with NSO 6.4.1.3 (cisco-iosxr-cli-7.61)
- Load the configuration into NSO using merge mode (won't overwrite existing config)
- Show a summary of loaded devices and authgroups

### After Migration

1. **Verify devices**:
   ```bash
   ncs_cli -u admin -C
   show devices device
   ```

2. **Check authgroups**:
   ```bash
   show devices authgroups
   ```

3. **Update device NED IDs** (if needed):
   - Some devices may need manual NED ID updates
   - Use MCP tool: `configure_router_interface` or Python API

4. **Reload packages**:
   ```bash
   packages reload
   ```

## Method 2: Using MCP Tool (Alternative)

If NSO 6.4.1.3 is running and MCP server is connected:

1. **Load the complete backup**:
   ```
   Use MCP tool: load_ncs_config
   - backup_file: /Users/gudeng/MCP_Server/backups/nso_configs/ncs_complete_backup_20251119_000310.xml
   - mode: merge (to avoid overwriting existing config)
   - dry_run: false
   ```

2. **Update NED IDs** (after loading):
   - Devices with old NED IDs will need to be updated
   - Use MCP tool: `configure_router_interface` or device configuration tools

## Method 3: Manual XML Load via NSO CLI

1. **Start NSO 6.4.1.3**

2. **Load configuration via CLI**:
   ```bash
   ncs_cli -u admin -C
   load merge /Users/gudeng/MCP_Server/backups/nso_configs/ncs_complete_backup_20251119_000310.xml
   commit
   ```

3. **Update NED IDs manually**:
   ```bash
   configure
   devices device <device-name> device-type cli ned-id cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61
   commit
   ```

## Important Notes

### NED ID Compatibility

The old NSO 6.1.4 used:
- `cisco-iosxr-cli-7.52`
- `cisco-iosxr-cli-3.5`
- `cisco-iosxr_netconf-7.10.1.1`

NSO 6.4.1.3 uses:
- `cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61`

The migration script automatically updates these, but you should verify after loading.

### Services Compatibility

Some service packages (OSPF, iBGP) from NSO 6.1.4 may not be compatible with NSO 6.4.1.3. If you encounter "Must be recompiled!" errors:

1. Remove incompatible service packages from `packages/` directory
2. Reinstall compatible versions for NSO 6.4.1.3
3. Or recreate services using NSO 6.4.1.3 compatible packages

### Device Connectivity

After migration:
1. Verify device connectivity: `ping_device(device_name)` via MCP
2. Fetch SSH host keys: `fetch_ssh_host_keys(device_name)` via MCP
3. Sync configuration: `sync_from_device(device_name)` via MCP

## Troubleshooting

### "Connection refused" Error

- Make sure NSO 6.4.1.3 is running
- Check: `ps aux | grep ncs`
- Start NSO: `ncs-start`

### "Must be recompiled!" Error

- Remove incompatible packages from `packages/` directory
- Clear `state/` directory
- Restart NSO

### "Invalid NED ID" Error

- Update device NED IDs manually
- Use: `devices device <name> device-type cli ned-id cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61`

### Configuration Conflicts

- Use merge mode when loading (default in script)
- Review conflicts: `show configuration`
- Resolve manually if needed

## Files Created

- `/Users/gudeng/MCP_Server/load_old_nso_config_20250101.py` - Migration script
- `/Users/gudeng/ncs-run-6413/ncs-cdb/old_config_migrated.xml` - Updated backup with new NED IDs

## Next Steps

After successful migration:

1. ✅ Verify all devices are loaded
2. ✅ Check authgroups are correct
3. ✅ Update any remaining NED IDs
4. ✅ Test device connectivity
5. ✅ Sync configurations from devices
6. ✅ Verify services are working

