# Cursor MCP Server Troubleshooting Guide

## Issue: MCP Server Not Appearing in Cursor IDE

If you've restarted Cursor but still can't see the MCP server, here are the steps to troubleshoot:

### 1. Check Configuration File Location

The MCP configuration file must be located at:
```
<project-root>/.cursor/mcp_config.json
```

In your case:
```
/Users/gudeng/MCP_Server/.cursor/mcp_config.json
```

### 2. Verify Configuration File Content

Your current configuration:
```json
{
  "mcpServers": {
    "nso-network-automation": {
      "command": "/Users/gudeng/MCP_Server/start_mcp_server.sh",
      "args": [],
      "env": {
        "NCS_DIR": "/Users/gudeng/NCS-614",
        "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
      }
    }
  }
}
```

### 3. Test MCP Server Manually

Test if the MCP server can start:

```bash
cd /Users/gudeng/MCP_Server
/Users/gudeng/MCP_Server/start_mcp_server.sh
```

Expected output:
```
INFO:__main__:🚀 Starting NSO MCP Server for Cursor...
INFO:__main__:✅ NSO environment configured: /Users/gudeng/NCS-614
INFO:__main__:✅ NSO modules imported successfully
INFO:__main__:✅ NSO connection established successfully
INFO:__main__:📱 Found 3 devices: ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']
INFO:__main__:✅ NSO MCP Server initialized successfully
```

### 4. Check Cursor MCP Integration

1. **Restart Cursor completely** (not just reload window)
2. **Check Cursor Settings**:
   - Go to Cursor Settings
   - Look for "MCP" or "Model Context Protocol" settings
   - Ensure MCP is enabled

3. **Check Cursor Logs**:
   - Open Cursor Developer Tools (Cmd+Shift+I)
   - Check Console for MCP-related errors
   - Look for connection attempts to your MCP server

### 5. Alternative Configuration Formats

Try these alternative configurations:

#### Option A: Direct Python Path
```json
{
  "mcpServers": {
    "nso-network-automation": {
      "command": "/Users/gudeng/MCP_Server/mcp_venv/bin/python",
      "args": ["/Users/gudeng/MCP_Server/nso_mcp_minimal.py"],
      "env": {
        "NCS_DIR": "/Users/gudeng/NCS-614",
        "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
      }
    }
  }
}
```

#### Option B: With Working Directory
```json
{
  "mcpServers": {
    "nso-network-automation": {
      "command": "/Users/gudeng/MCP_Server/start_mcp_server.sh",
      "args": [],
      "cwd": "/Users/gudeng/MCP_Server",
      "env": {
        "NCS_DIR": "/Users/gudeng/NCS-614",
        "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
      }
    }
  }
}
```

### 6. Check File Permissions

Ensure the wrapper script is executable:
```bash
chmod +x /Users/gudeng/MCP_Server/start_mcp_server.sh
```

### 7. Test MCP Server with Simple Input

Create a test script to verify MCP communication:

```python
# test_mcp_communication.py
import subprocess
import json

def test_mcp_server():
    try:
        # Start MCP server
        process = subprocess.Popen(
            ["/Users/gudeng/MCP_Server/start_mcp_server.sh"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"MCP Response: {response}")
        
        process.terminate()
        return True
        
    except Exception as e:
        print(f"Error testing MCP server: {e}")
        return False

if __name__ == "__main__":
    test_mcp_server()
```

### 8. Common Issues and Solutions

#### Issue: "Command not found"
- **Solution**: Use absolute paths in configuration
- **Check**: Ensure all paths exist and are accessible

#### Issue: "Permission denied"
- **Solution**: Make scripts executable with `chmod +x`
- **Check**: Verify file permissions

#### Issue: "Module not found"
- **Solution**: Ensure virtual environment is activated
- **Check**: Verify Python path and dependencies

#### Issue: "NSO connection failed"
- **Solution**: Start NSO daemon first
- **Check**: Verify NSO is running with `ncs --status`

### 9. Cursor-Specific Requirements

Some versions of Cursor may require:
- Specific MCP protocol versions
- Certain environment variables
- Specific file formats

Check Cursor's documentation for MCP integration requirements.

### 10. Debug Mode

Enable debug logging in the MCP server by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

This will provide more detailed information about what's happening during server startup.

### 11. Contact Support

If none of these steps resolve the issue:
1. Check Cursor's GitHub issues for MCP-related problems
2. Verify your Cursor version supports MCP
3. Consider using the HTTP server alternative instead of MCP

## Alternative: Use HTTP Server

If MCP continues to have issues, you can use the HTTP server instead:

```bash
cd /Users/gudeng/MCP_Server
source mcp_venv/bin/activate
source /Users/gudeng/NCS-614/ncsrc
python nso_http_server.py
```

Then use the HTTP client to interact with NSO tools.

