"""Tests for HALO Agent Contract emission (`eeik agent_contract`, ADR-009)."""

from __future__ import annotations

import pytest

import eeik
from eeik import contract as contract_mod

BLUEPRINTS = ["reviewer", "auditor", "architect", "engineer", "specialist",
              "investigator", "planner", "coordinator"]

# Which DecisionActions are within each authority ceiling (spec §3.3).
_WITHIN = {
    "OBSERVE": {"ALLOW", "DEFER"},
    "SUGGEST": {"ALLOW", "SUGGEST", "DEFER"},
    "ALERT": {"ALLOW", "SUGGEST", "ALERT", "DEFER"},
    "BLOCK": {"ALLOW", "SUGGEST", "ALERT", "BLOCK", "DEFER"},
}


@pytest.mark.parametrize("blueprint", BLUEPRINTS)
def test_contract_shape_and_invariants(blueprint):
    c = eeik.agent_contract(blueprint, f"test-{blueprint}")
    # required top-level fields present
    for key in ("identity", "purpose", "authorityLevel", "capabilities", "confidenceGate",
                "toolAccess", "inputContract", "outputContract", "failureBehaviour", "governance"):
        assert key in c
    # agentName matches the schema pattern
    assert c["identity"]["agentName"].replace("-", "").isalnum()
    # threshold never below the 0.80 floor (G-3)
    assert c["confidenceGate"]["threshold"] >= 0.80
    # every declared capability is within the authority ceiling (§3.3)
    assert set(c["capabilities"]) <= _WITHIN[c["authorityLevel"]]
    # input is tenant-scoped; output emits a decision
    assert c["inputContract"]["tenantScoped"] is True
    assert c["outputContract"]["emitsDecision"] is True
    # failure fallbacks never auto-enforce
    assert all(f["autoEnforced"] is False for f in c["failureBehaviour"])


def test_authority_mapping():
    assert eeik.agent_contract("auditor", "sec")["authorityLevel"] == "BLOCK"
    assert eeik.agent_contract("reviewer", "rev")["authorityLevel"] == "ALERT"
    assert eeik.agent_contract("investigator", "rca")["authorityLevel"] == "OBSERVE"
    assert eeik.agent_contract("engineer", "dev")["authorityLevel"] == "SUGGEST"


def test_supervisor_holds_no_tools():
    # Coordinators are supervisors — tool allowlist MUST be empty (spec §5, T-4).
    assert eeik.agent_contract("coordinator", "orchestrator")["toolAccess"] == []


def test_unknown_blueprint_raises():
    with pytest.raises(ValueError):
        eeik.agent_contract("nonexistent", "x")


def test_params_recorded_in_purpose():
    c = eeik.agent_contract("reviewer", "java-reviewer", language="java")
    assert "language=java" in c["purpose"]


def test_agentname_is_slugified():
    assert eeik.agent_contract("engineer", "My Fancy Agent!")["identity"]["agentName"] == "my-fancy-agent"


def test_validates_against_halo_schema():
    """Every blueprint's contract must pass HALO's own validator (schema + §3.3 binding rule)."""
    pytest.importorskip("halo_agent_harness", reason="halo-agent-harness not installed")
    if contract_mod._locate_schema() is None:
        pytest.skip("agent-contract.schema.json not locatable in this environment")
    for bp in BLUEPRINTS:
        ok, msg = eeik.validate_agent_contract(eeik.agent_contract(bp, f"test-{bp}"))
        assert ok, f"{bp}: {msg}"
