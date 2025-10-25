#!/usr/bin/env python3
"""
FastMCP NSO Server - Auto-Generated Tools Version
=================================================
Using FastMCP to create an MCP server with automatically generated NSO tools
based on YANG model analysis.
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

# Create FastMCP server
mcp = FastMCP("NSO Auto-Generated Tools Server")

# =============================================================================
# AUTO-GENERATED OSPF SERVICE TOOLS
# =============================================================================

def get_ospf_service_config(router_name: str = None) -> str:
    """Get OSPF service configuration for a router or all routers.
    
    Args:
        router_name: Router name to get OSPF config for (optional - shows all if not specified)
        
    Returns:
        str: Detailed OSPF service configuration
    """
    try:
        logger.info(f"🔧 Getting OSPF service configuration for: {router_name or 'all routers'}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        result_lines = [f"OSPF Service Configuration:"]
        result_lines.append("=" * 50)
        
        if hasattr(root, 'ospf') and hasattr(root.ospf, 'base'):
            ospf_base = root.ospf.base
            
            if router_name:
                if router_name in ospf_base:
                    service_config = ospf_base[router_name]
                    result_lines.append(f"\nRouter: {router_name}")
                    if hasattr(service_config, 'router_id'):
                        result_lines.append(f"  Router ID: {service_config.router_id}")
                    if hasattr(service_config, 'area'):
                        result_lines.append(f"  Area: {service_config.area}")
                else:
                    result_lines.append(f"No OSPF service configuration found for {router_name}")
            else:
                service_keys = list(ospf_base.keys()) if hasattr(ospf_base, 'keys') else []
                if service_keys:
                    result_lines.append(f"\nFound {len(service_keys)} OSPF service instances:")
                    for service_key in service_keys:
                        service_config = ospf_base[service_key]
                        result_lines.append(f"\nRouter: {service_key}")
                        if hasattr(service_config, 'router_id'):
                            result_lines.append(f"  Router ID: {service_config.router_id}")
                        if hasattr(service_config, 'area'):
                            result_lines.append(f"  Area: {service_config.area}")
                else:
                    result_lines.append("No OSPF service configurations found")
        else:
            result_lines.append("OSPF service package not available")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Got OSPF service configuration for: {router_name or 'all routers'}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error getting OSPF service configuration: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error getting OSPF service configuration: {e}"

def create_ospf_service(router_name: str, router_id: str, area: str = "0") -> str:
    """Create OSPF service instance for a router.
    
    Args:
        router_name: Router name to create OSPF service for
        router_id: OSPF Router ID in IPv4 format (e.g., '1.1.1.1')
        area: OSPF Area ID (default: '0' for area 0)
        
    Returns:
        str: Detailed result message showing OSPF service creation status
    """
    try:
        logger.info(f"🔧 Creating OSPF service for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Validate router exists
        if router_name not in root.devices.device:
            m.end_user_session()
            return f"Error: Router '{router_name}' not found in NSO devices"
        
        # Validate router_id format
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
        
        # Create OSPF service instance
        if router_name not in root.ospf.base:
            root.ospf.base.create(router_name)
        
        ospf_service = root.ospf.base[router_name]
        ospf_service.router_id = router_id
        ospf_service.area = area
        
        t.apply()
        
        m.end_user_session()
        
        result = f"""✅ Successfully created OSPF service for {router_name}:
  - Router ID: {router_id}
  - Area: {area}
  - Status: ✅ Applied to NSO service database
  - Note: Use NSO CLI 'commit' command to push to router"""
        
        logger.info(f"✅ Created OSPF service for {router_name}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error creating OSPF service for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error creating OSPF service for {router_name}: {e}"

def update_ospf_service(router_name: str, router_id: str = None, area: str = None) -> str:
    """Update OSPF service configuration for a router.
    
    Args:
        router_name: Router name to update OSPF service for
        router_id: New OSPF Router ID in IPv4 format (optional)
        area: New OSPF Area ID (optional)
        
    Returns:
        str: Detailed result message showing OSPF service update status
    """
    try:
        logger.info(f"🔧 Updating OSPF service for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Validate router exists
        if router_name not in root.devices.device:
            m.end_user_session()
            return f"Error: Router '{router_name}' not found in NSO devices"
        
        # Check if OSPF service exists
        if router_name not in root.ospf.base:
            m.end_user_session()
            return f"Error: OSPF service not found for {router_name}. Use create_ospf_service first."
        
        ospf_service = root.ospf.base[router_name]
        
        # Update router_id if provided
        if router_id:
            try:
                parts = router_id.split('.')
                if len(parts) != 4:
                    raise ValueError("Invalid format")
                for part in parts:
                    if not 0 <= int(part) <= 255:
                        raise ValueError("Invalid range")
                ospf_service.router_id = router_id
                logger.info(f"✅ Updated router ID: {router_id}")
            except ValueError:
                m.end_user_session()
                return f"Error: Invalid router ID format '{router_id}'. Use IPv4 format (e.g., '1.1.1.1')"
        
        # Update area if provided
        if area:
            ospf_service.area = area
            logger.info(f"✅ Updated area: {area}")
        
        t.apply()
        
        m.end_user_session()
        
        result_lines = [f"✅ Successfully updated OSPF service for {router_name}:"]
        if router_id:
            result_lines.append(f"  - Router ID: {router_id}")
        if area:
            result_lines.append(f"  - Area: {area}")
        result_lines.append(f"  - Status: ✅ Applied to NSO service database")
        result_lines.append(f"  - Note: Use NSO CLI 'commit' command to push to router")
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Updated OSPF service for {router_name}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error updating OSPF service for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error updating OSPF service for {router_name}: {e}"

def delete_ospf_service(router_name: str, confirm: bool = False) -> str:
    """Delete OSPF service instance for a router.
    
    Args:
        router_name: Router name to delete OSPF service for
        confirm: Confirmation flag for deletion (must be True)
        
    Returns:
        str: Detailed result message showing OSPF service deletion status
    """
    try:
        if not confirm:
            return f"❌ Deletion not confirmed. Set confirm=True to delete OSPF service from {router_name}"
        
        logger.info(f"🗑️ Deleting OSPF service for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Check if OSPF service exists
        if router_name in root.ospf.base:
            root.ospf.base[router_name].delete()
            t.apply()
            
            m.end_user_session()
            
            result = f"""✅ Successfully deleted OSPF service for {router_name}:
  - Status: ✅ Deleted from NSO service database
  - Note: Use NSO CLI 'commit' command to push to router"""
            
            logger.info(f"✅ Deleted OSPF service for {router_name}")
            return result
        else:
            m.end_user_session()
            return f"ℹ️ No OSPF service found for {router_name}"
        
    except Exception as e:
        logger.exception(f"❌ Error deleting OSPF service for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error deleting OSPF service for {router_name}: {e}"

def add_ospf_neighbor(router_name: str, neighbor_ip: str, neighbor_area: str) -> str:
    """Add OSPF neighbor to a router's service.
    
    Args:
        router_name: Router name to add neighbor to
        neighbor_ip: Neighbor IP address
        neighbor_area: Neighbor area ID
        
    Returns:
        str: Detailed result message showing neighbor addition status
    """
    try:
        logger.info(f"🔧 Adding OSPF neighbor {neighbor_ip} to router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Validate router exists
        if router_name not in root.devices.device:
            m.end_user_session()
            return f"Error: Router '{router_name}' not found in NSO devices"
        
        # Check if OSPF service exists
        if router_name not in root.ospf.base:
            m.end_user_session()
            return f"Error: OSPF service not found for {router_name}. Use create_ospf_service first."
        
        ospf_service = root.ospf.base[router_name]
        
        # Add neighbor to the service
        if hasattr(ospf_service, 'neighbor'):
            if neighbor_ip not in ospf_service.neighbor:
                ospf_service.neighbor.create(neighbor_ip)
                ospf_service.neighbor[neighbor_ip].area = neighbor_area
                logger.info(f"✅ Added neighbor {neighbor_ip} to area {neighbor_area}")
            else:
                logger.info(f"ℹ️ Neighbor {neighbor_ip} already exists")
        else:
            m.end_user_session()
            return f"Error: OSPF service for {router_name} does not support neighbors"
        
        t.apply()
        
        m.end_user_session()
        
        result = f"""✅ Successfully added OSPF neighbor for {router_name}:
  - Neighbor IP: {neighbor_ip}
  - Area: {neighbor_area}
  - Status: ✅ Applied to NSO service database
  - Note: Use NSO CLI 'commit' command to push to router"""
        
        logger.info(f"✅ Added OSPF neighbor {neighbor_ip} for {router_name}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error adding OSPF neighbor for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error adding OSPF neighbor for {router_name}: {e}"

def remove_ospf_neighbor(router_name: str, neighbor_ip: str, confirm: bool = False) -> str:
    """Remove OSPF neighbor from a router's service.
    
    Args:
        router_name: Router name to remove neighbor from
        neighbor_ip: Neighbor IP address to remove
        confirm: Confirmation flag for removal (must be True)
        
    Returns:
        str: Detailed result message showing neighbor removal status
    """
    try:
        if not confirm:
            return f"❌ Removal not confirmed. Set confirm=True to remove neighbor {neighbor_ip} from {router_name}"
        
        logger.info(f"🗑️ Removing OSPF neighbor {neighbor_ip} from router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Check if OSPF service exists
        if router_name in root.ospf.base:
            ospf_service = root.ospf.base[router_name]
            
            if hasattr(ospf_service, 'neighbor') and neighbor_ip in ospf_service.neighbor:
                ospf_service.neighbor[neighbor_ip].delete()
                t.apply()
                
                m.end_user_session()
                
                result = f"""✅ Successfully removed OSPF neighbor for {router_name}:
  - Neighbor IP: {neighbor_ip}
  - Status: ✅ Removed from NSO service database
  - Note: Use NSO CLI 'commit' command to push to router"""
                
                logger.info(f"✅ Removed OSPF neighbor {neighbor_ip} for {router_name}")
                return result
            else:
                m.end_user_session()
                return f"ℹ️ Neighbor {neighbor_ip} not found for {router_name}"
        else:
            m.end_user_session()
            return f"ℹ️ No OSPF service found for {router_name}"
        
    except Exception as e:
        logger.exception(f"❌ Error removing OSPF neighbor for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error removing OSPF neighbor for {router_name}: {e}"

def list_ospf_neighbors(router_name: str) -> str:
    """List OSPF neighbors for a router.
    
    Args:
        router_name: Router name to list neighbors for
        
    Returns:
        str: Detailed list of OSPF neighbors
    """
    try:
        logger.info(f"🔧 Listing OSPF neighbors for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        result_lines = [f"OSPF Neighbors for {router_name}:"]
        result_lines.append("=" * 40)
        
        if router_name in root.ospf.base:
            ospf_service = root.ospf.base[router_name]
            
            if hasattr(ospf_service, 'neighbor'):
                neighbor_keys = list(ospf_service.neighbor.keys()) if hasattr(ospf_service.neighbor, 'keys') else []
                
                if neighbor_keys:
                    result_lines.append(f"\nFound {len(neighbor_keys)} neighbors:")
                    for neighbor_key in neighbor_keys:
                        neighbor = ospf_service.neighbor[neighbor_key]
                        result_lines.append(f"\nNeighbor: {neighbor_key}")
                        if hasattr(neighbor, 'area'):
                            result_lines.append(f"  Area: {neighbor.area}")
                        if hasattr(neighbor, 'state'):
                            result_lines.append(f"  State: {neighbor.state}")
                else:
                    result_lines.append("\nNo neighbors configured")
            else:
                result_lines.append("\nNeighbor configuration not available")
        else:
            result_lines.append(f"\nNo OSPF service found for {router_name}")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Listed OSPF neighbors for {router_name}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error listing OSPF neighbors for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error listing OSPF neighbors for {router_name}: {e}"

def get_ospf_service_status(router_name: str) -> str:
    """Get OSPF service status and operational information.
    
    Args:
        router_name: Router name to get status for
        
    Returns:
        str: Detailed OSPF service status information
    """
    try:
        logger.info(f"🔧 Getting OSPF service status for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        result_lines = [f"OSPF Service Status for {router_name}:"]
        result_lines.append("=" * 50)
        
        if router_name in root.ospf.base:
            ospf_service = root.ospf.base[router_name]
            
            result_lines.append(f"\nService Configuration:")
            if hasattr(ospf_service, 'router_id'):
                result_lines.append(f"  Router ID: {ospf_service.router_id}")
            if hasattr(ospf_service, 'area'):
                result_lines.append(f"  Area: {ospf_service.area}")
            if hasattr(ospf_service, 'enabled'):
                result_lines.append(f"  Enabled: {ospf_service.enabled}")
            
            # Check for neighbors
            if hasattr(ospf_service, 'neighbor'):
                neighbor_keys = list(ospf_service.neighbor.keys()) if hasattr(ospf_service.neighbor, 'keys') else []
                result_lines.append(f"  Neighbors: {len(neighbor_keys)} configured")
            
            # Check service status
            result_lines.append(f"\nService Status:")
            result_lines.append(f"  Status: Active")
            result_lines.append(f"  Last Modified: {getattr(ospf_service, 'modified', 'Unknown')}")
            
        else:
            result_lines.append(f"\nNo OSPF service found for {router_name}")
            result_lines.append(f"Status: Not configured")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Got OSPF service status for {router_name}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error getting OSPF service status for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error getting OSPF service status for {router_name}: {e}"

# =============================================================================
# AUTO-GENERATED NSO RUNTIME TOOLS
# =============================================================================

def get_BGP_GRP__BGP_GRP_config(router_name: str = None) -> str:
    """Get BGP_GRP__BGP_GRP service configuration.
    
    Args:
        router_name: Router name to get BGP_GRP__BGP_GRP config for (optional)
        
    Returns:
        str: Detailed BGP_GRP__BGP_GRP service configuration
    """
    try:
        logger.info(f"🔧 Getting BGP_GRP__BGP_GRP service configuration for: {router_name or 'all routers'}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        result_lines = [f"BGP_GRP__BGP_GRP Service Configuration:"]
        result_lines.append("=" * 50)
        
        if hasattr(root, 'BGP_GRP__BGP_GRP'):
            service_root = root.BGP_GRP__BGP_GRP
            
            if hasattr(service_root, 'keys'):
                service_keys = list(service_root.keys())
                if service_keys:
                    result_lines.append(f"\nFound {len(service_keys)} BGP_GRP__BGP_GRP service instances:")
                    for service_key in service_keys:
                        result_lines.append(f"\nService Instance: {service_key}")
                        service_config = service_root[service_key]
                        # Show service attributes
                        for attr in dir(service_config):
                            if not attr.startswith('_') and not callable(getattr(service_config, attr)):
                                try:
                                    value = getattr(service_config, attr)
                                    result_lines.append(f"  {attr}: {value}")
                                except:
                                    pass
                else:
                    result_lines.append("\nNo BGP_GRP__BGP_GRP service instances found")
            else:
                result_lines.append("\nBGP_GRP__BGP_GRP service structure not available")
        else:
            result_lines.append("\nBGP_GRP__BGP_GRP service package not available")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Got BGP_GRP__BGP_GRP service configuration for: {router_name or 'all routers'}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error getting BGP_GRP__BGP_GRP service configuration: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error getting BGP_GRP__BGP_GRP service configuration: {e}"

def create_BGP_GRP__BGP_GRP_service(router_name: str) -> str:
    """Create BGP_GRP__BGP_GRP service instance.
    
    Args:
        router_name: Router name to create BGP_GRP__BGP_GRP service for
        
    Returns:
        str: Detailed result message showing service creation status
    """
    try:
        logger.info(f"🔧 Creating BGP_GRP__BGP_GRP service for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Validate router exists
        if router_name not in root.devices.device:
            m.end_user_session()
            return f"Error: Router '{router_name}' not found in NSO devices"
        
        # Create BGP_GRP__BGP_GRP service instance
        if hasattr(root, 'BGP_GRP__BGP_GRP'):
            if router_name not in root.BGP_GRP__BGP_GRP:
                root.BGP_GRP__BGP_GRP.create(router_name)
                logger.info(f"✅ Created BGP_GRP__BGP_GRP service instance for {router_name}")
            else:
                logger.info(f"ℹ️ BGP_GRP__BGP_GRP service already exists for {router_name}")
            
            t.apply()
            
            m.end_user_session()
            
            result = f"""✅ Successfully created BGP_GRP__BGP_GRP service for {router_name}:
  - Status: ✅ Applied to NSO service database
  - Note: Use NSO CLI 'commit' command to push to router"""
            
            logger.info(f"✅ Created BGP_GRP__BGP_GRP service for {router_name}")
            return result
        else:
            m.end_user_session()
            return f"Error: BGP_GRP__BGP_GRP service package not available"
        
    except Exception as e:
        logger.exception(f"❌ Error creating BGP_GRP__BGP_GRP service for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error creating BGP_GRP__BGP_GRP service for {router_name}: {e}"

def delete_BGP_GRP__BGP_GRP_service(router_name: str, confirm: bool = False) -> str:
    """Delete BGP_GRP__BGP_GRP service instance.
    
    Args:
        router_name: Router name to delete BGP_GRP__BGP_GRP service for
        confirm: Confirmation flag for deletion (must be True)
        
    Returns:
        str: Detailed result message showing service deletion status
    """
    try:
        if not confirm:
            return f"❌ Deletion not confirmed. Set confirm=True to delete BGP_GRP__BGP_GRP service from {router_name}"
        
        logger.info(f"🗑️ Deleting BGP_GRP__BGP_GRP service for router: {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Check if service exists
        if hasattr(root, 'BGP_GRP__BGP_GRP') and router_name in root.BGP_GRP__BGP_GRP:
            root.BGP_GRP__BGP_GRP[router_name].delete()
            t.apply()
            
            m.end_user_session()
            
            result = f"""✅ Successfully deleted BGP_GRP__BGP_GRP service for {router_name}:
  - Status: ✅ Deleted from NSO service database
  - Note: Use NSO CLI 'commit' command to push to router"""
            
            logger.info(f"✅ Deleted BGP_GRP__BGP_GRP service for {router_name}")
            return result
        else:
            m.end_user_session()
            return f"ℹ️ No BGP_GRP__BGP_GRP service found for {router_name}"
        
    except Exception as e:
        logger.exception(f"❌ Error deleting BGP_GRP__BGP_GRP service for {router_name}: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error deleting BGP_GRP__BGP_GRP service for {router_name}: {e}"

# =============================================================================
# BASIC TOOLS
# =============================================================================

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

def echo_text(text: str) -> str:
    """Echo back the provided text (debug/health)."""
    logger.info(f"🔧 Echoing text: {text}")
    return f"Echo: {text}"

# =============================================================================
# REGISTER TOOLS WITH FastMCP
# =============================================================================

# OSPF Service Tools
mcp.tool(get_ospf_service_config)
mcp.tool(create_ospf_service)
mcp.tool(update_ospf_service)
mcp.tool(delete_ospf_service)
mcp.tool(add_ospf_neighbor)
mcp.tool(remove_ospf_neighbor)
mcp.tool(list_ospf_neighbors)
mcp.tool(get_ospf_service_status)

# NSO Runtime Service Tools
mcp.tool(get_BGP_GRP__BGP_GRP_config)
mcp.tool(create_BGP_GRP__BGP_GRP_service)
mcp.tool(delete_BGP_GRP__BGP_GRP_service)

# Basic Tools
mcp.tool(show_all_devices)
mcp.tool(echo_text)

if __name__ == "__main__":
    logger.info("🚀 Starting FastMCP NSO Auto-Generated Tools Server...")
    logger.info("✅ FastMCP NSO Auto-Generated Tools Server Ready!")
    
    # Run the FastMCP server
    mcp.run()
