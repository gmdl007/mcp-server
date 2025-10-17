# NSO Multi-Agent Production Deployment Guide
# ===========================================

## Overview
This guide helps you deploy the NSO Multi-Agent Network Manager on a production host with real NCS devices using the standard production NSO installation path.

## Prerequisites
- NSO server running with real devices connected
- Python 3.8+ installed
- NSO Python API accessible at `/opt/ncs/current`
- Azure OpenAI API key and endpoint
- Production network devices connected to NSO

## Installation Steps

### 1. Copy Files to Production Host
```bash
# Copy these files to your production host:
scp nso_multi_agent_standalone_production.py target_host:/opt/nso-agent/
scp requirements.txt target_host:/opt/nso-agent/
scp nso_connection_test.py target_host:/opt/nso-agent/
scp DEPLOYMENT_GUIDE_PRODUCTION.md target_host:/opt/nso-agent/
```

### 2. Install Python Dependencies
```bash
# On production host:
pip install -r requirements.txt
```

### 3. Configure the Production Script
Edit `nso_multi_agent_standalone_production.py` and update these sections:

#### NSO Configuration (Lines 46-49) - PRODUCTION READY
```python
# Production NSO configuration - already set for standard production path
NSO_DIR = "/opt/ncs/current"  # Standard production NSO installation path
NSO_USER = "admin"            # Your NSO username
NSO_CONTEXT = "multi_agent_context"  # Your context name
```

#### Device Configuration (Lines 51-54) - DYNAMIC DISCOVERY
```python
# Device configuration - empty list for automatic discovery
EXPECTED_DEVICES = []  # Empty for dynamic discovery - update with your real device names if needed
AUTHGROUP_NAME = "cisco"  # Change if using different authgroup
```

#### Cisco Azure OpenAI Configuration (Lines 56-62) - ALREADY CONFIGURED
```python
# Cisco Azure OpenAI Configuration - Production ready
CLIENT_ID = 'cG9jLXRyaWFsMjAyM09jdG9iZXIxNwff_540f3843f35f87eeb7b238fc2f8807'
CLIENT_SECRET = 'b-mQoS2NXZe4I15lVXtY7iBHCAg9u7ufZFx7MZiOHAFlzRBkFmOaenUI2buRpRBb'
TOKEN_URL = "https://id.cisco.com/oauth2/default/v1/token"
LLM_ENDPOINT = "https://chat-ai.cisco.com"
APPKEY = "egai-prd-wws-log-chat-data-analysis-1"
```

#### Flask Configuration (Lines 64-67) - PRODUCTION SETTINGS
```python
# Flask configuration - adjust for production
FLASK_HOST = "0.0.0.0"  # Change if you want to restrict access
FLASK_PORT = 5606       # Change if port is already in use
FLASK_DEBUG = False     # Keep False for production
```

### 4. Test NSO Connection
Before running the full application, test NSO connectivity:

```python
# Create a simple test script for production
import os
import sys

# Set NSO environment for production
NSO_DIR = "/opt/ncs/current"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

# Test NSO connection
try:
    import ncs
    import ncs.maapi as maapi
    import ncs.maagic as maagic
    
    m = maapi.Maapi()
    m.start_user_session('admin', 'test_context')
    t = m.start_write_trans()
    root = maagic.get_root(t)
    
    # List devices
    devices = []
    for device in root.devices.device:
        devices.append(device.name)
    
    print(f"✅ NSO connection successful!")
    print(f"📱 Found {len(devices)} devices: {devices}")
    
    t.finish()
    m.close()
    
except Exception as e:
    print(f"❌ NSO connection failed: {e}")
```

### 5. Run the Production Application
```bash
# Start the production multi-agent application
python nso_multi_agent_standalone_production.py
```

### 6. Access Web Interface
Open your browser and navigate to:
```
http://your-production-host:5606
```

## Production Features

### Dynamic Device Discovery
The production version automatically discovers all devices connected to NSO:
- No need to hardcode device names
- Works with any device names
- Automatically adapts to your network topology

### Enhanced Error Handling
Production-ready error management:
- Comprehensive error messages
- Helpful troubleshooting information
- Graceful fallback mechanisms
- Detailed logging for production monitoring

### Real Device Support
Optimized for production network devices:
- Works with real routers, switches, firewalls
- Supports various NED types
- Handles production device responses
- Enhanced command execution

## Troubleshooting

### Common Production Issues

#### 1. NSO Connection Failed
- Verify NSO is running: `ncs --status`
- Check `/opt/ncs/current` path exists and is accessible
- Ensure NSO Python API is properly installed
- Verify user permissions for NSO access

#### 2. No Devices Found
- Check devices are connected in NSO: `ncs_cli -u admin -C "show devices"`
- Verify device operational state
- Check device authentication and connectivity
- Ensure devices are properly configured in NSO

#### 3. Cisco OAuth Errors
- Verify CLIENT_ID and CLIENT_SECRET are correct
- Check network connectivity to `id.cisco.com`
- Ensure appkey is valid and active
- Verify token endpoint is accessible from production network

#### 4. Command Execution Failed
- Check device operational state
- Verify NED support for command execution
- Check device authentication
- Ensure proper permissions for command execution

### Production Log Files
The application creates comprehensive log files:
- **Application logs**: `nso_multi_agent.log`
- **Console output**: Real-time monitoring
- **Error logs**: Detailed error information
- **Debug information**: Troubleshooting details

### Production Deployment Considerations
For production use, consider:
- **WSGI Server**: Use gunicorn or similar for production
- **SSL Certificates**: Set up SSL for secure communication
- **Logging**: Configure proper log rotation and management
- **Environment Variables**: Use environment variables for sensitive data
- **Monitoring**: Set up monitoring and alerting
- **Backup**: Regular backup of configuration and logs

## Example Production Queries
Once running, you can ask the agent about your production devices:
- "Show me all devices status"
- "What interfaces are on router1?"
- "Execute show version on switch1"
- "List all connected devices"
- "Check CPU usage on firewall1"
- "What is the operational state of all devices?"
- "Show me interface details for device router2"

## Production Support

### Key Differences from Development Version
- **NSO Path**: `/opt/ncs/current` (vs `/Users/gudeng/NCS-614`)
- **Device Discovery**: Dynamic (vs hardcoded netsim devices)
- **Error Messages**: Production-focused (vs netsim-specific)
- **Status Messages**: "Production devices" (vs "netsim devices")
- **Query Processing**: Enhanced for production device types

### Configuration Flexibility
- **EXPECTED_DEVICES**: Empty list for automatic discovery
- **Device Names**: Works with any device names found in NSO
- **Query Processing**: Enhanced for production device types
- **Error Handling**: More robust for production environments

## Support
If you encounter issues in production:
1. Check the log file for detailed error information
2. Verify NSO connectivity independently
3. Test Azure OpenAI API separately
4. Ensure all dependencies are installed
5. Check device connectivity and authentication
6. Verify NSO configuration and permissions

## Security Considerations
- Use environment variables for sensitive configuration
- Implement proper access controls
- Use SSL certificates for secure communication
- Regular security updates and monitoring
- Proper user authentication and authorization
