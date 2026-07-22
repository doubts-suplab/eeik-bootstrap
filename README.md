# Enterprise Engineering Intelligence Kit (EEIK) Bootstrap

## AI-Native Enterprise Engineering Bootstrap Platform

A ready-to-fork seed repository that gives **6 AI coding tools** — Claude Code, GitHub Copilot, Kiro, Codex CLI, Cursor, and Gemini CLI — the enterprise context they need to act as specialist engineers from day one.

EEIK transforms AI coding assistants from generic code generators into context-aware engineering partners that understand:

- Technology stacks
- Enterprise standards
- Architecture governance
- Modernization programs
- Delivery processes
- Cloud platforms
- AI engineering patterns
- Organizational knowledge

Drop the configuration layers from this repository into any project and all 6 AI tools become engineering assistants that understand your ecosystem from day one.

EEIK is not a runnable application.

It is an AI-native engineering operating system.

---

## Vision

Most organizations repeatedly rebuild the same engineering knowledge:

Coding standards
Architecture patterns
Governance processes
Migration approaches
Estimation models
Review checklists
Delivery workflows

EEIK captures this knowledge once and makes it reusable across every project.

The long-term goal is:

``` text
Project Requirements
            ↓
      EEIK Bootstrap
            ↓
 Capability Resolution
            ↓
 Repository Generation
            ↓
 Agent Generation
            ↓
 Governed Delivery
            ↓
 Knowledge Capture
            ↓
 Organizational Learning
```
Every project should leave the organization smarter than it was before the project started.

---

## What EEIK Provides
EEIK combines:

### AI Configuration Layer
For all 6 AI tools:
- **Claude Code** — `.claude/` (44 agents, 19 commands, hooks, memory)
- **GitHub Copilot** — `.github/` (44 agents, instructions, prompts, workflows)
- **Kiro** — `.kiro/steering/` (always-on steering docs)
- **Codex CLI** — `AGENTS.md` + 5 subdirectory `AGENTS.md` templates
- **Cursor** — `.cursor/rules/` (glob-matched `.mdc` rules)
- **Gemini CLI** — `GEMINI.md` (persistent project context)

### Capability Layer
Reusable engineering intelligence:
- Architecture
- Java
- Angular
- AWS
- AI Engineering
- Modernization
- Governance
- Operations
- Delivery

### Knowledge Layer
Reusable:
- Reference architectures
- ADRs
- Patterns
- Lessons learned
- Incident learnings
- Migration strategies

### Governance Layer
Built-in:
- Architecture reviews
- Security reviews
- AI reviews
- Production readiness reviews

### Generation Layer
Future platform capabilities:
- Repository Generator
- Agent Factory
- Capability Resolver
- Knowledge Platform

---

## Repository Structure

```
── AI Tool Adapters (root — read by each tool automatically) ─────────────────
CLAUDE.md          ⚠️  This is EEIK's own brief — DO NOT copy to target projects
                       Use templates/PROJECT-CLAUDE.md instead
AGENTS.md          Codex CLI root context
GEMINI.md          Gemini CLI persistent context
CONTRIBUTING.md    Contribution guide
SECURITY.md        Vulnerability reporting

── Tool-Specific Config ──────────────────────────────────────────────────────
.claude/           Claude Code  — 44 agents, 19 commands, hooks, memory, standards
.github/           Copilot      — 44 agents, instructions, prompts, workflows, hooks
.kiro/             Kiro         — steering docs (product, tech, structure), hooks
.cursor/           Cursor       — .mdc rules (golden-rules, architecture, security)

── Intelligence Layer (tool-agnostic) ────────────────────────────────────────
capability-packs/  19 packs — core, architecture, java, aws, ai-engineering,
                   agent-harness, governance, angular, react, data-engineering,
                   python, openshift, containers, delivery, modernization,
                   insurance, banking, belgium-insurance, healthcare
templates/         PROJECT-CLAUDE.md  ← use this as CLAUDE.md in target projects
                   Code templates per technology domain

── Generators ────────────────────────────────────────────────────────────────
generators/        adapter-generator  — Kiro/Codex/Cursor/Gemini adapter templates
                     codex-subdirs/   — 5 subdirectory AGENTS.md templates
                   repository-generator, agent-generator, capability-selector,
                   knowledge-generator, governance-generator, model-router,
                   project-analyzer
bootstrap/         /bootstrap command: manifests, schemas, validators, resolvers

── Executable Scripts ────────────────────────────────────────────────────────
scripts/           eeik_cli.py          — central CLI entry point
                   validate_manifest.py — JSON Schema + 8 governance rules (no AI needed)
                   activate_packs.py    — manifest → .claude/ materialisation
                   generate_adapters.py — generate all 6 AI tool adapters
                   claude_harness.py    — run generators via claude --print (CI)

── CI/CD ─────────────────────────────────────────────────────────────────────
.github/workflows/ eeik-validate.yml   — manifest + agent lint on PR
                   eeik-adapt.yml      — auto-regenerate adapters on manifest change

── Documentation ─────────────────────────────────────────────────────────────
docs/
├── eeik-guide.html    Interactive visual guide — open in browser for full overview
├── specs/             Internal design specs
├── concepts/          Vision, architecture, AI governance
├── reference/         Roadmap, inventory, platform capabilities
└── getting-started/   Adoption guide, use cases
```

