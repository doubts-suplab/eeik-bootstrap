# Architecture

Internal EEIK platform architecture.

---

## Contents

| Document | Covers |
|----------|--------|
| [system-overview.md](system-overview.md) | Full platform component map and data flow |
| [capability-resolution-engine.md](capability-resolution-engine.md) | How manifest fields map to capability packs |
| [repository-generator.md](repository-generator.md) | How repositories are assembled from packs and templates |
| [agent-factory.md](agent-factory.md) | Blueprint-based agent generation |
| [knowledge-platform.md](knowledge-platform.md) | Knowledge extraction, storage, and inheritance |

---

## Platform Overview

```
                    ┌──────────────────┐
                    │  Bootstrap Engine │   /bootstrap
                    └─────────┬────────┘
                              │ project-manifest.yaml
                              ▼
                 ┌────────────────────────┐
                 │  Capability Selector   │   capability-matrix.yaml
                 └─────────┬──────────────┘
                           │ selected-capabilities.yaml
                           ▼
             ┌───────────────────────────────┐
             │     Governance Generator      │   governance-profiles/
             └─────────┬─────────────────────┘
                       │ governance artifacts
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 Repository        Agent           Workflow
 Generator         Factory         Generator
        │              │
        ▼              ▼
  Generated        Generated
  Repository        Agents
                       │
                       ▼
              Knowledge Platform
              (captures learnings back)
```

## Component Responsibilities

| Component | Input | Output |
|-----------|-------|--------|
| Bootstrap Engine | Discovery questions | `project-manifest.yaml` |
| Capability Selector | Manifest | `selected-capabilities.yaml` |
| Governance Generator | Governance profile | Review checklists, CI gates, compliance templates |
| Repository Generator | Manifest + selected packs | Full project scaffold |
| Agent Factory | Manifest + blueprints | Project-specific `.claude/agents/` files |
| Knowledge Generator | Project artifacts | `knowledge/` entries (ADRs, lessons, incidents) |

## Key Design Decisions

- [ADR-G001](../../knowledge/adr-repository/README.md) — Hexagonal architecture for Java services
- [ADR-G002](../../knowledge/adr-repository/README.md) — Outbox pattern for event publishing
- [ADR-G003](../../knowledge/adr-repository/README.md) — CDK TypeScript for AWS infrastructure
- [ADR-G004](../../knowledge/adr-repository/README.md) — LangGraph for multi-agent systems
