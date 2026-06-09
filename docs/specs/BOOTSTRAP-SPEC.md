# Bootstrap Specification

Version: 1.0

---

# Purpose

The Bootstrap Engine is the entry point into EEIK.

Its responsibility is to discover project requirements and generate a project manifest that becomes the source of truth for all subsequent generation activities.

---

# Goals

The Bootstrap Engine must:

- Minimize setup effort
- Standardize project initialization
- Select relevant capability packs
- Generate a project manifest
- Configure governance
- Generate project-specific assets

---

# Primary Command

```text
/bootstrap
```

---

# Workflow

```text
User
  ↓
Bootstrap Interview
  ↓
Project Manifest
  ↓
Capability Selection
  ↓
Repository Generation
  ↓
Project Workspace
```

---

# Discovery Areas

## Project Type

Supported values:

```text
greenfield
modernization
poc
mvp
enterprise-platform
agent-platform
```

---

## Domain

Supported values:

```text
insurance
banking
healthcare
retail
generic
```

---

## Backend

Supported values:

```text
java21
java25
python
nodejs
mixed
```

---

## Frontend

Supported values:

```text
react
angular
none
```

---

## Cloud

Supported values:

```text
aws
azure
gcp
hybrid
```

---

## Architecture

Supported values:

```text
monolith
modular-monolith
microservices
event-driven
serverless
agentic
```

---

## AI

Supported values:

```text
none
rag
single-agent
multi-agent
agent-platform
```

---

## Modernization

Supported values:

```text
none
ibmi
rpg
cobol
mainframe
mixed
```

---

# Output

The Bootstrap Engine generates:

```text
project-manifest.yaml
```

---

# Responsibilities

The Bootstrap Engine must:

- Validate responses
- Resolve dependencies
- Select capability packs
- Select governance requirements
- Produce manifest

---

# Future Enhancements

- Conversational discovery
- Repository analysis
- Legacy system analysis
- Automatic architecture inference
