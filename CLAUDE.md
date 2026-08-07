# CLAUDE.md — Project Brief for Claude Code Sessions

## What This Repository Is

`eeik_bootstrap` is a **bootstrap and seed repository** — it is not a runnable application. Its purpose is to provide a ready-to-fork configuration base for enterprise projects. Drop the relevant files into any new or existing project to immediately establish:

- GitHub Copilot workspace instructions (`.github/` directory — already in this repo)
- Claude Code agent, command, and standards configuration (`.claude/` directory — this layer)
- Shared quality gates, coding standards, and memory structure

When adopting this seed into a real project, replace all placeholder values (e.g. service names, environment URLs, team names) with project-specific values.

---

## Generation Engine (v1.4) — governed, versioned

EEIK is evolving from copy-once static config into a **governed generation engine** (posture: an
engine other tools consume, *not* a product platform competing with APEX). Two things follow from that:

- **The engine is a package.** The executable core lives in the installable **`eeik/`** package
  (`pip install -e .` → the `eeik` console script, or `python -m eeik`). `scripts/*.py` are thin
  backward-compatible shims. The repo's *content* layers (`capability-packs/`, `knowledge/`,
  `templates/`, `generators/`, `bootstrap/`) are data the engine reads — not code.
- **Three surfaces, one implementation.** The CLI, the MCP server (`eeik mcp`, ADR-006), and the typed
  Python SDK (`import eeik`, ADR-007) are all adapters over `eeik/api.py`. Add behaviour to the SDK
  (`eeik/api.py`) and let the CLI/MCP delegate — do NOT duplicate logic per surface. The public API is
  `eeik.__all__`; the catalog accessor is `eeik.find_packs()` (not `catalog`, to avoid shadowing the
  submodule).
- **One canonical manifest schema.** `eeik/schemas/manifest.schema.json` is the single source of truth
  (`eeik/manifest.py` enforces it). Do NOT reintroduce a second schema copy.
- **Generators run on HALO.** EEIK's generators are agents; they flow through the `agent-harness`
  runtime (`eeik/generation.py`). Generation is **SUGGEST authority**, so it can never auto-enforce —
  drafts are gated, audited, and staged for human review, and it **fails safe** when HALO is absent.
  Do NOT re-implement a confidence gate inside EEIK — consume HALO's.
  See [ADR-003](docs/decisions/ADR-003-eeik-generators-run-on-halo.md).
- **Packs are versioned dependencies.** Every pack declares a `version` in `metadata.yaml`.
  `eeik lock` pins adopted versions + content digests to `eeik.lock`; `eeik diff` reports drift;
  `eeik upgrade` re-pins. See [ADR-004](docs/decisions/ADR-004-capability-pack-versioning-and-lockfile.md).

CLI: `eeik demo` (offline governed showcase), `eeik lock|diff|upgrade`, `eeik catalog` (queryable pack
index), `eeik architectures` (engine-surfaced reference architectures, ADR-010), `eeik verify`
(conformance gate, ADR-008), `eeik contract` (emit a HALO Agent Contract, ADR-009), `eeik mcp`
(read-model MCP server, ADR-006), `eeik run <gen> --governed`, `eeik seed` (copy the seed set into an
adopting project — the explicit dual-purpose boundary, ADR-011), `eeik lessons` (closed-loop knowledge
capture — HALO/APEX audit logs → staged `LL-NNN` lessons, SUGGEST authority, ADR-012), `eeik doctor`
(diagnose adoption/health problems — deps, HALO/MCP, manifest, resolution, drift, conformance — each
with an actionable fix).
Tests: `python3 -m pytest tests/ -q`. Keep `docs/progress.md`, `ROADMAP.md`, `README.md`, and
`docs/index.html` in sync when this layer changes.

---

## How to Use Claude Code Agents

Agents live in `.claude/agents/`. Claude Code automatically selects the most relevant agent based on the `description` field in each agent's frontmatter. You can also invoke agents explicitly by mentioning their name.

**Selection rule:** Read the description of each agent file to understand its trigger condition. The description is written as a precise activation trigger — if your task matches it, that agent will be selected.

**To invoke explicitly:** Reference the agent slug in your prompt:
- "Using the `java-developer` agent, implement the OrderService"
- "Run a `security-auditor` review on this PR diff"
- "Activate `estimator` and give me a P80 estimate for this feature"

**Key agents by domain:**

