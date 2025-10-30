"""
Simplified OSPF Service Tools

Based on NSO OSPF service packages, there are two main services:
1. OSPF Base Service: Basic OSPF configuration (Router ID, Area)
2. OSPF Neighbor Service: Manage OSPF neighbors

Essential OSPF Information Required:
- Router ID (required for base service)
- Area (optional, defaults to 0 for base service)
- Neighbor IP (required for neighbor service)
- Neighbor Area (optional, defaults to same as router's area)

For the simplified approach, I'll create 2 comprehensive service tools:
1. setup_ospf_base - Setup basic OSPF configuration with all required info at once
2. setup_ospf_neighbor - Setup OSPF neighborship with all required info at once
"""
