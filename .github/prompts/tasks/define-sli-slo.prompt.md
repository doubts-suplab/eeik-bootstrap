# Define SLI/SLO

Define Service Level Indicators and Service Level Objectives for the following service:

**Service:** $SERVICE_NAME
**Description:** $SERVICE_DESCRIPTION

## Instructions

1. Identify the user-visible reliability dimensions for this service
2. Define SLIs that accurately measure user experience (not internal metrics)
3. Set SLO targets based on business requirements and historical data
4. Calculate the error budget
5. Define burn rate alert thresholds
6. Produce the error budget policy

See `.github/instructions/sre.instructions.md` for SRE standards.

## Output Format

```markdown
## SLO Definition: {Service Name}

### Service Description
{Brief description of what the service does and who depends on it}

### SLIs

| SLI Name | What It Measures | Good Event Definition | Measurement Source |
|----------|----------------|----------------------|-------------------|
| Availability | HTTP error rate | Request is not a 5xx response | ALB access logs |
| Latency | p99 response time | Request completes in < {N}ms | CloudWatch Target Response Time |
| {custom} | {description} | {good event} | {source} |

### SLOs

| SLI | Target | Window | Measurement Method |
|-----|--------|--------|-------------------|
| Availability | {99.x}% | 30-day rolling | {CloudWatch metric} |
| Latency | {x}% of requests < {N}ms | 30-day rolling | {CloudWatch metric} |

### Error Budgets

| SLO | Monthly Budget (minutes) | Weekly Budget (minutes) |
|-----|------------------------|------------------------|
| Availability | {calculation} | {calculation} |

### Burn Rate Alerts

| Alert | Rate | Window | Severity | Action |
|-------|------|--------|---------|--------|
| Fast burn | {14.4×} | 1 hour | P2 | Page on-call |
| Slow burn | {6×} | 6 hours | P3 | Slack alert |

### Error Budget Policy

| Budget Remaining | Action |
|-----------------|--------|
| > 50% | Normal feature velocity |
| 25–50% | Reliability review required for new features |
| < 25% | Feature freeze; reliability work only |
| 0% | Executive escalation; post-mortem required |
```
