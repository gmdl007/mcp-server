# NSO Rollback Reference for dcloud Lab

## Complete Rollback Points List

### Current Setup (2025-11-11)

| Rollback ID | Name | Via | Date | Creator | Description |
|------------|------|-----|------|---------|-------------|
| **0** | rollback10014 | cli | 2025-11-11 11:44:07 | cisco | **Most Recent - After sync-from pce-11** |
| **1** | rollback10013 | cli | 2025-11-11 11:44:04 | cisco | After sync-from node-8 |
| **2** | rollback10012 | cli | 2025-11-11 11:44:02 | cisco | After sync-from node-7 |
| **3** | rollback10011 | cli | 2025-11-11 11:44:00 | cisco | After sync-from node-6 |
| **4** | rollback10010 | cli | 2025-11-11 11:43:58 | cisco | After sync-from node-5 |
| **5** | rollback10009 | cli | 2025-11-11 11:43:56 | cisco | After sync-from node-4 |
| **6** | rollback10008 | cli | 2025-11-11 11:43:53 | cisco | After sync-from node-3 |
| **7** | rollback10007 | cli | 2025-11-11 11:43:51 | cisco | After sync-from node-2 |
| **8** | rollback10006 | cli | 2025-11-11 11:43:42 | cisco | After sync-from node-1 |
| **9** | rollback10005 | **fix_admin_mode_sync** | 2025-11-11 11:42:16 | admin | **After fixing admin mode sync error** |
| **10** | rollback10004 | **add_devices_cisco_auth** | 2025-11-11 11:35:51 | admin | **After adding all 9 devices with cisco authgroup** |
| **11** | rollback10003 | cli | 2025-11-11 11:33:02 | admin | Before device addition |
| **12** | rollback10001 | system | 2025-11-08 15:13:26 | system | System rollback point |

## Key Rollback Points Explained

### **Rollback ID 0** (rollback10014) - Most Recent ✅
- **Via:** cli
- **Description:** Current state - All 9 routers successfully synced
- **Use this to:** Restore to the current working state

### **Rollback ID 9** (rollback10005) - After Admin Mode Fix
- **Via:** fix_admin_mode_sync
- **Description:** After setting NED setting read/admin-show-running-config = false
- **Configuration:** All devices have admin mode sync fix applied
- **Use this to:** Restore to state after fixing sync error but before syncing devices

### **Rollback ID 10** (rollback10004) - Initial Device Setup
- **Via:** add_devices_cisco_auth
- **Description:** After adding all 9 devices with cisco authgroup
- **Configuration:**
  - Devices: node-1 to node-8, pce-11
  - Authgroup: cisco
  - NED: cisco-iosxr-cli-7.61
  - Port: 22
- **Use this to:** Restore to initial device setup (before admin mode fix and sync)

## How to Restore

### Restore to Initial Setup (All devices added and synced)
```bash
ncs_cli -u admin -C
rollback 0
```

### Restore to Before Sync Operations
```bash
rollback 9
```

### Restore to Before Device Addition
```bash
rollback 10
```

## Understanding the "Via" Field

The **"via"** field in NSO rollback points indicates how the rollback point was created:

- **`cli`** - Created via NSO CLI commands (e.g., sync-from operations)
- **`add_devices_cisco_auth`** - Created by the add_devices_cisco_auth script
- **`fix_admin_mode_sync`** - Created by the fix_admin_mode_sync script
- **`system`** - Created by NSO system operations

### How to Use This Reference

1. **Identify rollback points** by their "via" field and timestamp
2. **Match the "via" field** to understand what operation created each point
3. **Use rollback IDs** to restore to specific states

## Note About Commit Descriptions

NSO's `show rollback` command does **not display commit comments/descriptions** in the rollback list view. The descriptions are stored in transaction logs but not shown in the standard rollback output.

**This reference document maps rollback IDs to their actual meaning** using:
- The "via" field (which script/operation created it)
- Timestamps (when it was created)
- Context (what was happening at that time)

## Current Configuration State

- **9 dcloud real routers** configured and synced
- **Authgroup:** cisco
- **NED:** cisco-iosxr-cli-7.61
- **NED Setting:** read/admin-show-running-config = false
- **All devices successfully synced from dcloud routers**

