# /memory-update — Update Project Memory Files

Update the relevant `.claude/memory/` files with new context from the current session.

## Usage

```
/memory-update "Added Redis caching to OrderService with 5-minute TTL for order status lookups"
/memory-update "Decided to use Kafka for cross-context events instead of REST callbacks — see ADR-003"
/memory-update "Identified N+1 query issue in OrderRepository.findByCustomerId — added to tech-debt.md as TD-005"
```

## What This Command Does

1. Parses the description to identify which memory files are affected
2. Updates the relevant files:
   - `decisions.md` — for architectural decisions
   - `patterns.md` — for new approved patterns or identified anti-patterns
   - `tech-debt.md` — for new tech debt items
   - `constraints.md` — for new constraints discovered
   - `rejected-approaches.md` — for approaches tried and rejected
   - `project-context.md` — for environment or service changes
   - `rca-tracker.md` — for incident or corrective action updates
3. Commits the changes with a `chore(memory):` conventional commit message

## When to Use

- After a significant architectural decision is made
- After a tech debt item is identified or resolved
- After a new pattern is established or an anti-pattern is discovered
- After a new constraint is added to the project
- After an incident is resolved and corrective actions are assigned
- After discovering an approach that was tried and doesn't work

## Memory File Guide

| What changed | File to update |
|-------------|----------------|
| Architectural decision | `decisions.md` |
| New implementation pattern | `patterns.md` |
| Identified anti-pattern | `patterns.md` |
| New tech debt | `tech-debt.md` |
| Tech debt resolved | `tech-debt.md` |
| New hard constraint | `constraints.md` |
| Approach tried and rejected | `rejected-approaches.md` |
| Environment URL or resource name changed | `project-context.md` |
| Incident or corrective action | `rca-tracker.md` |

## Notes

- Keep entries concise — memory files are read at session start; large files slow initialisation
- Each file should be under 500 lines — split into sub-files if a category grows very large
- Date all entries with `YYYY-MM-DD` format
