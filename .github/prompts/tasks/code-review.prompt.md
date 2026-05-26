---
mode: "ask"
description: "Perform a structured code review of the selected code block or file"
---

## Objective

Perform a structured code review of the provided code, producing findings labelled by severity. This task prompt gives a quick review for a single class or code block. For a full PR review pipeline (including security and performance scans), use the `pr-review-workflow.prompt.md` workflow instead.

---

## Instructions to Copilot

Review the provided code across these dimensions in order:

1. **Correctness** — logic errors, NPE risks, incorrect null handling, off-by-one errors, broken transactions
2. **Security** — SQL injection, missing input validation, exposed secrets, missing `@PreAuthorize`
3. **Performance** — N+1 queries, unbounded queries, object creation in loops, unclosed resources
4. **Architecture** — domain logic in controllers/repositories, violated SOLID principles, wrong layer responsibility
5. **Quality** — missing SLF4J logging on exception paths, raw types, empty catch blocks, `System.out.println`
6. **Style** — Google Java Style compliance, naming conventions, missing Javadoc
7. **Tests** — are tests present? Do they cover edge cases?

Use these severity labels:
- `[BLOCKER]` — Must fix before merge
- `[MAJOR]` — Should fix before merge
- `[MINOR]` — Fix in follow-up
- `[NIT]` — Optional polish

---

## Input

Paste the code to review directly in your message, or reference the open file.

---

## Output

```markdown
## Code Review — {ClassName or description}

### Summary
<2-3 sentences: what the code does, overall quality, merge readiness>

### Findings

#### [BLOCKER] <title>
**Location:** line X
**Issue:** <specific description>
**Fix:** <what to do>

#### [MAJOR] ...
#### [MINOR] ...
#### [NIT] ...

### Positive Notes
<What is done well — 1-3 bullets>

### Verdict
[ ] Ready to merge  [ ] Merge after blockers resolved  [ ] Significant rework needed
```

---

## Quality Gates

- [ ] Every finding references a specific line or code pattern — no vague observations
- [ ] Every blocker and major includes a concrete fix description
- [ ] Positive aspects noted (constructive review, not just criticism)
- [ ] Verdict clearly stated
