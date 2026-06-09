# Agent Specification

Version: 1.0

---

# Purpose

Defines the standard structure for all EEIK agents.

---

# Agent Structure

```yaml
name:
version:
owner:
purpose:
responsibilities:
inputs:
outputs:
constraints:
dependencies:
```

---

# Example

```yaml
name: java-architect

version: 1.0

owner: platform-team

purpose:
Design enterprise Java solutions.

responsibilities:
  - Architecture Reviews
  - Solution Design
  - Technology Selection

inputs:
  - Requirements
  - Existing Architecture

outputs:
  - Recommendations
  - Architecture Decisions

constraints:
  - Follow Java Standards

dependencies:
  - architecture-pack
  - java-pack
```

---

# Agent Types

Supported:

- Architect
- Engineer
- Reviewer
- Auditor
- Specialist
- Coordinator
- Planner

---

# Required Sections

Every agent must define:

- Purpose
- Responsibilities
- Inputs
- Outputs
- Constraints

---

# Design Principles

Agents should:

- Be specialized
- Be reusable
- Be composable
- Avoid overlapping responsibilities

---

# Agent Lifecycle

```text
Draft
  ↓
Review
  ↓
Approved
  ↓
Published
  ↓
Deprecated
```

---

# Future Extensions

Future versions may include:

- Model Routing
- Evaluation Metrics
- Memory Strategies
- Tool Permissions
- Governance Levels
