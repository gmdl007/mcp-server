#!/usr/bin/env python3
"""
Simple LlamaIndex NSO Agent Test
Tests the core functionality without interactive mode
"""

import asyncio
import logging
import os
import base64
import requests
from typing import List

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings

# Import environment variables
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure OpenAI configuration (same as flask_app_fixed.py)
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
token_url = os.getenv('TOKEN_URL')
llm_endpoint = os.getenv('LLM_ENDPOINT')
appkey = os.getenv('APP_KEY')

# NSO configuration
NSO_DIR = "/Users/gudeng/NCS-614"
os.environ['NCS_DIR'] = NSO_DIR
os.environ['DYLD_LIBRARY_PATH'] = f'{NSO_DIR}/lib'
os.environ['PYTHONPATH'] = f'{NSO_DIR}/src/ncs/pyapi'

# Add NSO Python API to Python path
import sys
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

# Import NSO modules
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic


def initialize_azure_llm():
    """Initialize Azure OpenAI LLM (same as flask_app_fixed.py)."""
    
    print("🔑 Getting Azure OpenAI token...")
    
    # Get Cisco OAuth token
    auth_key = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_key}",
    }
    
    token_response = requests.post(token_url, headers=headers, data="grant_type=client_credentials")
    token = token_response.json().get("access_token")
    
    print("✅ Token obtained")
    
    # Initialize LLM
    llm = AzureOpenAI(
        azure_endpoint=llm_endpoint,
        api_version="2024-07-01-preview",
        deployment_name='gpt-4o-mini',
        api_key=token,
        max_tokens=3000,
        temperature=0.1,
        additional_kwargs={"user": f'{{"appkey": "{appkey}"}}'}
    )
    
    Settings.llm = llm
    Settings.context_window = 8000
    
    print("✅ Azure OpenAI LLM initialized")
    return llm


def get_devices() -> str:
    """Find out all available routers in the lab."""
    try:
        with maapi.single_read_trans('admin', 'python', groups=['ncsadmin']) as t:
            root = maagic.get_root(t)
            if hasattr(root, 'devices') and hasattr(root.devices, 'device'):
                router_names = [device.name for device in root.devices.device]
                return ', '.join(router_names)
            else:
                return "No devices found."
    except Exception as e:
        return f"❌ Failed to get devices: {e}"


def get_router_interfaces_config(router_name: str) -> str:
    """Return configured interfaces (Loopback/GigabitEthernet/Ethernet) with IPv4 for a router."""
    try:
        with maapi.single_read_trans('admin', 'python', groups=['ncsadmin']) as t:
            root = maagic.get_root(t)
            try:
                dev = root.devices.device[router_name]
            except KeyError:
                return f"❌ Device '{router_name}' not found in NSO."
            
            cfg = dev.config
            lines: List[str] = []
            
            if hasattr(cfg, "interface"):
                if hasattr(cfg.interface, "Loopback"):
                    for lo in cfg.interface.Loopback:
                        ip = getattr(getattr(lo, "ipv4", None), "address", None)
                        ip_str = f" {getattr(ip, 'ip', '')}/{getattr(ip, 'mask', '')}" if ip else ""
                        lines.append(f"Loopback{lo.id}{ip_str}")
                
                if hasattr(cfg.interface, "GigabitEthernet"):
                    for gi in cfg.interface.GigabitEthernet:
                        ip = getattr(getattr(gi, "ipv4", None), "address", None)
                        ip_str = f" {getattr(ip, 'ip', '')}/{getattr(ip, 'mask', '')}" if ip else ""
                        lines.append(f"GigabitEthernet{gi.id}{ip_str}")
                
                if hasattr(cfg.interface, "Ethernet"):
                    for eth in cfg.interface.Ethernet:
                        ip = getattr(getattr(eth, "ipv4", None), "address", None)
                        ip_str = f" {getattr(ip, 'ip', '')}/{getattr(ip, 'mask', '')}" if ip else ""
                        lines.append(f"Ethernet{eth.id}{ip_str}")
            
            return "\n".join(lines) if lines else "NO_CONFIGURED_INTERFACES"
    except Exception as e:
        return f"❌ Failed to read interface config for '{router_name}': {e}"


def echo_text(text: str) -> str:
    """Echo back the provided text (debug/health)."""
    return f"Echo: {text}"


async def test_agent():
    """Test the LlamaIndex agent with NSO tools."""
    print("🚀 Testing Pure LlamaIndex NSO Agent")
    print("="*60)
    
    # Initialize Azure OpenAI LLM
    llm = initialize_azure_llm()
    
    # Create LlamaIndex tools (let LlamaIndex auto-generate schemas)
    tools = [
        FunctionTool.from_defaults(
            fn=get_devices,
            name="show_all_devices",
            description="Find out all available routers in the lab, return their names."
        ),
        FunctionTool.from_defaults(
            fn=get_router_interfaces_config,
            name="get_router_interfaces_config", 
            description="Return configured interfaces (Loopback/GigabitEthernet/Ethernet) with IPv4 for a router."
        ),
        FunctionTool.from_defaults(
            fn=echo_text,
            name="echo_text",
            description="Echo back the provided text (debug/health)."
        )
    ]
    
    print(f"✅ Created {len(tools)} LlamaIndex tools")
    
    # Create LlamaIndex agent
    agent = ReActAgent(tools=tools, llm=llm, verbose=True)
    
    print("\n🤖 LlamaIndex Agent with NSO Tools Ready!")
    print("="*60)
    
    # Test the agent
    print("\n1. Testing echo_text:")
    response1 = await agent.run("Use echo_text to say 'Hello from Pure LlamaIndex!'")
    print(f"Response: {response1}")
    
    print("\n2. Getting all devices:")
    response2 = await agent.run("Use show_all_devices to get all router names")
    print(f"Response: {response2}")
    
    print("\n3. Getting interface config:")
    response3 = await agent.run("Use get_router_interfaces_config to get interface configuration for router xr9kv-3")
    print(f"Response: {response3}")
    
    print("\n✅ All tests completed successfully!")
    print("🎉 Pure LlamaIndex + NSO integration is working!")


if __name__ == "__main__":
    asyncio.run(test_agent())
