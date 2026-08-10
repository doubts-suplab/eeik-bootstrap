# Chaos & Resilience Engineering Standard

**Applies To:** Services with a reliability target (an SLO / error budget) to defend.
**Pairs with:** SRE (SLIs/SLOs/error budgets) and incident management (GameDays exercise the response).

> Chaos engineering is **controlled experimentation to build confidence**, not breaking things for
> sport. Every experiment has a hypothesis, a bounded blast radius, and an abort condition.

---

## Golden Rules (Chaos)

| Rule | Implementation |
|---|---|
| Steady state is a business/SLI metric | e.g. successful-checkouts/min — not CPU% |
| Every experiment has a hypothesis | "Fault F holds steady state via mitigation M"; the run tries to disprove it |
| Blast radius starts minimal | One instance / one AZ / a small % of traffic before widening |
| Abort condition is defined first | An automated halt when steady state breaks past threshold |
| Rollback is ready before you start | You can stop and restore in seconds |
| Run with humans watching | Business hours, staffed on-call, error budget available |
| GameDays test the response | Runbook, alerting, and on-call are under test, not just the system |
| Findings get an owner | Each disproved hypothesis → a resilience-backlog item |

## Designing an experiment

```yaml
# Experiment template
steady_state:
  metric: checkout_success_rate
  healthy: ">= 99% over a 5-min window"
hypothesis: >
  When the payments dependency adds 2s p99 latency, checkout success stays >= 99% because the client
  timeout (1s) + circuit breaker fail fast to the "retry later" path.
fault:
  type: latency
  target: payments-service
  inject: "+2000ms p99, 10% of calls"
blast_radius: "staging; 5% of synthetic traffic"
abort_condition: "checkout_success_rate < 95% for 60s → halt + rollback"
rollback: "remove fault injection (automated)"
observe: [checkout_success_rate, circuit_breaker_state, error_budget_burn]
```

## Fault types to cover

- **Latency** — slow dependencies (the most common real-world failure).
- **Error** — a dependency returns 5xx / throttles.
- **Resource** — CPU/memory/disk/connection-pool exhaustion.
- **Infrastructure** — instance loss, **AZ loss**, node drain.
- **Network** — partition, DNS failure, packet loss.
- **State** — clock skew, cache wipe, leader loss.

## GameDays

- Schedule a facilitated exercise with a scenario the team hasn't rehearsed.
- The **incident-response path is under test**: does the alert fire, is the runbook correct, does on-call
  know the escalation? Capture gaps as action items with owners.
- Blameless review afterward — the system and the process are the subjects, not the people.

## Anti-Patterns

| Anti-Pattern | Correct Alternative |
|---|---|
| "Chaos" with no hypothesis | Define steady state + a falsifiable hypothesis first |
| No abort condition / rollback | Automated halt + instant rollback agreed before the run |
| Starting in prod at full scale | Smallest blast radius first; widen only after it holds |
| Running with no error budget | Experiment while budget exists; otherwise fix reliability first |
| Testing the system but not the humans | GameDays exercise alerting, runbook, and on-call too |

## Enforcement

- Experiments are reviewed for a valid hypothesis, blast radius, abort condition, and rollback before
  they run — an experiment without these is not approved.
- Prod experiments require explicit sign-off and available error budget.
- Findings land in the resilience backlog with owners; recurring themes are promoted to design standards.
- The `chaos-engineer` agent produces experiment designs and GameDay plans.
