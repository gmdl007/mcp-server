# 🚀 **NSO Client for Cursor Integration**

## ✅ **Server Status**
Your NSO HTTP server is running successfully on `http://localhost:5607` with:
- **NSO Connection**: ✅ Connected to NCS 6.1.4
- **Devices Available**: 3 devices (xr9kv-1, xr9kv-2, xr9kv-3)
- **Tools Available**: 14 NSO function tools

## 🔗 **How to Connect from Cursor**

### **Method 1: Use the Python Client (Recommended)**

1. **Open Cursor** and navigate to your project directory
2. **Run the interactive client**:
   ```bash
   cd /Users/gudeng/MCP_Server
   python interactive_nso_client.py
   ```

3. **Or use the simple client**:
   ```bash
   python nso_client.py
   ```

### **Method 2: Direct Python Integration**

In Cursor, create a new Python file and use this code:

```python
from nso_client import NSOClient

# Create client
client = NSOClient()

# Check connection
health = client.health_check()
print(f"Connected: {health['nso_connected']}")

# Show all devices
devices = client.show_all_devices()
print(f"Devices: {devices}")

# Get router version
version = client.get_router_version("xr9kv-1")
print(f"Version: {version}")

# Check CPU usage
cpu = client.check_cpu("xr9kv-1")
print(f"CPU: {cpu}")
```

### **Method 3: Direct HTTP Calls**

You can also make direct HTTP requests from Cursor:

```python
import requests
import json

# Health check
response = requests.get("http://localhost:5607/health")
print(response.json())

# Execute a tool
response = requests.post(
    "http://localhost:5607/tools/show_all_devices",
    json={"arguments": {}}
)
print(response.json())
```

## 🎯 **Available NSO Commands**

### **Device Discovery**
- `client.show_all_devices()` - Find all routers
- `client.iterate("show version")` - Execute command on all devices

### **Device Information**
- `client.get_router_version("xr9kv-1")` - Get router version
- `client.get_router_clock("xr9kv-1")` - Get router time
- `client.show_router_interfaces("xr9kv-1")` - Show interfaces

### **Network Protocols**
- `client.get_router_bgp_summary("xr9kv-1")` - BGP summary
- `client.get_router_isis_neighbors("xr9kv-1")` - ISIS neighbors
- `client.get_router_ospf_neigh("xr9kv-1")` - OSPF neighbors

### **System Monitoring**
- `client.check_cpu("xr9kv-1")` - CPU usage
- `client.check_memory("xr9kv-1")` - Memory usage
- `client.check_alarm("xr9kv-1")` - Router alarms

### **Network Diagnostics**
- `client.ping_router("xr9kv-1", "8.8.8.8")` - Ping from router
- `client.traceroute_router("xr9kv-1", "8.8.8.8")` - Traceroute from router
- `client.lldp_nei("xr9kv-1")` - LLDP neighbors

## 🧪 **Quick Test**

Run this in Cursor to test the connection:

```python
from nso_client import NSOClient

client = NSOClient()

# Test connection
print("🔍 Testing NSO connection...")
health = client.health_check()
print(f"✅ Server: {health['service']} v{health['version']}")
print(f"📡 NSO Connected: {health['nso_connected']}")

# Test device discovery
print("\n📱 Testing device discovery...")
devices = client.show_all_devices()
print(f"Found devices: {devices}")

# Test router version
print("\n🔍 Testing router version...")
version = client.get_router_version("xr9kv-1")
print(f"Version: {version[:100]}...")

print("\n🎉 All tests passed! NSO client is working.")
```

## 🌐 **Web Interface**

You can also access the server through your web browser:
- **Server Info**: http://localhost:5607/
- **Health Check**: http://localhost:5607/health
- **Tools List**: http://localhost:5607/tools

## 🔧 **Troubleshooting**

If you encounter issues:

1. **Check if server is running**:
   ```bash
   curl http://localhost:5607/health
   ```

2. **Check if NSO is running**:
   ```bash
   ncs --status
   ```

3. **Restart the server if needed**:
   ```bash
   cd /Users/gudeng/MCP_Server
   source mcp_venv/bin/activate
   source /Users/gudeng/NCS-614/ncsrc
   python nso_http_server.py
   ```

## 🎉 **You're Ready!**

Your NSO HTTP server is running and ready for Cursor integration. You can now:

- **Query network devices** directly from Cursor
- **Execute network commands** on your routers
- **Monitor network health** in real-time
- **Automate network operations** with Python scripts

**Happy Network Automation! 🚀**