---

## EEIK Architecture
```
                    ┌──────────────────┐
                    │    Bootstrap     │
                    └─────────┬────────┘
                              │
                              ▼
                 ┌────────────────────────┐
                 │ Capability Resolution  │
                 └─────────┬──────────────┘
                           │
                           ▼
             ┌───────────────────────────────┐
             │ Selected Capability Packs     │
             └─────────┬─────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼

   Repository      Agent         Governance
   Generator       Factory       Engine

        ▼              ▼              ▼

   Generated      Generated      Reviews
 Repository        Agents

                       ▼

              Knowledge Platform
```

---

## Supported Technology Domains

| Domain | Stack |
|--------|-------|
| **Legacy Java** | Spring 4.x/5.x, Spring MVC, JdbcTemplate, JUnit 4, Maven |
| **Modern Java** | Spring Boot 3.x, Java 17/21, `jakarta.*`, Spring Data JPA, Spring Security 6.x, OpenAPI 3 |
| **Angular** | Angular 17+, Standalone Components, Signals API, NgRx, RxJS 7+, strict TypeScript |
| **Mainframe** | IBM COBOL 6.x, HLASM, JCL, CICS, DB2 z/OS |
| **IBM i** | RPG IV, RPGLE (ILE), CL, DDS, DB2 for i |
| **AWS** | CDK TypeScript, Terraform HCL, ECS Fargate, EKS, Lambda, RDS Aurora, SageMaker, Bedrock |
| **Data / ML / AI** | SageMaker Pipelines, Bedrock, LangChain, LangGraph, RAG, MLOps |
| **Agentic AI** | LangGraph, CrewAI, AutoGen, MCP, Agent-to-Agent (A2A) protocols |
| **Platform** | Docker, Kubernetes, GitHub Actions, CloudWatch, X-Ray |

---

## EEIK Capability Packs
EEIK separates reusable engineering intelligence into capability packs.

Examples:
```
capability-packs/       (19 packs)
├── core/               foundational agents, golden rules, security/observability baselines
├── architecture/       enterprise-architect, arb-reviewer, reference architectures
├── java/               java-architect, spring-security-engineer, testcontainers patterns
├── aws/                cdk-engineer, bedrock-rag-patterns, eventbridge-patterns
├── ai-engineering/     ai-architect, rag-specialist, llm-evaluation-patterns, vector-db-selection
├── agent-harness/      agent-harness-protocol conformance → runtime doubts-suplab/agent-harness
├── governance/         compliance-reviewer, production-readiness-reviewer, GDPR/SOC2/PCI
├── angular/            angular-developer, signals migration guide
├── react/              react-developer (Next.js 14, Server Components, TanStack Query)
├── data-engineering/   data-engineer, lakehouse-patterns (Spark/Glue/Kafka/dbt)
├── python/             fastapi-engineer, python-developer
├── openshift/          openshift-engineer, SCC patterns
├── containers/         dockerfile-standard
├── delivery/           branching-standard, Conventional Commits
├── modernization/      ibmi-modernization-expert, cobol-standard, strangler-fig
├── insurance/          claims-processing-patterns, insurance-domain-glossary
├── banking/            swift-iso20022-patterns, banking-compliance-standard
├── belgium-insurance/  belgium-insurance-expert, Branch 21/23/26, FSMA/NBB, TOB
└── healthcare/         hl7-fhir-patterns, healthcare-compliance-standard
```

