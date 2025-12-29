#!/bin/bash
# Recreate Netsim with NCS 6.4.1.3
# This script recreates netsim using NCS-6413 with the old NED package

set -e

NSO_614_DIR="/Users/gudeng/NCS-614"
NSO_6413_DIR="/Users/gudeng/NCS-6413"
NETSIM_DIR="/Users/gudeng/MCP_Server/netsim"
OLD_NED_PATH="/Users/gudeng/ncs-run/packages/cisco-iosxr-cli-7.52"

echo "======================================================================"
echo "Recreating Netsim with NCS 6.4.1.3"
echo "======================================================================"
echo "NSO 6.4.1.3 Directory: $NSO_6413_DIR"
echo "Netsim Directory: $NETSIM_DIR"
echo "Using NED: $OLD_NED_PATH"
echo ""

# Stop old netsim if running
if [ -d "$NETSIM_DIR" ]; then
    echo "Stopping old netsim..."
    cd "$NETSIM_DIR"
    "$NSO_614_DIR/bin/ncs-netsim" stop 2>&1 || echo "Old netsim already stopped or not running"
    cd - > /dev/null
    
    # Backup old netsim
    BACKUP_DIR="${NETSIM_DIR}_old_614_backup"
    if [ -d "$BACKUP_DIR" ]; then
        rm -rf "$BACKUP_DIR"
    fi
    mv "$NETSIM_DIR" "$BACKUP_DIR"
    echo "✅ Backed up old netsim to: $BACKUP_DIR"
    echo ""
fi

# Create new netsim
echo "Creating new netsim with NCS-6413..."
cd /Users/gudeng/MCP_Server
"$NSO_6413_DIR/bin/ncs-netsim" create-network "$OLD_NED_PATH" 3 xr9kv --dir netsim

if [ $? -eq 0 ]; then
    echo "✅ Netsim created successfully"
else
    echo "❌ Failed to create netsim"
    exit 1
fi

# Start netsim
echo ""
echo "Starting netsim..."
cd "$NETSIM_DIR"
"$NSO_6413_DIR/bin/ncs-netsim" start

if [ $? -eq 0 ]; then
    echo "✅ Netsim started successfully"
else
    echo "⚠️  Netsim start had issues"
fi

# Wait a bit for devices to start
sleep 5

# List devices
echo ""
echo "Netsim devices:"
"$NSO_6413_DIR/bin/ncs-netsim" list

# Check status
echo ""
echo "Netsim status:"
"$NSO_6413_DIR/bin/ncs-netsim" status

echo ""
echo "======================================================================"
echo "Netsim Recreation Complete"
echo "======================================================================"
echo ""
echo "Devices are available on:"
echo "  xr9kv0: CLI SSH port 10022, NETCONF port 12022"
echo "  xr9kv1: CLI SSH port 10023, NETCONF port 12023"
echo "  xr9kv2: CLI SSH port 10024, NETCONF port 12024"
echo ""

