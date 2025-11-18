# Routing Information Summary - All Nodes

**Generated:** 2025-11-17  
**Nodes:** node-1 through node-8, pce-11, node-9

## Overview

This document summarizes all routing information that can be retrieved using MCP tools for the dCloud lab routers.

## Available MCP Routing Tools

### 1. **get_routing_table(router_name, protocol=None, prefix=None)**
   - Retrieves routing table information
   - Can filter by protocol (isis, bgp, static, etc.)
   - Can filter by prefix
   - **Status:** ✅ Working

### 2. **get_route_details(router_name, prefix)**
   - Gets detailed information for a specific route prefix
   - Shows next-hops, metrics, protocols, etc.
   - **Status:** ✅ Working

### 3. **get_bgp_neighbor_status(router_name)**
   - Shows BGP neighbor adjacency status
   - **Status:** ⚠️ Limited (works but BGP is configured for VPNv4/VPNv6/BGP-LS, not IPv4 unicast)

### 4. **get_ospf_neighbor_status(router_name)**
   - Shows OSPF neighbor adjacency status
   - **Status:** ✅ Working (but OSPF not configured on these nodes)

### 5. **execute_device_command(router_name, command)**
   - Can execute any show command for routing information
   - Examples: `show route summary`, `show isis database`, `show bgp all summary`, etc.
   - **Status:** ✅ Working

## Routing Protocol Summary

### IS-IS (Intermediate System to Intermediate System)
- **Status:** ✅ Active on all nodes
- **Level:** Level-2 (L2)
- **Neighbors:** All UP and IETF-NSF Capable
- **Routes:** ~150-152 IS-IS routes per node
- **Topology:** Fully connected mesh

### BGP (Border Gateway Protocol)
- **Status:** ✅ Active on most nodes
- **AS Number:** 65000 (iBGP)
- **Address Families:**
  - VPNv4 Unicast
  - VPNv6 Unicast
  - BGP-LS (Link-state)
- **Topology:** Route Reflector (pce-11) with clients (node-1 through node-9)
- **Note:** BGP is NOT configured for IPv4 unicast, only for VPN services

### OSPF (Open Shortest Path First)
- **Status:** ❌ Not configured on dCloud nodes
- **Note:** OSPF is only configured on netsim devices (xr9kv-1, xr9kv-2, xr9kv-3)

### Static Routes
- **Status:** ✅ Configured on all nodes
- **Count:** ~17-19 static routes per node

## Route Summary Statistics (from `show route summary`)

### node-1
- **Total Routes:** 182
- **IS-IS Routes:** 152
- **Static Routes:** 17
- **Connected Routes:** 5
- **Local Routes:** 7
- **Backup Routes:** 7

### node-2
- **Total Routes:** 183
- **IS-IS Routes:** 151
- **Static Routes:** 17
- **Connected Routes:** 6
- **Local Routes:** 8
- **Backup Routes:** 8

### node-3
- **Total Routes:** 182
- **IS-IS Routes:** 152
- **Static Routes:** 17
- **Connected Routes:** 5
- **Local Routes:** 7
- **Backup Routes:** 7

### node-4
- **Total Routes:** 183
- **IS-IS Routes:** 151
- **Static Routes:** 17
- **Connected Routes:** 6
- **Local Routes:** 8
- **Backup Routes:** 8

### node-5
- **Total Routes:** 183
- **IS-IS Routes:** 149
- **Static Routes:** 17
- **Connected Routes:** 7
- **Local Routes:** 9
- **Backup Routes:** 10

### node-6
- **Total Routes:** 182
- **IS-IS Routes:** 150
- **Static Routes:** 17
- **Connected Routes:** 6
- **Local Routes:** 8
- **Backup Routes:** 9

### node-7
- **Total Routes:** 183
- **IS-IS Routes:** 149
- **Static Routes:** 17
- **Connected Routes:** 7
- **Local Routes:** 9
- **Backup Routes:** 10

### node-8
- **Total Routes:** 183
- **IS-IS Routes:** 147
- **Static Routes:** 19
- **Connected Routes:** 7
- **Local Routes:** 9
- **Backup Routes:** 9

## IPv6 Routing

### node-1 IPv6 Summary
- **Total IPv6 Routes:** 57
- **IS-IS IPv6 Routes:** 38
- **Connected IPv6 Routes:** 3
- **Local IPv6 Routes:** 5
- **SRv6 Locators:** Configured

## MPLS Forwarding

### node-1 MPLS Summary
- **Label Switching Entries:** 198
- **Protected Entries:** 182 (Ready: 182, Active: 0)
- **SRGB Range:** 16000 - 23999
- **SRLB Range:** 15000 - 15999
- **LDP Neighbors:** 2 (node-2, node-6)

## IS-IS Database Information

### IS-IS LSPs (Link State Packets)
- **Total Level-2 LSPs:** 15 (on node-1)
- **Local Level-2 LSPs:** 1 per node
- **LSP Holdtime:** ~600-1200 seconds
- **All LSPs:** Synchronized across all nodes

