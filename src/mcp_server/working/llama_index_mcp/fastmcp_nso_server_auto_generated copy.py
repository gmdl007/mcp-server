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
# OSPF SERVICE TOOLS - SIMPLIFIED
# =============================================================================
# Two main OSPF services:
# 1. OSPF Base Service: Basic OSPF config (Router ID, Area)
# 2. OSPF Neighbor Service: Manage OSPF neighbors

def get_ospf_base_service(router_name: str = None) -> str:
    """Get OSPF base service configuration for a router or all routers.
    
    Args:
        router_name: Router name to get OSPF config for (optional - shows all if not specified)
        
    Returns:
        str: Detailed OSPF base service configuration
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
            # Use del to remove the service from the list
            del root.ospf.base[router_name]
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

def get_router_interfaces_config(router_name: str) -> str:
    """Return complete interface configuration tree for a router.
    
    Args:
        router_name: Name of the router device (e.g., 'xr9kv-1', 'xr9kv-2', 'xr9kv-3')
        
    Returns:
        str: Complete interface configuration showing IP addresses, descriptions, and status
    """
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
        logger.exception(f"❌ Error getting interface configuration: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error getting interface configuration for {router_name}: {e}"

def echo_text(text: str) -> str:
    """Echo back the provided text (debug/health)."""
    logger.info(f"🔧 Echoing text: {text}")
    return f"Echo: {text}"

# =============================================================================
# OSPF SERVICE TOOLS
# =============================================================================

def get_ospf_service_config(router_name: str = None) -> str:
    """Get NSO SERVICE-LEVEL OSPF configuration.
    
    This function shows OSPF configuration from NSO's OSPF SERVICE PACKAGE:
    - Shows NSO service-level OSPF base configurations
    - Shows OSPF service instances and their settings
    - Shows service-level OSPF area configurations
    
    IMPORTANT OSPF DISTINCTION:
    - This tool shows NSO SERVICE-LEVEL OSPF (root.ospf.base[router_name])
    - For DEVICE-LEVEL OSPF config, use get_router_config_section('ospf') instead
    - Service-level OSPF is managed by NSO's OSPF package, not direct device config
    
    Args:
        router_name: Specific router name to show OSPF service config for, or None to show all
        
    Returns:
        str: Detailed NSO service-level OSPF configuration
        
    Examples:
        # Get NSO service-level OSPF config for specific router
        get_ospf_service_config('xr9kv-1')
        
        # Get NSO service-level OSPF config for all routers
        get_ospf_service_config()
        
        # Get NSO service-level OSPF config for xr9kv-2
        get_ospf_service_config('xr9kv-2')
    """
    try:
        logger.info(f"🔧 Getting NSO SERVICE-LEVEL OSPF configuration for: {router_name or 'all routers'}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        t = m.start_read_trans()
        root = maagic.get_root(t)
        
        result_lines = [f"NSO SERVICE-LEVEL OSPF Configuration:"]
        result_lines.append("=" * 60)
        result_lines.append("Note: This shows NSO service-level OSPF, not device-level OSPF config")
        result_lines.append("")
        
        # Check if OSPF service package is available
        if hasattr(root, 'ospf') and hasattr(root.ospf, 'base'):
            ospf_base = root.ospf.base
            
            if router_name:
                # Show specific router's OSPF service config
                if router_name in ospf_base:
                    service_config = ospf_base[router_name]
                    result_lines.append(f"OSPF Service Configuration for {router_name}:")
                    result_lines.append("-" * 40)
                    
                    if hasattr(service_config, 'router_id'):
                        result_lines.append(f"  Router ID: {service_config.router_id}")
                    if hasattr(service_config, 'area'):
                        result_lines.append(f"  Area: {service_config.area}")
                    if hasattr(service_config, 'enabled'):
                        result_lines.append(f"  Enabled: {service_config.enabled}")
                    
                    # Check for neighbors
                    if hasattr(service_config, 'neighbor'):
                        neighbors = service_config.neighbor
                        if hasattr(neighbors, 'keys'):
                            neighbor_list = list(neighbors.keys())
                            if neighbor_list:
                                result_lines.append(f"  Neighbors: {len(neighbor_list)} configured")
                                for neighbor in neighbor_list:
                                    neighbor_config = neighbors[neighbor]
                                    result_lines.append(f"    - {neighbor}:")
                                    if hasattr(neighbor_config, 'local_interface'):
                                        result_lines.append(f"      Local Interface: {neighbor_config.local_interface}")
                                    if hasattr(neighbor_config, 'local_ip'):
                                        result_lines.append(f"      Local IP: {neighbor_config.local_ip}")
                                    if hasattr(neighbor_config, 'remote_ip'):
                                        result_lines.append(f"      Remote IP: {neighbor_config.remote_ip}")
                    else:
                        result_lines.append("  Neighbors: None")
                    
                    # Show any additional service-level configurations
                    for attr in dir(service_config):
                        if not attr.startswith('_') and attr not in ['router_id', 'area', 'enabled', 'neighbor', 'device']:
                            try:
                                value = getattr(service_config, attr)
                                if not callable(value):
                                    result_lines.append(f"  {attr}: {value}")
                            except:
                                pass
                else:
                    result_lines.append(f"No OSPF service configuration found for {router_name}")
            else:
                # Show all routers' OSPF service config
                if hasattr(ospf_base, 'keys'):
                    service_keys = list(ospf_base.keys())
                    if service_keys:
                        result_lines.append(f"OSPF Service Configurations ({len(service_keys)} routers):")
                        result_lines.append("-" * 40)
                        
                        for service_key in service_keys:
                            service_config = ospf_base[service_key]
                            result_lines.append(f"\nRouter: {service_key}")
                            
                            if hasattr(service_config, 'router_id'):
                                result_lines.append(f"  Router ID: {service_config.router_id}")
                            if hasattr(service_config, 'area'):
                                result_lines.append(f"  Area: {service_config.area}")
                            if hasattr(service_config, 'enabled'):
                                result_lines.append(f"  Enabled: {service_config.enabled}")
                    else:
                        result_lines.append("No OSPF service configurations found")
                else:
                    result_lines.append("No OSPF service configurations found")
        else:
            result_lines.append("OSPF service package not available or not configured")
            result_lines.append("Note: This requires NSO OSPF service package to be installed")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info(f"✅ Got NSO service-level OSPF configuration for: {router_name or 'all routers'}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error getting NSO service-level OSPF configuration: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error getting NSO service-level OSPF configuration: {e}"

# =============================================================================
# SIMPLIFIED OSPF SERVICE TOOLS
# Based on YANG: l-ospf-base.yang (base service) and ospf.yang (full service)
# =============================================================================

def setup_ospf_base_service(router_name: str, router_id: str, area: str = "0") -> str:
    """Setup OSPF base service configuration (required: router_name, router_id; optional: area).
    
    Based on l-ospf-base service package YANG model.
    Essential parameters: router_name, router_id
    Optional parameters: area (defaults to "0")
    
    Args:
        router_name: Router device name (REQUIRED)
        router_id: OSPF Router ID in IPv4 format (REQUIRED, e.g., "1.1.1.1")
        area: OSPF Area ID (optional, defaults to "0")
        
    Returns:
        str: Configuration result message
    """
    try:
        logger.info(f"🔧 Setting up OSPF base service for {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Access ospf service (try both ospf.base and l-ospf-base.base)
        if hasattr(root, 'ospf') and hasattr(root.ospf, 'base'):
            # Use ospf service
            # Create service instance if it doesn't exist
            if router_name not in root.ospf.base:
                base_service = root.ospf.base.create(router_name)
            else:
                base_service = root.ospf.base[router_name]
        elif hasattr(root, 'l-ospf-base') and hasattr(getattr(root, 'l-ospf-base'), 'base'):
            # Fallback to l-ospf-base if ospf not available
            l_ospf_base = getattr(root, 'l-ospf-base')
            if router_name not in l_ospf_base.base:
                base_service = l_ospf_base.base.create(router_name)
            else:
                base_service = l_ospf_base.base[router_name]
        else:
            m.end_user_session()
            return f"❌ OSPF base service package not available (tried both ospf.base and l-ospf-base.base)"
        
        # Set router ID (required)
        base_service.router_id = router_id
        
        # Set area (optional, defaults to "0")
        base_service.area = area
        
        t.apply()
        m.end_user_session()
        
        result = f"""✅ OSPF base service configured for {router_name}:
  - Router ID: {router_id}
  - Area: {area}
  
