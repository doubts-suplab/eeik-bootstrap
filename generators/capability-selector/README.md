# Capability Selector

## Purpose

Maps `project-manifest.yaml` fields to the capability packs required for that project.

The Capability Selector is the decision engine that sits between the Bootstrap Engine and the Generators. It reads a validated manifest and produces the resolved list of packs that will be activated for the project.

## Where the logic lives (v1.4)

> **The authoritative resolver is code, not this directory.** As of the generation-engine
> refactor, manifest → pack resolution is implemented in **`eeik/packs.py::resolve_packs`** and
> exercised through `eeik activate` / `eeik.resolve_packs()`. It handles cases a flat matrix cannot —
> top-level `cloud`/`ai`/`technology.data`, governance profiles, domain packs, modernization triggers,
> and manifest `capability_packs` overrides.
>
> The human-readable field → pack reference matrix is the single canonical file at
> **[`bootstrap/resolvers/capability-matrix.yaml`](../../bootstrap/resolvers/capability-matrix.yaml)**.
> A duplicate stub previously lived here; it was removed to avoid drift. Keep the canonical matrix in
> sync with `resolve_packs`.

## Design Principle

```
project-manifest.yaml
        ↓
resolve_packs (eeik/packs.py)          ← authoritative, code-driven
        ↓
resolved packs (eeik activate)
        ↓
Repository Generator + Agent Factory
```

## Mapping reference

See [`bootstrap/resolvers/capability-matrix.yaml`](../../bootstrap/resolvers/capability-matrix.yaml)
for the full, canonical field → pack mapping (all 19 packs, availability annotated). A sample:

| Manifest Field | Value | Packs Activated |
|----------------|-------|----------------|
| `technology.backend.language` | `java21` | `architecture-pack`, `java-pack` |
| `cloud` | `aws` | `aws-pack` |
| `technology.data.*` | any set | `data-engineering-pack` |
| `domain` | `insurance` | `insurance-pack` |
| `ai.enabled` | `true` | `ai-engineering-pack`, `agent-harness-pack` |
| `governance.profile` | `regulated`/`enterprise` | `governance-pack` |

`core-pack` and `delivery-pack` are always included — they are foundational.

## Pack Dependencies

When a pack is selected, its `metadata.yaml` dependencies are read and dependent packs are added
automatically (e.g. `java-pack` → `architecture-pack`). `resolve_packs` returns packs in dependency
order.

## Inspecting resolution

```bash
eeik activate --list   # show the packs a manifest resolves to
eeik catalog           # queryable pack index
```
