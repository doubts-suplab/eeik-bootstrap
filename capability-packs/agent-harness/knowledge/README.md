# Knowledge — Agent Harness

The **agent harness** is the generic, brand-neutral agent runtime for the ecosystem: the layer that stands
between an agent's decision logic and the outside world and makes execution safe, governed, observable, and
reproducible. It is a generic implementation of the "agent runtime" that
[AIEL](https://github.com/suplab/aether-iel) specifies but does not build.

## Reference runtime

- **Repo:** [`doubts-suplab/agent-harness`](https://github.com/doubts-suplab/agent-harness)
- **Protocol spec:** `docs/spec/harness-protocol.md`
- **Agent Contract schema:** `docs/spec/agent-contract.schema.json`
- **Decisions:** `docs/decisions/ADR-0001..0008`

## Ecosystem positioning

```
aether-iel (methodology/spec)
      │  defines the agent contract & governance
      ▼
eeik-bootstrap (this repo — bootstrapping/config)
      │  activates the harness via agent-harness-pack
      ▼
agent-harness (generic runtime)  ◀── you conform to this
      │  consumed by
      ▼
products: apex-sdlc, aether-grid, aether-core
```

## When this pack is selected

Manifests with `ai.enabled: true`, `ai.pattern in [single-agent, multi-agent, enterprise-agent-platform, agent]`,
or `project.project_type: agent-platform`. It layers on `ai-engineering-pack` (agent/prompt/eval standards) and
`governance-pack` (confidence gate, audit, human-in-the-loop).

See [`../standards/agent-harness-protocol.md`](../standards/agent-harness-protocol.md) for the conformance checklist.
