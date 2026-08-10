# Reference Architecture — AI-Augmented Service (RAG + governed agent on HALO)

**Stack:** FastAPI · Python 3.12 · Amazon Bedrock (Claude) · Aurora pgvector · HALO (agent-harness) · React · CDK
**Maturity:** Staging · **Manifest:** [`project-manifest.yaml`](project-manifest.yaml) (schema-valid)
**Resolves to packs:** `core · agent-harness · ai-engineering · architecture · aws · delivery · governance · python · react`

A blueprint for a retrieval-augmented assistant that answers over enterprise documents — where **every
model decision is governed by HALO** (confidence gate, tool allowlist, audit, human-review routing), so
the service can never silently auto-answer beyond its confidence.

---

## 1. Context

```
                 ┌───────────────────────── AWS account (eu-west-1) ─────────────────────────┐
                 │                                                                            │
  User ─▶ React ─┼▶ API GW ─▶ Assistant API (FastAPI, Fargate)                                │
                 │               │  ┌─────────────────── HALO runtime (in-process) ────────┐  │
                 │               │  │  confidence gate · tool allowlist · audit · review    │  │
                 │               │  └───────┬───────────────────────┬───────────────────────┘  │
                 │        (retrieve) ▼       (generate, via LLM port) ▼                          │
                 │       Aurora + pgvector            Amazon Bedrock (Claude / Titan)            │
                 │            ▲                                                                  │
  Docs ─▶ SQS ─▶ Ingestion worker ──(chunk · embed · upsert)─┘                                  │
                 └────────────────────────────────────────────────────────────────────────────┘
```

The Assistant API never calls Bedrock directly — it goes **through HALO's LLM port**, so the gate, the
tool registry, and the audit log wrap every generation. Retrieval and generation are both tool-governed.

---

## 2. The governed RAG loop

```
query
  │
  ├─▶ Retriever: embed query → pgvector top-k → grounded passages (+ citations)
  │        └─ zero relevant passages ─────────────▶ DEFER (no grounded answer)   [fast path]
  │
  ├─▶ HALO.invoke(assistant, {query, passages})
  │        agent proposes a Decision(action, confidence, rationale)
  │
  └─▶ HALO confidence gate:
         confidence ≥ threshold  AND grounded  ─▶ ALLOW  → answer with citations
         confidence < threshold  OR ungrounded ─▶ DEFER  → human-review queue (UI shows "pending review")
```

- **Grounding is mandatory.** An answer must cite retrieved passages; the agent DEFERs rather than
  answering from parametric memory alone (reduces hallucination).
- **The gate is non-optional.** It lives in HALO's core and runs on every invocation — the service cannot
  disable it (harness protocol §4). `autoEnforced` is set by HALO, never by the agent.
- **Tool access is default-deny.** The assistant's allowlist is `{retriever.search, bedrock.invoke}`; any
  other tool call is a security event, blocked before side effect (§5).

---

## 3. Agent Contract (governed by construction)

The assistant ships a HALO **Agent Contract** — generate it from EEIK's `ai-engineer`-style blueprint:

```bash
eeik contract --blueprint specialist --name knowledge-assistant --param domain=rag --validate
```

Contract highlights (see [`agent-contract` schema](https://github.com/doubts-suplab/agent-harness/blob/main/docs/spec/agent-contract.schema.json)):

| Field | Value | Why |
|---|---|---|
| authorityLevel | `SUGGEST` | an assistant proposes answers; it never auto-enforces a side effect |
| capabilities | `ALLOW, SUGGEST, DEFER` | within the SUGGEST ceiling (§3.3) |
| confidenceGate.threshold | `0.80` | floor for any externally-visible answer (G-3) |
| toolAccess | `retriever.search (Read), bedrock.invoke (Invoke)` | default-deny; no wildcards |
| failureBehaviour | `LLM unavailable → DEFER, autoEnforced=false` | fail safe, never fabricate |

---

## 4. Ingestion (offline, idempotent)

1. A document lands (S3 event → SQS). The worker **chunks** it (token-bounded, overlap), **embeds** each
   chunk (Bedrock Titan), and **upserts** into `pgvector` keyed by `docId + chunkId` (idempotent re-ingest).
2. Metadata (source, ACL, version) travels with each chunk so retrieval can **filter by entitlement** — a
   user only retrieves passages they're allowed to see.

---

## 5. Non-functional & governance targets

| Concern | Target | How |
|---|---|---|
| Grounded-answer rate | > 0.9 | retrieve-then-generate; DEFER when unretrieved |
| Hallucination guard | citations required | grounding check + gate; ungrounded → DEFER |
| Answer P95 | < 3 s | top-k retrieval + streamed generation |
| Auditability | 100% of decisions | HALO append-only, PII-redacted audit; `confidence_gate_bypass_total == 0` |
| Governance | enterprise | `ai-governance-review` gate; EU AI Act awareness (`ai-governance` standard) |
| Data entitlement | enforced at retrieval | per-chunk ACL filter; no cross-tenant leakage |

---

## 6. Why these choices

- **Govern at the runtime, not the prompt** — a prompt "please be careful" is not a control; HALO's gate,
  registry, and audit are enforced regardless of what the model emits. This is EEIK's governed-generation
  posture (ADR-003) applied to a product.
- **RAG over fine-tuning** — answers stay current with the document corpus and are *citable*; fine-tuning
  is opaque and stale. Revisit fine-tuning only for stable, high-volume, latency-critical narrow tasks.
- **pgvector over a dedicated vector DB** — one datastore (Aurora) for app state *and* embeddings until
  recall/latency at scale justifies OpenSearch/Pinecone. Fewer moving parts to govern and operate.
- **Bedrock behind the LLM port** — the provider is swappable (Bedrock ↔ another) without touching the
  governed loop; the harness owns no LLM (harness protocol: all I/O through ports).

---

## 7. Adopt it

```bash
eeik validate knowledge/reference-architectures/ai-augmented-service/project-manifest.yaml
# resolves to: core, agent-harness, ai-engineering, architecture, aws, delivery, governance, python, react
cp knowledge/reference-architectures/ai-augmented-service/project-manifest.yaml ./project-manifest.yaml
eeik activate --apply
pip install halo-agent-harness   # HALO — the governed runtime this architecture depends on
```

See [`runbook.md`](runbook.md) for operations (gate metrics, review-queue SLAs, ingestion health).
