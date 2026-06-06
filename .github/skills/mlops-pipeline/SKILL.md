# MLOps Pipeline Skill

## Trigger

Use this skill when building or reviewing MLOps pipelines, model registries, drift monitoring configurations, or automated retraining workflows.

## What This Skill Does

1. Designs the end-to-end ML pipeline: data ingestion → feature engineering → training → evaluation → registration → deployment → monitoring
2. Implements SageMaker Pipelines with quality gate steps
3. Configures SageMaker Model Monitor for data and model quality drift
4. Sets up model versioning and approval workflows in SageMaker Model Registry
5. Designs automated retraining triggers based on drift alerts
6. Assesses MLOps maturity level (0–2) and identifies gaps

## Inputs Required

- Current ML workflow description (how models are trained and deployed today)
- AWS environment and SageMaker configuration
- Model type and output (classifier, regressor, LLM)
- Data sources and feature store availability
- Monitoring requirements (drift detection, bias monitoring)

## Outputs Produced

- SageMaker Pipeline definition (Python SDK)
- Model Monitor configuration (schedule, baseline, thresholds)
- Model Registry approval workflow design
- Retraining trigger architecture
- MLOps maturity assessment with gap analysis

## MLOps Maturity Targets

| Level | Definition | Target |
|-------|-----------|--------|
| 0 — Manual | Ad-hoc training, manual deployment | — |
| 1 — ML Pipeline | Automated training; manual deployment | Minimum |
| 2 — Full MLOps | Automated training + deployment + monitoring + retraining | Target for all production ML |

## Standards Applied

See `.github/instructions/mlops-pipeline.instructions.md` and `.github/instructions/aws-data-ml-ai.instructions.md`

## Related Agents

- `mlops-engineer` — Claude Code agent for MLOps platform work
- `ml-engineer` — for training pipeline implementation
- `data-scientist` — for model development and evaluation
