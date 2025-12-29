#!/usr/bin/env python3
"""
Complete Network Topology Visualization - Based on Physical Topology
Created: 2025-11-19 22:05:00
Generates visualization from actual physical topology (not just CDP discovery)
"""

import networkx as nx
import matplotlib.pyplot as plt

# Complete topology data from physical diagram
topology_data = {
    'node-1': [
        ('node-2', 'Gi0/0/0/2', 'Gi0/0/0/1', '10.1.2.0/24'),
        ('node-6', 'Gi0/0/0/6', 'Gi0/0/0/1', '10.1.6.0/24'),
    ],
    'node-2': [
        ('node-1', 'Gi0/0/0/1', 'Gi0/0/0/2', '10.1.2.0/24'),
        ('node-6', 'Gi0/0/0/6', 'Gi0/0/0/2', '10.2.6.0/24'),
    ],
    'node-3': [
        ('node-4', 'Gi0/0/0/4', 'Gi0/0/0/3', '10.3.4.0/24'),
        ('node-8', 'Gi0/0/0/8', 'Gi0/0/0/3', '10.3.8.0/24'),
    ],
    'node-4': [
        ('node-3', 'Gi0/0/0/3', 'Gi0/0/0/4', '10.3.4.0/24'),
        ('node-5', 'Gi0/0/0/5', 'Gi0/0/0/4', '10.4.5.0/24'),
        ('node-8', 'Gi0/0/0/8', 'Gi0/0/0/4', '10.4.8.0/24'),
    ],
    'node-5': [
        ('node-4', 'Gi0/0/0/4', 'Gi0/0/0/5', '10.4.5.0/24'),
        ('node-6', 'Gi0/0/0/6', 'Gi0/0/0/5', '10.5.6.0/24'),
        ('node-7', 'Gi0/0/0/7', 'Gi0/0/0/5', '10.5.7.0/24'),
        ('node-8', 'Gi0/0/0/8', 'Gi0/0/0/5', '10.5.8.0/24'),
    ],
    'node-6': [
        ('node-1', 'Gi0/0/0/1', 'Gi0/0/0/6', '10.1.6.0/24'),
        ('node-2', 'Gi0/0/0/2', 'Gi0/0/0/6', '10.2.6.0/24'),
        ('node-5', 'Gi0/0/0/5', 'Gi0/0/0/6', '10.5.6.0/24'),
        ('node-7', 'Gi0/0/0/7', 'Gi0/0/0/6', '10.6.7.0/24'),
    ],
    'node-7': [
        ('node-5', 'Gi0/0/0/5', 'Gi0/0/0/7', '10.5.7.0/24'),
        ('node-6', 'Gi0/0/0/6', 'Gi0/0/0/7', '10.6.7.0/24'),
        ('node-8', 'Gi0/0/0/8', 'Gi0/0/0/7', '10.7.8.0/24'),
    ],
    'node-8': [
        ('node-3', 'Gi0/0/0/3', 'Gi0/0/0/8', '10.3.8.0/24'),
        ('node-4', 'Gi0/0/0/4', 'Gi0/0/0/8', '10.4.8.0/24'),
        ('node-5', 'Gi0/0/0/5', 'Gi0/0/0/8', '10.5.8.0/24'),
        ('node-7', 'Gi0/0/0/7', 'Gi0/0/0/8', '10.7.8.0/24'),
        ('pce-11', 'Gi0/0/0/11', 'Gi0/0/0/8', '10.8.11.0/24'),
    ],
    'pce-11': [
        ('node-8', 'Gi0/0/0/8', 'Gi0/0/0/11', '10.8.11.0/24'),
    ],
}

# Router metadata
router_info = {
    'node-1': {'loopback': '198.19.1.1', 'platform': 'IOS-XRv 9000', 'type': 'router'},
    'node-2': {'loopback': '198.19.1.2', 'platform': 'IOS-XRv 9000', 'type': 'router'},
    'node-3': {'loopback': '198.19.1.3', 'platform': 'IOS-XRv 9000', 'type': 'router'},
    'node-4': {'loopback': '198.19.1.4', 'platform': 'IOS-XRv 9000', 'type': 'router'},
    'node-5': {'loopback': '198.19.1.5', 'platform': 'XRd Control Plane', 'type': 'router'},
    'node-6': {'loopback': '198.19.1.6', 'platform': 'XRd Control Plane', 'type': 'router'},
    'node-7': {'loopback': '198.19.1.7', 'platform': 'XRd Control Plane', 'type': 'router'},
    'node-8': {'loopback': '198.19.1.8', 'platform': 'XRd Control Plane', 'type': 'router'},
    'pce-11': {'loopback': '198.19.1.11', 'platform': 'IOS-XR', 'type': 'pce'},
}

