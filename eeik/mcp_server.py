#!/usr/bin/env python3
"""
EEIK MCP server — expose the EEIK engine's read model over the Model Context Protocol.

This is the clearest expression of the "engine other tools consume" posture (ROADMAP Tier 2): one live
server that any MCP host (Claude Code, an APEX agent, an IDE) can call to *ask EEIK questions* —
instead of copying six static tool-adapter formats that drift. See ADR-006.

Tools (all read-only in v1): ``eeik_catalog``, ``eeik_validate_manifest``, ``eeik_resolve_packs``,
``eeik_pack_drift``. The tool logic lives in ``eeik/mcp_tools.py`` (dependency-free, unit tested); this
module is the thin transport layer over the MCP SDK.

Run it:
    eeik mcp                 # (or: python -m eeik.mcp_server / eeik-mcp)

Register it with an MCP host, e.g. Claude Code (.mcp.json):
    { "mcpServers": { "eeik": { "command": "eeik", "args": ["mcp"] } } }

The MCP SDK is an optional dependency — install with ``pip install -e ".[mcp]"``. Without it, this
module still imports (so the CLI can print a helpful message) but the server cannot start.
"""

from __future__ import annotations

import json
import sys

from eeik.mcp_tools import TOOLS, dispatch

try:
    import anyio
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool

    MCP_AVAILABLE = True
except ImportError:  # SDK not installed — fail gracefully, don't crash the CLI.
    MCP_AVAILABLE = False


def build_tools() -> list:
    """Build the MCP ``Tool`` list from the tool declarations. Requires the MCP SDK."""
    return [
        Tool(name=t["name"], description=t["description"], inputSchema=t["inputSchema"])
        for t in TOOLS
    ]


def _make_server():
    """Wire the tool declarations into an MCP ``Server``."""
    server = Server("eeik")

    @server.list_tools()
    async def _list_tools() -> list:
        return build_tools()

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict | None) -> list:
        try:
            result = dispatch(name, arguments or {})
        except Exception as exc:  # surface errors as tool content, never crash the server
            result = {"error": f"{type(exc).__name__}: {exc}"}
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    return server


async def _serve() -> None:
    server = _make_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> int:
    if not MCP_AVAILABLE:
        print(
            "The MCP SDK is not installed. Install it with:\n"
            "    pip install -e \".[mcp]\"\n"
            "then run `eeik mcp` again.",
            file=sys.stderr,
        )
        return 1
    anyio.run(_serve)
    return 0


if __name__ == "__main__":
    sys.exit(main())
