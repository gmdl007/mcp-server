# NSO MCP Server - Complete Development Guide

## Overview

This project provides a **Model Context Protocol (MCP) server** that exposes Cisco NSO (Network Services Orchestrator) automation capabilities as tools that can be consumed by AI agents and other MCP clients. The server is built using **FastMCP** and integrates with **LlamaIndex** for natural language agent interaction.

---

## Table of Contents

1. [Architecture](#architecture)
2. [NSO/NCS Setup](#nsoncso-setup)
3. [Netsim Setup and Usage](#netsim-setup-and-usage)
4. [MCP Server Setup](#mcp-server-setup)
5. [Available Tools](#available-tools)
6. [NSO API Usage Patterns](#nso-api-usage-patterns)
7. [Adding New Tools](#adding-new-tools)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Architecture

### Components

```
┌─────────────────┐
│  MCP Client     │  (LlamaIndex Agent, Cursor, etc.)
│  (AI Agent)     │
└────────┬────────┘
         │
         │ MCP Protocol (JSON-RPC)
         │
┌────────▼─────────────────────────────────┐
│     FastMCP NSO Server                   │
│  ┌───────────────────────────────────┐  │
│  │  FastMCP Framework                 │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  NSO Tool Functions                │  │
│  │  - Device Management               │  │
│  │  - Interface Configuration         │  │
│  │  - OSPF/BGP Services               │  │
│  │  - Sync Operations                 │  │
│  │  - Live-Status Queries             │  │
│  └───────────────────────────────────┘  │
└────────┬─────────────────────────────────┘
         │
         │ NSO Python API (MAAPI/Maagic)
         │
┌────────▼─────────────────────────────────┐
│      Cisco NSO/NCS                       │
│  ┌───────────────────────────────────┐  │
│  │  Configuration Database (CDB)      │  │
│  │  - Device Configurations          │  │
│  │  - Service Instances              │  │
│  │  - Operational Data                │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  Device Management                │  │
│  │  - Netsim Devices                 │  │
│  │  - Real Hardware                  │  │
│  └───────────────────────────────────┘  │
└────────┬─────────────────────────────────┘
         │
         │ SSH/NETCONF
         │
┌────────▼─────────────────────────────────┐
│      Network Devices                     │
│  (Netsim or Physical)                   │
└──────────────────────────────────────────┘
```

### NSO Python API Usage

The server uses NSO's Python API (`maapi` and `maagic`) to interact with NSO:

- **MAAPI (Management API)**: Low-level API for transactions and sessions
- **Maagic**: High-level Pythonic API for accessing NSO data models

**Key Patterns**:
- `maapi.Maapi()` - Create MAAPI session
- `start_user_session()` - Authenticate with NSO
- `start_read_trans()` / `start_write_trans()` - Begin transaction
- `maagic.get_root(t)` - Get root object for data access
- `device.live_status` - Access operational data
- `device.config` - Access configuration data

---

## NSO/NCS Setup

### Prerequisites

1. **Cisco NSO 6.1.4+** installed
2. **Python 3.11+** with virtual environment
3. **Netsim** (for virtual devices) or physical hardware

### NSO Installation Path

The server expects NSO at:
```
/Users/gudeng/NCS-614
```

Update this path in `fastmcp_nso_server_auto_generated.py` if your installation is different:

```python
NSO_DIR = "/Users/gudeng/NCS-614"
```

### Environment Variables

Set these environment variables (or use `.env` file):

```bash
export NCS_DIR=/Users/gudeng/NCS-614
export DYLD_LIBRARY_PATH=$NCS_DIR/lib
export PYTHONPATH=$NCS_DIR/src/ncs/pyapi
```

### Start NSO

```bash
cd /Users/gudeng/NCS-614
source ncsrc
ncs
```

Verify NSO is running:
```bash
ps aux | grep ncs
ncs_cli -u admin -C
```

---

## Netsim Setup and Usage

Netsim (Network Simulator) provides virtual Cisco IOS XR devices for testing without physical hardware.

### Netsim Directory Structure

```
netsim/
└── xr9kv/
    ├── xr9kv0/          # Device xr9kv-1 (port 10022)
    ├── xr9kv1/          # Device xr9kv-2 (port 10023)
    └── xr9kv2/          # Device xr9kv-3 (port 10024)
```

### Starting Netsim Devices

```bash
cd /Users/gudeng/MCP_Server/netsim/xr9kv

# Start all devices
./xr9kv0/start.sh &
./xr9kv1/start.sh &
./xr9kv2/start.sh &

# Check status
ps aux | grep xr9kv
```

### Adding Devices to NSO

Devices must be added to NSO before they can be managed:

```bash
ncs_cli -u admin -C

# Add device
admin@ncs# config
admin@ncs(config)# devices device xr9kv-1
admin@ncs(config-device-xr9kv-1)# device-type cli ned-id cisco-iosxr-cli-7.52:cisco-iosxr-cli-7.52
admin@ncs(config-device-xr9kv-1)# state admin-state unlocked
admin@ncs(config-device-xr9kv-1)# authgroup default
admin@ncs(config-device-xr9kv-1)# ned-settings
admin@ncs(config-device-xr9kv-1-ned-settings)# ssh
admin@ncs(config-device-xr9kv-1-ned-settings-ssh)# host-key-check false
admin@ncs(config-device-xr9kv-1-ned-settings-ssh)# commit
admin@ncs(config-device-xr9kv-1-ned-settings-ssh)# top
admin@ncs(config)# commit

# Repeat for xr9kv-2 and xr9kv-3
```

### Connecting to Devices

```bash
ncs_cli -u admin -C

# Connect to device
admin@ncs# devices device xr9kv-1 connect

# Sync configuration from device
admin@ncs# devices device xr9kv-1 sync-from
```

### SSH Access to Netsim Devices

**Ports**:
- xr9kv-1 (xr9kv0): Port 10022
- xr9kv-2 (xr9kv1): Port 10023
- xr9kv-3 (xr9kv2): Port 10024

**Credentials**:
- Username: `admin`
- Password: `admin`

**Example**:
```bash
ssh -p 10022 admin@localhost
```

### Netsim Limitations

Netsim devices are virtual and have some limitations:
- Limited operational data in `live-status`
- Some show commands may not work
- Statistics may be empty or simulated
- Interface operational data may not be populated

These limitations are normal and the tools handle them gracefully. Real hardware will have full operational data.

---

## MCP Server Setup

### Installation

```bash
# Clone repository
cd /Users/gudeng/MCP_Server

# Create virtual environment
python3 -m venv mcp_venv
source mcp_venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install fastmcp ncs-utils python-dotenv
```

### Environment Configuration

Create `.env` file:
```bash
# Azure OpenAI (for LlamaIndex agent)
TOKEN_URL=https://your-token-url
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret

# NSO Configuration
NSO_DIR=/Users/gudeng/NCS-614
```

### Starting the Server

```bash
# Activate virtual environment
source mcp_venv/bin/activate

# Start FastMCP NSO Server
python src/mcp_server/working/llama_index_mcp/fastmcp_nso_server_auto_generated.py
```

The server will start on the default MCP port and be ready to accept connections.

### Running with Cursor

Add to Cursor MCP settings (`~/.cursor/mcp.json` or Cursor settings):

```json
{
  "mcpServers": {
    "nso-automation": {
      "command": "python",
      "args": [
        "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/fastmcp_nso_server_auto_generated.py"
      ],
      "env": {
        "NCS_DIR": "/Users/gudeng/NCS-614",
        "DYLD_LIBRARY_PATH": "/Users/gudeng/NCS-614/lib",
        "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
      }
    }
  }
}
```

---

## Available Tools

### Device Management Tools

#### `show_all_devices()`
List all devices managed by NSO.

**NSO API Usage**:
```python
m = maapi.Maapi()
m.start_user_session('admin', 'python')
t = m.start_read_trans()
root = maagic.get_root(t)
devices = root.devices.device
```

#### `get_device_capabilities(router_name=None)`
Get device capabilities and NED information.

**NSO API Usage**:
```python
device = root.devices.device[router_name]
capabilities = device.capability
device_type = device.device_type
platform = device.platform
```

#### `check_device_sync_status(router_name=None)`
Check if device configuration is in sync with NSO.

**NSO API Usage**:
```python
device = root.devices.device[router_name]
# Check sync via operational data
device.state.reached
device.config_commit_result
```

### Interface Configuration Tools

#### `get_router_interfaces_config(router_name)`
Get all interface configurations for a device.

**NSO API Usage**:
```python
device = root.devices.device[router_name]
interfaces = device.config.interface
# Access interface types: GigabitEthernet, Loopback, etc.
if_type = interfaces.GigabitEthernet
interface = if_type[interface_number]
```

#### `configure_router_interface(router_name, interface_name, ...)`
Configure interface settings (IP, description, shutdown).

**NSO API Usage**:
```python
t = m.start_write_trans()  # Write transaction
root = maagic.get_root(t)
device = root.devices.device[router_name]
interface = device.config.interface.GigabitEthernet[interface_number]
interface.ipv4.address.create()
t.apply()  # Apply changes
```

### OSPF Service Tools

#### `setup_ospf_base_service(router_name, router_id, area)`
Create OSPF base service instance.

**NSO API Usage**:
```python
root = maagic.get_root(t)
ospf_service = root.services.ospf.base[router_name]
ospf_service.router_id = router_id
ospf_service.area = area
t.apply()
```

#### `setup_ospf_neighbor_service(...)`
Configure OSPF neighbor relationship.

**NSO API Usage**:
```python
ospf_service = root.services.ospf.base[router_name]
neighbor = ospf_service.neighbor[neighbor_device].create()
neighbor.local_interface = local_interface
neighbor.local_ip = local_ip
```

### Sync Operations

#### `sync_from_device(router_name)`
Pull configuration from device to NSO.

**NSO API Usage**:
```python
device = root.devices.device[router_name]
sync_action = device.sync_from
result = sync_action()
```

#### `sync_to_device(router_name)`
Push configuration from NSO to device.

**NSO API Usage**:
```python
device = root.devices.device[router_name]
sync_action = device.sync_to
result = sync_action()
```

### Live-Status / Operational Data

#### `explore_live_status(router_name)`
Explore available live-status paths.

**NSO API Usage**:
```python
device = root.devices.device[router_name]
live_status = device.live_status
# Access paths: exec, if__interfaces, cisco_ios_xr_stats__*, etc.
```

#### Command Execution via `exec.any`

**NSO API Usage**:
```python
live_status = device.live_status
exec_any = live_status.exec.any
inp = exec_any.get_input()
inp.args = ['show version']
result = exec_any.request(inp)
output = result.result
```

---

## NSO API Usage Patterns

### Pattern 1: Read Operations

```python
m = maapi.Maapi()
m.start_user_session('admin', 'python')
t = m.start_read_trans()
root = maagic.get_root(t)

# Access data
devices = root.devices.device
device = devices['xr9kv-1']
config = device.config

m.end_user_session()
```

### Pattern 2: Write Operations

```python
m = maapi.Maapi()
m.start_user_session('admin', 'python')
t = m.start_write_trans()
root = maagic.get_root(t)

# Make changes
device = root.devices.device['xr9kv-1']
device.config.interface.GigabitEthernet['0/0/0/0'].description = "Test"

# Apply changes
t.apply()

m.end_user_session()
```

### Pattern 3: Using `single_write_trans` Context Manager

```python
with maapi.single_write_trans('admin', 'python') as t:
    root = maagic.get_root(t)
    # Make changes
    device = root.devices.device['xr9kv-1']
    # Changes auto-committed when exiting context
```

### Pattern 4: Accessing Operational Data

```python
t = m.start_read_trans()
root = maagic.get_root(t)
device = root.devices.device['xr9kv-1']

# Live-status operational data
live_status = device.live_status

# Execute command
exec_any = live_status.exec.any
inp = exec_any.get_input()
inp.args = ['show version']
result = exec_any.request(inp)
```

### Pattern 5: Device Actions

```python
device = root.devices.device['xr9kv-1']

# Actions are accessed via methods
sync_from = device.sync_from
ping = device.ping
connect = device.connect

# Invoke action
result = sync_from()
```

---

## Adding New Tools

### Step 1: Define Function

```python
def my_new_tool(router_name: str) -> str:
    """Description of what the tool does.
    
    Args:
        router_name: Name of the router device
        
    Returns:
        str: Result message
        
    Examples:
        my_new_tool('xr9kv-1')
    """
    try:
        logger.info(f"🔧 Executing my_new_tool for: {router_name}")
        
        # NSO API usage
        m = maapi.Maapi()
        m.start_user_session('admin', 'python')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        # Your logic here
        device = root.devices.device[router_name]
        # ... access device data ...
        
        m.end_user_session()
        return "Success message"
        
    except Exception as e:
        logger.exception(f"❌ Error: {e}")
        return f"Error: {e}"
```

### Step 2: Register with FastMCP

```python
# In the REGISTER TOOLS section
mcp.tool(my_new_tool)
```

### Step 3: Test

```bash
# Restart MCP server
python src/mcp_server/working/llama_index_mcp/fastmcp_nso_server_auto_generated.py

# Test via Cursor or MCP client
```

---

## Testing

### Manual Testing Scripts

Test scripts are in the project root:

```bash
# Test live-status exploration
python test_live_status.py

# Test live-status data retrieval
python test_live_status_data.py

# Test command execution
python test_exec_commands.py
```

### Jupyter Notebook Testing

```bash
# Start Jupyter notebook
./src/mcp_server/working/llama_index_mcp/start_jupyter_demo.sh
```

The notebook (`mcp_client_demo.ipynb`) demonstrates:
- Connecting to MCP server
- Using tools via LlamaIndex agent
- Natural language interaction

### Testing Individual Tools

```python
# In Python REPL
import sys
sys.path.insert(0, 'src/mcp_server/working/llama_index_mcp')
from fastmcp_nso_server_auto_generated import show_all_devices

result = show_all_devices()
print(result)
```

---

## Troubleshooting

### NSO Connection Issues

**Problem**: Cannot connect to NSO

**Solution**:
1. Verify NSO is running: `ps aux | grep ncs`
2. Check NSO_DIR path is correct
3. Verify Python path includes NSO API: `echo $PYTHONPATH`
4. Test NSO CLI: `ncs_cli -u admin -C`

### Device Not Found

**Problem**: Tool reports device not found

**Solution**:
1. Verify device exists: `show_all_devices()`
2. Check device name matches exactly (case-sensitive)
3. Ensure device is added to NSO configuration

### Live-Status Empty

**Problem**: Live-status paths exist but are empty

**Solution**:
- This is normal for netsim devices
- Real hardware will have populated data
- Use `exec.any` for command execution instead

### Transaction Lock Errors

**Problem**: "Device is locked" errors

**Solution**:
```bash
# Check locks
ncs_cli -u admin -C
admin@ncs# show locks

# Clear locks if needed (as admin)
admin@ncs# clear locks
```

---

## Best Practices

1. **Always use try/except**: Handle NSO API errors gracefully
2. **Close sessions**: Always call `m.end_user_session()` or use context managers
3. **Use appropriate transaction types**: Read for queries, write for changes
4. **Commit explicitly**: Use `t.apply()` for write transactions
5. **Log operations**: Use logger for debugging
6. **Handle netsim limitations**: Gracefully handle missing operational data
7. **Document tool parameters**: Clear docstrings help AI agents use tools correctly

---

## Extending the Server

### Adding Service Packages

When adding support for new service packages:

1. Explore service YANG model in NSO
2. Create service instance management functions
3. Handle service lifecycle (create, update, delete)
4. Register tools with FastMCP

### Adding Protocol Support

For new protocols (e.g., BGP, ISIS):

1. Access via `device.config.router.bgp` or similar
2. Create protocol-specific tools
3. Support both configuration and operational data
4. Test with netsim first, then real hardware

---

## Resources

- **NSO Documentation**: `/Users/gudeng/NCS-614/doc/html/`
- **NSO Python API**: `/Users/gudeng/NCS-614/doc/html/ncspyapi/ncspyapi.html`
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp
- **MCP Specification**: https://modelcontextprotocol.io

---

*Last Updated: 2025-01-21*
*NSO Version: 6.1.4*
*Python: 3.11+*

