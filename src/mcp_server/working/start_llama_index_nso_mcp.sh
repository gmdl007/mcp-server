#!/bin/bash
set -euo pipefail

export NCS_DIR="/Users/gudeng/NCS-614"
export DYLD_LIBRARY_PATH="$NCS_DIR/lib"
export PYTHONPATH="$NCS_DIR/src/ncs/pyapi"
source "/Users/gudeng/MCP_Server/mcp_venv/bin/activate"
exec python "/Users/gudeng/MCP_Server/src/mcp_server/llama_index_nso_mcp.py"
