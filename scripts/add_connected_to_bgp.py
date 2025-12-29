#!/usr/bin/env python3
# add_connected_to_bgp.py
# Adds 'redistribute connected' to BGP 65001 on BGP‑speaking nodes

import sys
from ncs.maapi import Maapi
from ncs.maagic import get_root

# List of BGP‑speaking nodes
nodes = ['node-1', 'node-2', 'node-3', 'node-4']

# NSO connection parameters (adjust if needed)
HOST = 'localhost'
PORT = 0

# Create a MAAPI session (explicitly pass None for path)
maapi = Maapi(HOST, PORT, None)

for node in nodes:
    try:
        # Create a write transaction
        t = maapi.start_write_trans()
        root = t.get_root()
        device = root.devices.device[node]

        # Access the BGP 65001 container
        bgp = device.config.router.bgp[65001]

        # Add redistribute connected if missing
        if not bgp.redistribute.connected:
            bgp.redistribute.connected.create()

        # Commit the changes
        t.apply()
        print(f"[{node}] redistribute connected added to BGP 65001")
    except Exception as e:
        print(f"[{node}] error: {e}", file=sys.stderr)
