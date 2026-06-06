# Write Model Card

Produce a model card for the following AI/ML model:

**Model:** $MODEL_NAME
**Version:** $MODEL_VERSION

## Instructions

Follow the standard model card format. Be specific about limitations — a vague limitations section provides no governance value. Consult the `ai-governance-officer` agent for EU AI Act classification guidance.

## Model Card Template

```markdown
# Model Card: {Model Name} v{Version}

**Date:** {YYYY-MM-DD}
**Authors:** {team/authors}
**Model Type:** {classifier / regressor / language model / embedding model / etc.}
**Framework:** {scikit-learn / PyTorch / TensorFlow / Bedrock / etc.}

## Intended Use

### Designed For
<!-- What tasks is this model designed to perform? -->

### Intended Users
<!-- Who should use this model? -->

### Out-of-Scope Use
<!-- What must this model NOT be used for? Be explicit. -->

## Training Data

| Field | Value |
|-------|-------|
| Source | <!-- dataset name or description --> |
| Date Range | <!-- YYYY-MM-DD to YYYY-MM-DD --> |
| Size | <!-- rows / tokens --> |
| Known Biases | <!-- any known demographic or sampling biases --> |
| Preprocessing | <!-- normalisation, tokenisation, filtering steps --> |

## Evaluation Metrics

| Metric | Overall | Group A | Group B | Baseline |
|--------|---------|---------|---------|---------|
| {metric} | {value} | {value} | {value} | {value} |

*Evaluated on: {test dataset name and size}*

## Performance Limitations

<!-- Specific conditions under which performance degrades -->
<!-- Include failure modes observed during evaluation -->

## Ethical Considerations

<!-- Fairness risks, potential for misuse, privacy implications -->
<!-- Demographic groups that may be disadvantaged by model errors -->

## EU AI Act Classification

**Risk Tier:** Unacceptable / High / Limited / Minimal
**Rationale:** <!-- why this classification applies -->

## Governance

| Field | Value |
|-------|-------|
| Approved By | <!-- name/role --> |
| Approval Date | <!-- YYYY-MM-DD --> |
| Review Date | <!-- when to re-evaluate this card --> |
| Monitoring | <!-- drift monitoring: yes/no, tool used --> |
```
