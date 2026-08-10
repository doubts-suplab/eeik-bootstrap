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
| **Conformance gate (`eeik verify`)** | ✅ | Declared agents/standards resolve to files; manifest + lock consistent; fail/warn/pass + `--strict`; CLI/SDK/MCP (`eeik/verify.py`, ADR-008) |
| **Pack metadata reconciled** | ✅ | 30 gaps fixed (trim phantoms, `X-standard`→`X` renames, declare shipped files, author `insurance-compliance-standard`); `eeik verify --strict` clean (0/0/21); catalog advertises only real files |
| **Agent Contracts by construction** | ✅ | `eeik contract` / `eeik.agent_contract()` emit `agent-contract.schema.json`-conformant contracts per blueprint; validated by HALO's own validator (`eeik/contract.py`, ADR-009) |
| **Reference architectures (engine-surfaced)** | ✅ | 5 blueprints — order-management, ai-augmented-service, data-platform, multi-tenant-saas, multi-agent-ai-platform — each a schema-valid manifest + design + runbook; `eeik architectures` (CLI/SDK/MCP); `eeik verify` checks manifest + pack match (`eeik/architectures.py`, ADR-010) |
| **v1.2 domain packs completed** | ✅ | banking (`banking-domain-expert`, `payments-specialist`) + healthcare (`healthcare-domain-expert`, `clinical-data-specialist`) authored; python/data-engineering/openshift already substantive; verify clean |
| Resolver + schema fixes (surfaced by ref-archs) | ✅ | `resolve_packs` reads top-level `cloud`/`ai` and `technology.data.*` (aws/ai-engineering/data-engineering packs now resolve); schema gains `technology.data`, `alembic`, `adr_required`, `coverage_threshold`; CLI dispatches in-process |
| Engine test suite | ✅ | 50 tests — engine + MCP (round-trip) + SDK + verify + contracts + reference architectures |
| **Installable engine package** | ✅ | `scripts/` → `eeik/` package + `pyproject.toml`; `eeik` console script / `python -m eeik`; back-compat `scripts/*.py` shims; CI installs the package |
| **Single canonical manifest schema** | ✅ | `eeik/schemas/manifest.schema.json` replaces 3 divergent copies; fixed the stale-schema bug that rejected EEIK's own examples |
| **Pack/agent registry + catalog** | ✅ | `eeik catalog` — queryable index (`--tag` / `--query` / `--provides` / `--json`); all 20 packs tagged + categorised (`eeik/catalog.py`) |
| **Go language pack** | ✅ | `go-developer`, `go-microservices-engineer` + go-standard (cloud-native, gRPC, `-race` tests); `technology.backend.language: go` resolves it (schema + resolver + matrix) |
| **Node.js / TypeScript pack** | ✅ | `node-developer`, `typescript-api-engineer` + node-standard (strict TS, Zod, NestJS/Fastify, Vitest); resolves on `backend.language: node` |
| **Retail domain pack** | ✅ | `retail-domain-expert`, `ecommerce-specialist` + retail-standard (catalog/checkout/inventory/order state machine, PCI-DSS, GDPR); resolves on `project.domain: retail` |
| **Cloud/ops packs (FinOps · Chaos · Platform Eng.)** | ✅ | `finops-engineer` (cost visibility, rightsizing, RI/Savings-Plans, unit economics), `chaos-engineer` (hypothesis-driven fault injection, GameDays), `platform-engineer` (IDP, golden paths, Backstage) + standards. Opt-in flags `cloud.finops` / `observability.chaos_engineering` / `delivery.platform_engineering` — off by default. **25 packs total** |
| **Windsurf + Cline adapters** | ✅ | `eeik generate-adapters` also emits `.windsurf/rules/` + `.clinerules/` — **8 AI tools** at standards parity (`eeik/adapters.py`) |
| **Opt-in telemetry (local-first)** | ✅ | `eeik telemetry` — strictly opt-in, local-only, non-identifying pack/generator counters in `~/.eeik/`; no network code; `record()` no-op until enabled (`eeik/telemetry.py`) |
| **Versioned APEX integration contract** | ✅ | `docs/reference/apex-integration-contract.md` (v1.0) — the stable SDK/MCP surface + semver rules + assertable invariants consumers build against |
| **Directory taxonomy documented** | ✅ | ADR-005 + `ARCHITECTURE.md` — engine / content / adapters / docs layers + placement rule |
| **LLM-backed generators (repository/agent/knowledge/governance)** | ✅ | Real generation runs on HALO's `LlmPort` (Anthropic adapter, keyed by `ANTHROPIC_API_KEY`); `resolve_producer` returns `producer_kind='llm'` when a port is available and **fails safe** to the offline producer otherwise. Governed identically (SUGGEST, staged, `auto_enforced=False`). SDK `eeik.generate()`, MCP `eeik_generate`, and `eeik run <gen> --governed` all use it (`eeik/generation.py`) |
| **EEIK MCP server** | ✅ | `eeik mcp` — read model over MCP (`eeik_catalog`, `eeik_validate_manifest`, `eeik_resolve_packs`, `eeik_pack_drift`); read-only v1 (`eeik/mcp_server.py`, ADR-006) |
| **Stable Python API / SDK** | ✅ | `import eeik` — typed `find_packs`/`providers_of`/`validate_manifest`/`resolve_packs`/`pack_drift`/`write_lock`; CLI + MCP delegate to it (`eeik/api.py`, ADR-007) |
| **apex-sdlc onboarding consumes the engine** | ✅ | Cross-repo: APEX validates + resolves via the real engine — SDK (`import eeik`) or MCP (`eeik mcp`), vendored fallback (apex `app/onboarding/eeik_engine.py`) |
| **`eeik verify` (conformance gate)** | ✅ | `eeik verify --strict --exit-code` — pack conformance, manifest validity, lock drift, reference-architecture resolution; CI-gated (`eeik/verify.py`, ADR-008) |
| **Agent-generator emits HALO Agent Contracts** | ✅ | `eeik contract` emits a schema-valid HALO Agent Contract from a pack agent (`eeik/contract.py`, ADR-009) |
| **Reference architectures (engine-surfaced)** | ✅ | 5 blueprints — descriptor + schema-valid manifest + design + runbook + **deployable `cdk/` and `local-dev/`** (per-arch CDK app + docker-compose + seed data); `eeik architectures` surfaces deployment, verify-checked (`eeik/architectures.py`, ADR-010) |
| **Single canonical capability matrix** | ✅ | Resolver overlap consolidated onto `bootstrap/resolvers/capability-matrix.yaml`; duplicate stub removed; authoritative resolution is code (`eeik/packs.py`); APEX vendored copy re-synced |
| **Governed generation over MCP** | ✅ | `eeik_generate` (MCP) + `eeik.generate()` (SDK) return a staged, human-review draft — SUGGEST authority, `auto_enforced=false`, `autoApplied=false`, never applied; fails safe without HALO (`eeik/generation.py::run_generation`) |
| **Closed-loop knowledge capture from audit logs** | ✅ | `eeik lessons` / `eeik.capture_lessons()` / `eeik_capture_lessons` (MCP): HALO/APEX audit → staged `LL-NNN` lesson drafts, SUGGEST authority (`auto_enforced=false`), human-curated (`eeik/lessons.py`, ADR-012) |
| **Clarify dual-purpose root adapters** | ✅ | `bootstrap/seed-manifest.yaml` classifies every root entry seed/generated/engine; `eeik seed` + `eeik.seed_plan()` copy exactly the seed set; seed CI self-skips on the engine repo (ADR-011) |
| **`eeik doctor` (adoption/health diagnostic)** | ✅ | Diagnoses Python/deps, HALO+MCP availability, manifest validity, pack resolution, adapter materialisation, lock drift, conformance — each with an actionable fix; never throws. CLI (`--json`/`--strict`/`--exit-code`) + `eeik.doctor()` SDK + `eeik_doctor` MCP (`eeik/doctor.py`) |
| **Shipped-content smoke test + schema completeness** | ✅ | `tests/test_shipped_content.py` guards the real packs/examples; surfaced + fixed a validator crash on malformed input, a stale example, and schema↔resolver gaps (`technology.mainframe`, `anti-corruption-layer`, `solvency-ii`/`basel-iii`). `--json` on status/validate/diff. Engine tests run on **Python 3.11/3.12/3.13** with a **coverage floor (≥50%)** |
| **`eeik lint` (content-quality gate)** | ✅ | Lints agent/standard content well-formedness (frontmatter, name-matches-file, description quality, model/tools, structure); pass/warn/fail; CLI + `eeik.lint()` + `eeik_lint` MCP; replaces the inline frontmatter grep in CI (`eeik/lint.py`) |

