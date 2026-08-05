"""Tests for the EEIK generation-engine layer: pack versioning, lockfile drift, and HALO governance.

Run:  python3 -m pytest tests/ -q      (needs: pyyaml; agent-harness for the governance test)
"""

from __future__ import annotations

import pytest

from eeik import catalog as eeik_catalog
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


# ── catalog ───────────────────────────────────────────────────────────────────────

def test_catalog_covers_every_pack_and_is_categorised():
    cat = eeik_catalog.build_catalog()
    assert cat["packCount"] == len(cat["packs"]) >= 19
    # Every pack has a version, a resolved category, and a digest.
    for e in cat["packs"]:
        assert e["version"] and e["digest"]
        assert e["category"] and e["category"] != "uncategorised"


def test_catalog_filter_by_tag_and_query():
    entries = eeik_catalog.build_catalog()["packs"]
    banking = eeik_catalog.filter_by_tag(entries, "banking")
    assert [e["pack"] for e in banking] == ["banking"]
    # 'regulated' spans multiple domain packs.
    regulated = {e["pack"] for e in eeik_catalog.filter_by_tag(entries, "regulated")}
    assert {"banking", "healthcare", "insurance"} <= regulated
    # free-text query matches description/tags.
    assert any(e["pack"] == "healthcare" for e in eeik_catalog.filter_by_query(entries, "fhir"))


def test_catalog_find_providers():
    entries = eeik_catalog.build_catalog()["packs"]
    providers = eeik_catalog.find_providers(entries, "java-architect")
    assert ("java", "agent") in providers
    assert eeik_catalog.find_providers(entries, "no-such-agent") == []


# ── HALO governance ───────────────────────────────────────────────────────────────

# Requires the real HALO runtime (doubts-suplab/agent-harness). importorskip alone isn't enough:
# an unrelated/older `agent-harness` may be installed that imports but lacks the HALO API, so verify
# the actual symbols and skip cleanly when they're absent — this is an optional integration test.
halo = pytest.importorskip("agent_harness", reason="agent-harness not installed")
if not all(hasattr(halo, sym) for sym in ("AgentInput", "Harness", "DecisionAction")):
    pytest.skip(
        "installed 'agent_harness' is not the HALO runtime (missing AgentInput/Harness API)",
        allow_module_level=True,
    )


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
