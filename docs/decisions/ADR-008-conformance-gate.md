# ADR-008 — `eeik verify`: the conformance gate

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — Tier 3, closing the "generate → govern → verify" loop

---

## Context and Problem Statement

EEIK can now *generate* config (generators), *govern* generation (HALO), *version* it (lockfile), and
*index* it (catalog/SDK). What it could not do was **assert conformance**: does a repository actually
deliver what it claims? The catalog and SDK read a pack's `metadata.yaml` (`agents_provided`,
`standards_provided`) and report them as fact — but nothing checked those declarations against reality.
Running the first draft of the check found the problem immediately: **30 declarations across ~13 packs
resolve to no file** (e.g. `java` declares `spring-boot-engineer` with no such agent, and ships
`spring-security-engineer` without declaring it). The registry was advertising phantom capabilities.

## Decision

**Ship `eeik verify` — a conformance gate** that runs a set of checks and reports typed findings:

- **pack-conformance** — every declared agent/standard resolves to a file, and every shipped file is
  declared. A declaration resolves if the file exists **in the pack** *or* **in the shared `.claude/`
  layer** (some cross-cutting agents are materialised centrally, not per-pack — that is legitimate, not
  a gap).
- **manifest** — if a `project-manifest.yaml` exists, it validates against the canonical schema (schema
  errors are hard failures).
- **lock-drift** — if an `eeik.lock` exists, the packs still match it.

**Finding levels & gating.** Each finding is `fail` (hard correctness), `warn` (advisory / pre-existing
content gap), or `pass`. Exit code is non-zero on any `fail`; `--strict` also fails on `warn`. So CI can
run `eeik verify --exit-code` as a correctness gate today, and adopt `--strict` once the content gaps are
reconciled. Exposed on all three surfaces: `eeik verify`, `eeik.verify()` (SDK), and the `eeik_verify`
MCP tool — one implementation.

**On the 30 findings — reconcile separately, don't paper over.** Pack-conformance mismatches are
reported as **warnings**, not failures, because they are pre-existing *content* gaps, not engine
defects, and bundling a 30-line metadata/file reconciliation into the tool that discovered it would hide
the signal. Reconciliation (trim phantom declarations, declare shipped files, or author the missing
ones) is tracked in ROADMAP Tier 3 as its own change. Surfacing the gaps *is* the feature working.

## Considered Options

1. **Ship the gate now; track reconciliation (chosen)** — the tool's value is finding drift; warnings
   keep CI green while the content is fixed deliberately.
2. **Auto-fix metadata inside `verify`** — rejected: silently trimming advertised capabilities (or
   fabricating agent files) is a content decision, not a job for a read-only gate.
3. **Make every mismatch a hard failure** — rejected: would block CI on 30 pre-existing gaps with no
   migration path.

## Consequences

**Positive**
- The "generate → govern → verify" loop is closed; the catalog/SDK can be *trusted* once warnings clear.
- Conformance is CI-gateable (`--exit-code`, `--strict`) and queryable live (`eeik_verify` over MCP).
- The 30 gaps are now visible and tracked instead of silently shipped.

**Negative / trade-offs**
- `eeik verify` reports 30 warnings until the pack metadata is reconciled (tracked, Tier 3).
- `eeik.verify()` (function) shadows the `eeik.verify` submodule attribute; internal code imports the
  module as `from eeik.verify import …` (no consumer relies on `from eeik import verify` as the module).

## Related

- ADR-004 (lockfile/drift), ADR-007 (SDK). `eeik/verify.py`, `tests/test_verify.py`.
- ROADMAP Tier 3 → "reconcile pack metadata with shipped files (30 `eeik verify` warnings)".