---

## Backlog — Adoption, Distribution & Robustness (evaluation-driven, planned)

An external evaluation (2026-08) rates the engine as mature and well-governed; the biggest remaining
leverage is **first-adopter cognitive load** and **consuming the engine outside this monorepo**. The full
plan + per-item feasibility lives in [ROADMAP.md → Future Enhancements](../ROADMAP.md#future-enhancements--adoption-distribution--robustness-evaluation-driven).
Recommended next increment — a **v1.5 "Adoption & Distribution"** milestone (mostly docs + packaging,
low risk, high impact):

| Theme | Headline items | Status |
|---|---|---|
| Onboarding | ~~Adopter-first README + top-of-repo flow diagram; lead with `eeik seed`~~ ✅; ~~interactive guide as the newcomer landing page (README leads with it; guide opens with a Get Started section)~~ ✅ | ✅ Done |
| Distribution | ~~PyPI release automation (OIDC)~~ ✅ workflow ready; ~~badges~~ ✅ (GitHub topics = maintainer repo-setting) | ✅ Done |
| CLI UX | ~~`eeik doctor`~~ ✅; ~~`--json` on status/validate/diff~~ ✅ (inspection commands consistent) | ✅ Done |
| Testing | ~~Shipped-content smoke test~~ ✅; ~~Python 3.11/3.12/3.13 matrix + coverage floor~~ ✅; ~~hook tests~~ ✅ (30 subprocess cases); ~~content lint~~ ✅; ~~adapter-generation + pack-materialization tests~~ ✅ (17 cases); ~~LLM-generation tests~~ ✅ (StubLlm, 7 cases) | ✅ Done |
| Docs/process | ~~`CHANGELOG.md`, `CODE_OF_CONDUCT.md`, SUPPORT/FAQ~~ ✅; ~~engine security-model section~~ ✅ | ✅ Done |
| CI polish | ~~Dependabot (pip + github-actions)~~ ✅; ~~pre-commit (ruff/mypy + local eeik lint/verify)~~ ✅; ~~catalog/verify diagnostics uploaded as CI artifacts on failure~~ ✅ | ✅ Done _(repo-admin follow-up: mark `verify --strict` + `diff` as required checks)_ |
| Content | ~~Adapter parity matrix~~ ✅; ~~domain-pack criteria~~ ✅ (CONTRIBUTING); ~~staged→committed lessons promotion workflow~~ ✅ (reference-architecture expansion ongoing) | 🟡 In progress |
| Governance | ~~Preview/dry-run generation~~ ✅; ~~HALO-absent "works offline" table~~ ✅; ~~MCP production notes~~ ✅ (see [engine-reference.md](reference/engine-reference.md)) | ✅ Done |
| Strategic | Composable packs; signed packs / private registry; opt-in telemetry (license: AGPL-3.0 retained by decision) | ⬜ Planned (decisions) |

> **Composable packs** needs a *design decision*, not just implementation (a dependency model beyond
> today's flat `dependencies:`). The license question is settled — AGPL-3.0 is retained.

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

# Conformance gate — do packs deliver what they declare?
eeik verify                              # report (fail / warn / pass)
eeik verify --exit-code                  # CI gate (non-zero on hard failures)

# Proven, engine-surfaced reference architectures
eeik architectures                       # list blueprints
eeik architectures order-management      # detail: stack, components, resolved packs

# Serve the read model over MCP (any MCP host can call it live)
pip install -e ".[mcp]" && eeik mcp      # tools: catalog, validate_manifest, resolve_packs, pack_drift, verify

# Tests (versioning, drift, catalog, HALO governance, MCP round-trip)
python3 -m pytest tests/ -q
```
