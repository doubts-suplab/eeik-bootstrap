# Platform Capabilities

> **Posture (v1.4):** EEIK is a governed generation *engine*, not a product platform. It generates and
> governs *generation*; HALO governs *execution*; APEX is the SDLC product that consumes both. See
> [ADR-003](../decisions/ADR-003-eeik-generators-run-on-halo.md) and
> [ADR-004](../decisions/ADR-004-capability-pack-versioning-and-lockfile.md).

## Generation Engine (v1.4)

### Governed Generation (HALO)

EEIK's generators run on the `agent-harness` runtime. Every generation passes the confidence gate, is
audited, and — as SUGGEST authority — routes drafts to human review (never auto-applied). Fails safe
without HALO.

`eeik/generation.py` · `eeik run <gen> --governed` · `eeik demo`

---

### Pack Versioning & Drift Detection

Capability packs are versioned dependencies. `eeik.lock` records adopted versions + content digests;
drift (added/removed/version-changed/content-changed) is reported and CI-gateable.

`eeik/versions.py` · `eeik/lock.py` · `eeik lock | diff | upgrade`

---

### Capability Catalog (registry)

A queryable, machine-readable index of every pack, agent, command, and standard, with version +
content-digest provenance. Query by tag, free-text, or "which pack provides `<name>`?". The `--json`
output is the read model the EEIK MCP server exposes.

`eeik/catalog.py` · `eeik catalog [--tag | --query | --provides | --json]`

---

### MCP Server (live read model)

Exposes the engine's read model over the Model Context Protocol so any MCP host can query EEIK live —
replacing drift-prone static adapter files for *queryable* context. Read-only in v1; generation stays
governed/staged (ADR-003).

`eeik/mcp_server.py` · `eeik mcp` · tools: `eeik_catalog`, `eeik_validate_manifest`,
`eeik_resolve_packs`, `eeik_pack_drift`

---

### Python SDK (in-process)

The typed, stable `import eeik` surface — the in-process counterpart to the MCP server. Consumers
(e.g. apex-sdlc) call the engine as a library instead of shelling out. The CLI and MCP are adapters
over this one implementation.

`eeik/api.py` · `import eeik` → `find_packs` · `providers_of` · `validate_manifest` · `resolve_packs`
· `pack_drift` · `write_lock`

---

## Core Platform

### Bootstrap Engine

Discovers project requirements.

Outputs:

```text
Manifest
```

---

### Capability Resolver

Maps requirements to capability packs.

---

### Repository Generator

Generates project structures.

---

### Agent Factory

Generates project-specific agents.

---

### Governance Engine

Applies enterprise controls.

---

### Knowledge Platform

Captures organizational intelligence.

---

# Architecture Intelligence

Capabilities:

- Solution Design
- Architecture Reviews
- ADR Generation
- RFC Generation

---

# Delivery Intelligence

Capabilities:

- Estimation
- Planning
- Roadmaps
- Release Planning

---

# Modernization Intelligence

Capabilities:

- IBM i Analysis
- RPG Analysis
- COBOL Analysis
- Migration Planning

---

# AI Engineering Intelligence

Capabilities:

- Agent Design
- Agent Evaluation
- Prompt Design
- Memory Design

---

# Governance Intelligence

Capabilities:

- Architecture Reviews
- Security Reviews
- AI Reviews
- Production Readiness

---

# Knowledge Intelligence

Capabilities:

- Pattern Discovery
- Incident Analysis
- Lessons Learned
- Reference Architectures
