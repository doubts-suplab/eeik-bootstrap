# Runbook — AI-Augmented Service (RAG + governed agent on HALO)

Operational guide for the [AI-Augmented Service reference architecture](architecture.md). The governance
signals below are the ones that matter most for a *governed* AI service — treat gate integrity as P1.

---

## Key signals

| Signal | Where | Healthy |
|---|---|---|
| `confidence_gate_bypass_total` | HALO observability | **0** (any non-zero is a P1 — the gate was bypassed) |
| Grounded-answer rate | app metric `answers.grounded / answers.total` | > 0.9 |
| DEFER rate (→ human review) | app metric `decisions.DEFER` | steady; a spike means retrieval or model degraded |
| Human-review queue age | review-queue oldest item | within SLA (BLOCK-class 1h, else 4h — harness §7.4) |
| Answer P95 latency | CloudWatch `AssistantAPI/latency` | < 3 s |
| Ingestion lag | SQS `ApproximateAgeOfOldestMessage` | draining; < 5 min |
| Retrieval recall (sampled) | offline eval harness | not regressing vs baseline |

## SLOs

- **Gate integrity:** `confidence_gate_bypass_total == 0`, always. **Availability** 99.5%. **Answer P95** < 3 s.

---

## Common incidents

### `confidence_gate_bypass_total` > 0  — P1
The single most important invariant. A non-zero counter means an `autoEnforced=true` decision cleared that
should not have.
1. Freeze auto-answering (feature flag → force DEFER on all).
2. Pull the audit entries for the bypassing agent/correlation ids; identify the decision path.
3. This is a governance breach — engage the AI governance owner; do not resume auto-answer until root-caused.

### DEFER rate spikes (few answers, everything → human review)
1. **Retrieval empty?** pgvector healthy? embeddings present for the queried corpus? A failed ingestion can
   leave a topic un-retrievable → every query DEFERs (correctly, but investigate).
2. **Model degraded?** Bedrock latency/error rate; the failure default is DEFER with lowered confidence.
3. **Threshold too high?** Only change the gate threshold via the Agent Contract + review — never hot-patch
   below the 0.80 floor (G-3).

### Suspected hallucination / ungrounded answer
1. Every answer must carry citations; pull the answer's retrieved passages from the audit trail.
2. If an answer shipped without grounding, the grounding check failed open — treat as **P1**, force DEFER,
   patch the grounding guard, add a regression eval.

### Human-review queue breaching SLA
1. Is anyone draining it? The queue is where low-confidence answers *safely* wait — a stale queue means
   users get no answer, not a wrong one.
2. Scale reviewers or, if the DEFER rate is a false-positive spike, fix retrieval/model first (see above).

### Ingestion backlog
1. Worker running? DLQ depth? A poison document (unparseable) should be parked, not block the queue.
2. Re-ingest is idempotent (`docId + chunkId` upsert) — safe to replay after a fix.

---

## Routine operations

- **Deploy:** CDK per stack; blue/green on Fargate. Alembic migrations before the new task set.
- **Model/prompt change:** goes through the Agent Contract + `ai-governance-review` — a model swap is a
  governed change, not a config tweak. Re-run the offline eval (recall + grounded-answer rate) before rollout.
- **Threshold change:** edit the Agent Contract, validate (`eeik contract … --validate`), review, redeploy.
  Never below 0.80.
- **Corpus refresh:** re-embed changed documents; retrieval reads the new vectors immediately. To rebuild
  the whole index, re-run ingestion — the write path (answers) is unaffected.
- **Entitlement change:** per-chunk ACL metadata drives retrieval filtering; verify no cross-tenant recall
  after any ACL model change (add a retrieval-isolation test).

## Escalation
P1 (gate bypass, ungrounded answer shipped, cross-tenant recall) → AI governance owner + platform on-call.
P2 (elevated DEFER, ingestion backlog, review-queue SLA) → platform on-call. Attach: correlation id(s),
the audit entries, retrieved passages, and the gate/DEFER signal panel.
