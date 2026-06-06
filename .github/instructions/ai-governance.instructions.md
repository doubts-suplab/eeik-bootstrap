---
applyTo: "**/ai-models/**, **/model-cards/**, **/bedrock/**, **/sagemaker/**"
description: "EU AI Act risk classification, ISO 42001 controls, model card authoring, audit trail requirements, and AI acceptable use policy for enterprise AI systems."
---

# AI Governance — Copilot Instructions

> Applied automatically when working with AI model code, model cards, Bedrock, or SageMaker files. Loaded alongside copilot-instructions.md.

---

## EU AI Act Risk Tier Classification

Before deploying any AI system, classify it using the following tier table. Record the classification in the system's model card.

| Tier | Definition | Examples | Controls Required |
|------|-----------|---------|------------------|
| **Unacceptable Risk** | Banned — must not be deployed | Real-time biometric surveillance in public spaces; social scoring systems; subliminal manipulation | Do not build |
| **High Risk** | Directly affects fundamental rights or safety | Credit scoring, employment screening, medical diagnosis, law enforcement, educational assessment, critical infrastructure control | Full HITL, audit trail, bias evaluation, model card, ARB + AI governance approval |
| **Limited Risk** | Transparency obligations only | Chatbots, content recommendation, synthetic media | Disclosure to users, hallucination controls, model card recommended |
| **Minimal Risk** | No specific obligation | Spam filters, AI game NPCs, basic document search | Best practices; model card optional |

### High-Risk Classification Examples for This Organisation

| System | EU AI Act Article | Classification |
|--------|------------------|---------------|
| Credit risk model | Art. 6(2), Annex III §5 | High Risk |
| HR candidate ranking | Art. 6(2), Annex III §4 | High Risk |
| Clinical decision support | Art. 6(2), Annex III §6 | High Risk |
| Automated underwriting | Art. 6(2), Annex III §5 | High Risk |
| Customer service chatbot | Art. 50 | Limited Risk |
| Fraud detection (alert only) | Art. 6(2), Annex III §6 | High Risk |

---

## Mandatory Model Card Sections

Every AI system deployed to production must have a model card at `docs/ai-models/{system-name}/MODEL-CARD.md`. Use this template:

```markdown
# Model Card: {System Name}

Version: {semver}
Date: YYYY-MM-DD
Status: Draft | Reviewed | Approved
Owner: {team name}
EU AI Act Tier: Unacceptable | High | Limited | Minimal
ISO 42001 Review Completed: Yes | No | N/A

## System Overview

One paragraph: what does this system do, what decisions does it influence or automate?

## Intended Use

- **Primary use case:** {specific description}
- **Intended users:** {who operates or is subject to this system}
- **Deployment context:** {production environment description}

## Out-of-Scope Use

- Do not use for {specific misuse scenario 1}
- Do not use for {specific misuse scenario 2}
- Not validated for use with {excluded population or context}

## Training Data

- **Dataset:** {name, version, or description}
- **Date range:** {earliest — latest}
- **Size:** {number of samples}
- **Source:** {internal systems | licensed | public — specify licence}
- **PII included:** Yes (anonymised via {method}) | No
- **Known biases:** {list any known demographic or contextual biases in the training data}

## Evaluation Results

| Metric | Value | Dataset | Notes |
|--------|-------|---------|-------|
| Accuracy | 0.94 | held-out test set (n=10,000) | |
| Precision | 0.91 | held-out test set | |
| Recall | 0.88 | held-out test set | |
| F1 | 0.895 | held-out test set | |
| p99 Latency | 180ms | production load test | SageMaker ml.m5.xlarge |
| Faithfulness (RAG) | 0.82 | RAGAS evaluation set | Minimum threshold: 0.7 |

## Fairness Evaluation

Evaluated using **Amazon SageMaker Clarify** — results at `docs/ai-models/{name}/clarify-report/`.

| Demographic Group | Metric | Value | Acceptable Threshold | Pass/Fail |
|------------------|--------|-------|---------------------|-----------|
| Gender (Male vs Female) | Disparate Impact | 0.95 | ≥ 0.80 | Pass |
| Age (< 30 vs ≥ 30) | Statistical Parity Difference | 0.03 | ≤ 0.10 | Pass |

## Known Limitations

- {Limitation 1 — be specific, e.g., "Performance degrades for non-English text; BLEU score drops 40% for Spanish input"}
- {Limitation 2}
- {Limitation 3}

## Ethical Considerations

- {List any ethical risks identified and how they are mitigated}
- Human review required for: {list decision types that must be reviewed by a human}

## EU AI Act Compliance

- Conformity Assessment: {Internal | Third-party notified body} — Reference: {document ID}
- Technical Documentation: `docs/ai-models/{name}/technical-documentation/`
- Register Entry: EU AI Act Registration Number {number} (for High Risk)

## Contact and Governance

- System Owner: {name, email}
- AI Ethics Review: ai-governance@{company}.com
- Report issues: {Jira project or email}
- Review cadence: Quarterly (model performance) | Annually (full governance review)
```

---

## ISO 42001 Controls — Required Before Production Deployment

ISO 42001 defines an AI Management System (AIMS). The following controls are required for all production AI systems in this organisation:

