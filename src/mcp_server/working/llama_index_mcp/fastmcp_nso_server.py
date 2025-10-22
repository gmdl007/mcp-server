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
        m.start_user_session('cisco', 'test_context_1')
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
    """Return complete interface configuration tree for a router."""
    try:
        logger.info(f"🔧 Getting complete interface tree for router: {router_name}")
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        device = root.devices.device[router_name]
        interfaces = device.config.interface
        
        result_lines = [f"Complete Interface Configuration for {router_name}:"]
        result_lines.append("=" * 50)
        
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
                        
                        result_lines.append(f"\n{interface_name}:")
                        
                        # Check for IPv4 address
                        if hasattr(interface, 'ipv4') and hasattr(interface.ipv4, 'address'):
                            if hasattr(interface.ipv4.address, 'ip') and hasattr(interface.ipv4.address, 'mask'):
                                ip = interface.ipv4.address.ip
                                mask = interface.ipv4.address.mask
                                result_lines.append(f"  IPv4: {ip} {mask}")
                            else:
                                result_lines.append(f"  IPv4: Configured but no IP/mask found")
                        else:
                            result_lines.append(f"  IPv4: Not configured")
                        
                        # Check for description
                        if hasattr(interface, 'description'):
                            desc = interface.description
                            result_lines.append(f"  Description: {desc}")
                        
                        # Check for shutdown status
                        if hasattr(interface, 'shutdown'):
                            if interface.shutdown.exists():
                                result_lines.append(f"  Status: shutdown")
                            else:
                                result_lines.append(f"  Status: no shutdown")
                        else:
                            result_lines.append(f"  Status: no shutdown")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Got complete interface tree for {router_name}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error getting interface tree for {router_name}: {e}")
        return f"Error getting interface tree for {router_name}: {e}"

