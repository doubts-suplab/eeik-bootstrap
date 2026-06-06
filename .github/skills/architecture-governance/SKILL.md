# Architecture Governance Skill

## Trigger

Use this skill for Architecture Review Board (ARB) gate reviews, technology standard compliance checks, and architectural design validation before build begins.

## What This Skill Does

1. Reviews the proposed design against enterprise architecture standards
2. Validates technology choices against the approved technology list
3. Assesses security, scalability, and operational readiness
4. Produces a formal ARB Recommendation Report (Approved / Approved with Conditions / Rejected)
5. Classifies findings by severity: BLOCKER / MAJOR / MINOR / ADVISORY

## Inputs Required

- Proposed system or feature design (class diagram, component description, or ADR)
- Non-functional requirements: throughput, latency, availability, data classification
- Bounded context: which domain this belongs to
- Technology choices: frameworks, databases, messaging systems
- Integration points: upstream and downstream dependencies

## Outputs Produced

- ARB Recommendation Report with structured findings table
- Conditions for approval (if applicable)
- Required remediations with severity classification
- Architecture compliance checklist

## Standards Applied

See `.github/instructions/architecture-governance.instructions.md` and `.github/instructions/enterprise-architecture.instructions.md`

## Related Agents

- `arb-reviewer` — Claude Code agent for formal ARB reviews
- `architect` — for design guidance and ADR authoring
- `enterprise-architect` — for TOGAF-aligned enterprise architecture
