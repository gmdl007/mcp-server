#!/bin/bash
# NSO Multi-Agent Standalone Deployment Script
# ============================================

set -e  # Exit on any error

echo "🚀 NSO Multi-Agent Standalone Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="nso_multi_agent"
APP_DIR="/opt/nso_multi_agent"
SERVICE_USER="nso-agent"
PYTHON_VERSION="3.11"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. This is not recommended for production."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check system requirements
check_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VER >= 3.11" | bc -l) -eq 1 ]]; then
            print_status "Python $PYTHON_VER found ✓"
        else
            print_error "Python 3.11+ required. Found: $PYTHON_VER"
            exit 1
        fi
    else
        print_error "Python 3 not found"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found ✓"
    else
        print_error "pip3 not found"
        exit 1
    fi
    
    # Check NSO
    if [[ -d "/opt/ncs/current" ]]; then
        print_status "NSO installation found at /opt/ncs/current ✓"
    else
        print_warning "NSO installation not found at /opt/ncs/current"
        print_warning "Please update NSO_DIR in the application configuration"
    fi
}

# Create application directory
create_app_directory() {
    print_step "Creating application directory..."
    
    if [[ ! -d "$APP_DIR" ]]; then
        sudo mkdir -p "$APP_DIR"
        print_status "Created directory: $APP_DIR"
    else
        print_status "Directory already exists: $APP_DIR"
    fi
    
    # Set permissions
    sudo chown -R $USER:$USER "$APP_DIR"
    print_status "Set directory permissions"
}

# Install Python dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Create virtual environment
    if [[ ! -d "$APP_DIR/venv" ]]; then
        python3 -m venv "$APP_DIR/venv"
        print_status "Created virtual environment"
    fi
    
    # Activate virtual environment
    source "$APP_DIR/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_status "Installed Python dependencies"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Copy application files
copy_files() {
    print_step "Copying application files..."
    
    # Copy main application
    if [[ -f "nso_multi_agent_standalone.py" ]]; then
        cp nso_multi_agent_standalone.py "$APP_DIR/"
        print_status "Copied main application file"
    else
        print_error "nso_multi_agent_standalone.py not found"
        exit 1
    fi
    
    # Copy README
    if [[ -f "README.md" ]]; then
        cp README.md "$APP_DIR/"
        print_status "Copied README.md"
    fi
    
    # Create logs directory
    mkdir -p "$APP_DIR/logs"
    print_status "Created logs directory"
}

# Create systemd service
create_systemd_service() {
    print_step "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=NSO Multi-Agent Standalone Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/nso_multi_agent_standalone.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    print_status "Created systemd service: $SERVICE_FILE"
    
    # Reload systemd
    sudo systemctl daemon-reload
    print_status "Reloaded systemd configuration"
}

# Create configuration file
create_config() {
    print_step "Creating configuration file..."
    
    CONFIG_FILE="$APP_DIR/config.py"
    
    cat > "$CONFIG_FILE" <<EOF
# NSO Multi-Agent Configuration
# ===========================

# NSO Configuration
NSO_DIR = "/opt/ncs/current"  # Update this path if needed
NSO_USERNAME = "admin"
NSO_PASSWORD = "admin"  # Change this to your NSO password

# Azure OpenAI Configuration
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
TOKEN_URL = "https://id.cisco.com/oauth2/default/v1/token"
LLM_ENDPOINT = "https://chat-ai.cisco.com"
APP_KEY = "your_app_key_here"

# Web Application Configuration
WEB_HOST = "0.0.0.0"
WEB_PORT = 5606
DEBUG_MODE = False

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "$APP_DIR/logs/nso_multi_agent.log"
EOF
    
    print_status "Created configuration file: $CONFIG_FILE"
    print_warning "Please update the configuration file with your actual credentials"
}

# Create startup script
create_startup_script() {
    print_step "Creating startup script..."
    
    STARTUP_SCRIPT="$APP_DIR/start.sh"
    
    cat > "$STARTUP_SCRIPT" <<EOF
#!/bin/bash
# NSO Multi-Agent Startup Script

cd "$APP_DIR"
source venv/bin/activate
python nso_multi_agent_standalone.py
EOF
    
    chmod +x "$STARTUP_SCRIPT"
    print_status "Created startup script: $STARTUP_SCRIPT"
}

# Create management script
create_management_script() {
    print_step "Creating management script..."
    
    MGMT_SCRIPT="$APP_DIR/manage.sh"
    
    cat > "$MGMT_SCRIPT" <<EOF
#!/bin/bash
# NSO Multi-Agent Management Script

APP_NAME="$APP_NAME"
APP_DIR="$APP_DIR"

case "\$1" in
    start)
        echo "Starting NSO Multi-Agent..."
        sudo systemctl start \$APP_NAME
        ;;
    stop)
        echo "Stopping NSO Multi-Agent..."
        sudo systemctl stop \$APP_NAME
        ;;
    restart)
        echo "Restarting NSO Multi-Agent..."
        sudo systemctl restart \$APP_NAME
        ;;
    status)
        sudo systemctl status \$APP_NAME
        ;;
    logs)
        sudo journalctl -u \$APP_NAME -f
        ;;
    enable)
        echo "Enabling NSO Multi-Agent to start on boot..."
        sudo systemctl enable \$APP_NAME
        ;;
    disable)
        echo "Disabling NSO Multi-Agent from starting on boot..."
        sudo systemctl disable \$APP_NAME
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|logs|enable|disable}"
        exit 1
        ;;
esac
EOF
    
    chmod +x "$MGMT_SCRIPT"
    print_status "Created management script: $MGMT_SCRIPT"
}

# Test the installation
test_installation() {
    print_step "Testing installation..."
    
    # Check if the application can be imported
    cd "$APP_DIR"
    source venv/bin/activate
    
    if python -c "import llama_index, quart, nest_asyncio; print('All imports successful')" 2>/dev/null; then
        print_status "Application dependencies test passed ✓"
    else
        print_error "Application dependencies test failed"
        exit 1
    fi
}

# Main deployment function
main() {
    print_status "Starting deployment process..."
    
    check_root
    check_requirements
    create_app_directory
    install_dependencies
    copy_files
    create_config
    create_startup_script
    create_management_script
    create_systemd_service
    test_installation
    
    echo
    print_status "🎉 Deployment completed successfully!"
    echo
    print_status "Next steps:"
    echo "1. Update configuration: $APP_DIR/config.py"
    echo "2. Start the service: $APP_DIR/manage.sh start"
    echo "3. Check status: $APP_DIR/manage.sh status"
    echo "4. View logs: $APP_DIR/manage.sh logs"
    echo "5. Access web interface: http://localhost:5606"
    echo
    print_warning "Remember to:"
    echo "- Update NSO credentials in config.py"
    echo "- Update Azure OpenAI credentials in config.py"
    echo "- Configure firewall for port 5606"
    echo "- Enable the service: $APP_DIR/manage.sh enable"
}

# Run main function
main "$@"
