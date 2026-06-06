# Project Constraints

> Hard constraints that must NEVER be violated. These are not preferences — they are non-negotiable limits imposed by business, regulatory, legal, or architectural requirements.
>
> **Bootstrap Template** — Replace placeholder entries with your project's actual constraints.

---

## Technical Constraints

| Constraint | Reason | Implication |
|------------|--------|-------------|
| Java 21 minimum | LTS support, virtual threads (Loom) | No Java 17 features that were removed in 21 |
| `jakarta.*` only — no `javax.*` | Spring Boot 3.x requires Jakarta EE 10 | All legacy code must be migrated before integration |
| Constructor injection only — no `@Autowired` on fields | Testability and immutability | All Spring beans must accept dependencies through constructors |
| No hardcoded credentials anywhere in source | Security policy | All secrets via Secrets Manager or environment variables |
| No `SELECT *` in any SQL | Performance and schema evolution safety | Always specify column lists explicitly |
| <!-- TODO: Add project-specific technical constraints --> | | |

---

## Data & Privacy Constraints

| Constraint | Regulation / Policy | Scope |
|------------|-------------------|-------|
| PII must not appear in application logs | GDPR Article 5(1)(f) | All logging statements |
| PII must not be stored in unencrypted S3 | GDPR / Internal policy | All S3 data at rest |
| Data retention: customer records max 7 years | <!-- TODO: policy reference --> | Order and customer data |
| <!-- TODO: Add project-specific data constraints --> | | |

---

## Operational Constraints

| Constraint | Reason | Implication |
|------------|--------|-------------|
| No direct production database access by developers | Separation of duties | All production data changes via application or approved migration scripts |
| No manual changes to production infrastructure | Auditability | All infrastructure changes via CDK/Terraform with PR approval |
| No deployment to production on Fridays after 15:00 local time | Risk reduction | Schedule production deployments for Mon–Thu |
| <!-- TODO: Add project-specific operational constraints --> | | |

---

## Regulatory / Compliance Constraints

<!-- TODO: Add constraints from relevant regulations (PCI-DSS, HIPAA, FCA, etc.) -->

| Constraint | Source | Applies To |
|------------|--------|-----------|
| <!-- constraint --> | <!-- regulation --> | <!-- scope --> |

---

## Architecture Constraints

| Constraint | Reason |
|------------|--------|
| No cross-context database joins | DDD bounded context isolation |
| All cross-context communication via API or events — no shared databases | Loose coupling |
| All new services must have SLO defined before production deployment | Operational readiness |
| <!-- TODO: Add project-specific architecture constraints --> | |
