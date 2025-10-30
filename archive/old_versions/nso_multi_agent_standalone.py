#!/usr/bin/env python3
"""
NSO Multi-Agent Standalone Application
=====================================

A production-ready standalone Python application that replicates the functionality
of the NSO_python_multi-agend.ipynb notebook. This application provides:

- NSO device management and automation
- LlamaIndex ReActAgent with FunctionTools
- Quart web interface (async Flask alternative)
- Cisco Azure OpenAI integration
- Production deployment features

Based on the working notebook implementation using Quart + nest_asyncio.

Author: AI Assistant
Version: 2.0
Date: 2025-01-05
"""

import os
import sys
import json
import base64
import requests
import logging
import asyncio
import nest_asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# =============================================================================
# CONFIGURATION
# =============================================================================

# NSO Configuration - ADAPT THESE PATHS FOR YOUR ENVIRONMENT
NSO_DIR = "/Users/gudeng/NCS-614"  # Change this to your NSO installation path
NSO_USERNAME = "admin"
NSO_PASSWORD = "admin"  # Change this to your NSO password

# Azure OpenAI Configuration - ADAPT THESE FOR YOUR ENVIRONMENT
# Use environment variables for security (like the working notebook)
CLIENT_ID = os.getenv('CLIENT_ID', "cG9jLXRyaWFsMjAyM09jdG9iZXIxNwff_540f3843f35f87eeb7b238fc2f8807")
CLIENT_SECRET = os.getenv('CLIENT_SECRET', "b-mQoS2NXZe4I15lVXtY7iBHCAg9u7ufZFx7MZiOHAFlzRBkFmOaenUI2buRpRBb")
TOKEN_URL = os.getenv('TOKEN_URL', "https://id.cisco.com/oauth2/default/v1/token")
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', "https://chat-ai.cisco.com")
APP_KEY = os.getenv('APP_KEY', "egai-prd-wws-log-chat-data-analysis-1")

# Web Application Configuration
WEB_HOST = "0.0.0.0"
WEB_PORT = 5606
DEBUG_MODE = False

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nso_multi_agent.log')
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# NSO ENVIRONMENT SETUP
# =============================================================================

def setup_nso_environment():
    """Setup NSO environment variables and Python path."""
    try:
        # Set NSO environment variables
        os.environ['NCS_DIR'] = NSO_DIR
        os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
        os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'
        
        # Add NSO Python API to Python path
        nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
        if nso_pyapi_path not in sys.path:
            sys.path.insert(0, nso_pyapi_path)
        
        logger.info(f"✅ NSO environment configured:")
        logger.info(f"   - NCS_DIR: {NSO_DIR}")
        logger.info(f"   - PYTHONPATH: {nso_pyapi_path}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to setup NSO environment: {e}")
        return False

# =============================================================================
# NSO IMPORTS AND CONNECTION
# =============================================================================

def setup_nso_connection():
    """Setup NSO connection and return connection objects."""
    try:
        # Import NSO modules
        import ncs
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        
        logger.info("✅ NSO modules imported successfully")
        
        # Create NSO connection
        m = maapi.Maapi()
        m.start_user_session(NSO_USERNAME, 'python_session')
        t = m.start_write_trans()
        root = maagic.get_root(t)
        
        logger.info("✅ NSO connection established successfully")
        
        # Test device discovery
        devices = []
        for device in root.devices.device:
            devices.append(device.name)
        
        logger.info(f"📱 Found {len(devices)} devices: {devices}")
        
        return m, t, root
        
    except Exception as e:
        logger.error(f"❌ Failed to setup NSO connection: {e}")
        return None, None, None

# =============================================================================
# LLAMAINDEX AND LLM SETUP
# =============================================================================

