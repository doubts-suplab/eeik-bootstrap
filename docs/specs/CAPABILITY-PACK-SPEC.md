# Capability Pack Specification

Version: 1.0

---

# Purpose

Defines reusable engineering intelligence units.

---

# Standard Structure

```text
capability-pack/
│
├── agents/
├── commands/
├── prompts/
├── standards/
├── templates/
├── examples/
├── workflows/
├── knowledge/
└── README.md
```

---

# Requirements

Every pack must contain:

- Purpose
- Scope
- Dependencies
- Examples

---

# Pack Metadata

Example:

```yaml
name: aws-pack

version: 1.0

owner: platform-team

dependencies:
  - architecture-pack
```

---

# Pack Categories

Supported:

- architecture
- cloud
- language
- frontend
- domain
- governance
- operations
- modernization

---

# Design Rules

Packs should:

- Be modular
- Be reusable
- Have clear ownership
- Avoid duplication

---

# Examples

```text
aws-pack

java-pack

insurance-pack

modernization-pack
```
