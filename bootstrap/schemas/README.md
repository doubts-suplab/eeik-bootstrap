# Manifest schema — moved

The canonical, machine-readable project-manifest schema now lives **with the engine package**, as the
single source of truth (see [ADR-004] and the v1.4 restructure):

- **Normative schema:** [`eeik/schemas/manifest.schema.json`](../../eeik/schemas/manifest.schema.json)
  — JSON Schema draft-07; what `eeik validate` enforces.
- **Human-readable field reference:** [`docs/reference/manifest-schema.md`](../../docs/reference/manifest-schema.md).

Previously this directory held `manifest-schema.json` and a separate `manifest-schema.yaml`, and a
third, diverged copy lived under `scripts/schemas/`. Those were consolidated into the one canonical
file above so the validator, the generators, and the docs can never drift apart again.

[ADR-004]: ../../docs/decisions/ADR-004-capability-pack-versioning-and-lockfile.md
