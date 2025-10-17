# NSO Multi-Agent Standalone Deployment Guide
# ===========================================

## Overview
This guide helps you deploy the NSO Multi-Agent Network Manager on a different host with real NCS devices.

## Prerequisites
- NSO server running with real devices connected
- Python 3.8+ installed
- NSO Python API accessible
- Azure OpenAI API key and endpoint

## Installation Steps

### 1. Copy Files to Target Host
```bash
# Copy these files to your target host:
scp nso_multi_agent_standalone.py target_host:/path/to/deployment/
scp requirements.txt target_host:/path/to/deployment/
```

### 2. Install Python Dependencies
```bash
# On target host:
pip install -r requirements.txt
```

### 3. Configure the Script
Edit `nso_multi_agent_standalone.py` and update these sections:

#### NSO Configuration (Lines 25-30)
```python
# Change these paths for your environment
NSO_DIR = "/path/to/your/nso/installation"  # Your NSO installation path
NSO_USER = "admin"                          # Your NSO username
NSO_CONTEXT = "multi_agent_context"         # Your context name
```

#### Device Configuration (Lines 32-35)
```python
# Replace with your actual device names
EXPECTED_DEVICES = ["device1", "device2", "device3"]  # Your real device names
AUTHGROUP_NAME = "your_authgroup"                    # Your authgroup name
```

#### Cisco Azure OpenAI Configuration (Lines 51-57)
```python
# Cisco Azure OpenAI Configuration - Already configured
CLIENT_ID = 'cG9jLXRyaWFsMjAyM09jdG9iZXIxNwff_540f3843f35f87eeb7b238fc2f8807'
CLIENT_SECRET = 'b-mQoS2NXZe4I15lVXtY7iBHCAg9u7ufZFx7MZiOHAFlzRBkFmOaenUI2buRpRBb'
TOKEN_URL = "https://id.cisco.com/oauth2/default/v1/token"
LLM_ENDPOINT = "https://chat-ai.cisco.com"
APPKEY = "egai-prd-wws-log-chat-data-analysis-1"
```

#### Flask Configuration (Lines 44-47)
```python
# Adjust if needed
FLASK_HOST = "0.0.0.0"  # Change if you want to restrict access
FLASK_PORT = 5606       # Change if port is already in use
FLASK_DEBUG = False     # Set to True for development
```

### 4. Test NSO Connection
Before running the full application, test NSO connectivity:

```python
# Create a simple test script
import os
import sys

# Set NSO environment
NSO_DIR = "/path/to/your/nso/installation"
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

### 5. Run the Application
```bash
# Start the multi-agent application
python nso_multi_agent_standalone.py
```

### 6. Access Web Interface
Open your browser and navigate to:
```
http://your-host-ip:5606
```

## Troubleshooting

### Common Issues

#### 1. NSO Connection Failed
- Verify NSO is running: `ncs --status`
- Check NSO_DIR path is correct
- Ensure NSO Python API is accessible
- Verify user permissions

#### 2. Device Not Found
- Check device names in EXPECTED_DEVICES
- Verify devices are connected in NSO
- Check device operational state

#### 3. Cisco OAuth Errors
- Verify CLIENT_ID and CLIENT_SECRET are correct
- Check network connectivity to id.cisco.com
- Ensure appkey is valid
- Verify token endpoint is accessible

#### 4. Import Errors
- Install missing packages: `pip install package-name`
- Check Python path includes NSO API
- Verify Python version compatibility

### Log Files
The application creates a log file: `nso_multi_agent.log`

### Production Deployment
For production use, consider:
- Using a production WSGI server (gunicorn)
- Setting up SSL certificates
- Configuring proper logging
- Using environment variables for sensitive data

## Example Queries
Once running, you can ask the agent:
- "Show me all devices"
- "What is the status of device1?"
- "Execute show version on device2"
- "List all connected devices"
- "Check the operational state of all devices"

## Support
If you encounter issues:
1. Check the log file for error details
2. Verify NSO connectivity independently
3. Test Azure OpenAI API separately
4. Ensure all dependencies are installed
