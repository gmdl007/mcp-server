#!/usr/bin/env python3
"""
NSO Interactive Client for Cursor
=================================

An interactive Python client to connect to the NSO HTTP server.
Use this directly in Cursor to interact with your NSO network devices.

Author: AI Assistant
Version: 1.0
Date: 2025-01-16
"""

from nso_client import NSOClient
import json

def interactive_nso_client():
    """Interactive NSO client for Cursor."""
    print("🚀 NSO Interactive Client")
    print("=" * 50)
    
    # Create client
    client = NSOClient()
    
    # Health check
    health = client.health_check()
    if "error" in health:
        print(f"❌ {health['error']}")
        return
    
    print(f"✅ Connected to NSO server: {health['service']} v{health['version']}")
    print(f"📡 NSO Connected: {health['nso_connected']}")
    print()
    
    # Show available devices
    devices = client.show_all_devices()
    print(f"📱 Available Devices: {devices}")
    print()
    
    # Interactive menu
    while True:
        print("🔧 Available Commands:")
        print("  1. Show all devices")
        print("  2. Get router version")
        print("  3. Get router clock")
        print("  4. Show router interfaces")
        print("  5. Check CPU usage")
        print("  6. Check memory usage")
        print("  7. Get BGP summary")
        print("  8. Get ISIS neighbors")
        print("  9. Get OSPF neighbors")
        print("  10. Ping from router")
        print("  11. Traceroute from router")
        print("  12. Get LLDP neighbors")
        print("  13. Check alarms")
        print("  14. Execute command on all devices")
        print("  15. List all tools")
        print("  0. Exit")
        print()
        
        try:
            choice = input("Enter your choice (0-15): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                devices = client.show_all_devices()
                print(f"📱 Devices: {devices}")
            elif choice == "2":
                router = input("Enter router name: ").strip()
                version = client.get_router_version(router)
                print(f"🔍 Version: {version}")
            elif choice == "3":
                router = input("Enter router name: ").strip()
                clock = client.get_router_clock(router)
                print(f"🕐 Clock: {clock}")
            elif choice == "4":
                router = input("Enter router name: ").strip()
                interfaces = client.show_router_interfaces(router)
                print(f"🔌 Interfaces: {interfaces}")
            elif choice == "5":
                router = input("Enter router name: ").strip()
                cpu = client.check_cpu(router)
                print(f"💻 CPU: {cpu}")
            elif choice == "6":
                router = input("Enter router name: ").strip()
                memory = client.check_memory(router)
                print(f"🧠 Memory: {memory}")
            elif choice == "7":
                router = input("Enter router name: ").strip()
                bgp = client.get_router_bgp_summary(router)
                print(f"🌐 BGP: {bgp}")
            elif choice == "8":
                router = input("Enter router name: ").strip()
                isis = client.get_router_isis_neighbors(router)
                print(f"🔗 ISIS: {isis}")
            elif choice == "9":
                router = input("Enter router name: ").strip()
                ospf = client.get_router_ospf_neigh(router)
                print(f"🌐 OSPF: {ospf}")
            elif choice == "10":
                router = input("Enter router name: ").strip()
                ip = input("Enter IP address to ping: ").strip()
                ping_result = client.ping_router(router, ip)
                print(f"🏓 Ping: {ping_result}")
            elif choice == "11":
                router = input("Enter router name: ").strip()
                ip = input("Enter IP address to traceroute: ").strip()
                trace_result = client.traceroute_router(router, ip)
                print(f"🛤️  Traceroute: {trace_result}")
            elif choice == "12":
                router = input("Enter router name: ").strip()
                lldp = client.lldp_nei(router)
                print(f"🔗 LLDP: {lldp}")
            elif choice == "13":
                router = input("Enter router name: ").strip()
                alarms = client.check_alarm(router)
                print(f"🚨 Alarms: {alarms}")
            elif choice == "14":
                cmd = input("Enter command to execute on all devices: ").strip()
                result = client.iterate(cmd)
                print(f"🔄 Result: {result}")
            elif choice == "15":
                tools = client.list_tools()
                if "tools" in tools:
                    print("📋 Available Tools:")
                    for i, tool in enumerate(tools["tools"], 1):
                        print(f"  {i:2d}. {tool['name']}")
                        print(f"      {tool['description']}")
                else:
                    print("❌ Failed to list tools")
            else:
                print("❌ Invalid choice. Please try again.")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()

if __name__ == "__main__":
    interactive_nso_client()
