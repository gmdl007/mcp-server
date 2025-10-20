#!/usr/bin/env python3
"""
LlamaIndex NSO MCP Server
A proper MCP server built with LlamaIndex tools and NSO integration
"""

import asyncio
import logging
import os
import base64
import requests
import sys
from typing import Any, Dict, List

# LlamaIndex imports
from llama_index.core.tools import FunctionTool
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings

# MCP imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool

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
nso_pyapi_path = f'{NSO_DIR}/src/ncs/pyapi'
if nso_pyapi_path not in sys.path:
    sys.path.insert(0, nso_pyapi_path)

# Import NSO modules
import ncs
import ncs.maapi as maapi
import ncs.maagic as maagic


def initialize_azure_llm():
    """Initialize Azure OpenAI LLM (same as flask_app_fixed.py)."""
    
    logger.info("🔑 Getting Azure OpenAI token...")
    
    # Get Cisco OAuth token
    auth_key = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_key}",
    }
    
    token_response = requests.post(token_url, headers=headers, data="grant_type=client_credentials")
    token = token_response.json().get("access_token")
    
    logger.info("✅ Token obtained")
    
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
    
    logger.info("✅ Azure OpenAI LLM initialized")
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


# Create LlamaIndex tools (let LlamaIndex auto-generate schemas)
llama_tools = [
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

# Create MCP server
server = Server("llama-index-nso-mcp")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List all available NSO tools using LlamaIndex FunctionTools."""
    logger.debug("📋 list_tools (llama-index) invoked")
    
    tools = []
    for llama_tool in llama_tools:
        # Convert LlamaIndex FunctionTool to MCP Tool
        # Use auto-generated schema from LlamaIndex
        mcp_tool = Tool(
            name=llama_tool.metadata.name,
            description=llama_tool.metadata.description,
            inputSchema={"type": "object", "properties": {}, "required": []}  # Simplified schema
        )
        tools.append(mcp_tool)
    
    logger.debug(f"📋 Returning {len(tools)} tools")
    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls using LlamaIndex FunctionTools."""
    logger.debug(f"🔧 llama-index call_tool name={name} args={arguments}")
    
    try:
        # Find the corresponding LlamaIndex tool
        llama_tool = None
        for tool in llama_tools:
            if tool.metadata.name == name:
                llama_tool = tool
                break
        
        if not llama_tool:
            return CallToolResult(content=[TextContent(type="text", text=f"❌ Unknown tool: {name}")])
        
        # Execute the LlamaIndex tool
        logger.debug(f"🔧 Calling LlamaIndex tool with args: {arguments}")
        result = llama_tool.call(**arguments)
        logger.debug(f"🔧 LlamaIndex tool result: {result}")
        logger.debug(f"🔧 Result type: {type(result)}")
        
        # Extract the actual content from ToolOutput
        if hasattr(result, 'content'):
            actual_result = result.content
        elif hasattr(result, 'output'):
            actual_result = result.output
        else:
            actual_result = str(result)
        
        logger.debug(f"🔧 Actual result: {actual_result}")
        
        logger.debug(f"✅ Tool {name} executed successfully")
        return CallToolResult(content=[TextContent(type="text", text=str(actual_result))])
        
    except Exception as e:
        logger.exception(f"❌ Error executing tool {name}")
        return CallToolResult(content=[TextContent(type="text", text=f"❌ Error: {e}")])


async def main():
    """Main entry point for the LlamaIndex NSO MCP Server."""
    logger.info("🚀 Starting LlamaIndex NSO MCP Server...")
    
    # Initialize Azure OpenAI LLM
    llm = initialize_azure_llm()
    
    logger.info(f"✅ Created {len(llama_tools)} LlamaIndex tools")
    logger.info("🤖 LlamaIndex NSO MCP Server Ready!")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="llama-index-nso-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())