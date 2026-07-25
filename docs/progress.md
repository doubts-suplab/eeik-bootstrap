# EEIK — Progress (built vs. planned)

An honest status of the EEIK bootstrap. Mirrors the `docs/progress.md` convention used across the
ecosystem (`agent-harness`, `apex-sdlc`). For the forward plan see [`ROADMAP.md`](../ROADMAP.md).

Last updated: 2026-07-25 (v1.4 — Governed Generation Engine, Tier 1).

---

## Legend

- ✅ **Built** — implemented and exercised (tests or a runnable command).
- 🟡 **Partial** — usable, with known gaps.
- ⬜ **Planned** — designed, not yet built.

---

## Configuration layer (the original bootstrap)

| Capability | Status | Notes |
|---|---|---|
| 6 AI-tool adapters (Claude, Copilot, Kiro, Codex, Cursor, Gemini) | ✅ | `.claude/`, `.github/`, `.kiro/`, `.cursor/`, `AGENTS.md`, `GEMINI.md` |
| 19 capability packs | ✅ | Every pack now carries `metadata.yaml` with a `version` |
| Manifest → pack resolution → `.claude/` materialisation | ✅ | `activate_packs.py`, `capability-matrix.yaml` |
| Manifest validation (schema + governance rules) | ✅ | `validate_manifest.py` |
| Adapter generation from manifest | ✅ | `generate_adapters.py` |
| Safety hooks (bash/write/edit guards, session log) | ✅ | `.claude/hooks/` |

## Generation engine (v1.4 — the transformation)

| Capability | Status | Notes |
|---|---|---|
| **Governed generation on HALO** | ✅ | `eeik/generation.py` — gate + audit + human-review routing; SUGGEST authority, never auto-enforces (G-5); fails safe without HALO |
| `eeik run <generator> --governed` | ✅ | Routes real generation through the harness; drafts staged, not applied |
| `eeik demo` (offline governed showcase) | ✅ | Runs a generator on the real gate with no API key |
| **Pack versioning** | ✅ | `eeik/versions.py` — normalised versions + content digests |
| **Lockfile + drift detection** | ✅ | `eeik lock` / `diff` / `upgrade`; `eeik.lock`; CI gate via `diff --exit-code` |
| Engine test suite | ✅ | `tests/test_engine.py` — 11 tests (versioning, drift, catalog, HALO governance) |
| **Installable engine package** | ✅ | `scripts/` → `eeik/` package + `pyproject.toml`; `eeik` console script / `python -m eeik`; back-compat `scripts/*.py` shims; CI installs the package |
| **Single canonical manifest schema** | ✅ | `eeik/schemas/manifest.schema.json` replaces 3 divergent copies; fixed the stale-schema bug that rejected EEIK's own examples |
| **Pack/agent registry + catalog** | ✅ | `eeik catalog` — queryable index (`--tag` / `--query` / `--provides` / `--json`); all 19 packs tagged + categorised (`eeik/catalog.py`) |
| **Directory taxonomy documented** | ✅ | ADR-005 + `ARCHITECTURE.md` — engine / content / adapters / docs layers + placement rule |
| LLM-backed generators (repository/agent/knowledge/governance) | 🟡 | Prompts + governed harness exist; require the `claude` CLI / API key to produce real output |
| Stable Python API / SDK for consumers | ⬜ | Planned (Tier 2) — APEX would import instead of shelling out (unblocked by the package) |
| EEIK MCP server | ⬜ | Planned (Tier 2) — will expose the `catalog` read model + validate/resolve/generate |
| `eeik verify` (conformance gate) | ⬜ | Planned (Tier 3) |
| Agent-generator emits HALO Agent Contracts | ⬜ | Planned (Tier 3) |
| Closed-loop knowledge capture from audit logs | ⬜ | Planned (Tier 3) |
| Clarify dual-purpose root adapters | ⬜ | Planned (Tier 4) — taxonomy now documented (ADR-005) |

---

## How to see it in action

```bash
pip install -e ".[test]"     # installs the eeik engine + HALO (agent-harness) + pytest

# Governed generation on the real HALO gate — no API key needed
eeik demo

# Versioned adoption + drift detection
eeik lock                    # pin adopted pack versions → eeik.lock
eeik diff                    # later: report drift from upstream

# Query the capability catalog
eeik catalog --tag regulated             # packs tagged 'regulated'
eeik catalog --provides java-architect   # which pack provides that agent
eeik catalog --json                      # machine-readable index (MCP read model)

# Tests (versioning, drift, catalog, HALO governance)
python3 -m pytest tests/ -q
```
