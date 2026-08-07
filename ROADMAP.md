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
      the read model the MCP server will expose. All 22 packs are now tagged + categorised.
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
- [x] **Governed generation over MCP** — `eeik_generate` MCP tool + `eeik.generate()` SDK function run a
      generation through HALO and return a **staged, human-review draft** — never an auto-applied artifact.
      Generation is SUGGEST authority, so the shared core (`eeik/generation.py::run_generation`) guarantees
      `auto_enforced=false`, routes the draft to human review, keeps `confidence_gate_bypass_total=0`, and
      writes to a staging area; the MCP payload flags `autoApplied=false` explicitly. One implementation,
      three surfaces (CLI `demo`/`run`, SDK, MCP). Fails safe when HALO is absent. (`eeik/generation.py`,
      `eeik/mcp_tools.py`, ADR-003/006.)

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
- [x] **Closed-loop knowledge capture** — done (ADR-012). `eeik lessons --from audit.json` /
      `eeik.capture_lessons()` / `eeik_capture_lessons` (MCP) ingest HALO/APEX audit records, select the
      learnable ones (blocks, alerts, sub-0.80-confidence human-review outcomes), group them by theme, and
      draft `LL-NNN` lessons — **governed as SUGGEST authority**: staged under `.eeik-staging/lessons/`,
      `auto_enforced=false`, never auto-committed. A human curates Root Cause / Fix and promotes. Closes
      the loop `HALO/APEX audit → staged lesson → knowledge base`. (`eeik/lessons.py`)

### Tier 4 — Directory structure (Planned)

Staged directory maturation. Stages 1–2 (engine package + single canonical schema) are **done** above;
the remaining stages are tracked here so the framework's layout keeps pace with its scope.
- [x] **Directory-map ADR + `ARCHITECTURE.md`** — the layer taxonomy (engine / content / adapters /
      docs) is documented with a "where does a new X go?" placement rule.
      See [ADR-005](docs/decisions/ADR-005-layered-directory-taxonomy.md) and
      [ARCHITECTURE.md](ARCHITECTURE.md). *Documented before moving any content, by design.*
- [x] **Clarify the dual-purpose adapters** — done (ADR-011). `bootstrap/seed-manifest.yaml` classifies
      every root entry as `seed` (copy) / `generated` (regenerate via the engine) / `engine` (never copy).
      `eeik seed --into <dir> [--apply]` copies exactly the `seed` set (also `eeik seed --list`,
      `eeik.seed_plan()`), additive to `cp -r`. The seed's own `quality-gate.yml` product jobs self-skip
      on the engine repo (no `pom.xml`/`package.json`/`src/`). A test asserts no engine-only path is ever
      classified `seed`.
- [x] **Consolidate the resolver overlap** — unified on a single canonical matrix at
      `bootstrap/resolvers/capability-matrix.yaml` (all 19 packs, availability-annotated). The duplicate
      stub under `generators/capability-selector/` was removed; its README now redirects to the canonical
      file and states plainly that the *authoritative* resolver is code (`eeik/packs.py::resolve_packs`) —
      the matrix is human-readable reference. `eeik/packs.py::MATRIX_FILE` repointed accordingly; APEX's
      vendored copy + `PROVENANCE.md` re-synced (availability corrected: all 19 built, azure/gcp/retail
      remain v2.0).

---

## v1.2 — Domain Capability Packs (Complete)

Domain-specific packs, now substantive (agents + standards + knowledge) and conformance-checked by
`eeik verify` — the catalog advertises only agents that exist.

### Delivered
- [x] **Python capability pack** — `python-developer`, `fastapi-engineer`; python + fastapi standards.
- [x] **Go capability pack** — `go-developer`, `go-microservices-engineer`; go-standard (cloud-native,
      std-lib-first, gRPC/protobuf, `context`, table-driven `-race` tests). `technology.backend.language:
      go` resolves it (schema enum + resolver + matrix extended).
- [x] **Node.js / TypeScript capability pack** — `node-developer`, `typescript-api-engineer`;
      node-standard (strict TS, Zod boundaries, NestJS/Fastify, Vitest, `pino`). Resolves on
      `technology.backend.language: node`.
- [x] **Retail domain pack** — `retail-domain-expert`, `ecommerce-specialist`; retail-standard (catalog /
      cart-checkout / inventory-reservation / order state machine / PCI-DSS tokenised payments / GDPR).
      Resolves on `project.domain: retail` (previously annotated planned-for-v2.0; pulled forward). 22 packs total.
- [x] **Data Engineering pack** — `data-engineer`; data-engineering + data-pipeline standards; lakehouse
      knowledge. (Now auto-resolves from `technology.data.*` — schema + resolver extended.)
- [x] **OpenShift pack** — `openshift-engineer`, `kubernetes-engineer`; openshift standard.
- [x] **Banking domain pack** — `banking-domain-expert`, `payments-specialist` (SWIFT/ISO 20022, SEPA,
      SCA, PCI-DSS); banking-compliance standard. (v1.1)
- [x] **Healthcare domain pack** — `healthcare-domain-expert`, `clinical-data-specialist` (FHIR R4, HL7 v2,
      SNOMED/LOINC, HIPAA); healthcare-compliance standard. (v1.1)

---

## v1.3 — Reference Architectures

Complete, engine-surfaced reference architectures for common enterprise patterns. Each is a machine-
readable blueprint (`reference.yaml`), a **schema-valid manifest** you can feed to `eeik resolve-packs` /
the repository-generator, an `architecture.md`, and a `runbook.md`. `eeik architectures` lists them and
`eeik verify` checks each one still validates and resolves to the packs it declares (ADR-010).

### Delivered
- [x] **Order Management Microservice** — event-driven Spring Boot 3 / Java 21 / Aurora / Kafka on AWS;
      DDD, transactional outbox, choreographed saga, CQRS.
- [x] **AI-Augmented Service** — RAG on FastAPI / Bedrock / pgvector, every model call governed by HALO.
- [x] **Data Platform** — Kafka + Spark/Glue + dbt + Airflow + S3 lakehouse + Athena; medallion, idempotent
      ingestion, data-quality gates.
- [x] **Multi-Tenant SaaS** — shared infra + isolated tenants; Cognito identity, PostgreSQL RLS isolation,
      per-tenant metering/billing, noisy-neighbour controls.
- [x] **Engine surfacing + conformance** — `eeik architectures` (CLI), `eeik.reference_architectures()`
      (SDK), `eeik_reference_architectures` (MCP); `eeik verify` asserts manifest validity + pack match.

### Delivered (cont.)
- [x] **Per-architecture CDK stacks + seed data / local dev** — each of the 4 reference architectures now
      ships a deployable `cdk/` (TypeScript AWS CDK app — VPC/Aurora/MSK/ECS, pgvector, medallion
      lakehouse+Glue+Athena, Cognito+RLS as appropriate) and a `local-dev/` (`docker compose up -d` +
      seed data — Postgres/Kafka/MinIO/pgvector, with schema + demo rows). `reference.yaml` gained a
      `deployment` block; `eeik architectures` surfaces it and `eeik verify` asserts each `cdk/` has a
      `cdk.json` and each `local-dev/` a `docker-compose.yml`.

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
