# Insurance Compliance Standard

**Applies To:** All insurance domain projects  
**Frameworks:** Solvency II, IDD (Insurance Distribution Directive), GDPR, FCA Conduct Rules

---

## Solvency II Requirements

| Requirement | Implementation |
|-------------|---------------|
| Technical provisions auditable | Reserve calculations traceable to policy + claims inputs; full lineage retained |
| SCR / MCR reporting | Solvency and Minimum Capital Requirement calculations reproducible from source data |
| Own Risk & Solvency Assessment (ORSA) | Scenario/stress inputs documented and versioned |
| Data quality (Pillar III) | Completeness, accuracy, appropriateness checks on all regulatory-reported data |
| Actuarial function sign-off | Model changes affecting provisions require actuarial review before release |

---

## IDD — Distribution & Product Governance

| Rule | Implementation |
|------|---------------|
| Demands-and-needs test | Capture and persist the customer demands-and-needs assessment before a sale |
| IPID provided | Insurance Product Information Document surfaced before purchase; version retained |
| Target market defined | Product governance records the target market and distribution strategy |
| Fair value assessment | Evidence of product value assessment retained (FCA fair value) |
| Advice traceability | Personal recommendations logged with the reasoning shown to the customer |

---

## Claims & Underwriting Controls

- Underwriting decisions must be auditable with full input traceability (rating factors → premium)
- Claims decisions record the basis for acceptance/decline; adverse decisions carry a reason
- Fraud indicators are logged; SIU (Special Investigations Unit) referrals are auditable
- Reserving changes on open claims are versioned with the triggering event

---

## GDPR in Insurance

| Data Type | Classification | Retention |
|-----------|---------------|-----------|
| Policyholder PII | Personal Data | Policy term + 6 years (limitation period) |
| Health / medical data (life, health, PMI) | Special Category | Explicit consent; strict access control; term + 6 years |
| Claims investigation data | Legitimate Interest | 6 years post-settlement |
| Underwriting rating factors | Personal Data | Duration of policy + 6 years |

---

## AI in Insurance — Model Risk Management

For any AI model used in underwriting, pricing, claims triage, or fraud detection:

1. **Model documentation** — purpose, inputs, outputs, training data, version
2. **Bias testing** — test for discrimination on protected characteristics before production (e.g. pricing must not proxy prohibited factors)
3. **Explainability** — decision reason codes required for any adverse underwriting or claims decision
4. **Human oversight** — human review for declines, high-value claims, and non-standard risks
5. **Model monitoring** — track model drift; retrain schedule defined
6. **EU AI Act** — risk-pricing and eligibility for life & health insurance is classified as High Risk under AI Act Annex III
