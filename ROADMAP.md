# EEIK Bootstrap — Roadmap

This document tracks planned enhancements to the framework. Items are grouped by release milestone.

---

## Platform Posture — engine, not product

As the ecosystem matured, **APEX** grew from an augmentation *plan* into the runnable AI-SDLC
*product*, and **HALO** (`agent-harness`) became the governed agent runtime both APEX and Aether
consume. EEIK's transformation is deliberately **not** to become a competing product platform — APEX
already owns that surface and *consumes EEIK's generators for onboarding*. Instead EEIK evolves from a
passive pile of config + scripts into a **governed generation *engine*** with a stable, programmatic
surface that APEX and CI consume.

The boundaries the ecosystem is built on:

| Concern | Owner |
|---|---|
| Governs **generation** (repo/agent/standard scaffolding) | **EEIK** |
| Governs **execution** (confidence gate, tool registry, audit) | **HALO** |
| The **SDLC product** that orchestrates both | **APEX** |
| The **methodology/spec** everything conforms to | **AIEL** |

EEIK's "platform" energy goes into being the thing others call — not a new UI.

---

## Current Release — v1.x (Stable)

The v1.x line is the current stable baseline. It covers:

- **Core capability packs:** Java, Angular, AWS, Architecture, Core, Governance
- **48 agents** spanning Java, Angular, AWS, Python, Data Engineering, Kubernetes, AI/ML, agentic frameworks, operations, and modernisation
- **24 slash commands** covering the full development lifecycle
- **27 standards** for all primary technology stacks
- **4 safety hooks** (pre-bash-guard, pre-write-guard, post-edit-check, on-stop)
- **Dual-tool support:** Claude Code (`.claude/`) + GitHub Copilot (`.github/`)
- **Cursor and Kiro** configuration stubs

---

## v1.1 — Framework Completion (Complete)

Closing identified gaps across standards, agents, commands, and workflows.

### Standards (NEW)
- [x] `python.md` — PEP 8, type annotations, logging, testing
- [x] `fastapi.md` — Router organisation, Pydantic, DI, async/await
- [x] `data-engineering.md` — Kafka, Spark, dbt, idempotency
- [x] `ai-governance.md` — Model cards, risk tiers, EU AI Act, LLM controls
- [x] `modernization-patterns.md` — Strangler fig, ACL, COBOL/RPG field mapping
- [x] `graphql.md` — Schema design, N+1 prevention, pagination, security
- [x] `event-driven.md` — Outbox pattern, schema evolution, DLQ, circuit breaker

### Standards (EXPANDED)
- [x] `integration-standard.md` — Timeout table, retry policy, circuit breaker config, idempotency keys
- [x] `api-standard.md` — Authentication patterns, versioning strategy, error code registry, rate limiting

### Agents (NEW)
- [x] `python-developer` — FastAPI/Django/Flask, Pydantic, pytest, type annotations
- [x] `data-engineer` — Kafka, Spark, dbt, Airflow, idempotent pipelines
- [x] `kubernetes-engineer` — Helm, RBAC, NetworkPolicy, HPA, OpenShift
- [x] `dba-advisor` — Migrations, query plans, index design, connection pool sizing

### Slash Commands (NEW)
- [x] `/threat-model` — STRIDE threat modelling workflow
- [x] `/migrate-db` — Flyway/Liquibase migration generator with risk assessment
- [x] `/api-contract` — Contract-first API design with OpenAPI + Pact stubs
- [x] `/tech-debt` — Register and manage technical debt
- [x] `/setup-memory` — Interactive memory initialisation interview

### GitHub Workflows (NEW)
- [x] `quality-gate.yml` — Java + Angular + Python quality gates on PR
- [x] `security-scan.yml` — Gitleaks + OWASP + Trivy + CodeQL
- [x] `release.yml` — Semantic versioning + ECR push + GitHub Release

### Hooks (ENHANCED)
- [x] `post-edit-check.sh` — Added Python (print/bare-except/import*), SQL (SELECT*), YAML (hardcoded credentials) guards

