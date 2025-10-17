# 🚀 **NSO MCP Server Setup for Cursor**

## ✅ **What's Been Set Up**

Your NSO MCP server is now properly configured for Cursor integration:

### **📁 Files Created:**
- **`.cursor/mcp_config.json`** - Cursor MCP configuration
- **`nso_mcp_cursor.py`** - MCP server for Cursor
- **`nso_client.py`** - Python client for direct use
- **`simple_nso_test.py`** - Simple test script

### **🔧 Configuration:**
- **MCP Server**: `nso-mcp-cursor.py`
- **NSO Connection**: ✅ Connected to NCS 6.1.4
- **Devices Available**: 3 devices (xr9kv-1, xr9kv-2, xr9kv-3)
- **Tools Available**: 14 NSO function tools

## 🎯 **How to Use in Cursor**

### **Method 1: MCP Integration (Recommended)**

1. **Restart Cursor** to load the MCP configuration
2. **Open a new chat** in Cursor
3. **Ask Cursor to use NSO tools**:
   ```
   Show me all NSO devices
   Get the version of router xr9kv-1
   Check CPU usage on all routers
   ```

### **Method 2: Direct Python Client**

In Cursor, create a new Python file:

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

### **Method 3: Simple Test Script**

Run the test script directly in Cursor:

```bash
python simple_nso_test.py
```

## 🔧 **Available NSO Tools**

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

## 🌐 **Web Interface (Alternative)**

You can also access the HTTP server:
- **Server Info**: http://localhost:5607/
- **Health Check**: http://localhost:5607/health
- **Tools List**: http://localhost:5607/tools

## 🔧 **Troubleshooting**

### **If MCP doesn't work in Cursor:**

1. **Check if server is running**:
   ```bash
   curl http://localhost:5607/health
   ```

2. **Restart Cursor** to reload MCP configuration

3. **Check MCP configuration**:
   ```bash
   cat .cursor/mcp_config.json
   ```

4. **Test MCP server directly**:
   ```bash
   source mcp_venv/bin/activate
   source /Users/gudeng/NCS-614/ncsrc
   python nso_mcp_cursor.py
   ```

### **If NSO connection fails:**

1. **Check if NSO is running**:
   ```bash
   ncs --status
   ```

2. **Start NSO if needed**:
   ```bash
   cd /Users/gudeng/NCS-614
   source ncsrc
   ncs
   ```

## 🎉 **You're Ready!**

Your NSO network automation is now fully integrated with Cursor:

- ✅ **MCP Server**: Configured and ready
- ✅ **NSO Connection**: Established and working
- ✅ **14 Tools Available**: All NSO functions accessible
- ✅ **Cursor Integration**: Ready to use

**Happy Network Automation with Cursor! 🚀**

## 📞 **Support**

If you encounter any issues:
1. Check the troubleshooting section above
2. Verify NSO is running: `ncs --status`
3. Test the HTTP server: `curl http://localhost:5607/health`
4. Check server logs for error messages

---

**Your NSO MCP Server is ready for Cursor! 🎉**
