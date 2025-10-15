#!/bin/bash
# NSO Multi-Agent Production Deployment Script
# ============================================
# 
# This script automates the deployment of the NSO Multi-Agent Network Manager
# on a production host with real NCS devices.
#
# Usage: ./deploy_production.sh
#

echo "🚀 NSO Multi-Agent Production Deployment"
echo "========================================"

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Warning: Running as root. Consider using a non-root user."
fi

# Check Python installation
echo "🔍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python found: $PYTHON_VERSION"
else
    echo "❌ Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Check pip installation
echo "🔍 Checking pip installation..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found"
else
    echo "❌ pip3 not found. Please install pip first."
    exit 1
fi

# Check NSO installation
echo "🔍 Checking NSO installation..."
if [ -d "/opt/ncs/current" ]; then
    echo "✅ NSO found at /opt/ncs/current"
else
    echo "⚠️  NSO not found at /opt/ncs/current"
    echo "   Please ensure NSO is installed at the standard production path"
    echo "   or update the NSO_DIR in the configuration files"
fi

# Create deployment directory
DEPLOY_DIR="/opt/nso-agent"
echo "📁 Creating deployment directory: $DEPLOY_DIR"
sudo mkdir -p $DEPLOY_DIR
sudo chown $USER:$USER $DEPLOY_DIR

# Copy files to deployment directory
echo "📋 Copying files to deployment directory..."
cp nso_multi_agent_standalone_production.py $DEPLOY_DIR/
cp nso_connection_test_production.py $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp README_PRODUCTION.md $DEPLOY_DIR/
cp DEPLOYMENT_GUIDE_PRODUCTION.md $DEPLOY_DIR/
cp PRODUCTION_PACKAGE.md $DEPLOY_DIR/

echo "✅ Files copied to $DEPLOY_DIR"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd $DEPLOY_DIR
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test NSO connection
echo "🧪 Testing NSO connection..."
python3 nso_connection_test_production.py

if [ $? -eq 0 ]; then
    echo "✅ NSO connection test passed"
else
    echo "⚠️  NSO connection test failed"
    echo "   Please check your NSO configuration and try again"
    exit 1
fi

# Create systemd service file (optional)
echo "🔧 Creating systemd service file..."
sudo tee /etc/systemd/system/nso-agent.service > /dev/null <<EOF
[Unit]
Description=NSO Multi-Agent Network Manager
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/bin/python3 $DEPLOY_DIR/nso_multi_agent_standalone_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service file created"

# Enable and start service (optional)
read -p "🤔 Do you want to enable and start the service now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Enabling and starting service..."
    sudo systemctl daemon-reload
    sudo systemctl enable nso-agent
    sudo systemctl start nso-agent
    
    if [ $? -eq 0 ]; then
        echo "✅ Service started successfully"
        echo "📱 Access the web interface at: http://localhost:5606"
        echo "🔍 Check service status with: sudo systemctl status nso-agent"
        echo "📋 View logs with: sudo journalctl -u nso-agent -f"
    else
        echo "❌ Failed to start service"
        echo "   Check logs with: sudo journalctl -u nso-agent"
    fi
else
    echo "ℹ️  Service created but not started"
    echo "   To start manually: sudo systemctl start nso-agent"
    echo "   To enable auto-start: sudo systemctl enable nso-agent"
fi

echo ""
echo "🎉 Deployment completed!"
echo "========================"
echo "📁 Files deployed to: $DEPLOY_DIR"
echo "📱 Web interface: http://localhost:5606"
echo "🔧 Service management:"
echo "   - Start: sudo systemctl start nso-agent"
echo "   - Stop: sudo systemctl stop nso-agent"
echo "   - Status: sudo systemctl status nso-agent"
echo "   - Logs: sudo journalctl -u nso-agent -f"
echo ""
echo "📚 Documentation:"
echo "   - Quick start: README_PRODUCTION.md"
echo "   - Detailed guide: DEPLOYMENT_GUIDE_PRODUCTION.md"
echo "   - Package overview: PRODUCTION_PACKAGE.md"
echo ""
echo "🚀 Your NSO Multi-Agent Network Manager is ready for production!"
