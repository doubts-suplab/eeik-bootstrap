# /run-prr — Production Readiness Review

Activate `production-readiness-reviewer` and conduct a full PRR.

## Usage
```
/run-prr
/run-prr order-service
```

## What This Command Does
1. Reads runbook, SLO definitions, and monitoring configuration
2. Runs the full PRR checklist (observability, SLOs, operations, deployment, DR, security)
3. Produces READY / CONDITIONALLY READY / NOT READY verdict
4. Lists blocking items that must be resolved before go-live