### Process Documentation (NEW)
- [x] `docs/decisions/` — Seed ADRs: ADR-001 (Spring Data JPA), ADR-002 (Flyway)
- [x] `docs/runbooks/runbook-template.md` — Production runbook template
- [x] `ROADMAP.md` — This file
- [x] `CONTRIBUTING.md` — Expanded with full contribution workflow
- [x] `SECURITY.md` — Expanded with threat model template and disclosure process

### Memory Layer (IMPROVED)
- [x] `project-context.md` — First-steps checklist + example entries

### GitHub Copilot Parity (NEW)
- [x] `.github/agents/python-developer.agent.md` — GitHub Copilot agent for Python/FastAPI
- [x] `.github/agents/data-engineer.agent.md` — GitHub Copilot agent for data pipelines
- [x] `.github/agents/kubernetes-engineer.agent.md` — GitHub Copilot agent for K8s/Helm
- [x] `.github/agents/dba-advisor.agent.md` — GitHub Copilot agent for DBA tasks
- [x] `.github/instructions/python.instructions.md` — Python coding standards
- [x] `.github/instructions/fastapi.instructions.md` — FastAPI patterns and rules
- [x] `.github/instructions/data-engineering.instructions.md` — Pipeline standards
- [x] `.github/instructions/graphql.instructions.md` — GraphQL schema and resolver rules
- [x] `.github/instructions/event-driven.instructions.md` — Event-driven messaging patterns
- [x] `.github/instructions/modernization-patterns.instructions.md` — Legacy migration rules

---

## v1.4 — Governed Generation Engine (In Progress)

The platform-transformation track: EEIK stops being copy-once static config and becomes a governed,
versioned, queryable engine. See ADR-003 (generators on HALO) and ADR-004 (pack versioning + lockfile).

### Tier 1 — Structural (Delivered)
- [x] **Governed generation on HALO** — every generator runs through `Harness().invoke(...)`; generation
      is SUGGEST authority, so it can never auto-enforce (gate rule G-5), is audited, and routes drafts
      to human review. Fails safe when HALO is absent. (`eeik/generation.py`)
- [x] **Pack versioning** — every capability pack declares a `version`; three previously un-versioned
      packs (angular, react, belgium-insurance) now carry `metadata.yaml`.
- [x] **Lockfile + drift detection** — `eeik lock` pins adopted pack versions + content digests to
      `eeik.lock`; `eeik diff` reports drift (added/removed/version-changed/content-changed) and gates
      CI with `--exit-code`; `eeik upgrade` re-pins. (`eeik/lock.py`, `eeik/versions.py`)
- [x] **Engine test suite** — `tests/test_engine.py` covers versioning, drift, and the HALO governance
      guarantee (generation never auto-enforces; bypass counter stays 0).
- [x] **Offline showcase** — `eeik demo` runs a generator on the real HALO gate with no API key.

### Tier 1b — Structure & Packaging (Delivered)
- [x] **Installable engine package** — `scripts/` became the importable `eeik/` package with a
      `pyproject.toml` and an `eeik` console entry point (`eeik` / `python -m eeik`). Backward-compatible
      `scripts/*.py` shims remain; CI installs the package and calls `python -m eeik …`. This unblocks the
      Tier 2 SDK/MCP work (consumers import EEIK instead of shelling out).
- [x] **Single canonical manifest schema** — the three divergent schemas (`scripts/schemas/…` and two
      `bootstrap/schemas/…`) are consolidated into one source of truth,
      `eeik/schemas/manifest.schema.json`. This also fixed a latent bug: the validator had been enforcing
      a stale schema that rejected EEIK's own example manifests.

### Tier 2 — Engine surface
- [x] **Pack/agent registry + catalog** — `eeik catalog` builds a machine-readable, queryable index of
      packs, agents, commands, and standards with version + content-digest provenance. Query by `--tag`,
      free-text `--query`, or `--provides <name>` ("which pack provides `java-architect`?"); `--json` is
      the read model the MCP server will expose. All 19 packs are now tagged + categorised.
      (`eeik/catalog.py`)
