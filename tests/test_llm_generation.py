"""LLM-backed generation tests — the real (LLM) producer path, still HALO-governed.

Generation prefers a real LLM-backed producer when an ``LlmPort`` is available and fails safe to the
deterministic offline producer otherwise. We inject HALO's ``StubLlm`` so these run offline with no
API key: the stub stands in for the Anthropic adapter, exercising the same producer/governance seam.
"""

from __future__ import annotations

import importlib

import pytest

pytest.importorskip("halo_agent_harness", reason="halo-agent-harness not installed")

from halo_agent_harness.adapters.llm_stub import StubLlm  # noqa: E402

generation = importlib.import_module("eeik.generation")


DRAFT = "---\nname: refund-agent\nauthority_level: SUGGEST\n---\n\n# refund-agent\n\nA governed draft."


# ── producer selection ──────────────────────────────────────────────────────────

def test_resolve_producer_uses_llm_when_port_injected():
    producer, kind = generation.resolve_producer(
        "agent-generator", spec="a refund agent", llm_port=StubLlm(reply=DRAFT)
    )
    assert kind == "llm"
    text, confidence = producer()
    assert text == DRAFT
    # SUGGEST authority: an unreviewed machine draft never claims an auto-enforce-grade confidence.
    assert confidence == generation._LLM_DRAFT_CONFIDENCE < 0.80


def test_resolve_producer_failsafe_offline_without_port(monkeypatch):
    # No injected port and no ANTHROPIC_API_KEY → deterministic offline producer.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    producer, kind = generation.resolve_producer("agent-generator", spec="x")
    assert kind == "offline-demo"
    text, _ = producer()
    assert "offline" in text.lower()


def test_llm_producer_empty_content_raises():
    # An empty completion must raise so the harness resolves it *safely* (DEFER), not emit a blank draft.
    producer = generation.llm_producer("agent-generator", "prompt", llm_port=StubLlm(reply=""))
    with pytest.raises(RuntimeError):
        producer()


# ── prompt assembly ─────────────────────────────────────────────────────────────

def test_assemble_prompt_for_known_generator_includes_instructions_and_spec():
    prompt = generation._assemble_generator_prompt("agent-generator", "a refund eligibility agent")
    assert "agent-generator" in prompt
    assert "a refund eligibility agent" in prompt          # spec threaded through as extra instructions
    assert "Generator Instructions" in prompt              # the generator's own prompt file is included


def test_assemble_prompt_unknown_generator_falls_back_to_spec():
    prompt = generation._assemble_generator_prompt("no-such-generator", "do the thing")
    assert prompt.strip() == "do the thing"


# ── governance is unchanged on the LLM path ──────────────────────────────────────

def test_governed_generation_with_llm_stays_suggest_and_staged():
    producer, kind = generation.resolve_producer(
        "agent-generator", spec="a refund agent", llm_port=StubLlm(reply=DRAFT)
    )
    outcome = generation.run_generation("agent-generator", producer, producer_kind=kind, preview=True)
    if not outcome.halo_available:
        pytest.skip("HALO runtime not importable in this environment")
    assert outcome.producer_kind == "llm"
    assert outcome.action == "SUGGEST"
    assert outcome.auto_enforced is False          # G-5: SUGGEST never auto-enforces
    assert outcome.bypass_total == 0               # confidence_gate_bypass_total MUST stay 0
    assert outcome.artifact == DRAFT


def test_resolve_llm_port_returns_none_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert generation._resolve_llm_port() is None
