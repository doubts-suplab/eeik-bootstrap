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
      to human review. Fails safe when HALO is absent. (`scripts/generation_harness.py`)
- [x] **Pack versioning** — every capability pack declares a `version`; three previously un-versioned
      packs (angular, react, belgium-insurance) now carry `metadata.yaml`.
- [x] **Lockfile + drift detection** — `eeik lock` pins adopted pack versions + content digests to
      `eeik.lock`; `eeik diff` reports drift (added/removed/version-changed/content-changed) and gates
      CI with `--exit-code`; `eeik upgrade` re-pins. (`scripts/eeik_lock.py`, `scripts/pack_versions.py`)
- [x] **Engine test suite** — `tests/test_engine.py` covers versioning, drift, and the HALO governance
      guarantee (generation never auto-enforces; bypass counter stays 0).
- [x] **Offline showcase** — `eeik demo` runs a generator on the real HALO gate with no API key.

### Tier 2 — Engine surface (Planned)
- [ ] **Stable Python API / SDK** — so APEX onboarding imports EEIK instead of shelling out to scripts.
- [ ] **EEIK MCP server** — expose `validate-manifest`, `resolve-packs`, `generate-agent`,
      `query-catalog` as MCP tools; one live server replaces six drifting static tool-adapter formats.
- [ ] **Pack/agent registry + catalog** — a machine-readable, queryable index of packs, agents, and
      standards with provenance ("which packs support banking + FHIR?").

### Tier 3 — Closing the loop (Planned)
- [ ] **`eeik verify`** — assert a repo actually complies with the packs it adopted (conformance gate,
      not just generation).
- [ ] **Agent-generator emits HALO Agent Contracts** — every generated agent is
      `agent-contract.schema.json`-conformant (authority ceiling, tool allowlist, threshold) by
      construction.
- [ ] **Closed-loop knowledge capture** — HALO/APEX audit logs → lessons → back into EEIK knowledge
      packs, making "every project leaves the org smarter" real.

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

Provide complete, deployable reference architectures for common enterprise patterns.

### Planned
- [ ] **Order Management Microservice** — Full stack: Spring Boot + Angular + Aurora + Kafka + CDK
- [ ] **Data Platform** — Kafka + Spark + dbt + Airflow + S3/Glue + Athena
- [ ] **AI-Augmented Service** — Spring Boot + Bedrock + RAG pipeline + LangGraph orchestration
- [ ] **Multi-Tenant SaaS** — Shared cluster, tenant isolation, billing integration, Cognito multi-tenancy

Each reference architecture includes:
- Architecture diagram (text-based)
- CDK stack with all resources
- ADR explaining key design choices
- Operational runbook
- Seed data and local development setup

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
