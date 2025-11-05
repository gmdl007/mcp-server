# Available MCP NSO Automation Tools

## Device Management
- `show_all_devices` - List all router devices
- `get_router_interfaces_config` - Get complete interface configuration tree
- `configure_router_interface` - Configure interfaces (IP, description, shutdown)
- `get_interface_operational_status` - Get interface operational status

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

## Sync & Configuration Management
- `check_device_sync_status` - Check device sync status
- `show_sync_differences` - Show differences between NSO and device config
- `compare_device_config` - Compare NSO config with device config
- `sync_from_device` - Sync configuration from device to NSO
- `sync_to_device` - Sync configuration from NSO to device

## Transaction & System Management
- `list_transactions` - List recent NSO transactions
- `check_locks` - Check active locks in NSO
- `list_rollback_points` - List available rollback points
- `rollback_router_configuration` - Rollback NSO configuration
- `reload_nso_packages` - Reload all NSO packages
- `redeploy_nso_package` - Redeploy a specific NSO package

## Operational Data
- `explore_live_status` - Explore available live-status paths
- `get_interface_operational_status` - Get interface operational status

## Utility
- `echo_text` - Echo back text (debug/health check)

