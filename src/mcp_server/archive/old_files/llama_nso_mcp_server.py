#!/usr/bin/env python3
"""
LlamaIndex-style NSO MCP Server (compat layer)
Exposes minimal tools with robust per-call NSO sessions.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ListToolsResult, Tool, CallToolResult, TextContent

# NSO env
NSO_DIR = "/Users/gudeng/NCS-614"
NSO_USERNAME = "admin"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def setup_env() -> None:
    os.environ["NCS_DIR"] = NSO_DIR
    os.environ["DYLD_LIBRARY_PATH"] = f"{NSO_DIR}/lib"
    os.environ["PYTHONPATH"] = f"{NSO_DIR}/src/ncs/pyapi"
    pyapi = f"{NSO_DIR}/src/ncs/pyapi"
    if pyapi not in sys.path:
        sys.path.insert(0, pyapi)


def get_devices_text() -> str:
    try:
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        with maapi.single_read_trans(NSO_USERNAME, "python", groups=["ncsadmin"]) as t:
            root = maagic.get_root(t)
            names = [d.name for d in root.devices.device]
        return ", ".join(names) if names else ""
    except Exception as e:
        return f"❌ Failed to get devices: {e}"


def get_interfaces_text(router_name: str) -> str:
    try:
        import ncs.maapi as maapi
        import ncs.maagic as maagic
        with maapi.single_read_trans(NSO_USERNAME, "python", groups=["ncsadmin"]) as t:
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


server = Server("nso-mcp-server-llama")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    logger.debug("📋 list_tools (llama) invoked")
    tools = [
        Tool(
            name="show_all_devices",
            description="Find out all available routers in the lab, return their names.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_router_interfaces_config",
            description="Return configured interfaces (Loopback/GigabitEthernet/Ethernet) with IPv4 for a router.",
            inputSchema={
                "type": "object",
                "properties": {"router_name": {"type": "string"}},
                "required": ["router_name"],
            },
        ),
        Tool(
            name="echo_text",
            description="Echo back the provided text (debug/health).",
            inputSchema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        ),
    ]
    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    logger.debug(f"🔧 llama call_tool name={name} args={arguments}")
    try:
        setup_env()
        if name == "show_all_devices":
            text = get_devices_text()
        elif name == "get_router_interfaces_config":
            text = get_interfaces_text(arguments["router_name"])
        elif name == "echo_text":
            text = str(arguments.get("text", ""))
        else:
            text = f"❌ Unknown tool: {name}"
        return CallToolResult(content=[TextContent(type="text", text=text)])
    except Exception as e:
        logger.exception("call_tool error")
        return CallToolResult(content=[TextContent(type="text", text=f"❌ Error: {e}")])


async def main():
    logger.info("🚀 Starting NSO MCP Server (LlamaIndex compat)…")
    setup_env()
    async with stdio_server() as (r, w):
        await server.run(
            r,
            w,
            InitializationOptions(
                server_name="nso-mcp-server-llama",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())


