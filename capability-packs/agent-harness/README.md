# Agent Harness Capability Pack

**Version:** 1.0 | **Category:** Core | **Owner:** EEIK

---

## Purpose

Activates conformance to the **agent-harness protocol** — a generic, enterprise-grade agent runtime — for any
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

## Conformance

See [`standards/agent-harness-protocol.md`](standards/agent-harness-protocol.md) and the reference runtime's
`docs/spec/harness-protocol.md` §9 Conformance Checklist.
