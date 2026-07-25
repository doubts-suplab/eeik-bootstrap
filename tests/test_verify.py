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


def test_pack_conformance_flags_undeclared_and_missing():
    """A pack that ships a file it doesn't declare, or declares a file it doesn't ship, is flagged."""
    findings = check_pack_conformance()
    warns = [f for f in findings if f.level == "warn"]
    # java ships spring-security-engineer.md but its metadata doesn't declare it → flagged.
    assert any("spring-security-engineer" in f.subject for f in warns)
    # every warn names a concrete pack:subject and a message.
    assert all(":" in f.subject and f.message for f in warns)


def test_resolves_uses_pack_or_claude_layer(tmp_path):
    # An agent present in the shared .claude/ layer resolves even if absent from the pack dir.
    from eeik.verify import _resolves, CLAUDE_DIR

    # architect lives in .claude/agents/ (dogfood layer), not in most packs.
    assert (CLAUDE_DIR / "agents" / "architect.md").exists()
    assert _resolves("architect", "agents", tmp_path) is True
    assert _resolves("definitely-not-an-agent", "agents", tmp_path) is False
