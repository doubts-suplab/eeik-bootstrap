# Healthcare Compliance Standard

**Applies To:** All healthcare domain projects  
**Frameworks:** GDPR (Special Category Data), HIPAA (if US), NHS DSPT, CQC Standards

---

## Special Category Data (GDPR Article 9)

Health data is Special Category under GDPR — requires elevated protection.

| Rule | Implementation |
|------|---------------|
| Explicit consent or legal basis required | Document legal basis before collecting any health data |
| Data minimisation | Collect only what is clinically necessary |
| Access control | Role-based access; minimum necessary access (clinical need) |
| Audit logging | Every access to patient records logged (who, when, what) |
| Data retention | NHS: 8 years adult records; 25 years child records |
| Breach notification | 72 hours to ICO; notify affected individuals without undue delay |

---

## HIPAA (US Projects)

| Requirement | Implementation |
|-------------|---------------|
| PHI encrypted at rest | AES-256; encryption key managed separately from data |
| PHI encrypted in transit | TLS 1.2+ minimum |
| Minimum necessary access | Role-based; audit all PHI access |
| Business Associate Agreement | BAA required with all cloud providers touching PHI |
| Breach notification | 60 days to HHS; affected individuals notified |

---

## NHS Digital Standards

- NHS DSP Toolkit compliance required for systems processing NHS patient data
- Data Security and Protection Toolkit annual assessment
- Clinical safety case required for systems supporting clinical decisions
- DCB0129/DCB0160 clinical risk management standards

---

## AI in Healthcare — High Risk (EU AI Act)

Any AI system used in clinical decision support:

1. **High Risk classification** (EU AI Act Annex III) — full conformity assessment required
2. **Clinical validation** — prospective clinical study before deployment
3. **Human oversight mandatory** — clinical professional reviews all AI recommendations
4. **Explainability** — AI must be able to explain its recommendation in clinical terms
5. **Adverse event reporting** — mechanism for clinicians to report AI errors
6. **Post-market surveillance** — continuous monitoring of clinical outcomes
