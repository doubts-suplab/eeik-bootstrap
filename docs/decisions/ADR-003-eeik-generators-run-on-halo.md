# ADR-003 — EEIK generators run on the HALO agent-harness

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — governing EEIK's own generation layer

---

## Context and Problem Statement

EEIK's generators (`repository-generator`, `agent-generator`, `governance-generator`,
`knowledge-generator`, `project-analyzer`) are *agents*: they take a manifest or a repo scan, call an
LLM, and emit artifacts (repositories, agents, ADRs, governance profiles). Historically this ran
through `scripts/claude_harness.py`, which shells out to `claude --print` and writes the result
straight to disk.

That execution was **ungoverned**:

- **No confidence gate** — a low-confidence draft was written as if it were high-confidence output.
- **No tool registry** — the generator inherited whatever tools the `claude` CLI had.
- **No audit trail** — nothing recorded *what* was generated, *why*, or at what confidence.
- **No human-review routing** — generated repos/agents landed with no approval step.
- **It failed open** — a partial or bad generation still produced files.

This is precisely the anti-pattern that [HALO (`agent-harness`)](https://github.com/doubts-suplab/agent-harness)
exists to remove — and EEIK already ships the `agent-harness` capability pack telling *downstream*
projects to adopt it. EEIK was not dogfooding its own recommendation.

---

## Decision

**EEIK's generators run on HALO.** Every LLM-driven generation flows through
`Harness().invoke(agent, input)` (`eeik/generation.py`):

- Each generator is modelled as a HALO **`Agent`** with a static **`SUGGEST`** authority ceiling.
- Generation therefore **can never auto-enforce** (gate rule G-5: OBSERVE/SUGGEST-authority agents
  never auto-enforce, regardless of confidence). The artifact is written to a **staging area**
  (`.eeik-staging/`) and a **human-review** item is enqueued.
- Every run produces an **append-only, PII-redacted audit entry** and emits the
  `confidence_gate_bypass_total` counter (which must stay `0`).
- When HALO is not installed, generation **fails safe**: it stages the draft, warns, and never
  touches live configuration.

"AI drafts; a human approves and commits" becomes a **property of the runtime**, not a convention —
the same guarantee APEX relies on for its SUGGEST-authority SDLC phases.

---

## Considered Options

1. **Run generators on HALO (chosen)** — one conformant, audited, gated path; dogfoods the pack EEIK
   already ships; identical governance story to APEX.
2. **Re-implement a bespoke gate inside EEIK** — rejected: duplicates HALO, and the harness protocol
   forbids a confidence gate living anywhere but the runtime core.
3. **Leave generation ungoverned** — rejected: fails open, no audit, contradicts EEIK's own golden
   rules and the `agent-harness` pack it publishes.

---

## Consequences

**Positive**
- Generation is auditable, gated, and safe-by-default; drafts are never silently applied.
- EEIK consumes HALO exactly as APEX and aether-grid do — a fourth first-class consumer of the runtime.
- Agents EEIK generates can be emitted as HALO Agent Contracts (authority, tool allowlist, threshold),
  closing the loop: EEIK generates a contract conforming to HALO's schema → HALO runs it.

**Negative / trade-offs**
- EEIK gains an optional dependency on `agent-harness` (Python). Mitigated by the fail-safe path when
  it is absent.
- Generation now has an explicit approval step (staging) rather than writing straight to the tree —
  intentional, but a workflow change for existing users.

**Follow-ups**
- `agent-generator` emits `agent-contract.schema.json`-conformant contracts alongside the persona file.
- CI runs `eeik demo` as a smoke test of the governed path.

---

## Related

- ADR-004 — Capability packs are versioned; `eeik.lock` records adopted versions.
- `agent-harness` spec §4 (confidence gate), §10 (Agent Contract).
