# BGP Topology Map - All Nodes

**Generated:** 2025-11-17  
**Protocol:** BGP iBGP (AS 65000)  
**Address Families:** VPNv4 Unicast, VPNv6 Unicast, BGP-LS (Link-state)

## BGP Topology Visualization

```
                    pce-11 (198.19.2.11)
                    (Route Reflector / PCE)
                         |
        ┌────────────────┼────────────────┐
        |                |                |
     node-1          node-2          node-3
   (198.19.1.1)   (198.19.1.2)   (198.19.1.3)
   VPNv4/VPNv6    VPNv4/VPNv6    VPNv4/VPNv6
        |                |                |
        |                |                |
     node-4          node-6          node-8
   (198.19.1.4)   (198.19.1.6)   (198.19.1.8)
   VPNv4/VPNv6      BGP-LS          BGP-LS
        |                |                |
        └────────────────┴────────────────┘
                         |
                     node-9
                  (198.19.1.9)
                  VPNv4/VPNv6
```

## Detailed BGP Neighbor Status

### node-1 (Router ID: 198.19.1.1)
- **BGP Neighbors (2):**
  - **198.19.2.11** (pce-11) - VPNv4 Unicast
    - State: **Established** (up for 22:55:24)
    - Local: 198.19.1.1:179
    - Remote: 198.19.2.11:51844
    - Prefixes: 0 received, 0 advertised
  - **2011::11** (pce-11 IPv6) - VPNv6 Unicast
    - State: **Established** (up for 22:55:20)
    - Local: 2010::1:33525
    - Remote: 2011::11:179
    - Prefixes: 0 received, 0 advertised

### node-2 (Router ID: 198.19.1.2)
- **BGP Neighbors (2):**
  - **198.19.2.11** (pce-11) - VPNv4 Unicast
    - State: **Established** (up for 15:23:59)
    - Local: 198.19.1.2:19243
    - Remote: 198.19.2.11:179
    - Prefixes: 0 received, 0 advertised
    - Note: Had 1 connection drop (hold time expired) 15:34:00 ago
  - **2011::11** (pce-11 IPv6) - VPNv6 Unicast
    - State: **Established** (up for 15:24:04)
    - Local: 2010::2:21600
    - Remote: 2011::11:179
    - Prefixes: 0 received, 0 advertised

### node-3 (Router ID: 198.19.1.3)
- **BGP Neighbors (2):**
  - **198.19.2.11** (pce-11) - VPNv4 Unicast
    - State: **Established** (up for 00:56:17)
    - Local: 198.19.1.3:23050
    - Remote: 198.19.2.11:179
    - Prefixes: 0 received, 0 advertised
  - **2011::11** (pce-11 IPv6) - VPNv6 Unicast
    - State: **Established** (up for 00:56:12)
    - Local: 2010::3:35952
    - Remote: 2011::11:179
    - Prefixes: 0 received, 0 advertised

### node-4 (Router ID: 198.19.1.4)
- **BGP Neighbors (2):**
  - **198.19.2.11** (pce-11) - VPNv4 Unicast
    - State: **Established** (up for 22:55:48)
    - Local: 198.19.1.4:31023
    - Remote: 198.19.2.11:179
    - Prefixes: 0 received, 0 advertised
  - **2011::11** (pce-11 IPv6) - VPNv6 Unicast
    - State: **Established** (up for 22:55:53)
    - Local: 2010::4:48867
    - Remote: 2011::11:179
    - Prefixes: 0 received, 0 advertised

### node-5 (Router ID: Unknown)
- **BGP Status:** BGP instance 'default' not active
- **No BGP neighbors**

### node-6 (Router ID: 198.19.1.6)
- **BGP Neighbors (2):**
  - **198.19.2.11** (pce-11) - BGP-LS (Link-state)
    - State: **Established** (up for 22:56:15)
    - Local: 198.19.1.6:61094
    - Remote: 198.19.2.11:179
    - Prefixes: **3 received, 645 advertised**
    - Note: Active BGP-LS session with route exchange
  - **2011::11** (pce-11 IPv6) - VPNv6 Unicast
    - State: **Idle** (No address-family configured)
    - Not established

### node-7 (Router ID: Unknown)
- **BGP Status:** BGP instance 'default' not active
- **No BGP neighbors**

