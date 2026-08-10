# FinOps Capability Pack

Cloud cost engineering across the FinOps lifecycle — **Inform → Optimize → Operate**.

| Provides | |
|---|---|
| Agents | `finops-engineer` |
| Standards | `finops-standard` |
| Resolves when | `cloud.finops: true` (opt-in) — also add via `capability_packs.include: [finops]` |
| Depends on | `core`, `aws` |

Brings engineering rigour to spend: cost visibility + allocation (tagging), rightsizing, commitment
discounts (RI/Savings Plans), budgets + anomaly detection, storage lifecycle, egress reduction, and unit
economics. Every recommendation ties to a number (before → after, annualised saving, confidence) and
never trades away the SLO to save money.

See [`standards/finops-standard.md`](standards/finops-standard.md).