def configure_router_interface(router_name: str, interface_name: str, ip_address: str = None, description: str = None, shutdown: bool = None, delete_ip: bool = False) -> str:
    """Configure router interface settings including IP address management, description, and shutdown status.
    
    This function provides comprehensive interface configuration capabilities:
    - Add/Set IPv4 addresses with CIDR notation support
    - Delete existing IPv4 addresses from interfaces
    - Set interface descriptions
    - Configure interface shutdown/no-shutdown status
    - Apply changes to NSO configuration database
    
    Args:
        router_name: Name of the router device (e.g., 'xr9kv-1', 'xr9kv-2', 'xr9kv-3')
        interface_name: Interface name in format 'Type/Number' (e.g., 'GigabitEthernet/0/0/0/0', 'Loopback/100')
        ip_address: IPv4 address with CIDR mask (e.g., '192.168.1.1/24') or None to skip IP configuration
        description: Interface description text or None to skip description changes
        shutdown: True to shutdown interface, False to enable (no-shutdown), None to skip shutdown changes
        delete_ip: True to delete existing IPv4 address from interface, False to skip IP deletion
        
    Returns:
        str: Detailed result message showing what was configured and commit status
        
    Examples:
        # Add IP address
        configure_router_interface('xr9kv-1', 'GigabitEthernet/0/0/0/0', ip_address='192.168.1.1/24')
        
        # Delete IP address
        configure_router_interface('xr9kv-1', 'GigabitEthernet/0/0/0/0', delete_ip=True)
        
        # Set description and shutdown
        configure_router_interface('xr9kv-1', 'Loopback/100', description='Management loopback', shutdown=True)
        
        # Multiple changes at once
        configure_router_interface('xr9kv-1', 'GigabitEthernet/0/0/0/1', 
                                 ip_address='10.0.0.1/24', description='Uplink to core', shutdown=False)
    """
    try:
        logger.info(f"🔧 Configuring interface {interface_name} on router {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        # Start write transaction for configuration changes
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Get the device
        device = root.devices.device[router_name]
        interfaces = device.config.interface
        
        # Parse interface name (e.g., "GigabitEthernet/0/0/0/0" or "Loopback/0")
        if '/' in interface_name:
            if_type, if_number = interface_name.split('/', 1)
        else:
            return f"Error: Interface name must include type and number (e.g., 'GigabitEthernet/0/0/0/0')"
        
        # Get the interface object
        if hasattr(interfaces, if_type):
            if_objects = getattr(interfaces, if_type)
            # Interface key is a single string, not a tuple
            interface_key = if_number
            
            # Create interface if it doesn't exist
            if interface_key not in if_objects:
                if_objects.create(interface_key)
            
            interface = if_objects[interface_key]
            
            # Handle IP address configuration
            if delete_ip:
                # Delete existing IP address
                if hasattr(interface, 'ipv4'):
                    interface.ipv4.delete()
                    logger.info(f"✅ Deleted IP address from {interface_name}")
                else:
                    logger.info(f"ℹ️ No IP address to delete on {interface_name}")
            elif ip_address:
                # Parse IP address and mask (e.g., "192.168.1.1/24")
                if '/' in ip_address:
                    ip, mask = ip_address.split('/')
                    # Convert CIDR mask to dotted decimal
                    mask_int = int(mask)
                    if mask_int < 0 or mask_int > 32:
                        return f"Error: Invalid CIDR mask {mask_int}. Must be between 0 and 32."
                    
                    # Calculate dotted decimal mask
                    mask_bits = (0xFFFFFFFF << (32 - mask_int)) & 0xFFFFFFFF
                    mask_dotted = f"{(mask_bits >> 24) & 0xFF}.{(mask_bits >> 16) & 0xFF}.{(mask_bits >> 8) & 0xFF}.{mask_bits & 0xFF}"
                else:
                    ip = ip_address
                    mask_dotted = "255.255.255.0"  # Default /24
                
                # Create IPv4 configuration
                if not hasattr(interface, 'ipv4'):
                    interface.ipv4.create()
                if not hasattr(interface.ipv4, 'address'):
                    interface.ipv4.address.create()
                
                # Set IP and mask
                interface.ipv4.address.ip = ip
                interface.ipv4.address.mask = mask_dotted
                logger.info(f"✅ Set IP address {ip_address} on {interface_name}")
            
            # Configure description if provided
            if description:
                interface.description = description
                logger.info(f"✅ Set description '{description}' on {interface_name}")
            
            # Configure shutdown status if provided
            if shutdown is not None:
                if shutdown:
                    interface.shutdown.create()
                    logger.info(f"✅ Shutdown {interface_name}")
                else:
                    # Only delete shutdown if it exists
                    if hasattr(interface, 'shutdown') and interface.shutdown.exists():
                        interface.shutdown.delete()
                    logger.info(f"✅ No shutdown {interface_name}")
            
            # Apply the transaction to NSO configuration database
            t.apply()
            
            # Note: In NSO, changes are applied to the configuration database
            # The actual commit to devices is typically done through NSO CLI or web interface
            # For now, we'll indicate that changes are applied to NSO database
            logger.info(f"✅ Configuration applied to NSO database for {router_name}")
            commit_success = True  # Changes are in NSO database
            commit_error_msg = ""
            
            m.end_user_session()
            
            result_lines = [f"✅ Successfully configured interface {interface_name} on {router_name}:"]
            if delete_ip:
                result_lines.append(f"  - IP Address: Deleted")
            elif ip_address:
                result_lines.append(f"  - IP Address: {ip_address}")
            if description:
                result_lines.append(f"  - Description: {description}")
            if shutdown is not None:
                result_lines.append(f"  - Shutdown: {'Yes' if shutdown else 'No'}")
            
            # Add commit status to result
            if commit_success:
                result_lines.append(f"  - Status: ✅ Applied to NSO database")
                result_lines.append(f"  - Note: Use NSO CLI 'commit' command to push to router")
            else:
                result_lines.append(f"  - Status: ⚠️ Applied to NSO (commit failed: {commit_error_msg})")
            
            result = "\n".join(result_lines)
            logger.info(f"✅ Configuration completed for {interface_name}")
            return result
            
        else:
            m.end_user_session()
            return f"Error: Interface type '{if_type}' not supported"
            
    except Exception as e:
        logger.exception(f"❌ Error configuring interface {interface_name} on {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error configuring interface {interface_name} on {router_name}: {e}"

def commit_router_changes(router_name: str) -> str:
    """Note: In NSO, configuration changes are applied to the NSO database via MAAPI.
    The actual commit to physical devices is typically done through NSO CLI or web interface.
    This tool provides information about the commit process."""
    try:
        logger.info(f"ℹ️ Providing commit information for router: {router_name}")
        
        result = f"""ℹ️ Commit Information for {router_name}:

✅ Configuration changes have been applied to the NSO database.

📋 To commit changes to the physical router:
1. Access NSO CLI: ncs_cli -u cisco
2. Navigate to device: devices device {router_name} config
3. Execute commit: commit

🌐 Alternative - Use NSO Web Interface:
1. Open NSO web interface
2. Navigate to Devices → {router_name}
3. Click 'Commit' button

⚠️ Note: MAAPI applies changes to NSO database only.
Physical device commit requires NSO CLI or web interface."""
        
        logger.info(f"✅ Commit information provided for {router_name}")
        return result
            
    except Exception as e:
        logger.exception(f"❌ Error providing commit info for {router_name}: {e}")
        return f"Error providing commit information for {router_name}: {e}"

def echo_text(text: str) -> str:
    """Echo back the provided text (debug/health)."""
    logger.info(f"🔧 Echoing text: {text}")
    return f"Echo: {text}"

# Register tools with FastMCP
mcp.tool(show_all_devices)
mcp.tool(get_router_interfaces_config)
mcp.tool(configure_router_interface)
mcp.tool(commit_router_changes)
mcp.tool(echo_text)

if __name__ == "__main__":
    logger.info("🚀 Starting FastMCP NSO Server...")
    logger.info("✅ FastMCP NSO Server Ready!")
    
    # Run the FastMCP server
    mcp.run()