Each pack may contain:
- Standards
- Templates
- Prompts
- Workflows
- Knowledge assets
- Review criteria


## How to Adopt This Bootstrap

### 1. Create your project and copy the config layers

```bash
mkdir my-new-service && cd my-new-service
git init

EEIK=/path/to/eeik_bootstrap   # set this to where you cloned EEIK

cp -r $EEIK/.claude      ./.claude
cp -r $EEIK/.github      ./.github
cp -r $EEIK/.kiro        ./.kiro
cp -r $EEIK/.cursor      ./.cursor
cp    $EEIK/AGENTS.md    ./AGENTS.md
cp    $EEIK/GEMINI.md    ./GEMINI.md

# ⚠️  IMPORTANT: use templates/PROJECT-CLAUDE.md — NOT CLAUDE.md from the EEIK root.
# EEIK's CLAUDE.md describes the EEIK repo itself (bootstrap/, generators/, capability-packs/).
# Claude Code reads it and thinks it's inside EEIK, causing artifacts to be created there.
cp    $EEIK/templates/PROJECT-CLAUDE.md ./CLAUDE.md
```

### 2. Validate and generate adapters

```bash
# Validate your manifest (optional — create project-manifest.yaml from bootstrap/manifests/manifest-template.yaml first)
python3 $EEIK/scripts/validate_manifest.py project-manifest.yaml

# Regenerate all 6 AI tool adapters from your manifest
python3 $EEIK/scripts/generate_adapters.py --apply

# Materialise capability pack agents + standards into .claude/
python3 $EEIK/scripts/activate_packs.py --apply
```

### 3. Fill in project context

Edit `.claude/memory/project-context.md` — this is what every agent reads at session start:

- Service name and purpose
- Environment URLs and AWS account IDs
- Auth patterns (Cognito, IAM roles)
- Database engine and schema name

### 4. Adjust GitHub Copilot glob patterns

Each file in `.github/instructions/` has an `applyTo` frontmatter. Update to match your source layout:

```markdown
---
applyTo: "src/main/java/com/yourcompany/**/*.java"
---
```

### 5. Remove unused domains

Delete agents and instructions for domains not in your stack — lean context = sharper agents.

### 6. Open Claude Code in your new project (not in EEIK)

```bash
cd my-new-service   # ← must be here, not in EEIK
claude

# Smoke-test:
/estimate "implement POST /orders endpoint with idempotency key"
```

---

## Agent Catalogue (44 agents per layer)

Full catalogue with descriptions: **`AGENTS.md`** at the repository root.

### GitHub Copilot Agents — select via `@` in Copilot Chat

| Domain | Agents |
|--------|--------|
| Java | `java-dev`, `java-tech-lead`, `java-tester`, `jacoco-coverage-tester`, `developer` |
| Angular | `angular-dev`, `angular-tester`, `angular-coverage-checker` |
| Architecture | `architect`, `enterprise-architect`, `aws-architect`, `arb-reviewer` |
| Cloud / Infra | `cdk-terraform-helper`, `aws-deploy-helper`, `local-deploy-helper`, `containerisation-helper`, `ci-engineer`, `devsecops-engineer` |
| Quality | `reviewer`, `security-auditor`, `performance-reviewer`, `coverage-enforcer`, `test-quality-enforcer`, `tester` |
| Data / ML / AI | `data-scientist-aws`, `ml-engineer-aws`, `ai-engineer-aws`, `mlops-engineer`, `ai-governance-officer` |
| Agentic AI | `langraph-engineer`, `crewai-engineer`, `autogen-engineer`, `mcp-engineer`, `a2a-engineer` |
| Modernisation | `modernization-expert`, `ibmi-modernization-expert` |
| Delivery / Ops | `estimator`, `project-tracker`, `ops-engineer`, `sre-engineer`, `incident-handler`, `rca-agent` |
| Docs | `analyst`, `technical-writer` |

### Claude Code Agents — auto-selected by task context

