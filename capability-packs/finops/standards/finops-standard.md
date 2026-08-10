# Cloud FinOps Standard

**Applies To:** Any cloud workload with a bill someone has to answer for.
**Framework:** FinOps Foundation lifecycle — **Inform → Optimize → Operate**.

> Cost is a non-functional requirement. It is designed, measured, and reviewed — not discovered at
> month-end.

---

## Golden Rules (FinOps)

| Rule | Implementation |
|---|---|
| Everything is allocatable | Mandatory tags: `team`, `env`, `product`, `cost-center`; untagged spend is a defect |
| Delete waste before committing | Rightsize + remove orphans *before* buying RIs/Savings Plans |
| Commit to the floor, burst on-demand | Cover the stable baseline with commitments; keep the peak flexible/spot |
| Every resource has an owner | A tag maps spend to a team that can act on it |
| Budgets + anomaly alerts, always on | Alert per allocation dimension; catch runaways in hours, not at invoice time |
| Storage has a lifecycle | Hot → infrequent → archive → delete; no infinite-retention-by-default |
| Cost is a unit metric | Track `$/request`, `$/tenant`, `$/GB` — spend judged against value delivered |
| SLO wins ties | Rightsize to the reliability target's headroom; never below it to save money |

## Inform — allocation & visibility

- Enforce a **tagging taxonomy** at provisioning time (IaC-level, not after the fact). A resource that
  can't be created with required tags fails the pipeline.
- Build **showback** (visibility) first; graduate to **chargeback** (billing) only once tags are trusted.
- Break the bill down by team/env/product monthly; the largest *untagged* slice is the first bug to fix.

## Optimize — ranked, evidence-based

Rank every opportunity by **annualised saving × confidence ÷ effort**:

1. **Kill waste** — orphaned volumes/snapshots/IPs, idle load balancers, dev environments running 24/7.
2. **Rightsize** — from p95 utilisation, not peak-of-peak; leave the SLO's headroom.
3. **Schedule** — stop non-prod outside business hours (a ~65% saving on those hours).
4. **Storage class & lifecycle** — move cold objects down the tiers; compress/expire logs.
5. **Cut data transfer** — co-locate chatty services (avoid cross-AZ), cache egress, use private endpoints.
6. **Commitment discounts** — only on a proven, stable baseline, and only after 1–5.

```text
# WRONG: buy a 3-year RI for a fleet that includes idle + oversized instances → you commit to waste.
# RIGHT: delete idle → rightsize → observe the stable floor for 2–4 weeks → commit to that floor.
```

## Operate — make it continuous

- **Budgets** per allocation dimension with alert thresholds (e.g. 50/80/100% of forecast).
- **Anomaly detection** on spend, routed to the owning team, not a shared inbox.
- **Cost in CI** — flag PRs that add expensive resources (NAT gateway, always-on GPU, cross-region
  replication) so the trade-off is a conscious decision at review time.
- **Monthly review** against **unit-cost** trends — rising absolute spend is fine if `$/request` is
  falling; falling spend with rising unit cost is the real regression.

## Anti-Patterns

| Anti-Pattern | Correct Alternative |
|---|---|
| Optimising before allocating | Fix tagging first — you can't manage what you can't attribute |
| Buying RIs/Savings Plans to "save money" fast | Delete + rightsize first; commit only to the proven floor |
| Judging cost in absolutes | Track unit economics — cost per unit of value |
| Cost review once a quarter | Continuous budgets + anomaly alerts + CI cost checks |
| Cutting resources until the SLO breaks | Rightsize to the reliability target's headroom |

## Enforcement

- IaC policy checks reject untagged resources (the tagging taxonomy is a required input).
- A CI cost step comments the estimated monthly delta of a PR's infrastructure changes.
- Budgets + anomaly alerts run in the account; breaches page the owning team.
- The `finops-engineer` agent produces the ranked review; ARB signs off commitment purchases.
