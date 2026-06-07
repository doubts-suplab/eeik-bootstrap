# Review Execution Standard

**Pack:** governance-pack | **Version:** 1.0

---

## Reviewer Responsibilities

- Read all submitted artifacts before the review
- Use the review checklist — do not skip items
- Classify every finding (CRITICAL / MAJOR / MINOR / SUGGESTION)
- Provide actionable remediation for every CRITICAL and MAJOR finding
- Issue a clear verdict: APPROVE / APPROVE WITH CONDITIONS / DEFER / REJECT
- Log the decision with date and rationale

---

## Finding Classification

| Severity | Definition | Remediation SLA |
|----------|-----------|-----------------|
| CRITICAL | Security vulnerability, data breach risk, or compliance violation | Before any deployment |
| MAJOR | Significant reliability, performance, or standards compliance risk | Before next sprint |
| MINOR | Quality, maintainability, or observability gap | Within quarter |
| SUGGESTION | Optional improvement with clear benefit | Backlog |

---

## Review Report Structure

Every review must produce a report with:

```markdown
# {Review Type}: {Service/System Name}

**Date:** {date}
**Reviewer:** {name/agent}
**Artifact Version:** {version}

## Verdict
APPROVE / APPROVE WITH CONDITIONS / DEFER / REJECT

## Findings

### CRITICAL
- {finding}: {remediation required}

### MAJOR
- {finding}: {recommendation}

### MINOR
- {finding}: {suggestion}

## Conditions (if APPROVE WITH CONDITIONS)
- {condition}: due {date}

## Sign-off
Reviewer: {name} | Date: {date}
```

---

## Review Anti-Patterns

- ❌ Approving without reading all artifacts
- ❌ "LGTM" with no findings on a complex system
- ❌ Findings without remediation guidance
- ❌ Verbal approvals with no written record
- ❌ Review conducted after deployment
