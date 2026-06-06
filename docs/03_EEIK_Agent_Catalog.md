# EEIK Agent Catalog

> **Version:** 1.0 — 2026-06-06
> Complete listing of all 44 agents per layer, plus commands, hooks, and prompt libraries.

---

## 1. Architecture Agents

### `architect` / `architect.agent.md`
**When:** New service design, ADR authoring, bounded context reviews, API contract design, non-functional requirements analysis.
**Produces:** ADRs, sequence diagrams (Mermaid), API contract specifications, bounded context maps.
**Does not:** Write implementation code — architecture artefacts only.

### `enterprise-architect` / `enterprise-architect.agent.md`
**When:** TOGAF-aligned EA artefacts, capability maps, value streams, technology lifecycle assessments, programme-level architecture.
**Produces:** Capability maps, technology radar entries, integration pattern recommendations, portfolio views.
**Scale:** Programme/portfolio level — not service level.

### `arb-reviewer` / `arb-reviewer.agent.md`
**When:** Formal Architecture Review Board gate before build begins.
**Produces:** ARB Recommendation Report: APPROVED / APPROVED WITH CONDITIONS / REJECTED, with findings table.
**Severity:** BLOCKER / MAJOR / MINOR / ADVISORY per finding.

### `aws-architect` / `aws-architect.agent.md`
**When:** AWS Well-Architected reviews, CDK stack design, cost estimates, VPC/ECS/RDS/Lambda architecture.
**Produces:** CDK TypeScript skeleton stacks, cost estimates, Well-Architected findings, architecture diagrams.

---

## 2. Development Agents

### Java

#### `java-developer` / `java-dev.agent.md`
**When:** Ticket-scoped Spring Boot 3.x implementation — services, controllers, repositories, DTOs, MapStruct mappers.
**Produces:** Complete, compilable Java files with all imports, Javadoc, and unit tests.
**Constraint:** Implements within existing architecture; does not redesign.

#### `java-tech-lead` / `java-tech-lead.agent.md`
**When:** PR gating, standards enforcement, tech debt classification, framework-level decisions.
**Produces:** Code review with standards violations flagged, tech debt register entries, framework guidance.

#### `senior-developer` / `developer.agent.md`
**When:** Features requiring Spring Boot AND Angular together in one pass.
**Produces:** Full-stack implementation: Java service + Angular component together.

### Angular

#### `angular-developer` / `angular-dev.agent.md`
**When:** Standalone components, services, reactive forms, lazy routes, signal-based state.
**Produces:** Complete TypeScript/HTML/SCSS component sets with specs.

---

## 3. AI Engineering Agents

### `ai-engineer` / `ai-engineer-aws.agent.md`
**When:** Building generative AI applications: RAG pipelines, Bedrock LLM integration, prompt engineering, agent guardrails.
**Produces:** Python RAG pipeline code, Bedrock integration, prompt templates, output validation.
**Safety:** Logs metadata only (no PII), always sets `max_tokens`, always validates outputs.

### `langraph-engineer` / `langraph-engineer.agent.md`
**When:** LangGraph stateful graph workflows, agent state machines, conditional routing, cyclic agent loops.
**Produces:** Graph topology diagram (Mermaid), typed `State` schema, complete Python implementation.
**Safety:** Always defines maximum iteration count; always configures LangSmith tracing.

### `crewai-engineer` / `crewai-engineer.agent.md`
**When:** CrewAI multi-agent crews with role-based task delegation and tool integration.
**Produces:** Crew definition with agents, tasks, and process; complete Python implementation.

### `autogen-engineer` / `autogen-engineer.agent.md`
**When:** Microsoft AutoGen conversation patterns, GroupChat orchestration, tool-enabled agents.
**Produces:** AssistantAgent/UserProxyAgent configurations, GroupChat setups, conversation flows.

### `mcp-engineer` / `mcp-engineer.agent.md`
**When:** MCP server/client design — tool schemas, resource providers, stdio/SSE transports.
**Produces:** Complete Python or TypeScript MCP server, JSON Schema tool definitions, `mcp.json` config.

