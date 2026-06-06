# /review — Run Full PR Review Checklist

Run a comprehensive code review across security, performance, and quality dimensions.

## Usage

```
/review
/review src/main/java/com/example/order/
```

## What This Command Does

1. Activates the `code-reviewer` agent (and calls `security-auditor` and `performance-engineer` for specialist checks)
2. Reviews all changed files in the current diff or the specified path
3. Classifies findings by severity: `[BLOCKER]`, `[MAJOR]`, `[MINOR]`, `[NIT]`
4. Checks against all Golden Rules from `CLAUDE.md`
5. Produces a structured review report

## Review Dimensions

| Dimension | What Is Checked |
|-----------|----------------|
| **Correctness** | Logic errors, edge cases, null safety, error handling |
| **Security** | OWASP Top 10, injection risks, hardcoded secrets, authentication gaps |
| **Performance** | N+1 queries, unbounded result sets, missing indexes, blocking I/O |
| **Standards** | Golden Rules compliance, coding standards from `.claude/standards/` |
| **Tests** | Coverage adequacy, test quality, missing edge case tests |
| **Design** | SOLID violations, DDD boundary violations, anti-patterns from `.claude/memory/patterns.md` |

## Severity Definitions

- **[BLOCKER]** — Must be fixed before merge. Security vulnerability, data loss risk, or production regression.
- **[MAJOR]** — Should be fixed before merge. Significant quality, performance, or maintainability impact.
- **[MINOR]** — Should be addressed in this PR if possible; otherwise, raise a tech debt ticket.
- **[NIT]** — Style or preference; fix only if time permits.

## Output Format

```
## PR Review Report

### Summary
{N} BLOCKER / {N} MAJOR / {N} MINOR / {N} NIT

### Findings
[BLOCKER] `src/.../OrderService.java:42` — SQL built via string concatenation; SQL injection risk.
[MAJOR] `src/.../OrderController.java:89` — No input validation on `customerId` parameter.
[MINOR] `src/.../OrderMapper.java:15` — Missing Javadoc on public method.
[NIT] `src/.../OrderDto.java:5` — Field ordering inconsistent with team convention.

### Checklist
- [ ] All Golden Rules satisfied
- [ ] No hardcoded secrets
- [ ] All new public methods have Javadoc
- [ ] Tests cover the changed code paths
```
