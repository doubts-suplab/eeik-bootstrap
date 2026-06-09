# Concepts

Core EEIK concepts and design philosophy.

---

## Contents

| Document | Concept |
|----------|---------|
| [engineering-operating-system.md](engineering-operating-system.md) | What EEIK is and what problem it solves |
| [capability-lifecycle.md](capability-lifecycle.md) | How capability packs are selected and composed |
| [repository-lifecycle.md](repository-lifecycle.md) | How repositories are generated from manifests |
| [agent-lifecycle.md](agent-lifecycle.md) | How agents are selected, generated, and invoked |
| [knowledge-lifecycle.md](knowledge-lifecycle.md) | How organizational intelligence accumulates across projects |

---

## The Core Ideas

### Manifest-Driven Design

Every EEIK project starts with a `project-manifest.yaml` — a structured declaration of what a project is: its domain, technology stack, architecture style, cloud platform, and governance requirements.

The manifest is the single source of truth. Everything else — capability selection, repository scaffolding, agent generation, governance gates — is derived from it.

### Capability Packs

Engineering intelligence is separated into reusable, composable packs. A capability pack contains agents, standards, templates, commands, workflows, and knowledge relevant to one technology domain or engineering concern.

When the manifest says `backend.language: java21`, the Java and Architecture capability packs are automatically selected. A project only gets the intelligence relevant to what it is actually building.

### Agent Factory

Rather than maintaining hundreds of static agents, EEIK stores a small set of archetypal blueprints (architect, engineer, reviewer, auditor, planner, specialist) and composes project-specific agents at generation time. A claims-triage-specialist generated for an insurance project is different from a generic specialist, because it is composed with domain context from the insurance capability pack.

### Knowledge Feedback Loop

Every project produces learnings — incidents, ADRs, patterns, retrospective lessons. The Knowledge Generator extracts these back into the EEIK knowledge repository. Each subsequent project inherits a richer base of organizational intelligence.

```
Project runs → decisions captured → knowledge extracted → next project smarter
```

### Governance as Code

Governance requirements are not a checklist you fill in after the fact. They are derived from the manifest (`governance.profile: regulated`) and baked into the generated repository: review checklists, CI gates, mandatory approvals, compliance templates. A regulated project cannot accidentally skip its compliance review because the CI pipeline will not pass without it.