| Domain | Agents |
|--------|--------|
| Java / Spring Boot | `java-developer`, `java-tech-lead`, `java-tester`, `jacoco-coverage-tester`, `senior-developer` |
| Python | `python-developer` |
| Go | `go-developer`, `go-microservices-engineer` |
| Node / TypeScript | `node-developer`, `typescript-api-engineer` |
| Angular | `angular-developer`, `angular-tester`, `angular-coverage-checker` |
| Architecture | `architect`, `enterprise-architect`, `arb-reviewer` |
| Cloud / Infra | `aws-architect`, `cdk-terraform-helper`, `aws-deploy-helper`, `ci-engineer`, `containerisation-helper`, `kubernetes-engineer`, `devsecops-engineer`, `local-deploy-helper` |
| Data | `data-engineer`, `data-scientist` |
| Database | `dba-advisor` |
| Quality | `code-reviewer`, `security-auditor`, `performance-engineer`, `coverage-enforcer`, `test-quality-enforcer`, `tester` |
| AI / ML | `ai-engineer`, `ml-engineer`, `mlops-engineer`, `ai-governance-officer` |
| Agentic AI | `langraph-engineer`, `crewai-engineer`, `autogen-engineer`, `mcp-engineer`, `a2a-engineer` |
| Delivery | `estimator`, `project-tracker`, `business-analyst`, `technical-writer` |
| Operations | `incident-handler`, `rca-agent`, `ops-engineer`, `sre-engineer` |
| Modernisation | `modernization-expert`, `ibmi-modernization-expert` |

---

## Supported Technology Stack

### Legacy Java
- Spring Framework 4.x / 5.x (Spring MVC, Spring Security, Spring Batch)
- Java 8/11 with `javax.*` APIs
- JUnit 4, Mockito 2/3, Maven

### Modern Java
- Spring Boot 3.x with Java 17/21
- `jakarta.*` exclusively — no `javax.*`
- Spring Data JPA / Spring Data JDBC, Spring Security 6.x
- JUnit 5, AssertJ, Mockito 5, Testcontainers, Pact

### Angular
- Angular 15+ with standalone components
- Signals API, NgRx, RxJS 7+
- Jasmine / Karma / Istanbul for tests
- Strict TypeScript (`"strict": true`)

### Mainframe
- IBM Enterprise COBOL 6.x, CICS, DB2 z/OS
- IBM i (AS400): RPG IV, RPGLE (ILE), CL, DDS, DB2 for i
- JCL, VSAM, QSAM

### Python
- Python 3.11+ with type annotations (`mypy --strict`)
- FastAPI with Pydantic v2, SQLAlchemy async, Alembic
- pytest with `pytest-asyncio`, `pytest-cov`, `testcontainers-python`
- Ruff for formatting and linting

### Go
- Go 1.22+, standard-library-first (`net/http`, `database/sql`, `log/slog`)
- Cloud-native services: gRPC + protobuf (`buf`), context propagation, graceful shutdown
- Table-driven tests, `go test -race`, Testcontainers-go for integration
- `gofmt` + `go vet` + `golangci-lint`; idiomatic errors (`%w`, `errors.Is/As`)

### Node.js / TypeScript
- Node 20+, TypeScript 5.5+ (`"strict": true`, no `any`)
- NestJS / Fastify services; Zod validation at the boundary; typed, validated env config
- Vitest / Jest with coverage; Testcontainers for integration; `pino` structured logging
- ESLint `no-floating-promises`; parameterised queries (Prisma / Drizzle)

### Data Engineering
- Apache Kafka with Schema Registry (Avro / Protobuf)
- Apache Spark (PySpark DataFrame API)
- dbt (staging → intermediate → mart model layers)
- AWS Glue, Step Functions, Airflow

### GraphQL
- Schema-first with `.graphql` SDL files
- Spring for GraphQL (Java) or Strawberry / Ariadne (Python)
- DataLoader for N+1 prevention
- Cursor-based (Relay) pagination

### AWS
- CDK TypeScript (L2/L3 constructs preferred)
- Terraform HCL with remote state (S3 + DynamoDB lock)
- ECS Fargate, EKS, Lambda, API Gateway
- RDS Aurora, ElastiCache, DynamoDB
- SageMaker, Bedrock, Glue, Athena

---

## Golden Rules (Non-Negotiable)

These rules apply across ALL code in ALL domains. They are enforced by hooks and reviewed by the `code-reviewer` and `java-tech-lead` agents.

1. **Constructor injection only** — no `@Autowired` on fields; all injected fields are `final`
2. **No hardcoded secrets** — all credentials, API keys, connection strings go to AWS Secrets Manager or environment variables; never committed to source
3. **SLF4J not System.out** — `log.info(...)` with parameterised messages; never `System.out.println()`
4. **SOLID principles** — Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
5. **Domain-Driven Design** — respect bounded context boundaries; no cross-context direct database joins
6. **No `SELECT *`** — always specify explicit column lists in SQL
7. **Parameterised queries only** — never build SQL via string concatenation; use `NamedParameterJdbcTemplate` or named JPQL parameters
8. **Conventional Commits** — all commit messages follow `type(scope): description` format
9. **No partial implementations** — every method body is complete; no `// TODO implement this` in committed code
10. **`jakarta.*` in Boot 3.x** — never `javax.*` in Spring Boot 3.x code

---

## Before Writing Code

1. **Pick the correct agent** — check `.claude/agents/` descriptions and activate the right specialist
2. **Read the relevant standards file** — check `.claude/standards/` for the technology you are working in
3. **Read project context** — check `.claude/memory/project-context.md` for environment-specific details
4. **State what you are building** — before generating code, declare: the bounded context, the layer (domain/application/infrastructure/web), and the acceptance criteria
5. **Check for existing patterns** — use `Grep` to find similar existing implementations before inventing new abstractions

