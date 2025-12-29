# Available MCP NSO Automation Tools

**Total Tools: ~86 tools** (Updated: 2025-01-01)

## Device Management
- `show_all_devices` - List all router devices
- `get_router_interfaces_config` - Get complete interface configuration tree
- `configure_router_interface` - Configure interfaces (IP, description, shutdown)
- `get_interface_operational_status` - Get interface operational status
- `connect_device` - Connect NSO to device
- `fetch_ssh_host_keys` - Fetch SSH host keys from device (required before sync)
- `disconnect_device` - Disconnect NSO from device
- `ping_device` - Ping device to check connectivity
- `get_device_connection_status` - Get device connection status

## OSPF Service Tools
- `get_ospf_service_config` - Get OSPF service configuration
- `setup_ospf_base_service` - Setup OSPF base service
- `setup_ospf_neighbor_service` - Setup OSPF neighbor service
- `remove_ospf_neighbor_service` - Remove OSPF neighbor service
- `delete_ospf_service` - Delete OSPF service instance
- `normalize_ospf_service_interfaces` - Normalize OSPF interface formats

## BGP Service Tools
- `get_BGP_GRP__BGP_GRP_config` - Get BGP Group service configuration
- `create_BGP_GRP__BGP_GRP_service` - Create BGP Group service
- `delete_BGP_GRP__BGP_GRP_service` - Delete BGP Group service
- `get_ibgp_service_config` - Get iBGP service configuration
- `setup_ibgp_service` - Setup iBGP service between two routers
- `delete_ibgp_service` - Delete iBGP service

## Device Information & Capabilities
- `get_device_capabilities` - Get device capabilities
- `check_yang_modules_compatibility` - Check YANG module compatibility
- `list_device_modules` - List YANG modules supported by device
- `get_device_ned_info` - Get NED (Network Element Driver) information
- `get_device_version` - Get device version information

## Service Management
- `list_available_services` - List all available service models
- `get_service_model_info` - Get detailed service model information
- `list_service_instances` - List instances of a specific service
- `get_services_for_device` - List all services on device
- `get_service_status` - Get service operational status
- `count_services_by_type` - Count services by type
- `redeploy_service` - Redeploy specific service
- `redeploy_all_services_for_device` - Redeploy all services for device

## Sync & Configuration Management
- `check_device_sync_status` - Check device sync status
- `show_sync_differences` - Show differences between NSO and device config
- `compare_device_config` - Compare NSO config with device config
- `sync_from_device` - Sync configuration from device to NSO
- `sync_to_device` - Sync configuration from NSO to device
- `sync_all_devices` - Sync all devices (to/from NSO)
- `compare_all_devices` - Compare all devices against NSO config
- `get_all_devices_sync_status` - Get sync status for all devices

## Configuration Operations
- `get_router_config_section` - Get specific config section (BGP, OSPF, etc.)
- `delete_config_section` - Delete config section
- `list_config_sections` - List available config sections
- `backup_device_config` - Backup device configuration
- `list_device_backups` - List available backups
- `validate_device_config` - Validate device configuration
- `check_config_syntax` - Check configuration syntax

## Commit & Transaction Management
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

## Operational Data & Monitoring
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

## Device Command Execution
- `execute_device_command` - Execute show/exec commands on device
- `execute_device_command_batch` - Execute command on multiple devices

## Bulk Operations
- `sync_all_devices` - Sync all devices (to/from NSO)
- `compare_all_devices` - Compare all devices against NSO config
- `get_all_devices_sync_status` - Get sync status for all devices
- `shutdown_all_interfaces` - Shutdown all interfaces

## Device Group Management
- `create_device_group` - Create device group
- `list_device_groups` - List all device groups

## Audit & Change Tracking
- `get_configuration_changes` - Get recent configuration changes
- `list_notifications` - List recent notifications

## Advanced Operations
- `get_snmp_config` - Get SNMP configuration
- `get_access_lists` - List all access lists

## Package Management
- `reload_nso_packages` - Reload all NSO packages
- `redeploy_nso_package` - Redeploy a specific NSO package

## Utility
- `nso_health_check` - Check NSO health and automatically fix common issues
- `clear_stuck_sessions` - Clear stuck NSO sessions that are holding locks
- `echo_text` - Echo back text (debug/health check)

## Tool Categories Summary

- **Device Management**: 8 tools
- **OSPF Services**: 6 tools
- **BGP Services**: 6 tools
- **Device Information**: 5 tools
- **Service Management**: 8 tools
- **Sync & Configuration**: 8 tools
- **Configuration Operations**: 6 tools
- **Commit & Transactions**: 10 tools
- **Operational Data**: 11 tools
- **Command Execution**: 2 tools
- **Bulk Operations**: 4 tools
- **Device Groups**: 2 tools
- **Audit & Tracking**: 2 tools
- **Advanced Operations**: 2 tools
- **Package Management**: 2 tools
- **Utility**: 3 tools

**Total: ~86 tools**
