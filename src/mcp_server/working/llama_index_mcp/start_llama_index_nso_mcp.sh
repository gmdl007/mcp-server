#!/bin/bash
# LlamaIndex NSO MCP Server Startup Script

export NCS_DIR="/Users/gudeng/NCS-614"
export DYLD_LIBRARY_PATH="$NCS_DIR/lib"
export PYTHONPATH="$NCS_DIR/src/ncs/pyapi"

# Activate virtual environment
source "/Users/gudeng/MCP_Server/mcp_venv/bin/activate"

# Run the LlamaIndex NSO MCP server
exec python "/Users/gudeng/MCP_Server/src/mcp_server/working/llama_index_mcp/llama_index_nso_mcp_server.py"
