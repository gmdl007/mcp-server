#!/usr/bin/env python3
"""
NSO Multi-Agent Network Management Script
=========================================

This script provides comprehensive network device management capabilities using Cisco NSO.
It includes functions for device discovery, configuration, monitoring, and automation.

Author: Generated from NSO_python_multi-agend.ipynb
Date: 2025
"""

import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic
import io
import sys
import re
import os
import logging
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NSOManager:
    """
    Main class for NSO network device management
    """
    
    def __init__(self, username: str = 'admin', context: str = 'test_context_1'):
        """
        Initialize NSO Manager
        
        Args:
            username (str): NSO username
            context (str): NSO context name
        """
        self.username = username
        self.context = context
        self.m = None
        self.t = None
        self.root = None
        self._initialize_nso()
    
    def _initialize_nso(self):
        """Initialize NSO connection"""
        try:
            self.m = maapi.Maapi()
            self.m.start_user_session(self.username, self.context)
            self.t = self.m.start_write_trans()
            self.root = maagic.get_root(self.t)
            logger.info("✅ NSO session initialized successfully!")
            logger.info(f"MAAPI session started with user: {self.username}")
            logger.info("Write transaction started")
            logger.info("Root object obtained")
        except Exception as e:
            logger.error(f"❌ Failed to initialize NSO: {e}")
            raise
    
    def finish_transaction(self):
        """Finish the current transaction"""
        if self.t:
            self.t.finish()
    
    def apply_transaction(self):
        """Apply the current transaction"""
        if self.t:
            self.t.apply()
            logger.info("✅ Transaction applied successfully!")

class DeviceManager(NSOManager):
    """
    Device management operations
    """
    
    def show_all_devices(self) -> List[str]:
        """
        Find out all available routers in the lab, return their names.
        
        Returns:
            List[str]: List of device names
        """
        try:
            if hasattr(self.root, 'devices') and hasattr(self.root.devices, 'device'):
                # Collect router names into a list
                router_names = [device.name for device in self.root.devices.device]
                
                # Print each router name
                logger.info("📱 Available devices:")
                for name in router_names:
                    logger.info(f"   - {name}")
                
                return router_names
            else:
                logger.warning("No devices found.")
                return []
        except Exception as e:
            logger.error(f"❌ Error getting device list: {e}")
            return []
    
    def execute_command_on_router(self, router_name: str, command: str) -> str:
        """
        Executes a single command on a specific router using NSO and returns the result.
        
        Args:
            router_name (str): The name of the router to execute the command on.
            command (str): The command to execute.
        
        Returns:
            str: The result of the command execution.
        """
        try:
            # Initialize a write transaction
            with ncs.maapi.single_write_trans(self.username, 'python', groups=['ncsadmin']) as t:
                root = ncs.maagic.get_root(t)
                
                # Locate the specific device
                device = root.devices.device[router_name]
                
                # Get the 'show' action object
                show = device.live_status.__getitem__('exec').any
                
                # Prepare the input for the command
                inp = show.get_input()
                inp.args = [command]
                
                # Execute the command and get the result
                r = show.request(inp)
                
                # Format the result and return
                result = f'Result of Show Command "{command}" for Router "{router_name}": {r.result}'
                logger.info(result)
                return result
                
        except KeyError:
            error_msg = f"Device '{router_name}' not found in NSO."
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Failed to execute command '{command}' on device '{router_name}': {e}"
            logger.error(error_msg)
            return error_msg
    
    def iterate_devices_and_cmd(self, cmd: str) -> List[str]:
        """
        Execute a single command on all devices in NSO and print the results.
        
        Args:
            cmd (str): The command to execute on each device.
        
        Returns:
            List[str]: A list of strings containing the results of the command execution.
        """
        results = []  # Initialize a list to store the results
        with ncs.maapi.single_write_trans(self.username, 'python', groups=['ncsadmin']) as t:
            root = ncs.maagic.get_root(t)
            for box in root.devices.device:
                try:
                    # Get the 'show' action object
                    show = box.live_status.__getitem__('exec').any
                    
                    # Prepare the input for the command
                    inp = show.get_input()
                    inp.args = [cmd]
                    
                    # Execute the command and get the result
                    r = show.request(inp)
                    
                    # Format the result and print it
                    show_cmd = f'Result of Show Command "{cmd}" for Router Name {box.name}: {r.result}'
                    logger.info(show_cmd)
                    
                    # Append the result to the list
                    results.append(show_cmd)
                    
                except Exception as e:
                    error_msg = f"Failed to execute command '{cmd}' on device {box.name}: {e}"
                    logger.error(error_msg)
                    results.append(error_msg)
        
        # Return the list of results after the loop completes
        return results

