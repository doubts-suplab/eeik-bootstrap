# Changelog

All notable changes to EEIK are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Commits use [Conventional Commits](https://www.conventionalcommits.org/), so entries can be regenerated
from history.

## [Unreleased]

The **governed generation engine** track (v1.4) — EEIK stops being copy-once static config and becomes a
governed, versioned, queryable engine consumed by APEX and CI.

### Added
- **Installable engine** `eeik/` with a stable CLI, typed SDK (`import eeik`, ADR-007), and a
  read-model **MCP server** (`eeik mcp`, ADR-006) — three surfaces over one implementation.
- **Governed generation on HALO** — every generator runs through the confidence gate; SUGGEST
  authority, staged for human review, never auto-applied; fails safe without HALO (ADR-003).
- **Pack versioning + lockfile** — `eeik lock` / `diff` / `upgrade` pin versions + content digests to
  `eeik.lock` (ADR-004).
- **Queryable catalog** — `eeik catalog` indexes all 22 packs / agents / standards with provenance.
- **Conformance gate** — `eeik verify` (`--strict` / `--exit-code`) asserts packs deliver what they
  declare (ADR-008).
- **HALO Agent Contracts** — `eeik contract` emits schema-valid, runtime-governed contracts (ADR-009).
- **Reference architectures** — 4 engine-surfaced blueprints, each with a schema-valid manifest,
  design, runbook, **deployable CDK app**, and **local-dev** (docker-compose + seed) (ADR-010).
- **Governed generation over MCP/SDK** — `eeik generate` / `eeik.generate()` / `eeik_generate` return a
  staged, human-review draft.
- **Closed-loop knowledge capture** — `eeik lessons` drafts staged `LL-NNN` lessons from HALO/APEX
  audit logs; SUGGEST authority (ADR-012).
- **Seed boundary** — `bootstrap/seed-manifest.yaml` + `eeik seed` make the dual-purpose adapters
  explicit; copies exactly the seed set (ADR-011).
- **`eeik doctor`** — diagnoses adoption/health problems (deps, HALO/MCP, manifest, resolution, drift,
  conformance) with an actionable fix per finding; never throws.
- **New capability packs** — Go, Node.js/TypeScript (backend languages) and Retail (domain); 22 total.
- **`--json`** on `status` / `validate` / `diff` (alongside catalog/architectures/verify/doctor/lessons).
- **Shipped-content smoke test** and a **Python 3.11/3.12/3.13** CI matrix with a coverage floor.
- **Contributor tooling** — `.pre-commit-config.yaml` (hygiene hooks + `ruff` + `mypy` + local
  `eeik lint` / `eeik verify` gates), `[tool.ruff]` / `[tool.mypy]` config, and a "Your First
  Contribution" + "Local Development Setup" guide in `CONTRIBUTING.md`.
- **Dependabot** (`.github/dependabot.yml`) for the `pip` and `github-actions` ecosystems, grouped
  minor/patch with Conventional-Commit prefixes.
- **CI diagnostics on failure** — `eeik-validate.yml` uploads `catalog`/`verify`/`doctor`/`diff` JSON
  reports as an artifact when the engine-tests gate fails, so a red run is debuggable from the artifact.
- **Adapter-generation + pack-materialization tests** — `tests/test_adapters.py` (kiro/codex/cursor/
  gemini generators) and `tests/test_materialization.py` (`eeik activate` copy, managed-marker,
  dry-run, `--clean`, skip-on-exists); 17 cases, closing a long-standing coverage gap.

### Changed
- **Adopted the HALO rebrand (agent-harness ADR-0013).** The runtime's Python distribution/import
  package was renamed `agent-harness` / `agent_harness` → `halo-agent-harness` / `halo_agent_harness`.
  EEIK's optional dependency, all `import` sites (`generation.py`, `contract.py`, `doctor.py`, tests),
  the mypy override, and the `pip install` hints in docs were migrated accordingly. The `agent-harness`
  **capability pack** and the runtime **repository** keep their names (unchanged by ADR-0013).
- Consolidated three divergent manifest schemas into one canonical
  `eeik/schemas/manifest.schema.json` (ADR-005); documented the four-layer directory taxonomy.
- Resolver unified on a single canonical `bootstrap/resolvers/capability-matrix.yaml`; the
  authoritative resolution is code (`eeik/packs.py`).
- CI templates (`quality-gate.yml`, `security-scan.yml`, `release.yml`) self-skip their product jobs on
  the engine repo (no Java/Angular/product build present).

### Fixed
- Schema ↔ resolver gaps: added `technology.data`, `technology.mainframe`, `alembic`, governance
  `adr_required` / `coverage_threshold`, the `anti-corruption-layer` pattern, and `solvency-ii` /
  `basel-iii` frameworks — so data / modernization / regulated manifests validate.
- Manifest validation no longer throws on malformed input (non-mapping sections are coerced).
- Resolver read `cloud` / `ai` at the canonical top level (AWS / AI packs now resolve).
- Adopting `ruff`/`mypy` surfaced and fixed real defects: a wrong `draft_lesson` return annotation, a
  shadowed loop variable, a lockfile None-safety gap, an unused-variable dead branch in the resolver,
  and several stale imports — plus pyupgrade modernizations (`datetime.UTC`, `collections.abc.Callable`).

## [1.x] — Stable baseline

Configuration layers for six AI coding tools (Claude Code, GitHub Copilot, Cursor, Kiro, Codex CLI,
Gemini CLI), core capability packs, agents, standards, hooks, and the knowledge layer. See
[ROADMAP.md](ROADMAP.md) for the full v1.1 completion list.

[Unreleased]: https://github.com/doubts-suplab/eeik-bootstrap/compare/v1.3.0...HEAD
