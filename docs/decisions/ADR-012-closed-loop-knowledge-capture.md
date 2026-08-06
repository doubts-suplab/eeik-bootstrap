# ADR-012 — Closed-loop knowledge capture: audit logs become staged lessons

**Date:** 2026-08-06
**Status:** Accepted
**Deciders:** EEIK core team
**Context:** EEIK platform transformation — closing the loop (ROADMAP Tier 3)

---

## Context and Problem Statement

EEIK's pitch is "build projects, reuse knowledge, generate intelligence" — *every project should leave
the org smarter*. But the learning loop was open: HALO (and its consumers, e.g. APEX) already produce
an append-only, PII-redacted audit trail where every `BLOCK` / `ALERT` and every low-confidence
decision routed to a human carries a human-readable rationale — and none of it flowed back into EEIK's
`knowledge/` layer. The most information-rich moments a governed run produces (an agent over-reached
its tool allowlist; a generation was too uncertain to auto-enforce) evaporated in a log instead of
becoming a reusable lesson.

Meanwhile `knowledge/lessons-learned/` and the `/capture-lesson` command existed but were *entirely
manual* — a human had to notice, classify, and write each lesson. Nothing connected the runtime's own
signal to the knowledge base.

## Decision

**Mechanize the audit → lesson path as a governed generation.** `eeik/lessons.py` ingests audit
records (HALO's audit port shape / APEX's `audit_log`, field-aliased so a raw export feeds straight
in), selects the *learnable* ones, and drafts a lesson per theme in the repository's `LL-NNN` format:

- **Learnable** = a `BLOCK`/`ALERT`/`DEFER`, a human-review outcome, or confidence below the 0.80 gate
  floor. Routine `ALLOW`s are ignored.
- Records are **grouped by theme** (agent + rationale stem) so a recurring block yields *one* lesson
  with a signal-strength count, not N duplicates.
- Each draft carries what the machine can know for certain (what happened, the decision, the
  rationale, occurrence count) and leaves **Root Cause / Fix as curation stubs** for a human.

Crucially, **writing knowledge is a generation, and generation is SUGGEST authority** (ADR-003), so the
capture is routed through HALO's `run_generation`: the batch is staged under `.eeik-staging/lessons/`
with `auto_enforced=False` and never committed to `knowledge/lessons-learned/`. The machine *proposes*;
a human curates and promotes. It fails safe when HALO is absent, and is deterministic/offline (the
lesson skeleton is synthesised from audit fields — no LLM, no API key) so the governed path is always
exercisable.

Surfaced on all three surfaces (ADR-006/007): `eeik lessons --from audit.json` (CLI),
`eeik.capture_lessons(records)` (SDK), and `eeik_capture_lessons` (MCP) — each returning the drafted
lessons, staged paths, and the governance verdict, with `curated_lessons()` / `eeik lessons --list`
to read what's already been promoted.

## Considered Options

1. **Governed, staged, human-curated (chosen)** — the runtime's own signal drives lesson drafts, but
   nothing enters the knowledge base without a human, matching the SUGGEST-authority rule for all EEIK
   generation.
2. **Auto-commit lessons from audit logs** — rejected: it would let an agent's mistakes rewrite the
   org's knowledge base unreviewed, violating the confidence gate's whole point (and risking noise).
3. **Keep capture fully manual** (`/capture-lesson` only) — rejected: the highest-signal events (the
   ones the runtime already flagged) are exactly the ones a tired human forgets to write up.

## Consequences

**Positive**
- The learning loop closes: `HALO/APEX audit → eeik lessons → staged LL-NNN drafts → human curation`.
- Recurring governance events become one high-signal lesson, not noise.
- Same governance guarantee as all EEIK generation: staged, `auto_enforced=False`, never auto-applied.

**Negative / trade-offs**
- Drafts still need human curation to fill Root Cause / Fix — by design; the machine won't invent them.
- Lesson quality depends on audit-rationale quality; poor rationales yield thin drafts (a nudge to
  improve the upstream audit messages).

## Related

- ADR-003 (generators run on HALO), ADR-006 (MCP), ADR-007 (SDK). `eeik/lessons.py`,
  `eeik/generation.py`, `tests/test_lessons.py`, `knowledge/lessons-learned/`.
