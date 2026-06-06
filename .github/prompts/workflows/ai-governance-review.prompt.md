# AI Governance Review Workflow

Conduct a full AI governance review for the following AI/ML system before production deployment.

**System:** $SYSTEM_NAME
**Deployment Target:** $ENVIRONMENT

## Workflow Steps

### Step 1 — System Classification
Activate the `ai-governance-officer` agent to:
- Classify the system by EU AI Act risk tier
- Identify GDPR Article 22 exposure (automated decision-making)
- Determine required governance controls based on risk tier

### Step 2 — Model Card Production
Produce a complete model card covering:
- [ ] Intended use and out-of-scope use
- [ ] Training data provenance, date range, and known biases
- [ ] Evaluation metrics including fairness metrics by demographic group
- [ ] Known limitations and failure modes
- [ ] Ethical considerations

### Step 3 — Risk Assessment
Conduct the AI risk assessment:
- [ ] Identify top 5 risks with likelihood × impact ratings
- [ ] Define required controls for each risk
- [ ] Assess residual risk after controls are applied

### Step 4 — Technical Controls Review
Verify technical implementation:
- [ ] Output guardrails tested (Bedrock Guardrails or equivalent)
- [ ] Audit logging of all AI decisions implemented
- [ ] Human-in-the-loop gates for high-stakes decisions
- [ ] Monitoring configured: data drift, model quality, bias drift

### Step 5 — Governance Sign-Off
- [ ] Model card reviewed and signed off
- [ ] Risk register accepted by accountable business owner
- [ ] Monitoring thresholds and alert routing confirmed
- [ ] Post-deployment review date scheduled (30 days for new deployments)

### Step 6 — Documentation
- [ ] Model card committed to `docs/model-cards/`
- [ ] Risk register entry in `docs/ai-risk-register.md`
- [ ] Governance approval recorded with date and approver

## Output

Completed model card, risk assessment, and governance checklist ready for production sign-off.
