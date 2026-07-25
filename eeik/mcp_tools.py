"""
EEIK MCP tools — the read-model logic behind the EEIK MCP server.

These are plain, synchronous, JSON-serialisable functions with no MCP dependency, so they are unit
testable on their own. ``eeik/mcp_server.py`` is a thin transport layer that registers them with the
MCP SDK. The v1 tool set is **read-only** — catalog, manifest validation, pack resolution, and drift —
so an MCP host can *ask EEIK questions* safely. Generation stays behind the governed CLI (ADR-003):
it is SUGGEST authority and must stage drafts for human review, never return auto-applied artifacts.

Each tool returns a dict. The ``TOOLS`` list declares name + description + JSON input schema for
MCP ``list_tools``.
"""

from __future__ import annotations

from typing import Any

from eeik import api as _api


# ── tools (thin JSON adapters over the eeik SDK — one source of truth) ────────────

def catalog(tag: str | None = None, query: str | None = None, provides: str | None = None) -> dict:
    """Query the capability catalog (packs, agents, commands, standards)."""
    if provides:
        return {"name": provides, "providers": [p.to_dict() for p in _api.providers_of(provides)]}
    packs = _api.find_packs(tag=tag, query=query)
    return {"packCount": len(packs), "packs": [p.to_dict() for p in packs]}


def validate_manifest(content: str | None = None, path: str | None = None) -> dict:
    """Validate a project manifest against the canonical schema + governance rules."""
    return _api.validate_manifest(content=content, path=path).to_dict()


def resolve_packs(content: str | None = None, path: str | None = None) -> dict:
    """Resolve which capability packs a manifest activates (same logic as `eeik activate`)."""
    resolved = _api.resolve_packs(content=content, path=path)
    return {"resolved": resolved, "count": len(resolved)}


def pack_drift(lockfile: str | None = None) -> dict:
    """Report capability-pack drift between eeik.lock and the packs on disk."""
    return _api.pack_drift(lockfile=lockfile).to_dict()


# ── MCP tool declarations ─────────────────────────────────────────────────────

_STR = {"type": "string"}

TOOLS: list[dict[str, Any]] = [
    {
        "name": "eeik_catalog",
        "description": "Query EEIK's capability catalog: packs, and the agents/commands/standards they "
                       "provide. Filter by tag or free-text, or ask which pack provides a named item.",
        "handler": catalog,
        "inputSchema": {
            "type": "object",
            "properties": {
                "tag": {**_STR, "description": "Only packs carrying this tag (e.g. 'regulated')."},
                "query": {**_STR, "description": "Free-text match over name/description/tags."},
                "provides": {**_STR, "description": "Name of an agent/command/standard to locate."},
            },
        },
    },
    {
        "name": "eeik_validate_manifest",
        "description": "Validate a project-manifest against the canonical schema + governance rules. "
                       "Returns {valid, errors, warnings}.",
        "handler": validate_manifest,
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {**_STR, "description": "Inline manifest YAML."},
                "path": {**_STR, "description": "Path to a manifest file (used if content is absent)."},
            },
        },
    },
    {
        "name": "eeik_resolve_packs",
        "description": "Resolve which capability packs a manifest activates (agents/standards it would "
                       "materialise). Returns the ordered pack list.",
        "handler": resolve_packs,
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {**_STR, "description": "Inline manifest YAML."},
                "path": {**_STR, "description": "Path to a manifest file."},
            },
        },
    },
    {
        "name": "eeik_pack_drift",
        "description": "Report capability-pack drift between eeik.lock and the packs on disk "
                       "(added/removed/version-changed/content-changed).",
        "handler": pack_drift,
        "inputSchema": {
            "type": "object",
            "properties": {
                "lockfile": {**_STR, "description": "Path to a lockfile (default: eeik.lock)."},
            },
        },
    },
]


def tool_by_name(name: str) -> dict:
    for t in TOOLS:
        if t["name"] == name:
            return t
    raise KeyError(name)


def dispatch(name: str, arguments: dict | None = None) -> dict:
    """Invoke a tool by name with keyword arguments. Used by the MCP server's call_tool handler."""
    handler = tool_by_name(name)["handler"]
    return handler(**(arguments or {}))
