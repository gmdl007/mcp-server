#!/usr/bin/env python3
"""
NSO Client for Cursor Integration
=================================

A simple Python client to connect to the NSO HTTP server from Cursor.
This allows you to interact with your NSO network devices directly from Cursor.

Author: AI Assistant
Version: 1.0
Date: 2025-01-16
"""

import requests
import json
from typing import Dict, Any, List

class NSOClient:
    """Client to interact with NSO HTTP server."""
    
    def __init__(self, base_url: str = "http://localhost:5607"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the NSO server is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Health check failed: {e}"}
    
    def list_tools(self) -> Dict[str, Any]:
        """List all available NSO tools."""
        try:
            response = self.session.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to list tools: {e}"}
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific NSO tool."""
        try:
            response = self.session.post(
                f"{self.base_url}/tools/{tool_name}",
                json={"arguments": arguments},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to execute tool {tool_name}: {e}"}
    
    def show_all_devices(self) -> str:
        """Find all available routers."""
        result = self.execute_tool("show_all_devices", {})
        return result.get("result", "No devices found")
    
    def get_router_version(self, router_name: str) -> str:
        """Get router version."""
        result = self.execute_tool("get_router_version", {"router_name": router_name})
        return result.get("result", "Failed to get version")
    
    def get_router_clock(self, router_name: str) -> str:
        """Get router current time."""
        result = self.execute_tool("get_router_clock", {"router_name": router_name})
        return result.get("result", "Failed to get clock")
    
    def show_router_interfaces(self, router_name: str) -> str:
        """Show router interface status."""
        result = self.execute_tool("show_router_interfaces", {"router_name": router_name})
        return result.get("result", "Failed to get interfaces")
    
    def get_router_bgp_summary(self, router_name: str) -> str:
        """Get BGP summary."""
        result = self.execute_tool("get_router_bgp_summary", {"router_name": router_name})
        return result.get("result", "Failed to get BGP summary")
    
    def get_router_isis_neighbors(self, router_name: str) -> str:
        """Get ISIS neighbors."""
        result = self.execute_tool("get_router_isis_neighbors", {"router_name": router_name})
        return result.get("result", "Failed to get ISIS neighbors")
    
    def get_router_ospf_neigh(self, router_name: str) -> str:
        """Get OSPF neighbors."""
        result = self.execute_tool("get_router_ospf_neigh", {"router_name": router_name})
        return result.get("result", "Failed to get OSPF neighbors")
    
    def check_cpu(self, router_name: str) -> str:
        """Check CPU utilization."""
        result = self.execute_tool("check_cpu", {"router_name": router_name})
        return result.get("result", "Failed to check CPU")
    
    def check_memory(self, router_name: str) -> str:
        """Check memory usage."""
        result = self.execute_tool("check_memory", {"router_name": router_name})
        return result.get("result", "Failed to check memory")
    
    def ping_router(self, router_name: str, ip_address: str) -> str:
        """Ping from router."""
        result = self.execute_tool("ping_router", {
            "router_name": router_name,
            "ip_address": ip_address
        })
        return result.get("result", "Failed to ping")
    
    def traceroute_router(self, router_name: str, ip_address: str) -> str:
        """Traceroute from router."""
        result = self.execute_tool("traceroute_router", {
            "router_name": router_name,
            "ip_address": ip_address
        })
        return result.get("result", "Failed to traceroute")
    
    def lldp_nei(self, router_name: str) -> str:
        """Get LLDP neighbors."""
        result = self.execute_tool("lldp_nei", {"router_name": router_name})
        return result.get("result", "Failed to get LLDP neighbors")
    
    def check_alarm(self, router_name: str) -> str:
        """Check router alarms."""
        result = self.execute_tool("check_alarm", {"router_name": router_name})
        return result.get("result", "Failed to check alarms")
    
    def iterate(self, cmd: str) -> str:
        """Execute command on all devices."""
        result = self.execute_tool("iterate", {"cmd": cmd})
        return result.get("result", "Failed to iterate command")

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def main():
    """Example usage of the NSO client."""
    print("🚀 NSO Client Example")
    print("=" * 50)
    
    # Create client
    client = NSOClient()
    
    # Health check
    print("🔍 Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    print()
    
    # List tools
    print("📋 Available Tools:")
    tools = client.list_tools()
    if "tools" in tools:
        for i, tool in enumerate(tools["tools"], 1):
            print(f"  {i:2d}. {tool['name']}")
            print(f"      {tool['description']}")
    print()
    
    # Show all devices
    print("📱 All Devices:")
    devices = client.show_all_devices()
    print(f"  {devices}")
    print()
    
    # Get router version (using first device)
    if devices and devices != "No devices found":
        device_list = devices.split(', ')
        if device_list:
            first_device = device_list[0].strip()
            print(f"🔍 Router Version for {first_device}:")
            version = client.get_router_version(first_device)
            print(f"  {version}")
            print()
            
            print(f"🕐 Router Clock for {first_device}:")
            clock = client.get_router_clock(first_device)
            print(f"  {clock}")
            print()
            
            print(f"💻 CPU Usage for {first_device}:")
            cpu = client.check_cpu(first_device)
            print(f"  {cpu[:200]}...")  # Show first 200 chars
            print()

if __name__ == "__main__":
    main()
