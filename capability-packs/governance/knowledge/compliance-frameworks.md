# Compliance Frameworks Reference

**Pack:** governance-pack | **Version:** 1.0

---

## GDPR — Quick Reference

**Applies to:** Any system processing personal data of EU residents.

Key articles:
- Art. 5: Data processing principles (lawfulness, minimisation, accuracy, storage limitation)
- Art. 6: Lawful basis (consent, contract, legal obligation, legitimate interest)
- Art. 17: Right to erasure ("right to be forgotten")
- Art. 25: Data protection by design and by default
- Art. 33: 72-hour breach notification to supervisory authority
- Art. 83: Fines up to €20M or 4% of global annual turnover

**EEIK controls:** compliance-standard.md, compliance-reviewer agent, DPA template

---

## PCI-DSS v4.0 — Quick Reference

**Applies to:** Any system that stores, processes, or transmits cardholder data.

Key requirements:
- Req 3: Protect stored account data (never store CVV; tokenise PAN)
- Req 4: Encrypt transmission of cardholder data
- Req 7: Restrict access by business need
- Req 10: Log and monitor all access
- Req 11: Test security systems and processes
- Req 12: Maintain information security policies

**EEIK controls:** aws-pack security standard, cloud-security-reviewer agent

---

## EU AI Act — Risk Categories

**Applies to:** AI systems deployed in the EU.

| Risk Level | Examples | Requirements |
|------------|----------|-------------|
| Unacceptable | Cognitive manipulation, social scoring | **Prohibited** |
| High | Credit scoring, insurance risk assessment, HR decisions | Conformity assessment, human oversight, logging |
| Limited | Chatbots, deepfakes | Transparency disclosure |
| Minimal | Spam filters, game AI | No specific requirements |

**EEIK controls:** AI governance review, ai-governance-officer agent, model card template
