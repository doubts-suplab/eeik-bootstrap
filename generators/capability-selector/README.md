# Capability Selector

## Purpose

Maps `project-manifest.yaml` fields to the capability packs required for that project.

The Capability Selector is the decision engine that sits between the Bootstrap Engine and the Generators. It reads a validated manifest and produces `selected-capabilities.yaml` — the list of packs that will be activated for the project.

## Design Principle

```
project-manifest.yaml
        ↓
Capability Selector
        ↓
selected-capabilities.yaml
        ↓
Repository Generator + Agent Factory
```

## Mapping Logic

Each manifest field triggers one or more capability packs. The rules are defined in `capability-matrix.yaml`.

### Current Mappings

| Manifest Field | Value | Packs Activated |
|----------------|-------|----------------|
| `technology.backend.language` | `java21` | `architecture-pack`, `java-pack` |
| `cloud.provider` | `aws` | `aws-pack` |
| `domain` | `insurance` | `insurance-pack` |
| `ai.enabled` | `true` | `ai-engineering-pack` |
| `governance.profile` | any | `governance-pack` |

The `architecture-pack` and `governance-pack` are always included — they are foundational.

## Pack Dependencies

When a pack is selected, its `dependencies.yaml` is read and dependent packs are added automatically. Example:

```
java-pack selected
    → dependencies: [architecture-pack]
    → architecture-pack added (if not already present)
```

## Outputs

```yaml
# selected-capabilities.yaml
packs:
  - architecture-pack
  - java-pack
  - aws-pack
  - governance-pack

governance_profile: standard
agent_recommendations:
  - solution-architect
  - java-architect
  - aws-architect
```

## Files

```
capability-selector/
└── capability-matrix.yaml   ← Manifest field → pack mapping rules
```
