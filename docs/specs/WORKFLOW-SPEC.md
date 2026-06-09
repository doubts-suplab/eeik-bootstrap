# Workflow Specification

Version: 1.0

---

# Purpose

Workflows define multi-step engineering processes.

Commands invoke workflows.

Agents execute workflow steps.

---

# Design Principles

Workflows should:

- Be deterministic
- Be auditable
- Be reusable
- Support human review
- Support AI execution

---

# Workflow Hierarchy

```text
Command
  ↓
Workflow
  ↓
Activities
  ↓
Agents
```

---

# Workflow Structure

Every workflow must define:

```yaml
name:
version:
purpose:
trigger:
inputs:
outputs:
activities:
```

---

# Example

```yaml
name: bootstrap-workflow

version: 1.0

purpose:
Create project workspace.

trigger:
bootstrap-command
```

---

# Workflow Categories

## Bootstrap Workflows

Examples:

```text
project-discovery

capability-selection

workspace-generation
```

---

## Architecture Workflows

Examples:

```text
architecture-design

architecture-review

adr-creation
```

---

## Governance Workflows

Examples:

```text
security-review

ai-review

production-readiness-review
```

---

## Delivery Workflows

Examples:

```text
estimation

release-planning

roadmap-generation
```

---

## Modernization Workflows

Examples:

```text
legacy-analysis

migration-planning

strangler-design
```

---

# Standard Workflow Pattern

```text
Trigger
 ↓
Discovery
 ↓
Analysis
 ↓
Generation
 ↓
Review
 ↓
Approval
 ↓
Publish
```

---

# Human Review Points

Mandatory review points:

```text
Architecture

Security

Production Readiness
```

---

# Workflow State Model

```text
Created
 ↓
Running
 ↓
Review
 ↓
Approved
 ↓
Completed
```

Alternative:

```text
Rejected
Cancelled
Failed
```

---

# Workflow Ownership

Every workflow must define:

```yaml
owner:
reviewers:
approvers:
```

---

# Workflow Outputs

May generate:

```text
Documents

Agents

Repositories

Reviews

Reports

Knowledge Assets
```

---

# Future Enhancements

- Workflow telemetry
- Workflow optimization
- Workflow recommendation engine
- Workflow orchestration graph
