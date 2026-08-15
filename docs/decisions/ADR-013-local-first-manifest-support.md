# ADR-013 — The canonical manifest expresses a local-first / self-hosted posture

**Date:** 2026-08-15
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** Adopting the existing Aether repos under eeik governance (governance-spine work)

---

## Context and Problem Statement

The Aether ecosystem repos (aether-core, -grid, -memory, -vault, -flow, -iel) are **eeik-descended**
(provenance blocks, catalogue agents, mirrored golden rules) but were configured under the legacy
copy-once model, and their hand-authored `aether.manifest.yaml` files do **not** validate against the
canonical `eeik/schemas/manifest.schema.json` (`additionalProperties: false`).

Two of the mismatches are not accidental drift — they are the ecosystem's deliberate identity:

- `cloud.provider: local-first` — Aether runs self-hosted / offline-capable (local Ollama, Docker
  Compose), with **no** managed-cloud dependency. The schema enum was `aws | azure | gcp | hybrid`;
  none is honest for a local-first system, and forcing `hybrid` would misrepresent it.
- `delivery.methodology: incremental` — Aether ships in small, doc-synced increments rather than fixed
  sprints. The enum was `agile | kanban | scaled-agile`.

Relatedly, the `ai` block could not name Aether's actual runtime (**HALO / agent-harness**) or model
provider (**Ollama**): `framework` lacked `agent-harness`, and `foundation_model` had no local option.

Since eeik is *our own* governed engine, the right fix is to make the canonical schema able to describe
this posture — not to distort the repos to fit an AWS-shaped schema.

## Decision

**Extend the canonical manifest schema additively so a local-first, HALO-on-Ollama posture is
first-class.** Four enum additions, all backward-compatible:

- `cloud.provider` += `local-first`
- `delivery.methodology` += `incremental`
- `ai.framework` += `agent-harness` (the HALO generic agent runtime)
- `ai.foundation_model` += `ollama` (locally-served open models)

No fields were removed, no required-ness changed, no existing enum value altered — every previously
valid manifest still validates. `bootstrap/manifests/manifest-template.yaml` documents the new values.

## Considered Options

1. **Extend the schema additively (chosen)** — keeps the local-first identity honest; additive enum
   values are zero-risk to existing manifests; lets all six Aether repos validate as-authored.
2. **Force Aether onto `hybrid` / `agile`** — rejected: misrepresents a deliberately self-hosted,
   increment-driven ecosystem, and buries the local-first posture the repos were designed around.
3. **Add a per-project schema override** — rejected: fragments the "one canonical schema" invariant
   (CLAUDE.md) for what is a small, generally-useful set of values.

## Consequences

**Positive**
- The Aether repos can adopt a canonical `project-manifest.yaml` that validates without lying about
  their infrastructure or cadence — the precondition for `eeik lock` / `diff` / `verify` governance.
- Any future self-hosted / on-prem adopter benefits from the same vocabulary.

**Negative / trade-offs**
- The `ai` enums now carry two Aether-motivated values; kept generic (`agent-harness`, `ollama`) rather
  than brand-specific so they read as reusable, not Aether-only.

## Related

- `eeik/schemas/manifest.schema.json`, `bootstrap/manifests/manifest-template.yaml`.
- Consumed by the Aether adoption work (canonical `project-manifest.yaml` for aether-core, then the
  sibling-manifest migration). ADR-004 (versioning/lockfile), ADR-008 (conformance gate).
