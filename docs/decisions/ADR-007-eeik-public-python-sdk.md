# ADR-007 — EEIK ships a stable public Python API (SDK)

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — Tier 2, the in-process consumption surface

---

## Context and Problem Statement

The engine is now an installable package (ADR-005) with a catalog, a manifest validator, pack
resolution, and drift detection. Two consumption surfaces already exist: the **CLI** (humans, CI) and
the **MCP server** (agents/hosts, over a protocol, ADR-006). What is missing is the **in-process**
surface: a consumer such as `apex-sdlc` should be able to `import eeik` and call the engine as a
library — for onboarding, validation, and pack resolution — instead of shelling out to the CLI and
parsing text, or standing up an MCP client for a same-process call.

Without a *declared* public API, consumers would reach into internal modules (`eeik.manifest`,
`eeik.lock`, …) whose shapes are free to change, coupling them to internals.

## Decision

**EEIK exposes a curated, typed public API in `eeik/api.py`, re-exported from `eeik`.**

```python
import eeik

eeik.validate_manifest(path="project-manifest.yaml")   # -> ValidationResult(valid, errors, warnings)
eeik.resolve_packs(manifest=doc)                        # -> ["core", "architecture", "java", ...]
eeik.find_packs(tag="regulated")                        # -> [Pack(...), ...]
eeik.providers_of("java-architect")                     # -> [Provider(pack="java", kind="agent")]
eeik.pack_drift()                                       # -> DriftReport(lock_present, entries)
```

- **Typed results.** Frozen dataclasses (`Pack`, `Provider`, `ValidationResult`, `DriftEntry`,
  `DriftReport`) with a `.to_dict()` for JSON. Consumers get autocomplete and a stable shape.
- **One source of truth.** The SDK is the base; the **CLI** and the **MCP tools** are thin adapters over
  it (the MCP `eeik/mcp_tools.py` now delegates to `eeik/api.py` and calls `.to_dict()`). Behaviour can't
  diverge between surfaces.
- **Stability contract.** The names and return shapes in `eeik.__all__` / `eeik.api.__all__` are the
  supported API. Everything else in the package is internal and may change without notice.
- **Read-first.** The API mirrors the read-only MCP tool set plus `write_lock()`; generation stays
  behind the governed CLI/harness (ADR-003), not the plain SDK.

### One naming note

The catalog accessor is `eeik.find_packs()`, not `eeik.catalog()`, to avoid shadowing the internal
`eeik.catalog` submodule. A top-level function sharing a submodule's name would make
`from eeik import catalog` ambiguous; `find_packs` keeps both reachable.

## Considered Options

1. **Curated typed API re-exported from `eeik` (chosen)** — one stable surface, typed, with the CLI/MCP
   as adapters over it. Consumers import the package, not internals.
2. **Let consumers import internal modules directly** — rejected: couples consumers to shapes that are
   meant to change; no stability contract.
3. **Only offer the MCP server / CLI** — rejected: forces a subprocess or a protocol client for what is
   a same-process function call in APEX.

## Consequences

**Positive**
- `apex-sdlc` (and others) can `import eeik` and consume onboarding/validation/resolution as a library —
  the in-process complement to the MCP server.
- CLI, MCP, and SDK cannot drift: they share one implementation.
- Internals stay free to evolve behind the declared surface.

**Negative / trade-offs**
- A public API is now a maintenance commitment; changing `__all__` shapes is a breaking change.
- `find_packs` naming (vs `catalog`) is a small readability compromise to avoid the submodule clash.

## Related

- ADR-005 (package), ADR-006 (MCP server). `eeik/api.py`, `eeik/__init__.py`, `tests/test_sdk.py`.
- Next cross-repo step: `apex-sdlc` onboarding imports the SDK instead of shelling out.
