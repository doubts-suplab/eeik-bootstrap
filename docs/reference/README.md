# Reference

Schemas, specifications, and glossary for EEIK.

---

## Contents

| Document | Covers |
|----------|--------|
| [manifest-schema.md](manifest-schema.md) | Full `project-manifest.yaml` field reference |
| [capability-pack-schema.md](capability-pack-schema.md) | Capability pack `metadata.yaml` and `dependencies.yaml` structure |
| [agent-schema.md](agent-schema.md) | Agent frontmatter fields for Claude Code and GitHub Copilot |
| [command-schema.md](command-schema.md) | Slash command definition format |
| [workflow-schema.md](workflow-schema.md) | Workflow YAML structure and step types |
| [governance-schema.md](governance-schema.md) | Governance profile YAML fields |
| [glossary.md](glossary.md) | EEIK terminology definitions |

---

## Quick Lookups

### Manifest Fields

The most commonly referenced fields in `project-manifest.yaml`:

```yaml
project:
  name:                  # kebab-case project identifier
  project_type:          # greenfield | modernization | mvp | enterprise-platform

technology:
  backend:
    language:            # java21 | python312 | nodejs20
  frontend:
    framework:           # react | angular | none
  database:
    type:                # postgresql | aurora | dynamodb | db2-i

cloud:
  provider:              # aws | none
  infra_as_code:         # cdk | terraform | none

ai:
  enabled:               # true | false
  framework:             # langgraph | crewai | autogen | none

governance:
  profile:               # basic | standard | regulated | enterprise
```

See [manifest-schema.md](manifest-schema.md) for the complete field reference including all allowed values, defaults, and validation rules.

### Agent Frontmatter

```yaml
---
name: java-developer
description: >-
  Use for ticket-scoped Java Spring Boot implementation work.
  Trigger when asked to implement a Java feature.
model: claude-sonnet-4-6
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---
```

See [agent-schema.md](agent-schema.md) for all supported frontmatter fields.