Same 44 domains; invoke explicitly: *"Using the `java-developer` agent, implement the OrderService"*

---

## Instruction Files (29 — Auto-Applied by File Type)

| File | Applies To |
|------|-----------|
| `spring-boot.instructions.md` | `**/src/main/java/**/*.java` |
| `java-legacy.instructions.md` | Legacy Spring 4/5 Java files |
| `java-quality.instructions.md` | Java code quality and test coverage |
| `angular.instructions.md` | `**/*.ts`, `**/*.html`, `**/*.scss` |
| `mainframe.instructions.md` | `**/*.cbl`, `**/*.asm`, `**/*.jcl` |
| `mainframe-extended.instructions.md` | Extended COBOL/JCL patterns |
| `ibmi.instructions.md` | `**/*.rpgle`, `**/*.clle`, `**/*.dds` |
| `sql.instructions.md` | `**/*.sql`, MyBatis mapper XML |
| `test.instructions.md` | `**/*Test.java`, `**/*.spec.ts` |
| `aws-architecture.instructions.md` | `**/*.tf`, `**/cdk/**/*.ts` |
| `aws-data-ml-ai.instructions.md` | `**/*.ipynb`, `**/sagemaker/**` |
| `cdk-terraform.instructions.md` | CDK stacks and Terraform modules |
| `containerisation.instructions.md` | Dockerfiles, docker-compose, K8s manifests |
| `cicd.instructions.md` | `.github/workflows/**`, Jenkinsfile |
| `deployment.instructions.md` | Deployment scripts |
| `enterprise-architecture.instructions.md` | `**/architecture/**`, `**/adr/**` |
| `architecture-governance.instructions.md` | ARB reviews and standards compliance |
| `devsecops.instructions.md` | Security pipeline configuration |
| `incident-ops.instructions.md` | `**/runbooks/**`, `**/incidents/**` |
| `project-estimation.instructions.md` | `**/estimates/**`, `**/*.estimate.md` |
| `ai-governance.instructions.md` | AI system governance artefacts |
| `langgraph.instructions.md` | LangGraph agent graph code |
| `crewai.instructions.md` | CrewAI multi-agent code |
| `autogen.instructions.md` | Microsoft AutoGen code |
| `mcp-protocol.instructions.md` | MCP server/client code |
| `a2a-protocol.instructions.md` | Agent-to-Agent communication code |
| `mlops-pipeline.instructions.md` | MLOps pipeline code |
| `sre.instructions.md` | SLO definitions and runbooks |
| `memory-architecture.instructions.md` | `.claude/memory/**` files |

---

## Skills (12 — Auto-Loaded by GitHub Copilot)

| Skill | Triggers When |
|-------|--------------|
| `estimation` | Estimating effort, sizing stories, planning delivery |
| `jacoco-analysis` | JaCoCo reports, coverage thresholds, missed branches |
| `aws-cdk-deploy` | CDK deploy, diff, or rollback |
| `incident-response` | Declaring or managing a P1/P2 incident |
| `code-quality-scan` | SonarQube, SpotBugs, OWASP findings |
| `ai-governance` | AI system governance reviews and model cards |
| `architecture-governance` | ARB gate reviews and standards compliance |
| `devsecops` | Security pipeline configuration and gate setup |
| `langgraph-patterns` | LangGraph graph design and state machines |
| `mcp-server-design` | MCP server and tool schema design |
| `mlops-pipeline` | MLOps pipelines, model registry, drift monitoring |
| `sre-practices` | SLI/SLO definition and error budget management |

---

## Orchestrated Workflows (14)

Reference in Copilot Chat with `#file:.github/prompts/workflows/<name>.prompt.md`:

