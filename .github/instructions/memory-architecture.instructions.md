---
applyTo: "**/.claude/memory/**,**/memory/**/*.md"
---

# Memory Architecture Standards

## Claude Code Memory Files

Memory files in `.claude/memory/` are loaded automatically at session start. They provide persistent context that survives across sessions and agent handoffs.

## File Responsibilities

| File | Responsibility | Max Size |
|------|---------------|----------|
| `project-context.md` | Live project facts: environments, services, auth | 200 lines |
| `domain-glossary.md` | Business term definitions for this domain | 300 lines |
| `decisions.md` | Lightweight decision log (full ADRs in `docs/decisions/`) | 300 lines |
| `constraints.md` | Non-negotiable technical and business constraints | 200 lines |
| `patterns.md` | Approved patterns and forbidden anti-patterns | 400 lines |
| `tech-debt.md` | Prioritised tech debt register | 300 lines |
| `rca-tracker.md` | Incident and RCA status | 300 lines |
| `session-log.md` | Auto-updated by on-stop hook | 200 lines |
| `rejected-approaches.md` | Tried-and-rejected solutions | 200 lines |

## Update Protocol

- Update memory files whenever a significant decision, constraint, or pattern is established
- Use the `/memory-update` slash command to trigger structured updates
- Always date entries: `YYYY-MM-DD`
- Memory files are committed to source control — treat them as living documentation

## Quality Rules

- Keep entries concise — each memory file is read in full at every session start
- Remove stale entries promptly — outdated constraints or patterns cause agent confusion
- Do not put implementation code in memory files — reference file paths instead
- Do not duplicate content that belongs in `docs/` or source code

## Session Log Automation

The `on-stop.sh` hook auto-updates `session-log.md` with:
- The last git commit on the branch
- A list of files modified in the session

This provides continuity across sessions without manual effort.

## Agent-Specific Memory

For projects using multiple Claude Code sessions in parallel (e.g., separate frontend and backend sessions), maintain separate memory context per domain bounded context if the concerns are sufficiently different. Do not create per-agent memory files — memory is team/project level.
