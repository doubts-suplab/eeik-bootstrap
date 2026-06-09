# eeik-managed pack=delivery
# Branching Standard

**Applies To:** All projects using Git  
**Model:** GitHub Flow (simplified) with environment-locked branches

---

## Branch Model

```
main              ← production-ready; protected; requires PR + review
  │
  ├── feature/TICKET-123-short-description   ← feature work
  ├── fix/TICKET-456-bug-description         ← bug fixes
  ├── chore/update-dependencies              ← housekeeping
  └── hotfix/TICKET-789-critical-fix         ← emergency production fixes
```

---

## Rules

| Rule | Detail |
|------|--------|
| `main` is always deployable | Never commit a broken state to main |
| Feature branches from `main` | Always branch from the latest `main` |
| Short-lived branches | Feature branches merged within 1 sprint |
| No long-lived branches | No `develop`, `release/1.x` — use feature flags instead |
| PR required for `main` | No direct pushes — enforced by branch protection |
| Minimum 1 review | 2 reviewers for regulated/enterprise |
| Squash merge | Clean history on `main` — one commit per feature |

---

## Naming Convention

```
feature/PROJ-123-add-order-cancellation
fix/PROJ-456-null-pointer-in-payment-service
chore/upgrade-spring-boot-3-3
hotfix/PROJ-789-payment-double-charge
```

---

## CI/CD per Branch

| Branch Pattern | CI Trigger | Deployment |
|----------------|-----------|-----------|
| Any branch | Build + test + lint + security scan | None |
| `main` | Build + test + scan + CDK synth | Deploy to dev (auto) |
| Manual | — | Deploy to staging (manual approval) |
| Manual | — | Deploy to prod (2 approvals) |

---

## Feature Flags for Long-Running Features

When a feature takes > 1 sprint, use feature flags instead of long-lived branches:

```java
@Value("${feature.new-payment-flow:false}")
private boolean useNewPaymentFlow;

public PaymentResult processPayment(PaymentRequest request) {
    return useNewPaymentFlow
        ? newPaymentService.process(request)
        : legacyPaymentService.process(request);
}
```

Flag managed in AWS AppConfig or SSM Parameter Store — toggle without redeployment.
