#!/usr/bin/env python3
"""
FastMCP NSO Server
==================
Using FastMCP to create an MCP server with NSO tools
"""

import os
import sys
import logging
import requests
import base64
from dotenv import load_dotenv

# Set NSO environment variables
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add NSO Python API to Python path
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

# Import NSO modules
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

# Import FastMCP
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Azure OpenAI credentials
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
token_url = os.getenv('TOKEN_URL')
llm_endpoint = os.getenv('LLM_ENDPOINT')
appkey = os.getenv('APP_KEY')

# Create FastMCP server
mcp = FastMCP("NSO Server")

def show_all_devices() -> str:
    """Find out all available routers in the lab, return their names."""
    try:
        logger.info("🔧 Getting all devices from NSO...")
        m = maapi.Maapi()
        m.start_user_session('admin', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        devices = root.devices.device
        device_keys = list(devices.keys())
        device_names = [str(key[0]) for key in device_keys]
        m.end_user_session()
        
        result = f"Available devices: {', '.join(device_names)}"
        logger.info(f"✅ Found devices: {device_names}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error getting devices: {e}")
        return f"Error getting devices: {e}"

def get_router_interfaces_config(router_name: str) -> str:
    """Return configured interfaces (Loopback/GigabitEthernet/Ethernet) with IPv4 for a router."""
    try:
        logger.info(f"🔧 Getting interfaces for router: {router_name}")
        m = maapi.Maapi()
        m.start_user_session('admin', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        device = root.devices.device[router_name]
        interfaces = device.config.interface
        
        result_lines = [f"Interfaces for {router_name}:"]
        
        # Get all interface types
        interface_types = ['GigabitEthernet', 'Loopback', 'MgmtEth', 'TenGigE', 'Bundle_Ether']
        
        for if_type in interface_types:
            if hasattr(interfaces, if_type):
                if_objects = getattr(interfaces, if_type)
                if hasattr(if_objects, 'keys'):
                    interface_keys = list(if_objects.keys())
                    for interface_key in interface_keys:
                        interface_name = f"{if_type}/{str(interface_key[0])}"
                        interface = if_objects[interface_key]
                        
                        if hasattr(interface, 'ip') and hasattr(interface.ip, 'address'):
                            for addr in interface.ip.address:
                                result_lines.append(f"  {interface_name}: {addr.ip}")
                        else:
                            result_lines.append(f"  {interface_name}: No IP configured")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Got interfaces for {router_name}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error getting interfaces for {router_name}: {e}")
        return f"Error getting interfaces for {router_name}: {e}"

def echo_text(text: str) -> str:
    """Echo back the provided text (debug/health)."""
    logger.info(f"🔧 Echoing text: {text}")
    return f"Echo: {text}"

# Register tools with FastMCP
mcp.tool(show_all_devices)
mcp.tool(get_router_interfaces_config)
mcp.tool(echo_text)

if __name__ == "__main__":
    logger.info("🚀 Starting FastMCP NSO Server...")
    logger.info("✅ FastMCP NSO Server Ready!")
    
    # Run the FastMCP server
    mcp.run()
