# ADR-010 — Reference architectures are first-class, engine-surfaced blueprints

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — content depth (ROADMAP v1.3)

---

## Context and Problem Statement

EEIK's `knowledge/reference-architectures/` held prose only — an architecture a human reads, with no
machine-readable link to the engine. A reference architecture that isn't *checkable* rots: its stack
drifts from what the packs actually provide, its "manifest match" snippet stops validating, and nobody
notices. Meanwhile the engine (catalog, SDK, `resolve-packs`, `verify`) had no notion of them, so a
proven blueprint couldn't be listed, resolved, or conformance-checked.

## Decision

**Each reference architecture is a first-class, machine-readable directory the engine surfaces and
checks.** Under `knowledge/reference-architectures/<name>/`:

- `reference.yaml` — descriptor (title, maturity, stack, tags, components, `expected_packs`).
- `project-manifest.yaml` — a **schema-valid eeik manifest** — the same artifact `eeik resolve-packs`
  and the repository-generator consume. The blueprint *is* runnable input, not just a diagram.
- `architecture.md` + `runbook.md` — design and operations.

Surfaced on every read surface — `eeik/architectures.py` → `eeik architectures` (CLI),
`eeik.reference_architectures()` (SDK), `eeik_reference_architectures` (MCP) — and **checked by
`eeik verify`**: each architecture's manifest must validate and must resolve to exactly the packs its
descriptor claims (`expected_packs`). A drifted blueprint fails conformance like anything else.

Two reference architectures ship as the initial set:
- **order-management** — event-driven Spring Boot / Java 21 / Aurora / Kafka on AWS (DDD, outbox, saga, CQRS).
- **ai-augmented-service** — RAG on FastAPI / Bedrock / pgvector, every model call governed by HALO.

### Two correctness fixes this surfaced

Making the manifests resolve credibly exposed real engine bugs, fixed here:
1. **Resolver read the wrong path.** `resolve_packs` read `technology.cloud` / a non-existent
   `cloud.services`, but the canonical schema puts `cloud` and `ai` at the **top level** — so the `aws`
   and `ai-engineering`/`agent-harness` packs were *never* resolved for any schema-valid manifest. Now
   it reads the top level; AWS/AI manifests resolve correctly.
2. **Schema ↔ rules/stack gaps.** The `migration_tool` enum lacked `alembic` (EEIK's own Python stack),
   and the governance object rejected `adr_required` / `coverage_threshold` — fields EEIK's *own
   governance rules* recommend. All three added (backward-compatible).

Separately, the CLI now dispatches subcommands **in-process** rather than spawning `python -m eeik.<cmd>`,
removing a benign but ubiquitous re-execution `RuntimeWarning`.

## Considered Options

1. **Machine-readable, engine-surfaced, verify-checked (chosen)** — blueprints stay honest; the manifest
   is real, runnable input; drift is caught by CI.
2. **Keep them as prose** — rejected: unverifiable, drifts, invisible to the engine.
3. **Model each as a capability pack** — rejected: a reference architecture is a *manifest preset + design
   + ops*, not a provider of agents/standards; conflating the two muddies the catalog.

## Consequences

**Positive**
- Reference architectures are listable, resolvable, and conformance-checked; `eeik verify` guards them.
- The preset manifest feeds `resolve-packs` / the repository-generator directly — content is *runnable*.
- Fixing the resolver makes AWS/AI pack resolution correct for **all** manifests, not just these.

**Negative / trade-offs**
- Each new reference architecture must keep `expected_packs` in sync with resolution (verify enforces it).
- The schema grew three enum/property values (small, backward-compatible; apex's vendored copy should re-sync).

## Related

- ADR-004/005 (schema), ADR-008 (verify). `eeik/architectures.py`, `eeik/packs.py`, `tests/test_architectures.py`.
