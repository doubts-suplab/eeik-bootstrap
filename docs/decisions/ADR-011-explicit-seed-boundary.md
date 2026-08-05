# ADR-011 — The dual-purpose adapter boundary is explicit and machine-readable

**Date:** 2026-08-05
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — directory maturation (ROADMAP Tier 4)

---

## Context and Problem Statement

EEIK's root adapter directories — `.claude/`, `.github/`, `.cursor/`, `.kiro/`, and the root tool
contexts (`AGENTS.md`, `GEMINI.md`) plus `.vscode/` / `intellij/` — are **dual-purpose**: they are
simultaneously EEIK's own dogfood configuration (the engine runs against them) *and* the seed an
adopting project copies. ADR-005 named the four layers (engine / content / adapters / docs) but left
the adapter layer's dual role as a documented footgun: a naive `cp -r` of the repo drags the engine
package, the test suite, EEIK's own `eeik.lock`, and — worst — EEIK's *own* materialised agent set into
a product. There was no explicit, checkable statement of "what does an adopting project actually take?"

Concretely this bit us in CI: the generic product `quality-gate.yml` (a seed template) ran against the
eeik-bootstrap repo itself and failed, because the repo has no product build. The dual purpose wasn't
just a doc smell — it produced red checks.

## Decision

**Classify every root entry, in one machine-readable manifest, and make the copy operation explicit.**

`bootstrap/seed-manifest.yaml` is the single source of truth. Each root entry is one of three kinds:

- **`seed`** — copy into your project. Adapter shells + shared config a product wants verbatim
  (`.github/instructions`, the `quality-gate.yml` template, editor settings, a starter `CLAUDE.md`).
- **`generated`** — do **not** hand-copy. Produced by `eeik activate` / `eeik generate-adapters` from
  *your* manifest (`.claude/agents`, `.kiro/`, `.cursor/`, `AGENTS.md`, `GEMINI.md`). Copying EEIK's
  dogfood output would import EEIK's own agent set; regenerate instead.
- **`engine`** — EEIK's engine, content sources, and docs (`eeik/`, `tests/`, `capability-packs/`,
  `bootstrap/`, `eeik.lock`, …). Never copied; consumed through the installed `eeik` engine.

The manifest is surfaced on all three surfaces (consistent with ADR-006/007): `eeik seed` (CLI —
`--list` prints the taxonomy, `--into <dir> [--apply]` copies exactly the `seed` set),
`eeik.seed_plan()` (SDK), and it feeds the read model. `eeik seed` is **additive** to `cp -r`
ergonomics — it copies the *right subset* so an adopter no longer has to know which directories are
engine-only.

Separately, the seed templates that ship in the copy-set are made **self-aware of the seed repo**: the
`quality-gate.yml` product jobs (Java/Angular/Python) self-skip after a detect step when their project
files (`pom.xml` / `package.json` / `src/`) are absent — green on the engine repo, fully functional
downstream.

## Considered Options

1. **Machine-readable seed manifest + `eeik seed` (chosen)** — one source of truth; the boundary is
   checkable (a test asserts engine-only paths never appear in the seed set) and scriptable.
2. **Prose in ARCHITECTURE.md only** — rejected: unverifiable, drifts, and still leaves `cp -r` as the
   copy mechanism with no guard.
3. **Physically split the repo** (engine repo + seed repo) — rejected for now: breaks the dogfooding
   that keeps EEIK's own config honest, and is a far larger change than the ambiguity warrants.

## Consequences

**Positive**
- "What does an adopting project copy?" has one answer, in code, on three surfaces.
- `cp -r` adoption still works; `eeik seed` is the precise, guard-railed alternative.
- A test (`tests/test_seed.py`) fails if an engine-only path is ever classified as `seed`.
- The CI footgun is closed: seed templates self-skip on the engine repo.

**Negative / trade-offs**
- The manifest must be kept in sync as root entries are added (a test checks declared paths exist).
- The engine and seed still physically share one repo; this ADR makes the boundary explicit rather
  than physical. A future split (option 3) remains open if the layers diverge further.

## Related

- ADR-005 (layered directory taxonomy), ARCHITECTURE.md. `bootstrap/seed-manifest.yaml`, `eeik/seed.py`,
  `tests/test_seed.py`, `.github/workflows/quality-gate.yml`.
