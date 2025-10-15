# NSO Network Manager

A comprehensive Python script for managing Cisco NSO network devices, extracted from the `NSO_python_multi-agend.ipynb` notebook.

## Features

### 🔧 Core Functionality
- **Device Discovery**: Find and list all available network devices
- **Command Execution**: Execute commands on individual or all devices
- **Configuration Management**: Configure interfaces, subinterfaces, and other settings
- **Monitoring**: Check device health, alarms, CPU, memory, and logs
- **Protocol Support**: BGP, OSPF, ISIS, MPLS, LLDP monitoring
- **Network Operations**: Ping, traceroute, and connectivity testing

### 📊 Device Operations
- Show device version, clock, and status
- Display interface information and routing tables
- Monitor protocol neighbors and summaries
- Check system resources (CPU, memory)
- View alarms and logs

### ⚙️ Configuration Operations
- Configure subinterfaces with IP addresses
- Rollback configurations
- Apply bulk configurations

## Files

- **`nso_network_manager.py`**: Main script with all NSO functionality
- **`nso_examples.py`**: Usage examples and demonstrations
- **`start_nso_env.sh`**: Environment setup script

## Prerequisites

1. **NSO Installation**: Cisco NSO must be installed and running
2. **Python Environment**: Python 3.x with NSO Python API
3. **Environment Setup**: NSO environment must be sourced

### Setup NSO Environment

```bash
# Source NSO environment
export DYLD_LIBRARY_PATH=""
export PYTHONPATH=""
source /Users/gudeng/NCS-614/ncsrc

# Or use the provided script
./start_nso_env.sh
```

## Usage

### Basic Usage

```python
from nso_network_manager import NetworkManager

# Initialize the manager
nm = NetworkManager()

# Show all devices
devices = nm.show_all_devices()
print(f"Available devices: {devices}")

# Execute command on specific device
result = nm.get_router_version("xr9kv-1")
print(result)

# Execute command on all devices
results = nm.iterate_devices_and_cmd("show version")
```

### Running Examples

```bash
# Run the main script
python nso_network_manager.py

# Run usage examples
python nso_examples.py
```

### Command Line Usage

```bash
# Make scripts executable
chmod +x nso_network_manager.py
chmod +x nso_examples.py

# Run directly
./nso_network_manager.py
./nso_examples.py
```

## Class Structure

### NetworkManager
Main class that combines all functionality:
- Device discovery and management
- Command execution
- Configuration operations
- Monitoring and diagnostics

### Key Methods

#### Device Management
- `show_all_devices()`: List all available devices
- `execute_command_on_router(device, command)`: Execute command on specific device
- `iterate_devices_and_cmd(command)`: Execute command on all devices

#### Router Operations
- `get_router_version(device)`: Get device version
- `get_router_clock(device)`: Get device time
- `show_router_interfaces(device)`: Show interface status
- `get_router_ip_routes(device, prefix)`: Show routing information

#### Monitoring
- `check_alarm(device)`: Check device alarms
- `check_cpu(device)`: Check CPU usage
- `check_memory(device)`: Check memory usage
- `get_router_logs(device, match_string)`: Get device logs

#### Configuration
- `configure_subinterface(device, subinterface_id, ip, mask)`: Configure subinterface
- `roll_back(steps)`: Rollback configuration

## Example Operations

### 1. Device Discovery
```python
nm = NetworkManager()
devices = nm.show_all_devices()
# Output: ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']
```

### 2. Bulk Command Execution
```python
results = nm.iterate_devices_and_cmd("show version")
# Executes 'show version' on all devices
```

### 3. Interface Configuration
```python
success = nm.configure_subinterface(
    device_name="xr9kv-1",
    subinterface_id="0/0/0/0.100",
    ip_address="10.1.1.1",
    subnet_mask="255.255.255.0"
)
```

### 4. Comprehensive Monitoring
```python
# Run full health check on a device
results = nm.run_comprehensive_check("xr9kv-1")
# Returns version, clock, interfaces, alarms, CPU, memory, protocols
```

### 5. Device Status
```python
status = nm.get_device_status("xr9kv-1")
# Returns: oper_state, address, port, authgroup, etc.
```

## Error Handling

The script includes comprehensive error handling:
- Connection failures
- Device not found errors
- Command execution errors
- Configuration errors

All errors are logged with appropriate messages.

## Logging

The script uses Python's logging module with configurable levels:
- INFO: General information and successful operations
- ERROR: Error conditions and failures
- DEBUG: Detailed debugging information (when enabled)

## Integration with Jupyter Notebooks

This script can be easily integrated into Jupyter notebooks:

```python
# In a Jupyter notebook cell
from nso_network_manager import NetworkManager

nm = NetworkManager()
devices = nm.show_all_devices()
print(f"Found {len(devices)} devices")
```

## Troubleshooting

### Common Issues

1. **NSO Not Running**: Ensure NSO daemon is started
   ```bash
   ncs --status
   ```

2. **Environment Not Sourced**: Source NSO environment
   ```bash
   source /Users/gudeng/NCS-614/ncsrc
   ```

3. **Device Connection Issues**: Check device configuration in NSO
   ```bash
   ncs_cli -u admin -C
   show devices device
   ```

4. **Authentication Errors**: Verify authgroup configuration
   ```bash
   show devices authgroups
   ```

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

This script was extracted from the `NSO_python_multi-agend.ipynb` notebook. To add new functionality:

1. Add new methods to the appropriate class
2. Include proper error handling
3. Add logging statements
4. Update this README with examples

## License

This script is provided as-is for educational and development purposes.

