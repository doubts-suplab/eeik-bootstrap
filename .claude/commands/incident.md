# /incident — Declare and Coordinate an Incident

Declare a production incident and activate the incident management workflow.

## Usage

```
/incident "severity: P1, service: payment-service, symptom: 502 errors on checkout, customer impact: users cannot complete purchases"
```

## What This Command Does

1. Activates the `incident-handler` agent
2. Declares the incident with severity, affected services, and impact statement
3. Creates an incident record in `.claude/memory/rca-tracker.md`
4. Assigns response roles (Incident Commander, Technical Lead, Communications Lead, Scribe)
5. Opens the incident timeline and tracks all actions
6. Manages stakeholder communication cadence

## Severity Criteria

| Severity | Definition | Response SLA | Examples |
|----------|-----------|-------------|---------|
| P1 | Complete service outage or data loss risk | Immediate, 24/7 | Payment processing down, data corruption detected |
| P2 | Major feature degradation, significant user impact | < 30 min, on-call | Checkout slow (>10s), 20% error rate |
| P3 | Minor feature degradation, workaround available | < 4h, business hours | Reports delayed, non-critical feature unavailable |
| P4 | Cosmetic or low-impact issue | Next business day | UI glitch, non-critical alert firing |

## During the Incident

The `incident-handler` agent will:
- Maintain a live, time-stamped timeline
- Drive the 15-minute investigation cycle
- Coordinate parallel investigation workstreams
- Draft stakeholder communications for review
- Drive toward mitigation, then resolution

## After Resolution

Run `/rca "incident details"` to initiate the post-incident Root Cause Analysis.

## Key Principle

**Restore service first. Establish facts second.**

During a live incident, do not attempt full root cause analysis — focus on mitigation. The RCA happens after the incident is resolved.
