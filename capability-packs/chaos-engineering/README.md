# Chaos Engineering Capability Pack

Controlled resilience experimentation — prove the system meets its reliability target under failure.

| Provides | |
|---|---|
| Agents | `chaos-engineer` |
| Standards | `chaos-engineering-standard` |
| Resolves when | `observability.chaos_engineering: true` (opt-in) — also add via `capability_packs.include: [chaos-engineering]` |
| Depends on | `core` |

Hypothesis-driven fault-injection experiments with a defined steady state, a minimal blast radius, and
an abort condition — plus GameDays that exercise the incident-response path, not just the system. Pairs
with SRE (SLOs / error budgets) and incident management.

See [`standards/chaos-engineering-standard.md`](standards/chaos-engineering-standard.md).
