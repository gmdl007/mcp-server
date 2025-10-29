# Top 10 Most Useful Cisco NSO Tools to Implement

Based on current implementation and NSO capabilities, here are the **top 10 most valuable tools** to add to your NSO automation server:

---

## 🎯 **Currently Implemented** ✅
- Device management (`show_all_devices`)
- Interface configuration (`configure_router_interface`, `get_router_interfaces_config`)
- OSPF/BGP service management
- Device sync operations (`sync-from`, `sync-to`, `check_device_sync_status`)
- Configuration comparison (`compare_device_config`)
- Rollback management (`rollback_router_configuration`, `list_rollback_points`)

---

## 🔥 **Top 10 Tools to Implement** (Netsim-Compatible)

> **Note:** These tools are designed to work with netsim virtual devices and don't require real physical hardware. Some tools may have limited functionality with netsim but will work with real devices when available.

### **1. Device Connection & Connectivity** 🔌
**Priority: HIGH** | **Complexity: LOW** | **✅ Works with Netsim**

**Description:**
- Connect/disconnect devices from NSO
- Ping devices to check connectivity
- Check device connection status
- Verify device reachability before operations

**Use Cases:**
- Verify device is reachable before config changes
- Test connectivity after network changes
- Troubleshoot connection issues
- Validate NSO can communicate with devices

**NSO API:**
```python
# Device connection
device.connect()

# Ping device
device.ping()

# Check connection status
device.state.last_connect
```

**Functions to Implement:**
- `connect_device(device)` - Connect to a device
- `disconnect_device(device)` - Disconnect from a device
- `ping_device(device)` - Ping a device
- `get_device_connection_status(device)` - Check if device is connected
- `check_device_connectivity(device)` - Verify device is reachable

**Example CLI:**
```bash
ncs_cli> devices device xr9kv-1 connect
ncs_cli> devices device xr9kv-1 ping
ncs_cli> show devices device xr9kv-1 state | grep connected
```

---

### **2. Commit Queue Management** 📝
**Priority: HIGH** | **Complexity: LOW** | **✅ Works with Netsim**

**Description:**
- View pending commits
- Check commit status and history
- Commit with options (dry-run, async)
- Manage commit queue

**Use Cases:**
- Monitor pending configuration changes
- Verify commits completed successfully
- Debug commit failures
- Manage commit queue during high load

**NSO API:**
```python
# Commit queue
root.commit_queue.queue_element

# Commit with dry-run
with maapi.single_write_trans('admin', 'python') as t:
    # Make changes
    t.apply_params(True)  # dry-run
```

**Functions to Implement:**
- `list_commit_queue()` - List pending commits
- `get_commit_status(commit_id)` - Get status of a commit
- `commit_dry_run()` - Dry-run commit to see changes
- `commit_with_options(async=False, no_networking=False)` - Commit with options
- `clear_commit_queue()` - Clear commit queue (admin only)

**Example CLI:**
```bash
ncs_cli> show commit-queue
ncs_cli> commit dry-run
ncs_cli> show commit-queue queue-element {id}
```

---

### **3. Bulk Operations** 🔁
**Priority: HIGH** | **Complexity: LOW** | **✅ Works with Netsim**

**Description:**
- Apply configuration to multiple devices
- Batch operations (sync, compare, etc.)
- Device groups and filtering
- Parallel operations

**Use Cases:**
- Sync all devices after NSO restart
- Apply same config to multiple devices
- Bulk sync-from or sync-to operations
- Compare all devices at once

**Functions to Implement:**
- `sync_all_devices(direction='to')` - Sync all devices (sync-to or sync-from)
- `compare_all_devices()` - Compare all devices against NSO
- `get_all_devices_sync_status()` - Check sync status for all devices
- `apply_config_to_devices(devices, config_section)` - Apply config to multiple devices

**Example Use:**
```python
# Sync all devices to NSO config
sync_all_devices(direction='to')

# Compare all devices
compare_all_devices()
```

---

### **4. Device Capabilities & Modules** 🔧
**Priority: MEDIUM** | **Complexity: Low**

**Description:**
- Connect/disconnect devices
- Check device capabilities
- Verify device connectivity
- Ping devices

**Use Cases:**
- Verify device is reachable before config
- Check device support for features
- Test connectivity after network changes
- Validate NED compatibility

**NSO API:**
```python
# Device connection
device.connect()

# Device capabilities
device.capability

# Ping device
device.ping()
```

**Functions to Implement:**
- `connect_device(device)` - Connect to a device
- `disconnect_device(device)` - Disconnect from a device
- `ping_device(device)` - Ping a device
- `get_device_capabilities(device)` - List device capabilities
- `check_device_connectivity(device)` - Check if device is reachable

**Example CLI:**
```bash
ncs_cli> devices device xr9kv-1 connect
ncs_cli> devices device xr9kv-1 ping
ncs_cli> devices device xr9kv-1 check-sync
```

