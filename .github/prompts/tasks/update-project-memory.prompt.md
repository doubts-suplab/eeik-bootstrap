# Update Project Memory

Update the relevant `.claude/memory/` files with the following context from this session:

**What Changed:** $WHAT_CHANGED

## Instructions

1. Parse the description to identify which memory files need updating
2. Update each affected file with the new information
3. Date all new entries as `{YYYY-MM-DD}`
4. Keep entries concise — memory files are read at session start
5. Commit with `chore(memory): {description}` conventional commit message

## File Selection Guide

| What changed | File to update |
|-------------|----------------|
| New architectural decision | `.claude/memory/decisions.md` |
| New implementation pattern established | `.claude/memory/patterns.md` |
| Anti-pattern discovered | `.claude/memory/patterns.md` |
| New tech debt identified | `.claude/memory/tech-debt.md` |
| Tech debt resolved | `.claude/memory/tech-debt.md` |
| New hard constraint discovered | `.claude/memory/constraints.md` |
| Approach tried and failed | `.claude/memory/rejected-approaches.md` |
| Environment or service change | `.claude/memory/project-context.md` |
| Incident or corrective action | `.claude/memory/rca-tracker.md` |
| New domain term defined | `.claude/memory/domain-glossary.md` |

## Quality Rules

- Do not duplicate content that belongs in `docs/` or source code
- Reference file paths for implementation details — do not paste code into memory files
- Each file must stay under 500 lines — if a file grows large, split into sub-files
- Remove stale entries immediately — outdated constraints cause agent confusion

## Checklist

- [ ] Correct file(s) identified for the change
- [ ] Entry is dated `YYYY-MM-DD`
- [ ] Entry is concise (< 10 lines for a single decision or pattern)
- [ ] No credentials, personal data, or environment-specific secrets in memory files
- [ ] Changes committed with `chore(memory):` prefix
