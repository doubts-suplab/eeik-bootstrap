# Agent Factory Specification

Version: 1.0

---

# Purpose

The Agent Factory creates project-specific agents dynamically.

The platform should prefer generating agents over maintaining large static agent catalogs.

---

# Goals

- Reduce agent sprawl
- Increase specialization
- Enable project-specific intelligence
- Maintain consistency

---

# Primary Command

```text
/generate-agent
```

---

# Inputs

Required:

```yaml
name:
purpose:
responsibilities:
inputs:
outputs:
constraints:
```

---

# Agent Lifecycle

```text
Draft
 ↓
Generated
 ↓
Reviewed
 ↓
Approved
 ↓
Published
 ↓
Deprecated
```

---

# Generated Assets

The Agent Factory produces:

```text
agent.md
prompt.md
memory-strategy.md
evaluation-strategy.md
command-set.md
```

---

# Agent Categories

Supported:

```text
Architect
Engineer
Reviewer
Auditor
Planner
Coordinator
Specialist
Investigator
```

---

# Agent Metadata

Example:

```yaml
name: claims-specialist

version: 1.0

category: specialist

owner: insurance-pack
```

---

# Generation Rules

Prefer:

```text
Reuse Existing Agent
```

before:

```text
Generate New Agent
```

---

# Agent Evaluation

Every generated agent must define:

- Success criteria
- Failure criteria
- Escalation conditions

---

# Future Enhancements

- Agent telemetry
- Agent evolution
- Agent performance scoring
- Agent recommendation engine
