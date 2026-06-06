# Multi-Agent System Design Workflow

Design a multi-agent AI system to solve the following problem.

**Problem:** $PROBLEM_DESCRIPTION
**Framework Preference:** LangGraph / CrewAI / AutoGen / Custom A2A

## Workflow Steps

### Step 1 — Problem Decomposition
Before designing agents, decompose the problem:
- [ ] What are the distinct subtasks that must be completed?
- [ ] Which subtasks can run in parallel vs. must be sequential?
- [ ] What information must flow between subtasks?
- [ ] Where do human decisions need to be inserted?

### Step 2 — Agent Topology Design
Define the agent architecture:
- [ ] List each agent with: name, role, capability scope, tools available
- [ ] Define the orchestration pattern (supervisor, peer-to-peer, pipeline)
- [ ] Design the communication protocol (task schema, context object)
- [ ] Identify where output validation between agents is needed

### Step 3 — State & Context Design
Design the shared state:
- [ ] Define the typed state schema (Pydantic model / TypedDict)
- [ ] Identify which state fields accumulate (require reducers)
- [ ] Design context pruning for long chains (token budget management)
- [ ] Define checkpoint strategy for resumability

### Step 4 — Safety Design
Before implementation, define:
- [ ] Maximum iteration count for any agent loop
- [ ] Timeout per agent call
- [ ] Human-in-the-loop gates and their trigger conditions
- [ ] Rollback/abort mechanism for stuck pipelines
- [ ] Output validation before passing to downstream agents

### Step 5 — Implementation
Activate the appropriate framework agent:
- **LangGraph** → `langraph-engineer` agent
- **CrewAI** → `crewai-engineer` agent
- **AutoGen** → `autogen-engineer` agent
- **Custom A2A** → `a2a-engineer` agent

### Step 6 — Observability Setup
- [ ] Configure LangSmith / logging for all agent interactions
- [ ] Implement token usage tracking across all agents
- [ ] Produce a test harness with representative inputs

## Output

Agent topology diagram, typed state schema, complete implementation, and safety controls documentation.
