# Enterprise Engineering Intelligence Kit (EEIK) Bootstrap

A ready-to-fork workspace seed that provisions Claude Code and GitHub Copilot with rich, structured context for enterprise software development programs. Drop the files from this repository into any project and both tools become context-aware assistants that understand your technology stack, coding conventions, specialist agent roles, and operational processes — from day one.

This is **not a runnable application**. It is a configuration and context layer for Claude Code and GitHub Copilot.

---

## Repository Structure

```
.github/                             ← GitHub Copilot configuration
├── copilot-instructions.md          ← Always-on repo-wide context (auto-loaded)
├── instructions/          (29)      ← Path-specific instructions (auto-applied by file type)
├── agents/                (44)      ← Custom agent personas (select via @ in Copilot Chat)
├── prompts/
│   ├── tasks/             (22)      ← Single-purpose task prompts
│   └── workflows/         (14)      ← Multi-step orchestrated workflows
├── skills/                (12)      ← Auto-loaded reusable capability packs
└── hooks/                  (2)      ← Session and tool-use lifecycle logging

.claude/                             ← Claude Code configuration
├── settings.json                    ← Model, permissions, hooks
├── agents/                (44)      ← Claude Code specialist agents (auto-selected)
├── commands/              (10)      ← Slash commands (/adr, /estimate, /review, …)
├── hooks/                  (4)      ← pre-bash-guard, pre-write-guard, post-edit-check, on-stop
├── memory/                (10)      ← Persistent context loaded at session start
└── standards/              (8)      ← Coding standards per technology domain

.vscode/                             ← VS Code settings and extension recommendations
.editorconfig                        ← Cross-editor formatting rules
AGENTS.md                            ← Complete agent catalogue and quick-reference
CLAUDE.md                            ← Claude Code session brief and golden rules
TRACKER.md                           ← Bootstrap completion tracker
docs/                                ← Detailed specifications and implementation guides
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

Edit `.claude/memory/project-context.md`:
- Fill in service inventory, environment URLs, AWS account IDs, on-call contacts

### 3. Adjust `applyTo` Glob Patterns

Each file in `.github/instructions/` has an `applyTo` frontmatter. Update to match your source layout:

```markdown
---
applyTo: "src/main/java/com/yourcompany/**/*.java"
---
```

### 4. Remove Unused Domains

Delete instruction files, agents, and prompts for domains not used in your project:

```bash
# Example: no mainframe code
rm .github/instructions/mainframe*.instructions.md
rm .github/agents/modernization-expert.agent.md
rm .github/agents/ibmi-modernization-expert.agent.md
rm .github/prompts/tasks/modernize-*.prompt.md
rm .github/prompts/workflows/cobol-to-java-workflow.prompt.md
rm .claude/agents/modernization-expert.md
rm .claude/agents/ibmi-modernization-expert.md
rm .claude/standards/mainframe.md
```

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
