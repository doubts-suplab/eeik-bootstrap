# Command Specification

Version: 1.0

---

# Purpose

Commands provide reusable execution patterns within EEIK.

Commands are user-facing entry points that invoke workflows, agents, generators, validators, or orchestration logic.

Commands should be:

- Discoverable
- Reusable
- Idempotent where possible
- Capability-aware
- Manifest-aware

---

# Design Principles

## Single Responsibility

A command should perform one primary function.

Good:

```text
/bootstrap
```

Bad:

```text
/bootstrap-and-generate-and-review
```

---

## Human Friendly

Commands should be memorable.

Example:

```text
/bootstrap
/generate-agent
/create-adr
```

---

## Manifest Driven

Commands should leverage project manifest context whenever available.

---

# Command Structure

Every command must define:

```yaml
name:
version:
purpose:
owner:
inputs:
outputs:
dependencies:
permissions:
```

---

# Example

```yaml
name: bootstrap

version: 1.0

purpose:
Initialize a new project.

owner:
eeik-core

inputs:
- project-details

outputs:
- project-manifest

dependencies:
- bootstrap-engine

permissions:
- repository-read
```

---

# Command Categories

## Bootstrap Commands

Project initialization.

Examples:

```text
/bootstrap

/analyze-project

/discover-capabilities
```

---

## Generation Commands

Generate artifacts.

Examples:

```text
/generate-repository

/generate-agent

/generate-workflow

/generate-template
```

---

## Architecture Commands

Architecture-focused.

Examples:

```text
/create-architecture

/create-adr

/create-rfc

/review-architecture
```

---

## Governance Commands

Governance activities.

Examples:

```text
/run-security-review

/run-ai-review

/run-prr
```

---

## Knowledge Commands

Knowledge management.

Examples:

```text
/capture-lesson

/capture-incident

/create-runbook
```

---

## Modernization Commands

Legacy modernization.

Examples:

```text
/analyze-rpg

/analyze-cobol

/create-modernization-plan
```

---

# Required Metadata

Every command must declare:

## Name

Unique identifier.

---

## Purpose

Business purpose.

---

## Inputs

Expected parameters.

---

## Outputs

Generated artifacts.

---

## Dependencies

Required capabilities.

---

## Permissions

Required access level.

---

# Command Lifecycle

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

# Naming Standards

Format:

```text
/action-object
```

Examples:

```text
/create-adr

/generate-agent

/review-security
```

---

# Future Enhancements

- Command telemetry
- Command analytics
- Command recommendations
- Context-aware command discovery
