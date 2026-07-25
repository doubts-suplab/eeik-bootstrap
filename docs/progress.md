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
| **Governed generation on HALO** | ✅ | `generation_harness.py` — gate + audit + human-review routing; SUGGEST authority, never auto-enforces (G-5); fails safe without HALO |
| `eeik run <generator> --governed` | ✅ | Routes real generation through the harness; drafts staged, not applied |
| `eeik demo` (offline governed showcase) | ✅ | Runs a generator on the real gate with no API key |
| **Pack versioning** | ✅ | `pack_versions.py` — normalised versions + content digests |
| **Lockfile + drift detection** | ✅ | `eeik lock` / `diff` / `upgrade`; `eeik.lock`; CI gate via `diff --exit-code` |
| Engine test suite | ✅ | `tests/test_engine.py` — 8 tests (versioning, drift, HALO governance) |
| LLM-backed generators (repository/agent/knowledge/governance) | 🟡 | Prompts + governed harness exist; require the `claude` CLI / API key to produce real output |
| Stable Python API / SDK for consumers | ⬜ | Planned (Tier 2) — APEX would import instead of shelling out |
| EEIK MCP server | ⬜ | Planned (Tier 2) |
| Pack/agent registry + catalog | ⬜ | Planned (Tier 2) |
| `eeik verify` (conformance gate) | ⬜ | Planned (Tier 3) |
| Agent-generator emits HALO Agent Contracts | ⬜ | Planned (Tier 3) |
| Closed-loop knowledge capture from audit logs | ⬜ | Planned (Tier 3) |

---

## How to see it in action

```bash
# Governed generation on the real HALO gate — no API key needed
pip install agent-harness            # the HALO runtime EEIK now consumes
python3 scripts/eeik_cli.py demo

# Versioned adoption + drift detection
python3 scripts/eeik_cli.py lock     # pin adopted pack versions → eeik.lock
python3 scripts/eeik_cli.py diff     # later: report drift from upstream

# Tests (versioning, drift, HALO governance)
python3 -m pytest tests/ -q
```
