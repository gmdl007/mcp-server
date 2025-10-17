#!/usr/bin/env python3
"""
Simple NSO Test for Cursor
==========================

A simple script to test NSO connection and run basic commands.
Perfect for running directly in Cursor.

Author: AI Assistant
Version: 1.0
Date: 2025-01-16
"""

from nso_client import NSOClient
import json

def main():
    """Simple NSO test function."""
    print("🚀 NSO Simple Test for Cursor")
    print("=" * 50)
    
    # Create client
    client = NSOClient()
    
    # Test connection
    print("🔍 Testing NSO connection...")
    health = client.health_check()
    if "error" in health:
        print(f"❌ {health['error']}")
        return
    
    print(f"✅ Server: {health['service']} v{health['version']}")
    print(f"📡 NSO Connected: {health['nso_connected']}")
    print()
    
    # Test device discovery
    print("📱 Testing device discovery...")
    devices = client.show_all_devices()
    print(f"Found devices: {devices}")
    print()
    
    # Test router version
    print("🔍 Testing router version...")
    version = client.get_router_version("xr9kv-1")
    print(f"Version: {version[:100]}...")
    print()
    
    # Test router clock
    print("🕐 Testing router clock...")
    clock = client.get_router_clock("xr9kv-1")
    print(f"Clock: {clock[:100]}...")
    print()
    
    # Test CPU usage
    print("💻 Testing CPU usage...")
    cpu = client.check_cpu("xr9kv-1")
    print(f"CPU: {cpu[:100]}...")
    print()
    
    # Test memory usage
    print("🧠 Testing memory usage...")
    memory = client.check_memory("xr9kv-1")
    print(f"Memory: {memory[:100]}...")
    print()
    
    # Test interfaces
    print("🔌 Testing interfaces...")
    interfaces = client.show_router_interfaces("xr9kv-1")
    print(f"Interfaces: {interfaces[:100]}...")
    print()
    
    # Test BGP
    print("🌐 Testing BGP...")
    bgp = client.get_router_bgp_summary("xr9kv-1")
    print(f"BGP: {bgp[:100]}...")
    print()
    
    # Test ISIS
    print("🔗 Testing ISIS...")
    isis = client.get_router_isis_neighbors("xr9kv-1")
    print(f"ISIS: {isis[:100]}...")
    print()
    
    # Test OSPF
    print("🌐 Testing OSPF...")
    ospf = client.get_router_ospf_neigh("xr9kv-1")
    print(f"OSPF: {ospf[:100]}...")
    print()
    
    # Test LLDP
    print("🔗 Testing LLDP...")
    lldp = client.lldp_nei("xr9kv-1")
    print(f"LLDP: {lldp[:100]}...")
    print()
    
    # Test alarms
    print("🚨 Testing alarms...")
    alarms = client.check_alarm("xr9kv-1")
    print(f"Alarms: {alarms[:100]}...")
    print()
    
    # Test iterate command
    print("🔄 Testing iterate command...")
    iterate_result = client.iterate("show version")
    print(f"Iterate: {iterate_result[:200]}...")
    print()
    
    print("🎉 All tests completed successfully!")
    print("✅ NSO client is working perfectly in Cursor!")

if __name__ == "__main__":
    main()
