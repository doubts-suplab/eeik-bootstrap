"""Edge-case coverage for the resolver (eeik/packs.py) and governance rules (eeik/manifest.py)."""

from __future__ import annotations

import pytest

from eeik.manifest import check_governance_rules
from eeik.packs import resolve_packs


def _resolve(**parts) -> list[str]:
    manifest = {
        "schema_version": "1.0",
        "project": {"name": "svc", "domain": "generic", "project_type": "greenfield"},
        "technology": {"backend": {"language": "java"}},
    }
    manifest.update(parts)
    return resolve_packs(manifest, {})


# ── resolver: technology-driven ─────────────────────────────────────────────────

@pytest.mark.parametrize("language,expected", [
    ("java", "java"), ("python", "python"), ("go", "go"), ("node", "node"),
])
def test_backend_language_resolves_its_pack(language, expected):
    packs = _resolve(technology={"backend": {"language": language}})
    assert expected in packs
    assert packs[0] == "core"            # core is always first


@pytest.mark.parametrize("fw,pack", [("angular", "angular"), ("react", "react")])
def test_frontend_framework_resolves(fw, pack):
    packs = _resolve(technology={"backend": {"language": "java"}, "frontend": {"framework": fw}})
    assert pack in packs


@pytest.mark.parametrize("provider", ["aws", "multi"])
def test_cloud_provider_resolves_aws(provider):
    assert "aws" in _resolve(cloud={"provider": provider})


def test_containerisation_resolves_containers():
    packs = _resolve(technology={"backend": {"language": "go"},
                                 "containerisation": {"runtime": "docker"}})
    assert "containers" in packs


def test_mainframe_platform_resolves_modernization():
    packs = _resolve(technology={"backend": {"language": "java"}, "mainframe": {"platform": "ibmi"}})
    assert "modernization" in packs


@pytest.mark.parametrize("data", [
    {"streaming": "kafka"}, {"batch": "spark"}, {"transformation": "dbt"},
    {"warehouse": "athena"}, {"orchestration": "airflow"},
])
def test_data_workload_resolves_data_engineering(data):
    packs = _resolve(technology={"backend": {"language": "python"}, "data": data})
    assert "data-engineering" in packs


# ── resolver: domain / governance / ai ──────────────────────────────────────────

@pytest.mark.parametrize("domain", ["insurance", "banking", "healthcare", "retail"])
def test_domain_resolves_domain_pack(domain):
    packs = _resolve(project={"name": "x", "domain": domain, "project_type": "greenfield"})
    assert domain in packs


def test_generic_domain_adds_no_domain_pack():
    packs = _resolve()
    assert not ({"insurance", "banking", "healthcare", "retail"} & set(packs))


@pytest.mark.parametrize("profile", ["regulated", "enterprise"])
def test_regulated_profile_resolves_governance(profile):
    assert "governance" in _resolve(governance={"profile": profile})


def test_basic_profile_no_governance_pack():
    assert "governance" not in _resolve(governance={"profile": "basic"})


def test_ai_enabled_resolves_ai_packs():
    packs = _resolve(ai={"enabled": True, "pattern": "multi-agent"})
    assert "ai-engineering" in packs and "agent-harness" in packs


def test_ai_enabled_without_pattern_skips_agent_harness():
    packs = _resolve(ai={"enabled": True, "pattern": "none"})
    assert "ai-engineering" in packs and "agent-harness" not in packs


# ── resolver: always-on + overrides ─────────────────────────────────────────────

def test_core_architecture_delivery_always_present():
    packs = _resolve()
    assert {"core", "architecture", "delivery"} <= set(packs)


def test_capability_packs_include_and_exclude():
    packs = _resolve(capability_packs={"include": ["banking"], "exclude": ["delivery"]})
    assert "banking" in packs and "delivery" not in packs


def test_capability_packs_explicit_replaces_resolution():
    packs = _resolve(capability_packs={"explicit": True, "include": ["core", "java"]})
    assert set(packs) == {"core", "java"}      # nothing else, and core first
    assert packs[0] == "core"


def test_missing_resolved_pack_is_skipped_not_crashing():
    # An include for a pack that doesn't exist is filtered out (with a warning), never crashes.
    packs = _resolve(capability_packs={"include": ["no-such-pack"]})
    assert "no-such-pack" not in packs
    assert "core" in packs


# ── governance rules ────────────────────────────────────────────────────────────

def test_regulated_without_frameworks_is_an_error():
    errors, _ = check_governance_rules({"governance": {"profile": "regulated"},
                                        "project": {"domain": "generic"}})
    assert any("compliance_framework" in e for e in errors)


def test_domain_framework_mismatch_warns():
    _, warnings = check_governance_rules({
        "governance": {"profile": "regulated", "compliance_frameworks": ["gdpr"]},
        "project": {"domain": "banking"},
    })
    assert any("banking" in w for w in warnings)


def test_enterprise_without_adr_required_warns():
    _, warnings = check_governance_rules({"governance": {"profile": "enterprise"},
                                          "project": {"domain": "generic"}})
    assert any("adr_required" in w for w in warnings)


def test_low_coverage_threshold_warns():
    _, warnings = check_governance_rules({
        "governance": {"profile": "enterprise", "adr_required": True, "coverage_threshold": 50},
        "project": {"domain": "generic"},
    })
    assert any("coverage_threshold" in w for w in warnings)


def test_bad_project_name_is_an_error():
    errors, _ = check_governance_rules({"project": {"name": "bad name!", "domain": "generic"},
                                        "governance": {"profile": "basic"}})
    assert any("project.name" in e for e in errors)


def test_java_below_17_warns():
    _, warnings = check_governance_rules({
        "technology": {"backend": {"language": "java", "version": 11}},
        "project": {"domain": "generic"}, "governance": {"profile": "basic"},
    })
    assert any("Java 17" in w for w in warnings)


def test_malformed_governance_section_does_not_crash():
    # A scalar `governance` (invalid) must not raise — it yields no governance errors here.
    errors, warnings = check_governance_rules({"governance": "regulated",
                                               "project": {"domain": "generic"}})
    assert isinstance(errors, list) and isinstance(warnings, list)
