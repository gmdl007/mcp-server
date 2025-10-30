#!/bin/bash

# FastMCP NSO Server - Auto-Generated Tools Version
# Startup script for the auto-generated tools server

# echo "🚀 Starting FastMCP NSO Auto-Generated Tools Server..." >&2

# Change to the project directory
cd /Users/gudeng/MCP_Server

# Activate virtual environment
source mcp_venv/bin/activate

# Set NSO environment variables
export NSO_DIR="/Users/gudeng/NCS-614"
export NCS_DIR="$NSO_DIR"
export DYLD_LIBRARY_PATH="$NSO_DIR/lib"
export PYTHONPATH="$NSO_DIR/src/ncs/pyapi"

# Start the auto-generated tools server
# Redirect stderr to a log file to keep stdout clean for MCP protocol
exec python src/mcp_server/working/llama_index_mcp/fastmcp_nso_server_auto_generated.py 2>/tmp/fastmcp_auto_generated.log
