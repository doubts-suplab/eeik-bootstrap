"""Tests for the public EEIK SDK — the stable `import eeik` surface (ADR-007)."""

from __future__ import annotations

import pytest

import eeik


def test_public_surface_is_importable():
    for name in ("find_packs", "providers_of", "validate_manifest", "resolve_packs",
                 "pack_drift", "write_lock", "Pack", "ValidationResult", "DriftReport"):
        assert hasattr(eeik, name), f"eeik.{name} missing from the public API"


def test_find_packs_returns_typed_packs():
    packs = eeik.find_packs()
    assert len(packs) >= 19
    assert all(isinstance(p, eeik.Pack) for p in packs)
    regulated = {p.pack for p in eeik.find_packs(tag="regulated")}
    assert {"banking", "healthcare", "insurance"} <= regulated


def test_providers_of():
    provs = eeik.providers_of("java-architect")
    assert [(p.pack, p.kind) for p in provs] == [("java", "agent")]
    assert eeik.providers_of("no-such-thing") == []


def test_validate_manifest_typed_result():
    ok = eeik.validate_manifest(path="bootstrap/examples/greenfield-java-aws.yaml")
    assert isinstance(ok, eeik.ValidationResult)
    assert ok.valid and ok.errors == []
    bad = eeik.validate_manifest(manifest={"project": {"name": "x"}})
    assert bad.valid is False and bad.errors


def test_resolve_packs_from_dict():
    manifest = {
        "schema_version": "1.0",
        "project": {"name": "svc", "domain": "generic", "project_type": "greenfield"},
        "technology": {"backend": {"language": "java"}},
    }
    resolved = eeik.resolve_packs(manifest=manifest)
    assert "core" in resolved and "java" in resolved


def test_pack_drift_typed_report():
    report = eeik.pack_drift()
    assert isinstance(report, eeik.DriftReport)
    assert report.has_drift == bool(report.entries)


def test_to_dict_shapes_match_the_wire():
    p = eeik.find_packs(tag="banking")[0]
    assert set(p.to_dict()) == {"pack", "name", "version", "category", "description",
                                "tags", "agents", "commands", "standards", "digest"}
    assert set(eeik.pack_drift().to_dict()) == {"lockPresent", "driftCount", "drift"}


def test_resolve_requires_an_argument():
    with pytest.raises(ValueError):
        eeik.resolve_packs()