### `a2a-engineer` / `a2a-engineer.agent.md`
**When:** Agent-to-Agent communication protocol design, multi-agent orchestration, inter-agent task delegation.
**Produces:** Agent topology diagram, communication schemas, orchestration code, safety controls.

---

## 4. Modernisation Agents

### `modernization-expert` / `modernization-expert.agent.md`
**When:** COBOL/JCL → Java migration, Spring 4/5 → Spring Boot 3.x upgrade, monolith decomposition.
**Produces:** Migration assessment, phased plan, strangler-fig design, coexistence strategy.
**Philosophy:** Never big-bang rewrite; always strangler-fig or phased re-platform.

### `ibmi-modernization-expert` / `ibmi-modernization-expert.agent.md`
**When:** RPG IV, RPGLE, CL analysis; IBM i to Java migration; iSeries-to-cloud strategy.
**Produces:** Program analysis report (data structures, file I/O, business rules), Java equivalent design, migration effort estimate.
**Speciality:** IBM i data type precision mapping (packed decimal → `BigDecimal`).

---

## 5. Code Explanation Agents

### `technical-writer` / `technical-writer.agent.md`
**When:** API documentation, architecture guides, onboarding docs, runbooks, ADRs as narrative.
**Produces:** Clear, accurate, testable documentation following the Divio system (tutorials, how-to, reference, explanation).
**Rule:** Never documents what code does — documents why and how to use it.

### `business-analyst` / `analyst.agent.md`
**When:** Translating business requirements into OpenAPI specs, Gherkin acceptance criteria, event schemas.
**Produces:** OpenAPI 3.x YAML, Gherkin feature files, data models, event schemas.
**Position:** Upstream — designs APIs before implementation. Not for documenting existing APIs (use `technical-writer`).

---

## 6. DevSecOps Agents

### `devsecops-engineer` / `devsecops-engineer.agent.md`
**When:** Embedding security into CI/CD: SAST, DAST, secrets scanning, container scanning, dependency checks.
**Produces:** GitHub Actions YAML with security stages, tool configurations, security gate thresholds, CVE suppression files.

### `security-auditor` / `security-auditor.agent.md`
**When:** OWASP Top 10 code reviews, vulnerability analysis, authentication and authorisation reviews.
**Produces:** Severity-rated findings (CRITICAL/HIGH/MEDIUM/LOW) with remediation code.
**Trigger:** Code handling auth, SQL, file I/O, user input, or after `/security-scan`.

### `ci-engineer` / `ci-engineer.agent.md`
**When:** GitHub Actions pipeline design, build optimisation, test parallelisation, quality gate configuration.
**Produces:** Complete `.github/workflows/*.yml` files, caching strategies, deployment triggers.

---

## 7. Delivery Agents

### `estimator` / `estimator.agent.md`
**When:** Effort estimates for features, epics, or technical tasks.
**Formula:** `Human Days = Σ Raw Hours ÷ 6.4` with P50/P80/P90 confidence ranges.
**Produces:** Task breakdown table, P50/P80/P90 summary, assumptions list, risk register.

### `project-tracker` / `project-tracker.agent.md`
**When:** Sprint health assessment, dependency mapping, delivery status reports.
**Produces:** Sprint status report with blockers table, risk register, delivery forecast, next actions.

---

## 8. Operations Agents

### `ops-engineer` / `ops-engineer.agent.md`
**When:** CloudWatch dashboards, alarm configuration, runbook authoring, capacity planning, operational readiness.
**Produces:** CloudWatch alarm definitions, runbooks following standard template, capacity models.
**Rule:** Every alert must have a runbook; every runbook must have actionable steps.

### `sre-engineer` / `sre-engineer.agent.md`
**When:** SLI/SLO definition, error budget policy, toil identification, game day planning.
**Produces:** SLO definition document, error budget calculation, burn rate alert configuration, toil backlog.

