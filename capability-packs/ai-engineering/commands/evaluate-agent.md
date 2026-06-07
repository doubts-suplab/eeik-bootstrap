# /evaluate-agent — Run Agent Evaluation

Run the evaluation dataset for an agent and produce a quality report.

## Usage
```
/evaluate-agent claims-settlement-agent
/evaluate-agent agents/evaluation/claims-settlement-agent/dataset.yaml
```

## What This Command Does
1. Reads the evaluation dataset
2. Runs each test case through the agent
3. Scores against expected outputs using defined pass criteria
4. Produces: pass rate, metric scores, failure analysis
5. Compares against baseline (if available)
6. Flags regressions (> 5% drop in primary metric)
