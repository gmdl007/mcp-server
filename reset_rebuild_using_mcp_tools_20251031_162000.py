#!/usr/bin/env python3
"""
Reset and Rebuild Router Configuration Using Only MCP Tools

This script uses ONLY the existing MCP tools - no custom code!
"""

import sys
import os

# Set up environment
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add paths
sys.path.insert(0, '/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp')
sys.path.insert(0, f'{NSO_DIR}/src/ncs/pyapi')

# Import MCP tools directly
from fastmcp_nso_server_auto_generated import (
    delete_ospf_service,
    delete_ibgp_service,
    configure_router_interface,
    delete_router_subinterfaces,
    setup_ospf_base_service,
    setup_ospf_neighbor_service,
    setup_ibgp_service,
    show_all_devices
)

def main():
    print("="*70)
    print("Reset and Rebuild Using MCP Tools Only")
    print("="*70)
    print("\nTopology: xr9kv-1 <-> xr9kv-2 <-> xr9kv-3\n")
    
    routers = ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']
    
    # Step 1: Delete OSPF services
    print("\n" + "="*70)
    print("STEP 1: Delete OSPF Services")
    print("="*70)
    for router in routers:
        result = delete_ospf_service(router, confirm=True)
        print(result)
    
    # Step 2: Delete iBGP services
    print("\n" + "="*70)
    print("STEP 2: Delete iBGP Services")
    print("="*70)
    ibgp_services = ['peer1-2', 'peer2-3']
    for service in ibgp_services:
        try:
            result = delete_ibgp_service(service, confirm=True)
            print(result)
        except:
            print(f"  ⚠️  Service {service} may not exist")
    
    # Step 3: Delete all interfaces (including Loopback0)
    print("\n" + "="*70)
    print("STEP 3: Delete All Interfaces")
    print("="*70)
    
    # Delete sub-interfaces first
    result = delete_router_subinterfaces(router_name=None, confirm=True)
    print(result)
    
    # Delete Loopback0 on each router by deleting IP
    for router in routers:
        result = configure_router_interface(
            router_name=router,
            interface_name='Loopback/0',
            delete_ip=True
        )
        print(f"\n{router} Loopback0: {result}")
    
    # Step 4: Create Loopback0 interfaces
    print("\n" + "="*70)
    print("STEP 4: Create Loopback0 Interfaces")
    print("="*70)
    
    loopbacks = {
        'xr9kv-1': '1.1.1.1/32',
        'xr9kv-2': '2.2.2.2/32',
        'xr9kv-3': '3.3.3.3/32'
    }
    
    for router, ip in loopbacks.items():
        result = configure_router_interface(
            router_name=router,
            interface_name='Loopback/0',
            ip_address=ip
        )
        print(f"\n{router}: {result}")
    
    # Step 5: Create Physical Interfaces
    print("\n" + "="*70)
    print("STEP 5: Create Physical Interfaces")
    print("="*70)
    
    # Link 1: xr9kv-1 <-> xr9kv-2
    print("\nLink: xr9kv-1 <-> xr9kv-2")
    result = configure_router_interface(
        router_name='xr9kv-1',
        interface_name='GigabitEthernet/0/0/0/0',
        ip_address='192.168.12.1/24'
    )
    print(f"xr9kv-1 Gi0/0/0/0: {result}")
    
    result = configure_router_interface(
        router_name='xr9kv-2',
        interface_name='GigabitEthernet/0/0/0/0',
        ip_address='192.168.12.2/24'
    )
    print(f"xr9kv-2 Gi0/0/0/0: {result}")
    
    # Link 2: xr9kv-2 <-> xr9kv-3
    print("\nLink: xr9kv-2 <-> xr9kv-3")
    result = configure_router_interface(
        router_name='xr9kv-2',
        interface_name='GigabitEthernet/0/0/0/1',
        ip_address='192.168.23.1/24'
    )
    print(f"xr9kv-2 Gi0/0/0/1: {result}")
    
    result = configure_router_interface(
        router_name='xr9kv-3',
        interface_name='GigabitEthernet/0/0/0/0',
        ip_address='192.168.23.2/24'
    )
    print(f"xr9kv-3 Gi0/0/0/0: {result}")
    
    # Step 6: Create OSPF Base Services
    print("\n" + "="*70)
    print("STEP 6: Create OSPF Base Services")
    print("="*70)
    
    router_ids = {
        'xr9kv-1': '1.1.1.1',
        'xr9kv-2': '2.2.2.2',
        'xr9kv-3': '3.3.3.3'
    }
    
    for router, rid in router_ids.items():
        result = setup_ospf_base_service(router, rid, '0')
        print(f"\n{router}: {result}")
    
    # Step 7: Create OSPF Neighbor Links
    print("\n" + "="*70)
    print("STEP 7: Create OSPF Neighbor Links")
    print("="*70)
    
    # Link 1: xr9kv-1 <-> xr9kv-2
    print("\nLink: xr9kv-1 <-> xr9kv-2")
    result = setup_ospf_neighbor_service(
        router_name='xr9kv-1',
        router_id='1.1.1.1',
        neighbor_device='xr9kv-2',
        local_interface='0/0/0/0',
        local_ip='192.168.12.1',
        remote_ip='192.168.12.2',
        area='0'
    )
    print(f"xr9kv-1 -> xr9kv-2: {result}")
    
    result = setup_ospf_neighbor_service(
        router_name='xr9kv-2',
        router_id='2.2.2.2',
        neighbor_device='xr9kv-1',
        local_interface='0/0/0/0',
        local_ip='192.168.12.2',
        remote_ip='192.168.12.1',
        area='0'
    )
    print(f"xr9kv-2 -> xr9kv-1: {result}")
    
    # Link 2: xr9kv-2 <-> xr9kv-3
    print("\nLink: xr9kv-2 <-> xr9kv-3")
    result = setup_ospf_neighbor_service(
        router_name='xr9kv-2',
        router_id='2.2.2.2',
        neighbor_device='xr9kv-3',
        local_interface='0/0/0/1',
        local_ip='192.168.23.1',
        remote_ip='192.168.23.2',
        area='0'
    )
    print(f"xr9kv-2 -> xr9kv-3: {result}")
    
    result = setup_ospf_neighbor_service(
        router_name='xr9kv-3',
        router_id='3.3.3.3',
        neighbor_device='xr9kv-2',
        local_interface='0/0/0/0',
        local_ip='192.168.23.2',
        remote_ip='192.168.23.1',
        area='0'
    )
    print(f"xr9kv-3 -> xr9kv-2: {result}")
    
    # Step 8: Create iBGP Services
    print("\n" + "="*70)
    print("STEP 8: Create iBGP Services")
    print("="*70)
    
    # iBGP peer 1-2
    print("\nCreating iBGP: peer1-2 (xr9kv-1 <-> xr9kv-2)")
    result = setup_ibgp_service(
        router1='xr9kv-1',
        router1_lo0_ip='1.1.1.1',
        router1_router_id='1.1.1.1',
        router2='xr9kv-2',
        router2_lo0_ip='2.2.2.2',
        router2_router_id='2.2.2.2',
        as_number=65000,
        service_name='peer1-2'
    )
    print(result)
    
    # iBGP peer 2-3
    print("\nCreating iBGP: peer2-3 (xr9kv-2 <-> xr9kv-3)")
    result = setup_ibgp_service(
        router1='xr9kv-2',
        router1_lo0_ip='2.2.2.2',
        router1_router_id='2.2.2.2',
        router2='xr9kv-3',
        router2_lo0_ip='3.3.3.3',
        router2_router_id='3.3.3.3',
        as_number=65000,
        service_name='peer2-3'
    )
    print(result)
    
    print("\n" + "="*70)
    print("✅ REBUILD COMPLETE!")
    print("="*70)
    print("\nConfiguration Summary:")
    print("  ✅ Loopback0: 1.1.1.1, 2.2.2.2, 3.3.3.3")
    print("  ✅ Physical Links: xr9kv-1 Gi0/0/0/0 <-> xr9kv-2 Gi0/0/0/0 (192.168.12.0/24)")
    print("                     xr9kv-2 Gi0/0/0/1 <-> xr9kv-3 Gi0/0/0/0 (192.168.23.0/24)")
    print("  ✅ OSPF: All routers with Router IDs and neighbor links")
    print("  ✅ iBGP: peer1-2, peer2-3 (AS 65000)")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