### `incident-handler` / `incident-handler.agent.md`
**When:** Live production incident — P1/P2 declaration, war room coordination, stakeholder communication.
**Produces:** Incident record with live timeline, 15-minute investigation cycles, stakeholder update drafts.
**Rule:** Restore service first. Establish root cause second.

### `rca-agent` / `rca-agent.agent.md`
**When:** Post-incident blameless root cause analysis.
**Produces:** Full RCA document: timeline, 5-Whys analysis, contributing factors, SMART corrective actions.
**Updates:** `.claude/memory/rca-tracker.md` with each new incident.

---

## 9. AI Governance Agents

### `ai-governance-officer` / `ai-governance-officer.agent.md`
**When:** AI system governance review, model card production, EU AI Act classification, GDPR Article 22 assessment.
**Produces:** EU AI Act risk tier classification, model card, AI risk register entry, pre-deployment governance checklist.
**Rule:** Never approves high-risk AI without documented human-in-the-loop controls.

### `data-scientist` / `data-scientist-aws.agent.md`
**When:** EDA, feature engineering, model training/evaluation, SageMaker experiments.
**Produces:** Reproducible Python pipelines with fixed random seeds, cross-validation results with confidence intervals, baseline comparisons.

### `ml-engineer` / `ml-engineer-aws.agent.md`
**When:** ML training pipeline implementation, feature stores, model serving, MLOps infrastructure.
**Produces:** SageMaker Pipeline definitions, model serving configurations, feature store schemas.

### `mlops-engineer` / `mlops-engineer.agent.md`
**When:** Model registry, drift monitoring, automated retraining pipelines, ML CI/CD.
**Produces:** MLOps maturity assessment, SageMaker Model Monitor configuration, retraining trigger design.

---

## 10. Commands (Claude Code Slash Commands)

| Command | Agent Activated | Primary Output |
|---------|----------------|----------------|
| `/adr` | `architect` | ADR in `docs/decisions/` |
| `/rca` | `rca-agent` | RCA in `docs/rca/` + `rca-tracker.md` update |
| `/estimate` | `estimator` | P50/P80/P90 breakdown table |
| `/review` | `code-reviewer` + `security-auditor` + `performance-engineer` | Structured findings by severity |
| `/incident` | `incident-handler` | Incident record + live timeline |
| `/security-scan` | `security-auditor` | OWASP findings + secrets scan |
| `/deploy-check` | `aws-deploy-helper` | Go/No-Go checklist + deployment command |
| `/memory-update` | Context-dependent | Updated `.claude/memory/` files |
| `/coverage-report` | `jacoco-coverage-tester` / `angular-coverage-checker` | Targeted test stubs |
| `/sync-docs` | `technical-writer` | API documentation gap report |

---

## 11. Hooks

### Claude Code Hooks (`.claude/hooks/`)

| Hook | Trigger | Blocks |
|------|---------|--------|
| `pre-bash-guard.sh` | PreToolUse:Bash | Force-push, hard reset, `rm -rf /`, DROP DATABASE, `cdk destroy`, AWS terminations |
| `pre-write-guard.sh` | PreToolUse:Write | Unsafe write targets |
| `post-edit-check.sh` | PostToolUse:Edit | Post-edit validation failures |
| `on-stop.sh` | Stop | Auto-updates `session-log.md` |

### GitHub Copilot Hooks (`.github/hooks/`)

| Hook | Events Captured | Log File |
|------|----------------|---------|
| `session-hooks.json` | sessionStart, sessionEnd, userPromptSubmitted | `.copilot-session.log` |
| `tool-use-hooks.json` | preToolUse, postToolUse, errorOccurred | `.copilot-tool.log` |

---

## 12. Prompt Libraries

### Task Prompts (22 — `.github/prompts/tasks/`)

Single-purpose prompts invoked via `#file:` in Copilot Chat or the corresponding slash command:

