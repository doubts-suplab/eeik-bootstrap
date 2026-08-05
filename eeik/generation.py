#!/usr/bin/env python3
"""
EEIK Generation Harness — run EEIK's own generators *on* HALO (the agent-harness runtime).

EEIK's generators are agents: they take a manifest, call an LLM, and emit artifacts (repos, agents,
ADRs). Historically that ran ungoverned through ``claude --print`` — no confidence gate, no audit,
no human-review routing, and it failed *open* (a low-confidence draft was written straight to disk).

That is exactly the anti-pattern HALO exists to remove, and EEIK already ships the ``agent-harness``
capability pack telling *downstream* projects to adopt it. This module closes the dogfooding gap
(ADR-003): every generation now flows through ``Harness().invoke(...)``.

Because generation is a **SUGGEST-authority** activity, the harness gate (rule G-5) guarantees it can
*never* auto-enforce — the artifact is always written to a **staging area** and a **human-review**
item is enqueued. "AI drafts; a human approves and commits" becomes a property of the runtime, not a
convention. When HALO is not installed we **fail safe**: stage, warn, and never touch live config.

    from eeik.generation import govern_generation
    govern_generation("agent-generator", producer_fn)   # producer_fn() -> (artifact_text, confidence)

CLI:
    python3 -m eeik demo           # offline, governed showcase (no API key)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).parent.parent
STAGING_DIR = REPO_ROOT / ".eeik-staging"

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_CYAN = "\033[96m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"

# A producer runs the underlying generation and returns (artifact_text, confidence[0..1]).
Producer = Callable[[], "tuple[str, float]"]

try:
    from agent_harness import (
        Agent,
        AgentInput,
        AuthorityLevel,
        Decision,
        DecisionAction,
        Harness,
    )
    from agent_harness.adapters.inmemory import (
        InMemoryAudit,
        InMemoryHumanReview,
        InMemoryKillSwitch,
        InMemoryObservability,
    )

    HALO_AVAILABLE = True
except ImportError:  # HALO not installed — the seam still works, fail-safe.
    HALO_AVAILABLE = False


# ── the generator, expressed as a HALO agent ─────────────────────────────────────

if HALO_AVAILABLE:

    class GeneratorAgent:
        """An EEIK generator as a HALO agent (spec §10).

        Authority is fixed at SUGGEST: generation proposes drafts and can never auto-enforce
        (gate rule G-5). The agent runs the producer and proposes a SUGGEST decision; the harness
        owns ``auto_enforced`` and the routing to human review.
        """

        def __init__(self, generator_name: str, producer: Producer) -> None:
            self.name = f"eeik-{generator_name}"
            self.authority_level = AuthorityLevel.SUGGEST
            self.capabilities = frozenset({DecisionAction.SUGGEST, DecisionAction.DEFER})
            self._producer = producer
            self.artifact: str = ""

        def run(self, request: AgentInput, tools) -> Decision:  # noqa: ANN001 (ToolInvoker)
            self.artifact, confidence = self._producer()
            confidence = max(0.0, min(1.0, float(confidence)))
            return Decision(
                action=DecisionAction.SUGGEST,
                confidence=confidence,
                rationale=(
                    f"{self.name} produced a draft artifact "
                    f"({len(self.artifact)} chars) for human review."
                ),
            )


def _write_staged(generator_name: str, artifact: str) -> Path:
    out_dir = STAGING_DIR / generator_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "artifact.md"
    out_file.write_text(artifact, encoding="utf-8")
    return out_file


# ── structured outcome (the SDK/MCP surface) ─────────────────────────────────────

@dataclass(frozen=True)
class GenerationOutcome:
    """The governed result of one generation — JSON-serialisable, no console coupling.

    The invariant every field defends: generation is SUGGEST authority, so ``auto_enforced`` is
    always ``False`` and the draft is always *staged*, never applied. A consumer (CLI, SDK, MCP)
    reads this to prove the governed path ran; it never receives an auto-applied artifact.
    """

    generator: str
    halo_available: bool
    producer_kind: str            # "offline-demo" | "registered" | "llm"
    action: str | None            # None only when HALO is absent (fail-safe, ungoverned stage)
    confidence: float | None
    auto_enforced: bool           # MUST be False — SUGGEST never auto-enforces (gate rule G-5)
    staged: bool                  # the artifact was written to staging, not live config
    staged_path: str              # path relative to the repo root
    bypass_total: int             # confidence_gate_bypass_total — MUST be 0
    review: dict[str, Any] | None  # {"reason", "slaSeconds"} when routed to a human
    audit: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifact: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_generation(
    generator_name: str,
    producer: Producer,
    *,
    producer_kind: str = "offline-demo",
    tenant: str = "eeik",
    user: str = "eeik-cli",
) -> GenerationOutcome:
    """Run one generation through the HALO gate and return a structured, staged-only outcome.

    This is the shared core behind ``eeik demo`` / ``eeik run --governed`` (CLI), ``eeik.generate``
    (SDK), and the ``eeik_generate`` MCP tool — one implementation, three surfaces. It performs **no**
    console output; ``govern_generation`` formats a trace from the returned outcome. Whatever the
    outcome, the artifact is only ever *staged* — never applied — because generation is SUGGEST
    authority. When HALO is not installed we **fail safe**: stage, warn, and never certify the gate.
    """
    if not HALO_AVAILABLE:
        artifact, confidence = producer()
        staged = _write_staged(generator_name, artifact)
        return GenerationOutcome(
            generator=generator_name,
            halo_available=False,
            producer_kind=producer_kind,
            action=None,
            confidence=max(0.0, min(1.0, float(confidence))),
            auto_enforced=False,
            staged=True,
            staged_path=str(staged.relative_to(REPO_ROOT)),
            bypass_total=0,
            review=None,
            audit=[],
            warnings=[
                "HALO (agent-harness) is not installed — generation ran UNGOVERNED. "
                "Install it (pip install agent-harness) for a certified gate. Fail-safe: the artifact "
                "was staged, not applied.",
            ],
            artifact=artifact,
        )

    audit = InMemoryAudit()
    review = InMemoryHumanReview()
    obs = InMemoryObservability()
    harness = Harness(
        audit=audit,
        human_review=review,
        observability=obs,
        kill_switch=InMemoryKillSwitch(),
    )

    agent = GeneratorAgent(generator_name, producer)
    request = AgentInput(
        tenant_id=tenant,
        user_id=user,
        context={"generator": generator_name},
        metadata={"correlationId": f"gen-{generator_name}"},
    )
    output = harness.invoke(agent, request)
    decision = output.decision
    staged = _write_staged(generator_name, agent.artifact)

    review_item: dict[str, Any] | None = None
    if review.items:
        item = review.items[0]
        review_item = {"reason": item.reason, "slaSeconds": item.sla_seconds}

    return GenerationOutcome(
        generator=generator_name,
        halo_available=True,
        producer_kind=producer_kind,
        action=decision.action.value,
        confidence=decision.confidence,
        auto_enforced=decision.auto_enforced,
        staged=True,
        staged_path=str(staged.relative_to(REPO_ROOT)),
        bypass_total=obs.counter("confidence_gate_bypass_total"),
        review=review_item,
        audit=[{"outcome": e.outcome, "rationale": e.rationale} for e in audit.entries],
        artifact=agent.artifact,
    )


def govern_generation(
    generator_name: str,
    producer: Producer,
    *,
    producer_kind: str = "offline-demo",
    tenant: str = "eeik",
    user: str = "eeik-cli",
) -> int:
    """Run one generation through the HALO gate and print a governance trace. Returns an exit code.

    Thin console wrapper over :func:`run_generation` — the CLI/demo surface. The structured outcome
    is the source of truth; this only formats it.
    """
    print(f"\n{ANSI_BOLD}EEIK Governed Generation{ANSI_RESET}  ·  generator: {ANSI_CYAN}{generator_name}{ANSI_RESET}")
    outcome = run_generation(
        generator_name, producer, producer_kind=producer_kind, tenant=tenant, user=user,
    )

    if not outcome.halo_available:
        print(f"  {ANSI_YELLOW}⚠ HALO (agent-harness) is not installed — running UNGOVERNED.{ANSI_RESET}")
        print(f"    Install it for governed generation:  pip install agent-harness")
        print(f"    Fail-safe: artifact staged (not applied) → {outcome.staged_path}\n")
        return 0

    enforced = outcome.auto_enforced
    verdict_colour = ANSI_GREEN if not enforced else ANSI_RED
    print(f"  {ANSI_DIM}authority{ANSI_RESET} SUGGEST   "
          f"{ANSI_DIM}action{ANSI_RESET} {outcome.action}   "
          f"{ANSI_DIM}confidence{ANSI_RESET} {outcome.confidence:.2f}")
    print(f"  {ANSI_DIM}gate → auto_enforced:{ANSI_RESET} {verdict_colour}{enforced}{ANSI_RESET}  "
          f"{ANSI_DIM}(G-5: SUGGEST never auto-enforces){ANSI_RESET}")
    print(f"  {ANSI_DIM}bypass counter:{ANSI_RESET} {outcome.bypass_total}  "
          f"{ANSI_DIM}(must be 0){ANSI_RESET}")

    if outcome.review:
        print(f"  {ANSI_CYAN}→ routed to human review{ANSI_RESET}  "
              f"reason={outcome.review['reason']}  sla={outcome.review['slaSeconds']}s")
    for entry in outcome.audit:
        print(f"  {ANSI_DIM}audit:{ANSI_RESET} {entry['outcome']}  \"{entry['rationale']}\"")

    print(f"\n  {ANSI_GREEN}✓ Draft staged for approval:{ANSI_RESET} {outcome.staged_path}")
    print(f"  {ANSI_DIM}Approve by reviewing and moving the artifact into place, then commit.{ANSI_RESET}\n")
    return 0


# ── offline demo producer ────────────────────────────────────────────────────────

def _demo_producer() -> tuple[str, float]:
    """A deterministic, offline stand-in for a real LLM generation (no API key needed)."""
    artifact = (
        "---\n"
        "name: refund-eligibility-agent\n"
        "authority_level: SUGGEST\n"
        "tool_allowlist: [read_policy, read_ledger]\n"
        "confidence_threshold: 0.80\n"
        "---\n\n"
        "# refund-eligibility-agent\n\n"
        "Proposes refund eligibility decisions from policy + ledger context. Emitted as a HALO\n"
        "Agent Contract so it is runtime-governed by construction.\n"
    )
    return artifact, 0.72  # below the 0.80 bar — the gate will route to review either way


def offline_producer(generator: str, spec: str | None = None) -> Producer:
    """A deterministic, offline producer for any generator (no API key / network).

    Real LLM-backed generation requires the ``claude`` CLI or an API key and lives behind
    ``eeik run``; when neither is available this stand-in keeps the *governed path* exercisable —
    the point being to demonstrate the gate/stage/review behaviour, not the model output. The draft
    echoes the requested generator and spec so a caller can see their intent was received.
    """

    def _produce() -> tuple[str, float]:
        intent = (spec or "").strip() or "(no spec provided)"
        artifact = (
            f"# Draft from `{generator}` (offline)\n\n"
            f"**Requested intent:** {intent}\n\n"
            "> This is a deterministic offline draft produced without an LLM. It exists to exercise\n"
            "> EEIK's *governed* generation path: SUGGEST authority, staged for human review, never\n"
            "> auto-applied. Install `agent-harness` and wire an LLM-backed producer via `eeik run`\n"
            "> for real content.\n"
        )
        return artifact, 0.72  # below the 0.80 bar → routed to review

    return _produce


def resolve_producer(generator: str, spec: str | None = None) -> tuple[Producer, str]:
    """Return ``(producer, producer_kind)`` for a generator.

    v1: always the deterministic offline producer (``producer_kind='offline-demo'``). The seam is
    here so a future LLM-backed producer (``eeik run`` with an API key) can register per generator
    without changing the SDK/MCP callers.
    """
    return offline_producer(generator, spec), "offline-demo"


def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK generation harness (HALO-governed)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="Offline governed-generation showcase (no API key)")
    args = parser.parse_args()

    if args.cmd == "demo":
        print(f"{ANSI_BOLD}── EEIK in action: a generator running on HALO ──{ANSI_RESET}")
        rc = govern_generation("agent-generator", _demo_producer)
        if HALO_AVAILABLE:
            print(f"{ANSI_DIM}The draft was governed by the same runtime APEX uses for its SDLC "
                  f"phase agents.{ANSI_RESET}\n")
        return rc
    return 1


if __name__ == "__main__":
    sys.exit(main())
