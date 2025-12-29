# Virtual Environment Fix Instructions

## Problem
Your `fastmcp_nso_server_auto_generated.py` cannot start because:

1. **Virtual environment is broken**: Created with Python 3.13, which is no longer available
2. **Python version mismatch**: `fastmcp` requires Python 3.10+, but system has Python 3.9.6
3. **Missing dependencies**: `requests`, `python-dotenv`, and `fastmcp` are not installed

## Solution Options

### Option 1: Install Python 3.10+ via Homebrew (Recommended)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Create new virtual environment with Python 3.12
cd /Users/gudeng/MCP_Server
rm -rf mcp_venv
/opt/homebrew/bin/python3.12 -m venv mcp_venv
source mcp_venv/bin/activate
pip install --upgrade pip
pip install requests python-dotenv fastmcp
```

### Option 2: Install Python 3.10+ via pyenv

```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.12
pyenv install 3.12.0
pyenv local 3.12.0

# Create new virtual environment
cd /Users/gudeng/MCP_Server
rm -rf mcp_venv
python -m venv mcp_venv
source mcp_venv/bin/activate
pip install --upgrade pip
pip install requests python-dotenv fastmcp
```

### Option 3: Use System Python 3.10+ (if available)

```bash
# Find available Python versions
ls /usr/local/bin/python* 2>/dev/null
ls /Library/Frameworks/Python.framework/Versions/*/bin/python* 2>/dev/null

# If Python 3.10+ is found, use it to create venv
cd /Users/gudeng/MCP_Server
rm -rf mcp_venv
/usr/local/bin/python3.12 -m venv mcp_venv  # or whatever path you find
source mcp_venv/bin/activate
pip install --upgrade pip
pip install requests python-dotenv fastmcp
```

## Quick Test

After fixing the virtual environment, test the server:

```bash
cd /Users/gudeng/MCP_Server
source mcp_venv/bin/activate
python src/mcp_server/working/llama_index_mcp/fastmcp_nso_server_auto_generated.py
```

## Current Status

✅ `requests` and `python-dotenv` have been installed in the new venv (Python 3.9)
❌ `fastmcp` cannot be installed - requires Python 3.10+

You must upgrade to Python 3.10+ before `fastmcp` can be installed.

