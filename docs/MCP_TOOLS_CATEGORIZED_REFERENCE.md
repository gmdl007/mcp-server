# MCP Tools for NCS - Categorized Reference

**Generated:** 2025-11-18  
**Purpose:** Complete categorized reference of all available MCP tools for Cisco NSO/NCS automation

---

## Table of Contents

1. [Device Management](#1-device-management)
2. [Interface Configuration](#2-interface-configuration)
3. [Service Management](#3-service-management)
4. [Routing & Protocols](#4-routing--protocols)
5. [Configuration Management](#5-configuration-management)
6. [Sync & Commit Operations](#6-sync--commit-operations)
7. [Rollback & Recovery](#7-rollback--recovery)
8. [Monitoring & Health](#8-monitoring--health)
9. [Device Capabilities & Information](#9-device-capabilities--information)
10. [Transaction & Lock Management](#10-transaction--lock-management)
11. [Bulk Operations](#11-bulk-operations)
12. [Troubleshooting & Diagnostics](#12-troubleshooting--diagnostics)

---

## 1. Device Management

### Device Discovery & Listing
- **`show_all_devices()`**
  - Lists all devices managed by NSO
  - Returns: Comma-separated list of device names
  - Example: `show_all_devices()`

### Device Connection
- **`connect_device(router_name)`**
  - Establishes connection between NSO and device
  - Required before most operations
  - Example: `connect_device('node-1')`

- **`disconnect_device(router_name)`**
  - Disconnects NSO from device
  - Example: `disconnect_device('node-1')`

- **`ping_device(router_name)`**
  - Pings device to check connectivity
  - Verifies NSO can reach device
  - Example: `ping_device('node-1')`

- **`fetch_ssh_host_keys(router_name)`**
  - Fetches SSH host keys from device
  - Critical step when adding new devices
  - Must be done before sync-from operations
  - Example: `fetch_ssh_host_keys('node-1')`

---

## 2. Interface Configuration

### Interface Information
- **`get_router_interfaces_config(router_name)`**
  - Returns complete interface configuration tree
  - Shows IP addresses, descriptions, and status
  - Example: `get_router_interfaces_config('node-1')`

### Interface Configuration
- **`configure_router_interface(router_name, interface_name, ip_address, description, shutdown, delete_ip)`**
  - Comprehensive interface configuration
  - Supports: IP address management, descriptions, shutdown status
  - Can add/delete IPv4 addresses
  - Example: `configure_router_interface('node-1', 'GigabitEthernet/0/0/0/0', ip_address='192.168.1.1/24', description='Uplink', shutdown=False)`

### Interface Cleanup
- **`delete_router_subinterfaces(router_name, confirm)`**
  - Deletes all sub-interfaces (interfaces with dots in name)
  - Preserves physical interfaces and Loopbacks
  - Requires confirm=True for safety
  - Example: `delete_router_subinterfaces('node-1', confirm=True)`

---

## 3. Service Management

### Service Discovery
- **`list_available_services()`**
  - Lists all available service models/packages in NSO
  - Shows service packages deployed
  - Example: `list_available_services()`

- **`get_service_model_info(service_name)`**
  - Get detailed information about a specific service model
  - Shows service structure, parameters, instances
  - Example: `get_service_model_info('ospf')`

- **`list_service_instances(service_name)`**
  - Lists all instances of a specific service
  - Shows configured service instances
  - Example: `list_service_instances('ospf')`

- **`get_services_for_device(router_name)`**
  - Lists all services deployed on a device
  - Shows service instances using the device
  - Example: `get_services_for_device('node-1')`

- **`get_service_status(service_type, service_name)`**
  - Get operational status/plan for a service instance
  - Example: `get_service_status('ospf', 'node-1')`

### OSPF Services
- **`setup_ospf_base_service(router_name, router_id, area)`**
  - Creates/updates OSPF base service instance
  - Example: `setup_ospf_base_service('node-1', '1.1.1.1', '0')`

- **`setup_ospf_neighbor_service(router_name, router_id, neighbor_device, local_interface, local_ip, remote_ip, area, remote_interface)`**
  - Creates OSPF neighbor relationship
  - Example: `setup_ospf_neighbor_service('node-1', '1.1.1.1', 'node-2', 'GigabitEthernet/0/0/0/0', '192.168.1.1', '192.168.1.2', '0')`

- **`get_ospf_service_config(router_name)`**
  - Get NSO service-level OSPF configuration
  - Shows service instances and settings
  - Example: `get_ospf_service_config('node-1')`

- **`remove_ospf_neighbor_service(router_name, neighbor_device, confirm)`**
  - Removes OSPF neighbor relationship
  - Requires confirm=True
  - Example: `remove_ospf_neighbor_service('node-1', 'node-2', confirm=True)`

- **`delete_ospf_service(router_name, confirm)`**
  - Deletes OSPF service instance
  - Requires confirm=True
  - Example: `delete_ospf_service('node-1', confirm=True)`

- **`delete_ospf_link_service(link_name, confirm)`**
  - Deletes OSPF link service instance
  - Link format: "router1::router2"
  - Example: `delete_ospf_link_service('node-1::node-2', confirm=True)`

- **`delete_all_ospf_links_service(confirm)`**
  - Deletes all OSPF link service instances
  - Bulk cleanup operation
  - Example: `delete_all_ospf_links_service(confirm=True)`

### iBGP Services
- **`setup_ibgp_service(service_name, as_number, router1, router1_lo0_ip, router1_router_id, router2, router2_lo0_ip, router2_router_id)`**
  - Creates iBGP service between two routers using Loopback0
  - Example: `setup_ibgp_service('peer1-2', 65000, 'node-1', '1.1.1.1', '1.1.1.1', 'node-2', '1.1.1.2', '1.1.1.2')`

- **`get_ibgp_service_config(service_name)`**
  - Get iBGP service configuration
  - Example: `get_ibgp_service_config('peer1-2')`

- **`delete_ibgp_service(service_name, confirm)`**
  - Deletes iBGP service instance
  - Requires confirm=True
  - Example: `delete_ibgp_service('peer1-2', confirm=True)`

### BGP_GRP Services
- **`create_BGP_GRP__BGP_GRP_service(router_name)`**
  - Creates BGP_GRP__BGP_GRP service instance
  - Example: `create_BGP_GRP__BGP_GRP_service('node-1')`

- **`get_BGP_GRP__BGP_GRP_config(router_name)`**
  - Get BGP_GRP__BGP_GRP service configuration
  - Example: `get_BGP_GRP__BGP_GRP_config('node-1')`

- **`delete_BGP_GRP__BGP_GRP_service(router_name, confirm)`**
  - Deletes BGP_GRP__BGP_GRP service instance
  - Requires confirm=True
  - Example: `delete_BGP_GRP__BGP_GRP_service('node-1', confirm=True)`

### Service Redeployment
- **`redeploy_service(service_type, service_name)`**
  - Triggers reactive redeploy of a service instance
  - Example: `redeploy_service('ospf', 'node-1')`

- **`redeploy_all_services_for_device(router_name)`**
  - Finds all services using a device and redeploys them
  - Example: `redeploy_all_services_for_device('node-1')`

### Package Management
- **`reload_nso_packages(force)`**
  - Reloads all NSO packages
  - Example: `reload_nso_packages(force=False)`

- **`redeploy_nso_package(package_name)`**
  - Redeploys a specific NSO package
  - Example: `redeploy_nso_package('ospf')`

---

## 4. Routing & Protocols

### Routing Tables
- **`get_routing_table(router_name, protocol, prefix)`**
  - Retrieves routing table, optionally filtered
  - Protocol options: 'bgp', 'ospf', 'isis', 'static'
  - Example: `get_routing_table('node-1', protocol='isis')`
  - Example: `get_routing_table('node-1', prefix='10.0.0.0/8')`

- **`get_route_details(router_name, prefix)`**
  - Get detailed route information for specific prefix
  - Example: `get_route_details('node-1', '198.19.1.1/32')`

### BGP Operations
- **`get_bgp_neighbor_status(router_name)`**
  - Retrieves BGP neighbor status using show commands
  - Shows neighbor state, uptime, message counts
  - Example: `get_bgp_neighbor_status('node-1')`

### OSPF/IS-IS Operations
- **`get_ospf_neighbor_status(router_name)`**
  - Retrieves OSPF/IS-IS neighbor adjacency status
  - Works for both OSPF and IS-IS
  - Example: `get_ospf_neighbor_status('node-1')`

---

## 5. Configuration Management

### Configuration Retrieval
- **`get_router_config_section(router_name, section)`**
  - Gets specific configuration section (bgp, ospf, isis, system, etc.)
  - Example: `get_router_config_section('node-1', 'bgp')`
  - Example: `get_router_config_section('node-1', 'ospf')`

- **`list_config_sections(router_name)`**
  - Lists available configuration sections on device
  - Example: `list_config_sections('node-1')`

### Configuration Deletion
- **`delete_config_section(router_name, section, confirm)`**
  - Removes entire configuration section
  - Requires confirm=True for safety
  - Example: `delete_config_section('node-1', 'bgp', confirm=True)`

### Configuration Validation
- **`check_config_syntax(router_name)`**
  - Checks configuration syntax errors
  - Example: `check_config_syntax('node-1')`

---

## 6. Sync & Commit Operations

### Device Synchronization
- **`sync_from_device(router_name)`**
  - Pulls running configuration from device to NSO CDB
  - Use when device has been configured directly
  - Example: `sync_from_device('node-1')`

- **`sync_to_device(router_name)`**
  - Pushes NSO CDB configuration to device
  - Use when NSO has config that needs to be applied
  - Example: `sync_to_device('node-1')`

- **`check_device_sync_status(router_name)`**
  - Checks synchronization status between NSO CDB and device
  - Shows IN-SYNC or OUT-OF-SYNC status
  - Example: `check_device_sync_status('node-1')`

- **`compare_device_config(router_name)`**
  - Compares NSO configuration with device configuration
  - Shows unified diff format
  - Example: `compare_device_config('node-1')`

### Commit Operations
- **`commit_with_description(description)`**
  - Commits pending changes with descriptive tag
  - Description stored with commit for rollback identification
  - Example: `commit_with_description('Configured Loopback0 interfaces')`

- **`commit_dry_run(description)`**
  - Preview changes without applying them
  - Shows what would be committed
  - Example: `commit_dry_run('Preview OSPF configuration changes')`

- **`commit_async(description)`**
  - Commits changes asynchronously to queue
  - Example: `commit_async('Deploy OSPF configuration')`

### Commit Queue Management
- **`list_commit_queue(limit)`**
  - Lists pending commits in commit queue
  - Shows status, IDs, and other information
  - Example: `list_commit_queue(limit=20)`

- **`get_commit_status(commit_id)`**
  - Gets status of specific commit in queue
  - Example: `get_commit_status('12345')`

---

## 7. Rollback & Recovery

### Rollback Operations
- **`list_rollback_points(limit)`**
  - Lists available rollback points with descriptions
  - Shows rollback IDs and commit comments
  - Example: `list_rollback_points(limit=50)`

- **`find_rollback_by_description(search_term, limit)`**
  - Searches rollback descriptions to find rollback ID
  - Eliminates trial-and-error when rolling back
  - Example: `find_rollback_by_description('OSPF')`

- **`rollback_router_configuration(rollback_id, description)`**
  - Rolls back NSO configuration to previous state
  - rollback_id=0: most recent commit
  - Affects entire NSO configuration (global operation)
  - Example: `rollback_router_configuration(0)`
  - Example: `rollback_router_configuration(1, description='Rollback to before OSPF config')`

### Backup Operations
- **`backup_device_config(router_name, backup_name)`**
  - Creates backup of device configuration
  - Uses NSO rollback or file save
  - Example: `backup_device_config('node-1', 'backup_before_ospf_change')`

- **`list_device_backups(router_name)`**
  - Lists available backups for a device
  - Example: `list_device_backups('node-1')`

---

## 8. Monitoring & Health

### Device Health
- **`nso_health_check(auto_fix)`**
  - Comprehensive health check on NSO
  - Detects: NSO responsiveness, device locks, stuck sessions, hung processes
  - Can automatically fix issues when auto_fix=True
  - Example: `nso_health_check(auto_fix=True)`

- **`get_device_cpu_usage(router_name)`**
  - Gets CPU utilization for device
  - Example: `get_device_cpu_usage('node-1')`

- **`get_device_memory_usage(router_name)`**
  - Gets memory usage for device
  - Example: `get_device_memory_usage('node-1')`

- **`get_device_performance_metrics(router_name, metric_type)`**
  - Gets device performance metrics
  - Metric types: 'cpu', 'memory', 'interface'
  - Example: `get_device_performance_metrics('node-1', 'cpu')`

### Alarms & Notifications
- **`get_device_alarms(router_name, severity)`**
  - Gets device alarms
  - Optional severity filter: 'critical', 'major', 'minor'
  - Example: `get_device_alarms('node-1', severity='critical')`

- **`list_notifications(router_name, limit)`**
  - Lists recent notifications
  - Optional device filter
  - Example: `list_notifications('node-1', limit=50)`

### Configuration Changes
- **`get_configuration_changes(router_name, hours)`**
  - Gets recent configuration changes for device
  - Default: 24 hours lookback
  - Example: `get_configuration_changes('node-1', hours=24)`

---

## 9. Device Capabilities & Information

### Device Information
- **`get_device_version(router_name)`**
  - Gets device version information
  - Uses platform data and live-status
  - Example: `get_device_version('node-1')`

- **`get_device_capabilities(router_name)`**
  - Gets device capabilities and supported features
  - Shows device type, NED info, supported protocols
  - Example: `get_device_capabilities('node-1')`

- **`get_device_ned_info(router_name)`**
  - Gets NED (Network Element Driver) information
  - Example: `get_device_ned_info('node-1')`

### YANG Modules
- **`list_device_modules(router_name)`**
  - Lists YANG modules supported by device
  - Example: `list_device_modules('node-1')`

- **`check_yang_modules_compatibility(router_name, verbose)`**
  - Checks YANG module compatibility between NSO and device
  - Example: `check_yang_modules_compatibility('node-1', verbose=True)`

### Additional Device Info
- **`get_snmp_config(router_name)`**
  - Gets SNMP configuration for device
  - Example: `get_snmp_config('node-1')`

- **`get_access_lists(router_name)`**
  - Lists all access lists on device
  - Example: `get_access_lists('node-1')`

---

## 10. Transaction & Lock Management

### Transactions
- **`list_transactions(limit)`**
  - Lists recent NSO transactions
  - Tracks configuration changes and commits
  - Example: `list_transactions(limit=20)`

### Lock Management
- **`check_locks(router_name)`**
  - Checks active locks in NSO
  - Shows which devices/paths are locked
  - Example: `check_locks('node-1')`

- **`clear_stuck_sessions(automatic)`**
  - Clears stuck NSO sessions holding locks
  - Identifies and terminates stuck sessions
  - Example: `clear_stuck_sessions(automatic=True)`

---

## 11. Bulk Operations

### Multi-Device Operations
- **`sync_all_devices(direction)`**
  - Syncs all devices (to or from NSO)
  - Direction: 'to' (push) or 'from' (pull)
  - Example: `sync_all_devices('to')`

- **`compare_all_devices()`**
  - Compares all devices against NSO configuration
  - Example: `compare_all_devices()`

- **`get_all_devices_sync_status()`**
  - Gets sync status for all devices
  - Example: `get_all_devices_sync_status()`

### Batch Command Execution
- **`execute_device_command_batch(router_names, command)`**
  - Executes command on multiple devices
  - Router names: comma-separated list
  - Example: `execute_device_command_batch('node-1,node-2,node-3', 'show version')`

### Device Groups
- **`create_device_group(group_name, device_names)`**
  - Creates custom device group for bulk operations
  - Device names: comma-separated list
  - Example: `create_device_group('core-routers', 'node-1,node-2,node-3')`

- **`list_device_groups()`**
  - Lists all device groups
  - Example: `list_device_groups()`

---

## 12. Troubleshooting & Diagnostics

### Command Execution
- **`execute_device_command(router_name, command)`**
  - Executes arbitrary show or exec command on device
  - Uses live-status for command execution
  - Example: `execute_device_command('node-1', 'show version')`
  - Example: `execute_device_command('node-1', 'show bgp vpnv4 unicast summary')`

### Interface Operations
- **`shutdown_all_interfaces(router_name, confirm)`**
  - Shuts down all interfaces on router
  - Requires confirm=True for safety
  - Example: `shutdown_all_interfaces('node-1', confirm=True)`

---

## Quick Reference by Use Case

### Initial Device Setup
1. `show_all_devices()` - List devices
2. `fetch_ssh_host_keys(router_name)` - Fetch SSH keys
3. `connect_device(router_name)` - Connect to device
4. `ping_device(router_name)` - Verify connectivity
5. `sync_from_device(router_name)` - Import existing config

### Service Deployment
1. `list_available_services()` - See available services
2. `setup_ospf_base_service(...)` - Create OSPF service
3. `setup_ospf_neighbor_service(...)` - Add neighbors
4. `commit_with_description(...)` - Commit changes
5. `sync_to_device(router_name)` - Push to device

### Troubleshooting
1. `check_device_sync_status(router_name)` - Check sync
2. `compare_device_config(router_name)` - See differences
3. `get_device_alarms(router_name)` - Check alarms
4. `execute_device_command(router_name, 'show logging')` - View logs
5. `nso_health_check(auto_fix=True)` - Health check

### Configuration Management
1. `get_router_config_section(router_name, section)` - View config
2. `configure_router_interface(...)` - Configure interface
3. `commit_dry_run(...)` - Preview changes
4. `commit_with_description(...)` - Commit
5. `list_rollback_points()` - View rollback options

### Monitoring
1. `get_bgp_neighbor_status(router_name)` - BGP status
2. `get_ospf_neighbor_status(router_name)` - OSPF/IS-IS status
3. `get_routing_table(router_name)` - Routing table
4. `get_device_cpu_usage(router_name)` - CPU usage
5. `get_device_alarms(router_name)` - Alarms

---

## Notes

- **Safety Parameters:** Many destructive operations require `confirm=True` to prevent accidental changes
- **Device Connection:** Most operations require device to be connected first via `connect_device()`
- **Sync Operations:** Use `sync-from` to pull device config to NSO, `sync-to` to push NSO config to device
- **Rollback:** Rollback affects entire NSO configuration, not just one device
- **Service vs Device Config:** Service-level config (e.g., `get_ospf_service_config`) shows NSO service abstraction, while device-level config (e.g., `get_router_config_section('ospf')`) shows actual device configuration

---

*Last Updated: 2025-11-18*  
*Total Tools: 100+*

