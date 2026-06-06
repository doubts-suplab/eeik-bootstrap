---
applyTo: "**/architecture/**, **/adr/**, **/rfc/**, **/*.arch.md"
description: "ARB process, ADR/RFC authoring standards, technology lifecycle classification, and architecture fitness functions for enterprise governance."
---

# Architecture Governance — Copilot Instructions

> Applied automatically when working with architecture records, ADRs, RFCs, and architecture markdown files. Loaded alongside copilot-instructions.md.

---

## Architecture Review Board (ARB)

### Trigger Conditions — When ARB Review is Mandatory

The following changes **must not proceed to implementation** without a recorded ARB decision:

| Trigger | Examples |
|---------|---------|
| New service or application | A new Spring Boot service, a new Lambda function used by > 1 team |
| New persistent data store | Adding DynamoDB table, RDS instance, ElasticSearch cluster, Redis for primary storage |
| New cloud provider | First use of Azure or GCP resources in an AWS-primary estate |
| Technology not on Approved List | Any language, framework, or SaaS tool with no existing approved usage in the estate |
| Cross-domain data sharing | A service in Domain A reading data owned by Domain B |
| Change to shared infrastructure | Changes to the VPC, Transit Gateway, API Gateway stage, or shared Route 53 zone |
| Data residency or sovereignty change | Moving data outside the approved region set (e.g., eu-west-1 to us-east-1 for EU data) |
| Vendor lock-in increase | Adopting a proprietary API where a vendor-neutral alternative exists and was not formally evaluated |

### Submitting for ARB Review

1. Author an RFC using the `write-rfc.prompt.md` task prompt
2. Open a pull request targeting `architecture/rfcs/` — do not merge without an ARB decision
3. Tag `@arb-reviewer` and `@enterprise-architect` in the PR description
4. ARB meeting cadence: fortnightly; P1 incidents can trigger an emergency ARB within 24 hours
5. Record the outcome in `docs/architecture/decisions/governance-register.md`

See `.github/agents/arb-reviewer.agent.md` and `.github/agents/enterprise-architect.agent.md`.

---

## ADR — Architecture Decision Record

### Mandatory Format

Every ADR file must be at `docs/decisions/ADR-{NNN}-{slug}.md` and contain all six sections:

```markdown
# ADR-{NNN}: {Title — present tense, e.g., "Use DynamoDB for session storage"}

Date: YYYY-MM-DD
Status: Proposed | Accepted | Deprecated | Superseded by ADR-{NNN}
Deciders: {Comma-separated names or teams}
Tags: {storage | compute | integration | security | ml | platform}

## Context

What is the problem or opportunity forcing a decision? Include constraints, non-functional
requirements, and any relevant business context. Minimum 3 sentences.

## Decision

State the decision as an active sentence: "We will use X because Y."
Be specific — name the exact technology, version, configuration, or pattern chosen.

## Consequences

### Positive
- {Concrete benefit with measurable expectation where possible}

### Negative
- {Known cost, risk, or limitation that is accepted}

### Neutral
- {Side effects that are neither clearly positive nor negative}

## Alternatives Considered

| Option | Pros | Cons | Reason Rejected |
|--------|------|------|----------------|
| Option A | ... | ... | ... |
| Option B | ... | ... | ... |

## References

- RFC: {link if applicable}
- Spike: {link to spike branch or document}
- ARB Decision: {link to governance register entry}
- External: {standards body reference, vendor documentation}
```

### ADR Status Transitions

```
Proposed → Accepted     (after ARB approval or team decision for non-ARB changes)
Proposed → Rejected     (ARB or team rejects; reasons must be recorded in Context)
Accepted → Deprecated   (technology end-of-life or superseded without a direct replacement)
Accepted → Superseded by ADR-{NNN}  (replaced by a new decision)
```

Never delete an ADR — only transition its status. The record of rejected paths is as valuable as accepted ones.

---

## RFC — Request for Comments

RFCs are required for any change that affects > 1 team or that the ARB must review. RFCs live at `architecture/rfcs/RFC-{NNN}-{slug}.md`.

### Mandatory RFC Sections

```markdown
# RFC-{NNN}: {Title}

Author: {name}
Date: YYYY-MM-DD
Status: Draft | Under Review | Approved | Rejected | Withdrawn
ARB Review Required: Yes | No
Related ADRs: ADR-{NNN}, ...

## Problem Statement

Describe the specific problem being solved. Include evidence: error rates, latency p99 data,
cost data, or incident references. Do not describe the solution here.

## Motivation

Why does this problem need to be solved now? What is the cost of inaction?

## Proposed Solution

Describe the solution precisely. Include:
- Architecture diagrams (as Mermaid or PlantUML inline)
- Configuration examples
- API contracts (OpenAPI snippet or JSON Schema)
- Data model changes (ERD or table definitions)

## Alternatives Considered

For each rejected alternative, state: what it was, why it was considered, why it was rejected.

## Drawbacks

What are the known downsides or risks of the proposed solution?

## Success Criteria

| Criterion | Measurement | Target |
|-----------|------------|--------|
| Latency   | p99 API response time | < 200ms |
| Availability | Error rate | < 0.1% |

## Migration Plan

Step-by-step migration path including rollback procedure. Identify any dual-write periods,
feature flags, or traffic shifting strategy.

## Rollout Plan

Phase 1: {scope, date, owners}
Phase 2: {scope, date, owners}
Rollback trigger: {specific condition that triggers rollback}
```

