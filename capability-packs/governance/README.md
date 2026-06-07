# Governance Capability Pack

**Version:** 1.0 | **Category:** Core | **Owner:** EEIK

---

## Purpose

Enterprise governance intelligence: architecture reviews, security reviews, AI governance, production readiness reviews, and compliance controls. Selected for all projects — governance profile determines which reviews apply.

---

## Governance Profiles

| Profile | Applies To | Reviews |
|---------|-----------|---------|
| `basic` | PoC, internal tools | None mandatory |
| `standard` | Internal products | Architecture + Security |
| `regulated` | Insurance, Banking, Healthcare | Architecture + Security + PRR + Compliance |
| `enterprise` | Enterprise platforms | All reviews + ARB gate |

---

## What's Included

| Area | Content |
|------|---------|
| Agents | architecture-reviewer, security-reviewer, production-readiness-reviewer, compliance-reviewer |
| Standards | governance-standard, review-standard, compliance-standard |
| Templates | review-checklist.md.template, risk-register.md.template, decision-log.md.template |
| Commands | run-review, run-prr, run-ai-review, run-compliance-check |
| Workflows | governance-review.yaml, production-readiness.yaml |
| Knowledge | compliance-frameworks.md |

---

## Dependencies

```yaml
- architecture-pack  # architecture-principles used in reviews
```
