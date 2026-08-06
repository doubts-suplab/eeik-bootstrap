"""Tests for closed-loop knowledge capture — audit logs → staged, governed lessons (ADR-012)."""

from __future__ import annotations

import eeik
from eeik import lessons as lessons_mod
from eeik import mcp_tools


_AUDIT = [
    # Two identical blocks → one grouped lesson.
    {"action": "BLOCK", "confidence": 0.9, "auto_enforced": False,
     "rationale": "Agent attempted a tool not on its allowlist: delete_repo", "agent": "pr-reviewer"},
    {"action": "BLOCK", "confidence": 0.88, "auto_enforced": False,
     "rationale": "Agent attempted a tool not on its allowlist: delete_repo", "agent": "pr-reviewer"},
    # A low-confidence human-review defer → its own lesson.
    {"action": "DEFER", "confidence": 0.6, "auto_enforced": False,
     "rationale": "Low confidence generating an ADR", "agent": "architecture-agent"},
    # Routine allow → not learnable.
    {"action": "ALLOW", "confidence": 0.99, "auto_enforced": True, "rationale": "routine", "agent": "docs"},
]


def test_only_learnable_records_produce_lessons():
    report = eeik.capture_lessons(_AUDIT)
    assert report.total_records == 4
    assert report.learnable == 3          # the ALLOW is excluded
    # Two blocks share a theme → grouped; the defer is separate → 2 drafts.
    assert len(report.lessons) == 2


def test_capture_is_governed_suggest_and_staged_never_committed():
    report = eeik.capture_lessons(_AUDIT)
    assert report.auto_enforced is False   # SUGGEST authority — never auto-committed
    assert report.staged is True
    for lsn in report.lessons:
        assert lsn.staged_path.startswith(".eeik-staging/")   # staged, not in the knowledge base
        assert lsn.lesson_id.startswith("LL-")


def test_lesson_numbering_continues_past_curated():
    curated = {c["file"].split("-")[1] for c in eeik.curated_lessons()}  # e.g. {'001','003'}
    highest = max((int(n) for n in curated), default=0)
    report = eeik.capture_lessons(_AUDIT)
    first_new = int(report.lessons[0].lesson_id.split("-")[1])
    assert first_new == highest + 1        # doesn't collide with an existing LL-NNN


def test_allow_only_audit_yields_no_lessons():
    report = eeik.capture_lessons([
        {"action": "ALLOW", "confidence": 0.99, "auto_enforced": True, "rationale": "fine", "agent": "x"},
    ])
    assert report.learnable == 0
    assert report.lessons == []


def test_mcp_capture_lessons_flags_not_committed():
    res = mcp_tools.dispatch("eeik_capture_lessons", {"records": _AUDIT})
    assert res["autoApplied"] is False
    assert res["auto_enforced"] is False
    assert "eeik_capture_lessons" in {t["name"] for t in mcp_tools.TOOLS}


def test_audit_record_field_aliases():
    # APEX/HALO field aliases normalise (decision→action, autoEnforced→auto_enforced, project→tenant).
    rec = lessons_mod.AuditRecord.from_dict(
        {"decision": "alert", "autoEnforced": False, "project": "acme", "explanation": "x"}
    )
    assert rec.action == "ALERT" and rec.auto_enforced is False and rec.tenant == "acme"
    assert rec.is_learnable()
