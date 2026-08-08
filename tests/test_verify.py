"""Tests for the EEIK conformance gate (`eeik verify`)."""

from __future__ import annotations

import eeik
# `eeik.verify` is the public function; import the module internals directly for the unit checks.
from eeik.verify import CLAUDE_DIR, _resolves, check_pack_conformance


def test_verify_returns_typed_report():
    report = eeik.verify()
    assert isinstance(report, eeik.VerifyReport)
    # The EEIK repo has no project-manifest and a clean lock, so there are no hard failures.
    assert report.ok is True and report.fails == []


def test_verify_findings_have_valid_levels():
    report = eeik.verify()
    assert report.findings, "expected at least some findings"
    assert all(f.level in {"pass", "warn", "fail"} for f in report.findings)


def test_verify_to_dict_shape():
    d = eeik.verify().to_dict()
    assert set(d) == {"ok", "counts", "findings"}
    assert set(d["counts"]) == {"fail", "warn", "pass"}
    assert d["ok"] is True


def test_pack_conformance_is_clean():
    """Regression guard: after metadata reconciliation, every pack is conformant (no warn/fail)."""
    findings = check_pack_conformance()
    problems = [f for f in findings if f.level in {"warn", "fail"}]
    assert problems == [], f"pack-conformance regressions: {[f.subject for f in problems]}"


def test_pack_conformance_flags_a_bad_pack(tmp_path, monkeypatch):
    """The mechanism still detects drift: a pack that declares a phantom agent + ships an undeclared file."""
    import importlib

    verify_mod = importlib.import_module("eeik.verify")  # the module (eeik.verify attr is the function)

    pack = tmp_path / "fake-pack"
    (pack / "agents").mkdir(parents=True)
    (pack / "agents" / "real-agent.md").write_text("# real", encoding="utf-8")
    (pack / "metadata.yaml").write_text(
        "name: fake-pack\nversion: '1.0'\nagents_provided:\n  - ghost-agent\n", encoding="utf-8"
    )
    monkeypatch.setattr(verify_mod, "PACKS_DIR", tmp_path)

    warns = [f for f in check_pack_conformance() if f.level == "warn"]
    subjects = " ".join(f"{f.subject} {f.message}" for f in warns)
    assert "ghost-agent" in subjects        # declared but no file
    assert "real-agent" in subjects         # shipped but not declared


def test_resolves_uses_pack_or_claude_layer(tmp_path):
    # An agent present in the shared .claude/ layer resolves even if absent from the pack dir.
    # architect lives in .claude/agents/ (dogfood layer), not in most packs.
    assert (CLAUDE_DIR / "agents" / "architect.md").exists()
    assert _resolves("architect", "agents", tmp_path) is True
    assert _resolves("definitely-not-an-agent", "agents", tmp_path) is False