---

## Estimation Formula

Human Days = **Σ Raw Hours ÷ 6.4**

Where: `6.4 = 8 hours/day × 80% efficiency`

The 80% efficiency factor accounts for: meetings, context-switching, PR review cycles, environment issues, code review iterations, and interruptions.

**Confidence ranges:**

| Scenario | Multiplier | Use For |
|----------|------------|---------|
| P50 (Likely) | ×1.0 | Sprint planning baseline |
| P80 (Conservative) | ×1.3 | Sprint commitment |
| P90 (Pessimistic) | ×1.6 | Release planning buffer |

**Typical raw hours by task type:**

| Task | Simple | Moderate | Complex |
|------|--------|----------|---------|
| REST API endpoint (Spring Boot) | 2–4h | 4–8h | 8–16h |
| Angular standalone component | 2–4h | 4–8h | 8–12h |
| Unit test class | 1–2h | 2–4h | 4–6h |
| Integration test (Testcontainers) | 2–4h | 4–6h | 6–10h |
| CDK stack (new resource) | 2–4h | 4–8h | 8–20h |
| Database migration script | 1–2h | 2–4h | 4–8h |

Invoke the `/estimate` command or activate the `estimator` agent for a full breakdown.

---

## Available Slash Commands

| Command | Description |
|---------|-------------|
| `/bootstrap` | Interactive project discovery — generates `project-manifest.yaml` |
| `/setup-memory` | Interactive interview to populate all `.claude/memory/` files with project context |
| `/validate-manifest` | Validate `project-manifest.yaml` against the schema and governance rules |
| `/generate-repo` | Generate full repository scaffold from validated manifest |
| `/generate-agent --blueprint <type> --name <name>` | Generate a project-specific agent from a blueprint |
| `/adr "decision title"` | Scaffold a new Architecture Decision Record in `docs/decisions/` |
| `/rca "symptoms"` | Open an RCA workflow with 5-Whys template |
| `/estimate "feature description"` | Produce a bottom-up P50/P80/P90 effort estimate |
| `/review` | Run full PR review checklist across security, performance, and quality |
| `/threat-model "service description"` | STRIDE threat model for a service or bounded context |
| `/incident "severity: P1\|P2, service: name, symptom: description"` | Declare and coordinate an incident |
| `/security-scan [file or directory]` | OWASP Top 10 review plus secrets scan |
| `/deploy-check "env: dev\|staging\|prod, service: name"` | Pre-deployment readiness checklist |
| `/migrate-db "description"` | Generate Flyway/Liquibase migration with rollback and risk assessment |
| `/api-contract "resource description"` | Contract-first API design — OpenAPI stub + Pact consumer test |
| `/tech-debt add "description"` | Register a new tech debt item to `.claude/memory/tech-debt.md` |
| `/memory-update "what changed"` | Update relevant `.claude/memory/` files with new context |
| `/coverage-report [module path]` | JaCoCo/Istanbul coverage analysis with targeted test stubs |
| `/sync-docs` | Sync API documentation against OpenAPI specs |

---

## Memory and Context

Claude Code reads `.claude/memory/` files at the start of sessions to load persistent context. Use these files to avoid re-explaining the project on every session.

| File | Purpose |
|------|---------|
| `project-context.md` | Service inventory, environments, auth patterns, key resource names |
| `domain-glossary.md` | Business terminology — what terms mean in this project's domain |
| `decisions.md` | Architecture Decision Log — what was decided and why |
| `constraints.md` | Hard technical and business constraints that must never be violated |
| `patterns.md` | Approved implementation patterns and anti-patterns to avoid |
| `tech-debt.md` | Tech debt register with priority and target sprint |
| `rca-tracker.md` | Incident/RCA status log |
| `session-log.md` | Auto-updated by the `on-stop.sh` hook with each session's changed files |
| `rejected-approaches.md` | Things that were tried and rejected — prevents re-trying failed ideas |

Use `/memory-update` to update these files when significant decisions or changes occur.

---

## What NOT To Do

- Do NOT use `javax.*` in Spring Boot 3.x code — use `jakarta.*`
- Do NOT use `@Autowired` on fields — constructor injection only
- Do NOT write `SELECT *` in any SQL query
- Do NOT hardcode credentials, API keys, passwords, or AWS account IDs in source code
- Do NOT use `Thread.sleep()` in tests — use `Awaitility.await().until()`
- Do NOT write empty catch blocks — at minimum log the exception at WARN or ERROR level
- Do NOT use `new Date()` or `java.util.Calendar` — use `java.time` (LocalDate, LocalDateTime, Instant, ZonedDateTime)
- Do NOT add new Maven/npm dependencies without checking the BOM and flagging version conflicts
- Do NOT write partial implementations — if a method is not complete, say so explicitly
- Do NOT commit directly to `main` or `master` — always use a feature branch and PR
- Do NOT use `System.out.println()` anywhere in production code — use SLF4J
- Do NOT use `Optional.get()` without a preceding `isPresent()` check or `orElseThrow()`
