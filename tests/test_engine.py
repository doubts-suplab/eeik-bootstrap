"""Tests for the EEIK generation-engine layer: pack versioning, lockfile drift, and HALO governance.

Run:  python3 -m pytest tests/ -q      (needs: pyyaml; agent-harness for the governance test)
"""

from __future__ import annotations

import pytest

from eeik import lock as eeik_lock
from eeik import versions as pack_versions


# ── pack_versions ────────────────────────────────────────────────────────────────

def test_normalise_version_float_and_string_agree():
    assert pack_versions.normalise_version(1.0) == pack_versions.normalise_version("1.0")


def test_normalise_version_defaults_when_missing():
    assert pack_versions.normalise_version(None) == "0.0.0"


def test_fingerprints_cover_known_packs():
    fps = pack_versions.all_pack_fingerprints(["core", "java"])
    assert set(fps) == {"core", "java"}
    assert fps["core"]["version"] and len(fps["core"]["digest"]) == 16


# ── lockfile drift ────────────────────────────────────────────────────────────────

def test_lock_roundtrip(tmp_path):
    doc = eeik_lock.build_lock(["core", "java"])
    path = tmp_path / "eeik.lock"
    eeik_lock.write_lock(doc, path)
    back = eeik_lock.read_lock(path)
    assert back == doc


def test_drift_detects_added_removed_and_version_change():
    locked = {
        "packs": {
            "core": {"version": "1.0", "digest": "aaaa000000000000"},
            "java": {"version": "1.0", "digest": "bbbb000000000000"},
        }
    }
    current = {
        "core": {"version": "1.0", "digest": "aaaa000000000000"},  # unchanged
        "java": {"version": "1.1", "digest": "cccc000000000000"},  # version bump
        "python": {"version": "1.0", "digest": "dddd000000000000"},  # added
    }
    drift = {d["pack"]: d["kind"] for d in eeik_lock.compute_drift(locked, current)}
    assert drift == {"java": "version-changed", "python": "added"}


def test_drift_detects_content_change_without_version_bump():
    locked = {"packs": {"core": {"version": "1.0", "digest": "aaaa000000000000"}}}
    current = {"core": {"version": "1.0", "digest": "ffff111111111111"}}
    drift = eeik_lock.compute_drift(locked, current)
    assert drift == [{"pack": "core", "kind": "content-changed", "from": "1.0", "to": "1.0"}]


def test_no_drift_when_identical():
    fp = {"core": {"version": "1.0", "digest": "aaaa000000000000"}}
    assert eeik_lock.compute_drift({"packs": fp}, dict(fp)) == []


# ── HALO governance ───────────────────────────────────────────────────────────────

halo = pytest.importorskip("agent_harness", reason="agent-harness not installed")


def test_generation_is_never_auto_enforced_and_routes_to_review():
    """A generation is SUGGEST authority — the gate (G-5) must never auto-enforce it."""
    from agent_harness import AgentInput, Harness
    from agent_harness.adapters.inmemory import InMemoryHumanReview, InMemoryObservability

    from eeik import generation as generation_harness

    review = InMemoryHumanReview()
    obs = InMemoryObservability()
    harness = Harness(human_review=review, observability=obs)

    agent = generation_harness.GeneratorAgent(
        "unit-test-generator", lambda: ("draft artifact body", 0.99)  # high confidence on purpose
    )
    out = harness.invoke(agent, AgentInput("t", "u", context={"generator": "unit-test-generator"}))

    assert out.decision.auto_enforced is False          # G-5: SUGGEST never auto-enforces
    assert len(review.items) == 1                        # routed to a human
    assert obs.counter("confidence_gate_bypass_total") == 0  # no gate bypass, ever
