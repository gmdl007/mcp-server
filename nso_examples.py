#!/usr/bin/env python3
"""
NSO Network Manager Usage Examples
=================================

This script demonstrates how to use the NSO Network Manager for various operations.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nso_network_manager import NetworkManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def example_basic_operations():
    """Example of basic NSO operations"""
    print("🔧 Example 1: Basic Operations")
    print("=" * 50)
    
    # Initialize Network Manager
    nm = NetworkManager()
    
    # Show all devices
    devices = nm.show_all_devices()
    print(f"Available devices: {devices}")
    
    # Execute command on specific device
    if devices:
        device = devices[0]
        print(f"\n📋 Getting version for {device}:")
        version = nm.get_router_version(device)
        print(version)
        
        print(f"\n🕐 Getting clock for {device}:")
        clock = nm.get_router_clock(device)
        print(clock)

def example_bulk_operations():
    """Example of bulk operations on all devices"""
    print("\n🔧 Example 2: Bulk Operations")
    print("=" * 50)
    
    nm = NetworkManager()
    
    # Run command on all devices
    print("📊 Running 'show version' on all devices:")
    results = nm.iterate_devices_and_cmd("show version")
    
    print(f"\n✅ Executed command on {len(results)} devices")

def example_monitoring():
    """Example of monitoring operations"""
    print("\n🔧 Example 3: Monitoring Operations")
    print("=" * 50)
    
    nm = NetworkManager()
    devices = nm.show_all_devices()
    
    if devices:
        device = devices[0]
        print(f"🔍 Monitoring {device}:")
        
        # Check alarms
        alarms = nm.check_alarm(device)
        print(f"Alarms: {alarms[:100]}..." if len(alarms) > 100 else f"Alarms: {alarms}")
        
        # Check CPU
        cpu = nm.check_cpu(device)
        print(f"CPU: {cpu[:100]}..." if len(cpu) > 100 else f"CPU: {cpu}")
        
        # Check memory
        memory = nm.check_memory(device)
        print(f"Memory: {memory[:100]}..." if len(memory) > 100 else f"Memory: {memory}")

def example_configuration():
    """Example of configuration operations"""
    print("\n🔧 Example 4: Configuration Operations")
    print("=" * 50)
    
    nm = NetworkManager()
    devices = nm.show_all_devices()
    
    if devices:
        device = devices[0]
        print(f"⚙️ Configuring subinterface on {device}:")
        
        # Configure a subinterface
        success = nm.configure_subinterface(
            device_name=device,
            subinterface_id="0/0/0/0.999",
            ip_address="192.168.99.1",
            subnet_mask="255.255.255.0"
        )
        
        if success:
            print("✅ Subinterface configured successfully!")
        else:
            print("❌ Failed to configure subinterface")

def example_device_status():
    """Example of device status checking"""
    print("\n🔧 Example 5: Device Status")
    print("=" * 50)
    
    nm = NetworkManager()
    
    # Get status for all devices
    status_list = nm.get_all_device_status()
    
    print("📊 Device Status Summary:")
    for status in status_list:
        print(f"  {status['name']}:")
        print(f"    State: {status['oper_state']}")
        print(f"    Address: {status['address']}:{status['port']}")
        print(f"    Auth Group: {status['authgroup']}")
        print()

def main():
    """Main function to run all examples"""
    print("🚀 NSO Network Manager Usage Examples")
    print("=" * 60)
    
    try:
        # Run all examples
        example_basic_operations()
        example_bulk_operations()
        example_monitoring()
        example_configuration()
        example_device_status()
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

