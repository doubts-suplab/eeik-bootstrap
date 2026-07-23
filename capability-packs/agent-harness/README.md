# Agent Harness Capability Pack

**Version:** 1.0 | **Category:** Core | **Owner:** EEIK

---

## Purpose

Activates conformance to **HALO** (the **agent-harness protocol**) — a generic, enterprise-grade agent runtime — for any
AI/agent project. Rather than re-implementing agent execution (typed envelope, confidence gate, tool registry,
orchestration, audit) per product, projects conform to one protocol and consume one reference runtime.

Selected when `ai.enabled: true`, `ai.pattern` is agentic, or `project_type: agent-platform`.

---

## What's Included

| Area | Content |
|------|---------|
| Standards | `agent-harness-protocol` (conformance summary → full spec in the runtime repo) |
| Knowledge | Ecosystem positioning + reference-runtime links |
| Reference runtime | [`doubts-suplab/agent-harness`](https://github.com/doubts-suplab/agent-harness) |

This pack ships no agents/commands of its own — it activates a **runtime standard**. Agent *design* standards
come from `ai-engineering-pack`; governance controls from `governance-pack` (both dependencies).

---

## Dependencies

```yaml
- ai-engineering-pack   # agent/prompt/evaluation design standards
- governance-pack       # confidence gate, audit, human-in-the-loop controls
```

---

## Worked example — apex-sdlc

[`apex-sdlc`](https://github.com/doubts-suplab/apex-sdlc) is the reference consumer of this pack. It maps its
SDLC personas and phases directly onto the harness authority model — a concrete template for any project
activating this pack:

| SDLC phase | Persona | Phase agent | Harness authority | Governed outcome |
|---|---|---|---|---|
| Requirements | Business Analyst | `RequirementsAgent` | SUGGEST | always → human review |
| Architecture | Architect | `ArchitectureAgent` | SUGGEST | always → human review |
| Development | Developer | `PRReviewerAgent` | ALERT | auto-enforced advisory when confident |
| Testing | QA Engineer | `QAAnalystAgent` | SUGGEST | always → human review |
| CI/CD | Tech Lead | `ReleaseEngineerAgent` | RATE_LIMIT | auto-enforced release when green |
| Docs | Developer | `TechWriterAgent` | SUGGEST | always → human review |
| Governance | CISO | `ComplianceOfficerAgent` | BLOCK | auto-block only at ≥ 0.95; else human review |

The key lesson for pack adopters: **make "AI drafts, humans approve" a property of the authority ladder, not a
convention.** SUGGEST-authority agents can never auto-enforce (harness gate rule G-5), so those phases always
route to a human — no app-level code re-implements that guarantee. See apex's
[reference journey](https://github.com/doubts-suplab/apex-sdlc/blob/main/examples/reference-project/README.md)
for a runnable end-to-end walk of one project through all seven phases, and its `docs/personas.md` for the
persona↔phase↔agent catalog.

---

## Conformance

See [`standards/agent-harness-protocol.md`](standards/agent-harness-protocol.md) and the reference runtime's
`docs/spec/harness-protocol.md` §9 Conformance Checklist.
