# /bootstrap — EEIK Project Discovery & Manifest Generation

Run this command at the start of any new project to generate a fully validated `project-manifest.yaml` that drives all subsequent EEIK tooling — capability selection, repository generation, agent configuration, and governance setup.

## Usage

```
/bootstrap
```

No arguments required. The command runs an interactive discovery interview.

---

## What This Command Does

1. Runs a structured discovery interview (10 question areas)
2. Applies capability resolution rules from `bootstrap/resolvers/capability-matrix.yaml`
3. Determines governance profile and required reviews
4. Generates a validated `project-manifest.yaml` at the project root
5. Outputs a capability selection summary with agent recommendations
6. Flags any incompatible combinations or governance requirements

---

## Discovery Interview

Ask the user the following questions **one section at a time**. Wait for a clear answer before proceeding. Accept shorthand answers (e.g. "java21" → `language: java, version: 21`). If the user is uncertain, offer the default value and move on.

---

### Section 1 — Project Identity

```
What is the project name? (kebab-case, e.g. claims-modernization)
What does this project do? (one sentence)
Which team owns it?
```

---

### Section 2 — Project Type

```
What type of project is this?

  1. greenfield        → New system built from scratch
  2. modernization     → Replacing or wrapping a legacy system
  3. poc               → Proof of concept, time-boxed exploration
  4. mvp               → Minimum viable product
  5. enterprise-platform → Shared internal platform used by multiple teams
  6. agent-platform    → AI agent platform or multi-agent system
```

---

### Section 3 — Business Domain

```
Which business domain?

  1. insurance
  2. banking
  3. healthcare
  4. retail
  5. generic
```

⚠️ Internally: insurance / banking / healthcare requires governance `regulated` or `enterprise`. Override silently if user selects basic/standard and explain.

---

### Section 4 — Backend Technology

```
Primary backend language and version?

  1. java 21    (Spring Boot 3.x — recommended)
  2. java 25    (Spring Boot 4.x)
  3. python     (FastAPI / Django)
  4. mixed      (Multiple backend languages)
```

If java: also ask `Framework? (spring-boot / quarkus — default: spring-boot)`

---

### Section 5 — Frontend

```
Does this project have a frontend?

  1. react
  2. angular
  3. none (API / backend only)
```

---

### Section 6 — Cloud & Infrastructure

```
Which cloud platform?

  1. aws    (recommended)
  2. azure
  3. gcp
  4. hybrid

Infrastructure-as-code tooling?

  1. cdk        (TypeScript CDK — recommended for AWS)
  2. terraform
  3. both
  4. none
```

---

### Section 7 — Architecture Style

```
Which architectural style?

  1. microservices      → Independent deployable services
  2. modular-monolith   → Single deployment, clear module boundaries
  3. event-driven       → Asynchronous, event-first design
  4. serverless         → Lambda-first, event-triggered
  5. monolith           → Single deployable unit
  6. agentic            → AI agent orchestration platform
```

Optional follow-up:
```
Additional patterns? (select all that apply)
  ddd / cqrs / saga / outbox / api-gateway / bff / strangler-fig / none
```

---

### Section 8 — AI Capabilities

```
AI or agentic capabilities?

  1. none
  2. rag                      → Retrieval-augmented generation
  3. single-agent             → One AI agent
  4. multi-agent              → Multiple coordinated agents
  5. enterprise-agent-platform → Organisation-wide agent infrastructure
```

If AI enabled:
```
Framework?
  1. langgraph      (recommended for multi-agent)
  2. crewai
  3. autogen
  4. bedrock-agents (AWS native)
  5. mcp
```

---

### Section 9 — Governance

```
Governance level?

  1. basic      → Minimal, PoC / internal tools
  2. standard   → Code review, security scan, architecture review
  3. regulated  → Financial / healthcare / insurance — formal compliance
  4. enterprise → ARB gates, formal sign-off, full audit trail
```

