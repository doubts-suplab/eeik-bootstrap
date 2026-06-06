# Game Day Exercise Workflow

Design and execute a game day (chaos engineering) exercise to test system reliability.

**Service:** $SERVICE_NAME
**Hypothesis:** $RELIABILITY_HYPOTHESIS (e.g., "The system degrades gracefully when the database is unavailable")

## Workflow Steps

### Step 1 — Hypothesis Definition
Define what you are testing:
- [ ] State the hypothesis clearly: "When {failure condition}, the system will {expected behaviour}"
- [ ] Define the blast radius: what is the maximum acceptable impact on users?
- [ ] Define the abort condition: what observation triggers immediate halt?

### Step 2 — Steady State Baseline
Activate the `sre-engineer` agent to document the steady state:
- [ ] Current SLI values: availability, latency p99, error rate
- [ ] CloudWatch dashboard baseline screenshot
- [ ] Confirm monitoring and alerting are working before the exercise

### Step 3 — Exercise Design

| Component | Failure Type | Injection Method | Duration |
|-----------|-------------|-----------------|---------|
| {service} | {dependency down / latency / error} | {AWS FIS / manual} | {N minutes} |

### Step 4 — Safety Controls
Before running:
- [ ] All team members know the abort signal
- [ ] On-call engineer is available and briefed
- [ ] Rollback plan confirmed: how to restore normal state immediately
- [ ] Customer-facing impact is bounded and acceptable

### Step 5 — Execute
1. Record start time
2. Inject the failure condition
3. Observe system behaviour against the hypothesis
4. Monitor SLI values and error rates continuously
5. Abort if steady state SLO is breached beyond acceptable threshold

### Step 6 — Observe & Analyse
- [ ] Did alerts fire as expected?
- [ ] Did the system degrade gracefully (or fail completely)?
- [ ] What was the user-visible impact?
- [ ] Was the hypothesis confirmed or refuted?

### Step 7 — Produce Report
```markdown
## Game Day Report: {Exercise Name}
**Date:** {YYYY-MM-DD}
**Duration:** {N minutes}
**Hypothesis:** {stated hypothesis}
**Result:** Confirmed / Refuted

### Observations
{What happened during the exercise}

### Findings
{What reliability gaps were discovered}

### Actions
| Action | Owner | Target Date |
|--------|-------|------------|
```

## Output

Game day plan, execution log, and findings report with actionable reliability improvements.
