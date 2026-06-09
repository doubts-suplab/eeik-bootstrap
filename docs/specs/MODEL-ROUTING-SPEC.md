# Model Routing Specification

Version: 1.0

---

# Purpose

Define how EEIK selects AI models for specific workloads.

Different tasks require different models.

Model routing optimizes:

- Quality
- Cost
- Speed
- Context utilization

---

# Design Principles

## Best Model For Task

Do not use one model for everything.

---

## Cost Awareness

Expensive models should be reserved for high-value work.

---

## Capability Based Routing

Route based on task complexity.

---

## Vendor Agnostic

Routing should support:

```text
Anthropic
OpenAI
Google
Local Models
Future Providers
```

---

# Routing Hierarchy

```text
Request
 ↓
Task Classification
 ↓
Routing Policy
 ↓
Model Selection
 ↓
Execution
```

---

# Supported Workload Types

## Architecture

Examples:

```text
Solution Design

System Design

Modernization Design

Reference Architectures
```

Recommended:

```text
Claude Sonnet
```

---

## Engineering

Examples:

```text
Java Development

Python Development

React Development

Angular Development
```

Recommended:

```text
Claude Sonnet
```

---

## Code Reviews

Examples:

```text
PR Reviews

Refactoring Reviews

Coverage Reviews
```

Recommended:

```text
Claude Sonnet
```

---

## Documentation

Examples:

```text
README

Runbooks

Guides

Wiki Content
```

Recommended:

```text
GPT
Claude Sonnet
```

---

## Estimation

Examples:

```text
Story Estimation

Project Estimation

Roadmaps
```

Recommended:

```text
GPT
Claude Sonnet
```

---

## Governance

Examples:

```text
Architecture Reviews

Security Reviews

AI Reviews
```

Recommended:

```text
Claude Sonnet
```

---

## Agent Generation

Examples:

```text
Agent Design

Prompt Design

Workflow Design
```

Recommended:

```text
Claude Sonnet
```

---

## Knowledge Curation

Examples:

```text
ADR Creation

Incident Summaries

Lessons Learned
```

Recommended:

```text
GPT
Claude Sonnet
```

---

# Default Routing Policy

## Tier 1

High Complexity

Examples:

```text
Architecture

Governance

Modernization

Agent Design
```

Route To:

```text
Claude Sonnet
```

---

## Tier 2

Medium Complexity

Examples:

```text
Documentation

Knowledge Management

Estimations
```

Route To:

```text
GPT
Claude Sonnet
```

---

## Tier 3

Low Complexity

Examples:

```text
Formatting

Template Generation

Simple Transformations
```

Route To:

```text
Local Models
```

---

# Local Model Strategy

Fallback Usage:

```text
Offline Operation

Low Risk Tasks

Formatting

Template Expansion
```

Examples:

```text
Llama

Qwen

Mistral
```

---

# Agent Routing

Agents should declare:

```yaml
preferred-model:
fallback-model:
```

Example:

```yaml
agent:
  name: java-architect

preferred-model:
  claude-sonnet

fallback-model:
  gpt
```

---

# Routing Metadata

Each request should capture:

```yaml
task-type:
complexity:
cost-tier:
selected-model:
```

---

# Governance Rules

Critical workloads:

```text
Architecture

Security

Modernization

AI Governance
```

must not use low-capability models by default.

---

# Future Enhancements

- Dynamic routing
- Cost optimization
- Performance-based routing
- Agent-specific routing policies
- Multi-model collaboration
