---
applyTo: "**/slo/**/*.md,**/runbooks/**/*.md,**/*.slo.yml,**/monitoring/**"
---

# SRE Practice Standards

## SLI/SLO Definition

- Define SLIs that directly measure user experience — not internal implementation metrics
- Every production service must have at minimum: availability SLO and latency SLO
- Express SLOs as percentages over a rolling 30-day window
- Measure SLIs from the user's perspective (ALB access logs, synthetic probes) — not internal health checks

## Error Budgets

- Calculate error budget as `(1 - SLO_target) × window_duration`
- Define an error budget policy with three states: healthy (>50%), at-risk (25–50%), exhausted (<25%)
- Implement fast-burn and slow-burn alerts:
  - Fast burn: consuming 5% of monthly budget in 1 hour → P2 alert
  - Slow burn: consuming 10% of monthly budget in 6 hours → P3 alert
- Error budget exhaustion triggers feature freeze — reliability work takes priority

## Monitoring Requirements

- Every service must emit the four golden signals: latency, traffic, errors, saturation
- P99 latency is the minimum latency SLI — P50 alone is insufficient
- All CloudWatch alarms must have a linked runbook in the alarm description
- Set `TreatMissingData: BREACHING` on availability alarms — missing data is not healthy

## Toil Management

- Define toil as: manual, repetitive, reactive, scales with service growth, provides no enduring value
- Track toil time per week per engineer — target <50% of working time on toil
- Automate toil with Lambda, Step Functions, or shell automation within one quarter of identification
- Measure toil elimination: record time saved per week after automation

## Reliability Patterns

- Implement retry with exponential backoff and jitter for all external calls
- Use circuit breakers for dependencies with >1% error rate sustained over 5 minutes
- Implement timeouts on all outbound calls — no blocking call without a deadline
- Design for graceful degradation: define what the service does when each dependency fails

## On-Call

- Every P1/P2 alert must be actionable — if an alert fires and there is no action to take, remove or tune it
- On-call runbooks must be executable in under 15 minutes by any on-call engineer
- Conduct game day exercises quarterly to test incident response procedures
- Measure and improve MTTR and MTTD as team-level SRE KPIs
