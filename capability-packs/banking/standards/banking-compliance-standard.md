# Banking Compliance Standard

**Applies To:** All banking domain projects  
**Frameworks:** PCI-DSS, GDPR, Basel III, FCA Conduct Rules, PSD2

---

## PCI-DSS Requirements (Card Data)

| Requirement | Implementation |
|-------------|---------------|
| Never store full PAN | Tokenise at point of capture (Stripe/Adyen token); never store raw card number |
| Never store CVV | CVV must not be stored post-authorisation under any circumstances |
| Card data encrypted | AES-256 for any stored card data (token vault) |
| Transmission encrypted | TLS 1.2+ minimum for all card data in transit |
| Cardholder environment isolated | Separate VPC/subnet; no direct internet access |
| Logging of all access | CloudTrail + VPC Flow Logs for CHD environment |
| MFA on all admin access | AWS IAM Identity Center with MFA required |

---

## AML / KYC Requirements

| Rule | Implementation |
|------|---------------|
| Customer identity verified before account opening | KYC workflow with document verification |
| Transaction monitoring | Real-time pattern matching for suspicious activity |
| SAR filing capability | Suspicious Activity Report generation and secure submission |
| Sanctions screening | OFAC/HM Treasury screening on all counterparties |
| Records retained 5 years | AML records: minimum 5 years post-relationship end |

---

## Basel III Capital Requirements

- Risk-weighted assets must be tracked and reported
- Capital ratio calculations must be auditable with full input traceability
- Stress testing scenarios must be documented and reproducible
- Any AI model used in risk scoring must be explainable (model risk management)

---

## GDPR in Banking

| Data Type | Classification | Retention |
|-----------|---------------|-----------|
| Account holder PII | Personal Data | 7 years post-closure (AML obligation) |
| Transaction history | Personal Data | 7 years (regulatory minimum) |
| Credit assessments | Special Category (financial) | Duration of credit relationship + 6 years |
| Fraud investigation data | Legitimate Interest | 6 years |

---

## AI in Banking — Model Risk Management

For any AI model used in credit decisions, fraud detection, or risk scoring:

1. **Model documentation** — purpose, inputs, outputs, training data, version
2. **Bias testing** — test for demographic bias before production deployment
3. **Explainability** — decision reason codes required for any adverse credit decision (FCA requirement)
4. **Human oversight** — human review for high-value/high-risk automated decisions
5. **Model monitoring** — track model drift; retrain schedule defined
6. **EU AI Act** — credit scoring classified as High Risk under AI Act Annex III