⚠️ If regulated domain + user selects basic/standard → inform and override to `regulated`.

---

### Section 10 — Delivery & Modernization

```
Delivery model?

  1. single-team
  2. multi-team
  3. enterprise-program

Legacy modernization involved?

  1. none
  2. ibmi      (IBM i / AS400 / RPG)
  3. cobol     (COBOL / mainframe batch)
  4. mainframe (CICS / DB2 z/OS)
  5. mixed
```

---

## Capability Resolution

After collecting answers, resolve capability packs from `bootstrap/resolvers/capability-matrix.yaml`:

```
selected_packs = []

for each manifest field → look up in capability-matrix.yaml → add matching packs
deduplicate → sort by resolution_order
add project_type.extra_packs
apply governance_override for regulated domains
collect compliance_hints from domain entry
```

---

## Manifest Generation

Write `project-manifest.yaml` at the project root using this structure:

```yaml
# Generated by EEIK /bootstrap
# Date: {today}
# Schema: bootstrap/schemas/manifest-schema.json

schema_version: "1.0"

project:
  name: {project.name}
  description: {project.description}
  owner: {project.owner}
  domain: {domain}
  project_type: {project_type}

technology:
  backend:
    language: {backend.language}
    version: {backend.version}
    framework: {backend.framework}
  frontend:
    framework: {frontend.framework}
  database:
    migration_tool: flyway

architecture:
  style: {architecture.style}
  api_style: rest

cloud:
  provider: {cloud.provider}
  infra_as_code: {infra_as_code}
  regions: [eu-west-1]
  multi_account: true

ai:
  enabled: {true if ai != none}
  pattern: {ai.pattern}
  framework: {ai.framework}
  governance_required: {true if regulated domain or multi-agent+}

governance:
  profile: {governance.profile}
  reviews_required: {from capability-matrix}

delivery:
  model: {delivery.model}
  methodology: agile
  sprint_length_weeks: 2
  cicd_platform: github-actions

modernization:
  enabled: {true if != none}
  source_platform: {source_platform}

observability:
  enabled: true
  logging: cloudwatch
  tracing: x-ray
  metrics: cloudwatch
  slo_required: {true if regulated or enterprise governance}
```

---

## Output Summary

Print this after writing the manifest:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EEIK Bootstrap Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Project:        {name}
  Domain:         {domain}
  Type:           {project_type}
  Governance:     {governance.profile}

  ✅ Manifest written → project-manifest.yaml

  Selected Capability Packs:
  {list each resolved pack with ✅/🔧/📋 status}

  Recommended Agents (from .claude/agents/):
  {list top 5–8 agents most relevant to this manifest}

  Required Reviews:
  {list from governance.reviews_required}

  ⚠️  Warnings:
  {any flagged incompatibilities or planned-but-missing packs}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Next steps:
  /validate-manifest   → validate the generated manifest
  /estimate "feature"  → estimate effort on first features
  /adr "decision"      → record first architecture decisions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Validation After Generation

After generating the manifest, run these checks automatically:

- All required fields present: `schema_version`, `project.name`, `project.domain`, `project.project_type`, `technology.backend.language`, `architecture.style`, `cloud.provider`, `governance.profile`, `delivery.model`
- All values match allowed enums in `bootstrap/schemas/manifest-schema.json`
- Regulated domain → governance is `regulated` or `enterprise`
- No incompatible combinations (e.g. mainframe + serverless architecture)

If validation fails, show failures and ask user to correct before writing file.

---

## Files Written

| File | Description |
|------|-------------|
| `project-manifest.yaml` | Generated project manifest — source of truth for all EEIK tooling |

---

## Error Cases

| Situation | Action |
|-----------|--------|
| Regulated domain + basic governance | Auto-override to `regulated`, explain to user |
| User uncertain about a field | Use schema default, add comment in manifest |
| Incompatible combination | Flag, explain, ask for clarification |
| Skip AI section | Set `ai.enabled: false`, omit AI fields |
