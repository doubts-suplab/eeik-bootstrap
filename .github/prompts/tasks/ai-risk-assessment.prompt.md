# AI Risk Assessment

Conduct an AI risk assessment for the following system:

**System:** $SYSTEM_NAME
**Purpose:** $SYSTEM_PURPOSE

## Instructions

1. Classify the system by EU AI Act risk tier
2. Identify the top 5 risks with likelihood and impact ratings
3. Specify required controls for each risk
4. Produce a pre-deployment checklist
5. Recommend monitoring requirements

See `.github/instructions/ai-governance.instructions.md` for compliance standards.

## Risk Assessment Output

```markdown
## AI Risk Assessment: {System Name}

**Date:** {YYYY-MM-DD}
**Assessor:** AI Governance Officer

### EU AI Act Classification
**Risk Tier:** Unacceptable / High / Limited / Minimal
**Rationale:** {specific reason based on Article references}

### Risk Register

| Ref | Risk | Category | Likelihood | Impact | Rating | Required Control |
|-----|------|----------|-----------|--------|--------|-----------------|
| R-01 | {risk description} | Bias / Privacy / Security / Safety | H/M/L | H/M/L | H/M/L | {control} |

### GDPR Article 22 Assessment
**Automated Decision-Making:** Yes / No
**Significant Effect on Individuals:** Yes / No
**Safeguards Required:** {list if applicable}

### Pre-Deployment Checklist
- [ ] Model card completed and approved
- [ ] Bias evaluation completed across demographic groups
- [ ] Human-in-the-loop controls implemented for high-stakes decisions
- [ ] Audit logging of all AI decisions implemented
- [ ] Output guardrails tested
- [ ] Drift monitoring configured
- [ ] User notification of AI involvement (if required by GDPR)

### Monitoring Requirements
- Data drift: {metric, threshold, alert target}
- Model quality: {metric, threshold, alert target}
- Fairness: {metric, threshold, alert target}

### Residual Risk
**Accepted Risk Level:** {Low / Medium}
**Accepted By:** {role}
**Review Date:** {YYYY-MM-DD}
```
