# Agent Evaluation Standard

**Pack:** ai-engineering-pack | **Version:** 1.0

---

## Evaluation Requirements

Every agent must have an evaluation dataset before production deployment.

| Requirement | Minimum |
|-------------|---------|
| Benchmark inputs | 20 curated test cases |
| Coverage | Happy path, edge cases, adversarial inputs |
| Metrics defined | At least 2 measurable metrics |
| Baseline established | Run evaluation before any prompt change |
| Regression threshold | < 5% drop in primary metric triggers review |

---

## Standard Metrics

| Metric | What It Measures | Tool |
|--------|----------------|------|
| Task completion rate | % of tasks completed correctly end-to-end | Manual review |
| Hallucination rate | % of responses containing fabricated facts | LLM-as-judge |
| Format compliance | % of responses in correct output format | Schema validation |
| Latency p99 | Time to complete at 99th percentile | CloudWatch |
| Tool call accuracy | % of tool calls correct (right tool, right args) | Trace analysis |
| Escalation rate | % of requests correctly escalated to human | Manual review |

---

## Evaluation Dataset Format

```yaml
# agents/evaluation/{agent-name}/dataset.yaml
agent: {agent-name}
version: 1.0

cases:
  - id: TC-001
    description: Happy path — valid input produces expected output
    input:
      {input fields}
    expected_output:
      {expected fields}
    pass_criteria: exact_match | contains | schema_valid

  - id: TC-002
    description: Edge case — empty input
    input: {}
    expected_behaviour: escalate_to_human
    pass_criteria: escalation_triggered
```

---

## Running Evaluations

Evaluations must be run:
- Before any prompt version change
- Before production deployment
- Weekly in production (spot check 10 cases)
- After any model version change
