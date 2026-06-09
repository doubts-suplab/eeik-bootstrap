# Estimation Standard

**Applies To:** All projects and delivery models  
**Owned By:** `estimator` agent  
**Used By:** Sprint planning, release planning, ARB submissions

---

## Formula

```
Human Days = Σ Raw Hours ÷ 6.4
```

Where `6.4 = 8 hours/day × 80% efficiency`

The 80% efficiency factor accounts for: meetings, PR review cycles, context-switching, environment issues, code review iterations, and interruptions.

---

## Confidence Ranges

| Scenario | Multiplier | When to Use |
|----------|------------|-------------|
| P50 (Likely) | ×1.0 | Sprint planning baseline |
| P80 (Conservative) | ×1.3 | Sprint commitment |
| P90 (Pessimistic) | ×1.6 | Release planning buffer |

**Always present P50 and P80. Add P90 for release planning or regulated delivery.**

---

## Raw Hours Reference Table

| Task Type | Simple | Moderate | Complex |
|-----------|--------|----------|---------|
| REST API endpoint (Spring Boot) | 2–4h | 4–8h | 8–16h |
| Domain model + aggregate | 2–4h | 4–8h | 8–16h |
| Repository layer (JPA) | 1–2h | 2–4h | 4–8h |
| Unit test class | 1–2h | 2–4h | 4–6h |
| Integration test (Testcontainers) | 2–4h | 4–6h | 6–10h |
| CDK stack (new resource) | 2–4h | 4–8h | 8–20h |
| Database migration script | 1–2h | 2–4h | 4–8h |
| Angular component (standalone) | 2–4h | 4–8h | 8–12h |
| FastAPI endpoint (Python) | 1–3h | 3–6h | 6–12h |
| LangGraph agent node | 2–4h | 4–8h | 8–16h |
| CI/CD pipeline change | 1–2h | 2–4h | 4–8h |
| Architecture document (ADR) | 1–2h | 2–4h | 4–8h |
| Security review | 2–4h | 4–8h | 8–16h |
| Performance investigation | 2–4h | 4–8h | 8–24h |

---

## Estimation Output Format

```
Feature: {feature description}

Task Breakdown:
┌────────────────────────────────────────┬───────────┬─────────────┐
│ Task                                   │ Complexity│ Raw Hours   │
├────────────────────────────────────────┼───────────┼─────────────┤
│ Domain model                           │ Moderate  │ 4h          │
│ Repository layer                       │ Simple    │ 2h          │
│ Use case + service                     │ Moderate  │ 6h          │
│ REST controller                        │ Simple    │ 3h          │
│ Unit tests                             │ Moderate  │ 4h          │
│ Integration tests                      │ Moderate  │ 5h          │
│ CDK resource (if new)                  │ Simple    │ 2h          │
├────────────────────────────────────────┼───────────┼─────────────┤
│ Total Raw Hours                        │           │ 26h         │
└────────────────────────────────────────┴───────────┴─────────────┘

Human Days = 26h ÷ 6.4 = 4.1 days

Confidence:
  P50 (Likely):       4.1 days
  P80 (Conservative): 5.3 days
  P90 (Pessimistic):  6.6 days

Assumptions:
  - Developer is familiar with the domain
  - No external dependency blockers
  - DB schema changes are non-breaking

Risks:
  - If {risk}: add {n} days buffer
```