### IS-IS Features
- **Area Address:** 49
- **NLPID:** IPv4 (0xcc), IPv6 (0x8e)
- **Multi-Topology:** IPv4 Unicast, IPv6 Unicast
- **Segment Routing:** SRv6 Locators configured
- **Router Capabilities:** All nodes support IETF-NSF

## BGP Neighbor Information

### Route Reflector: pce-11 (198.19.2.11)
- **Cluster ID:** Configured
- **Clients:** node-1, node-2, node-3, node-4, node-6, node-8, node-9
- **Address Families:** VPNv4, VPNv6, BGP-LS

### BGP VPNv4 Summary (node-1 example)
- **BGP Router ID:** 198.19.1.1
- **Local AS:** 65000
- **BGP Mode:** STANDALONE
- **Neighbor:** 198.19.2.11 (pce-11)
- **Up Time:** 23:15:45
- **Messages:** 1398 sent/rcvd
- **Prefixes Received:** 0 (Route Reflector may not advertise prefixes to clients)

## Useful Show Commands Available via MCP

### Routing Table Commands
- `show route` - Full routing table
- `show route summary` - Route summary statistics
- `show route protocol isis` - IS-IS routes only
- `show route protocol bgp` - BGP routes only
- `show route protocol static` - Static routes only
- `show route protocol connected` - Connected routes only
- `show route protocol local` - Local routes only
- `show route ipv6` - IPv6 routing table
- `show route ipv6 summary` - IPv6 route summary
- `show route longer-prefixes <prefix>` - Routes matching prefix
- `show route <prefix>` - Specific route details

### IS-IS Commands
- `show isis neighbors` - IS-IS neighbor status
- `show isis database` - IS-IS link state database
- `show isis database detail` - Detailed IS-IS database
- `show isis topology` - IS-IS topology

### BGP Commands
- `show bgp vpnv4 unicast summary` - VPNv4 summary (✅ Works)
- `show bgp vpnv6 unicast summary` - VPNv6 summary
- `show bgp link-state summary` - BGP-LS summary
- `show bgp neighbors` - BGP neighbor details
- `show bgp summary` - IPv4 unicast summary (⚠️ Not configured - shows error)
- `show bgp all summary` - All address families (⚠️ Syntax error on IOS XR)

### MPLS Commands
- `show mpls forwarding` - MPLS forwarding table
- `show mpls forwarding summary` - MPLS forwarding summary
- `show mpls ldp neighbor` - LDP neighbor information
- `show mpls ldp discovery` - LDP discovery information

### Other Useful Commands
- `show cef summary` - CEF (Cisco Express Forwarding) summary
- `show rib client` - RIB (Routing Information Base) client information

## Route Prefix Examples

### Loopback Addresses (198.19.1.x/32)
- All nodes have loopback addresses in 198.19.1.0/24
- Learned via IS-IS

### Interface Networks (10.x.x.0/24)
- Point-to-point links between nodes
- Learned via IS-IS

### Service Networks
- Multiple service networks (11.11.x.0/24, 13.127.x.0/24, etc.)
- Learned via IS-IS

## Notes

1. **BGP Configuration:** BGP is configured for VPN services (VPNv4/VPNv6) and BGP-LS, not for IPv4 unicast routing. This is why `get_bgp_neighbor_status` may show limited information when checking for IPv4 unicast neighbors.

2. **IS-IS is Primary IGP:** IS-IS is the primary Interior Gateway Protocol (IGP) for IPv4 and IPv6 routing.

3. **MPLS/Segment Routing:** All nodes support MPLS and Segment Routing (SRv6).

4. **Route Reflector:** pce-11 acts as a Route Reflector for BGP VPN services.

5. **Topology:** The network forms a fully connected IS-IS topology with all neighbors UP.

## MCP Tool Usage Examples

```python
# Get full routing table
get_routing_table('node-1')

# Get IS-IS routes only
get_routing_table('node-1', protocol='isis')

# Get BGP routes only
get_routing_table('node-1', protocol='bgp')

# Get routes for specific prefix
get_routing_table('node-1', prefix='198.19.1.0/24')

# Get detailed route information
get_route_details('node-1', '198.19.1.1/32')

# Get BGP neighbor status
get_bgp_neighbor_status('node-1')

# Get IS-IS neighbor status
get_ospf_neighbor_status('node-1')  # Note: OSPF not configured, but tool works

# Execute custom show commands
execute_device_command('node-1', 'show route summary')
execute_device_command('node-1', 'show isis database detail')
execute_device_command('node-1', 'show bgp vpnv4 unicast summary')  # Correct syntax
execute_device_command('node-1', 'show mpls forwarding summary')
execute_device_command('node-1', 'show route isis')  # IS-IS routes
```

## Conclusion

The MCP tools provide comprehensive access to routing information including:
- Full routing tables with protocol filtering
- Detailed route information
- Protocol-specific neighbor status (BGP, OSPF)
- IS-IS database and topology information
- MPLS forwarding information
- Custom show commands for any routing-related information

All routing information is accessible via the MCP tools, making it easy to monitor and troubleshoot the network routing state.

