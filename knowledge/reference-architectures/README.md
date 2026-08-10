# Reference Architectures

Proven architectural blueprints, ready to adapt for new projects.

As of EEIK v1.4 each reference architecture is a **first-class, engine-surfaced** directory
(see [ADR-010](../../docs/decisions/ADR-010-reference-architectures-engine-surfaced.md)):

```
<name>/
├── reference.yaml          # machine-readable descriptor (title, stack, components, expected_packs, deployment)
├── project-manifest.yaml   # a SCHEMA-VALID eeik manifest — feed to `eeik resolve-packs` / repo-generator
├── architecture.md         # the design
├── runbook.md              # operations
├── cdk/                    # deployable AWS CDK app (TypeScript) — the architecture as infrastructure
└── local-dev/              # docker-compose + seed data to run it on a laptop, no AWS
```

The engine surfaces and checks them:

```bash
eeik architectures                    # list them (also: eeik.reference_architectures() / MCP)
eeik architectures order-management   # detail + the packs it resolves to
eeik verify                           # asserts each manifest still validates & resolves to its declared packs
```

## Index (engine-surfaced)

| Architecture | Stack | Maturity | Resolves to |
|---|---|---|---|
| [order-management](order-management/architecture.md) | Spring Boot 3 · Java 21 · Aurora · Kafka · CDK | Production | core · architecture · aws · delivery · java |
| [ai-augmented-service](ai-augmented-service/architecture.md) | FastAPI · Bedrock · pgvector · HALO · React · CDK | Staging | + agent-harness · ai-engineering · governance · python · react |
| [data-platform](data-platform/architecture.md) | Kafka · Spark/Glue · dbt · Airflow · S3 lakehouse · Athena · CDK | Production | + data-engineering · python |
| [multi-tenant-saas](multi-tenant-saas/architecture.md) | Spring Boot 3 · Aurora RLS · Cognito · EventBridge · React · CDK | Production | core · architecture · aws · delivery · governance · java · react |
| [multi-agent-ai-platform](multi-agent-ai-platform/architecture.md) | FastAPI · LangGraph · Bedrock · DynamoDB · HALO · CDK | Staging | + agent-harness · ai-engineering · governance · python (supervisor + workers, no frontend) |

Each architecture is also **deployable**: `cdk/` is a real AWS CDK app (`npm install && npx cdk deploy`)
and `local-dev/` brings it up on a laptop with `docker compose up -d` + seed data. `eeik architectures
<name>` surfaces both paths, and `eeik verify` checks each declared `cdk/` has a `cdk.json` and each
`local-dev/` a `docker-compose.yml` — so the infrastructure can't silently rot either.

