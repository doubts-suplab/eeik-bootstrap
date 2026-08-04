"""Tests for engine-surfaced reference architectures (ADR-010)."""

from __future__ import annotations

from pathlib import Path

import eeik
from eeik import architectures as arch_mod

REPO_ROOT = Path(__file__).parent.parent


def test_reference_architectures_load_typed():
    archs = eeik.reference_architectures()
    assert len(archs) >= 2
    assert all(isinstance(a, eeik.ReferenceArchitecture) for a in archs)
    names = {a.name for a in archs}
    assert {"order-management", "ai-augmented-service"} <= names


def test_get_by_name_and_fields():
    om = eeik.reference_architecture("order-management")
    assert om is not None
    assert om.maturity == "production"
    assert "java-21" in om.stack and om.manifest_path.endswith("project-manifest.yaml")
    assert om.expected_packs and om.components
    assert eeik.reference_architecture("nonexistent") is None


def test_each_architecture_manifest_is_valid_and_resolves_to_declared_packs():
    """The core promise: every reference architecture ships a schema-valid manifest that resolves to
    exactly the packs its descriptor claims — so it can't rot out of conformance."""
    for a in eeik.reference_architectures():
        manifest = REPO_ROOT / a.manifest_path
        result = eeik.validate_manifest(path=str(manifest))
        assert result.valid, f"{a.name}: manifest invalid: {result.errors}"
        actual = eeik.resolve_packs(path=str(manifest))
        assert actual == a.expected_packs, f"{a.name}: resolves to {actual}, declares {a.expected_packs}"


def test_resolved_packs_helper():
    om = eeik.reference_architecture("order-management")
    assert "aws" in arch_mod.resolved_packs(om)  # the resolver fix: AWS pack now resolves


def test_verify_includes_reference_architecture_findings():
    report = eeik.verify()
    ref = [f for f in report.findings if f.check == "reference-architectures"]
    assert ref, "verify should include reference-architecture findings"
    assert all(f.level == "pass" for f in ref), [f.message for f in ref if f.level != "pass"]


def test_to_dict_is_json_shaped():
    d = eeik.reference_architecture("ai-augmented-service").to_dict()
    assert set(d) >= {"name", "title", "stack", "tags", "expected_packs", "components", "manifest_path"}
