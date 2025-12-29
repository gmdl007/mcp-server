#!/bin/bash
# NSO Upgrade Script: 6.1.4 to 6.4.1
# This script helps migrate from NSO 6.1.4 to 6.4.1

set -e

CURRENT_NSO="/Users/gudeng/NCS-614"
CURRENT_RUN="/Users/gudeng/ncs-run"
NEW_NSO="/Users/gudeng/NCS-6413"
NEW_RUN="/Users/gudeng/ncs-run-6413"
BACKUP_DIR="/Users/gudeng/nso-backup-$(date +%Y%m%d-%H%M%S)"

echo "============================================================"
echo "NSO Upgrade Script: 6.1.4 to 6.4.1.3 (ARM64)"
echo "============================================================"
echo ""
echo "Current NSO: $CURRENT_NSO"
echo "Current Run: $CURRENT_RUN"
echo "New NSO: $NEW_NSO"
echo "New Run: $NEW_RUN"
echo "Backup: $BACKUP_DIR"
echo ""

# Step 1: Backup
echo "Step 1: Creating backup..."
mkdir -p "$BACKUP_DIR"
echo "  Backing up ncs-run..."
cp -r "$CURRENT_RUN" "$BACKUP_DIR/ncs-run-backup"
echo "  ✅ Backup created: $BACKUP_DIR"
echo ""

# Step 2: Check if NSO 6.4.1.3 is installed
echo "Step 2: Checking NSO 6.4.1.3 installation..."
if [ ! -d "$NEW_NSO" ]; then
    echo "  ⚠️  NSO 6.4.1.3 not found at $NEW_NSO"
    echo "  Please install NSO 6.4.1.3 first:"
    echo "    chmod +x ~/Downloads/nso-6.4.1.3.darwin.arm64.signed.bin"
    echo "    ~/Downloads/nso-6.4.1.3.darwin.arm64.signed.bin --local-install $NEW_NSO"
    exit 1
fi

if [ ! -f "$NEW_NSO/bin/ncs" ]; then
    echo "  ⚠️  NSO 6.4.1 installation incomplete"
    exit 1
fi

VERSION=$("$NEW_NSO/bin/ncs" --version 2>&1 | head -1)
echo "  ✅ Found NSO: $VERSION"
echo ""

# Step 3: Create new runtime directory
echo "Step 3: Creating new runtime directory..."
if [ -d "$NEW_RUN" ]; then
    echo "  ⚠️  $NEW_RUN already exists"
    read -p "  Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$NEW_RUN"
    else
        echo "  Exiting..."
        exit 1
    fi
fi

"$NEW_NSO/bin/ncs-setup" --dest "$NEW_RUN"
echo "  ✅ Created: $NEW_RUN"
echo ""

# Step 4: Copy packages
echo "Step 4: Migrating packages..."
if [ -d "$CURRENT_RUN/packages" ]; then
    echo "  Copying packages from $CURRENT_RUN/packages..."
    cp -r "$CURRENT_RUN/packages"/* "$NEW_RUN/packages/" 2>/dev/null || true
    echo "  ✅ Packages copied"
else
    echo "  ⚠️  No packages directory found"
fi
echo ""

# Step 5: Copy configuration
echo "Step 5: Migrating configuration..."
if [ -f "$CURRENT_RUN/ncs.conf" ]; then
    echo "  Copying ncs.conf..."
    cp "$CURRENT_RUN/ncs.conf" "$NEW_RUN/ncs.conf"
    echo "  ✅ Configuration copied"
    echo "  ⚠️  Please review ncs.conf for version-specific changes"
else
    echo "  ⚠️  No ncs.conf found"
fi
echo ""

# Step 6: Export device configurations
echo "Step 6: Exporting device configurations..."
if [ -d "$CURRENT_RUN/ncs-cdb" ]; then
    echo "  Copying CDB..."
    cp -r "$CURRENT_RUN/ncs-cdb" "$NEW_RUN/ncs-cdb" 2>/dev/null || true
    echo "  ✅ CDB copied"
else
    echo "  ⚠️  No CDB directory found"
fi
echo ""

echo "============================================================"
echo "Migration Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Review and update $NEW_RUN/ncs.conf"
echo "2. Update NED packages to 6.4.1 compatible versions"
echo "3. Start new NSO instance:"
echo "   cd $NEW_RUN"
echo "   $NEW_NSO/bin/ncs --start"
echo "4. Test connectivity and packages"
echo "5. Once verified, switch to new version"
echo ""
echo "Backup location: $BACKUP_DIR"
echo ""