---

### **5. Commit Queue Management** 📝
**Priority: MEDIUM** | **Complexity: Medium**

**Description:**
- View pending commits
- Manage commit queue
- Check commit status
- Commit with options (dry-run, async, etc.)

**Use Cases:**
- Monitor pending configuration changes
- Manage commit queue during high load
- Verify commits completed successfully
- Debug commit failures

**NSO API:**
```python
# Commit queue
root.commit_queue

# Commit with transaction
t.apply()
```

**Functions to Implement:**
- `list_commit_queue()` - List pending commits
- `get_commit_status(commit_id)` - Get status of a commit
- `commit_dry_run(device=None)` - Dry-run commit to see changes
- `commit_async(device=None)` - Commit asynchronously
- `clear_commit_queue()` - Clear commit queue (admin only)

**Example CLI:**
```bash
ncs_cli> show commit-queue
ncs_cli> commit dry-run
```

---

### **5. Configuration Section Management** ⚙️
**Priority: MEDIUM** | **Complexity: LOW** | **✅ Works with Netsim**

**Description:**
- Get/delete any configuration section
- Query specific config paths
- Batch config reads
- Config path exploration

**Use Cases:**
- Read specific config sections (BGP, ISIS, etc.)
- Delete entire config sections
- Explore device configuration structure
- Extract specific configuration data

**NSO API:**
```python
# Access config sections
root.devices.device[name].config

# Delete config section
del device.config.section
```

**Functions to Implement:**
- `get_router_config_section(device, section)` - Get specific config section
- `delete_config_section(device, section, confirm=False)` - Delete config section
- `list_config_sections(device)` - List available config sections
- `get_config_tree(device, path)` - Get config subtree

**Example CLI:**
```bash
ncs_cli> show running-config devices device xr9kv-1 config bgp
ncs_cli> devices device xr9kv-1 config bgp delete-config
```

---

### **6. Service Status & List** 📋
**Priority: MEDIUM** | **Complexity: LOW** | **✅ Works with Netsim**

**Description:**
- List all services for a device
- Get service status and details
- Query service instances
- Service dependency information

**Use Cases:**
- See what services are using a device
- Find all service instances
- Verify service configuration
- Service inventory management

**NSO API:**
```python
# Service list for device
root.devices.device[name].service_list

# Service instances
root.services.ospf.base
```

**Functions to Implement:**
- `get_services_for_device(device)` - List all services on a device
- `list_all_service_instances(service_type=None)` - List all service instances
- `get_service_details(service_type, service_name)` - Get detailed service info
- `count_services_by_type()` - Count services by type

**Example CLI:**
```bash
ncs_cli> show devices device xr9kv-1 service-list
ncs_cli> show services service-list
```

---

### **7. Transaction Management** 💾
**Priority: MEDIUM** | **Complexity: LOW** | **✅ Works with Netsim**

**Description:**
- View transaction history
- Check transaction status
- Transaction locking information
- Track configuration changes

**Use Cases:**
- Track who made what changes
- Verify transaction completion
- Debug locking issues
- Audit configuration changes

**NSO API:**
```python
# Transaction info
root.transactions.transaction

# Lock info
root.locks.lock
```

**Functions to Implement:**
- `list_transactions(limit=50)` - List recent transactions
- `get_transaction_details(transaction_id)` - Get transaction details
- `check_locks(device=None)` - Check active locks
- `wait_for_lock(timeout=30)` - Wait for lock to release

**Example CLI:**
```bash
ncs_cli> show transactions
ncs_cli> show locks
```

---

### **8. Service Redeploy** 🔄
**Priority: MEDIUM** | **Complexity: LOW** | **✅ Works with Netsim**

**Description:**
- Redeploy services after changes
- Reactivate services
- Verify service deployment

**Use Cases:**
- Redeploy OSPF service after device changes
- Reactivate services after maintenance
- Refresh service configuration
- Re-apply service to devices

**NSO API:**
```python
# Service redeploy
service = root.services.ospf.base[router_name]
service.reactive_re_deploy()
```

**Functions to Implement:**
- `redeploy_service(service_type, service_name)` - Redeploy a service
- `redeploy_all_services_for_device(device)` - Redeploy all services on device

**Example CLI:**
```bash
ncs_cli> services ospf base xr9kv-1 reactive-re-deploy
```

---

### **9. Compliance & Validation** ✔️
**Priority: MEDIUM** | **Complexity: High**

**Description:**
- Validate configurations against policies
- Run compliance checks
- Generate compliance reports
- Policy enforcement

**Use Cases:**
- Ensure configs meet organizational standards
- Validate security policies
- Check for configuration drift
- Generate audit reports

**NSO API:**
```python
# Compliance (if compliance package installed)
root.compliance.compliance_data
```

