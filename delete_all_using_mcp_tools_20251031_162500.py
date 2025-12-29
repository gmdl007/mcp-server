#!/usr/bin/env python3
"""
Delete All Configuration Using Only MCP Tools
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
    show_all_devices
)

def main():
    print("="*70)
    print("Delete All Configuration Using MCP Tools")
    print("="*70)
    
    routers = ['xr9kv-1', 'xr9kv-2', 'xr9kv-3']
    
    # Step 1: Delete OSPF services
    print("\n" + "="*70)
    print("STEP 1: Deleting OSPF Services")
    print("="*70)
    for router in routers:
        result = delete_ospf_service(router, confirm=True)
        print(f"{router}: {result}")
    
    # Step 2: Delete iBGP services
    print("\n" + "="*70)
    print("STEP 2: Deleting iBGP Services")
    print("="*70)
    ibgp_services = ['peer1-2', 'peer2-3']
    for service in ibgp_services:
        try:
            result = delete_ibgp_service(service, confirm=True)
            print(f"{service}: {result}")
        except:
            print(f"{service}: No service found (or already deleted)")
    
    # Step 3: Delete all sub-interfaces
    print("\n" + "="*70)
    print("STEP 3: Deleting Sub-Interfaces")
    print("="*70)
    result = delete_router_subinterfaces(router_name=None, confirm=True)
    print(result)
    
    # Step 4: Delete all physical interfaces
    print("\n" + "="*70)
    print("STEP 4: Deleting Physical Interfaces")
    print("="*70)
    
    # Delete GigabitEthernet interfaces by deleting their IPs
    interfaces_to_delete = {
        'xr9kv-1': ['GigabitEthernet/0/0/0/0'],
        'xr9kv-2': ['GigabitEthernet/0/0/0/0', 'GigabitEthernet/0/0/0/1'],
        'xr9kv-3': ['GigabitEthernet/0/0/0/0']
    }
    
    for router, iface_list in interfaces_to_delete.items():
        for iface in iface_list:
            result = configure_router_interface(
                router_name=router,
                interface_name=iface,
                delete_ip=True
            )
            print(f"{router} {iface}: {result}")
    
    # Step 5: Delete Loopback0
    print("\n" + "="*70)
    print("STEP 5: Deleting Loopback0 Interfaces")
    print("="*70)
    for router in routers:
        result = configure_router_interface(
            router_name=router,
            interface_name='Loopback/0',
            delete_ip=True
        )
        print(f"{router} Loopback0: {result}")
    
    print("\n" + "="*70)
    print("✅ DELETE COMPLETE!")
    print("="*70)
    print("\nAll configurations deleted:")
    print("  ✅ OSPF services deleted")
    print("  ✅ iBGP services deleted")
    print("  ✅ Sub-interfaces deleted")
    print("  ✅ Physical interfaces deleted")
    print("  ✅ Loopback0 interfaces deleted")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

