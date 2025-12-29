# NSO MCP Tools Overview

**Total: ~86 Tools** | **Last Updated: 2025-01-01**

## 📊 Quick Summary

Your NSO MCP server provides comprehensive network automation capabilities organized into 15 major categories:

### Tool Categories

1. **Device Management** (9 tools) - Connect, disconnect, fetch SSH keys, ping, status checks
2. **OSPF Services** (6 tools) - Deploy and manage OSPF routing
3. **BGP Services** (6 tools) - Configure iBGP and BGP groups
4. **Device Information** (5 tools) - Capabilities, versions, NED info
5. **Service Management** (8 tools) - List, deploy, redeploy services
6. **Sync & Configuration** (8 tools) - Sync status, compare configs
7. **Configuration Operations** (6 tools) - Backup, validate, check syntax
8. **Commit & Transactions** (10 tools) - Rollback, commit queue, locks
9. **Operational Data** (11 tools) - Routing tables, CPU, memory, alarms
10. **Command Execution** (2 tools) - Execute show/exec commands
11. **Bulk Operations** (4 tools) - Sync all, compare all devices
12. **Device Groups** (2 tools) - Create and manage device groups
13. **Audit & Tracking** (2 tools) - Configuration changes, notifications
14. **Advanced Operations** (2 tools) - SNMP, ACL management
15. **Package Management** (2 tools) - Reload, redeploy packages
16. **Utility** (3 tools) - Health checks, session management

---

## 🔧 Essential Tools by Use Case

### **Getting Started**
- `show_all_devices()` - List all managed devices
- `nso_health_check()` - Check NSO health and fix issues
- `get_device_connection_status()` - Check device connectivity

### **Adding New Devices**
- `fetch_ssh_host_keys()` - **NEW!** Fetch SSH host keys (required before sync)
- `connect_device()` - Connect to device
- `sync_from_device()` - Pull configuration from device

### **Device Configuration**
- `configure_router_interface()` - Configure IP addresses, descriptions
- `get_router_interfaces_config()` - View interface configurations
- `get_router_config_section()` - Get specific config sections (BGP, OSPF, etc.)

### **Service Deployment**
- `setup_ospf_base_service()` - Deploy OSPF base configuration
- `setup_ospf_neighbor_service()` - Configure OSPF neighbors
- `setup_ibgp_service()` - Deploy iBGP between routers

### **Monitoring & Status**
- `get_bgp_neighbor_status()` - Check BGP peer status
- `get_ospf_neighbor_status()` - Check OSPF adjacencies
- `get_routing_table()` - View routing table
- `get_device_cpu_usage()` - Monitor CPU utilization
- `get_device_memory_usage()` - Monitor memory usage

### **Configuration Management**
- `check_device_sync_status()` - Check if device is in sync
- `compare_device_config()` - Compare NSO vs device config
- `sync_to_device()` - Push NSO config to device
- `sync_from_device()` - Pull device config to NSO

### **Troubleshooting**
- `execute_device_command()` - Run show commands on devices
- `get_device_alarms()` - Check device alarms
- `list_notifications()` - View recent notifications
- `check_locks()` - Check for configuration locks

### **Rollback & Recovery**
- `list_rollback_points()` - View available rollback points
- `rollback_router_configuration()` - Rollback to previous state
- `find_rollback_by_description()` - Find rollback by description
- `backup_device_config()` - Create configuration backup

---

## 📋 Complete Tool List

### Device Management
- `show_all_devices` - List all router devices
- `get_router_interfaces_config` - Get complete interface configuration tree
- `configure_router_interface` - Configure interfaces (IP, description, shutdown)
- `get_interface_operational_status` - Get interface operational status
- `connect_device` - Connect NSO to device
- `disconnect_device` - Disconnect NSO from device
- `ping_device` - Ping device to check connectivity
- `get_device_connection_status` - Get device connection status

### OSPF Service Tools
- `get_ospf_service_config` - Get OSPF service configuration
- `setup_ospf_base_service` - Setup OSPF base service
- `setup_ospf_neighbor_service` - Setup OSPF neighbor service
- `remove_ospf_neighbor_service` - Remove OSPF neighbor service
- `delete_ospf_service` - Delete OSPF service instance
- `normalize_ospf_service_interfaces` - Normalize OSPF interface formats

### BGP Service Tools
- `get_BGP_GRP__BGP_GRP_config` - Get BGP Group service configuration
- `create_BGP_GRP__BGP_GRP_service` - Create BGP Group service
- `delete_BGP_GRP__BGP_GRP_service` - Delete BGP Group service
- `get_ibgp_service_config` - Get iBGP service configuration
- `setup_ibgp_service` - Setup iBGP service between two routers
- `delete_ibgp_service` - Delete iBGP service

### Device Information & Capabilities
- `get_device_capabilities` - Get device capabilities
- `check_yang_modules_compatibility` - Check YANG module compatibility
- `list_device_modules` - List YANG modules supported by device
- `get_device_ned_info` - Get NED (Network Element Driver) information
- `get_device_version` - Get device version information

