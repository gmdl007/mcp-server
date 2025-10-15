# NSO Multi-Agent Standalone Application

A production-ready standalone Python application that provides intelligent network automation using NSO (Network Services Orchestrator) and LlamaIndex ReActAgent.

## 🚀 Features

- **NSO Integration**: Full NSO device management and automation
- **AI-Powered**: LlamaIndex ReActAgent with FunctionTools for intelligent query processing
- **Modern Web Interface**: Quart-based async web application
- **Cisco Azure OpenAI**: Integrated with Cisco's Azure OpenAI service
- **Production Ready**: Comprehensive logging, error handling, and monitoring
- **Standalone**: No Jupyter notebook dependencies

## 📋 Prerequisites

### System Requirements
- Python 3.11+
- NSO (Network Services Orchestrator) installed and running
- Network devices configured in NSO

### NSO Setup
1. Install NSO on your system
2. Start NSO daemon: `ncs --start`
3. Configure your network devices in NSO
4. Ensure devices are connected and synced

## 🛠️ Installation

### 1. Extract Package
```bash
unzip nso_multi_agent_package.zip
cd nso_multi_agent_package
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Edit `nso_multi_agent_standalone.py` and update the configuration section:

```python
# NSO Configuration - ADAPT THESE PATHS FOR YOUR ENVIRONMENT
NSO_DIR = "/opt/ncs/current"  # Change this to your NSO installation path
NSO_USERNAME = "admin"
NSO_PASSWORD = "admin"  # Change this to your NSO password

# Azure OpenAI Configuration - ADAPT THESE FOR YOUR ENVIRONMENT
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
TOKEN_URL = "https://id.cisco.com/oauth2/default/v1/token"
LLM_ENDPOINT = "https://chat-ai.cisco.com"
APP_KEY = "your_app_key"
```

## 🚀 Usage

### Basic Usage
```bash
python nso_multi_agent_standalone.py
```

### Production Deployment
```bash
# Using Gunicorn with Uvicorn workers
gunicorn nso_multi_agent_standalone:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5606

# Or using Uvicorn directly
uvicorn nso_multi_agent_standalone:app --host 0.0.0.0 --port 5606 --workers 4
```

### Access the Application
- **Web Interface**: http://localhost:5606
- **Health Check**: http://localhost:5606/health

## 🤖 Available Commands

The AI agent can process natural language queries and execute various network operations:

### Device Discovery
- "Show me all devices"
- "What devices are in the lab?"
- "List all routers"

### Device Information
- "Show version on xr9kv-1"
- "What interfaces are on device xr9kv-2?"
- "Show CPU usage on all devices"
- "Check memory on xr9kv-3"

### Network Operations
- "Ping 192.168.1.1 from xr9kv-1"
- "Traceroute to 8.8.8.8 from xr9kv-2"
- "Show BGP summary on xr9kv-1"
- "Show ISIS neighbors on all devices"

### Troubleshooting
- "Check alarms on xr9kv-1"
- "Show logs on xr9kv-2"
- "Show LLDP neighbors on all devices"

## 📊 Monitoring and Logging

### Log Files
- **Application Log**: `nso_multi_agent.log`
- **Console Output**: Real-time logging to stdout

### Health Check Endpoint
```bash
curl http://localhost:5606/health
```

Response:
```json
{
    "status": "healthy",
    "service": "nso-multi-agent",
    "version": "2.0",
    "nso_connected": true
}
```

## 🔒 Security Considerations

1. **NSO Credentials**: Change default NSO username/password
2. **Network Access**: Configure firewall rules for port 5606
3. **API Keys**: Secure your Azure OpenAI credentials
4. **HTTPS**: Consider using HTTPS in production (requires SSL certificates)

## 🐛 Troubleshooting

### Common Issues

#### 1. NSO Connection Failed
```
❌ Failed to setup NSO connection
```
**Solution**: 
- Verify NSO is running: `ncs --status`
- Check NSO_DIR path is correct
- Ensure NSO Python API is accessible

#### 2. LLM Authentication Failed
```
❌ Failed to setup LLM
```
**Solution**:
- Verify CLIENT_ID and CLIENT_SECRET are correct
- Check network connectivity to Cisco OAuth endpoint
- Ensure APP_KEY is valid

#### 3. Device Commands Failing
```
syntax error: missing display group
```
**Solution**:
- This is normal for netsim devices
- Use simpler commands like "show version"
- Check device connectivity in NSO

#### 4. Port Already in Use
```
OSError: [Errno 48] Address already in use
```
**Solution**:
- Change WEB_PORT in configuration
- Kill existing process: `lsof -t -i :5606 | xargs kill -9`

### Debug Mode
Enable debug mode for detailed logging:
```python
DEBUG_MODE = True
```

## 📈 Performance Optimization

### Production Settings
```python
# Increase worker processes
WEB_WORKERS = 4

# Optimize LLM settings
MAX_TOKENS = 3000
TEMPERATURE = 0.1
MAX_ITERATIONS = 1000
```

### Monitoring
- Monitor CPU and memory usage
- Check NSO connection status
- Monitor LLM API rate limits
- Review application logs regularly

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Restarting the Application
```bash
# Graceful restart
pkill -f nso_multi_agent_standalone.py
python nso_multi_agent_standalone.py
```

### Backup Configuration
- Backup your configuration settings
- Export NSO device configurations
- Save custom function tools

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Verify NSO and network connectivity
4. Check LlamaIndex and Quart documentation

## 📄 License

This application is provided as-is for educational and development purposes.

## 🎯 Version History

- **v2.0**: Quart-based async web application with nest_asyncio
- **v1.0**: Initial Flask-based implementation

---

**Happy Network Automation! 🚀**