class RouterOperations(DeviceManager):
    """
    Router-specific operations and monitoring
    """
    
    def get_router_version(self, router_name: str) -> str:
        """
        Retrieves the router version using the 'show version' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The version information of the router.
        """
        command = "show version"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_clock(self, router_name: str) -> str:
        """
        Retrieves the router current time using the 'show clock' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The current time information of the router.
        """
        command = "show clock"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_lo0_ip(self, router_name: str) -> str:
        """
        Retrieves the router Loopback0 IP address using the 'show ip interface loopback0' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The Loopback0 IP address information of the router.
        """
        command = "show ip interface loopback0"
        return self.execute_command_on_router(router_name, command)
    
    def show_router_interfaces(self, router_name: str) -> str:
        """
        Retrieves the summary of router interface status using the 'show ipv4 interface brief' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The interface status information of the router.
        """
        command = "show ipv4 interface brief"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_ip_routes(self, router_name: str, prefix: str) -> str:
        """
        Retrieves a particular IPv4 route using the 'show route ipv4 <prefix>' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
            prefix (str): The IP prefix (e.g., "192.168.1.0/24") to look up in the routing table.
        
        Returns:
            str: The routing information for the specified prefix.
        """
        command = f"show route ipv4 {prefix}"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_bgp_summary(self, router_name: str) -> str:
        """
        Retrieves the BGP summary information using the 'show bgp ipv4 unicast summary' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The BGP summary information of the router.
        """
        command = "show bgp ipv4 unicast summary"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_isis_neighbors(self, router_name: str) -> str:
        """
        Retrieves the ISIS neighbors information using the 'show isis neighbors' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The ISIS neighbors information of the router.
        """
        command = "show isis neighbors"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_ospf_summary(self, router_name: str) -> str:
        """
        Retrieves the OSPF summary information using the 'show ospf vrf all-inclusive summary' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The OSPF summary information of the router.
        """
        command = "show ospf vrf all-inclusive summary"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_ospf_neigh(self, router_name: str) -> str:
        """
        Retrieves the OSPF neighbor information using the 'show ospf neighbor' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The OSPF neighbor information of the router.
        """
        command = "show ospf neighbor"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_control_plane_cpu(self, router_name: str) -> str:
        """
        Retrieves the router control plane CPU usage using the 'show processes cpu' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The control plane CPU usage information of the router.
        """
        command = "show processes cpu"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_memory_usage(self, router_name: str) -> str:
        """
        Retrieves the router memory usage using the 'show processes memory' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The memory usage information of the router.
        """
        command = "show processes memory"
        return self.execute_command_on_router(router_name, command)
    
    def ping_router(self, router_name: str, ip_address: str) -> str:
        """
        Pings an IP address using the 'ping' command on a router.
        
        Args:
            router_name (str): The name of the router to execute the command on.
            ip_address (str): The IP address to ping.
        
        Returns:
            str: The result of the ping command.
        """
        command = f"ping {ip_address} source Loopback 0"
        return self.execute_command_on_router(router_name, command)
    
    def traceroute_router(self, router_name: str, ip_address: str) -> str:
        """
        Performs a traceroute to a device using the 'traceroute' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
            ip_address (str): The IP address to traceroute.
        
        Returns:
            str: The result of the traceroute command.
        """
        command = f"traceroute {ip_address} source Loopback 0"
        return self.execute_command_on_router(router_name, command)
    
    def lldp_nei(self, router_name: str) -> str:
        """
        Find the connected neighbors with 'show lldp neighbor' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The result of the 'show lldp neighbor' command.
        """
        command = "show lldp neighbor"
        return self.execute_command_on_router(router_name, command)
    
    def mpls_lfib(self, router_name: str, prefix: Optional[str] = None) -> str:
        """
        Check the MPLS Label Forwarding Information Base (LFIB).
        
        Args:
            router_name (str): The name of the router to execute the command on.
            prefix (str, optional): The specific prefix to filter MPLS LFIB information.
        
        Returns:
            str: The result of the MPLS LFIB command execution.
        """
        if prefix:
            command = f"show mpls forwarding prefix {prefix}"
        else:
            command = "show mpls forwarding"
        
        return self.execute_command_on_router(router_name, command)