### node-8 (Router ID: 198.19.1.8)
- **BGP Neighbors (2):**
  - **198.19.2.11** (pce-11) - BGP-LS (Link-state)
    - State: **Established** (up for 22:56:59)
    - Local: 198.19.1.8:16401
    - Remote: 198.19.2.11:179
    - Prefixes: **342 received, 665 advertised**
    - Note: Active BGP-LS session with significant route exchange
  - **2011::11** (pce-11 IPv6) - VPNv6 Unicast
    - State: **Idle** (No address-family configured)
    - Not established

### pce-11 (Router ID: 198.19.2.11)
- **Role:** Route Reflector / Path Computation Element (PCE)
- **Cluster ID:** 198.19.2.11
- **IPv4 Address:** 198.19.2.11
- **IPv6 Address:** 2011::11
- **BGP Neighbors (7 active):**
  - **198.19.1.1** (node-1) - VPNv4/VPNv6 - Route-Reflector Client
  - **198.19.1.2** (node-2) - VPNv4/VPNv6 - Route-Reflector Client
  - **198.19.1.3** (node-3) - VPNv4/VPNv6 - Route-Reflector Client
  - **198.19.1.4** (node-4) - VPNv4/VPNv6 - Route-Reflector Client
  - **198.19.1.6** (node-6) - BGP-LS - Route-Reflector Client (342 prefixes received)
  - **198.19.1.8** (node-8) - BGP-LS - Route-Reflector Client (342 prefixes received)
  - **198.19.1.9** (node-9) - VPNv4/VPNv6 - Route-Reflector Client

## BGP Topology Summary

### Hub-and-Spoke Architecture (Route Reflector)
- **Central Hub:** pce-11 (198.19.2.11) - Route Reflector with Cluster ID 198.19.2.11
- **Spoke Nodes (Route-Reflector Clients):** node-1, node-2, node-3, node-4, node-6, node-8, node-9
- **Not Connected:** node-5, node-7 (BGP not active)

### Address Family Distribution

| Node | VPNv4 | VPNv6 | BGP-LS | Status |
|------|-------|-------|--------|--------|
| node-1 | ✅ | ✅ | ❌ | Established |
| node-2 | ✅ | ✅ | ❌ | Established |
| node-3 | ✅ | ✅ | ❌ | Established |
| node-4 | ✅ | ✅ | ❌ | Established |
| node-5 | ❌ | ❌ | ❌ | Not Active |
| node-6 | ❌ | ❌ | ✅ | Established (BGP-LS only) |
| node-7 | ❌ | ❌ | ❌ | Not Active |
| node-8 | ❌ | ❌ | ✅ | Established (BGP-LS only) |
| node-9 | ✅ | ✅ | ❌ | Established |

### Key Observations

1. **Route Reflector Pattern:** All BGP sessions are to pce-11, indicating a hub-and-spoke route reflector topology with Cluster ID 198.19.2.11
2. **VPN Services:** node-1, node-2, node-3, node-4, and node-9 are configured for VPNv4/VPNv6 (MPLS VPN services)
3. **BGP-LS Services:** node-6 and node-8 are running BGP-LS (Link-state) for traffic engineering/SR-PCE, actively exchanging 342 prefixes each with pce-11
4. **No IPv4 Unicast:** No nodes have IPv4 unicast BGP configured (only VPN and Link-state)
5. **Dual Stack:** Most nodes have both IPv4 and IPv6 BGP sessions to pce-11
6. **Active Route Exchange:** 
   - node-6: 645 prefixes advertised, 3 received
   - node-8: 665 prefixes advertised, 342 received
   - pce-11: Receiving 342 BGP-LS prefixes from both node-6 and node-8

### BGP Session Details

**Common Configuration:**
- AS Number: 65000 (iBGP)
- Hold Time: 180 seconds
- Keepalive: 60 seconds
- NSR: Enabled
- Route Refresh: Supported (old + new)
- 4-byte AS: Supported

**Session Uptime:**
- node-1: ~23 hours
- node-2: ~15 hours (had connection drop)
- node-3: ~1 hour (recently established)
- node-4: ~23 hours
- node-6: ~23 hours
- node-8: ~23 hours

## BGP vs IS-IS Comparison

| Protocol | Purpose | Topology | Status |
|----------|---------|----------|--------|
| **IS-IS** | IGP (Internal Gateway Protocol) | Mesh (all nodes connected) | Active on all nodes |
| **BGP** | EGP (External Gateway Protocol) | Hub-and-Spoke (to pce-11) | Active on 6/8 nodes |

**IS-IS:** Provides internal routing between all nodes (mesh topology)  
**BGP:** Provides VPN services and traffic engineering (hub-and-spoke to pce-11)

