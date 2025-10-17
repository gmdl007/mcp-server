#!/bin/bash

# NSO Environment Startup Script
# This script automates the setup of NSO environment for Jupyter notebook development

echo "🚀 Starting NSO Environment Setup..."
echo "=================================="

# Step 1: Initialize conda
echo "📦 Step 1: Initializing conda environment..."
eval "$(/Users/gudeng/miniforge3/bin/conda shell.zsh hook)"
if [ $? -eq 0 ]; then
    echo "✅ Conda initialized successfully"
else
    echo "❌ Failed to initialize conda"
    exit 1
fi

# Step 2: Activate base environment
echo "🔄 Step 2: Activating base conda environment..."
conda activate base
if [ $? -eq 0 ]; then
    echo "✅ Base environment activated"
else
    echo "❌ Failed to activate base environment"
    exit 1
fi

# Step 3: Set up NSO environment variables
echo "🔧 Step 3: Setting up NSO environment..."
export DYLD_LIBRARY_PATH=""
export PYTHONPATH=""

# Source NSO environment
source /Users/gudeng/NCS-614/ncsrc
if [ $? -eq 0 ]; then
    echo "✅ NSO environment sourced successfully"
    echo "   NCS_DIR: $NCS_DIR"
    echo "   PYTHONPATH: $PYTHONPATH"
else
    echo "❌ Failed to source NSO environment"
    exit 1
fi

# Step 4: Check if NSO is running
echo "🔍 Step 4: Checking NSO status..."
ncs --status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ NSO is already running"
else
    echo "⚠️  NSO is not running. Starting NSO daemon..."
    ncs
    if [ $? -eq 0 ]; then
        echo "✅ NSO daemon started successfully"
        # Wait a moment for NSO to fully start
        sleep 3
    else
        echo "❌ Failed to start NSO daemon"
        exit 1
    fi
fi

# Step 5: Verify NSO connection
echo "🧪 Step 5: Testing NSO Python API connection..."
python -c "
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

try:
    m = maapi.Maapi()
    m.start_user_session('admin','test_context_1')
    t = m.start_write_trans()
    root = maagic.get_root(t)
    t.finish()
    print('✅ NSO Python API connection test successful')
except Exception as e:
    print(f'❌ NSO Python API connection test failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ NSO Python API is working correctly"
else
    echo "❌ NSO Python API test failed"
    exit 1
fi

# Step 6: Display final status
echo ""
echo "🎉 NSO Environment Setup Complete!"
echo "=================================="
echo "✅ Conda base environment: ACTIVE"
echo "✅ NSO environment: LOADED"
echo "✅ NSO daemon: RUNNING"
echo "✅ NSO Python API: READY"
echo ""
echo "📝 You can now:"
echo "   - Run Jupyter notebooks with NSO functionality"
echo "   - Execute NSO Python scripts"
echo "   - Use ncs CLI commands"
echo ""
echo "🔗 NSO Web UI: http://localhost:8080/login.html"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "To start Jupyter Lab, run:"
echo "   jupyter lab --ip=0.0.0.0 --port=8888 --no-browser"