- [x] **EEIK MCP server** — `eeik mcp` exposes the engine's read model over the Model Context Protocol:
      `eeik_catalog`, `eeik_validate_manifest`, `eeik_resolve_packs`, `eeik_pack_drift`. One live server
      any MCP host calls, replacing drift-prone static adapter files for *queryable* context. Read-only
      in v1 (generation stays governed/staged, ADR-003); testable core + real client↔server round-trip.
      See [ADR-006](docs/decisions/ADR-006-eeik-mcp-server.md). (`eeik/mcp_server.py`, `eeik/mcp_tools.py`)
- [x] **Stable Python API / SDK** — `import eeik` exposes a curated, typed surface (`find_packs`,
      `providers_of`, `validate_manifest`, `resolve_packs`, `pack_drift`, `write_lock`) returning frozen
      dataclasses. The CLI and MCP tools are now thin adapters over it — one source of truth. Consumers
      like apex-sdlc can import EEIK instead of shelling out.
      See [ADR-007](docs/decisions/ADR-007-eeik-public-python-sdk.md). (`eeik/api.py`)
- [x] **apex-sdlc onboarding consumes the engine** — the cross-repo payoff: APEX's onboarding front door
      calls the real engine (manifest validation + pack resolution) via an `EeikEngine` with two backends
      — **SDK** (`import eeik`, in-process) and **MCP** (`eeik mcp`) — falling back to its vendored copy
      when eeik is absent. (apex-sdlc `app/onboarding/eeik_engine.py`, `service.onboard_with_eeik`.)
- [ ] **Governed generation over MCP** — an MCP `generate` tool that returns a staged, human-review draft
      (not an auto-applied artifact), once the review handoff over MCP is designed.

### Tier 3 — Closing the loop
- [x] **`eeik verify`** — the conformance gate: every declared agent/standard resolves to a file, the
      manifest validates, and the lock matches. Findings are fail/warn/pass; `--exit-code` / `--strict`
      gate CI. On all three surfaces (CLI, `eeik.verify()` SDK, `eeik_verify` MCP tool).
      See [ADR-008](docs/decisions/ADR-008-conformance-gate.md). (`eeik/verify.py`)
- [x] **Reconcile pack metadata with shipped files** — the 30 conformance gaps are resolved: phantom
      declarations trimmed, `X-standard`→`X` renames aligned to real files, shipped-but-undeclared files
      declared (e.g. `spring-security-engineer`, `cobol-standard`), and the genuinely-missing
      `insurance-compliance-standard` authored (mirroring banking/healthcare). `eeik verify --strict`
      is now clean (0 fail / 0 warn / 21 pass); the catalog/SDK advertise only agents/standards that exist.
- [x] **Agent-generator emits HALO Agent Contracts** — `eeik contract` / `eeik.agent_contract()`
      deterministically emit an `agent-contract.schema.json`-conformant contract from a blueprint:
      the archetype fixes the authority ceiling, which fixes capabilities + gate threshold (never below
      0.80), tool allowlist (supervisors hold none), and safe failure behaviour. All 8 blueprints validate
      against HALO's own validator. Closes the chain: EEIK generates against HALO's contract schema → HALO runs it.
      See [ADR-009](docs/decisions/ADR-009-agent-generator-emits-halo-contracts.md). (`eeik/contract.py`)
- [ ] **Closed-loop knowledge capture** — HALO/APEX audit logs → lessons → back into EEIK knowledge
      packs, making "every project leaves the org smarter" real.

### Tier 4 — Directory structure (Planned)

