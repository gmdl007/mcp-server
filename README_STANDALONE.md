# NSO Multi-Agent Standalone Deployment Package
# ============================================

## Files Created for Deployment

### 1. Main Application
- **`nso_multi_agent_standalone.py`** - Complete standalone multi-agent application
- **`requirements.txt`** - Python dependencies
- **`DEPLOYMENT_GUIDE.md`** - Detailed deployment instructions

### 2. Testing and Validation
- **`nso_connection_test.py`** - NSO connectivity test script

## Quick Start for Target Host

### Step 1: Copy Files
```bash
# Copy these files to your target host:
scp nso_multi_agent_standalone.py target_host:/path/to/deployment/
scp requirements.txt target_host:/path/to/deployment/
scp nso_connection_test.py target_host:/path/to/deployment/
scp DEPLOYMENT_GUIDE.md target_host:/path/to/deployment/
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Application
Edit `nso_multi_agent_standalone.py` and update these key sections:

#### NSO Configuration (Lines 25-30)
```python
NSO_DIR = "/path/to/your/nso/installation"  # Your NSO path
NSO_USER = "admin"                          # Your NSO user
NSO_CONTEXT = "multi_agent_context"         # Your context
```

#### Device Configuration (Lines 32-35)
```python
EXPECTED_DEVICES = ["device1", "device2", "device3"]  # Your real devices
AUTHGROUP_NAME = "your_authgroup"                     # Your authgroup
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

### Step 4: Test NSO Connection
```bash
python nso_connection_test.py
```

### Step 5: Run Application
```bash
python nso_multi_agent_standalone.py
```

### Step 6: Access Web Interface
Open browser: `http://your-host:5606`

## Key Features

### ✅ NSO Integration
- Automatic NSO environment setup
- Device discovery and management
- Command execution on real devices
- Error handling and logging

### ✅ Multi-Agent Capabilities
- LlamaIndex ReActAgent integration
- Azure OpenAI LLM support
- Multiple NSO tools available
- Natural language query processing

### ✅ Web Interface
- Flask-based web UI
- Real-time agent interaction
- Device status monitoring
- Command execution interface

### ✅ Production Ready
- Comprehensive error handling
- Logging and monitoring
- SSL support (optional)
- Environment configuration

## Available Agent Tools

1. **show_all_devices** - List all NSO devices
2. **get_device_info** - Get detailed device information
3. **execute_command_on_device** - Execute commands on devices
4. **get_device_version** - Get device version information
5. **check_device_status** - Check device operational status

## Example Queries

- "Show me all devices"
- "What is the status of device1?"
- "Execute show version on device2"
- "List all connected devices"
- "Check the operational state of all devices"

## Troubleshooting

### Common Issues:
1. **NSO Connection Failed** - Check NSO_DIR path and NSO status
2. **Device Not Found** - Update EXPECTED_DEVICES with real device names
3. **Cisco OAuth Errors** - Verify CLIENT_ID, CLIENT_SECRET, and network connectivity
4. **Import Errors** - Install missing packages from requirements.txt

### Log Files:
- Application logs: `nso_multi_agent.log`
- Console output for real-time monitoring

## Support

The application includes comprehensive error handling and logging. Check the log file for detailed error information if issues occur.

## Notes

- No virtual environment required
- No Jupyter notebook dependency
- Works with real NCS devices (not netsim)
- Assumes NSO is already configured and running
- Devices should already be connected in NSO