Note: Use NSO CLI 'commit' to push to physical router"""
        
        logger.info(f"✅ OSPF base service configured for {router_name}")
        return result
            
    except Exception as e:
        logger.exception(f"❌ Error setting up OSPF base service: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"❌ Error setting up OSPF base service: {e}"

def setup_ospf_neighbor_service(
    router_name: str, 
    router_id: str,
    neighbor_device: str,
    local_interface: str,
    local_ip: str,
    remote_ip: str,
    area: str = "0",
    remote_interface: str = None
) -> str:
    """Setup OSPF neighbor service configuration.
    
    Based on ospf service package YANG model.
    Essential parameters: router_name, router_id, neighbor_device, local_interface, local_ip, remote_ip
    Optional parameters: area (defaults to "0"), remote_interface
    
    Args:
        router_name: Local router device name (REQUIRED)
        router_id: Local router ID in IPv4 format (REQUIRED, e.g., "1.1.1.1")
        neighbor_device: Neighbor router device name (REQUIRED)
        local_interface: Local interface name (REQUIRED, e.g., "GigabitEthernet/0/0/0/0" or "GigabitEthernet0/0/0/0")
        local_ip: Local interface IP address (REQUIRED, e.g., "192.168.1.1")
        remote_ip: Remote interface IP address (REQUIRED, e.g., "192.168.1.2")
        area: OSPF Area ID (optional, defaults to "0")
        remote_interface: Remote interface name (optional)
        
    Returns:
        str: Configuration result message
    """
    try:
        logger.info(f"🔧 Setting up OSPF neighbor service for {router_name}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Access ospf service - create base if it doesn't exist
        if hasattr(root, 'ospf') and hasattr(root.ospf, 'base'):
            # Create base service instance if it doesn't exist
            if router_name not in root.ospf.base:
                base_service = root.ospf.base.create(router_name)
                base_service.router_id = router_id
                base_service.area = area
            else:
                base_service = root.ospf.base[router_name]
            
            # Ensure router ID and area are set
            base_service.router_id = router_id
            base_service.area = area
            
            # Add neighbor - check if already exists
            if neighbor_device in base_service.neighbor:
                neighbor = base_service.neighbor[neighbor_device]
            else:
                neighbor = base_service.neighbor.create(neighbor_device)
            
            # Convert interface format from "GigabitEthernet/0/0/0/0" to "GigabitEthernet0/0/0/0"
            if '/' in local_interface:
                local_if_formatted = local_interface.replace('/', '', 1)
            else:
                local_if_formatted = local_interface
            
            if remote_interface and '/' in remote_interface:
                remote_if_formatted = remote_interface.replace('/', '', 1)
            elif remote_interface:
                remote_if_formatted = remote_interface
            else:
                remote_if_formatted = None
            
            neighbor.local_interface = local_if_formatted
            neighbor.local_ip = local_ip
            neighbor.remote_ip = remote_ip
            
            # Set remote interface if provided (optional)
            if remote_if_formatted:
                neighbor.remote_interface = remote_if_formatted
            
            t.apply()
            m.end_user_session()
            
            result = f"""✅ OSPF neighbor service configured for {router_name}:
  - Router ID: {router_id}
  - Area: {area}
  - Neighbor Device: {neighbor_device}
  - Local Interface: {local_interface} ({local_ip})
  - Remote IP: {remote_ip}
  {f"- Remote Interface: {remote_interface}" if remote_interface else ""}
  
