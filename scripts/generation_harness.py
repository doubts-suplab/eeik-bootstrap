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

    from generation_harness import govern_generation
    govern_generation("agent-generator", producer_fn)   # producer_fn() -> (artifact_text, confidence)

CLI:
    python3 scripts/generation_harness.py demo           # offline, governed showcase (no API key)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable

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


def govern_generation(
    generator_name: str,
    producer: Producer,
    *,
    tenant: str = "eeik",
    user: str = "eeik-cli",
) -> int:
    """Run one generation through the HALO gate. Returns a process exit code.

    Whatever the outcome, the artifact is only ever staged — never applied to live config — because
    generation is SUGGEST authority. The function prints a full governance trace (decision, audit,
    review queue) so ``eeik run --governed`` and ``eeik demo`` show the runtime *in action*.
    """
    print(f"\n{ANSI_BOLD}EEIK Governed Generation{ANSI_RESET}  ·  generator: {ANSI_CYAN}{generator_name}{ANSI_RESET}")

    if not HALO_AVAILABLE:
        # Fail safe: cannot certify the gate → never apply. Stage and warn.
        artifact, confidence = producer()
        staged = _write_staged(generator_name, artifact)
        print(f"  {ANSI_YELLOW}⚠ HALO (agent-harness) is not installed — running UNGOVERNED.{ANSI_RESET}")
        print(f"    Install it for governed generation:  pip install agent-harness")
        print(f"    Fail-safe: artifact staged (not applied) → {staged.relative_to(REPO_ROOT)}\n")
        return 0

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

    # ── governance trace ─────────────────────────────────────────────────────────
    enforced = decision.auto_enforced
    verdict_colour = ANSI_GREEN if not enforced else ANSI_RED
    print(f"  {ANSI_DIM}authority{ANSI_RESET} SUGGEST   "
          f"{ANSI_DIM}action{ANSI_RESET} {decision.action.value}   "
          f"{ANSI_DIM}confidence{ANSI_RESET} {decision.confidence:.2f}")
    print(f"  {ANSI_DIM}gate → auto_enforced:{ANSI_RESET} {verdict_colour}{enforced}{ANSI_RESET}  "
          f"{ANSI_DIM}(G-5: SUGGEST never auto-enforces){ANSI_RESET}")
    print(f"  {ANSI_DIM}bypass counter:{ANSI_RESET} {obs.counter('confidence_gate_bypass_total')}  "
          f"{ANSI_DIM}(must be 0){ANSI_RESET}")

    if review.items:
        item = review.items[0]
        print(f"  {ANSI_CYAN}→ routed to human review{ANSI_RESET}  "
              f"reason={item.reason}  sla={item.sla_seconds}s")
    for entry in audit.entries:
        print(f"  {ANSI_DIM}audit:{ANSI_RESET} {entry.outcome}  \"{entry.rationale}\"")

    print(f"\n  {ANSI_GREEN}✓ Draft staged for approval:{ANSI_RESET} {staged.relative_to(REPO_ROOT)}")
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
