#!/bin/bash
# NSO MCP Server Wrapper for Cursor
# ==================================

# Set NSO environment
export NCS_DIR="/Users/gudeng/NCS-614"
export DYLD_LIBRARY_PATH="$NCS_DIR/lib"
export PYTHONPATH="$NCS_DIR/src/ncs/pyapi"

# Source NSO environment if available
if [ -f "$NCS_DIR/ncsrc" ]; then
    source "$NCS_DIR/ncsrc"
fi

# Activate MCP virtual environment
source "/Users/gudeng/MCP_Server/mcp_venv/bin/activate"

# Start the MCP server
exec python "/Users/gudeng/MCP_Server/src/mcp_server/nso_mcp_simple_fixed.py"