| Workflow | Description |
|---------|-------------|
| `full-feature-dev` | Analyst → Architect → Developer → Tester → Coverage → Reviewer |
| `pr-review-workflow` | Code → Security → Performance → Test Quality |
| `tdd-cycle` | Red → Green → Refactor → Coverage |
| `cobol-to-java-workflow` | COBOL modernisation pipeline |
| `aws-infra-deploy` | Architect → CDK → CI/CD → Deploy → Ops |
| `incident-rca-workflow` | Detection → Triage → War Room → Resolution → RCA |
| `arb-review-workflow` | Formal ARB gate review |
| `ai-governance-review` | AI system classification → Model Card → Risk Assessment → Sign-Off |
| `multi-agent-system-design` | Problem Decomposition → Topology → State → Implement |
| `mcp-server-development` | Capability Design → Security → Schema → Implement |
| `ibmi-to-cloud-workflow` | IBM i Discovery → Architecture → Phased Migration → Cutover |
| `devsecops-pipeline-review` | Audit → Gap Analysis → Remediate → Validate |
| `game-day-exercise` | Hypothesis → Baseline → Inject → Observe → Report |
| `ml-model-delivery` | Experiment → Governance → MLOps → Deploy → Monitor |

---

## Task Prompts (22)

Reference with `#file:.github/prompts/tasks/<name>.prompt.md`:

| Prompt | Action |
|--------|--------|
| `generate-unit-tests` | JUnit 5 / Jasmine test class |
| `generate-integration-tests` | Spring Boot + Testcontainers |
| `generate-rest-api` | Controller + service + DTO + OpenAPI |
| `generate-angular-component` | Standalone component + spec |
| `generate-angular-service` | HttpClient service + spec |
| `generate-mapstruct-mapper` | MapStruct interface |
| `generate-openapi-spec` | OpenAPI 3.0 YAML spec |
| `add-javadoc` | Complete Javadoc on all public members |
| `add-logging` | SLF4J at correct levels throughout |
| `code-review` | Structured single-class review |
| `explain-code` | Plain-English explanation |
| `explain-mainframe-program` | COBOL/JCL/Assembler walkthrough |
| `explain-rpg-program` | IBM i RPG IV / RPGLE analysis |
| `refactor-to-clean-code` | SOLID / clean code refactor |
| `modernize-cobol-to-java` | COBOL → Java with risk matrix |
| `modernize-rpg-to-java` | RPG → Java migration |
| `write-adr` | Architecture Decision Record scaffold |
| `write-rfc` | Request for Comments document |
| `write-model-card` | AI/ML model card |
| `ai-risk-assessment` | EU AI Act + GDPR risk assessment |
| `define-sli-slo` | SLI/SLO definition with error budget |
| `update-project-memory` | Update `.claude/memory/` files |

---

## Claude Code Slash Commands (19) — Claude Code only

> Slash commands live in `.claude/commands/` and work **only in Claude Code**. Kiro, Codex CLI, Cursor, and Gemini CLI use steering docs and rules files instead.

| Command | Description |
|---------|-------------|
| `/bootstrap` | Interactive project discovery → generates `project-manifest.yaml` |
| `/validate-manifest` | Validate manifest against JSON Schema + 8 governance rules |
| `/generate-repo` | Full repository scaffold from manifest (9-step) |
| `/generate-agent --blueprint <type>` | Generate project-specific agent from 8 blueprints |
| `/analyze-project` | Scan existing repo → infer stack → suggest packs |
| `/estimate "feature"` | P50/P80/P90 effort estimate using 6.4h/day formula |
| `/review` | Full PR review: correctness, security, performance, quality |
| `/adr "decision title"` | Scaffold Architecture Decision Record |
| `/create-adr "title"` | Full ADR with context, decision, consequences, alternatives |
| `/create-rfc "title"` | RFC for significant decisions requiring team review |
| `/rca "symptoms"` | Blameless 5-Whys root cause analysis |
| `/incident "P1, service: X"` | Declare and coordinate an incident |
| `/capture-incident "title"` | Capture incident learnings into memory |
| `/capture-lesson "lesson"` | Capture pattern or lesson into memory |
| `/security-scan [path]` | OWASP Top 10 review + secrets scan |
| `/deploy-check "env: X"` | Pre-deployment readiness checklist (24-point) |
| `/coverage-report [path]` | JaCoCo/Istanbul gap analysis + targeted test stubs |
| `/memory-update "what changed"` | Update `.claude/memory/` persistent context |
| `/sync-docs [path]` | Validate API docs against OpenAPI spec |

---

## Claude Code Memory Files

`.claude/memory/` files are read at session start — no re-explaining the project on every session:

