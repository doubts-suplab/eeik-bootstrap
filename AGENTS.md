# Agent Catalogue

Complete index of all agents, skills, and workflows in the EEIK Bootstrap repository.

- **GitHub Copilot agents** — `.github/agents/` — activated via Copilot Chat `@` selector in VS Code
- **Claude Code agents** — `.claude/agents/` — auto-selected by Claude Code based on task context
- **Skills** — `.github/skills/` — auto-loaded reusable capability packs
- **Workflows** — `.github/prompts/workflows/` — multi-agent orchestration prompts

---

## GitHub Copilot Agents (44 total)

### Java / Spring Boot

| Agent File | Name | Use When |
|-----------|------|---------|
| `java-dev.agent.md` | Java Developer | Implementing a Spring Boot ticket (service, controller, DTO, repository) |
| `java-tech-lead.agent.md` | Java Tech Lead | PR gating, standards enforcement, tech debt classification |
| `java-tester.agent.md` | Java Test Engineer | JUnit 5 unit, slice, and Testcontainers integration tests |
| `jacoco-coverage-tester.agent.md` | JaCoCo Coverage Analyst | Analysing JaCoCo reports and closing coverage gaps |
| `developer.agent.md` | Senior Developer | Full-stack implementation (Java + Angular together) |

### Angular

| Agent File | Name | Use When |
|-----------|------|---------|
| `angular-dev.agent.md` | Angular Developer | Standalone components, signals, reactive forms, lazy routes |
| `angular-tester.agent.md` | Angular Test Engineer | Jasmine/TestBed specs for components and services |
| `angular-coverage-checker.agent.md` | Angular Coverage Analyst | Istanbul/Karma coverage analysis and gap closure |

### Architecture & Design

| Agent File | Name | Use When |
|-----------|------|---------|
| `architect.agent.md` | Solution Architect | ADRs, bounded context design, API contracts, NFRs |
| `enterprise-architect.agent.md` | Enterprise Architect | Capability maps, TOGAF, technology lifecycle, EA artefacts |
| `aws-architect.agent.md` | AWS Solution Architect | Well-Architected reviews, CDK stacks, VPC/ECS/RDS design |
| `arb-reviewer.agent.md` | ARB Reviewer | Architecture Review Board gate reviews and sign-off |

### Code Review & Quality

| Agent File | Name | Use When |
|-----------|------|---------|
| `reviewer.agent.md` | Code Reviewer | PR reviews with [BLOCKER]/[MAJOR]/[MINOR]/[NIT] findings |
| `security-auditor.agent.md` | Security Auditor | OWASP Top 10 audit, CVSS ratings, remediation code |
| `performance-reviewer.agent.md` | Performance Specialist | N+1 queries, unbounded results, rendering bottlenecks |
| `coverage-enforcer.agent.md` | Coverage Guardian | Coverage gap analysis and targeted test generation |
| `test-quality-enforcer.agent.md` | Test Quality Inspector | Anti-pattern detection and test suite remediation |
| `tester.agent.md` | QA Engineer | Full test pyramid for any stack |

### Infrastructure & Deployment

| Agent File | Name | Use When |
|-----------|------|---------|
| `cdk-terraform-helper.agent.md` | CDK / Terraform Helper | CDK TypeScript stacks or Terraform HCL modules |
| `aws-deploy-helper.agent.md` | AWS Deploy Helper | Deploy commands, pre-deploy checklists, rollback runbooks |
| `local-deploy-helper.agent.md` | Local Deploy Helper | Docker Compose, local env setup, seed data |
| `containerisation-helper.agent.md` | Containerisation Helper | Dockerfiles, K8s manifests, container security hardening |
| `ci-engineer.agent.md` | CI Engineer | GitHub Actions pipelines, quality gates, build optimisation |
| `devsecops-engineer.agent.md` | DevSecOps Engineer | SAST/DAST/secrets scanning, security pipeline gates |

### Data, ML & AI

