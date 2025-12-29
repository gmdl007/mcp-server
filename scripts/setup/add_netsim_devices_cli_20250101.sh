#!/bin/bash
# Add netsim devices using NSO CLI directly

NSO_CLI="/Users/gudeng/NCS-6413/bin/ncs_cli"
NSO_RUN_DIR="/Users/gudeng/ncs-run-6413"

echo "======================================================================"
echo "Adding Netsim Devices to NSO 6.4.1.3 via CLI"
echo "======================================================================"

# Using cisco-iosxr-cli-7.61 NED (already installed and compiled)
echo "Adding devices with cisco-iosxr-cli-7.61 NED..."
cd "$NSO_RUN_DIR"
"$NSO_CLI" -u admin <<EOF
configure
devices device xr9kv0 address 127.0.0.1
devices device xr9kv0 port 10022
devices device xr9kv0 authgroup cisco
devices device xr9kv0 device-type cli ned-id cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61
devices device xr9kv0 state admin-state unlocked
devices device xr9kv1 address 127.0.0.1
devices device xr9kv1 port 10023
devices device xr9kv1 authgroup cisco
devices device xr9kv1 device-type cli ned-id cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61
devices device xr9kv1 state admin-state unlocked
devices device xr9kv2 address 127.0.0.1
devices device xr9kv2 port 10024
devices device xr9kv2 authgroup cisco
devices device xr9kv2 device-type cli ned-id cisco-iosxr-cli-7.61:cisco-iosxr-cli-7.61
devices device xr9kv2 state admin-state unlocked
commit
exit
EOF

echo ""
echo "======================================================================"
echo "Verifying devices..."
echo "======================================================================"
"$NSO_CLI" -u admin <<EOF
show running-config devices device xr9kv0
show running-config devices device xr9kv1
show running-config devices device xr9kv2
exit
EOF

echo ""
echo "======================================================================"
echo "Testing authgroup - connecting to xr9kv0..."
echo "======================================================================"
"$NSO_CLI" -u admin <<EOF
devices device xr9kv0 connect
devices device xr9kv0 sync-from
exit
EOF

