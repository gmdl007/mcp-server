#!/bin/bash

# FastMCP NSO Server Startup Script
# =================================

# Set NSO environment variables
export NSO_DIR="/Users/gudeng/NCS-6413"
export NCS_DIR="$NSO_DIR"
export DYLD_LIBRARY_PATH="$NSO_DIR/lib"
export PYTHONPATH="$NSO_DIR/src/ncs/pyapi"

# Activate virtual environment
source /Users/gudeng/MCP_Server/mcp_venv/bin/activate

# Start FastMCP server
exec python /Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/fastmcp_nso_server.py
