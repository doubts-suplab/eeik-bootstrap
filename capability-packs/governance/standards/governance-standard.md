# Governance Standard

**Pack:** governance-pack | **Version:** 1.0

---

## Review Requirements by Profile

| Review Type | basic | standard | regulated | enterprise |
|-------------|-------|----------|-----------|------------|
| Architecture Review | — | ✅ | ✅ | ✅ |
| Security Review | — | ✅ | ✅ | ✅ |
| ARB Gate | — | — | — | ✅ |
| Production Readiness Review | — | — | ✅ | ✅ |
| AI Governance Review | — | — | ✅* | ✅* |
| Compliance Review | — | — | ✅ | ✅ |

*If AI is enabled.

---

## Review Principles

1. **Reviews are gates, not rubber stamps.** A review finding must be resolved or formally accepted with documented rationale before the gate closes.
2. **Findings are classified.** CRITICAL = blocks release. MAJOR = must fix this sprint. MINOR = fix within quarter. SUGGESTION = nice to have.
3. **Decisions are recorded.** Every governance decision (APPROVE / APPROVE WITH CONDITIONS / REJECT) is logged with date, reviewer, and rationale.
4. **Reviews are repeatable.** Use the templates in this pack so every reviewer asks the same questions.
5. **Governance shifts left.** Architecture review happens before implementation. Security review happens before deployment. Not after.

---

## Review Lifecycle

```
1. Author submits for review (with required artifacts)
          ↓
2. Reviewer conducts review (uses checklist)
          ↓
3. Findings produced (CRITICAL / MAJOR / MINOR)
          ↓
4. Author resolves findings
          ↓
5. Reviewer verifies resolution
          ↓
6. Gate closes: APPROVE or APPROVE WITH CONDITIONS
          ↓
7. Decision logged in decisions.md
```

---

## Artifacts Required for Each Review

| Review | Required Artifacts |
|--------|-------------------|
| Architecture Review | Solution architecture doc, ADRs, NFRs |
| Security Review | Architecture doc, IAM design, data classification |
| PRR | Runbook, SLOs, alerts, DR plan, rollback procedure |
| AI Governance | Agent definitions, model card, evaluation results |
| Compliance | Data flow diagram, DPA, processing records |
