# Enterprise Engineering Intelligence Kit (EEIK) Bootstrap

## AI-Native Enterprise Engineering Bootstrap Platform

A ready-to-fork enterprise engineering intelligence platform that provisions Claude Code and GitHub Copilot with rich, structured context for enterprise software development programs.

EEIK transforms AI coding assistants from generic code generators into context-aware engineering partners that understand:

- Technology stacks
- Enterprise standards
- Architecture governance
- Modernization programs
- Delivery processes
- Cloud platforms
- AI engineering patterns
- Organizational knowledge

Drop the configuration layers from this repository into any project and both Claude Code and GitHub Copilot become engineering assistants that understand your ecosystem from day one.

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
For:
- Claude Code
- GitHub Copilot

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
CLAUDE.md          Claude Code session brief + golden rules
AGENTS.md          OpenAI Codex CLI manifest
GEMINI.md          Google Gemini CLI context
CONTRIBUTING.md    Contribution guide
SECURITY.md        Vulnerability reporting

── Tool-Specific Config ──────────────────────────────────────────────────────
.claude/           Claude Code  — agents, commands, hooks, memory, standards
.github/           Copilot      — instructions, agents, prompts, workflows, hooks
.kiro/             Kiro (AWS)   — steering docs, hooks
.cursor/           Cursor       — .mdc rules (golden-rules, architecture, security)

── Intelligence Layer (tool-agnostic) ────────────────────────────────────────
capability-packs/  13 packs — core, java, python, aws, containers, modernization,
                   ai-engineering, architecture, governance, delivery,
                   insurance, banking, healthcare
knowledge/         Patterns, anti-patterns, ADRs, lessons-learned,
                   incident-repository, event-catalog, reference-architectures
templates/         Code templates per technology domain

── Generators ────────────────────────────────────────────────────────────────
generators/        project-analyzer, repository-generator, agent-generator,
                   capability-selector, knowledge-generator, governance-generator,
                   model-router, adapter-generator
bootstrap/         /bootstrap command: manifests, schemas, validators, resolvers

── Executable Scripts ────────────────────────────────────────────────────────
scripts/           eeik_cli.py          — central CLI entry point
                   validate_manifest.py — JSON Schema + governance rules
                   activate_packs.py    — manifest → .claude/ materialisation
                   generate_adapters.py — synthesise multi-tool adapter files
                   claude_harness.py    — run generators via claude --print

── CI/CD ─────────────────────────────────────────────────────────────────────
.github/workflows/ eeik-validate.yml   — manifest + agent lint on PR
                   eeik-adapt.yml      — auto-regenerate adapters on manifest change

── Documentation ─────────────────────────────────────────────────────────────
docs/
├── eeik-guide.html           Interactive visual guide (open in browser)
├── specs/                    Internal design specs (11 files)
├── concepts/                 Vision, architecture, AI governance
├── reference/                Roadmap, inventory, platform capabilities
├── getting-started/          Adoption guide, use cases
└── [domain folders]          Architecture, AI engineering, modernization, etc.
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
capability-packs/
├── architecture/
├── governance/
├── java/
├── spring-boot/
├── react/
├── angular/
├── python/
├── aws/
├── containers/
├── ai-engineering/
├── langgraph/
├── modernization/
├── operations/
├── delivery/
├── enterprise-architecture/
└── insurance/
```

Each pack may contain:
- Standards
- Templates
- Prompts
- Workflows
- Knowledge assets
- Review criteria


## How to Adopt This Bootstrap

### 1. Copy the Configuration Layers

```bash
# GitHub Copilot layer
cp -r .github/        /path/to/your-project/.github/

# Claude Code layer
cp -r .claude/        /path/to/your-project/.claude/

# Editor config
cp -r .vscode/        /path/to/your-project/.vscode/
cp    .editorconfig   /path/to/your-project/.editorconfig
cp    AGENTS.md       /path/to/your-project/AGENTS.md
cp    CLAUDE.md       /path/to/your-project/CLAUDE.md
```

### 2. Customise Master Instructions

Edit `.github/copilot-instructions.md`:
- **Program Context** — describe your specific project and bounded contexts
- **Technology Stack** — reflect your actual versions and dependency policy
- **Architecture style** — e.g., Event-driven, Layered, Hexagonal, Microservices
- **Delivery model** — e.g., Continuous Delivery, Incremental delivery, Staged rollout

Edit `.claude/memory/project-context.md` with:

- Service inventory
- Environment details
- Security requirements
- Integration landscape

### 3. Adjust `applyTo` Glob Patterns

Each file in `.github/instructions/` has an `applyTo` frontmatter. Update to match your source layout:

```markdown
---
applyTo: "src/main/java/com/yourcompany/**/*.java"
---
```

### 4. Remove Unused Domains

Delete instruction files, agents, and prompts for domains not used in your project.


### 5. Verify Context is Loading

Open any `.java` file and ask Copilot Chat:
> "What coding standards apply to this file?"

It should describe the standards from `copilot-instructions.md` and the matching `*.instructions.md`.

Ask Claude Code:
> "What agents are available and when should I use each?"

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

## Claude Code Slash Commands (10)

Type in Claude Code to activate specialist workflows:

| Command | Description |
|---------|-------------|
| `/adr "decision title"` | Scaffold Architecture Decision Record |
| `/rca "symptoms"` | Blameless 5-Whys root cause analysis |
| `/estimate "feature"` | P50/P80/P90 effort estimate |
| `/review` | Full PR review: correctness, security, performance, quality |
| `/incident "severity: P1, service: X, symptom: Y"` | Declare and coordinate an incident |
| `/security-scan [path]` | OWASP Top 10 review + secrets scan |
| `/deploy-check "env: X, service: Y"` | Pre-deployment readiness checklist |
| `/memory-update "what changed"` | Update `.claude/memory/` persistent context |
| `/coverage-report [path]` | JaCoCo/Istanbul gap analysis + targeted tests |
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

- [ ] `copilot-instructions.md` customised (program context, stack, dependency policy)
- [ ] `.claude/memory/project-context.md` filled in (services, environments, auth)
- [ ] `applyTo` glob patterns updated to match project source layout
- [ ] Unused domain files removed (e.g., no mainframe → remove mainframe agents/instructions)
- [ ] At least one Copilot agent invoked and responding in correct persona
- [ ] At least one Claude Code slash command tested (`/estimate "hello world feature"`)
- [ ] `.gitignore` includes `.copilot-*.log` and `.claude/memory/session-log.md`
- [ ] Recommended VS Code extensions installed (`.vscode/extensions.json`)
- [ ] Golden Rules from `CLAUDE.md` understood by the team

---

## Contributing

1. **File naming:** `<name>.agent.md`, `<name>.instructions.md`, `<name>.prompt.md`
2. **Agent frontmatter:** `name`, `description` (trigger condition), `model`, `tools`
3. **Instruction frontmatter:** `applyTo` glob pattern
4. **Skill frontmatter:** `name`, `description`; folder name must match skill name
5. **Register new agents** in `AGENTS.md` and `CLAUDE.md` agent table
6. **Update TRACKER.md** when adding new files
7. Test each new file: invoke in Copilot Chat and Claude Code, verify persona is correct