Note: Use NSO CLI 'commit' to push to physical router"""
            
            logger.info(f"✅ OSPF neighbor service configured for {router_name}")
            return result
        else:
            m.end_user_session()
            return f"❌ OSPF service package not available"
            
    except Exception as e:
        logger.exception(f"❌ Error setting up OSPF neighbor service: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"❌ Error setting up OSPF neighbor service: {e}"

def remove_ospf_neighbor_service(router_name: str, neighbor_device: str, confirm: bool = False) -> str:
    """Remove OSPF neighbor service configuration.
    
    This function removes an OSPF neighbor relationship for a router.
    IMPORTANT: This requires confirm=True to prevent accidental deletions.
    
    Args:
        router_name: Router device name (REQUIRED)
        neighbor_device: Neighbor device name to remove (REQUIRED)
        confirm: Must be True to delete (REQUIRED for safety)
        
    Returns:
        str: Removal result message
        
    Example:
        # Remove OSPF neighbor
        remove_ospf_neighbor_service('xr9kv-1', 'xr9kv-2', confirm=True)
    """
    if not confirm:
        return "❌ ERROR: You must set confirm=True to delete OSPF neighbor service. This is required for safety."
    
    try:
        logger.info(f"🔧 Removing OSPF neighbor service for {router_name}, neighbor {neighbor_device}")
        
        m = maapi.Maapi()
        m.start_user_session('cisco', 'test_context_1')
        
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # Check if OSPF service exists
        if hasattr(root, 'ospf') and hasattr(root.ospf, 'base'):
            if router_name in root.ospf.base:
                ospf_service = root.ospf.base[router_name]
                
                # Check if neighbor exists
                if hasattr(ospf_service, 'neighbor') and neighbor_device in ospf_service.neighbor:
                    # Delete the neighbor using del
                    del ospf_service.neighbor[neighbor_device]
                    
                    t.apply()
                    m.end_user_session()
                    
                    result = f"""✅ Successfully removed OSPF neighbor service:
  - Router: {router_name}
  - Removed Neighbor: {neighbor_device}
  - Status: ✅ Removed from NSO service database
  - Note: Use NSO CLI 'commit' command to push to router"""
                    
                    logger.info(f"✅ Removed OSPF neighbor {neighbor_device} for {router_name}")
                    return result
                else:
                    m.end_user_session()
                    return f"ℹ️ Neighbor '{neighbor_device}' not found for {router_name}"
            else:
                m.end_user_session()
                return f"ℹ️ No OSPF service found for {router_name}"
        else:
            m.end_user_session()
            return f"❌ OSPF service package not available"
            
    except Exception as e:
        logger.exception(f"❌ Error removing OSPF neighbor service: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"❌ Error removing OSPF neighbor service: {e}"

# =============================================================================
# ROLLBACK TOOLS
# =============================================================================

def rollback_router_configuration(rollback_id: int = 0) -> str:
    """Rollback NSO configuration to a previous state.
    
    This function rolls back the NSO configuration to a specified rollback point.
    - rollback_id=0: Rolls back 1 step (most recent commit)
    - rollback_id=1: Rolls back 2 steps
    - rollback_id=n: Rolls back (n+1) steps
    
    Args:
        rollback_id: The rollback ID to restore to (defaults to 0 for most recent)
        
    Returns:
        str: Result message showing rollback status
        
    Examples:
        # Rollback to most recent commit (1 step)
        rollback_router_configuration(0)
        
        # Rollback 2 steps
        rollback_router_configuration(1)
    """
    try:
        logger.info(f"🔧 Rolling back configuration to rollback ID: {rollback_id}")
        
        # Use the proper NSO rollback API
        with maapi.single_write_trans('admin', 'python') as t:
            t.load_rollback(rollback_id)
            t.apply()
        
        result = f"""✅ Successfully rolled back configuration:
  - Rollback ID: {rollback_id}
  - Status: ✅ Applied to NSO configuration database
  - Note: This affects all devices in NSO
  - Previous configuration has been restored"""
        
        logger.info(f"✅ Rollback completed to rollback ID {rollback_id}")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error during rollback: {e}")
        return f"❌ Error during rollback to ID {rollback_id}: {e}"

def list_rollback_points() -> str:
    """List available rollback points in NSO.
    
    Returns:
        str: Detailed list of available rollback points
    """
    try:
        logger.info("🔧 Listing available rollback points...")
        
        m = maapi.Maapi()
        m.start_user_session('admin', 'python')
        t = m.start_read_trans()
        
        result_lines = ["Available NSO Rollback Points:"]
        result_lines.append("=" * 50)
        
        # Get rollback information from the root
        root = maagic.get_root(t)
        
        # NSO stores rollback information in /rollback-conf
        if hasattr(root, 'rollback_conf'):
            rollback_conf = root.rollback_conf
            # Get rollback list - typically stored as a list
            result_lines.append(f"\nRollback points are available for configuration restoration.")
            result_lines.append(f"Use rollback_router_configuration(rollback_id) to restore a point.")
        else:
            result_lines.append("\nRollback information structure not directly accessible via this API.")
        
        result_lines.append("\n💡 To see available rollbacks:")
        result_lines.append("  1. Use NSO CLI: ncs_cli -u admin")
        result_lines.append("  2. Type: show rollback")
        result_lines.append("\n📋 To perform rollback:")
        result_lines.append("  - Use rollback_router_configuration(rollback_id) function")
        result_lines.append("  - rollback_id=0: Most recent (1 step back)")
        result_lines.append("  - rollback_id=1: 2 steps back")
        result_lines.append("  - rollback_id=n: n+1 steps back")
        
        m.end_user_session()
        
        result = "\n".join(result_lines)
        logger.info("✅ Listed rollback information")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Error listing rollbacks: {e}")
        try:
            m.end_user_session()
        except:
            pass
        return f"Error listing rollbacks: {e}"

# =============================================================================
# REGISTER TOOLS WITH FastMCP
# =============================================================================

# OSPF Service Tools
mcp.tool(get_ospf_service_config)  # Get OSPF service configuration
mcp.tool(setup_ospf_base_service)  # Setup OSPF base service
mcp.tool(setup_ospf_neighbor_service)  # Setup OSPF neighbor service
mcp.tool(remove_ospf_neighbor_service)  # Remove OSPF neighbor service
mcp.tool(delete_ospf_service)  # Delete OSPF base service

# OSPF Service Tools - Old broken-up tools (commented out)
# mcp.tool(create_ospf_service)
# mcp.tool(update_ospf_service)
# mcp.tool(add_ospf_neighbor)
# mcp.tool(remove_ospf_neighbor)
# mcp.tool(list_ospf_neighbors)
# mcp.tool(get_ospf_service_status)

# NSO Runtime Service Tools
mcp.tool(get_BGP_GRP__BGP_GRP_config)
mcp.tool(create_BGP_GRP__BGP_GRP_service)
mcp.tool(delete_BGP_GRP__BGP_GRP_service)

# Interface Configuration Tools
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

# Rollback Tools
mcp.tool(rollback_router_configuration)
mcp.tool(list_rollback_points)

# Basic Tools
mcp.tool(show_all_devices)
mcp.tool(get_router_interfaces_config)
mcp.tool(configure_router_interface)
mcp.tool(echo_text)

if __name__ == "__main__":
    logger.info("🚀 Starting FastMCP NSO Auto-Generated Tools Server...")
    logger.info("✅ FastMCP NSO Auto-Generated Tools Server Ready!")
    
    # Run the FastMCP server
    mcp.run()
