#!/usr/bin/env python3
"""
LlamaIndex MCP Client for NSO Tools
Uses LlamaIndex's native MCP client capabilities
"""

import asyncio
import logging
import os
import base64
import requests
from typing import List

from llama_index.core.agent import ReActAgent
from llama_index.core.llms import LLM
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings
from llama_index.mcp import BasicMCPClient, get_tools_from_mcp_url

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


def initialize_azure_llm():
    """Initialize Azure OpenAI LLM (same as flask_app_fixed.py)."""
    
    # Get Cisco OAuth token
    auth_key = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_key}",
    }
    
    token_response = requests.post(token_url, headers=headers, data="grant_type=client_credentials")
    token = token_response.json().get("access_token")
    
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
    
    return llm


async def create_llama_mcp_client():
    """Create LlamaIndex MCP client connected to NSO server."""
    
    print("🚀 Creating LlamaIndex MCP Client for NSO...")
    
    try:
        # Method 1: Direct MCP client connection
        print("📡 Connecting to LlamaIndex NSO MCP Server...")
        
        # Create MCP client for stdio connection
        mcp_client = BasicMCPClient(
            server_command="/Users/gudeng/MCP_Server/src/mcp_server/start_llama_index_nso_mcp.sh",
            server_args=[],
            server_env={
                "NCS_DIR": "/Users/gudeng/NCS-614",
                "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
            }
        )
        
        # Get tools from MCP server
        tools = await mcp_client.get_tools()
        
        print(f"✅ Connected! Found {len(tools)} tools:")
        for tool in tools:
            print(f"   • {tool.metadata.name}: {tool.metadata.description}")
        
        return mcp_client, tools
        
    except Exception as e:
        print(f"❌ Error creating MCP client: {e}")
        return None, []


async def demo_llama_mcp_tools():
    """Demonstrate using LlamaIndex MCP tools."""
    
    # Create MCP client
    mcp_client, tools = await create_llama_mcp_client()
    
    if not mcp_client or not tools:
        print("❌ Failed to create MCP client")
        return
    
    # Create LlamaIndex agent with MCP tools
    try:
        llm = initialize_azure_llm()
        agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)
        
        print("\n" + "="*60)
        print("🤖 LlamaIndex Agent with MCP Tools Ready!")
        print("="*60)
        
        # Test the tools through the agent
        print("\n1. Testing echo_text:")
        response1 = await agent.achat("Use echo_text to say 'Hello from LlamaIndex MCP!'")
        print(f"Response: {response1}")
        
        print("\n2. Getting all devices:")
        response2 = await agent.achat("Use show_all_devices to get all router names")
        print(f"Response: {response2}")
        
        print("\n3. Getting interface config:")
        response3 = await agent.achat("Use get_router_interfaces_config to get interface configuration for router xr9kv-3")
        print(f"Response: {response3}")
        
        print("\n" + "="*60)
        print("💬 Interactive Mode - Ask questions about your network!")
        print("Type 'quit' to exit")
        print("="*60)
        
        # Interactive mode
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                response = await agent.achat(user_input)
                print(f"Agent: {response}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        # Clean up
        await mcp_client.close()
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")


async def direct_tool_usage():
    """Demonstrate direct tool usage without agent."""
    
    print("🔧 Direct MCP Tool Usage Demo")
    print("="*50)
    
    mcp_client, tools = await create_llama_mcp_client()
    
    if not mcp_client or not tools:
        return
    
    try:
        # Find specific tools
        echo_tool = None
        devices_tool = None
        interfaces_tool = None
        
        for tool in tools:
            if tool.metadata.name == "echo_text":
                echo_tool = tool
            elif tool.metadata.name == "show_all_devices":
                devices_tool = tool
            elif tool.metadata.name == "get_router_interfaces_config":
                interfaces_tool = tool
        
        # Test tools directly
        if echo_tool:
            print("\n1. Testing echo_text directly:")
            result = await echo_tool.acall(text="Direct tool call!")
            print(f"   Result: {result}")
        
        if devices_tool:
            print("\n2. Testing show_all_devices directly:")
            result = await devices_tool.acall()
            print(f"   Result: {result}")
        
        if interfaces_tool:
            print("\n3. Testing get_router_interfaces_config directly:")
            result = await interfaces_tool.acall(router_name="xr9kv-3")
            print(f"   Result: {result}")
        
        print("\n✅ Direct tool usage successful!")
        
        await mcp_client.close()
        
    except Exception as e:
        print(f"❌ Error in direct tool usage: {e}")


async def main():
    """Main function."""
    print("🚀 LlamaIndex MCP Client for NSO Tools")
    print("="*60)
    
    choice = input("Choose mode:\n1. Agent mode (interactive)\n2. Direct tool usage\n3. Both\nChoice (1-3): ")
    
    if choice == "1":
        await demo_llama_mcp_tools()
    elif choice == "2":
        await direct_tool_usage()
    elif choice == "3":
        await direct_tool_usage()
        print("\n" + "="*60)
        await demo_llama_mcp_tools()
    else:
        print("Invalid choice. Running direct tool usage...")
        await direct_tool_usage()


if __name__ == "__main__":
    asyncio.run(main())