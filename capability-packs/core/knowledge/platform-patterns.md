# Platform-Wide Patterns

Patterns that apply across all technology stacks and domains in EEIK-managed projects.

---

## Pattern: Memory File Usage

**Context:** Claude Code sessions lose context between sessions.

**Solution:** Read `.claude/memory/` at the start of each session. Update with `/memory-update` after significant changes. The memory files act as a persistent project brain.

```
Session starts
    ↓
Claude reads: project-context.md, decisions.md, constraints.md, patterns.md
    ↓
Work proceeds with full project context
    ↓
Significant change made
    ↓
/memory-update "what changed"
    ↓
Memory files updated for next session
```

---

## Pattern: Conventional Commit → Changelog

**Context:** Teams need release notes without manual writing.

**Solution:** Conventional Commits (`feat`, `fix`, `chore`, etc.) enable automated changelog generation with `standard-version` or `semantic-release`.

```
feat(orders): add order cancellation endpoint   → appears in CHANGELOG.md
fix(payments): handle null amount               → appears in CHANGELOG.md
chore(deps): upgrade spring boot                → NOT in changelog (chore filtered)
```

---

## Pattern: Feature Branch → PR → Review → Merge

**Context:** All changes need code review before production.

**Solution:** Enforce branch protection on `main`. Every change via PR. `/review` runs the review workflow.

```
feature/TICKET-123-add-cancellation
    ↓
PR opened → /review runs automatically
    ↓
BLOCKER → REQUEST CHANGES
No BLOCKER → APPROVE (1 reviewer minimum)
    ↓
Merge to main → deploy-dev.yaml triggers
    ↓
Successful → promote to staging
```

---

## Pattern: Agent Specialisation Over Generalism

**Context:** A single large-context prompt for all tasks produces mediocre results.

**Solution:** Use specialist agents for each domain. The `architect` handles design. The `java-developer` handles implementation. The `security-auditor` handles security.

**Rule:** If an agent's description doesn't match the task, don't use it — find or generate the right specialist.

---

## Pattern: ADR-Before-Implementation

**Context:** Architectural decisions get made in Slack or verbal conversations and are forgotten.

**Solution:** Any decision that will be hard to change later gets an ADR BEFORE implementation begins. The `/create-adr` command takes 10 minutes and prevents weeks of rework.

**Trigger condition:** "This decision will affect multiple services, or we cannot easily reverse it" → write the ADR first.