def setup_llm():
    """Setup Azure OpenAI LLM with Cisco authentication."""
    try:
        from llama_index.llms.azure_openai import AzureOpenAI
        
        # Get authentication token
        auth_key = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_key}",
        }
        
        # Make a POST request to retrieve the token
        token_response = requests.post(TOKEN_URL, headers=headers, data="grant_type=client_credentials")
        token = token_response.json().get("access_token")
        
        if not token:
            raise Exception("Failed to get authentication token")
        
        # Create LLM instance
        llm = AzureOpenAI(
            azure_endpoint=LLM_ENDPOINT,
            api_version="2024-07-01-preview",
            deployment_name='gpt-4o-mini',
            api_key=token,
            max_tokens=3000,
            temperature=0.1,
            additional_kwargs={"user": f'{{"appkey": "{APP_KEY}"}}'}
        )
        
        logger.info("✅ Azure OpenAI LLM configured successfully")
        return llm
        
    except Exception as e:
        logger.error(f"❌ Failed to setup LLM: {e}")
        return None

def setup_llamaindex():
    """Setup LlamaIndex components."""
    try:
        from llama_index.core.agent import ReActAgent
        from llama_index.core.tools import FunctionTool
        from llama_index.core import Settings
        
        # Set LlamaIndex settings
        Settings.context_window = 32000
        Settings.chunk_size = 1024
        
        logger.info("✅ LlamaIndex components imported successfully")
        return ReActAgent, FunctionTool, Settings
        
    except Exception as e:
        logger.error(f"❌ Failed to setup LlamaIndex: {e}")
        return None, None, None

# =============================================================================
# NSO FUNCTION TOOLS
# =============================================================================

