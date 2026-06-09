# Bootstrap Engine

The Bootstrap Engine is the entry point into EEIK.

Purpose:

- Discover project requirements
- Generate project manifest
- Select capability packs
- Configure governance
- Generate project workspace

Primary Command:

```text
/bootstrap
```

Outputs:

```text
project-manifest.yaml
selected-capabilities.yaml
governance-profile.yaml
```

The Bootstrap Engine is the authoritative source for all repository generation activities.

## Structure

```text
bootstrap/
│
├── README.md
│
├── questions/
│   ├── project-type.yaml
│   ├── domain.yaml
│   ├── architecture.yaml
│   ├── backend.yaml
│   ├── frontend.yaml
│   ├── cloud.yaml
│   ├── ai.yaml
│   ├── modernization.yaml
│   ├── governance.yaml
│   └── delivery.yaml
│
├── schemas/
│   └── manifest-schema.yaml
│
├── manifests/
│   ├── manifest-template.yaml
│   ├── insurance-template.yaml
│   ├── modernization-template.yaml
│   ├── aws-template.yaml
│   └── ai-platform-template.yaml
│
├── resolvers/
│   ├── capability-matrix.md
│   ├── dependency-resolver.md
│   ├── governance-resolver.md
│   └── agent-resolver.md
│
├── validators/
│   ├── manifest-validator.md
│   ├── dependency-validator.md
│   └── governance-validator.md
│
└── examples/
    ├── insurance-modernization.yaml
    ├── aws-java-platform.yaml
    └── agentic-platform.yaml

```
