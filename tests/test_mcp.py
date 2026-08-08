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


def test_tool_generate_is_governed_and_staged_never_applied():
    """The one write-ish MCP tool must never auto-apply: SUGGEST authority, staged for review."""
    res = t.dispatch("eeik_generate", {"generator": "agent-generator", "spec": "a refund agent"})
    assert res["autoApplied"] is False          # explicit wire guarantee
    assert res["auto_enforced"] is False         # gate rule G-5: SUGGEST never auto-enforces
    assert res["staged"] is True                 # written to staging, not live config
    assert res["bypass_total"] == 0              # confidence_gate_bypass_total must be 0
    assert ".eeik-staging/" in res["staged_path"]
    assert "a refund agent" in res["artifact"]   # the spec reached the producer
    # advertised in the tool list
    assert "eeik_generate" in {tool["name"] for tool in t.TOOLS}


def test_tool_generate_preview_is_governed_but_not_persisted():
    res = t.dispatch("eeik_generate", {"generator": "agent-generator", "spec": "x", "preview": True})
    assert res["staged"] is False and res["staged_path"] == ""   # preview: not persisted
    assert res["autoApplied"] is False and res["auto_enforced"] is False  # still governed
    assert "preview" in res["note"].lower()


# ── real MCP round-trip (client ↔ server over in-memory streams) ───────────────────

def test_mcp_roundtrip():
    pytest.importorskip("mcp")
    import anyio

    # The in-memory client↔server helper's import path varies across mcp SDK versions; skip the
    # round-trip cleanly if this SDK doesn't expose it (the pure tool layer above still covers logic).
    try:
        from mcp.shared.memory import create_connected_server_and_client_session as connect
    except ImportError:
        pytest.skip("installed mcp SDK lacks create_connected_server_and_client_session")

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
