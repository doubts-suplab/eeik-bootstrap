# CLAUDE.md — Project Brief for Claude Code Sessions

## What This Repository Is

`eeik_bootstrap` is a **bootstrap and seed repository** — it is not a runnable application. Its purpose is to provide a ready-to-fork configuration base for enterprise projects. Drop the relevant files into any new or existing project to immediately establish:

- GitHub Copilot workspace instructions (`.github/` directory — already in this repo)
- Claude Code agent, command, and standards configuration (`.claude/` directory — this layer)
- Shared quality gates, coding standards, and memory structure

When adopting this seed into a real project, replace all placeholder values (e.g. service names, environment URLs, team names) with project-specific values.

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
| Angular | `angular-developer`, `angular-tester`, `angular-coverage-checker` |
| Architecture | `architect`, `enterprise-architect`, `arb-reviewer` |
| Cloud / Infra | `aws-architect`, `cdk-terraform-helper`, `aws-deploy-helper`, `ci-engineer`, `containerisation-helper`, `devsecops-engineer`, `local-deploy-helper` |
| Quality | `code-reviewer`, `security-auditor`, `performance-engineer`, `coverage-enforcer`, `test-quality-enforcer`, `tester` |
| AI / ML | `ai-engineer`, `ml-engineer`, `data-scientist`, `mlops-engineer`, `ai-governance-officer` |
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
| `/adr "decision title"` | Scaffold a new Architecture Decision Record in `docs/decisions/` |
| `/rca "symptoms"` | Open an RCA workflow with 5-Whys template |
| `/estimate "feature description"` | Produce a bottom-up P50/P80/P90 effort estimate |
| `/review` | Run full PR review checklist across security, performance, and quality |
| `/incident "severity: P1\|P2, service: name, symptom: description"` | Declare and coordinate an incident |
| `/security-scan [file or directory]` | OWASP Top 10 review plus secrets scan |
| `/deploy-check "env: dev\|staging\|prod, service: name"` | Pre-deployment readiness checklist |
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
