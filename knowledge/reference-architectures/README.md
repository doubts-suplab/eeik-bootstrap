# Reference Architectures

Proven architectural blueprints, ready to adapt for new projects.

As of EEIK v1.4 each reference architecture is a **first-class, engine-surfaced** directory
(see [ADR-010](../../docs/decisions/ADR-010-reference-architectures-engine-surfaced.md)):

```
<name>/
├── reference.yaml          # machine-readable descriptor (title, stack, components, expected_packs)
├── project-manifest.yaml   # a SCHEMA-VALID eeik manifest — feed to `eeik resolve-packs` / repo-generator
├── architecture.md         # the design
└── runbook.md              # operations
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

## Legacy prose blueprints

- [multi-agent-ai-platform.md](multi-agent-ai-platform.md) — narrative blueprint (pre-v1.4 format; not
  yet engine-surfaced).

Planned (ROADMAP v1.3): Data Platform, Multi-Tenant SaaS.
