#!/usr/bin/env python3
"""
Simple MCP Server Test
Tests basic MCP functionality without LlamaIndex
"""

import asyncio
import logging
from typing import Any, Dict

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("simple-test-mcp")

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    logger.debug("📋 list_tools invoked")
    
    tools = [
        Tool(
            name="echo",
            description="Echo back the provided text",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo back"
                    }
                },
                "required": ["text"]
            }
        )
    ]
    
    logger.debug(f"📋 Returning {len(tools)} tools")
    return ListToolsResult(tools=tools)

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    logger.debug(f"🔧 call_tool name={name} args={arguments}")
    
    if name == "echo":
        text = arguments.get("text", "")
        result = f"Echo: {text}"
        logger.debug(f"🔧 Echo result: {result}")
        return CallToolResult(content=[TextContent(type="text", text=result)])
    else:
        return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])

async def main():
    """Main entry point."""
    logger.info("🚀 Starting Simple MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-test-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
