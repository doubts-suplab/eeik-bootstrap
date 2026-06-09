# AI Engineering

Claude Code and GitHub Copilot integration, model routing, agent design, and memory strategies.

---

## Contents

| Document | Covers |
|----------|--------|
| [model-routing.md](model-routing.md) | How EEIK selects the right Claude model for each task |

---

## What This Section Covers

EEIK is an AI-native platform — both Claude Code and GitHub Copilot are first-class citizens. This section documents how EEIK integrates with, configures, and extends these tools.

### Claude Code Integration

EEIK configures Claude Code via `.claude/`:

| Directory | Purpose |
|-----------|---------|
| `agents/` | 44 specialist agents, auto-selected by task context |
| `commands/` | Slash commands (`/bootstrap`, `/estimate`, `/review`, etc.) |
| `memory/` | Persistent context files loaded at session start |
| `standards/` | Technology coding standards read before code generation |
| `hooks/` | Pre/post guards and session lifecycle automation |

### GitHub Copilot Integration

EEIK configures Copilot via `.github/`:

| Directory | Purpose |
|-----------|---------|
| `instructions/` | Path-scoped instructions auto-applied by file type |
| `agents/` | Custom agent personas invoked with `@` in Copilot Chat |
| `prompts/tasks/` | Single-purpose task prompts |
| `prompts/workflows/` | Multi-step orchestrated workflows |
| `skills/` | Auto-loaded reusable capability packs |

### Model Routing

Different tasks require different Claude models. The [model-router](../../generators/model-router/README.md) determines which model to use:

| Task Category | Model |
|--------------|-------|
| Compliance assessments, ARB reviews | `claude-opus-4-8` |
| Architecture design, code implementation, PR review | `claude-sonnet-4-6` |
| High-throughput classification, templated generation | `claude-haiku-4-5-20251001` |

See [model-routing.md](model-routing.md) for the full routing policy.

### Agent Design

EEIK agents are generated from blueprints by the Agent Factory rather than maintained as static files. Each agent has:

- A `description` field used for auto-selection
- A `model` field set by the model router
- A system prompt composed from the relevant capability pack's standards and context

### Memory Strategies

Claude Code reads `.claude/memory/` files at session start. EEIK uses this for persistent context that survives session boundaries: service inventory, environment details, architecture decisions, tech debt, and RCA tracking.

The `on-stop.sh` hook auto-updates `session-log.md` at the end of every session.
