# Compliance Standard

**Pack:** governance-pack | **Version:** 1.0

---

## GDPR Requirements (All EU Projects)

| Requirement | Implementation |
|-------------|---------------|
| Lawful basis documented | Data Processing Agreement (DPA) per data type |
| Data minimisation | Only collect data needed for stated purpose |
| Retention limits | TTL defined for all data; automated deletion |
| Subject access requests | API or manual process to export individual's data |
| Right to erasure | Process to delete individual's data (including backups) |
| Data breach notification | 72-hour notification procedure documented |
| DPO involvement | For large-scale processing or special category data |

---

## PCI-DSS (Payments)

| Requirement | Control |
|-------------|---------|
| Cardholder data never stored | Tokenise via payment provider before storage |
| PAN never logged | CloudWatch log scrubbing for card patterns |
| Network segmentation | Payment processing in isolated VPC segment |
| Access control | Role-based; no shared credentials |
| Vulnerability management | Monthly scans; critical patches within 30 days |
| Penetration testing | Annual; after significant change |

---

## AI Act (EU AI Systems)

For AI systems classified as Limited or High Risk:

| Requirement | Action |
|-------------|--------|
| Risk classification | Classify against Annex III categories |
| Model card | Produce per `write-model-card` prompt |
| Human oversight | Document human-in-the-loop gates |
| Transparency | Users informed when interacting with AI |
| Logging | Audit log of AI decisions retained for review |
| Conformity assessment | For High Risk: formal assessment before deployment |