class MonitoringOperations(RouterOperations):
    """
    Monitoring and diagnostic operations
    """
    
    def get_router_logs(self, router_name: str, match_string: Optional[str] = None) -> str:
        """
        Retrieves router logs using the 'show logging last 50' command or filters by the specified string.
        
        Args:
            router_name (str): The name of the router to execute the command on.
            match_string (str, optional): The string to match within the logs.
        
        Returns:
            str: The filtered logs or the last 50 logs of the router.
        """
        if match_string:
            # If a match string is provided, retrieve the logs with string matching
            full_logs = self.execute_command_on_router(router_name, f"show logging | include {match_string}")
            
            if full_logs:
                result = f"Logs matching '{match_string}' on router '{router_name}':\n{full_logs}"
            else:
                result = f"No logs matching '{match_string}' found on router '{router_name}'."
        else:
            # If no match string is provided, retrieve the last 50 logs
            command = "show logging last 50"
            full_logs = self.execute_command_on_router(router_name, command)
            
            result = f"Last 50 logs on router '{router_name}':\n{full_logs}"
        
        return result
    
    def check_alarm(self, router_name: str) -> str:
        """
        Retrieves the router alarm information by using the 'show alarms brief' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The alarm information of the router.
        """
        command = "show alarms brief"
        return self.execute_command_on_router(router_name, command)
    
    def check_fans(self, router_name: str) -> str:
        """
        Retrieves the router fan information by using the 'admin show env fan | noprompts' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The fan information of the router from admin show output.
        """
        command = "admin show env fan | noprompts"
        return self.execute_command_on_router(router_name, command)
    
    def check_power(self, router_name: str) -> str:
        """
        Retrieves the router power related information by using the 'admin show env power | noprompts' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The power information of the router from admin show output.
        """
        command = "admin show env power | noprompts"
        return self.execute_command_on_router(router_name, command)
    
    def check_cpu(self, router_name: str) -> str:
        """
        Retrieves the router CPU utilization information by using the 'show processes cpu sorted 5min' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The CPU utilization information of the router.
        """
        command = "show processes cpu sorted 5min"
        return self.execute_command_on_router(router_name, command)
    
    def check_memory(self, router_name: str) -> str:
        """
        Retrieves the router memory summary information by using the 'show memory summary' command.
        
        Args:
            router_name (str): The name of the router to execute the command on.
        
        Returns:
            str: The memory summary information of the router.
        """
        command = "show memory summary"
        return self.execute_command_on_router(router_name, command)

class ConfigurationOperations(MonitoringOperations):
    """
    Configuration management operations
    """
    
    def configure_subinterface(self, device_name: str, subinterface_id: str, ip_address: str, subnet_mask: str) -> bool:
        """
        Configures a subinterface with specified parameters on a device or router
        
        Args:
            device_name (str): The name of the device to configure.
            subinterface_id (str): The subinterface identifier (e.g., '0/0/0/0.200').
            ip_address (str): The IPv4 address to assign to the subinterface.
            subnet_mask (str): The subnet mask for the IP address.
        
        Returns:
            bool: True if configuration was successful, False otherwise.
        """
        try:
            with ncs.maapi.single_write_trans(self.username, 'python') as t:
                root = ncs.maagic.get_root(t)
                device = root.devices.device[device_name]
                device.config.cisco_ios_xr__interface.GigabitEthernet_subinterface.GigabitEthernet.create(subinterface_id)
                subint = device.config.cisco_ios_xr__interface.GigabitEthernet_subinterface.GigabitEthernet[subinterface_id]
                subint.ipv4.address.ip = ip_address
                subint.ipv4.address.mask = subnet_mask
                t.apply()
            
            logger.info(f"✅ Successfully configured subinterface {subinterface_id} on {device_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to configure subinterface {subinterface_id} on {device_name}: {e}")
            return False
    
    def roll_back(self, steps: int = 0) -> bool:
        """
        Rolls back to a specified commit.
        
        Args:
            steps (int): The number of steps to roll back. Defaults to 0, 
                        which rolls back to the most recent commit.
        
        Returns:
            bool: True if rollback was successful, False otherwise.
        """
        try:
            import ncs.maapi as m  # Ensure the correct library is imported for transactions
            
            rollback_id = steps  # Use the input number as rollback ID (0 for the latest commit)
            with m.single_write_trans(self.username, 'python') as t:
                t.load_rollback(rollback_id)
                t.apply()
            
            logger.info(f"✅ Successfully rolled back {steps} steps")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to rollback {steps} steps: {e}")
            return False

