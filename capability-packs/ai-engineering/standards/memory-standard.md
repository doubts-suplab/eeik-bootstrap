# Agent Memory Standard

**Pack:** ai-engineering-pack | **Version:** 1.0

---

## Memory Patterns

| Pattern | When to Use | Technology |
|---------|------------|------------|
| In-session | Conversation context, short-lived tasks | LangGraph state |
| Persistent DB | Long-lived user preferences, task history | PostgreSQL / DynamoDB |
| Vector Store | Semantic retrieval, RAG, knowledge bases | pgvector / OpenSearch / Pinecone |
| None | Stateless one-shot tasks | — |

---

## Memory Design Rules

- **PII must never be stored in agent memory** without explicit user consent and encryption
- In-session state: define the state schema explicitly (no untyped dicts in production)
- Persistent memory: define TTL for every stored object — no indefinite retention
- Vector store: chunk documents consistently (chunk size, overlap — document in architecture)
- Memory access must be scoped: agent A cannot read agent B's memory without explicit design

---

## LangGraph State Pattern

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # conversation history
    context: dict                              # retrieved RAG context
    task_id: str                               # correlation ID
    iteration_count: int                       # guard against infinite loops
    # Never: raw PII fields
```

---

## Memory Governance

For regulated domains:
- All stored data must have a defined retention period
- Data subject requests (GDPR Article 17) must be supported — design for deletion
- Memory contents must be loggable for audit (excluding PII)
