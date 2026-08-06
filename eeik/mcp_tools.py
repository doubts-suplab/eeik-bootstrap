"""
EEIK MCP tools — the read-model logic behind the EEIK MCP server.

These are plain, synchronous, JSON-serialisable functions with no MCP dependency, so they are unit
testable on their own. ``eeik/mcp_server.py`` is a thin transport layer that registers them with the
MCP SDK. Most tools are **read-only** — catalog, manifest validation, pack resolution, drift, verify,
reference architectures — so an MCP host can *ask EEIK questions* safely.

The one write-ish tool, ``eeik_generate``, is **governed by construction** (ADR-003): generation is
SUGGEST authority, so it runs through HALO's confidence gate (``auto_enforced`` is always ``False``),
routes the draft to human review, and writes it to a *staging* area — it never returns an auto-applied
artifact and never touches live config. The MCP surface therefore exposes generation without exposing
enforcement: a host gets a *staged draft to review*, exactly like the CLI.

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


def verify() -> dict:
    """Run the conformance gate: do packs deliver what they declare; is the manifest/lock consistent."""
    return _api.verify().to_dict()


def reference_architectures() -> dict:
    """List EEIK's proven reference architectures (blueprints with a schema-valid manifest)."""
    return {"architectures": [a.to_dict() for a in _api.reference_architectures()]}


def generate(generator: str = "agent-generator", spec: str | None = None) -> dict:
    """Run one governed generation and return a STAGED, human-review draft (never auto-applied)."""
    outcome = _api.generate(generator, spec=spec)
    result = outcome.to_dict()
    # Make the governance guarantee explicit in the wire payload the host reads.
    result["autoApplied"] = False
    result["note"] = (
        "SUGGEST authority: this draft is staged for human review, not applied. "
        "Review the artifact and move it into place to adopt it."
    )
    return result


def capture_lessons(records: list[dict] | None = None) -> dict:
    """Closed-loop capture: draft STAGED lessons from HALO/APEX audit records (never auto-committed)."""
    report = _api.capture_lessons(records or [])
    result = report.to_dict()
    result["autoApplied"] = False
    result["note"] = (
        "SUGGEST authority: lessons are staged for human curation, never committed to the knowledge "
        "base. Fill Root Cause / Fix and promote them by hand."
    )
    return result


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
    {
        "name": "eeik_verify",
        "description": "Run the EEIK conformance gate: whether packs deliver the agents/standards they "
                       "declare, and whether the manifest and lockfile are consistent. Returns "
                       "{ok, counts, findings}.",
        "handler": verify,
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "eeik_reference_architectures",
        "description": "List EEIK's proven reference architectures — engine-surfaced blueprints, each with "
                       "a schema-valid manifest, stack, components, and the capability packs it activates.",
        "handler": reference_architectures,
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "eeik_generate",
        "description": "Run a GOVERNED generation and return a STAGED, human-review draft — never "
                       "auto-applied. Generation is SUGGEST authority: the draft passes HALO's confidence "
                       "gate (auto_enforced is always false), is routed to human review, and is written to "
                       "a staging area, not live config. Returns the decision, review routing, audit trail, "
                       "staged path, and the draft artifact.",
        "handler": generate,
        "inputSchema": {
            "type": "object",
            "properties": {
                "generator": {**_STR, "description": "Generator to run (e.g. 'agent-generator', "
                                                     "'repository-generator'). Default: agent-generator."},
                "spec": {**_STR, "description": "Free-text intent describing what to generate."},
            },
        },
    },
    {
        "name": "eeik_capture_lessons",
        "description": "Closed-loop knowledge capture: draft STAGED lessons from HALO/APEX audit records "
                       "(blocks, alerts, low-confidence human-review outcomes). SUGGEST authority — drafts "
                       "are staged for human curation, never committed to the knowledge base. Returns the "
                       "drafted lessons, staged paths, and the governance verdict.",
        "handler": capture_lessons,
        "inputSchema": {
            "type": "object",
            "properties": {
                "records": {
                    "type": "array",
                    "description": "Audit records (HALO/APEX). Each: action, confidence, outcome, "
                                   "rationale, agent, tenant, timestamp.",
                    "items": {"type": "object"},
                },
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
