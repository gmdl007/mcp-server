#!/bin/bash
# Startup script for FastMCP NSO Server
# This script sets up the environment and starts the server

cd /Users/gudeng/MCP_Server

# Setup pyenv (if needed)
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

# Setup Homebrew (required for NSO dependencies)
eval "$(/opt/homebrew/bin/brew shellenv)"

# Activate virtual environment
source mcp_venv/bin/activate

# Set NSO environment variables
export NCS_DIR="/Users/gudeng/NCS-614"
export DYLD_LIBRARY_PATH="$NCS_DIR/lib"
export PYTHONPATH="$NCS_DIR/src/ncs/pyapi"

# Start the server
python src/mcp_server/working/llama_index_mcp/fastmcp_nso_server_auto_generated.py

