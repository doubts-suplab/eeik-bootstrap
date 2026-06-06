# ML Model Delivery Workflow

Deliver a machine learning model from experiment to production.

**Model:** $MODEL_NAME
**Business Use Case:** $USE_CASE

## Workflow Steps

### Step 1 — Experiment Validation
Activate the `data-scientist` agent to validate the experiment:
- [ ] Evaluation metric appropriate for the business problem
- [ ] Train/validation/test split is sound (no data leakage)
- [ ] Performance reported with confidence intervals, not just point estimates
- [ ] Baseline comparison (what's the model being compared against?)
- [ ] Fairness metrics assessed where relevant

### Step 2 — Production Readiness Assessment
Activate the `ml-engineer` agent to assess production readiness:
- [ ] Feature engineering pipeline is reproducible (same features at train and serve time)
- [ ] Inference latency meets the production SLO requirement
- [ ] Memory and compute requirements are within infrastructure budget
- [ ] Model artefact size is manageable for serving

### Step 3 — AI Governance Review
Activate the `ai-governance-officer` agent:
- [ ] EU AI Act risk classification
- [ ] Model card produced
- [ ] AI risk assessment completed
- [ ] GDPR Article 22 assessment (if applicable)

### Step 4 — MLOps Pipeline Setup
Activate the `mlops-engineer` agent to configure:
- [ ] SageMaker Pipeline for reproducible training
- [ ] Model registered in SageMaker Model Registry
- [ ] Approval workflow configured
- [ ] SageMaker Model Monitor configured (data drift, model quality, bias)
- [ ] Automated retraining trigger defined

### Step 5 — Deployment
- [ ] Champion/challenger deployment configured (shadow mode first)
- [ ] Traffic split plan: 10% → 50% → 100%
- [ ] Rollback mechanism confirmed (revert to previous model version)
- [ ] Monitoring dashboard ready before go-live

### Step 6 — Post-Deployment Review (30 days)
- [ ] Drift monitoring: no significant data or model quality drift
- [ ] Fairness metrics stable
- [ ] Business KPI impact assessed
- [ ] Retraining schedule confirmed

## Output

Validated model, MLOps pipeline, governance documentation, and production monitoring configuration.