---

## Technology Lifecycle Classification

All technologies used in the estate are classified using a four-tier model. The authoritative list is at `docs/architecture/tech-radar.md`.

| Tier | Definition | Action Required |
|------|-----------|----------------|
| **Invest** | Actively adopt and grow usage; long-term support confirmed | Default choice when applicable |
| **Tolerate** | Acceptable for existing use; no new projects should start here | Plan migration to Invest-tier alternative; track in tech-debt register |
| **Migrate** | Active migration away; new features must not use | Create migration ADR; assign sprint allocation |
| **Eliminate** | No new usage; existing usage must be removed by sunset date | Hard gate in CI: flag usage in code scan |

### Current Classification Examples (update `tech-radar.md` as the source of truth)

| Technology | Tier | Notes |
|-----------|------|-------|
| Java 21 (LTS) | Invest | Target runtime for all JVM services |
| Spring Boot 3.x | Invest | Standard application framework |
| AWS CDK v2 (TypeScript) | Invest | Standard IaC |
| Python 3.12 | Invest | Standard for ML and data workloads |
| Java 11 | Tolerate | Existing services; migrate to Java 21 by Q4 2025 |
| Spring Boot 2.x | Migrate | Spring Boot 2 OSS support ended Nov 2023 |
| Java 8 | Eliminate | No new usage; sunset existing by Q2 2025 |
| Apache Commons Collections 3.x | Eliminate | Known CVEs; replace with Guava or JDK equivalents |

---

## Architecture Fitness Functions

Fitness functions are automated checks that prevent architectural drift. They run in CI.

### ArchUnit Rules (Java — `src/test/java/architecture/ArchitectureTest.java`)

```java
// No cross-schema SQL joins — services must not query across domain boundaries
@ArchTest
static final ArchRule no_cross_schema_joins = noClasses()
    .that().resideInAPackage("..repository..")
    .should().dependOnClassesThat()
    .resideInAPackage("..repository..") // different bounded context
    .because("Cross-domain queries couple bounded contexts — use APIs or events instead");

// No circular module dependencies
@ArchTest
static final ArchRule no_cycles = slices()
    .matching("com.enterprise.(*)..").should().beFreeOfCycles();

// Domain layer must not depend on infrastructure
@ArchTest
static final ArchRule domain_independence = noClasses()
    .that().resideInAPackage("..domain..")
    .should().dependOnClassesThat()
    .resideInAnyPackage("..infrastructure..", "..adapter..");

// Max efferent coupling per class: 20 dependencies
@ArchTest
static final ArchRule max_coupling = classes()
    .should(haveMaximumNumberOfDependencies(20));
```

### Coupling Thresholds

| Metric | Warning | Fail |
|--------|---------|------|
| Efferent coupling per class | > 15 | > 20 |
| Package cyclomatic complexity | > 10 | > 15 |
| Inter-service synchronous call chains | > 3 hops | > 5 hops |
| Shared database tables across services | Any | Any |

---

## Technical Radar Format

The radar at `docs/architecture/tech-radar.md` uses four quadrants: Languages & Frameworks, Platforms, Tools, Techniques.

Each entry follows this format:

```markdown
### {Technology Name} — {Invest | Tolerate | Migrate | Eliminate}

**Quadrant:** Languages & Frameworks | Platforms | Tools | Techniques
**Since:** YYYY-MM-DD
**Owner:** {team or person responsible}
**Context:** One paragraph — why this classification, what triggered any status change.
**Migration Path:** (only for Migrate/Eliminate) Link to ADR or migration guide.
```

---

## Governance Decision Register

`docs/architecture/decisions/governance-register.md` records every ARB decision. Format:

```markdown
| Date | RFC/ADR | Title | Decision | Deciders | Conditions |
|------|---------|-------|----------|----------|-----------|
| 2024-11-01 | RFC-014 | Adopt Kafka for event streaming | Approved | ARB Quorum | Must use MSK; Confluent Schema Registry required |
| 2024-09-15 | RFC-011 | Add GCP Vertex AI | Rejected | ARB Quorum | AWS Bedrock covers use case; revisit if gap proven |
```

---

## What Constitutes a Material Architectural Change

A change is **material** if it meets any of the following criteria. Material changes require an ADR at minimum; many also require ARB review per the trigger table above.

- Changes the public API contract of a service used by > 1 consumer
- Changes the data model of a shared entity in a way that is not backward compatible
- Introduces a new dependency on an external vendor API with data egress
- Changes the authentication or authorization model for any user-facing system
- Increases the blast radius of a failure (e.g., moves from stateless to stateful, adds shared mutable state)
- Changes the deployment topology (e.g., single-region to multi-region, monolith to microservice)
- Affects data retention, data classification, or PII handling

---

## Anti-Patterns — Flag These

| Pattern | Action |
|---------|--------|
| ADR with no Alternatives Considered section | Incomplete — request alternatives before approving |
| RFC with no rollback plan | Block — rollback is mandatory for all RFC-gated changes |
| Technology in Migrate/Eliminate tier introduced in new service | Block — raise ARB exception request |
| Cross-domain database join in production code | Flag with ArchUnit rule violation; require RFC |
| Architecture decision made in a Slack thread with no ADR | Create ADR from Slack thread content; date = decision date |
