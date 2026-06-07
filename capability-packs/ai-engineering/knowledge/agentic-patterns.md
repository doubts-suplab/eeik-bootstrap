# Agentic AI Patterns

**Pack:** ai-engineering-pack | **Version:** 1.0

---

## 1. Single Agent (ReAct)

**When to use:** Single-domain task, linear reasoning, tool use required.

```
User → Agent (reason → act → observe → reason...) → Result
```

**Frameworks:** LangGraph single node, LangChain AgentExecutor

---

## 2. Supervisor Pattern (Multi-Agent)

**When to use:** Complex tasks requiring different specialists; supervisor routes to the right agent.

```
User → Supervisor Agent
           ↓         ↓          ↓
       Researcher  Analyst  Writer Agent
           └─────────┴──────────┘
                  ↓
              Supervisor aggregates → Result
```

**Framework:** LangGraph with supervisor node + worker subgraphs

---

## 3. RAG (Retrieval-Augmented Generation)

**When to use:** Agent needs to answer questions grounded in a document corpus.

```
User Query → Embed → Vector Search → Retrieved Chunks
                                          ↓
                               LLM + Context → Grounded Answer
```

**Components:** Ingestion pipeline + Vector DB + Retrieval + Generation

---

## 4. Human-in-the-Loop

**When to use:** High-stakes decisions (financial, medical, legal) that require human approval before action.

```
Agent → [interrupt] → Human Review → [resume] → Agent continues
```

**LangGraph:** `interrupt()` + `Command(resume=...)` pattern

---

## 5. Parallel Fan-Out

**When to use:** Multiple independent subtasks that can run concurrently.

```
Coordinator → [fork] → Task A | Task B | Task C → [join] → Aggregate
```

**LangGraph:** Parallel node execution with `Send` API

---

## Model Selection Guide

| Task Type | Recommended Model | Why |
|-----------|------------------|-----|
| Complex reasoning, architecture | claude-sonnet-4-6 | Best reasoning quality |
| High-volume classification | claude-haiku-4-5 | Cost-efficient, fast |
| Code generation | claude-sonnet-4-6 | Code quality + reasoning |
| Embeddings | Amazon Titan Embed v2 | AWS native, cost-efficient |
| Image understanding | claude-sonnet-4-6 | Multimodal capability |
