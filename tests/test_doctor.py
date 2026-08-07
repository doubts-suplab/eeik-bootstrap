"""Tests for `eeik doctor` — the adoption/health diagnostic."""

from __future__ import annotations

import importlib
from pathlib import Path

import eeik
from eeik import mcp_tools

# `eeik.doctor` (the package attribute) is the SDK function; import the module for its internals.
doctor_mod = importlib.import_module("eeik.doctor")


def test_doctor_report_shape_and_healthy_on_this_repo():
    report = eeik.doctor()
    assert isinstance(report, eeik.DoctorReport)
    d = report.to_dict()
    assert set(d) == {"healthy", "ok", "counts", "diagnostics"}
    assert set(d["counts"]) == {"fail", "warn", "pass", "skip"}
    # The engine repo itself should be healthy (all its own deps + conformance are in place).
    assert report.ok is True
    # Every diagnostic carries a known level and a check name.
    for diag in report.diagnostics:
        assert diag.level in {"pass", "warn", "fail", "skip"}
        assert diag.check


def test_doctor_never_throws_even_if_a_check_errors(monkeypatch):
    def boom():
        raise RuntimeError("kaboom")

    monkeypatch.setattr(doctor_mod, "_CHECKS", (doctor_mod.check_python, boom))
    report = doctor_mod.doctor()  # must not raise
    levels = {d.check: d.level for d in report.diagnostics}
    assert levels["python"] == "pass"
    assert levels["boom"] == "warn"  # the errored check is reported, not fatal


def test_missing_core_dependency_is_a_fail(monkeypatch):
    monkeypatch.setattr(doctor_mod, "_installed", lambda m: m != "jsonschema")
    diag = doctor_mod.check_core_deps()
    assert diag.level == "fail" and "jsonschema" in diag.message and diag.fix


def test_halo_absent_is_a_warn_not_a_fail(monkeypatch):
    monkeypatch.setattr(doctor_mod, "_installed", lambda m: False)
    diag = doctor_mod.check_halo()
    assert diag.level == "warn"          # optional — generation still runs fail-safe
    assert "agent-harness" in diag.fix


def test_valid_manifest_and_resolution_pass(monkeypatch, tmp_path: Path):
    manifest = tmp_path / "project-manifest.yaml"
    manifest.write_text(Path("bootstrap/examples/greenfield-java-aws.yaml").read_text())
    monkeypatch.setattr(doctor_mod, "MANIFEST", manifest)
    assert doctor_mod.check_manifest().level == "pass"
    resolution = doctor_mod.check_pack_resolution()
    assert resolution.level == "pass" and "all present" in resolution.message


def test_invalid_manifest_is_a_fail(monkeypatch, tmp_path: Path):
    manifest = tmp_path / "project-manifest.yaml"
    manifest.write_text("project: {name: x}\n")  # missing required sections
    monkeypatch.setattr(doctor_mod, "MANIFEST", manifest)
    diag = doctor_mod.check_manifest()
    assert diag.level == "fail" and diag.fix


def test_missing_lockfile_warns(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(doctor_mod, "LOCKFILE", tmp_path / "nope.lock")
    diag = doctor_mod.check_lockfile()
    assert diag.level == "warn" and "eeik lock" in diag.fix


def test_mcp_tool_is_registered_and_read_only():
    res = mcp_tools.dispatch("eeik_doctor", {})
    assert set(res) >= {"healthy", "ok", "counts", "diagnostics"}
    assert "eeik_doctor" in {t["name"] for t in mcp_tools.TOOLS}
