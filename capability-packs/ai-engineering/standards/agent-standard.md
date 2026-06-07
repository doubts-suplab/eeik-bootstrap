# Agent Design Standard

**Pack:** ai-engineering-pack | **Version:** 1.0

Every agent built with EEIK must satisfy these requirements before deployment.

---

## Required Agent Definition Fields

```yaml
name: {agent-name}              # kebab-case, unique
purpose: {one sentence}         # what does this agent do?
domain: {bounded context}       # which business area?
version: 1.0

responsibilities:               # what it does
  - {responsibility}

inputs:                         # what it consumes
  - name: {input}
    type: {type}
    required: true|false

outputs:                        # what it produces
  - name: {output}
    type: {type}

constraints:                    # what it must never do
  - {constraint}

tools_allowed:                  # explicit tool whitelist
  - {tool}

escalation_strategy:            # when to hand off to human
  condition: {when}
  action: {what}

failure_handling:               # what to do on error
  on_error: {action}
  max_retries: {n}

evaluation_strategy:
  metrics: [{metric}]
  benchmark_dataset: {path}
```

---

## Agent Quality Gates

Every agent must pass these before production:

| Gate | Requirement |
|------|------------|
| Purpose clarity | One-sentence purpose understood by non-technical reviewer |
| Constraint definition | At least 3 explicit constraints (what it must NOT do) |
| Tool whitelist | Only listed tools can be used — no open-ended tool access |
| Failure handling | Explicit on_error behaviour defined |
| Evaluation | At least 10 benchmark inputs/outputs in evaluation dataset |
| Escalation | Human escalation path defined |
| Governance | AI governance review completed for regulated domains |

---

## Anti-Patterns

| Anti-Pattern | Risk | Alternative |
|-------------|------|-------------|
| Unconstrained tool access | Data exfiltration, unintended side effects | Explicit tool whitelist |
| No failure handling | Silent failures, corrupted state | on_error strategy required |
| Vague purpose | Scope creep, misuse | Single-sentence purpose |
| No evaluation data | Undetectable regression | Benchmark dataset required |
| God agent (does everything) | Unpredictable, ungovernatable | Single responsibility per agent |
| PII in agent memory | Data breach risk | PII-free memory design |
