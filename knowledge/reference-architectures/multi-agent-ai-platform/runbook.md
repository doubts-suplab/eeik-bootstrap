# Runbook — Multi-Agent AI Platform (supervisor + workers on HALO)

Operating the platform: what to watch, and how to respond. Governance is enforced by HALO in-process —
most incidents are about routing health, review-queue flow, and runaway graphs, not the gate itself.

## Key signals

| Signal | Meaning | Healthy |
|---|---|---|
| `confidence_gate_bypass_total` | Governed decisions that skipped the gate | **0** (always) |
| `agent.decision.defer_rate` | Share of decisions routed to human review | steady; no sudden spikes |
| `agent.supervisor.routing_decision` | Worker selection distribution | matches expected task mix |
| `agent.graph.recursion_depth` p99 | Hops before `END` | below the configured bound |
| review-queue age p95 | Time a DEFERred decision waits for a human | within SLA |

## SLOs

- **Bypass counter:** `confidence_gate_bypass_total == 0` — any non-zero is a P1.
- **Run completion:** p95 end-to-end run latency within target for the task class.
- **Review SLA:** 95% of DEFERred decisions actioned within the queue SLA (default 4h).

## Common incidents

### `confidence_gate_bypass_total` > 0 — P1
The gate was bypassed — a governance invariant is broken. Freeze auto-actions, capture the offending
run_id from the audit table, and page the platform owner. The gate lives in HALO core and cannot be
disabled by config, so a non-zero here means a code/deploy regression — roll back.

### Routing collapse (supervisor sends everything to one worker)
Check `agent.supervisor.routing_decision` distribution. Usually a prompt/classifier regression or a
worker that's erroring so the supervisor retries onto a fallback. Inspect recent audit entries for that
worker; roll back the supervisor prompt if the shift aligns with a deploy.

### DEFER rate spikes (everything → human review)
The gate is doing its job, but something upstream lowered confidence — a degraded model, a broken tool
the workers depend on, or ambiguous inputs. Check tool denials and model errors; the queue will drain
once the cause is fixed. Do **not** lower the threshold to clear the queue.

### Runaway graph (recursion_depth climbing)
A cycle isn't terminating. The depth bound should cap it to a safe `DEFER`; if runs still hang, lower the
bound and add an explicit `END` condition to the offending node. Inspect the checkpoint for the stuck
`thread_id`.

### Review-queue breaching SLA
Not enough reviewers for the DEFER volume. Add reviewers or triage by risk; audit shows each pending
decision's rationale and age. Never auto-approve to clear the backlog.

### Checkpoint store throttling
DynamoDB on-demand should absorb bursts; if throttled, check for hot `thread_id` partitions (a single
run looping) and confirm PITR/retention. Prune old threads (no native TTL).

## Routine operations

- **Add a worker agent:** define its authority ceiling + tool allowlist, register it, wire a supervisor
  route. Never give the supervisor tools.
- **Change the routing policy:** update the model-tier map (route/worker/high-stakes) — it's policy, not
  per-call code.
- **Rotate models:** swap the Bedrock model id behind the HALO LLM port; agents are unaffected.
- **Prune checkpoints:** scheduled job deletes threads older than the retention window.

## Escalation

1. Platform on-call (routing, graph, queue).
2. AI governance owner (gate, audit, review policy).
3. Cloud/infra on-call (DynamoDB, Bedrock quota, Fargate).