**Functions to Implement:**
- `run_compliance_check(device)` - Run compliance check on device
- `validate_config_policy(device, policy)` - Validate against specific policy
- `get_compliance_report()` - Generate compliance report
- `check_config_drift(device)` - Check for configuration drift

**Example CLI:**
```bash
ncs_cli> compliance check-report device xr9kv-1
```

---

### **8. Notification & Event Monitoring** 📢
**Priority: LOW** | **Complexity: High**

**Description:**
- Monitor device notifications
- Track configuration changes
- Subscribe to events
- Event filtering and alerting

**Use Cases:**
- Monitor device events in real-time
- Track configuration change history
- Alert on specific events
- Audit trail for changes

**NSO API:**
```python
# Notifications
root.notifications

# Service notifications
root.services.ospf.base[router_name].notifications
```

**Functions to Implement:**
- `list_notifications(device=None, limit=100)` - List recent notifications
- `subscribe_to_notifications(device, callback)` - Subscribe to real-time events
- `get_notification_history(device, hours=24)` - Get notification history

**Example CLI:**
```bash
ncs_cli> show notifications
ncs_cli> show notifications device xr9kv-1
```

---

### **9. Configuration Templates** 📋
**Priority: MEDIUM** | **Complexity: Medium**

**Description:**
- Create and manage config templates
- Apply templates to devices
- Template variables and inheritance
- Template validation

**Use Cases:**
- Standardize device configurations
- Quick deployment of common configs
- Maintain configuration consistency
- Template-based service provisioning

**NSO API:**
```python
# Config templates (if template package installed)
root.config_template
```

**Functions to Implement:**
- `create_config_template(name, config)` - Create a config template
- `apply_template_to_device(template, device, variables)` - Apply template to device
- `list_config_templates()` - List available templates
- `validate_template(template, device)` - Validate template against device

**Example CLI:**
```bash
ncs_cli> config-template apply template ospf-base router xr9kv-1
```

---

### **10. Service Path & Dependency Tracking** 🔗
**Priority: LOW** | **Complexity: High**

**Description:**
- Track service dependencies
- View service paths
- Analyze service impact
- Service relationship mapping

**Use Cases:**
- Understand service dependencies
- Impact analysis for changes
- Service topology visualization
- Dependency validation

**NSO API:**
```python
# Service path (if service-mapping package installed)
root.service_mapping.service_path
```

**Functions to Implement:**
- `get_service_dependencies(service)` - Get service dependencies
- `get_service_path(service)` - Get service path
- `analyze_service_impact(service)` - Analyze impact of service changes
- `get_services_on_device(device)` - Get all services using a device

**Example CLI:**
```bash
ncs_cli> show services service-list device xr9kv-1
ncs_cli> show services service-list | grep ospf
```

---

## 📊 **Implementation Priority**

### **Phase 1 (High Priority - Implement First - All Netsim-Compatible):**
1. ✅ **Device Connection & Connectivity** - Essential for device management
2. ✅ **Commit Queue Management** - Critical for operations
3. ✅ **Bulk Operations** - Efficiency improvement

### **Phase 2 (Medium Priority - All Netsim-Compatible):**
4. ✅ **Device Capabilities & Modules** - Device information
5. ✅ **Configuration Section Management** - Advanced config operations
6. ✅ **Service Status & List** - Service inventory
7. ✅ **Transaction Management** - Change tracking
8. ✅ **Service Redeploy** - Service lifecycle

### **Phase 3 (Advanced - May Require Additional Packages):**
9. ✅ **Compliance & Validation** - Requires compliance package
10. ✅ **Configuration Templates** - Requires template package

---

## 🛠️ **Implementation Notes**

### **NSO API Access Patterns:**
- Use `maapi.Maapi()` for read operations
- Use `maapi.single_write_trans()` for write operations
- Access operational data via `live_status` subtree
- Access actions via `_ncs_action_` namespace

### **Error Handling:**
- Always wrap in try/except blocks
- Handle device connectivity errors gracefully
- Provide fallback to CLI commands where API is limited

### **Testing:**
- Test with netsim devices first
- Verify against NSO CLI output
- Test error scenarios (device down, invalid config, etc.)

---

## 📚 **References**

- **NSO Python API Documentation:** `/Users/gudeng/NCS-614/doc/html/ncspyapi/ncspyapi.html`
- **NSO Developer Guide:** https://nso-docs.cisco.com
- **NSO Examples:** `/Users/gudeng/NCS-614/examples.ncs/`

---

## 💡 **Next Steps**

1. **Choose tools from Phase 1** to implement first
2. **Review NSO API documentation** for specific functions
3. **Test with netsim devices** before production use
4. **Document tool parameters** and return values clearly
5. **Add error handling** and user-friendly messages

---

*Last Updated: 2025-01-21*
*Based on NSO 6.1.4 and current FastMCP NSO Server implementation*

