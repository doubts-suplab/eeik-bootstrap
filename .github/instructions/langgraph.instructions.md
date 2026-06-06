---
applyTo: "**/langgraph/**, **/graphs/**, **/workflows/**/*.py"
description: "LangGraph StateGraph construction, node functions, edge types, checkpointing, HITL patterns, streaming, subgraphs, and Bedrock integration."
---

# LangGraph — Copilot Instructions

> Applied automatically when working with LangGraph graph files, state definitions, and Python workflow modules. Loaded alongside copilot-instructions.md.

---

## StateGraph Construction

Always define state as a `TypedDict` with field-level `Annotated` reducers. Use `operator.add` for list fields that accumulate across nodes; use default assignment (`field: str`) for scalar fields that overwrite.

```python
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # Accumulates
    user_id: str                                               # Overwrites
    current_step: str                                          # Overwrites
    error: str | None                                          # Overwrites; None = no error
    context: Annotated[list[str], operator.add]               # Accumulates retrieved context
```

### Graph Construction Pattern

```python
from langgraph.graph import StateGraph, END

# Build graph
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("retrieve", retrieve_node)
builder.add_node("generate", generate_node)
builder.add_node("validate", validate_node)
builder.add_node("human_review", human_review_node)

# Set entry point
builder.set_entry_point("retrieve")

# Add fixed edges
builder.add_edge("retrieve", "generate")
builder.add_edge("human_review", "generate")

# Add conditional edges
builder.add_conditional_edges(
    "generate",
    route_after_generate,           # routing function — returns a string key
    {
        "valid": "validate",
        "needs_review": "human_review",
        "error": END,
    }
)

builder.add_edge("validate", END)

# Compile with checkpointer
graph = builder.compile(checkpointer=checkpointer)
```

---

## Node Function Requirements

Every node function must:
- Accept the full state dict as input
- Return a **dict** with only the keys it updates (LangGraph merges partial updates)
- Never mutate the input state directly
- Handle exceptions internally and set the `error` field rather than raising

```python
from typing import Any

def generate_node(state: AgentState) -> dict[str, Any]:
    """Generate a response based on retrieved context."""
    try:
        response = llm.invoke([
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=state["messages"][-1].content),
        ])
        return {
            "messages": [response],       # Appended (Annotated list)
            "current_step": "generated",  # Overwrites
            "error": None,                # Clear any previous error
        }
    except Exception as exc:
        return {
            "error": str(exc),
            "current_step": "error",
        }
```

---

## Edge Types

| Edge Type | Method | Usage |
|-----------|--------|-------|
| Fixed edge | `add_edge(source, target)` | Always transition from source to target |
| Conditional edge | `add_conditional_edges(source, fn, mapping)` | Route based on state; routing function returns a string key |
| Entry point | `set_entry_point(node)` | First node to execute |
| Conditional entry | `set_conditional_entry_point(fn, mapping)` | Choose starting node based on initial state |

### Routing Function Pattern

```python
def route_after_generate(state: AgentState) -> str:
    """Route based on confidence and error state."""
    if state.get("error"):
        return "error"
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    if state.get("requires_human_approval"):
        return "needs_review"
    return "valid"
```

---

## MessagesState for Conversation Graphs

Use `MessagesState` from LangGraph for chat applications — it pre-defines the `messages` field with the correct `add_messages` reducer that handles deduplication by message ID.

```python
from langgraph.graph import MessagesState

class ChatState(MessagesState):
    # MessagesState provides: messages: Annotated[list[AnyMessage], add_messages]
    session_id: str
    user_context: dict[str, str]

# The add_messages reducer automatically handles:
# - Deduplication (updates existing message if same ID)
# - Appending new messages
# - Proper serialization for checkpointing
```

---

## Checkpointer Setup

### SQLite (development and single-instance production)

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# Synchronous
with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)

# Asynchronous
async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
```

### Redis (production, multi-instance)

```python
from langgraph.checkpoint.redis import RedisSaver
from redis import Redis

redis_client = Redis.from_url(
    url=os.environ["REDIS_URL"],          # redis://redis-host:6379/0
    decode_responses=False,                # Must be False for LangGraph
    socket_timeout=5,
    socket_connect_timeout=5,
)

checkpointer = RedisSaver(redis_client)
checkpointer.setup()  # Creates required key structures — call once on startup
graph = builder.compile(checkpointer=checkpointer)
```

### Thread Config — Required for Checkpointing

```python
# Every invocation that uses checkpointing MUST provide a thread_id
config = {"configurable": {"thread_id": "user-session-abc123"}}

result = graph.invoke({"messages": [HumanMessage(content="Hello")]}, config=config)

# Resume from checkpoint (HITL pattern)
graph.invoke(None, config=config)  # None input = resume from last checkpoint
```

---

## Human-in-the-Loop (HITL)

### Interrupt Before/After a Node

```python
# interrupt_before: pause BEFORE executing the named node
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"],   # Graph pauses before this node runs
    interrupt_after=["generate"],         # Graph pauses after this node completes
)

