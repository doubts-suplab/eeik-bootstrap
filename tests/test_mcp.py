"""Tests for the EEIK MCP server: the pure tool layer, plus a real client↔server round-trip.

Run:  python3 -m pytest tests/test_mcp.py -q   (needs the [mcp] + [test] extras for the round-trip)
"""

from __future__ import annotations

import json

import pytest

from eeik import mcp_tools as t


# ── pure tool layer (no MCP SDK needed) ───────────────────────────────────────────

def test_tool_catalog_tag_and_provides():
    regulated = {p["pack"] for p in t.catalog(tag="regulated")["packs"]}
    assert {"banking", "healthcare", "insurance"} <= regulated
    assert t.catalog(provides="java-architect")["providers"] == [{"pack": "java", "kind": "agent"}]


def test_tool_validate_manifest():
    ok = t.validate_manifest(path="bootstrap/examples/greenfield-java-aws.yaml")
    assert ok["valid"] and ok["errors"] == []
    bad = t.validate_manifest(content="project: {name: x}")
    assert bad["valid"] is False and bad["errors"]


def test_tool_resolve_packs_and_drift():
    resolved = t.resolve_packs(path="bootstrap/examples/greenfield-java-aws.yaml")["resolved"]
    assert "core" in resolved and "java" in resolved
    assert "driftCount" in t.pack_drift()


def test_dispatch_unknown_tool_raises():
    with pytest.raises(KeyError):
        t.dispatch("nope", {})


# ── real MCP round-trip (client ↔ server over in-memory streams) ───────────────────

def test_mcp_roundtrip():
    pytest.importorskip("mcp")
    import anyio
    from mcp.shared.memory import create_connected_server_and_client_session as connect

    from eeik.mcp_server import _make_server

    async def _run():
        server = _make_server()
        async with connect(server) as client:
            await client.initialize()

            listed = await client.list_tools()
            names = {tool.name for tool in listed.tools}
            assert {
                "eeik_catalog",
                "eeik_validate_manifest",
                "eeik_resolve_packs",
                "eeik_pack_drift",
            } <= names

            result = await client.call_tool("eeik_catalog", {"tag": "regulated"})
            payload = json.loads(result.content[0].text)
            packs = {p["pack"] for p in payload["packs"]}
            assert {"banking", "healthcare", "insurance"} <= packs

    anyio.run(_run)
