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
output is the read model the planned EEIK MCP server exposes.

`eeik/catalog.py` · `eeik catalog [--tag | --query | --provides | --json]`

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
