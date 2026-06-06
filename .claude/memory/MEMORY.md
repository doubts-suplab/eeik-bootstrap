# Claude Code Memory Index

This directory provides persistent context that Claude Code loads at the start of each session. Files here persist across sessions and survive agent handoffs.

## Files in This Directory

| File | Purpose | Updated By |
|------|---------|------------|
| `project-context.md` | Service inventory, environments, auth patterns, key resource names | Team / `/memory-update` |
| `domain-glossary.md` | Business terminology definitions for this project's domain | Team / Business Analyst |
| `decisions.md` | Architecture Decision Log — what was decided and why | Architect / ARB Reviewer |
| `constraints.md` | Hard technical and business constraints that must never be violated | Tech Lead / Architect |
| `patterns.md` | Approved implementation patterns and anti-patterns to avoid | Tech Lead |
| `tech-debt.md` | Tech debt register with priority and target sprint | Tech Lead / Team |
| `rca-tracker.md` | Incident/RCA status log with corrective action tracking | RCA Agent / Ops |
| `session-log.md` | Auto-updated by the `on-stop.sh` hook — files changed each session | Automatic |
| `rejected-approaches.md` | Things tried and rejected — prevents re-trying failed ideas | Team |

## How to Update

Use the `/memory-update` slash command or invoke the relevant agent:

```
/memory-update "Added Redis caching layer to OrderService — see decisions.md"
```

Or directly edit the relevant file and commit.

## Loading Behaviour

Claude Code reads these files automatically at the start of each session when they exist. Keep each file focused and under 500 lines — large files slow session initialisation.

## Bootstrap Note

This is a **seed template**. When adopting this repository:

1. Replace all placeholder values with project-specific content
2. Remove or update any entries marked with `<!-- TODO: fill in -->`
3. Delete this notice from `MEMORY.md` once the files are populated
