#!/usr/bin/env python3
"""
Enable CDP on ALL GigabitEthernet interfaces - one node at a time.
Created: 2025-11-19 21:43:00
"""

import ncs
import sys
from ncs.maapi import Maapi
from ncs.maagic import get_root

def enable_cdp_single_node(node_name):
    """Enable CDP on ALL GigabitEthernet interfaces for a single node."""
    
    all_gigabit_interfaces = [
        '0/0/0/0', '0/0/0/1', '0/0/0/2', '0/0/0/3',
        '0/0/0/4', '0/0/0/5', '0/0/0/6', '0/0/0/7',
        '0/0/0/8', '0/0/0/9', '0/0/0/10', '0/0/0/11'
    ]
    
    results = []
    
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = get_root(t)
        
        try:
            device = root.devices.device[node_name]
            cisco_config = device.config.cisco_ios_xr__interface
            
            node_count = 0
            for interface_id in all_gigabit_interfaces:
                try:
                    # Check if interface exists
                    if interface_id in cisco_config.GigabitEthernet:
                        interface = cisco_config.GigabitEthernet[interface_id]
                        
                        # Enable CDP on this interface
                        interface.cdp.create()
                        node_count += 1
                        results.append(f"  ✓ GigabitEthernet{interface_id} - CDP enabled")
                except Exception as e:
                    # Interface doesn't exist, skip it
                    pass
            
            results.append(f"\n✓ {node_name}: Enabled CDP on {node_count} GigabitEthernet interfaces")
            
        except Exception as e:
            results.append(f"✗ {node_name}: Error - {str(e)}")
            return "\n".join(results)
        
        # Commit changes
        t.apply()
        results.append(f"✓ {node_name}: Configuration committed to NSO")
    
    return "\n".join(results)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        node = sys.argv[1]
        result = enable_cdp_single_node(node)
        print(result)
    else:
        # Process all nodes
        nodes = ['node-1', 'node-2', 'node-3', 'node-4', 'node-5', 'node-6', 'node-7', 'node-8']
        for node in nodes:
            print(f"\n{'='*60}")
            print(f"Processing {node}")
            print('='*60)
            result = enable_cdp_single_node(node)
            print(result)

