# /create-architecture — Design a Solution Architecture

Activate the `solution-architect` agent and produce a full solution architecture document for a new service or system.

## Usage
```
/create-architecture "Payment processing service with fraud detection and PCI-DSS compliance"
```

## What This Command Does
1. Activates `solution-architect` agent
2. Elicits bounded context, NFRs, and integration requirements
3. Produces a solution architecture document using `templates/solution-architecture.md.template`
4. Identifies ADRs needed and drafts the first one
5. Flags risks and open questions

## Output
- `docs/architecture/{service-name}-architecture.md`
- `docs/decisions/ADR-001-{first-key-decision}.md`
