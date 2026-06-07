# Repository Generator

## Purpose

Transforms a validated `project-manifest.yaml` into a complete, runnable project repository scaffold.

The Repository Generator is the execution heart of EEIK. Given a manifest, it produces:

- Directory structure with all required packages and layers
- Skeleton source files with correct patterns applied
- Infrastructure-as-code stubs (CDK stacks)
- CI/CD pipeline configuration
- Governance artifacts (ADRs, risk register, review checklists)
- Agent configuration tailored to the project
- `.claude/` and `.github/` directory setup

## Invocation

```text
/generate-repo
```

Reads: `project-manifest.yaml` (must pass `/validate-manifest` first)

## What Gets Generated

| Manifest Field            | Generated Output                                        |
|---------------------------|---------------------------------------------------------|
| `technology.backend`      | Package structure, skeleton service, test scaffolding   |
| `technology.database`     | Repository layer, migration scripts, entity stubs       |
| `technology.messaging`    | Event publisher/consumer stubs, outbox pattern          |
| `architecture.patterns`   | Pattern-specific boilerplate applied to skeleton code   |
| `cloud.infra_as_code`     | CDK stacks or Terraform modules per environment         |
| `ai.enabled`              | LangGraph graph skeleton, agent definitions             |
| `governance.profile`      | Review checklists, risk register, compliance templates  |
| `delivery.cicd_platform`  | CI/CD workflow files                                    |
| `observability.enabled`   | Logging/tracing/metrics configuration stubs             |

## Structure

```
repository-generator/
│
├── README.md
│
├── prompts/
│   ├── repository-generation.md      ← Master generation prompt
│   ├── project-assembly.md           ← Multi-pack assembly logic
│   └── dependency-resolution.md      ← Pack dependency resolution
│
├── templates/
│   └── repository-layout.md          ← Canonical repo layout reference
│
├── workflows/
│   ├── repository-generation.yaml    ← End-to-end generation workflow
│   └── repository-upgrade.yaml       ← Upgrade existing repo to new manifest
│
└── examples/
    ├── java-microservice-output.md   ← Example output for greenfield Java
    └── ai-agent-poc-output.md        ← Example output for AI PoC
```

## Generation Sequence

```
1. Read + validate project-manifest.yaml
2. Run capability-selector → resolve required packs
3. Run governance-generator → produce governance assets
4. Scaffold directory structure
5. Apply technology-specific templates
6. Apply architecture pattern overlays
7. Apply AI/agentic overlays (if enabled)
8. Generate CDK / Terraform stubs
9. Generate CI/CD configuration
10. Generate .claude/ and .github/ configuration
11. Output generation report
```

## Agents

- `architect` — owns scaffold design decisions
- `java-architect` — owns Java package layout (if java backend)
- `ai-architect` — owns agentic scaffold (if AI enabled)
- `cdk-engineer` — owns CDK stack structure (if aws)
