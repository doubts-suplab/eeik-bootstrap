# /rca — Open a Root Cause Analysis Workflow

Open an RCA workflow with 5-Whys template for a resolved production incident.

## Usage

```
/rca "Payment service returned 502s for 45 minutes on 2026-06-06 between 14:30 and 15:15 UTC"
```

## What This Command Does

1. Activates the `rca-agent` specialist
2. Creates a new RCA document in `docs/rca/` (or `docs/incidents/`)
3. Walks through the structured 5-Whys analysis
4. Identifies contributing factors and produces corrective actions
5. Updates `.claude/memory/rca-tracker.md` with the new incident and open actions

## Pre-Requisites

Provide as much context as possible:
- The incident ID (if declared via `/incident`)
- The incident timeline (from `.claude/memory/rca-tracker.md` or the incident channel)
- Affected services and their CloudWatch logs or Datadog traces
- The resolution action that fixed the problem

## Output

The command produces:
1. A complete RCA document at `docs/rca/INCIDENT-{NNN}.md`
2. An entry in `.claude/memory/rca-tracker.md`
3. A list of SMART corrective actions with suggested owners and target dates

## 5-Whys Process

The RCA agent will guide through:
1. **Symptom** — the observable problem (e.g., "502 errors from ALB")
2. **Why 1** — immediate technical cause
3. **Why 2** — underlying configuration or code cause
4. **Why 3** — process or architectural cause
5. **Why 4/5** — systemic root cause

## Notes

- RCAs must be blameless — the goal is systemic improvement, not individual accountability
- Corrective actions must have an owner and a target date to be actionable
- P1 RCAs must be published within 48 hours of resolution
- Update corrective action status in `rca-tracker.md` as actions are completed
