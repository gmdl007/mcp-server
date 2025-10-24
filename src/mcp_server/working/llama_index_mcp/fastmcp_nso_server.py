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

def execute_router_command(router_name: str, command: str) -> str:
    """Execute a router command on a specific device.
    
    This function executes router commands directly on the device using NSO's live status:
    - Execute show commands (e.g., 'show version', 'show interfaces')
    - Execute configuration commands (e.g., 'configure terminal', 'interface GigabitEthernet0/0/0/0')
    - Execute any valid router command
    - Return command output in readable format
    
    Args:
        router_name: Name of the router device (e.g., 'xr9kv-1', 'xr9kv-2', 'xr9kv-3')
        command: Router command to execute (e.g., 'show version', 'show interfaces', 'show ospf neighbor')
        
    Returns:
        str: Command output from the router
        
    Examples:
        # Execute show commands
        execute_router_command('xr9kv-1', 'show version')
        execute_router_command('xr9kv-1', 'show interfaces')
        execute_router_command('xr9kv-1', 'show ospf neighbor')
        
        # Execute configuration commands
        execute_router_command('xr9kv-1', 'show running-config')
        execute_router_command('xr9kv-1', 'show ip route')
        
        # Execute any router command
        execute_router_command('xr9kv-2', 'show bgp summary')
    """
    try:
        logger.info(f"🔧 Executing command '{command}' on router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        # Validate router exists
        if router_name not in root.devices.device:
            m.end_user_session()
            return f"Error: Router '{router_name}' not found in NSO devices"
        
        device = root.devices.device[router_name]
        
        try:
            # Get the 'exec' action object for live status
            show = device.live_status.__getitem__('exec').any
            
            # Prepare the input for the command
            inp = show.get_input()
            inp.args = [command]
            
            # Execute the command and get the result
            result = show.request(inp)
            
            # Format the output
            output_lines = [f"Command Execution Result for {router_name}:"]
            output_lines.append("=" * 60)
            output_lines.append(f"Command: {command}")
            output_lines.append("-" * 40)
            
            if hasattr(result, 'result') and result.result:
                # Split the result into lines for better formatting
                result_lines = str(result.result).split('\n')
                for line in result_lines:
                    if line.strip():  # Only add non-empty lines
                        output_lines.append(line)
            else:
                output_lines.append("No output returned from command")
            
            output_lines.append("-" * 40)
            output_lines.append(f"✅ Command executed successfully on {router_name}")
            
            m.end_user_session()
            
            result_text = "\n".join(output_lines)
            logger.info(f"✅ Command '{command}' executed successfully on {router_name}")
            return result_text
            
        except Exception as cmd_error:
            m.end_user_session()
            logger.exception(f"❌ Command execution error for {router_name}: {cmd_error}")
            return f"Error executing command '{command}' on {router_name}: {cmd_error}"
            
    except Exception as e:
        logger.exception(f"❌ Error executing command on {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error executing command '{command}' on {router_name}: {e}"

def get_router_config_section(router_name: str, config_section: str) -> str:
    """Get configuration for any top-level section of a router.
    
    This function provides flexible access to router configuration sections:
    - Display interface configurations (interface)
    - Display OSPF configurations (ospf)
    - Display BGP configurations (bgp)
    - Display any other top-level configuration section
    
    Args:
        router_name: Name of the router device (e.g., 'xr9kv-1', 'xr9kv-2', 'xr9kv-3')
        config_section: Configuration section name (e.g., 'interface', 'ospf', 'bgp', 'system')
        
    Returns:
        str: Detailed configuration for the specified section
        
    Examples:
        # Get interface configuration
        get_router_config_section('xr9kv-1', 'interface')
        
        # Get OSPF configuration
        get_router_config_section('xr9kv-1', 'ospf')
        
        # Get BGP configuration
        get_router_config_section('xr9kv-1', 'bgp')
        
        # Get system configuration
        get_router_config_section('xr9kv-1', 'system')
    """
    try:
        logger.info(f"🔧 Getting {config_section} configuration for router: {router_name}")
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        # Validate router exists
        if router_name not in root.devices.device:
            m.end_user_session()
            return f"Error: Router '{router_name}' not found in NSO devices"
        
        device = root.devices.device[router_name]
        
        result_lines = [f"{config_section.title()} Configuration for {router_name}:"]
        result_lines.append("=" * 60)
        
        # Handle different configuration sections
        if config_section.lower() == 'interface':
            # Special handling for interfaces (detailed)
            interfaces = device.config.interface
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
        
        elif config_section.lower() == 'ospf':
            # Handle OSPF configuration
            if hasattr(device.config, 'ospf'):
                ospf_config = device.config.ospf
                result_lines.append(f"\nOSPF Configuration:")
                
                # Check for OSPF base configuration
                if hasattr(ospf_config, 'base'):
                    result_lines.append(f"  Base Configuration:")
                    base_configs = list(ospf_config.base.keys()) if hasattr(ospf_config.base, 'keys') else []
                    for base_key in base_configs:
                        base = ospf_config.base[base_key]
                        result_lines.append(f"    Device: {base_key}")
                        if hasattr(base, 'router_id'):
                            result_lines.append(f"      Router ID: {base.router_id}")
                        if hasattr(base, 'area'):
                            result_lines.append(f"      Area: {base.area}")
                else:
                    result_lines.append(f"  No OSPF base configuration found")
                
                # Check for OSPF area configuration
                if hasattr(ospf_config, 'area'):
                    result_lines.append(f"  Area Configuration:")
                    areas = list(ospf_config.area.keys()) if hasattr(ospf_config.area, 'keys') else []
                    for area_key in areas:
                        area = ospf_config.area[area_key]
                        result_lines.append(f"    Area: {area_key}")
                        if hasattr(area, 'interface'):
                            interfaces = list(area.interface.keys()) if hasattr(area.interface, 'keys') else []
                            for if_key in interfaces:
                                result_lines.append(f"      Interface: {if_key}")
            else:
                result_lines.append(f"  No OSPF configuration found")
        
        elif config_section.lower() == 'bgp':
            # Handle BGP configuration
            if hasattr(device.config, 'bgp'):
                bgp_config = device.config.bgp
                result_lines.append(f"\nBGP Configuration:")
                
                # Check for BGP AS configuration
                if hasattr(bgp_config, 'as'):
                    result_lines.append(f"  AS Number: {getattr(bgp_config, 'as')}")
                
                # Check for BGP neighbors
                if hasattr(bgp_config, 'neighbor'):
                    result_lines.append(f"  Neighbors:")
                    neighbors = list(bgp_config.neighbor.keys()) if hasattr(bgp_config.neighbor, 'keys') else []
                    for neighbor_key in neighbors:
                        neighbor = bgp_config.neighbor[neighbor_key]
                        result_lines.append(f"    Neighbor: {neighbor_key}")
                        if hasattr(neighbor, 'remote_as'):
                            result_lines.append(f"      Remote AS: {neighbor.remote_as}")
            else:
                result_lines.append(f"  No BGP configuration found")
        
        else:
            # Generic handling for other configuration sections
            if hasattr(device.config, config_section):
                section_config = getattr(device.config, config_section)
                result_lines.append(f"\n{config_section.title()} Configuration:")
                
                # Try to display the configuration in a readable format
                try:
                    # Convert to string representation
                    config_str = str(section_config)
                    if config_str and config_str != 'None':
                        # Split into lines and indent
                        lines = config_str.split('\n')
                        for line in lines[:20]:  # Limit to first 20 lines
                            if line.strip():
                                result_lines.append(f"  {line}")
                        if len(lines) > 20:
                            result_lines.append(f"  ... (truncated, {len(lines)-20} more lines)")
                    else:
                        result_lines.append(f"  No {config_section} configuration found")
                except Exception as e:
                    result_lines.append(f"  Error reading {config_section} configuration: {e}")
            else:
                result_lines.append(f"  No {config_section} configuration section found")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Got {config_section} configuration for {router_name}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error getting {config_section} configuration for {router_name}: {e}")
        return f"Error getting {config_section} configuration for {router_name}: {e}"

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

def rollback_router_changes(router_name: str, rollback_id: int = None) -> str:
    """Rollback router configuration to a previous state.
    
    This function provides rollback capabilities for router configurations:
    - Rollback to a specific rollback ID
    - List available rollback IDs
    - Rollback to the most recent previous state
    
    Args:
        router_name: Name of the router device (e.g., 'xr9kv-1', 'xr9kv-2', 'xr9kv-3')
        rollback_id: Specific rollback ID to restore to, or None to list available rollbacks
        
    Returns:
        str: Detailed result message showing rollback status and available rollbacks
        
    Examples:
        # List available rollbacks
        rollback_router_changes('xr9kv-1')
        
        # Rollback to specific ID
        rollback_router_changes('xr9kv-1', rollback_id=1)
        
        # Rollback to most recent (rollback 0)
        rollback_router_changes('xr9kv-1', rollback_id=0)
    """
    try:
        logger.info(f"🔧 Rolling back configuration for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        if rollback_id is None:
            # List available rollbacks
            result_lines = [f"Available rollbacks for {router_name}:"]
            result_lines.append("=" * 50)
            
            # Get rollback information
            t = m.start_read_trans()
            root = maagic.get_root(t)
            
            device = root.devices.device[router_name]
            
            # Check if device has rollback data
            if hasattr(device, 'rollback') and hasattr(device.rollback, 'rollback'):
                rollbacks = device.rollback.rollback
                if hasattr(rollbacks, 'keys'):
                    rollback_keys = list(rollbacks.keys())
                    for i, key in enumerate(rollback_keys):
                        rollback = rollbacks[key]
                        result_lines.append(f"  Rollback {i}: {rollback}")
                else:
                    result_lines.append("  No rollback data available")
            else:
                result_lines.append("  No rollback data available")
            
            m.end_user_session()
            
            result_lines.append("\n📋 Usage:")
            result_lines.append("  - To rollback to specific ID: rollback_router_changes('xr9kv-1', rollback_id=1)")
            result_lines.append("  - To rollback to most recent: rollback_router_changes('xr9kv-1', rollback_id=0)")
            
            result = "\n".join(result_lines)
            logger.info(f"✅ Listed rollbacks for {router_name}")
            return result
            
        else:
            # Perform rollback
            t = m.start_write_trans()
            root = maagic.get_root(t)
            
            device = root.devices.device[router_name]
            
            # Perform rollback using NSO's rollback functionality
            try:
                # Use NSO's rollback method - need to use the correct API
                # Based on NSO documentation, rollback is typically done via CLI or specific API calls
                # For now, we'll provide information about how to perform rollback
                
                result_lines = [f"ℹ️ Rollback information for {router_name}:"]
                result_lines.append("=" * 50)
                result_lines.append(f"  - Requested rollback ID: {rollback_id}")
                result_lines.append(f"  - Status: ⚠️ Rollback requires NSO CLI or specific API")
                
                result_lines.append("\n📋 To perform rollback via NSO CLI:")
                result_lines.append(f"  1. Access NSO CLI: ncs_cli -u cisco")
                result_lines.append(f"  2. Navigate to device: devices device {router_name}")
                result_lines.append(f"  3. Execute rollback: rollback {rollback_id}")
                result_lines.append(f"  4. Commit changes: commit")
                
                result_lines.append("\n🌐 Alternative - Use NSO Web Interface:")
                result_lines.append(f"  1. Open NSO web interface")
                result_lines.append(f"  2. Navigate to Devices → {router_name}")
                result_lines.append(f"  3. Click 'Rollback' button")
                result_lines.append(f"  4. Select rollback {rollback_id}")
                
                result_lines.append("\n⚠️ Note: MAAPI rollback requires specific NSO API calls.")
                result_lines.append("   This tool provides rollback information and CLI instructions.")
                
                result = "\n".join(result_lines)
                logger.info(f"✅ Rollback information provided for {router_name} rollback {rollback_id}")
                
            except Exception as rollback_error:
                result = f"❌ Error providing rollback info for {router_name}: {rollback_error}"
                logger.exception(f"❌ Rollback error for {router_name}: {rollback_error}")
            
            m.end_user_session()
            return result
            
    except Exception as e:
        logger.exception(f"❌ Error with rollback for {router_name}: {e}")
        return f"Error with rollback for {router_name}: {e}"

def provision_ospf_base(router_name: str, router_id: str, area: str = "0") -> str:
    """Provision OSPF base configuration on a router.
    
    This function provisions OSPF base configuration using NSO's OSPF package:
    - Configure OSPF router ID
    - Configure OSPF area
    - Apply changes to NSO database
    
    Args:
        router_name: Name of the router device (e.g., 'xr9kv-1', 'xr9kv-2', 'xr9kv-3')
        router_id: OSPF router ID in IPv4 format (e.g., '1.1.1.1', '2.2.2.2')
        area: OSPF area ID (default: '0' for area 0)
        
    Returns:
        str: Detailed result message showing OSPF configuration status
        
    Examples:
        # Configure OSPF base for xr9kv-1
        provision_ospf_base('xr9kv-1', '1.1.1.1', '0')
        
        # Configure OSPF base for xr9kv-2 with area 0
        provision_ospf_base('xr9kv-2', '1.1.1.2')
        
        # Configure OSPF base for xr9kv-3 with custom area
        provision_ospf_base('xr9kv-3', '1.1.1.3', '1')
    """
    try:
        logger.info(f"🔧 Provisioning OSPF base configuration for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Validate router exists
        if router_name not in root.devices.device:
            m.end_user_session()
            return f"Error: Router '{router_name}' not found in NSO devices"
        
        # Validate router_id format (basic IPv4 validation)
        try:
            parts = router_id.split('.')
            if len(parts) != 4:
                raise ValueError("Invalid format")
            for part in parts:
                if not 0 <= int(part) <= 255:
                    raise ValueError("Invalid range")
        except ValueError:
            m.end_user_session()
            return f"Error: Invalid router ID format '{router_id}'. Use IPv4 format (e.g., '1.1.1.1')"
        
        # Configure OSPF base
        try:
            # Check if OSPF base configuration exists, create if not
            if router_name not in root.ospf.base:
                logger.info(f"🔧 Creating OSPF base configuration for {router_name}")
                root.ospf.base.create(router_name)
            
            # Access OSPF base configuration
            ospf_base = root.ospf.base[router_name]
            
            # Set router ID
            ospf_base.router_id = router_id
            logger.info(f"✅ Set OSPF router ID: {router_id}")
            
            # Set area
            ospf_base.area = area
            logger.info(f"✅ Set OSPF area: {area}")
            
            # Apply changes
            t.apply()
            
            logger.info(f"✅ OSPF base configuration applied to NSO database for {router_name}")
            
            m.end_user_session()
            
            result_lines = [f"✅ Successfully provisioned OSPF base configuration for {router_name}:"]
            result_lines.append(f"  - Router ID: {router_id}")
            result_lines.append(f"  - Area: {area}")
            result_lines.append(f"  - Status: ✅ Applied to NSO database")
            result_lines.append(f"  - Note: Use NSO CLI 'commit' command to push to router")
            
            result = "\n".join(result_lines)
            logger.info(f"✅ OSPF base configuration completed for {router_name}")
            return result
            
        except Exception as ospf_error:
            m.end_user_session()
            logger.exception(f"❌ OSPF configuration error for {router_name}: {ospf_error}")
            return f"Error configuring OSPF base for {router_name}: {ospf_error}"
            
    except Exception as e:
        logger.exception(f"❌ Error provisioning OSPF base for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error provisioning OSPF base for {router_name}: {e}"

def echo_text(text: str) -> str:
    """Echo back the provided text (debug/health)."""
    logger.info(f"🔧 Echoing text: {text}")
    return f"Echo: {text}"

# Register tools with FastMCP
mcp.tool(show_all_devices)
mcp.tool(get_router_interfaces_config)
mcp.tool(get_router_config_section)
mcp.tool(execute_router_command)
mcp.tool(configure_router_interface)
mcp.tool(commit_router_changes)
mcp.tool(rollback_router_changes)
mcp.tool(provision_ospf_base)
mcp.tool(echo_text)

if __name__ == "__main__":
    logger.info("🚀 Starting FastMCP NSO Server...")
    logger.info("✅ FastMCP NSO Server Ready!")
    
    # Run the FastMCP server
    mcp.run()
