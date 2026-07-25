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

from pathlib import Path
from typing import Any

import yaml

from eeik import catalog as _catalog
from eeik import lock as _lock
from eeik import manifest as _manifest
from eeik import packs as _packs


def _load_manifest(content: str | None, path: str | None) -> dict:
    """Parse a manifest from inline YAML ``content`` or a file ``path`` (content wins)."""
    if content:
        doc = yaml.safe_load(content)
    elif path:
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    else:
        raise ValueError("provide either 'content' (inline YAML) or 'path'")
    if not isinstance(doc, dict):
        raise ValueError("manifest is not a YAML mapping")
    return doc


# ── tools ───────────────────────────────────────────────────────────────────────

def catalog(tag: str | None = None, query: str | None = None, provides: str | None = None) -> dict:
    """Query the capability catalog (packs, agents, commands, standards)."""
    doc = _catalog.build_catalog()
    entries = doc["packs"]
    if provides:
        hits = _catalog.find_providers(entries, provides)
        return {"name": provides, "providers": [{"pack": p, "kind": k} for p, k in hits]}
    if tag:
        entries = _catalog.filter_by_tag(entries, tag)
    if query:
        entries = _catalog.filter_by_query(entries, query)
    return {"packCount": len(entries), "packs": entries}


def validate_manifest(content: str | None = None, path: str | None = None) -> dict:
    """Validate a project manifest against the canonical schema + governance rules."""
    manifest = _load_manifest(content, path)
    errors, warnings = _manifest.validate_document(manifest)
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def resolve_packs(content: str | None = None, path: str | None = None) -> dict:
    """Resolve which capability packs a manifest activates (same logic as `eeik activate`)."""
    manifest = _load_manifest(content, path)
    resolved = _packs.resolve_packs(manifest, _packs.load_matrix())
    return {"resolved": resolved, "count": len(resolved)}


def pack_drift(lockfile: str | None = None) -> dict:
    """Report capability-pack drift between eeik.lock and the packs on disk."""
    path = _lock.lock_path(lockfile)
    locked = _lock.read_lock(path)
    if locked is None:
        return {"lockPresent": False, "drift": [], "message": "no eeik.lock — run `eeik lock`"}
    from eeik.versions import all_pack_fingerprints

    current = all_pack_fingerprints(_lock.resolve_current_packs())
    drift = _lock.compute_drift(locked, current)
    return {"lockPresent": True, "driftCount": len(drift), "drift": drift}


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