# Execute until interrupt
result = graph.invoke(
    {"messages": [HumanMessage(content=user_input)]},
    config={"configurable": {"thread_id": thread_id}}
)

# Inspect state at interrupt point
snapshot = graph.get_state(config={"configurable": {"thread_id": thread_id}})
pending_messages = snapshot.values["messages"]

# Human updates state and resumes
graph.update_state(
    config={"configurable": {"thread_id": thread_id}},
    values={"human_approved": True, "reviewer_id": "emp_456"},
    as_node="human_review",
)

# Resume execution — pass None as input to continue from checkpoint
final_result = graph.invoke(None, config={"configurable": {"thread_id": thread_id}})
```

---

## Streaming

### `.stream()` — Node-level events

```python
for chunk in graph.stream(
    {"messages": [HumanMessage(content="Analyse this document")]},
    config={"configurable": {"thread_id": thread_id}},
    stream_mode="values",   # "values" = full state after each node; "updates" = partial update dict
):
    print(chunk)
```

### `.astream_events()` — Token-level streaming

```python
async for event in graph.astream_events(
    {"messages": [HumanMessage(content="Summarise")]},
    config={"configurable": {"thread_id": thread_id}},
    version="v2",
):
    if event["event"] == "on_chat_model_stream":
        chunk = event["data"]["chunk"]
        print(chunk.content, end="", flush=True)
    elif event["event"] == "on_chain_end":
        print(f"\n[Node completed: {event['name']}]")
```

---

## Subgraph Pattern

Parent and child graphs must have compatible state schemas. The child graph can only update keys present in the parent state.

```python
# Child graph state — must be a subset of parent state keys
class SubState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sub_result: str

child_builder = StateGraph(SubState)
child_builder.add_node("sub_process", sub_process_node)
child_builder.set_entry_point("sub_process")
child_builder.add_edge("sub_process", END)
child_graph = child_builder.compile()

# Add compiled child graph as a node in parent graph
parent_builder.add_node("run_subgraph", child_graph)
parent_builder.add_edge("preprocess", "run_subgraph")
parent_builder.add_edge("run_subgraph", "postprocess")
```

---

## LangGraph Studio Integration

`langgraph.json` at repo root:

```json
{
  "dependencies": ["."],
  "graphs": {
    "main_graph": "./src/graphs/main.py:graph",
    "research_graph": "./src/graphs/research.py:graph"
  },
  "env": ".env",
  "python_version": "3.12"
}
```

---

## LangGraph + AWS Bedrock Claude Integration

```python
from langchain_aws import ChatBedrock
import boto3

bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name="eu-west-1",
)

llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    client=bedrock_client,
    model_kwargs={
        "max_tokens": 4096,
        "temperature": 0.0,    # 0.0 for deterministic tool-calling graphs
        "top_p": 0.999,
    },
    streaming=True,             # Enable for token-level streaming in astream_events
)

# Bind tools to the model
llm_with_tools = llm.bind_tools(tools=[search_tool, calculator_tool])

def agent_node(state: AgentState) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}
```

---

## Common Graph Topologies

| Topology | Pattern | Use Case |
|----------|---------|---------|
| Linear | A → B → C → END | Simple sequential processing |
| Branching | A → conditional → {B, C} → END | Route based on content/confidence |
| Loop | A → B → conditional → {A (retry), END} | Retry until success or max iterations |
| Supervisor | Supervisor → conditional → {Worker1, Worker2} → Supervisor | Multi-agent orchestration |
| RAG | Retrieve → Grade → conditional → {Generate, Rewrite} | Self-correcting RAG |

### Loop with Max Iterations Guard

```python
class LoopState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    iteration_count: int

def increment_counter(state: LoopState) -> dict:
    return {"iteration_count": state["iteration_count"] + 1}

def should_continue(state: LoopState) -> str:
    if state["iteration_count"] >= 5:
        return "max_iterations_reached"
    if is_complete(state):
        return "done"
    return "continue"
```

---

## Error Handling in Nodes

```python
def risky_node(state: AgentState) -> dict[str, Any]:
    try:
        result = external_api_call(state["context"])
        return {"result": result, "error": None}
    except httpx.TimeoutException:
        return {"error": "API timeout after 30s", "current_step": "retry_needed"}
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            return {"error": "rate_limited", "current_step": "backoff_needed"}
        return {"error": f"HTTP {exc.response.status_code}", "current_step": "error"}
```

---

## Memory Management

| Memory Type | Implementation | Scope |
|------------|---------------|-------|
| Short-term (in-conversation) | LangGraph state dict | Single thread/session |
| Cross-session (user profile) | `store` parameter in `compile(store=InMemoryStore())` | Shared across threads by user_id |
| Long-term (document/knowledge) | Tool — vector store search via LangChain retriever | Accessed by any graph node |

```python
from langgraph.store.memory import InMemoryStore
# In production: use RedisStore or PostgresStore

store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)

# In a node — access cross-session memory
def personalized_node(state: AgentState, store: BaseStore) -> dict:
    user_prefs = store.get(("user_preferences",), state["user_id"])
    # ...
```
