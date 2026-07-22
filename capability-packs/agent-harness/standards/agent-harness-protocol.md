# Standard — Agent Harness Protocol (conformance summary)

> This is the **condensed** conformance standard. The full normative protocol lives in the reference runtime
> repo: [`doubts-suplab/agent-harness` → `docs/spec/harness-protocol.md`](https://github.com/doubts-suplab/agent-harness/blob/main/docs/spec/harness-protocol.md).
> A project that activates the `agent-harness-pack` MUST run its agents through a harness-conformant runtime.

## Why

Every agent needs a runtime that makes execution safe, governed, observable, and reproducible. Rather than
re-implement that per project, conform to one protocol. This standard is the checklist; the linked spec is the
authority. The protocol is a generic implementation of the "agent runtime" that
[AIEL](https://github.com/suplab/aether-iel) specifies.

## The non-negotiables (MUST)

1. **Typed envelope.** One `AgentInput{tenantId, userId, context, metadata}` in; one
   `AgentOutput{decision{action, confidence, rationale, autoEnforced}, agentName, executedAt}` out.
   `tenantId`/`userId` validated on every invocation.
2. **Confidence gate in the runtime, centralized, non-disableable.**
   `confidence < 0.8 → autoEnforced=false → human review`. No config/flag/env/API turns it off. Agents never
   set `autoEnforced`. Emit `confidence_gate_bypass_total` — it MUST stay `0`.
3. **Tool registry is default-deny.** Explicit per-agent allowlists; **no wildcards**; out-of-allowlist calls
   refused before any side effect and logged as security events. Supervisor agents hold no tools.
4. **Two-axis decision model.** Static `authorityLevel` (`OBSERVE < SUGGEST < ALERT < RATE_LIMIT < BLOCK`) vs.
   dynamic `DecisionAction` (`ALLOW | BLOCK | ALERT | SUGGEST | DEFER`); an agent may not emit an action beyond
   its authority.
5. **No self-escalation.** Authority is static per Agent Contract; it cannot widen at runtime.
6. **Audit append-only + PII-redacted.** Every `BLOCK`/`ALERT` carries a human-readable explanation.
7. **Safe failure defaults.** Every failure resolves to a non-enforcing decision with lowered confidence —
   never fail open.
8. **Framework-free core.** Adapters (LLM/memory/audit/human-review/observability) depend on the core; the core
   depends on nothing. The `LlmPort` shape follows the apex-sdlc provider abstraction.

## How to conform

- Depend on the reference runtime (`doubts-suplab/agent-harness`) or implement the protocol in your language.
- Define each agent with an **Agent Contract** validated against
  [`agent-contract.schema.json`](https://github.com/doubts-suplab/agent-harness/blob/main/docs/spec/agent-contract.schema.json).
- Verify against the spec's §9 Conformance Checklist.