| Agent File | Name | Use When |
|-----------|------|---------|
| `data-scientist-aws.agent.md` | Data Scientist | SageMaker experiments, EDA, feature engineering, model evaluation |
| `ml-engineer-aws.agent.md` | ML Engineer | SageMaker training pipelines, model serving, MLOps |
| `ai-engineer-aws.agent.md` | AI Engineer | Bedrock LLM integration, RAG pipelines, prompt engineering |
| `mlops-engineer.agent.md` | MLOps Engineer | Model registry, drift monitoring, automated retraining |
| `ai-governance-officer.agent.md` | AI Governance Officer | Model cards, EU AI Act classification, AI risk assessment |

### Agentic AI

| Agent File | Name | Use When |
|-----------|------|---------|
| `langraph-engineer.agent.md` | LangGraph Engineer | Stateful graph agent workflows and state machines |
| `crewai-engineer.agent.md` | CrewAI Engineer | Multi-agent crews with role-based task delegation |
| `autogen-engineer.agent.md` | AutoGen Engineer | Microsoft AutoGen conversation patterns and GroupChat |
| `mcp-engineer.agent.md` | MCP Engineer | Model Context Protocol server and tool design |
| `a2a-engineer.agent.md` | A2A Engineer | Agent-to-Agent communication protocol design |

### Modernisation

| Agent File | Name | Use When |
|-----------|------|---------|
| `modernization-expert.agent.md` | Modernisation Expert | COBOL/JCL → Java migration, Spring 4/5 → Boot 3.x upgrade |
| `ibmi-modernization-expert.agent.md` | IBM i Expert | RPG/CL/DDS analysis, IBM i to Java migration strategy |

### Delivery & Operations

| Agent File | Name | Use When |
|-----------|------|---------|
| `estimator.agent.md` | Estimator | P50/P80/P90 bottom-up effort estimates |
| `project-tracker.agent.md` | Project Tracker | Sprint health, dependency mapping, delivery status |
| `ops-engineer.agent.md` | Ops Engineer | CloudWatch dashboards, alarms, runbooks, capacity planning |
| `sre-engineer.agent.md` | SRE Engineer | SLI/SLO definition, error budget policy, toil elimination |
| `incident-handler.agent.md` | Incident Handler | P1/P2 incident coordination and stakeholder communication |
| `rca-agent.agent.md` | RCA Agent | Post-incident 5-Whys analysis and corrective actions |

### Governance & Documentation

| Agent File | Name | Use When |
|-----------|------|---------|
| `analyst.agent.md` | Business Analyst | OpenAPI specs, Gherkin acceptance criteria, data models |
| `technical-writer.agent.md` | Technical Writer | API docs, architecture guides, onboarding, runbooks |
| `ai-governance-officer.agent.md` | AI Governance Officer | AI risk registers, model cards, compliance checklists |

---

## Claude Code Agents (44 total)

Claude Code auto-selects the most relevant agent from `.claude/agents/` based on your task. You can also invoke explicitly: *"Using the `java-developer` agent, implement the OrderService"*.

### Java / Spring Boot
`java-developer` · `java-tech-lead` · `java-tester` · `jacoco-coverage-tester` · `senior-developer`

### Angular
`angular-developer` · `angular-tester` · `angular-coverage-checker`

### Architecture
`architect` · `enterprise-architect` · `arb-reviewer`

### Cloud & Infrastructure
`aws-architect` · `cdk-terraform-helper` · `aws-deploy-helper` · `ci-engineer` · `containerisation-helper` · `devsecops-engineer` · `local-deploy-helper`

### Data, ML & AI
`ai-engineer` · `data-scientist` · `ml-engineer` · `mlops-engineer` · `ai-governance-officer`

### Agentic AI
`langraph-engineer` · `crewai-engineer` · `autogen-engineer` · `mcp-engineer` · `a2a-engineer`

### Modernisation
`modernization-expert` · `ibmi-modernization-expert`

