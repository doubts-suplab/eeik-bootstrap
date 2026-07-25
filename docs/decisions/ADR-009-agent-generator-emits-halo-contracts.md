# ADR-009 — The agent-generator emits HALO Agent Contracts by construction

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — closing the loop from generation to runtime governance

---

## Context and Problem Statement

EEIK's agent-generator produces a `.agent.md` **persona** — a prompt/behaviour spec for a tool like
Claude Code. But an agent's *governance* — its authority ceiling, the DecisionActions it may emit, its
confidence-gate threshold, its tool allowlist, its safe failure behaviour — lived nowhere machine-readable.
HALO (`agent-harness`) defines exactly that as the **Agent Contract**
(`docs/spec/agent-contract.schema.json`, spec §10): the static envelope a conformant runtime loads at
startup. AIEL specifies the contract; HALO enforces it; but the chain broke in the middle — EEIK generated
personas, not contracts. Nothing guaranteed a generated agent was *runtime-governable*.

## Decision

**EEIK emits a HALO-conformant Agent Contract for every generated agent, deterministically, from the
blueprint archetype** (`eeik/contract.py`; `eeik contract` / `eeik.agent_contract(...)`).

The build is **deterministic, not LLM-driven**, and the archetype fixes governance so a contract *cannot*
over-reach by construction:

| Blueprint | authorityLevel | Rationale |
|---|---|---|
| investigator | `OBSERVE` | read-only analysis (RCA, forensics) |
| architect / engineer / specialist / planner / coordinator | `SUGGEST` | drafts; never auto-enforce |
| reviewer | `ALERT` | advisory findings; may auto-enforce when confident |
| auditor | `BLOCK` | security / compliance gate |

- **Capabilities** are derived from the authority (every action within the ceiling, §3.3) — so a
  generated contract can never declare a DecisionAction beyond its authority.
- **Confidence-gate threshold** is derived from the authority and never below the **0.80 floor** (G-3):
  ALERT 0.80, BLOCK 0.95.
- **Tool allowlist** comes from the blueprint's `tools_allowed`, mapped to Read/Write/Invoke permissions;
  **coordinators (supervisors) get an empty allowlist** (T-4).
- **Failure behaviour** always resolves to a safe `DEFER` with `autoEnforced=false`.
- The **governance sign-off is left unsigned** — the contract is a *draft* a human approves (consistent
  with governed generation, ADR-003).

**Validation reuses HALO's own validator.** `eeik.validate_agent_contract` calls
`agent_harness.contract.validate_contract` (JSON Schema + the §3.3 semantic binding rule) when the harness
and schema are locatable (editable install, `$AGENT_CONTRACT_SCHEMA`, or a sibling `agent-harness` repo).
When they are not, generation still works and validation is reported as *skipped* — fail-safe, no hard
dependency. EEIK does **not** vendor a copy of the schema (that would drift); HALO remains the authority.

## Considered Options

1. **Deterministic contract from the archetype, validated by HALO (chosen)** — governance is a property
   of the blueprint, not of prompt text; provably conformant; no schema duplication.
2. **Have the LLM emit the contract alongside the persona** — rejected: governance fields (authority,
   threshold, tool allowlist) must be deterministic and bounded, not model-authored.
3. **Vendor the contract schema into EEIK and validate locally** — rejected: reintroduces the schema
   drift ADR-004/ADR-005 worked to remove; HALO owns the contract schema.

## Consequences

**Positive**
- The chain closes: **AIEL specifies → EEIK generates a contract-conformant agent → HALO runs it.**
- Every generated agent is runtime-governable by construction; all 8 blueprints validate against HALO's
  real schema + binding rule (tested).
- Reuses HALO's validator — one source of truth for what "conformant" means.

**Negative / trade-offs**
- Validation is best-effort when the harness/schema aren't installed (reported as skipped).
- The blueprint→authority mapping is an EEIK policy; changing it changes generated governance.

## Related

- ADR-003 (governed generation), ADR-006/007 (MCP/SDK). `eeik/contract.py`, `tests/test_contract.py`.
- HALO `docs/spec/agent-contract.schema.json`, `agent_harness.contract.validate_contract`.