| Category | Prompts |
|----------|---------|
| Code Generation | `generate-rest-api`, `generate-angular-component`, `generate-angular-service`, `generate-unit-tests`, `generate-integration-tests`, `generate-mapstruct-mapper`, `generate-openapi-spec` |
| Documentation | `add-javadoc`, `add-logging`, `write-adr`, `write-rfc`, `write-model-card` |
| Explanation | `explain-code`, `explain-mainframe-program`, `explain-rpg-program` |
| Modernisation | `modernize-cobol-to-java`, `modernize-rpg-to-java`, `refactor-to-clean-code` |
| Governance | `ai-risk-assessment`, `define-sli-slo`, `code-review`, `update-project-memory` |

### Workflow Prompts (14 — `.github/prompts/workflows/`)

Multi-agent orchestration sequences:

| Workflow | Agent Sequence |
|---------|---------------|
| `full-feature-dev` | Analyst → Architect → Developer → Tester → Coverage → Reviewer |
| `pr-review-workflow` | Reviewer → Security → Performance → Test Quality |
| `tdd-cycle` | Analyst → Tester → Developer → Reviewer → Coverage |
| `cobol-to-java-workflow` | Modernisation Expert → Architect → Developer → Tester → Security |
| `aws-infra-deploy` | AWS Architect → CDK Helper → CI Engineer → Deploy Helper → Ops |
| `incident-rca-workflow` | Incident Handler → Ops → RCA Agent → Project Tracker |
| `arb-review-workflow` | ARB Reviewer → (conditions tracked) |
| `ai-governance-review` | AI Governance Officer → AI Engineer → MLOps Engineer |
| `multi-agent-system-design` | A2A Engineer + (LangGraph/CrewAI/AutoGen) Engineer |
| `mcp-server-development` | MCP Engineer → Security Auditor |
| `ibmi-to-cloud-workflow` | IBM i Expert → Architect → AWS Architect → Java Developer |
| `devsecops-pipeline-review` | DevSecOps Engineer → CI Engineer |
| `game-day-exercise` | SRE Engineer → Ops Engineer → Incident Handler |
| `ml-model-delivery` | Data Scientist → ML Engineer → MLOps Engineer → AI Governance Officer |

---

## 13. Agent Collaboration Patterns

### PR Review Pipeline
```
code-reviewer (correctness, quality)
    ↓
security-auditor (OWASP, secrets, injection)
    ↓
performance-engineer (N+1, unbounded sets, latency)
    ↓
test-quality-enforcer (anti-patterns, flaky tests)
    ↓
coverage-enforcer or jacoco-coverage-tester (gap analysis)
```

### Feature Delivery Pipeline
```
business-analyst (requirements → OpenAPI + Gherkin)
    ↓
architect (design → ADR + sequence diagram)
    ↓
java-developer / angular-developer (implementation)
    ↓
java-tester / angular-tester (test suites)
    ↓
jacoco-coverage-tester / angular-coverage-checker (coverage gap closure)
    ↓
code-reviewer (final gate)
```

### AI System Delivery
```
ai-engineer (build RAG/LLM/agent system)
    ↓
ai-governance-officer (model card + risk assessment)
    ↓
mlops-engineer (monitoring + retraining pipeline)
    ↓
security-auditor (guardrails + PII review)
    ↓
sre-engineer (SLO + error budget for AI system)
```

---

## 14. Escalation Matrix

| Situation | First Agent | Escalate To |
|-----------|------------|-------------|
| PR with Java violation | `code-reviewer` | `java-tech-lead` |
| Security finding in code | `code-reviewer` | `security-auditor` |
| Architectural question | `architect` | `enterprise-architect` (portfolio), `arb-reviewer` (gate) |
| AI system deployment | `ai-engineer` | `ai-governance-officer` |
| Production incident | `incident-handler` | `sre-engineer` (SLO breach), `rca-agent` (post-resolution) |
| Coverage gap | `coverage-enforcer` | `jacoco-coverage-tester` (Java-only JaCoCo) |
| Multi-agent design | `a2a-engineer` | Domain-specific (langraph-engineer, crewai-engineer, etc.) |
