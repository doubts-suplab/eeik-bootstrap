# Modernization Capability Pack

## Purpose

Provides intelligence for modernizing legacy systems — IBM i (AS/400), COBOL mainframe, Oracle Forms, and RPGLE codebases — to cloud-native Java/Python microservices on AWS.

## Manifest Trigger

```yaml
modernization:
  enabled: true
  source_platform: ibmi | cobol | mainframe | oracle-forms | mixed
```

## Agents

| Agent | Role |
|-------|------|
| `ibmi-modernization-expert` | IBM i / RPG IV / RPGLE / CL analysis and migration planning |
| `cobol-analyzer` | COBOL program analysis, business rule extraction, complexity scoring |
| `modernization-architect` | Target state architecture, strangler fig planning, wave definition |
| `legacy-integration-engineer` | Coexistence adapters, API facades, data sync bridges |

## What Gets Generated

For a `modernization` project type, `/generate-repo` adds:

```
docs/modernization/
├── current-state-assessment.md
├── target-state-architecture.md
├── migration-waves.md
└── coexistence-strategy.md

src/main/java/.../infrastructure/legacy/
├── adapter/
│   └── {LegacySystem}Adapter.java      ← Strangler fig facade
└── sync/
    └── {Entity}DataSyncJob.java         ← Data migration job
```

## Dependencies

- architecture-pack (foundational patterns and templates)
- java-pack (target implementation standards)
- aws-pack (target platform)