class NetworkManager(ConfigurationOperations):
    """
    Main Network Manager class that combines all functionality
    """
    
    def __init__(self, username: str = 'admin', context: str = 'test_context_1'):
        """
        Initialize the Network Manager
        
        Args:
            username (str): NSO username
            context (str): NSO context name
        """
        super().__init__(username, context)
        self.devices = self.show_all_devices()
    
    def get_device_status(self, device_name: str) -> Dict[str, Any]:
        """
        Get comprehensive status information for a device
        
        Args:
            device_name (str): Name of the device
            
        Returns:
            Dict[str, Any]: Device status information
        """
        try:
            with ncs.maapi.single_read_trans(self.username, 'python') as t:
                root = ncs.maagic.get_root(t)
                device = root.devices.device[device_name]
                
                status = {
                    'name': device_name,
                    'oper_state': device.state.oper_state,
                    'error_tag': device.state.oper_state_error_tag,
                    'transaction_mode': device.state.transaction_mode,
                    'last_transaction_id': device.state.last_transaction_id,
                    'address': device.address,
                    'port': device.port,
                    'authgroup': device.authgroup
                }
                
                return status
                
        except Exception as e:
            logger.error(f"❌ Failed to get status for {device_name}: {e}")
            return {'name': device_name, 'error': str(e)}
    
    def get_all_device_status(self) -> List[Dict[str, Any]]:
        """
        Get status information for all devices
        
        Returns:
            List[Dict[str, Any]]: List of device status information
        """
        status_list = []
        for device_name in self.devices:
            status = self.get_device_status(device_name)
            status_list.append(status)
        return status_list
    
    def run_comprehensive_check(self, device_name: str) -> Dict[str, str]:
        """
        Run a comprehensive check on a device
        
        Args:
            device_name (str): Name of the device
            
        Returns:
            Dict[str, str]: Results of all checks
        """
        results = {}
        
        logger.info(f"🔍 Running comprehensive check on {device_name}")
        
        # Basic information
        results['version'] = self.get_router_version(device_name)
        results['clock'] = self.get_router_clock(device_name)
        results['interfaces'] = self.show_router_interfaces(device_name)
        
        # Monitoring
        results['alarms'] = self.check_alarm(device_name)
        results['cpu'] = self.check_cpu(device_name)
        results['memory'] = self.check_memory(device_name)
        
        # Network protocols
        results['bgp'] = self.get_router_bgp_summary(device_name)
        results['isis'] = self.get_router_isis_neighbors(device_name)
        results['ospf'] = self.get_router_ospf_summary(device_name)
        
        return results
    
    def run_all_device_checks(self) -> Dict[str, Dict[str, str]]:
        """
        Run comprehensive checks on all devices
        
        Returns:
            Dict[str, Dict[str, str]]: Results for all devices
        """
        all_results = {}
        
        for device_name in self.devices:
            logger.info(f"🔍 Running checks on {device_name}")
            all_results[device_name] = self.run_comprehensive_check(device_name)
        
        return all_results

def main():
    """
    Main function to demonstrate the Network Manager capabilities
    """
    print("🚀 NSO Multi-Agent Network Management Script")
    print("=" * 60)
    
    try:
        # Initialize the Network Manager
        nm = NetworkManager()
        
        # Show all devices
        print("\n📱 Available Devices:")
        devices = nm.show_all_devices()
        print(f"Found {len(devices)} devices: {', '.join(devices)}")
        
        # Get device status
        print("\n📊 Device Status:")
        status_list = nm.get_all_device_status()
        for status in status_list:
            print(f"  {status['name']}: {status['oper_state']} ({status['address']}:{status['port']})")
        
        # Run basic commands on all devices
        print("\n🔧 Running 'show version' on all devices:")
        results = nm.iterate_devices_and_cmd("show version")
        
        # Example: Run comprehensive check on first device
        if devices:
            print(f"\n🔍 Running comprehensive check on {devices[0]}:")
            check_results = nm.run_comprehensive_check(devices[0])
            print(f"✅ Completed comprehensive check on {devices[0]}")
            print(f"   - Version: {'✅' if 'NETSIM' in check_results['version'] else '❌'}")
            print(f"   - Interfaces: {'✅' if 'interface' in check_results['interfaces'].lower() else '❌'}")
        
        print("\n🎉 NSO Network Management Script completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error in main execution: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