### Quality & Security
`code-reviewer` · `security-auditor` · `performance-engineer` · `coverage-enforcer` · `test-quality-enforcer` · `tester` · `business-analyst`

### Delivery & Operations
`estimator` · `project-tracker` · `ops-engineer` · `sre-engineer` · `incident-handler` · `rca-agent` · `technical-writer`

---

## Skills (12 total)

Auto-loaded by Copilot when context matches. Located in `.github/skills/`.

| Skill | Use When |
|-------|---------|
| `estimation/` | Estimating, sizing, or planning effort |
| `jacoco-analysis/` | JaCoCo reports, coverage thresholds, missed branches |
| `aws-cdk-deploy/` | CDK deploy, diff, or stack rollback |
| `incident-response/` | Declaring or managing a P1/P2 incident |
| `code-quality-scan/` | SonarQube, SpotBugs, OWASP Dependency Check findings |
| `ai-governance/` | AI system governance reviews and model cards |
| `architecture-governance/` | ARB gate reviews and architecture compliance |
| `devsecops/` | Security pipeline configuration and gate setup |
| `langgraph-patterns/` | LangGraph graph design and state machine patterns |
| `mcp-server-design/` | MCP server and tool schema design |
| `mlops-pipeline/` | MLOps pipelines, model registry, drift monitoring |
| `sre-practices/` | SLI/SLO definition and error budget management |

---

## Orchestrated Workflows (14 total)

Located in `.github/prompts/workflows/`. Reference via `#file:` in Copilot Chat.

| Workflow | Description |
|---------|-------------|
| `full-feature-dev.prompt.md` | Analyst → Architect → Developer → Tester → Coverage → Reviewer |
| `pr-review-workflow.prompt.md` | Code → Security → Performance → Test Quality review |
| `tdd-cycle.prompt.md` | Red → Green → Refactor → Coverage |
| `cobol-to-java-workflow.prompt.md` | COBOL modernisation: Analyse → Design → Implement → Test |
| `aws-infra-deploy.prompt.md` | Architect → CDK → CI/CD → Deploy → Smoke Test |
| `incident-rca-workflow.prompt.md` | Detection → Triage → War Room → Resolution → RCA |
| `arb-review-workflow.prompt.md` | Formal ARB gate review: Intake → Standards → Assess → Recommend |
| `ai-governance-review.prompt.md` | AI system: Classification → Model Card → Risk Assessment → Sign-Off |
| `multi-agent-system-design.prompt.md` | Problem Decomposition → Agent Topology → State Design → Implement |
| `mcp-server-development.prompt.md` | Capability Design → Security → Schema → Implement → Document |
| `ibmi-to-cloud-workflow.prompt.md` | Discovery → Architecture → Phased Migration → Cutover |
| `devsecops-pipeline-review.prompt.md` | Audit → Gap Analysis → Remediate → Validate |
| `game-day-exercise.prompt.md` | Hypothesis → Baseline → Inject → Observe → Report |
| `ml-model-delivery.prompt.md` | Experiment → Governance → MLOps → Deploy → Monitor |

---

## Slash Commands (Claude Code only)

Located in `.claude/commands/`. Type `/command-name` in Claude Code.

| Command | Description |
|---------|-------------|
| `/adr "decision title"` | Scaffold a new Architecture Decision Record |
| `/rca "symptoms"` | Open a blameless RCA workflow |
| `/estimate "feature description"` | Produce P50/P80/P90 effort estimate |
| `/review` | Run full PR review checklist |
| `/incident "severity: P1, service: name, symptom: ..."` | Declare and coordinate an incident |
| `/security-scan [path]` | OWASP Top 10 review and secrets scan |
| `/deploy-check "env: X, service: Y"` | Pre-deployment readiness checklist |
| `/memory-update "what changed"` | Update `.claude/memory/` files |
| `/coverage-report [path]` | Coverage gap analysis with targeted test stubs |
| `/sync-docs [path]` | Sync API documentation against OpenAPI specs |