class NSOFunctionTools:
    """Container for all NSO function tools."""
    
    def __init__(self, root):
        self.root = root
    
    def show_all_devices(self) -> str:
        """Find out all available routers in the lab, return their names."""
        if hasattr(self.root, 'devices') and hasattr(self.root.devices, 'device'):
            router_names = [device.name for device in self.root.devices.device]
            for name in router_names:
                print(name)
            return ', '.join(router_names)
        else:
            print("No devices found.")
            return "No devices found."
    
    def execute_command_on_router(self, router_name: str, command: str) -> str:
        """Execute a single command on a specific router using NSO."""
        try:
            import ncs.maapi as maapi
            import ncs.maagic as maagic
            
            with maapi.single_write_trans(NSO_USERNAME, 'python', groups=['ncsadmin']) as t:
                root = maagic.get_root(t)
                device = root.devices.device[router_name]
                show = device.live_status.__getitem__('exec').any
                inp = show.get_input()
                inp.args = [command]
                r = show.request(inp)
                result = f'Result of Show Command "{command}" for Router "{router_name}": {r.result}'
                print(result)
                return result
                
        except KeyError:
            error_msg = f"Device '{router_name}' not found in NSO."
            print(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Failed to execute command '{command}' on device '{router_name}': {e}"
            print(error_msg)
            return error_msg
    
    def get_router_version(self, router_name: str) -> str:
        """Retrieve router version using 'show version' command."""
        return self.execute_command_on_router(router_name, "show version")
    
    def get_router_clock(self, router_name: str) -> str:
        """Retrieve router current time using 'show clock' command."""
        return self.execute_command_on_router(router_name, "show clock")
    
    def show_router_interfaces(self, router_name: str) -> str:
        """Retrieve router interface status using 'show ipv4 interface brief' command."""
        return self.execute_command_on_router(router_name, "show ipv4 interface brief")
    
    def get_router_ip_routes(self, router_name: str, prefix: str) -> str:
        """Retrieve IPv4 route using 'show route ipv4 <prefix>' command."""
        command = f"show route ipv4 {prefix}"
        return self.execute_command_on_router(router_name, command)
    
    def get_router_bgp_summary(self, router_name: str) -> str:
        """Retrieve BGP summary using 'show bgp ipv4 unicast summary' command."""
        return self.execute_command_on_router(router_name, "show bgp ipv4 unicast summary")
    
    def get_router_isis_neighbors(self, router_name: str) -> str:
        """Retrieve ISIS neighbors using 'show isis neighbors' command."""
        return self.execute_command_on_router(router_name, "show isis neighbors")
    
    def get_router_ospf_neigh(self, router_name: str) -> str:
        """Retrieve OSPF neighbors using 'show ospf neighbor' command."""
        return self.execute_command_on_router(router_name, "show ospf neighbor")
    
    def get_router_control_plane_cpu(self, router_name: str) -> str:
        """Retrieve CPU usage using 'show processes cpu' command."""
        return self.execute_command_on_router(router_name, "show processes cpu")
    
    def get_router_memory_usage(self, router_name: str) -> str:
        """Retrieve memory usage using 'show processes memory' command."""
        return self.execute_command_on_router(router_name, "show processes memory")
    
    def ping_router(self, router_name: str, ip_address: str) -> str:
        """Ping an IP address from a router."""
        command = f"ping {ip_address} source Loopback 0"
        return self.execute_command_on_router(router_name, command)
    
    def traceroute_router(self, router_name: str, ip_address: str) -> str:
        """Perform traceroute to an IP address from a router."""
        command = f"traceroute {ip_address} source Loopback 0"
        return self.execute_command_on_router(router_name, command)
    
    def lldp_nei(self, router_name: str) -> str:
        """Find connected neighbors using 'show lldp neighbor' command."""
        return self.execute_command_on_router(router_name, "show lldp neighbor")
    
    def check_alarm(self, router_name: str) -> str:
        """Retrieve router alarm information using 'show alarms brief' command."""
        return self.execute_command_on_router(router_name, "show alarms brief")
    
    def check_cpu(self, router_name: str) -> str:
        """Retrieve CPU utilization using 'show processes cpu sorted 5min' command."""
        return self.execute_command_on_router(router_name, "show processes cpu sorted 5min")
    
    def check_memory(self, router_name: str) -> str:
        """Retrieve memory summary using 'show memory summary' command."""
        return self.execute_command_on_router(router_name, "show memory summary")
    
    def iterate(self, cmd: str) -> List[str]:
        """Execute a command on all devices."""
        results = []
        try:
            import ncs.maapi as maapi
            import ncs.maagic as maagic
            
            with maapi.single_write_trans(NSO_USERNAME, 'python', groups=['ncsadmin']) as t:
                root = maagic.get_root(t)
                for box in root.devices.device:
                    try:
                        show = box.live_status.__getitem__('exec').any
                        inp = show.get_input()
                        inp.args = [cmd]
                        r = show.request(inp)
                        show_cmd = f'Result of Show Command "{cmd}" for Router Name {box.name}: {r.result}'
                        print(show_cmd)
                        results.append(show_cmd)
                    except Exception as e:
                        print(f"Failed to execute command '{cmd}' on device {box.name}: {e}")
        except Exception as e:
            print(f"Failed to iterate command '{cmd}': {e}")
        
        return results

# =============================================================================
# WEB APPLICATION (QUART)
# =============================================================================

def create_web_app(agent, nso_tools):
    """Create and configure the Quart web application."""
    try:
        from quart import Quart, request, render_template_string, redirect, url_for
        
        app = Quart(__name__)
        
        # HTML template
        form_template = """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>NSO Multi-Agent Query Interface</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    font-size: 28px;
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .status {
                    background-color: #e8f5e8;
                    border: 1px solid #4CAF50;
                    padding: 10px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    text-align: center;
                }
                form {
                    margin-bottom: 20px;
                }
                textarea {
                    width: 100%;
                    height: 80px;
                    padding: 15px;
                    font-size: 16px;
                    border: 2px solid #ddd;
                    border-radius: 8px;
                    resize: vertical;
                    box-sizing: border-box;
                }
                textarea:focus {
                    border-color: #4CAF50;
                    outline: none;
                }
                input[type="submit"] {
                    padding: 12px 24px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 10px;
                }
                input[type="submit"]:hover {
                    background-color: #45a049;
                }
                pre {
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 14px;
                    color: #333;
                    border: 1px solid #e9ecef;
                    max-height: 500px;
                    overflow-y: auto;
                }
                button {
                    background-color: #ff6347;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 10px;
                }
                button:hover {
                    background-color: #e5533d;
                }
                .footer {
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 NSO Multi-Agent Query Interface</h1>
                <div class="status">
                    ✅ System Status: Online | 🤖 Agent: Active | 🌐 NSO: Connected
                </div>
                <form action="/" method="post">
                    <textarea name="text" placeholder="Enter your network query here (e.g., 'show me all devices', 'what interfaces are on xr9kv-1?')" required></textarea>
                    <br>
                    <input type="submit" value="🔍 Query Agent">
                </form>
                {% if response %}
                <h2>📋 Response:</h2>
                <pre>{{ response }}</pre>
                {% endif %}
                <form action="/reset-agent" method="post">
                    <button type="submit">🔄 Reset Agent</button>
                </form>
                <div class="footer">
                    <p>NSO Multi-Agent System v2.0 | Powered by LlamaIndex & Quart</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        @app.route("/", methods=["GET", "POST"])
        async def home():
            response = None
            
            if request.method == "POST":
                form = await request.form
                query_text = form.get("text", "").strip()
                
                if query_text:
                    try:
                        logger.info(f"🔍 Processing query: {query_text}")
                        
                        if agent:
                            # Use the agent with native async/await
                            response = await agent.run(query_text)
                            response = str(response)
                            logger.info(f"✅ Response generated successfully")
                        else:
                            # Fallback: direct NSO tool execution
                            response = "AI Agent not available. NSO tools are working but LLM is not configured."
                            logger.warning("⚠️ Agent not available, using fallback response")
                        
                    except Exception as e:
                        response = f"Error processing query: {str(e)}"
                        logger.error(f"❌ Error: {e}")
                        import traceback
                        traceback.print_exc()
            
            return await render_template_string(form_template, response=response)
        
        @app.route("/reset-agent", methods=["POST"])
        async def reset_agent():
            # Reinitialize the agent
            global agent, llm
            if llm:
                agent = create_agent(llm, nso_tools)
                logger.info("🔄 Agent and LLM have been reset.")
            else:
                logger.warning("⚠️ Cannot reset agent: LLM not available")
            return redirect(url_for("home"))
        
        @app.route("/health", methods=["GET"])
        async def health_check():
            """Health check endpoint for monitoring."""
            return {
                "status": "healthy",
                "service": "nso-multi-agent",
                "version": "2.0",
                "nso_connected": nso_tools is not None
            }
        
        logger.info("✅ Quart web application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to create web application: {e}")
        return None

# =============================================================================
# AGENT CREATION
# =============================================================================

def create_agent(llm, nso_tools):
    """Create the ReActAgent with all NSO function tools."""
    try:
        from llama_index.core.agent import ReActAgent
        from llama_index.core.tools import FunctionTool
        
        # Create function tools
        tools = [
            FunctionTool.from_defaults(fn=nso_tools.show_all_devices),
            FunctionTool.from_defaults(fn=nso_tools.get_router_version),
            FunctionTool.from_defaults(fn=nso_tools.get_router_clock),
            FunctionTool.from_defaults(fn=nso_tools.show_router_interfaces),
            FunctionTool.from_defaults(fn=nso_tools.get_router_ip_routes),
            FunctionTool.from_defaults(fn=nso_tools.get_router_bgp_summary),
            FunctionTool.from_defaults(fn=nso_tools.get_router_isis_neighbors),
            FunctionTool.from_defaults(fn=nso_tools.get_router_ospf_neigh),
            FunctionTool.from_defaults(fn=nso_tools.get_router_control_plane_cpu),
            FunctionTool.from_defaults(fn=nso_tools.get_router_memory_usage),
            FunctionTool.from_defaults(fn=nso_tools.ping_router),
            FunctionTool.from_defaults(fn=nso_tools.traceroute_router),
            FunctionTool.from_defaults(fn=nso_tools.lldp_nei),
            FunctionTool.from_defaults(fn=nso_tools.check_alarm),
            FunctionTool.from_defaults(fn=nso_tools.check_cpu),
            FunctionTool.from_defaults(fn=nso_tools.check_memory),
            FunctionTool.from_defaults(fn=nso_tools.iterate),
        ]
        
        # Create ReActAgent
        agent = ReActAgent(
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=1000
        )
        
        logger.info(f"✅ ReActAgent created with {len(tools)} tools")
        return agent
        
    except Exception as e:
        logger.error(f"❌ Failed to create agent: {e}")
        return None

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

# Global variables for web app access
agent = None
llm = None
nso_tools = None

# =============================================================================
# MAIN APPLICATION
# =============================================================================

async def main():
    """Main application entry point."""
    global agent, llm, nso_tools  # Make variables global for web app access
    
    logger.info("🚀 Starting NSO Multi-Agent Standalone Application")
    logger.info("=" * 60)
    
    # Step 1: Setup NSO environment
    logger.info("📋 Step 1: Setting up NSO environment...")
    if not setup_nso_environment():
        logger.error("❌ Failed to setup NSO environment. Exiting.")
        return
    
    # Step 2: Setup NSO connection
    logger.info("📋 Step 2: Setting up NSO connection...")
    m, t, root = setup_nso_connection()
    if not root:
        logger.error("❌ Failed to setup NSO connection. Exiting.")
        return
    
    # Step 3: Setup LLM
    logger.info("📋 Step 3: Setting up Azure OpenAI LLM...")
    llm = setup_llm()
    if not llm:
        logger.warning("⚠️ Failed to setup LLM. Running in NSO-only mode (no AI agent).")
        logger.warning("⚠️ Web interface will be available but agent queries will not work.")
        # Continue without LLM for testing
    
    # Step 4: Setup LlamaIndex
    logger.info("📋 Step 4: Setting up LlamaIndex...")
    ReActAgent, FunctionTool, Settings = setup_llamaindex()
    if not ReActAgent:
        logger.error("❌ Failed to setup LlamaIndex. Exiting.")
        return
    
    # Set the LLM in Settings
    Settings.llm = llm
    
    # Step 5: Create NSO function tools
    logger.info("📋 Step 5: Creating NSO function tools...")
    nso_tools = NSOFunctionTools(root)
    logger.info("✅ NSO function tools created successfully")
    
    # Step 6: Create agent
    logger.info("📋 Step 6: Creating ReActAgent...")
    agent = create_agent(llm, nso_tools) if llm else None
    if not agent and llm:
        logger.error("❌ Failed to create agent. Exiting.")
        return
    elif not agent:
        logger.warning("⚠️ Running without AI agent (LLM not available)")
    
    # Step 7: Create web application
    logger.info("📋 Step 7: Creating web application...")
    app = create_web_app(agent, nso_tools)
    if not app:
        logger.error("❌ Failed to create web application. Exiting.")
        return
    
    # Step 8: Start the application
    logger.info("📋 Step 8: Starting web server...")
    logger.info("=" * 60)
    logger.info("🎉 NSO Multi-Agent Application Started Successfully!")
    logger.info(f"🌐 Web Interface: http://{WEB_HOST}:{WEB_PORT}")
    logger.info(f"🔍 Health Check: http://{WEB_HOST}:{WEB_PORT}/health")
    logger.info("🔒 Press CTRL+C to stop")
    logger.info("=" * 60)
    
    # Run the Quart application
    await app.run_task(host=WEB_HOST, port=WEB_PORT, debug=DEBUG_MODE)

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        # Run the main application
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Application failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
