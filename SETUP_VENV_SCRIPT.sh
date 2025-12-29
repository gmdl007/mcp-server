#!/bin/bash
# Setup script for FastMCP NSO Server Virtual Environment
# This script sets up the virtual environment with Python 3.12 and installs all dependencies

set -e

cd /Users/gudeng/MCP_Server

# Setup pyenv in this shell session
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

# Check if Python 3.12 is installed, if not install it
if ! pyenv versions | grep -q "3.12"; then
    echo "Installing Python 3.12.7 (this may take several minutes)..."
    pyenv install 3.12.7
fi

# Set local Python version
pyenv local 3.12.7

# Remove old virtual environment
if [ -d "mcp_venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf mcp_venv
fi

# Create new virtual environment with Python 3.12
echo "Creating new virtual environment with Python 3.12.7..."
python -m venv mcp_venv

# Activate virtual environment
source mcp_venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install requests python-dotenv fastmcp

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "To use it, run:"
echo "  source mcp_venv/bin/activate"
echo ""
echo "To test the server:"
echo "  python src/mcp_server/working/llama_index_mcp/fastmcp_nso_server_auto_generated.py"