Staged directory maturation. Stages 1–2 (engine package + single canonical schema) are **done** above;
the remaining stages are tracked here so the framework's layout keeps pace with its scope.
- [x] **Directory-map ADR + `ARCHITECTURE.md`** — the layer taxonomy (engine / content / adapters /
      docs) is documented with a "where does a new X go?" placement rule.
      See [ADR-005](docs/decisions/ADR-005-layered-directory-taxonomy.md) and
      [ARCHITECTURE.md](ARCHITECTURE.md). *Documented before moving any content, by design.*
- [ ] **Clarify the dual-purpose adapters** — the root `.claude/`/`.github/`/`.kiro/`/`.cursor/` are both
      EEIK's own dogfood config *and* the seed users copy (a documented footgun). Make the copy-target
      explicit without breaking the `cp -r` adoption ergonomics.
- [ ] **Consolidate the resolver overlap** — `generators/capability-selector` vs `bootstrap/resolvers`
      cover overlapping ground; unify now that the taxonomy ADR has landed.

---

## v1.2 — Domain Capability Packs

Expanding domain-specific packs that are currently stubs.

### Planned
- [ ] **Python capability pack** — Promote `python-developer` agent; add FastAPI and data science templates
- [ ] **Data Engineering pack** — Full pipeline templates (Kafka, Spark, dbt), Airflow DAG skeletons
- [ ] **OpenShift pack** — Kubernetes engineer agent, Helm chart templates, SCC patterns
- [ ] **Banking domain pack** — PCI-DSS controls, SWIFT integration patterns, payment flow agents
- [ ] **Healthcare domain pack** — FHIR-aware agent, HIPAA privacy controls, HL7 integration patterns

---

## v1.3 — Reference Architectures

Complete, engine-surfaced reference architectures for common enterprise patterns. Each is a machine-
readable blueprint (`reference.yaml`), a **schema-valid manifest** you can feed to `eeik resolve-packs` /
the repository-generator, an `architecture.md`, and a `runbook.md`. `eeik architectures` lists them and
`eeik verify` checks each one still validates and resolves to the packs it declares (ADR-010).

### Delivered
- [x] **Order Management Microservice** — event-driven Spring Boot 3 / Java 21 / Aurora / Kafka on AWS;
      DDD, transactional outbox, choreographed saga, CQRS. (`knowledge/reference-architectures/order-management/`)
- [x] **AI-Augmented Service** — RAG on FastAPI / Bedrock / pgvector, every model call governed by HALO
      (gate, tool allowlist, audit, human review). (`knowledge/reference-architectures/ai-augmented-service/`)
- [x] **Engine surfacing + conformance** — `eeik architectures` (CLI), `eeik.reference_architectures()`
      (SDK), `eeik_reference_architectures` (MCP); `eeik verify` asserts manifest validity + pack match.

### Planned
- [ ] **Data Platform** — Kafka + Spark + dbt + Airflow + S3/Glue + Athena
- [ ] **Multi-Tenant SaaS** — Shared cluster, tenant isolation, billing integration, Cognito multi-tenancy
- [ ] Per-architecture CDK stacks + seed data / local dev setup (currently: manifest + design + runbook)

---

## v2.0 — Multi-Cloud & Advanced Patterns

### Planned
- [ ] **Azure capability pack** — AKS, Azure DevOps, Entra ID, Cosmos DB patterns
- [ ] **GCP capability pack** — GKE, Cloud Run, BigQuery, Pub/Sub patterns
- [ ] **FinOps agent** — Cloud cost optimisation recommendations, rightsizing, reserved instance analysis
- [ ] **Platform Engineering agent** — Internal developer platform (IDP) design, backstage integration
- [ ] **Chaos Engineering** — Game day exercise templates, fault injection patterns, SLO impact analysis
- [ ] **GraphQL Federation** — Apollo Federation v2 patterns, subgraph design, gateway configuration

---

## Contributing to the Roadmap

To propose a new capability:

1. Open a GitHub issue with the label `enhancement`
2. Describe the use case, target audience, and proposed agents/standards/commands
3. Reference any existing patterns to build on
4. The core team reviews monthly and assigns to a milestone

See `CONTRIBUTING.md` for the full contribution workflow.
