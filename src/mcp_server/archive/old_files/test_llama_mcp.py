#!/usr/bin/env python3
"""
Simple LlamaIndex MCP Test
Tests the MCP integration without user input
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


async def test_direct_mcp():
    """Test direct MCP tool usage."""
    
    print("🔧 Testing Direct MCP Tool Usage")
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
                return True
                
    except Exception as e:
        print(f"❌ Error in direct MCP test: {e}")
        return False


async def test_llama_agent():
    """Test LlamaIndex agent with MCP tools."""
    
    print("\n🤖 Testing LlamaIndex Agent with MCP Tools")
    print("="*60)
    
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
                
                # Create LlamaIndex agent with Azure OpenAI
                print("\n🔧 Initializing Azure OpenAI LLM...")
                llm = initialize_azure_llm()
                agent = ReActAgent.from_tools(wrapped_tools, llm=llm, verbose=True)
                
                print("\n🤖 Testing agent with echo_text:")
                response1 = await agent.achat("Use echo_text to say 'Hello from LlamaIndex + MCP!'")
                print(f"Agent Response: {response1}")
                
                print("\n🤖 Testing agent with show_all_devices:")
                response2 = await agent.achat("Use show_all_devices to get all router names")
                print(f"Agent Response: {response2}")
                
                print("\n✅ LlamaIndex Agent test successful!")
                return True
                
    except Exception as e:
        print(f"❌ Error in LlamaIndex agent test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🚀 LlamaIndex MCP Integration Test")
    print("="*60)
    
    # Test 1: Direct MCP
    direct_success = await test_direct_mcp()
    
    # Test 2: LlamaIndex Agent
    agent_success = await test_llama_agent()
    
    print("\n" + "="*60)
    print("📊 Test Results:")
    print(f"   Direct MCP: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"   LlamaIndex Agent: {'✅ PASS' if agent_success else '❌ FAIL'}")
    
    if direct_success and agent_success:
        print("\n🎉 All tests passed! LlamaIndex MCP integration is working!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())