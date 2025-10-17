#!/usr/bin/env python3
"""
Test script for NSO Agent with LlamaIndex
This script tests the NSO network management agent functionality
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
    logger.info(f"NCS_DIR: {os.environ.get('NCS_DIR')}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    return True

def test_nso_connection():
    """Test basic NSO connection"""
    logger.info("Testing NSO connection...")
    
    try:
        import ncs
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        
        # Create MAAPI session
        m = maapi.Maapi()
        m.start_user_session('admin', 'test_context_1')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        # List devices
        devices = []
        for device in root.devices.device:
            devices.append(device.name)
        
        logger.info(f"✅ NSO connection successful! Found {len(devices)} devices: {devices}")
        
        # Clean up
        t.finish()
        m.close()
        
        return True, devices
        
    except Exception as e:
        logger.error(f"❌ NSO connection failed: {e}")
        return False, []

def test_llamaindex_imports():
    """Test LlamaIndex imports"""
    logger.info("Testing LlamaIndex imports...")
    
    try:
        # Try basic imports first
        from llama_index.core.agent import ReActAgent
        from llama_index.core.tools import FunctionTool
        logger.info("✅ Basic LlamaIndex imports successful")
        
        # Try Azure OpenAI
        from llama_index.llms.azure_openai import AzureOpenAI
        logger.info("✅ Azure OpenAI import successful")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ LlamaIndex import failed: {e}")
        return False

def create_simple_nso_tools():
    """Create simple NSO tools for testing"""
    logger.info("Creating simple NSO tools...")
    
    try:
        import ncs
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        from llama_index.core.tools import FunctionTool
        
        def get_device_list():
            """Get list of all devices in NSO"""
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
                return f"Error getting devices: {e}"
        
        def get_device_status(device_name):
            """Get status of a specific device"""
            try:
                m = maapi.Maapi()
                m.start_user_session('admin', 'test_context_1')
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                device = root.devices.device[device_name]
                status = device.live_status.oper_state
                address = device.address
                
                t.finish()
                m.close()
                
                return f"Device {device_name}: Status={status}, Address={address}"
                
            except Exception as e:
                return f"Error getting device status: {e}"
        
        def execute_device_command(device_name, command):
            """Execute a command on a specific device"""
            try:
                m = maapi.Maapi()
                m.start_user_session('admin', 'test_context_1')
                t = m.start_write_trans()
                root = maagic.get_root(t)
                
                device = root.devices.device[device_name]
                result = device.live_status.connected
                
                t.finish()
                m.close()
                
                if result:
                    return f"Device {device_name} is connected. Command '{command}' would be executed."
                else:
                    return f"Device {device_name} is not connected. Cannot execute command '{command}'."
                
            except Exception as e:
                return f"Error executing command: {e}"
        
        # Create tools
        device_list_tool = FunctionTool.from_defaults(fn=get_device_list)
        device_status_tool = FunctionTool.from_defaults(fn=get_device_status)
        device_command_tool = FunctionTool.from_defaults(fn=execute_device_command)
        
        tools = [device_list_tool, device_status_tool, device_command_tool]
        
        logger.info("✅ NSO tools created successfully")
        return tools
        
    except Exception as e:
        logger.error(f"❌ Failed to create NSO tools: {e}")
        return []

def test_simple_agent():
    """Test a simple agent without external LLM"""
    logger.info("Testing simple agent...")
    
    try:
        from llama_index.core.agent import ReActAgent
        from llama_index.llms.openai import OpenAI
        
        # Create a simple mock LLM for testing
        from llama_index.core.llms import ChatMessage, MessageRole, LLM
        
        class MockLLM(LLM):
            def complete(self, prompt, **kwargs):
                # Simple mock response
                if "devices" in prompt.lower():
                    return "I can help you with device management. Let me check the available devices."
                elif "status" in prompt.lower():
                    return "I can check device status for you."
                else:
                    return "I'm here to help with network management tasks."
            
            def chat(self, messages, **kwargs):
                if isinstance(messages, list) and len(messages) > 0:
                    # Extract text from ChatMessage objects
                    text = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
                else:
                    text = str(messages)
                return self.complete(text)
            
            def stream_complete(self, prompt, **kwargs):
                # For streaming, just yield the complete response
                response = self.complete(prompt, **kwargs)
                yield response
        
        # Create tools
        tools = create_simple_nso_tools()
        if not tools:
            logger.error("❌ No tools available for agent")
            return False
        
        # Create agent with mock LLM
        mock_llm = MockLLM()
        agent = ReActAgent(tools=tools, llm=mock_llm, verbose=True)
        
        logger.info("✅ Simple agent created successfully")
        
        # Test agent with a simple query
        try:
            response = agent.chat("What devices are available?")
            logger.info(f"✅ Agent response: {response}")
            return True
        except Exception as e:
            logger.error(f"❌ Agent test failed: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Failed to create simple agent: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting NSO Agent Test")
    logger.info("=" * 50)
    
    # Step 1: Setup environment
    if not setup_environment():
        logger.error("❌ Environment setup failed")
        return False
    
    # Step 2: Test NSO connection
    nso_ok, devices = test_nso_connection()
    if not nso_ok:
        logger.error("❌ NSO connection test failed")
        return False
    
    # Step 3: Test LlamaIndex imports
    llamaindex_ok = test_llamaindex_imports()
    if not llamaindex_ok:
        logger.error("❌ LlamaIndex import test failed")
        return False
    
    # Step 4: Test simple agent
    agent_ok = test_simple_agent()
    if not agent_ok:
        logger.error("❌ Agent test failed")
        return False
    
    logger.info("🎉 All tests passed! NSO Agent is ready for use.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
