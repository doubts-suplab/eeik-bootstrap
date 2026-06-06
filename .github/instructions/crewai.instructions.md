---
applyTo: "**/crewai/**/*.py,**/crew/**/*.py,**/agents/**/*.py"
---

# CrewAI Development Standards

## Agent Design

- Define `role`, `goal`, and `backstory` for every agent — all three are required for effective specialisation
- Keep each agent's role narrowly focused — one clear responsibility per agent
- Assign only the tools each agent needs — do not give all tools to all agents
- Use `verbose=True` during development; disable or redirect output in production

## Task Design

- Every task must have a `description`, `expected_output`, and assigned `agent`
- Use `context=[prior_task]` to chain outputs between tasks
- Define `expected_output` with enough specificity to guide the agent's output format
- Prefer Pydantic model outputs for structured data tasks

## Process Selection

- Use `Process.sequential` for ordered, dependent task chains
- Use `Process.hierarchical` only when a manager agent must dynamically route to workers
- Always define `max_rpm` or `max_execution_time` to prevent runaway crew execution

## Tool Integration

- Subclass `BaseTool` for all custom tools; annotate `_run` with type hints
- Handle tool errors gracefully — return error messages as strings, never raise unhandled exceptions
- Enable tool caching (`cache_function`) for expensive or external-calling tools

## Safety

- Always test crew output with representative inputs before production deployment
- Monitor token usage across all agents in a crew — multi-agent costs accumulate quickly
- Implement output validation before passing crew results to downstream systems
