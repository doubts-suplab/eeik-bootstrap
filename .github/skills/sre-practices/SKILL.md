# SRE Practices Skill

## Trigger

Use this skill when defining SLIs/SLOs, setting up error budget tracking, implementing reliability patterns, or conducting game day exercises.

## What This Skill Does

1. Defines Service Level Indicators (SLIs) that measure user-visible reliability
2. Sets Service Level Objectives (SLOs) with appropriate targets and windows
3. Calculates error budgets and defines burn rate alert thresholds
4. Designs error budget policy (when to freeze features vs. proceed)
5. Identifies toil and designs automation to eliminate it
6. Plans game day exercises to test reliability under failure conditions

## Inputs Required

- Service description: what it does, who uses it, what they depend on
- Current monitoring setup (CloudWatch, Datadog, etc.)
- Business availability requirements (customer SLA, regulatory)
- Historical incident data (if available)
- Current toil inventory (if available)

## Outputs Produced

- SLO definition document with SLI measurement methodology
- Error budget calculation and policy
- CloudWatch alarm configuration for burn rate alerts
- Toil reduction prioritised backlog
- Game day exercise plan
- On-call runbook improvements

## SLO Quick Reference

```
Error Budget = (1 - SLO_target) × window
Example: 99.9% over 30 days = 43.8 minutes of allowed downtime

Fast-burn alert: consuming 5% of monthly budget in 1 hour
Slow-burn alert: consuming 10% of monthly budget in 6 hours
```

## Standards Applied

See `.github/instructions/sre.instructions.md` and `.github/instructions/incident-ops.instructions.md`

## Related Agents

- `sre-engineer` — Claude Code agent for SRE practice implementation
- `ops-engineer` — for CloudWatch monitoring and runbook authoring
- `incident-handler` — for incident response
- `rca-agent` — for post-incident analysis
