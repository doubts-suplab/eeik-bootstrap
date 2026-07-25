# ADR-006 — EEIK exposes an MCP server (read model over the Model Context Protocol)

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — Tier 2, the "engine other tools consume" surface

---

## Context and Problem Statement

EEIK's original integration model is **static file projection**: it generates six per-tool adapter
formats (`.claude/`, `.github/`, `.kiro/`, `.cursor/`, `AGENTS.md`, `GEMINI.md`) that adopters copy.
Those projections **drift** the moment they're copied (the very problem ADR-004's lockfile addresses),
and they can only carry *static* context — a tool cannot *ask EEIK a question* ("which packs support
banking + FHIR?", "does this manifest validate?") at the point of use.

Now that the engine is an installable package (ADR-005 Stage 1) with a queryable catalog and a
structured manifest validator, EEIK can offer a **live** interface instead of only static files.

## Decision

**EEIK ships an MCP server** (`eeik mcp` / `eeik-mcp` / `python -m eeik.mcp_server`) that exposes the
engine's **read model** over the Model Context Protocol. Any MCP host (Claude Code, an APEX agent, an
IDE) connects once and calls tools live.

**v1 tools — read-only:**

| Tool | Answers |
|---|---|
| `eeik_catalog` | Which packs/agents/commands/standards exist? Filter by tag, free-text, or "who provides `<name>`?" |
| `eeik_validate_manifest` | Is this manifest valid against the canonical schema + governance rules? |
| `eeik_resolve_packs` | Which capability packs would this manifest activate? |
| `eeik_pack_drift` | Has the adopted pack set drifted from `eeik.lock`? |

**Design constraints:**
- **Read-only in v1.** Generation is deliberately *not* an MCP tool yet: it is SUGGEST authority and
  must stage drafts for human review (ADR-003). An MCP `generate` tool would have to return a governed,
  staged result — a later increment, once the human-review handoff over MCP is designed.
- **Testable core, thin transport.** Tool logic lives in `eeik/mcp_tools.py` (dependency-free, unit
  tested + exercised via a real in-memory client↔server round-trip); `eeik/mcp_server.py` is only the
  MCP SDK wiring.
- **Optional dependency.** The MCP SDK is the `[mcp]` extra; without it the module still imports and the
  CLI prints an install hint (fail-safe, consistent with the HALO integration).

Register with a host, e.g. Claude Code `.mcp.json`:
```json
{ "mcpServers": { "eeik": { "command": "eeik", "args": ["mcp"] } } }
```

## Considered Options

1. **MCP server exposing the read model (chosen)** — one live, conformant surface; replaces drift-prone
   static projections for *queryable* context; standard protocol, many hosts.
2. **A bespoke REST API** — rejected for the "ask EEIK live from an agent" use case: no standard client,
   every host needs custom glue. (A thin REST facade may still come later for non-MCP consumers.)
3. **Keep only static adapter files** — rejected: cannot answer questions at point of use, and drifts.

## Consequences

**Positive**
- Hosts get live, conformant access to EEIK's catalog, validation, and resolution — no copied files.
- The `--json` catalog read model (Tier 2) becomes callable over a standard protocol.
- Clean separation (`mcp_tools` vs `mcp_server`) keeps the logic testable and the SDK optional.

**Negative / trade-offs**
- A new optional dependency (`mcp`) and a long-running process to operate.
- Read-only for now — generation over MCP is deferred until the governed handoff is designed.

## Related

- ADR-003 (governed generation), ADR-004 (versioning/lockfile), ADR-005 (taxonomy).
- `eeik/mcp_tools.py`, `eeik/mcp_server.py`, `tests/test_mcp.py`.