### Service Management
- `list_available_services` - List all available service models
- `get_service_model_info` - Get detailed service model information
- `list_service_instances` - List instances of a specific service
- `get_services_for_device` - List all services on device
- `get_service_status` - Get service operational status
- `count_services_by_type` - Count services by type
- `redeploy_service` - Redeploy specific service
- `redeploy_all_services_for_device` - Redeploy all services for device

### Sync & Configuration Management
- `check_device_sync_status` - Check device sync status
- `show_sync_differences` - Show differences between NSO and device config
- `compare_device_config` - Compare NSO config with device config
- `sync_from_device` - Sync configuration from device to NSO
- `sync_to_device` - Sync configuration from NSO to device
- `sync_all_devices` - Sync all devices (to/from NSO)
- `compare_all_devices` - Compare all devices against NSO config
- `get_all_devices_sync_status` - Get sync status for all devices

### Configuration Operations
- `get_router_config_section` - Get specific config section (BGP, OSPF, etc.)
- `delete_config_section` - Delete config section
- `list_config_sections` - List available config sections
- `backup_device_config` - Backup device configuration
- `list_device_backups` - List available backups
- `validate_device_config` - Validate device configuration
- `check_config_syntax` - Check configuration syntax

### Commit & Transaction Management
- `list_transactions` - List recent NSO transactions
- `check_locks` - Check active locks in NSO
- `list_rollback_points` - List available rollback points
- `rollback_router_configuration` - Rollback NSO configuration
- `find_rollback_by_description` - Find rollback by searching descriptions
- `commit_with_description` - Commit with descriptive tag
- `list_commit_queue` - List pending commits in queue
- `get_commit_status` - Get status of specific commit
- `commit_dry_run` - Dry-run commit to preview changes
- `commit_async` - Commit changes asynchronously

### Operational Data & Monitoring
- `explore_live_status` - Explore available live-status paths
- `get_interface_operational_status` - Get interface operational status
- `get_bgp_neighbor_status` - Get BGP neighbor status
- `get_ospf_neighbor_status` - Get OSPF neighbor adjacency status
- `get_interface_statistics` - Get interface statistics
- `get_routing_table` - Get routing table
- `get_route_details` - Get detailed route information
- `get_device_cpu_usage` - Get CPU utilization
- `get_device_memory_usage` - Get memory usage
- `get_device_alarms` - Get device alarms
- `get_device_performance_metrics` - Get device performance metrics

### Device Command Execution
- `execute_device_command` - Execute show/exec commands on device
- `execute_device_command_batch` - Execute command on multiple devices

### Bulk Operations
- `sync_all_devices` - Sync all devices (to/from NSO)
- `compare_all_devices` - Compare all devices against NSO config
- `get_all_devices_sync_status` - Get sync status for all devices
- `shutdown_all_interfaces` - Shutdown all interfaces

### Device Group Management
- `create_device_group` - Create device group
- `list_device_groups` - List all device groups

### Audit & Change Tracking
- `get_configuration_changes` - Get recent configuration changes
- `list_notifications` - List recent notifications

### Advanced Operations
- `get_snmp_config` - Get SNMP configuration
- `get_access_lists` - List all access lists

### Package Management
- `reload_nso_packages` - Reload all NSO packages
- `redeploy_nso_package` - Redeploy a specific NSO package

### Utility
- `nso_health_check` - Check NSO health and automatically fix common issues
- `clear_stuck_sessions` - Clear stuck NSO sessions that are holding locks
- `echo_text` - Echo back text (debug/health check)

---

## 🚀 Common Workflows

### Deploy OSPF Network
1. `configure_router_interface()` - Configure interface IPs
2. `setup_ospf_base_service()` - Deploy OSPF base for each router
3. `setup_ospf_neighbor_service()` - Configure OSPF neighbors
4. `get_ospf_neighbor_status()` - Verify adjacencies
5. `commit_with_description()` - Commit changes

### Deploy iBGP Network
1. `configure_router_interface()` - Configure Loopback0 IPs
2. `setup_ibgp_service()` - Deploy iBGP between routers
3. `get_bgp_neighbor_status()` - Verify BGP peers
4. `get_routing_table()` - Verify routes
5. `commit_with_description()` - Commit changes

### Troubleshoot Network Issue
1. `nso_health_check()` - Check NSO health
2. `get_device_connection_status()` - Check device connectivity
3. `execute_device_command()` - Run show commands
4. `get_device_alarms()` - Check for alarms
5. `get_bgp_neighbor_status()` / `get_ospf_neighbor_status()` - Check protocol status
6. `compare_device_config()` - Compare NSO vs device config

### Rollback Configuration
1. `list_rollback_points()` - View available rollback points
2. `find_rollback_by_description()` - Find specific rollback
3. `rollback_router_configuration()` - Perform rollback
4. `sync_to_device()` - Push rollback to device

---

## 📚 Documentation

- **Complete Tool List**: `list_all_mcp_tools_20250101.md`
- **Implementation Details**: `PHASE1_2_3_TOOLS_IMPLEMENTATION_20250101.md`
- **NSO MCP Server Guide**: `docs/NSO_MCP_SERVER_GUIDE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`

---

**Note**: All tools are accessible via the MCP server and can be called by AI agents or MCP clients. The server handles NSO authentication, error handling, and logging automatically.

