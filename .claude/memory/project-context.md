# Project Context

> **Bootstrap Template** — Replace all `<!-- TODO -->` values with project-specific information when adopting this seed.

---

## Project Identity

| Field | Value |
|-------|-------|
| Project Name | <!-- TODO: e.g. "Order Management Platform" --> |
| Team | <!-- TODO: e.g. "Payments Engineering" --> |
| Domain | <!-- TODO: e.g. "Order Fulfilment" --> |
| Primary Language | <!-- TODO: Java 21 / TypeScript / Python --> |
| Framework | <!-- TODO: Spring Boot 3.x / Angular 17 --> |

---

## Service Inventory

<!-- TODO: List each service with its repo, purpose, and owner -->

| Service | Repository | Purpose | Owner Team |
|---------|-----------|---------|------------|
| <!-- service-name --> | <!-- org/repo --> | <!-- brief description --> | <!-- team --> |

---

## Environments

| Environment | URL / Endpoint | AWS Account | Region |
|-------------|---------------|-------------|--------|
| Local | http://localhost:8080 | N/A | N/A |
| Dev | <!-- TODO --> | <!-- TODO --> | eu-west-1 |
| Staging | <!-- TODO --> | <!-- TODO --> | eu-west-1 |
| Production | <!-- TODO --> | <!-- TODO --> | eu-west-1 |

---

## Key AWS Resources

| Resource Type | Name | Environment | Purpose |
|---------------|------|-------------|---------|
| ECS Cluster | <!-- TODO --> | prod | Application hosting |
| RDS Instance | <!-- TODO --> | prod | Primary database |
| S3 Bucket | <!-- TODO --> | prod | Document storage |
| Secrets Manager | <!-- TODO --> | prod | Application secrets |

---

## Authentication Patterns

<!-- TODO: Describe how your application authenticates users and services -->

- **User Auth:** <!-- e.g. "Cognito User Pool with JWT tokens; token validated in Spring Security filter" -->
- **Service-to-Service Auth:** <!-- e.g. "IAM roles via ECS task role; no static credentials" -->
- **External API Auth:** <!-- e.g. "API Gateway API key stored in Secrets Manager as /prod/external-api/key" -->

---

## Database

| Field | Value |
|-------|-------|
| Engine | <!-- TODO: PostgreSQL 15 / Aurora PostgreSQL / DB2 z/OS --> |
| Schema name | <!-- TODO --> |
| Migration tool | <!-- TODO: Flyway / Liquibase --> |
| ORM | <!-- TODO: Spring Data JPA / Spring Data JDBC / NamedParameterJdbcTemplate --> |

---

## Messaging

| System | Broker | Topics / Queues | Purpose |
|--------|--------|-----------------|---------|
| <!-- TODO --> | <!-- Kafka / SQS / SNS --> | <!-- topic names --> | <!-- purpose --> |

---

## On-Call & Escalation

| Role | Contact | Coverage |
|------|---------|----------|
| Engineering On-Call | <!-- TODO: PagerDuty rotation --> | 24/7 |
| Platform On-Call | <!-- TODO --> | Business hours |
| Engineering Manager | <!-- TODO --> | Business hours |

---

## CI/CD

| Stage | Tool | Trigger |
|-------|------|---------|
| Build | GitHub Actions | Push to any branch |
| Test | GitHub Actions | Push to any branch |
| Deploy (Dev) | GitHub Actions | Merge to `main` |
| Deploy (Prod) | GitHub Actions | Manual approval after staging |
