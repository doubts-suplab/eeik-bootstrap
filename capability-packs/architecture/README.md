# Architecture Capability Pack

**Version:** 1.0  
**Category:** Core  
**Owner:** EEIK

---

## Purpose

Provides enterprise architecture intelligence for solution design, architecture reviews, ADR authoring, NFR analysis, integration design, and modernisation planning.

This pack is selected automatically when any of the following manifest fields are present:
- `architecture.style` (any value)
- `technology.backend.language: java`
- `project.project_type: enterprise-platform`

---

## What's Included

| Area | Files |
|------|-------|
| Agents | solution-architect, enterprise-architect, arb-reviewer, modernization-architect |
| Standards | architecture-principles, nfr-standard, integration-standard, event-driven-standard |
| Templates | solution-architecture.md, adr-template.md, rfc-template.md |
| Commands | create-architecture, review-architecture, create-adr, create-rfc |
| Workflows | architecture-design.yaml, architecture-review.yaml |
| Knowledge | reference-architectures.md, architecture-patterns.md |

---

## Quick Start

```
# Design a new solution
/create-architecture "Payment processing service with fraud detection"

# Review an existing design
/review-architecture

# Record an architectural decision
/adr "Use event sourcing for order state management"
```

---

## Agents

| Agent | Trigger |
|-------|---------|
| `solution-architect` | New service design, bounded context modelling, API contract design |
| `enterprise-architect` | Cross-domain design, capability mapping, transformation roadmaps |
| `arb-reviewer` | Architecture Review Board gate reviews, standards compliance |
| `modernization-architect` | Legacy system analysis, strangler fig planning, migration waves |

---

## Dependencies

This pack has no external pack dependencies. It is a foundational pack.