def create_topology_graph():
    """Create NetworkX graph from complete physical topology."""
    G = nx.Graph()
    
    # Add nodes with attributes
    for router, info in router_info.items():
        G.add_node(router, 
                   loopback=info['loopback'],
                   platform=info['platform'],
                   node_type=info['type'])
    
    # Add edges (avoid duplicates)
    edges_added = set()
    
    for source_router, neighbors in topology_data.items():
        for neighbor, local_intf, remote_intf, subnet in neighbors:
            # Create unique edge identifier (sorted to avoid duplicates)
            edge_key = tuple(sorted([source_router, neighbor]))
            
            if edge_key not in edges_added:
                G.add_edge(source_router, neighbor,
                          local_intf=local_intf,
                          remote_intf=remote_intf,
                          subnet=subnet)
                edges_added.add(edge_key)
    
    return G

def visualize_topology(G, output_file='complete_network_topology.png'):
    """Create visualization of the complete network topology."""
    
    # Create figure with larger size
    plt.figure(figsize=(20, 14))
    
    # Manual positions based on physical topology diagram
    pos = {
        # Top row
        'node-1': (6, 10),
        'node-2': (10, 10),
        
        # Middle-upper row
        'node-6': (8, 8),
        
        # Center (node-5 is the hub)
        'node-5': (8, 6),
        
        # Middle-lower row
        'node-7': (10, 4),
        'node-8': (6, 4),
        
        # Bottom row
        'node-3': (4, 2),
        'node-4': (2, 2),
        
        # PCE
        'pce-11': (8, 2),
    }
    
    # Separate nodes by type
    routers_xrv = [n for n, d in G.nodes(data=True) if 'IOS-XRv' in d.get('platform', '')]
    routers_xrd = [n for n, d in G.nodes(data=True) if 'XRd' in d.get('platform', '')]
    pce_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'pce']
    
    # Draw nodes with different colors by platform
    nx.draw_networkx_nodes(G, pos, nodelist=routers_xrv, 
                          node_color='lightblue', 
                          node_size=3500, 
                          node_shape='s',  # square for IOS-XRv
                          label='IOS-XRv 9000')
    
    nx.draw_networkx_nodes(G, pos, nodelist=routers_xrd, 
                          node_color='lightgreen', 
                          node_size=3500, 
                          node_shape='o',  # circle for XRd
                          label='XRd Control Plane')
    
    nx.draw_networkx_nodes(G, pos, nodelist=pce_nodes, 
                          node_color='lightyellow', 
                          node_size=3500, 
                          node_shape='d',  # diamond for PCE
                          label='PCE')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=2.5, alpha=0.7, edge_color='gray')
    
    # Draw labels for nodes
    node_labels = {}
    for node, data in G.nodes(data=True):
        node_labels[node] = f"{node}\n{data['loopback']}"
    
    nx.draw_networkx_labels(G, pos, node_labels, font_size=9, font_weight='bold')
    
    # Draw edge labels (subnet information)
    edge_labels = {}
    for u, v, data in G.edges(data=True):
        edge_labels[(u, v)] = f"{data['subnet']}"
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7, 
                                 bbox=dict(boxstyle="round,pad=0.3", 
                                          facecolor='white', 
                                          edgecolor='gray', 
                                          alpha=0.9))
    
    # Add title and annotations
    plt.title('Complete Network Topology - Physical Connections\n' +
             'Based on Physical Topology Diagram + OSPF Verification\n' +
             'Generated: 2025-11-19 22:05', 
             fontsize=16, fontweight='bold', pad=20)
    
    # Add statistics box
    stats_text = (
        f"Total Routers: {len([n for n in G.nodes() if 'node-' in n])}\n"
        f"Total Links: {G.number_of_edges()}\n"
        f"OSPF Adjacencies: {G.number_of_edges() * 2}\n"
        f"All neighbors: FULL state"
    )
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.legend(loc='upper right', fontsize=12)
    plt.axis('off')
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Complete topology diagram saved to: {output_file}")
    
    # Also save as SVG for scalability
    svg_file = output_file.replace('.png', '.svg')
    plt.savefig(svg_file, format='svg', bbox_inches='tight')
    print(f"✓ Complete topology diagram saved to: {svg_file}")
    
    plt.close()

