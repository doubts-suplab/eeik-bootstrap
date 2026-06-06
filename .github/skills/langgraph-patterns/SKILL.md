# LangGraph Patterns Skill

## Trigger

Use this skill when designing or implementing LangGraph agent workflows, state machines, or multi-step LLM pipelines with branching logic.

## What This Skill Does

1. Designs the agent workflow as a directed graph (nodes and edges)
2. Defines the typed `State` schema with appropriate reducers
3. Implements conditional edge routing for dynamic branching
4. Configures checkpointing for resumable long-running workflows
5. Sets up LangSmith tracing for observability
6. Produces a Mermaid diagram of the graph topology

## Inputs Required

- Description of the agent workflow: what problem it solves, what steps are needed
- Available tools (search, code execution, database access, etc.)
- Whether human-in-the-loop breakpoints are required
- State persistence requirements (in-memory vs. database checkpointing)

## Outputs Produced

- Mermaid graph topology diagram
- Typed `State` schema with all fields and reducers
- Complete Python implementation with all nodes, edges, and graph compilation
- LangSmith tracing configuration
- Termination condition documentation

## Common Patterns

- **ReAct Agent**: model → tools → model loop with termination condition
- **Supervisor**: orchestrator routes tasks to specialist sub-agents
- **Plan-and-Execute**: planner generates plan; executor works through steps
- **Reflection**: generator → critic → refined output loop

## Standards Applied

See `.github/instructions/langgraph.instructions.md`

## Key Safety Rule

Every graph with cycles must have a maximum iteration count. Infinite loops are a production and cost risk.

## Related Agents

- `langraph-engineer` — Claude Code agent for LangGraph implementation
- `a2a-engineer` — for multi-agent communication design
- `mcp-engineer` — for tool integration via MCP
