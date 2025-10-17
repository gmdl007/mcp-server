# Connecting to NSO HTTP Server from Cursor

## 🚀 **Server Status**
- **HTTP Server**: Running on `http://localhost:5607`
- **NSO Connection**: ✅ Connected to NCS 6.1.4
- **Devices Available**: 3 devices (xr9kv-1, xr9kv-2, xr9kv-3)
- **Tools Available**: 14 NSO function tools

## 🔗 **Connection Methods**

### **Method 1: Direct HTTP API Calls**

You can make direct HTTP requests to the server:

```bash
# Health check
curl http://localhost:5607/health

# List all tools
curl http://localhost:5607/tools

# Execute a tool
curl -X POST -H "Content-Type: application/json" \
  -d '{"arguments": {"router_name": "xr9kv-1"}}' \
  http://localhost:5607/tools/get_router_version
```

### **Method 2: MCP-Compatible Endpoints**

The server provides MCP-compatible endpoints:

```bash
# MCP tools list
curl http://localhost:5607/mcp/tools/list

# MCP tool execution
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "show_all_devices", "arguments": {}}' \
  http://localhost:5607/mcp/tools/call
```

### **Method 3: Python Client**

Create a Python client to connect:

```python
import requests
import json

class NSOClient:
    def __init__(self, base_url="http://localhost:5607"):
        self.base_url = base_url
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def list_tools(self):
        response = requests.get(f"{self.base_url}/tools")
        return response.json()
    
    def execute_tool(self, tool_name, arguments):
        response = requests.post(
            f"{self.base_url}/tools/{tool_name}",
            json={"arguments": arguments}
        )
        return response.json()

# Usage
client = NSOClient()
print(client.health_check())
print(client.list_tools())

# Execute a tool
result = client.execute_tool("show_all_devices", {})
print(result)
```

## 🎯 **Available NSO Tools**

### **Device Discovery & Management**
- `show_all_devices` - Find all available routers
- `iterate` - Execute command on all devices

### **Device Information & Status**
- `get_router_version` - Get router version
- `get_router_clock` - Get router time
- `show_router_interfaces` - Show interface status

### **Network Routing & Protocols**
- `get_router_bgp_summary` - BGP summary
- `get_router_isis_neighbors` - ISIS neighbors
- `get_router_ospf_neigh` - OSPF neighbors

### **System Resources & Performance**
- `check_cpu` - CPU utilization
- `check_memory` - Memory usage

### **Network Diagnostics & Troubleshooting**
- `ping_router` - Ping from router
- `traceroute_router` - Traceroute from router
- `lldp_nei` - LLDP neighbors
- `check_alarm` - Router alarms

## 🔧 **Example Usage**

### **1. Discover All Devices**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"arguments": {}}' \
  http://localhost:5607/tools/show_all_devices
```

### **2. Get Router Version**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"arguments": {"router_name": "xr9kv-1"}}' \
  http://localhost:5607/tools/get_router_version
```

### **3. Check CPU Usage**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"arguments": {"router_name": "xr9kv-1"}}' \
  http://localhost:5607/tools/check_cpu
```

### **4. Execute Command on All Devices**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"arguments": {"cmd": "show version"}}' \
  http://localhost:5607/tools/iterate
```

## 🌐 **Web Interface**

You can also access the server through a web browser:
- **Server Info**: http://localhost:5607/
- **Health Check**: http://localhost:5607/health
- **Tools List**: http://localhost:5607/tools

## 🔒 **Security Notes**

- The server is running on `0.0.0.0:5607` (accessible from any interface)
- No authentication is currently implemented
- For production use, consider adding authentication and HTTPS

## 📞 **Support**

If you encounter any issues:
1. Check if the server is running: `curl http://localhost:5607/health`
2. Verify NSO is running: `ncs --status`
3. Check server logs for error messages

---

**Happy Network Automation! 🚀**
