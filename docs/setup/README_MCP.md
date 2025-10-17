# NSO MCP Server with LlamaIndex Integration

A Model Context Protocol (MCP) server that exposes NSO network automation capabilities through LlamaIndex function tools.

## 🚀 Features

- **MCP Protocol**: Standardized Model Context Protocol server
- **NSO Integration**: Full NSO device management and automation
- **LlamaIndex Tools**: 17 NSO function tools available to AI clients
- **Async Support**: Fully asynchronous implementation
- **Error Handling**: Comprehensive error handling and logging

## 📋 Prerequisites

1. **NSO Installation**: Cisco NSO must be installed and running
2. **Python Environment**: Python 3.11+ with virtual environment
3. **MCP Dependencies**: Install MCP server requirements

## 🛠️ Installation

### 1. Install MCP Dependencies

```bash
# Create virtual environment
python3 -m venv mcp_venv
source mcp_venv/bin/activate

# Install MCP requirements
pip install -r mcp_requirements.txt
```

### 2. Configure NSO Environment

Update the NSO configuration in `nso_mcp_server.py`:

```python
# NSO Configuration
NSO_DIR = "/Users/gudeng/NCS-614"  # Update this path
NSO_USERNAME = "admin"
NSO_PASSWORD = "admin"  # Update this password
```

### 3. Start NSO

```bash
# Start NSO daemon
cd /Users/gudeng/NCS-614
source ncsrc
ncs
```

## 🚀 Usage

### 1. Start the MCP Server

```bash
# Activate virtual environment
source mcp_venv/bin/activate

# Start the MCP server
python nso_mcp_server.py
```

### 2. Connect MCP Client

The server exposes the following tools:

#### **📱 Device Discovery & Management**
- `show_all_devices` - Find all available routers
- `iterate` - Execute command on all devices

#### **📊 Device Information & Status**
- `get_router_version` - Get router version
- `get_router_clock` - Get router time
- `show_router_interfaces` - Show interface status

#### **🌐 Network Routing & Protocols**
- `get_router_bgp_summary` - BGP summary
- `get_router_isis_neighbors` - ISIS neighbors
- `get_router_ospf_neigh` - OSPF neighbors

#### **💻 System Resources & Performance**
- `check_cpu` - CPU utilization
- `check_memory` - Memory usage

#### **🔍 Network Diagnostics & Troubleshooting**
- `ping_router` - Ping from router
- `traceroute_router` - Traceroute from router
- `lldp_nei` - LLDP neighbors
- `check_alarm` - Router alarms

## 🔧 MCP Client Integration

### Example MCP Client Usage

```python
import asyncio
from mcp.client import Client

async def main():
    # Connect to MCP server
    client = Client("nso-mcp-server")
    await client.connect()
    
    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {[tool.name for tool in tools.tools]}")
    
    # Call a tool
    result = await client.call_tool(
        name="show_all_devices",
        arguments={}
    )
    print(f"Devices: {result.content[0].text}")
    
    # Get router version
    result = await client.call_tool(
        name="get_router_version",
        arguments={"router_name": "xr9kv-1"}
    )
    print(f"Version: {result.content[0].text}")

asyncio.run(main())
```

### Claude Desktop Integration

Add to Claude Desktop configuration:

```json
{
  "mcpServers": {
    "nso-network-automation": {
      "command": "python",
      "args": ["/Users/gudeng/MCP_Server/nso_mcp_server.py"],
      "env": {
        "NCS_DIR": "/Users/gudeng/NCS-614",
        "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
      }
    }
  }
}
```

## 🎯 Example Queries

Once connected, you can ask Claude or other MCP clients:

- "Show me all devices in the network"
- "What's the version of router xr9kv-1?"
- "Check CPU usage on all routers"
- "Show BGP neighbors on xr9kv-2"
- "Ping 8.8.8.8 from xr9kv-1"
- "What interfaces are up on xr9kv-3?"

## 🔍 Troubleshooting

### Common Issues

1. **NSO Connection Failed**
   - Ensure NSO is running: `ncs --status`
   - Check NSO_DIR path is correct
   - Verify NSO Python API is accessible

2. **MCP Server Not Starting**
   - Check virtual environment is activated
   - Verify all dependencies are installed
   - Check NSO environment variables

3. **Tool Execution Errors**
   - Verify device names exist in NSO
   - Check device operational state
   - Ensure proper NSO permissions

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │◄──►│   MCP Server     │◄──►│   NSO System    │
│  (Claude, etc.) │    │  (nso_mcp_server)│    │  (NCS + Devices)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  LlamaIndex      │
                       │  Function Tools  │
                       └──────────────────┘
```

## 🔒 Security Considerations

1. **NSO Credentials**: Use environment variables for sensitive data
2. **Network Access**: Configure firewall rules appropriately
3. **MCP Security**: Use secure MCP client connections
4. **Device Access**: Ensure proper NSO device permissions

## 📈 Performance

- **Async Operations**: All operations are asynchronous
- **Connection Pooling**: Efficient NSO connection management
- **Error Recovery**: Automatic retry and error handling
- **Logging**: Comprehensive logging for monitoring

## 🔄 Updates and Maintenance

### Updating Dependencies

```bash
pip install --upgrade -r mcp_requirements.txt
```

### Adding New Tools

1. Add new method to `NSOMCPTools` class
2. Update `handle_list_tools()` with new tool definition
3. Add tool handler in `handle_call_tool()`

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review MCP server logs
3. Verify NSO and network connectivity
4. Check MCP client documentation

## 📄 License

This MCP server is provided as-is for educational and development purposes.

---

**Happy Network Automation with MCP! 🚀**
