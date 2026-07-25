# ADR-005 — Layered directory taxonomy (engine / content / adapters)

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — Tier 4 (directory structure), the "document before moving" step

---

## Context and Problem Statement

As EEIK matured from a config seed into a governed generation *engine* (ADR-003, ADR-004), its top
level grew a mix of things with very different lifecycles — executable code, authoring content, tool
adapters, and docs — with no stated rule for which is which. New contributions landed wherever felt
convenient (three divergent schemas, a `generators/capability-selector` that overlaps
`bootstrap/resolvers`, engine scripts mixed with content). Without an explicit taxonomy, that drift
continues.

The Stage 1–2 restructure (installable `eeik/` package + one canonical schema) already moved the
engine into its own layer. This ADR **names the taxonomy** so future additions land correctly, and
records the moves we deliberately deferred — the principle is **document the model before relocating
content**, because the content paths are referenced widely and underpin the `cp -r` adoption ergonomics.

---

## Decision

EEIK's top level is organised into **four layers**, documented in [`ARCHITECTURE.md`](../../ARCHITECTURE.md):

| Layer | Directories | Nature |
|---|---|---|
| **Engine** | `eeik/`, `scripts/` (shims), `tests/`, `pyproject.toml` | Executable Python. Installable package; the only layer that runs. |
| **Content** | `capability-packs/`, `knowledge/`, `templates/`, `generators/`, `bootstrap/` | Data the engine reads. Markdown/YAML; no code. |
| **Adapters** | `.claude/`, `.github/`, `.kiro/`, `.cursor/`, `AGENTS.md`, `GEMINI.md`, `.vscode/`, `intellij/` | Per-tool config — both EEIK's own dogfood config *and* the seed adopters copy. |
| **Docs & meta** | `docs/`, `README.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` | Human-facing documentation and repository metadata. |

**Placement rule:** code goes in `eeik/`; a thing the engine *reads* goes in a Content directory;
a per-tool projection goes in an Adapter directory; prose goes in `docs/`. The canonical schema lives
with the engine (`eeik/schemas/`) because the engine enforces it.

### Deferred (document now, move later)

- **Dual-purpose adapters.** The root adapters serve two masters (EEIK's own config vs. the copy seed);
  a future change makes the copy-target explicit without breaking `cp -r`. Tracked in ROADMAP Tier 4.
- **Resolver overlap.** `generators/capability-selector` and `bootstrap/resolvers` cover overlapping
  ground; unify once this taxonomy is in place.

No content directories are moved in this ADR.

---

## Considered Options

1. **Name the taxonomy, defer content moves (chosen)** — locks the mental model with near-zero risk;
   content relocations happen later, deliberately, against a documented model.
2. **Big-bang reorg now** — rejected: high blast radius (instruction globs, CI, README, cross-repo
   references, `cp -r` ergonomics) for low marginal benefit over naming the model first.
3. **Leave it undocumented** — rejected: drift continues; new contributors have no placement rule.

---

## Consequences

**Positive**
- A single, referable answer to "where does a new X go?" (`ARCHITECTURE.md`).
- The engine/content boundary is explicit, reinforcing that packs are *data* the `eeik` package reads.
- Deferred moves are on the record with rationale, not forgotten.

**Negative / trade-offs**
- The dual-purpose-adapter footgun persists until the deferred move; documented, not yet fixed.

---

## Related

- ADR-003 — EEIK generators run on HALO.
- ADR-004 — Capability-pack versioning & lockfile.
- [`ARCHITECTURE.md`](../../ARCHITECTURE.md), ROADMAP.md → *v1.4 → Tier 4 — Directory structure*.
