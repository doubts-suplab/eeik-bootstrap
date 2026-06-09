# EEIK Knowledge Repository

The organizational intelligence layer of EEIK.

Knowledge here is **not static documentation** — it is the accumulated learning from real projects that feeds back into the platform, making every subsequent project smarter.

## Knowledge Principle

```
Project runs
    ↓
Decisions, incidents, patterns captured
    ↓
/capture-lesson | /create-adr | /capture-incident
    ↓
Knowledge Repository
    ↓
Next project inherits intelligence
```

## Structure

```
knowledge/
├── patterns/               ← Approved implementation patterns with examples
├── anti-patterns/          ← Known failure modes to avoid
├── event-catalog/          ← Canonical domain event definitions
├── reference-architectures/← Proven architectural blueprints
├── adr-repository/         ← Cross-project ADR library
├── lessons-learned/        ← Project retrospective learnings
└── incident-repository/    ← Post-mortem learnings and runbooks
```

## Commands

| Command                        | Purpose                                               |
|--------------------------------|-------------------------------------------------------|
| `/create-adr "title"`         | Scaffold a new ADR in `docs/decisions/`               |
| `/create-rfc "title"`         | Scaffold a Request for Comments document              |
| `/capture-lesson "learning"`  | Extract a lesson into the lessons-learned repository  |
| `/capture-incident "summary"` | Extract RCA findings into the incident repository     |
| `/memory-update "what changed"` | Update `.claude/memory/` files with new context     |

## Contribution Rules

Every project must contribute back:

1. **ADRs** — one per significant architectural decision
2. **Lessons Learned** — one entry per sprint retrospective
3. **Incident Learnings** — one entry per P1/P2 incident resolved
4. **Pattern candidates** — when a novel solution is approved by the team
