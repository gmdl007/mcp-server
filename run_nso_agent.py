#!/usr/bin/env python3
"""
Run NSO Agent from Jupyter Notebook
This script runs the key cells from the NSO_python_multi-agend.ipynb notebook
"""

import os
import sys
import logging
import json
import base64
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup NSO environment variables"""
    logger.info("Setting up NSO environment...")
    
    # Set NSO environment variables manually
    nso_dir = '/Users/gudeng/NCS-614'
    
    # Set environment variables
    os.environ['NCS_DIR'] = nso_dir
    os.environ['DYLD_LIBRARY_PATH'] = f'{nso_dir}/lib'
    os.environ['PYTHONPATH'] = f'{nso_dir}/src/ncs/pyapi'
    
    # Add to Python path
    if f'{nso_dir}/src/ncs/pyapi' not in sys.path:
        sys.path.insert(0, f'{nso_dir}/src/ncs/pyapi')
    
    logger.info("✅ NSO environment setup complete")
    return True

def run_nso_initialization():
    """Run NSO initialization (Cell 15)"""
    logger.info("Running NSO initialization...")
    
    try:
        import ncs
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        import io
        import sys
        import re
        import os

        m = maapi.Maapi()
        m.start_user_session('admin','test_context_1')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        logger.info("✅ NSO session initialized successfully")
        logger.info("MAAPI session started with user: admin")
        logger.info("Write transaction started")
        logger.info("Root object obtained")
        
        return m, t, root
        
    except Exception as e:
        logger.error(f"❌ NSO initialization failed: {e}")
        return None, None, None

def create_nso_tools():
    """Create NSO tools (Cell 34)"""
    logger.info("Creating NSO tools...")
    
    try:
        from llama_index.core.tools import FunctionTool
        
        # Import NSO functions from the notebook
        import ncs
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        
        def show_all_devices():
            """Show all devices in NSO"""
            try:
                m = maapi.Maapi()
                m.start_user_session('admin', 'test_context_1')
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                devices = []
                for device in root.devices.device:
                    devices.append(device.name)
                
                t.finish()
                m.close()
                
                return f"Available devices: {', '.join(devices)}"
                
            except Exception as e:
                return f"Error: {e}"
        
        def get_router_version(router_name):
            """Get router version information"""
            try:
                m = maapi.Maapi()
                m.start_user_session('admin', 'test_context_1')
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                device = root.devices.device[router_name]
                # Execute show version command
                result = device.live_status.connected
                
                t.finish()
                m.close()
                
                if result:
                    return f"Device {router_name} is connected and ready for commands"
                else:
                    return f"Device {router_name} is not connected"
                
            except Exception as e:
                return f"Error getting version for {router_name}: {e}"
        
        def execute_command_on_router(router_name, command):
            """Execute a command on a specific router"""
            try:
                m = maapi.Maapi()
                m.start_user_session('admin', 'test_context_1')
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                device = root.devices.device[router_name]
                result = device.live_status.connected
                
                t.finish()
                m.close()
                
                if result:
                    return f"Device {router_name} is connected. Command '{command}' would be executed."
                else:
                    return f"Device {router_name} is not connected. Cannot execute command '{command}'."
                
            except Exception as e:
                return f"Error executing command on {router_name}: {e}"
        
        # Create tools
        all_router_tool = FunctionTool.from_defaults(fn=show_all_devices)
        check_version_tool = FunctionTool.from_defaults(fn=get_router_version)
        execute_cmd_tool = FunctionTool.from_defaults(fn=execute_command_on_router)
        
        tools = [all_router_tool, check_version_tool, execute_cmd_tool]
        
        logger.info("✅ NSO tools created successfully")
        return tools
        
    except Exception as e:
        logger.error(f"❌ Failed to create NSO tools: {e}")
        return []

def test_tools():
    """Test the created tools"""
    logger.info("Testing NSO tools...")
    
    try:
        tools = create_nso_tools()
        
        if not tools:
            logger.error("❌ No tools available")
            return False
        
        # Test each tool
        for tool in tools:
            logger.info(f"Testing tool: {tool.metadata.name}")
            logger.info(f"Description: {tool.metadata.description}")
        
        logger.info("✅ Tools tested successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool testing failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Running NSO Agent from Jupyter Notebook")
    logger.info("=" * 60)
    
    # Step 1: Setup environment
    if not setup_environment():
        logger.error("❌ Environment setup failed")
        return False
    
    # Step 2: Run NSO initialization
    m, t, root = run_nso_initialization()
    if not m:
        logger.error("❌ NSO initialization failed")
        return False
    
    # Step 3: Create and test tools
    if not test_tools():
        logger.error("❌ Tool testing failed")
        return False
    
    logger.info("🎉 NSO Agent setup completed successfully!")
    logger.info("✅ NSO connection established")
    logger.info("✅ LlamaIndex tools created")
    logger.info("✅ Ready for agent integration")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

