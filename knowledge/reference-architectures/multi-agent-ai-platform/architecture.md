# Reference Architecture — Multi-Agent AI Platform (supervisor + workers on HALO)

> A governed multi-agent platform: a **supervisor** routes each task to specialist **worker agents**
> (research, code, archive), and **every agent runs on HALO** — centralized confidence gate,
> default-deny tool registry, audit, and human-review routing. The supervisor holds no tools (spec §6);
> workers reach the model only through HALO's LLM port. Distinct from the single-agent
> [`ai-augmented-service`](../ai-augmented-service/architecture.md): this one is about **orchestrating
> many governed agents**.

- **Manifest:** [`project-manifest.yaml`](project-manifest.yaml) — validates + resolves to
  `core, agent-harness, ai-engineering, architecture, aws, delivery, governance, python`.
- **Maturity:** PoC → staging.
- **Deploy:** [`cdk/`](cdk/) (AWS) · **Run locally:** [`local-dev/`](local-dev/) (DynamoDB Local).

---

## Overview

```
User/System ──▶ API Gateway ──▶ FastAPI (ECS Fargate)
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │  Supervisor (routes) │   holds NO tools
                          └──────────┬───────────┘
                        routes to    │
              ┌──────────────┬───────┴───────┬──────────────┐
              ▼              ▼               ▼               ▼
          Research        Code           Archive        (more…)
           Agent          Agent           Agent
              │              │               │
              └──────┬───────┴───────────────┘
                     ▼                    ▼
       HALO runtime (in-process)     DynamoDB
       gate · registry · audit ·     (checkpoints + append-only audit)
       human review                       ▲
                     │                     │
                     ▼                     │
              Amazon Bedrock (Claude) via HALO LLM port
```

Orchestration follows the harness's **Supervisor + Workers** pattern (spec §6): the supervisor
classifies and routes but never executes side effects; the workers act, each with its own authority
ceiling and tool allowlist. LangGraph expresses the graph; HALO governs every node.

## Components

| Component | Tech | Responsibility |
|---|---|---|
| Platform API | FastAPI (ECS Fargate) | Task intake + streaming; submits runs to the supervisor; exposes status |
| Supervisor | LangGraph node (no tools) | Classifies the task, routes to a worker; never acts directly |
| Worker agents | Research / Code / Archive on HALO | Do the work under governance; each a distinct authority + allowlist |
| HALO runtime | `halo-agent-harness` (in-process) | Confidence gate, tool registry, audit, human-review routing |
| Checkpoint store | DynamoDB | LangGraph state — long, multi-step runs survive restarts |
| Foundation model | Amazon Bedrock (Claude) | Supervisor routing + worker reasoning, only via the HALO LLM port |

## Key design decisions

1. **The supervisor holds no tools (spec §6).** Routing is a decision, not a side effect. Only workers
   act, and only through HALO's default-deny tool registry — no wildcards.
2. **Per-worker authority + allowlist.** The research agent may read sources; the code agent may write to
   a scratch workspace; the archive agent may write to the store. No agent can widen its own authority.
3. **Model routing by cost/capability.** A fast, cheap model routes (e.g. a Haiku-class model); balanced
   models do the work (Sonnet-class); a frontier model (Opus-class) is **reserved** for high-stakes
   reasoning only. Routing is a policy, not hardcoded per call.
4. **Checkpointing makes runs resumable.** DynamoDB persists LangGraph state; a failed step resolves to a
   safe `DEFER` (spec §8), never a silent retry-loop.
5. **Human-in-the-loop at high-risk nodes.** For regulated work, interrupt before a high-risk action and
   route to review — which is also what the gate does automatically for low-confidence decisions.

```python
# High-risk nodes pause for approval; low-confidence decisions are DEFERred by the gate automatically.
from langgraph.types import interrupt

def review_node(state: AgentState) -> AgentState:
    if state["risk_level"] == "HIGH":
        decision = interrupt({"message": "High-risk action requires approval",
                              "action": state["proposed_action"]})
        return {"next": "EXECUTE" if decision["approved"] else "ABORT"}
    return {"next": "EXECUTE"}
```

## Governance (why this is on HALO, not raw LangGraph)

Raw LangGraph gives you orchestration but no governance. On HALO, every agent invocation carries the
**typed decision envelope**; the **confidence gate** stamps `auto_enforced` (an agent never sets it);
tool access is **default-deny**; audit is **append-only and PII-redacted**; and `confidence_gate_bypass_total`
MUST stay `0`. The platform inherits all of this for free — it supplies the *agents* and the
*infrastructure adapters* (DynamoDB audit/checkpoint), not the gate/registry/audit.

## Observability

Key metrics for this architecture:

- `agent.supervisor.routing_decision` — which worker was selected (tag by `worker_name`)
- `agent.tool.invocation_count` — tool calls per run (default-deny denials are security events)
- `agent.graph.recursion_depth` — hops before `END` (bound it to catch runaway loops)
- `agent.session.token_usage` — tokens per run, split by model tier
- `agent.decision.defer_rate` — share of decisions routed to human review
- `confidence_gate_bypass_total` — MUST be `0` (alarm on any non-zero)

## Limitations

- LangGraph is Python-only — Java services need a sidecar or a Spring AI alternative.
- Bedrock regional model availability may constrain the routing policy outside `eu-west-1`.
- The DynamoDB checkpointer has no native TTL cleanup — schedule pruning of old threads.

See [`runbook.md`](runbook.md) for operations (routing health, DEFER spikes, review-queue SLAs).