| File | Purpose |
|------|---------|
| `project-context.md` | **Fill this in** — service inventory, environments, auth patterns |
| `domain-glossary.md` | Business term definitions for this domain |
| `decisions.md` | Lightweight architecture decision log |
| `constraints.md` | Hard constraints that must never be violated |
| `patterns.md` | Approved patterns and forbidden anti-patterns |
| `tech-debt.md` | Prioritised tech debt register |
| `rca-tracker.md` | Incident/RCA status and corrective action tracking |
| `session-log.md` | Auto-updated by `on-stop.sh` hook |
| `rejected-approaches.md` | Tried-and-rejected solutions |

---

## Coding Standards

`.claude/standards/` provides the mandatory rules agents read before writing code:

| File | Covers |
|------|--------|
| `java.md` | Spring Boot 3.x, constructor injection, SLF4J, jakarta.*, JUnit 5 |
| `angular.md` | Standalone components, signals, OnPush, reactive forms |
| `aws.md` | IAM least privilege, encryption, CDK patterns, tagging |
| `sql.md` | No SELECT *, parameterised queries, Flyway conventions |
| `testing.md` | JUnit 5/AssertJ/Mockito, Jasmine/Karma, AAA pattern, thresholds |
| `cicd.md` | Pipeline stages, quality gates, OIDC auth, artefact promotion |
| `containers.md` | Multi-stage Dockerfiles, non-root users, JVM flags, K8s probes |
| `mainframe.md` | COBOL, RPG, CL, JCL standards and migration guidance |

---

## Estimator Formula

All estimates use:

> **Human Days = Σ Raw Hours ÷ 6.4**
> `6.4 = 8 hours/day × 80% efficiency`

| Scenario | Multiplier | Use For |
|----------|------------|---------|
| P50 | ×1.0 | Sprint planning baseline |
| P80 | ×1.3 | Sprint commitment |
| P90 | ×1.6 | Release planning buffer |

---

## Hooks

### GitHub Copilot (`/.github/hooks/`)
| Hook | Events | Output |
|------|--------|--------|
| `session-hooks.json` | sessionStart, sessionEnd, userPromptSubmitted | `.copilot-session.log` |
| `tool-use-hooks.json` | preToolUse, postToolUse, errorOccurred | `.copilot-tool.log` |

### Claude Code (`/.claude/hooks/`)
| Hook | Trigger | Action |
|------|---------|--------|
| `pre-bash-guard.sh` | Before every Bash command | Blocks: force-push, `rm -rf /`, `DROP DATABASE`, `cdk destroy`, AWS terminations |
| `pre-write-guard.sh` | Before every file write | Validates target path safety |
| `post-edit-check.sh` | After every file edit | Post-write validation |
| `on-stop.sh` | Session end | Auto-updates `.claude/memory/session-log.md` |

---

## Adoption Checklist

Before using this bootstrap in a production project:

- [ ] `templates/PROJECT-CLAUDE.md` copied as `CLAUDE.md` (**not** EEIK's root `CLAUDE.md`)
- [ ] `.claude/memory/project-context.md` filled in (services, environments, auth, AWS resources)
- [ ] `applyTo` glob patterns in `.github/instructions/` updated to match project source layout
- [ ] Unused domain files removed (no mainframe → delete mainframe agents/instructions)
- [ ] `python3 scripts/validate_manifest.py project-manifest.yaml` passes
- [ ] `python3 scripts/generate_adapters.py --apply` run to generate all 6 tool adapters
- [ ] At least one Claude Code slash command tested (`/estimate "hello world feature"`)
- [ ] At least one GitHub Copilot agent invoked (`@java-architect` or `@aws-architect`)
- [ ] Claude Code opened from **inside the project directory**, not from EEIK
- [ ] Golden Rules understood by the team (constructor injection, no secrets, jakarta.*, etc.)

---

## Contributing

1. **File naming:** `<name>.agent.md`, `<name>.instructions.md`, `<name>.prompt.md`
2. **Agent frontmatter:** `name`, `description` (trigger condition), `model`, `tools`
3. **Instruction frontmatter:** `applyTo` glob pattern
4. **Skill frontmatter:** `name`, `description`; folder name must match skill name
5. **Register new agents** in `AGENTS.md` and `CLAUDE.md` agent table
6. **Update TRACKER.md** when adding new files
7. Test each new file: invoke in Copilot Chat and Claude Code, verify persona is correct
