#!/bin/bash
# Install NED package: cisco-iosxr-7.61.4 for NSO 6.4.1

set -e

NSO_RUN="/Users/gudeng/ncs-run-6413"
PACKAGES_DIR="${NSO_RUN}/packages"
NEDS_DIR="${PACKAGES_DIR}/neds"
DOWNLOADS_DIR="${HOME}/Downloads"
SIGNED_BIN="${DOWNLOADS_DIR}/ncs-6.4.1-cisco-iosxr-7.61.4.signed.bin"

echo "============================================================"
echo "Installing NED: cisco-iosxr-7.61.4"
echo "============================================================"
echo ""

# Step 1: Extract signed.bin
echo "Step 1: Extracting signed.bin package..."
if [ ! -f "$SIGNED_BIN" ]; then
    echo "❌ Error: File not found: $SIGNED_BIN"
    exit 1
fi

cd "$DOWNLOADS_DIR"
chmod +x "$SIGNED_BIN"
./ncs-6.4.1-cisco-iosxr-7.61.4.signed.bin

echo "✅ Extraction complete"
echo ""

# Step 2: Find the tar.gz file
echo "Step 2: Finding extracted tar.gz file..."
TAR_FILE=$(find "$DOWNLOADS_DIR" -name "ncs-6.4.1-cisco-iosxr-7.61.4*.tar.gz" -type f | head -1)

if [ -z "$TAR_FILE" ]; then
    echo "❌ Error: tar.gz file not found after extraction"
    echo "   Please check Downloads directory for extracted files"
    exit 1
fi

echo "✅ Found: $TAR_FILE"
echo ""

# Step 3: Extract and install to neds directory
echo "Step 3: Installing NED to packages/neds/..."
mkdir -p "$NEDS_DIR"

cd "$NEDS_DIR"
tar -xzf "$TAR_FILE"

# Get the extracted directory name
EXTRACTED_DIR=$(tar -tzf "$TAR_FILE" | head -1 | cut -d'/' -f1)
TARGET_DIR="${NEDS_DIR}/${EXTRACTED_DIR}"

if [ -d "$TARGET_DIR" ]; then
    echo "✅ NED installed to: $TARGET_DIR"
    
    # Check if it should be in packages/ directly (like other NEDs)
    if [ -d "${PACKAGES_DIR}/${EXTRACTED_DIR}" ]; then
        echo "⚠️  NED also exists in packages/ - checking structure..."
    fi
    
    # Move to packages/ if neds/ structure is not standard
    if [[ "$EXTRACTED_DIR" == cisco-iosxr-cli-* ]]; then
        echo "Moving to packages/ directory (standard location)..."
        if [ -d "${PACKAGES_DIR}/${EXTRACTED_DIR}" ]; then
            rm -rf "${PACKAGES_DIR}/${EXTRACTED_DIR}"
        fi
        mv "$TARGET_DIR" "${PACKAGES_DIR}/"
        echo "✅ Moved to: ${PACKAGES_DIR}/${EXTRACTED_DIR}"
    fi
else
    echo "❌ Error: Installation failed"
    exit 1
fi

echo ""
echo "============================================================"
echo "✅ NED Installation Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Start NSO (if not running):"
echo "   cd $NSO_RUN"
echo "   ncs"
echo ""
echo "2. Reload packages:"
echo "   ncs_cli -u admin -C"
echo "   packages reload"
echo ""

