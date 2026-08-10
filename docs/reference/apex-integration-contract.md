# EEIK Integration Contract (for APEX and other consumers)

**Contract version: `1.0`** · Engine: `eeik >= 1.4` · Status: **stable**

This is the versioned surface a consuming product — primarily [apex-sdlc](https://github.com/doubts-suplab/apex-sdlc),
also aether-grid — can build against and trust across engine releases. EEIK is an **engine other tools
consume, not a product** (see [ROADMAP — posture](../../ROADMAP.md)); this document is the promise that
makes that consumption safe.

> **The rule:** anything listed under **Stable surface** below changes only under semver. Anything not
> listed is internal and may change without notice — do not import it.

---

## Consumption modes

A consumer picks one; all three return the same shapes for the same inputs.

| Mode | How | When |
|---|---|---|
| **SDK** (in-process) | `import eeik`; call the typed API (ADR-007) | Same host/venv as the engine — fastest, no subprocess |
| **MCP** (over the protocol) | spawn `eeik mcp`; call the `eeik_*` tools (ADR-006) | Engine runs out-of-process / remote; language-neutral |
| **Vendored fallback** | a minimal re-implementation over the vendored `capability-matrix.yaml` | Engine not installed on the host (degraded, resolve-only) |

APEX wires all three behind one interface (`app/onboarding/eeik_engine.py`: `SdkEngine` / `McpEngine`
+ offline fallback), selected at runtime. The contract below is what that interface depends on.

---

## Stable surface

Each SDK function has a 1:1 MCP tool with the same inputs/outputs. Payloads are JSON-serialisable; every
typed result exposes `.to_dict()`.

### Read model (the core APEX depends on)

| Capability | SDK | MCP tool | Input → Output |
|---|---|---|---|
| Validate a manifest | `eeik.validate_manifest(manifest=…\|content=…\|path=…)` | `eeik_validate_manifest` | manifest → `ValidationResult{valid, errors[], warnings[]}` |
| Resolve capability packs | `eeik.resolve_packs(manifest=…\|content=…\|path=…)` | `eeik_resolve_packs` | manifest → `list[str]` (pack names, `core` first) |
| Query the catalog | `eeik.find_packs(tag=…, query=…)` | `eeik_catalog` | filters → `list[Pack]` |
| Providers of a capability | `eeik.providers_of(name)` | `eeik_catalog` (`provides`) | name → `list[Provider]` |
| Pack drift vs. lockfile | `eeik.pack_drift(lockfile=…)` | `eeik_pack_drift` | — → `DriftReport{lockPresent, driftCount, drift[]}` |
| Reference architectures | `eeik.reference_architectures()` / `reference_architecture(name)` | `eeik_reference_architectures` | — → `list[ReferenceArchitecture]` |

### Conformance & health (advisory)

| Capability | SDK | MCP tool | Output |
|---|---|---|---|
| Conformance gate | `eeik.verify()` | `eeik_verify` | `VerifyReport{ok, findings[]}` |
| Content lint | `eeik.lint()` | `eeik_lint` | `LintReport` |
| Adoption/health doctor | `eeik.doctor()` | `eeik_doctor` | `DoctorReport{healthy, diagnostics[]}` |

### Governed write (SUGGEST authority)

| Capability | SDK | MCP tool | Guarantee |
|---|---|---|---|
| Generate an artifact | `eeik.generate(generator, spec=…, preview=…)` | `eeik_generate` | Runs on HALO; **`auto_enforced=False`**, staged for human review, never applied; fails safe without HALO |
| Emit / validate a HALO Agent Contract | `eeik.agent_contract(...)` / `eeik.validate_agent_contract(...)` | — | schema-conformant (ADR-009) |
| Capture lessons from audit logs | `eeik.capture_lessons(records)` | `eeik_capture_lessons` | staged `LL-NNN` drafts, SUGGEST authority |

### Stable data types

`ValidationResult`, `Pack`, `Provider`, `DriftReport` / `DriftEntry`, `ReferenceArchitecture`,
`VerifyReport` / `Finding`, `LintReport`, `DoctorReport`, `GenerationOutcome`, `LessonCaptureReport` —
all exported from `eeik.__all__`, all with `.to_dict()`. Field **additions** are minor-version; field
**removals/renames** are major.

---

## Compatibility guarantees (semver on this contract)

- **Patch** (`1.0.x`) — bug fixes; no surface change.
- **Minor** (`1.x`) — additive only: new functions/tools, new optional inputs, new result fields.
  Existing calls keep working.
- **Major** (`2.0`) — may remove/rename. Announced in `CHANGELOG.md` with a migration note; the prior
  major is supported for one release.

Additional promises:

- **One drift schema** across CLI/SDK/MCP: `eeik diff --json` == `eeik.pack_drift().to_dict()` ==
  `eeik_pack_drift`.
- **`resolve_packs` order is stable**: `core` first, remainder sorted — safe to diff/snapshot.
- **Generation never auto-applies**: `GenerationOutcome.auto_enforced` is always `False` and
  `bypass_total` is always `0` — a consumer can assert both.
- **Fail-safe**: read-model calls never require HALO; governed generation degrades to staged-only when
  HALO is absent (`halo_available=False`), never throwing.

## What is NOT part of the contract

Internal modules (`eeik.packs`, `eeik.generation` internals, `eeik.runner`, `eeik.prompts`, `_`-prefixed
names), console output/formatting, exit codes beyond documented `--exit-code` gates, and the on-disk
layout of `capability-packs/` (consume it through `find_packs()`, not by reading files). Import these and
you are outside the contract.

## Versioning this document

Bump **Contract version** on any change to the Stable surface, and record it in `CHANGELOG.md`. The
engine version and the contract version move independently — an engine `1.5` may still serve contract
`1.0`.
