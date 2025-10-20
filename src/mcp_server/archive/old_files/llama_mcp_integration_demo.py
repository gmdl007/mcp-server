#!/usr/bin/env python3
"""
LlamaIndex + MCP Integration Demo
Shows how to use MCP tools with LlamaIndex agents
"""

import asyncio
import logging
import os
import base64
import requests
from typing import Any, Dict, List

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

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


class MCPToolWrapper:
    """Wrapper to make MCP tools compatible with LlamaIndex."""
    
    def __init__(self, name: str, description: str, mcp_session: ClientSession):
        self.name = name
        self.description = description
        self.mcp_session = mcp_session
    
    async def acall(self, **kwargs) -> str:
        """Call the MCP tool."""
        try:
            result = await self.mcp_session.call_tool(self.name, kwargs)
            return result.content[0].text
        except Exception as e:
            return f"Error: {e}"
    
    def call(self, **kwargs) -> str:
        """Synchronous call (for compatibility)."""
        return asyncio.run(self.acall(**kwargs))


async def create_mcp_tools():
    """Create MCP tools wrapped for LlamaIndex."""
    
    server_params = StdioServerParameters(
        command="/Users/gudeng/MCP_Server/src/mcp_server/start_llama_index_nso_mcp.sh",
        args=[],
        env={
            "NCS_DIR": "/Users/gudeng/NCS-614",
            "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
        }
    )
    
    print("🔧 Creating MCP tools for LlamaIndex...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get available tools
                tools_result = await session.list_tools()
                
                print(f"✅ Found {len(tools_result.tools)} MCP tools:")
                
                # Create wrapped tools
                wrapped_tools = []
                for tool in tools_result.tools:
                    print(f"   • {tool.name}: {tool.description}")
                    
                    # Create FunctionTool wrapper
                    wrapper = MCPToolWrapper(tool.name, tool.description, session)
                    
                    # Create LlamaIndex FunctionTool
                    llama_tool = FunctionTool.from_defaults(
                        fn=wrapper.call,
                        name=tool.name,
                        description=tool.description,
                        fn_schema=tool.inputSchema
                    )
                    
                    wrapped_tools.append(llama_tool)
                
                return wrapped_tools, session
                
    except Exception as e:
        print(f"❌ Error creating MCP tools: {e}")
        return [], None


async def demo_llama_mcp_integration():
    """Demonstrate LlamaIndex + MCP integration."""
    
    print("🚀 LlamaIndex + MCP Integration Demo")
    print("="*60)
    
    # Create MCP tools
    tools, session = await create_mcp_tools()
    
    if not tools:
        print("❌ No MCP tools available")
        return
    
    try:
        # Create LlamaIndex agent with Azure OpenAI
        llm = initialize_azure_llm()
        agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)
        
        print("\n🤖 LlamaIndex Agent with MCP Tools Ready!")
        print("="*60)
        
        # Test the integration
        print("\n1. Testing echo_text:")
        response1 = await agent.achat("Use echo_text to say 'Hello from LlamaIndex + MCP!'")
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
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")


async def direct_mcp_demo():
    """Direct MCP tool usage demo."""
    
    print("🔧 Direct MCP Tool Usage Demo")
    print("="*50)
    
    server_params = StdioServerParameters(
        command="/Users/gudeng/MCP_Server/src/mcp_server/start_llama_index_nso_mcp.sh",
        args=[],
        env={
            "NCS_DIR": "/Users/gudeng/NCS-614",
            "PYTHONPATH": "/Users/gudeng/NCS-614/src/ncs/pyapi"
        }
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("✅ Connected to LlamaIndex NSO MCP Server!")
                
                # Test tools directly
                print("\n1. Testing echo_text:")
                result = await session.call_tool("echo_text", {"text": "Direct MCP call!"})
                print(f"   Result: {result.content[0].text}")
                
                print("\n2. Testing show_all_devices:")
                result = await session.call_tool("show_all_devices", {})
                print(f"   Result: {result.content[0].text}")
                
                print("\n3. Testing get_router_interfaces_config:")
                result = await session.call_tool("get_router_interfaces_config", {"router_name": "xr9kv-3"})
                print(f"   Result: {result.content[0].text}")
                
                print("\n✅ Direct MCP usage successful!")
                
    except Exception as e:
        print(f"❌ Error in direct demo: {e}")


async def main():
    """Main function."""
    print("🚀 LlamaIndex + MCP Integration for NSO Tools")
    print("="*60)
    
    choice = input("Choose demo:\n1. LlamaIndex Agent + MCP\n2. Direct MCP usage\n3. Both\nChoice (1-3): ")
    
    if choice == "1":
        await demo_llama_mcp_integration()
    elif choice == "2":
        await direct_mcp_demo()
    elif choice == "3":
        await direct_mcp_demo()
        print("\n" + "="*60)
        await demo_llama_mcp_integration()
    else:
        print("Invalid choice. Running direct MCP demo...")
        await direct_mcp_demo()


if __name__ == "__main__":
    asyncio.run(main())