| Control | ISO 42001 Reference | Verification |
|---------|-------------------|-------------|
| AI policy documented and approved | §5.2 | Document at `docs/ai-governance/ai-policy.md` |
| Risk assessment completed | §6.1.2 | `ai-risk-assessment.prompt.md` output stored |
| Objectives and KPIs defined | §6.2 | In model card Evaluation Results section |
| Roles and responsibilities assigned | §5.3 | Model card Contact section completed |
| Data governance documented | §8.4 | Data lineage and consent documented |
| Monitoring and measurement active | §9.1 | SageMaker Model Monitor configured |
| Internal audit scheduled | §9.2 | Quarterly review in calendar |
| Nonconformity and corrective action process | §10.1 | AI incident classification process followed |

---

## Audit Trail Requirements

All High-Risk AI systems must emit **immutable audit log records** for every inference. Log to a write-once store (e.g., AWS CloudTrail Lake, S3 with Object Lock).

### Required Fields per Inference Record

```json
{
  "event_type": "ai_inference",
  "model_id": "arn:aws:bedrock:eu-west-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
  "model_version": "3-sonnet-20240229-v1:0",
  "system_id": "credit-risk-scoring-v2",
  "input_hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "output_hash_sha256": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "user_id": "usr_abc123",
  "session_id": "sess_xyz789",
  "timestamp": "2024-11-01T14:30:00.000Z",
  "latency_ms": 142,
  "cost_tokens": { "input": 512, "output": 128 },
  "decision_outcome": "APPROVED | DECLINED | REFERRED",
  "hitl_reviewed": false,
  "hitl_reviewer_id": null,
  "jurisdiction": "GB"
}
```

- Do **not** log raw input or output — log hashes only (PII protection)
- Retention: minimum 5 years for High-Risk systems (EU AI Act Article 12)
- Logs must be exportable for regulatory inspection within 24 hours of request

---

## Human-in-the-Loop (HITL) Requirements

| EU AI Act Tier | HITL Required | Mode |
|---------------|--------------|------|
| High Risk | Mandatory | Meaningful oversight — human can override every decision |
| Limited Risk | Recommended | Escalation path available |
| Minimal Risk | Not required | — |

### HITL Implementation Pattern

- High-Risk systems must present a **confidence score** alongside every automated decision
- If `confidence < 0.85`, the system must **automatically route to human review**
- The human reviewer must be provided with the model's explanation (SHAP values or equivalent)
- Override decisions must be logged with reviewer ID and reasoning
- HITL override rate must be reported in quarterly model performance reviews

---

## Hallucination and Groundedness Thresholds (RAG Systems)

| Metric | Tool | Minimum Threshold | Action if Below |
|--------|------|------------------|----------------|
| Faithfulness | RAGAS | 0.70 | Block deployment; retune retrieval |
| Answer Relevancy | RAGAS | 0.75 | Review prompt template; expand context window |
| Context Precision | RAGAS | 0.65 | Improve chunking strategy or embedding model |
| Context Recall | RAGAS | 0.70 | Increase top-k retrieval; review document preprocessing |

Run RAGAS evaluation as part of ML CI pipeline before every model version promotion.

---

## Bias Evaluation — SageMaker Clarify

Required for all systems used in: credit decisions, employment screening, healthcare triage, insurance underwriting.

```python
# SageMaker Clarify bias configuration
from sagemaker import clarify

clarify_processor = clarify.SageMakerClarifyProcessor(
    role=role,
    instance_count=1,
    instance_type="ml.m5.xlarge",
    sagemaker_session=session
)

bias_config = clarify.BiasConfig(
    label_values_or_threshold=[1],          # positive outcome value
    facet_name="gender",                     # protected attribute
    facet_values_or_threshold=["F"],         # group to evaluate
    group_name="age_band"                    # intersectional analysis
)

# Acceptable thresholds — fail CI if exceeded
# DI (Disparate Impact): must be >= 0.80 (i.e., minority group ≥ 80% of majority group outcome rate)
# SPD (Statistical Parity Difference): must be <= ±0.10
# FTR (False Positive Rate difference): must be <= 0.05 for credit/employment decisions
```

---

## AI Acceptable Use Policy Template

Include in `docs/ai-governance/acceptable-use-policy.md`:

```markdown
## Prohibited Uses

- Generating content that impersonates a real person without consent
- Automated decision-making on loan/employment/housing applications without HITL for edge cases
- Processing special category personal data (health, biometrics, religion) without explicit consent
- Generating synthetic training data from production PII without anonymisation review

## Required Disclosures

- Users must be informed when interacting with an AI system (chatbots, automated emails, scoring systems)
- AI-generated content presented externally must be labelled as AI-generated

## Incident Reporting

Report AI incidents (bias discovered, model drift, unexpected outputs) via the AI incident register at {Jira project}.
```

---

## AI Incident Classification

| Class | Definition | Response |
|-------|-----------|---------|
| AI-P1 | Discriminatory outcome confirmed; regulatory breach | Disable system immediately; notify DPO; ARB within 24h |
| AI-P2 | Model drift detected (PSI > 0.2); significant accuracy degradation | Page on-call ML engineer; retrain within 48h |
| AI-P3 | Evaluation metric dropped below threshold; unexpected output pattern | ML team investigates next business day |
| AI-P4 | Isolated unusual output; no systemic pattern | Log in model card Known Limitations; review at next quarterly |
