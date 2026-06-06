---
applyTo: "**/mlops/**/*.py,**/sagemaker/**/*.py,**/pipelines/**/*.py,**/*.pipeline.py"
---

# MLOps Pipeline Standards

## Model Lifecycle

- All models must pass through: Experiment → Registered → Approved → Deployed → Monitored → Deprecated
- Never deploy a model that has not been registered and approved in the Model Registry
- Record with every model version: training data version, evaluation metrics, training date, approver
- Define model expiry policy — retrain or retire models older than the data freshness threshold

## Pipeline Design

- Use SageMaker Pipelines or equivalent for all production ML workflows — not ad-hoc scripts
- Every pipeline must be reproducible: same inputs → same outputs (deterministic data processing and fixed random seeds)
- Implement quality gates as pipeline steps — do not promote models that fail the quality gate
- Version all pipeline definitions alongside the model code

## Feature Engineering

- Ensure training/serving feature parity — feature computation must be identical in both contexts
- Store feature transformation logic in a versioned artifact alongside the model
- Implement point-in-time correctness for all join operations in training data preparation
- Validate feature schema before training and serving — schema drift is a silent failure mode

## Model Monitoring

- Implement data quality monitoring: detect input feature distribution shift
- Implement model quality monitoring: track prediction accuracy against ground truth labels
- Define alert thresholds for each monitored metric — alerts must route to the responsible team
- Implement bias monitoring for all models with demographic inputs or user-facing decisions

## Retraining

- Define trigger conditions for automated retraining: drift threshold breach, scheduled cadence, new data volume
- Automated retraining pipelines must still require human approval before production deployment
- Test retraining pipeline on a schedule even when drift has not been detected — prevents pipeline rot
- Implement champion/challenger deployment for new model versions — do not flip 100% traffic immediately

## Governance

- Produce a model card for every model version before production approval
- Maintain audit log: who approved the model, on what data, with what metrics, when
- Never delete training data for a model still in production — it is the audit evidence
- Classify all models by EU AI Act risk tier; high-risk models require additional governance controls
