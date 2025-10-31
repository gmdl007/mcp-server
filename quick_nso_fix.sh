#!/bin/bash
# Quick NSO Health Check and Fix Script
# Run this when NSO appears hung or unresponsive

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HEALTH_CHECK_SCRIPT="$SCRIPT_DIR/nso_health_check_auto_fix_20251031_153500.py"

echo "============================================================"
echo "Quick NSO Fix - Automated Health Check and Repair"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ -d "$SCRIPT_DIR/mcp_venv" ]; then
    source "$SCRIPT_DIR/mcp_venv/bin/activate"
fi

# Set environment variables
export NCS_DIR=/Users/gudeng/NCS-614
export DYLD_LIBRARY_PATH=/Users/gudeng/NCS-614/lib
export PYTHONPATH=/Users/gudeng/NCS-614/src/ncs/pyapi:$PYTHONPATH

# Run health check with auto-fix
python3 "$HEALTH_CHECK_SCRIPT" "$@"

EXIT_CODE=$?

echo ""
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ NSO is healthy"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "⚠️  Issues found but fixed"
else
    echo "❌ Issues found, may need manual intervention"
fi
echo "============================================================"

exit $EXIT_CODE

