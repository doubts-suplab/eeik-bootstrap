---
applyTo: "**/a2a/**/*.py,**/a2a/**/*.ts,**/agent_comms/**/*.py"
---

# Agent-to-Agent (A2A) Protocol Standards

## Communication Design

- Define explicit agent capability contracts before implementing agent communication
- Use typed schemas (Pydantic / TypedDict) for all inter-agent message payloads
- Version all inter-agent message schemas — breaking changes require a version bump
- Every agent-to-agent call must include: `task_id`, `requesting_agent`, `target_capability`, and `payload`

## Orchestration Patterns

- Always set a maximum iteration count for orchestrator loops — no unbounded agent cycles
- Implement timeout on every agent call — stuck agents must not block the orchestrator indefinitely
- Use circuit breaker pattern for agents that call unreliable external services
- Log every agent handoff: sender, receiver, task ID, timestamp, and response latency

## State Management

- Design shared context objects with explicit schema — avoid passing raw untyped dicts
- Implement context pruning to manage token budgets in long agent chains
- Store conversation state externally (database / vector store) for resumable workflows
- Define context TTL — stale context should not be passed to agents in resumed workflows

## Safety & Control

- Implement human-in-the-loop gates for high-stakes decisions (financial, medical, PII-impacting)
- Scope agent permissions — each agent may only call capabilities it is authorised for
- Validate agent outputs before passing to downstream agents — never trust and forward blindly
- Implement kill-switch mechanisms for stuck or runaway agent pipelines

## Error Handling

- Define a retry strategy with exponential backoff for transient agent failures
- Implement dead-letter handling for tasks that exhaust retries
- Return structured error responses from agents — never let unhandled exceptions propagate silently
- Produce audit trail entries for all failed agent calls

## Audit & Observability

- Log every agent-to-agent interaction with full task context for debugging and compliance
- Track cumulative token usage across agent hops
- Implement distributed tracing (trace ID propagated through all agent calls)
