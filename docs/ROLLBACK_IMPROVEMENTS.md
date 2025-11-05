# Rollback Improvements - Commit Tagging & Descriptions

## Overview

The NSO automation MCP tools have been enhanced with commit tagging and description capabilities to eliminate trial-and-error when identifying rollback points. This allows you to tag each commit with a description, making it much easier to know which rollback point to restore.

## New Features

### 1. **Commit with Description Tool**

A new tool `commit_with_description()` allows you to commit configuration changes with a descriptive tag:

```python
# Commit all pending changes with a description
commit_with_description("Setup OSPF base services for 3 routers")
commit_with_description("Configured Loopback0 interfaces for all routers")
commit_with_description("Added iBGP peering between router 1 and 3")
```

**Benefits:**
- Each commit is tagged with a description
- Descriptions appear in rollback history
- Easy to identify which rollback point contains which changes
- No more guessing rollback IDs

### 2. **Enhanced Rollback with Descriptions**

The `rollback_router_configuration()` function now accepts an optional description parameter:

```python
# Rollback to most recent commit
rollback_router_configuration(0)

# Rollback 2 steps with a description tag
rollback_router_configuration(1, description="Rollback to before OSPF config")
```

**Benefits:**
- Tag rollback operations themselves
- Document why a rollback was performed
- Better audit trail

### 3. **Improved Rollback Listing**

The `list_rollback_points()` function has been enhanced to show more information:

```python
# List available rollback points
list_rollback_points(limit=50)
```

**Features:**
- Shows rollback IDs with step information
- Provides guidance on how to view detailed rollback info
- Instructions for using rollback with descriptions

## Best Practices

### Workflow Example

1. **Make configuration changes:**
   ```python
   configure_router_interface('xr9kv-1', 'Loopback/0', ip_address='1.1.1.1/32')
   configure_router_interface('xr9kv-2', 'Loopback/0', ip_address='2.2.2.2/32')
   configure_router_interface('xr9kv-3', 'Loopback/0', ip_address='3.3.3.3/32')
   ```

2. **Commit with descriptive tag:**
   ```python
   commit_with_description("Configured Loopback0 interfaces for all 3 routers")
   ```

3. **Continue with more changes:**
   ```python
   setup_ospf_base_service('xr9kv-1', '1.1.1.1', '0')
   setup_ospf_base_service('xr9kv-2', '2.2.2.2', '0')
   setup_ospf_base_service('xr9kv-3', '3.3.3.3', '0')
   ```

4. **Commit this batch:**
   ```python
   commit_with_description("Setup OSPF base services for all routers")
   ```

5. **When you need to rollback:**
   ```python
   # List rollback points to see what's available
   list_rollback_points()
   
   # Rollback to before OSPF config (1 step back)
   rollback_router_configuration(0, description="Rollback to before OSPF setup")
   ```

### Description Guidelines

**Good descriptions:**
- "Configured Loopback0 for routers 1, 2, and 3"
- "Setup OSPF base service for xr9kv-1"
- "Added iBGP peering between router 1 and 3 via Loopback0"
- "Removed all OSPF neighbor relationships"

**Poor descriptions:**
- "Changes" (too vague)
- "Config" (not descriptive)
- "Update" (doesn't explain what)

## Technical Details

### How It Works

1. **Commit with Description:**
   - Uses NSO's `CommitParams` API
   - Stores description with the commit transaction
   - Description is accessible via rollback history

2. **Rollback Points:**
   - Each commit creates a rollback point
   - Rollback ID 0 = most recent commit (1 step back)
   - Rollback ID 1 = 2 steps back
   - Rollback ID n = (n+1) steps back

3. **Viewing Commit History:**
   - Use `list_rollback_points()` for basic info
   - For detailed commit descriptions, use NSO CLI:
     ```bash
     ncs_cli -u admin
     show rollback 0 detail
     show rollback 1 detail
     ```

## Migration Notes

- **Backward Compatible:** All existing tools work as before
- **Optional Descriptions:** Descriptions are optional - existing code continues to work
- **Default Behavior:** If no description is provided, commits work as before

## Example: Complete Setup with Tagged Commits

```python
# Step 1: Configure interfaces
configure_router_interface('xr9kv-1', 'Loopback/0', ip_address='1.1.1.1/32')
configure_router_interface('xr9kv-2', 'Loopback/0', ip_address='2.2.2.2/32')
configure_router_interface('xr9kv-3', 'Loopback/0', ip_address='3.3.3.3/32')
commit_with_description("Configured Loopback0 interfaces")

# Step 2: Setup physical links
configure_router_interface('xr9kv-1', 'GigabitEthernet/0/0/0/0', ip_address='192.168.12.1/30')
configure_router_interface('xr9kv-2', 'GigabitEthernet/0/0/0/0', ip_address='192.168.12.2/30')
configure_router_interface('xr9kv-2', 'GigabitEthernet/0/0/0/1', ip_address='192.168.23.1/30')
configure_router_interface('xr9kv-3', 'GigabitEthernet/0/0/0/1', ip_address='192.168.23.2/30')
commit_with_description("Configured physical links: R1-R2 and R2-R3")

# Step 3: Setup OSPF
setup_ospf_base_service('xr9kv-1', '1.1.1.1', '0')
setup_ospf_base_service('xr9kv-2', '2.2.2.2', '0')
setup_ospf_base_service('xr9kv-3', '3.3.3.3', '0')
commit_with_description("Setup OSPF base services for all routers")

# Step 4: Setup OSPF neighbors
setup_ospf_neighbor_service('xr9kv-1', '1.1.1.1', 'xr9kv-2', ...)
setup_ospf_neighbor_service('xr9kv-2', '2.2.2.2', 'xr9kv-3', ...)
commit_with_description("Setup OSPF neighbor relationships")

# Step 5: Setup iBGP
setup_ibgp_service('r1-r3-ibgp', 65000, 'xr9kv-1', '1.1.1.1', '1.1.1.1', 
                   'xr9kv-3', '3.3.3.3', '3.3.3.3')
commit_with_description("Setup iBGP peering between router 1 and 3")

# If you need to rollback:
# - Rollback ID 0: Before iBGP setup
# - Rollback ID 1: Before OSPF neighbors
# - Rollback ID 2: Before OSPF base
# - Rollback ID 3: Before physical links
# - Rollback ID 4: Before Loopback0 configs
```

## See Also

- `rollback_router_configuration()` - Rollback to a specific point
- `list_rollback_points()` - View available rollback points
- `commit_with_description()` - Commit with a tag

