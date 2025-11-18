# IS-IS Topology Map - All Nodes

**Generated:** 2025-11-17  
**Protocol:** IS-IS Level-2 (L2)  
**All neighbors are UP and IETF-NSF Capable**

## Topology Visualization

```
                    vmx-9
                     |
                     |
        ┌────────────┴────────────┐
        |                         |
     node-5 ────────────────── node-7
        |                         |
        |                         |
     node-4 ────────────────── node-8
        |                         |
        |                         |
     node-3                       |
        |                         |
        |                         |
     node-6 ────────────────── node-2
        |                         |
        └────────────┬────────────┘
                     |
                  node-1
```

## Detailed Node Connections

### node-1
- **Neighbors (2):**
  - node-2 via Gi0/0/0/2
  - node-6 via Gi0/0/0/6

### node-2
- **Neighbors (3):**
  - node-1 via Gi0/0/0/1
  - node-6 via Gi0/0/0/6
  - node-7 via Gi0/0/0/7

### node-3
- **Neighbors (2):**
  - node-4 via Gi0/0/0/4
  - node-8 via Gi0/0/0/8

### node-4
- **Neighbors (3):**
  - node-3 via Gi0/0/0/3
  - node-5 via Gi0/0/0/5
  - node-8 via Gi0/0/0/8

### node-5
- **Neighbors (5):**
  - vmx-9 via Gi0/0/0/9
  - node-4 via Gi0/0/0/4
  - node-6 via Gi0/0/0/6
  - node-7 via Gi0/0/0/7
  - node-8 via Gi0/0/0/8

### node-6
- **Neighbors (4):**
  - node-1 via Gi0/0/0/1
  - node-2 via Gi0/0/0/2
  - node-5 via Gi0/0/0/5
  - node-7 via Gi0/0/0/7

### node-7
- **Neighbors (5):**
  - vmx-9 via Gi0/0/0/9
  - node-2 via Gi0/0/0/2
  - node-5 via Gi0/0/0/5
  - node-6 via Gi0/0/0/6
  - node-8 via Gi0/0/0/8

### node-8
- **Neighbors (4):**
  - node-3 via Gi0/0/0/3
  - node-4 via Gi0/0/0/4
  - node-5 via Gi0/0/0/5
  - node-7 via Gi0/0/0/7

### vmx-9 (External Node)
- **Neighbors (2):**
  - node-5 via Gi0/0/0/9
  - node-7 via Gi0/0/0/9

## Topology Characteristics

### Network Segments

**Left Cluster (node-1, node-2, node-6):**
- Triangle topology with redundant paths
- node-1 is a leaf node (2 neighbors)
- node-2 and node-6 are transit nodes

**Right Cluster (node-3, node-4, node-8):**
- Triangle topology
- node-3 is a leaf node (2 neighbors)
- node-4 and node-8 are transit nodes

**Central Hub (node-5, node-7):**
- Highly connected nodes (5 neighbors each)
- Connect left and right clusters
- Connect to external node vmx-9
- Form redundant paths between clusters

### Connectivity Summary

| Node | Neighbor Count | Role |
|------|---------------|------|
| node-1 | 2 | Leaf (Left cluster) |
| node-2 | 3 | Transit (Left cluster) |
| node-3 | 2 | Leaf (Right cluster) |
| node-4 | 3 | Transit (Right cluster) |
| node-5 | 5 | Hub (Central) |
| node-6 | 4 | Transit (Left cluster) |
| node-7 | 5 | Hub (Central) |
| node-8 | 4 | Transit (Right cluster) |
| vmx-9 | 2 | External connection |

### Path Redundancy

- **Left to Right cluster:** Multiple paths via node-5 and node-7
- **All nodes:** Connected to IS-IS Level-2 database
- **No single point of failure:** Multiple redundant paths exist

## IS-IS Database Status

**Level-2 LSPs:** 15 total (all nodes present)
- All nodes have LSPs in the database
- All neighbors show "Up" state
- All are IETF-NSF Capable

## Interface Mapping

| Connection | Local Interface | Remote Interface |
|------------|----------------|------------------|
| node-1 ↔ node-2 | Gi0/0/0/2 | Gi0/0/0/1 |
| node-1 ↔ node-6 | Gi0/0/0/6 | Gi0/0/0/1 |
| node-2 ↔ node-6 | Gi0/0/0/6 | Gi0/0/0/2 |
| node-2 ↔ node-7 | Gi0/0/0/7 | Gi0/0/0/2 |
| node-3 ↔ node-4 | Gi0/0/0/4 | Gi0/0/0/3 |
| node-3 ↔ node-8 | Gi0/0/0/8 | Gi0/0/0/3 |
| node-4 ↔ node-5 | Gi0/0/0/5 | Gi0/0/0/4 |
| node-4 ↔ node-8 | Gi0/0/0/8 | Gi0/0/0/4 |
| node-5 ↔ node-6 | Gi0/0/0/6 | Gi0/0/0/5 |
| node-5 ↔ node-7 | Gi0/0/0/7 | Gi0/0/0/5 |
| node-5 ↔ node-8 | Gi0/0/0/8 | Gi0/0/0/5 |
| node-5 ↔ vmx-9 | Gi0/0/0/9 | (external) |
| node-6 ↔ node-7 | Gi0/0/0/7 | Gi0/0/0/6 |
| node-7 ↔ node-8 | Gi0/0/0/8 | Gi0/0/0/7 |
| node-7 ↔ vmx-9 | Gi0/0/0/9 | (external) |

