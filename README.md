# NSO MCP Server for Cursor

A Model Context Protocol (MCP) server that integrates Cisco NSO (Network Services Orchestrator) with Cursor IDE for network automation tasks.

## 🚀 Quick Start

1. **Prerequisites**
   - Cisco NSO installed and running
   - Python 3.13+
   - Cursor IDE

2. **Installation**
   ```bash
   # Clone or navigate to the project
   cd /Users/gudeng/MCP_Server
   
   # Activate the MCP virtual environment
   source mcp_venv/bin/activate
   
   # Install dependencies
   pip install -r src/mcp_server/mcp_requirements.txt
   ```

3. **Configuration**
   - MCP configuration is automatically set up in `.cursor/mcp.json`
   - NSO environment variables are configured in the wrapper script

4. **Usage**
   - Restart Cursor IDE
   - Open Tools & MCP settings
   - Verify "nso-network-automation" shows "14 tools available"

## 📁 Project Structure

```
MCP_Server/
├── src/                          # Source code
│   ├── mcp_server/              # MCP server implementation
│   │   ├── nso_mcp_simple_fixed.py    # Main MCP server
│   │   ├── start_nso_mcp.sh           # Wrapper script
│   │   ├── mcp_requirements.txt       # Dependencies
│   │   └── diagnose_mcp.py            # Diagnostic tool
│   ├── flask_apps/              # Flask applications
│   └── notebooks/               # Jupyter notebooks
├── config/                      # Configuration files
│   ├── cursor_mcp_config.json  # Cursor MCP config
│   └── mcp_config.json         # Alternative config
├── scripts/                     # Utility scripts
│   ├── deployment/             # Deployment scripts
│   └── testing/                # Test scripts
├── docs/                       # Documentation
│   ├── setup/                  # Setup guides
│   ├── deployment/             # Deployment guides
│   └── troubleshooting/        # Troubleshooting
├── archive/                    # Archived files
│   ├── old_versions/          # Previous implementations
│   ├── backup_notebooks/      # Backup notebooks
│   └── test_files/            # Old test files
├── netsim/                     # NSO network simulation
├── mcp_venv/                   # Python virtual environment
└── .cursor/                    # Cursor configuration
    └── mcp.json               # MCP server config
```

## 🛠️ Available Tools

The MCP server exposes 14 NSO network automation tools:

### Device Management
- `show_all_devices` - List all available routers
- `get_router_version` - Get router version information
- `get_router_clock` - Get router current time

### Network Monitoring
- `show_router_interfaces` - Show interface status
- `get_router_bgp_summary` - BGP summary
- `get_router_isis_neighbors` - ISIS neighbors
- `get_router_ospf_neigh` - OSPF neighbors
- `lldp_nei` - LLDP neighbors

### System Monitoring
- `check_cpu` - CPU utilization
- `check_memory` - Memory summary
- `check_alarm` - Router alarms

### Network Testing
- `ping_router` - Ping from router
- `traceroute_router` - Traceroute from router

### Bulk Operations
- `iterate` - Execute command on all devices

## 🔧 Configuration

### NSO Configuration
- **NSO Directory**: `/Users/gudeng/NCS-614`
- **Username**: `admin`
- **Password**: `admin`
- **Devices**: `xr9kv-1`, `xr9kv-2`, `xr9kv-3`

### MCP Configuration
The MCP server is configured in multiple locations for redundancy:
- `.cursor/mcp.json` (primary)
- `~/.cursor/mcp.json` (global backup)
- `config/cursor_mcp_config.json` (project config)

## 🧪 Testing

Run the diagnostic tool to verify setup:
```bash
cd /Users/gudeng/MCP_Server
source mcp_venv/bin/activate
python src/mcp_server/diagnose_mcp.py
```

## 📚 Documentation

- [Setup Guide](docs/setup/README_MCP.md)
- [Cursor Integration](docs/setup/CURSOR_INTEGRATION.md)
- [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md)
- [Troubleshooting](docs/troubleshooting/CURSOR_MCP_TROUBLESHOOTING.md)

## 🚀 Deployment

Deployment scripts are available in `scripts/deployment/`:
- `deploy.sh` - Basic deployment
- `deploy_production.sh` - Production deployment
- `Dockerfile` - Container deployment
- `deployment.yaml` - Kubernetes deployment

## 🔍 Troubleshooting

1. **"No tools, prompts, or resources"**
   - Check NSO is running
   - Verify MCP configuration in `.cursor/mcp.json`
   - Run diagnostic tool

2. **Connection Issues**
   - Verify NSO environment variables
   - Check wrapper script permissions
   - Review Cursor logs

3. **Tool Execution Errors**
   - Ensure NSO devices are accessible
   - Check NSO user permissions
   - Verify device names

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting guide
2. Run the diagnostic tool
3. Review Cursor MCP documentation
4. Check NSO logs and status