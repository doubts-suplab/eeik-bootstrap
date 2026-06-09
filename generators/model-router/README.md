# Model Router

## Purpose

Determine which Claude model to use for each task category.

EEIK uses three Claude models with distinct trade-offs:

| Model                  | String                       | Use For                                              |
|------------------------|------------------------------|------------------------------------------------------|
| Claude Opus 4.8        | `claude-opus-4-8`            | Complex reasoning, high-stakes decisions, compliance |
| Claude Sonnet 4.6      | `claude-sonnet-4-6`          | Balanced — most engineering and review tasks         |
| Claude Haiku 4.5       | `claude-haiku-4-5-20251001`  | High-throughput, classification, templated output    |

## Routing Policies

| Policy File         | Covers                                          |
|---------------------|-------------------------------------------------|
| architecture.yaml   | Architecture design, ADRs, ARB submissions      |
| engineering.yaml    | Code implementation, review, testing, CDK       |
| governance.yaml     | Security, compliance, PRR, AI governance        |
| documentation.yaml  | Docs, READMEs, runbooks, API specs              |

## Default Policy

When no explicit task type is matched:

```
model: claude-sonnet-4-6
rationale: "Best balance of quality and cost for general engineering tasks"
```

## Usage

The model router is consulted by:

1. `/generate-agent` — to set `model` in generated agent frontmatter
2. `workflows/*.yaml` — to configure model per step
3. Agent definitions — to self-declare preferred model

## Routing Decision Tree

```
Is this compliance/regulatory assessment?         → claude-opus-4-6
Is this complex multi-system architectural design? → claude-opus-4-6
Is this high-throughput classification/tagging?   → claude-haiku-4-5
Otherwise                                          → claude-sonnet-4-6
```