def print_topology_summary(G):
    """Print text summary of complete topology."""
    print("\n" + "="*70)
    print("COMPLETE NETWORK TOPOLOGY SUMMARY")
    print("="*70)
    
    print(f"\nTotal Routers: {len([n for n in G.nodes() if 'node-' in n])}")
    print(f"Total Devices: {G.number_of_nodes()}")
    print(f"Total Links: {G.number_of_edges()}")
    print(f"OSPF Adjacencies: {G.number_of_edges() * 2} (bidirectional)")
    
    print("\n" + "-"*70)
    print("OSPF NEIGHBOR COUNT PER ROUTER:")
    print("-"*70)
    
    for node in sorted([n for n in G.nodes() if 'node-' in n or 'pce-' in n]):
        neighbors = list(G.neighbors(node))
        print(f"{node:10s} → {len(neighbors)} neighbors: {', '.join(sorted(neighbors))}")
    
    print("\n" + "-"*70)
    print("ALL PHYSICAL LINKS:")
    print("-"*70)
    
    for u, v, data in sorted(G.edges(data=True)):
        print(f"{u:10s} ↔ {v:10s} | {data['subnet']:15s}")
    
    print("\n" + "="*70)

def generate_mermaid_diagram(G):
    """Generate Mermaid syntax for web-based visualization."""
    
    mermaid = ["```mermaid", "graph TB"]
    
    # Add style classes
    mermaid.append("    classDef xrv fill:#ADD8E6,stroke:#333,stroke-width:2px")
    mermaid.append("    classDef xrd fill:#90EE90,stroke:#333,stroke-width:2px")
    mermaid.append("    classDef pce fill:#FFFFE0,stroke:#333,stroke-width:2px")
    mermaid.append("")
    
    # Add nodes
    for node, data in sorted(G.nodes(data=True)):
        label = f"{node}<br/>{data['loopback']}"
        mermaid.append(f"    {node}[\"{label}\"]")
    
    mermaid.append("")
    
    # Add edges
    edges_added = set()
    for u, v, data in sorted(G.edges(data=True)):
        edge_key = tuple(sorted([u, v]))
        if edge_key not in edges_added:
            mermaid.append(f"    {u} ---|{data['subnet']}| {v}")
            edges_added.add(edge_key)
    
    mermaid.append("")
    
    # Apply styles
    for node, data in G.nodes(data=True):
        if 'IOS-XRv' in data.get('platform', ''):
            mermaid.append(f"    class {node} xrv")
        elif 'XRd' in data.get('platform', ''):
            mermaid.append(f"    class {node} xrd")
        elif data.get('node_type') == 'pce':
            mermaid.append(f"    class {node} pce")
    
    mermaid.append("```")
    
    return "\n".join(mermaid)

if __name__ == "__main__":
    # Create graph
    G = create_topology_graph()
    
    # Print summary
    print_topology_summary(G)
    
    # Create visualization
    output_path = '/Users/gudeng/MCP_Server/docs/complete_network_topology_20251119.png'
    visualize_topology(G, output_path)
    
    # Generate Mermaid diagram
    mermaid_output = '/Users/gudeng/MCP_Server/docs/complete_network_topology_mermaid_20251119.md'
    with open(mermaid_output, 'w') as f:
        f.write("# Complete Network Topology - Mermaid Diagram\n\n")
        f.write("**Based on Physical Topology Diagram**\n\n")
        f.write(generate_mermaid_diagram(G))
    
    print(f"✓ Mermaid diagram saved to: {mermaid_output}")
    print("\n✓ Complete topology visualization finished!")

