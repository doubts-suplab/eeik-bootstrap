#!/usr/bin/env python3
"""
EEIK Closed-Loop Knowledge Capture — turn HALO/APEX audit logs into staged lessons.

The promise "every project leaves the org smarter" only holds if what a governed run *learns* flows
back into the knowledge base. HALO (and its consumers, e.g. APEX) already emit an append-only,
PII-redacted audit trail: every ``BLOCK`` / ``ALERT`` and every low-confidence decision routed to a
human carries a human-readable rationale. Those are exactly the moments a team wants captured as a
reusable lesson — instead they evaporate in a log.

This module closes that loop. It ingests audit records, selects the *learnable* ones, drafts a
lesson in the repository's ``LL-NNN`` format, and — because writing knowledge is a generation and
generation is **SUGGEST authority** (ADR-003) — routes the whole capture through HALO so the drafts
are **staged for human review, never auto-committed**. A human curates and promotes; the machine only
proposes. Deterministic and offline: the lesson skeleton is synthesised from the audit fields (no LLM,
no API key), so the governed path is always exercisable.

    from eeik.lessons import capture_lessons
    report = capture_lessons(records)   # records: list[dict] of audit entries

CLI:
    eeik lessons --from audit.json     # draft lessons from an audit export (staged)
    eeik lessons --list                # list the curated lessons already in the knowledge base
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from eeik.generation import STAGING_DIR, run_generation

REPO_ROOT = Path(__file__).parent.parent
LESSONS_DIR = REPO_ROOT / "knowledge" / "lessons-learned"
LESSONS_STAGING = STAGING_DIR / "lessons"

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"

# A HALO decision action → (lesson severity, lesson category). These are the "learnable" outcomes:
# an agent was blocked/alerted, or a low-confidence call was deferred to a human. ALLOW is routine.
_ACTION_SEVERITY = {
    "BLOCK": ("CRITICAL", "Governance"),
    "ALERT": ("HIGH", "Governance"),
    "DEFER": ("MEDIUM", "Governance"),
}
_LEARNABLE_ACTIONS = set(_ACTION_SEVERITY)
# A human-review outcome is learnable regardless of action (a human had to intervene).
_REVIEW_OUTCOMES = {"human-review", "rejected", "overridden", "escalated"}
# Below this the confidence gate would have deferred anyway (spec §4).
_CONFIDENCE_FLOOR = 0.80


@dataclass(frozen=True)
class AuditRecord:
    """A normalised HALO/APEX audit entry — the closed-loop input.

    Accepts the fields HALO's audit port and APEX's audit_log emit; unknown fields are ignored so a
    raw export can be fed straight in.
    """

    action: str = "ALLOW"
    confidence: float = 1.0
    auto_enforced: bool = True
    outcome: str = ""
    rationale: str = ""
    agent: str = ""
    tenant: str = ""
    category: str = ""
    timestamp: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AuditRecord:
        get = d.get
        return cls(
            action=str(get("action", get("decision", "ALLOW"))).upper(),
            confidence=float(get("confidence", 1.0)),
            auto_enforced=bool(get("auto_enforced", get("autoEnforced", True))),
            outcome=str(get("outcome", "")),
            rationale=str(get("rationale", get("explanation", ""))),
            agent=str(get("agent", get("agent_name", get("name", "")))),
            tenant=str(get("tenant", get("tenant_id", get("project", "")))),
            category=str(get("category", "")),
            timestamp=str(get("timestamp", get("created_at", ""))),
        )

    def is_learnable(self) -> bool:
        """A record worth a lesson: a block/alert/defer, a human-review outcome, or sub-floor confidence."""
        return (
            self.action in _LEARNABLE_ACTIONS
            or self.outcome in _REVIEW_OUTCOMES
            or self.confidence < _CONFIDENCE_FLOOR
        )

    def severity_category(self) -> tuple[str, str]:
        sev, cat = _ACTION_SEVERITY.get(self.action, ("MEDIUM", "Governance"))
        return sev, (self.category or cat)


@dataclass(frozen=True)
class LessonDraft:
    lesson_id: str
    title: str
    category: str
    severity: str
    staged_path: str
    source_records: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LessonCaptureReport:
    total_records: int
    learnable: int
    halo_available: bool
    auto_enforced: bool          # MUST be False — capture is SUGGEST authority, staged only
    staged: bool
    lessons: list[LessonDraft] = field(default_factory=list)
    review: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["lessons"] = [lsn.to_dict() for lsn in self.lessons]
        return d


def _next_lesson_number() -> int:
    """The next LL-NNN, one past the highest already curated in the knowledge base."""
    highest = 0
    if LESSONS_DIR.exists():
        for f in LESSONS_DIR.glob("LL-*.md"):
            m = re.match(r"LL-(\d+)", f.name)
            if m:
                highest = max(highest, int(m.group(1)))
    return highest + 1


def _theme_key(rec: AuditRecord) -> str:
    """Group records that describe the same underlying event (agent + a normalised rationale stem)."""
    stem = re.sub(r"[^a-z0-9 ]", "", rec.rationale.lower()).strip()
    stem = " ".join(stem.split()[:6])  # first few words carry the theme
    return f"{rec.agent}:{stem}"


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48] or "governed-decision"


def draft_lesson(lesson_id: str, group: list[AuditRecord]) -> tuple[str, str, str, str]:
    """Synthesise a lesson (id, title, category, severity, markdown) from a group of audit records."""
    lead = group[0]
    severity, category = lead.severity_category()
    action_desc = {
        "BLOCK": "HALO blocked an agent action",
        "ALERT": "HALO raised an alert on an agent action",
        "DEFER": "HALO deferred a low-confidence decision to a human",
    }.get(lead.action, "A governed decision required human review")
    title = (lead.rationale.split(".")[0].strip() or action_desc)[:80]
    agents = sorted({r.agent for r in group if r.agent})
    confidences = [r.confidence for r in group]
    body = f"""# {lesson_id}: {title}

**Category:** {category}
**Severity:** {severity} — derived from a HALO governance decision
**Captured:** (staged from audit log — set the date on curation)
**Source:** closed-loop capture from {len(group)} audit record(s){' · agents: ' + ', '.join(agents) if agents else ''}

---

## What Happened

{action_desc} across {len(group)} occurrence(s). The governance runtime's rationale was:

> {lead.rationale or '(no rationale recorded)'}

Decision action was `{lead.action}`; confidence ranged {min(confidences):.2f}–{max(confidences):.2f}
(the gate defers below {_CONFIDENCE_FLOOR:.2f}). This decision was **not** auto-enforced — it was
surfaced for human oversight, which is why it is worth capturing.

## Root Cause

<!-- Curate on promotion: why did the agent reach a decision the gate could not auto-enforce?
     Prompt/context gap, missing tool permission, ambiguous policy, or genuine edge case? -->

## Fix / Prevention

<!-- Curate on promotion. Candidate directions:
     - Tighten the agent's contract (authority, tool allowlist) if it over-reached.
     - Add a capability-pack standard or an anti-pattern entry so future agents avoid this.
     - If recurring, promote to knowledge/patterns/ or raise the confidence threshold for this task. -->

## Signal Strength

{len(group)} audit occurrence(s). Recurring low-confidence or blocked decisions on the same theme are
a strong signal to encode a rule rather than re-review each time.
"""
    return lesson_id, title, category, severity, body


def capture_lessons(
    records: list[dict[str, Any]] | list[AuditRecord],
    *,
    tenant: str = "eeik",
) -> LessonCaptureReport:
    """Draft staged lessons from audit records — governed as SUGGEST authority (never auto-committed).

    Selects the learnable records, groups them by theme, drafts one lesson per theme in the LL-NNN
    format, stages the drafts under ``.eeik-staging/lessons/``, and routes the capture through HALO so
    the batch carries a governance verdict (``auto_enforced=False``). Fails safe without HALO.
    """
    parsed = [r if isinstance(r, AuditRecord) else AuditRecord.from_dict(r) for r in records]
    learnable = [r for r in parsed if r.is_learnable()]

    # Group by theme, stable order.
    groups: dict[str, list[AuditRecord]] = {}
    for r in learnable:
        groups.setdefault(_theme_key(r), []).append(r)

    LESSONS_STAGING.mkdir(parents=True, exist_ok=True)
    drafts: list[LessonDraft] = []
    n = _next_lesson_number()
    for group in groups.values():
        lesson_id = f"LL-{n:03d}"
        _id, title, category, severity, body = draft_lesson(lesson_id, group)
        fname = f"{lesson_id}-{_slug(title)}.md"
        (LESSONS_STAGING / fname).write_text(body, encoding="utf-8")
        drafts.append(LessonDraft(
            lesson_id=lesson_id, title=title, category=category, severity=severity,
            staged_path=str((LESSONS_STAGING / fname).relative_to(REPO_ROOT)),
            source_records=len(group),
        ))
        n += 1

    # Govern the batch: capture is a knowledge generation → SUGGEST, staged, never auto-enforced.
    summary = (
        f"Closed-loop knowledge capture: {len(drafts)} lesson draft(s) from {len(learnable)} "
        f"learnable audit record(s) (of {len(parsed)} total)."
    )
    # Confidence stays below the floor on purpose — captured knowledge is always human-curated.
    outcome = run_generation(
        "knowledge-generator", lambda: (summary, 0.6), producer_kind="offline-demo", tenant=tenant,
    )

    return LessonCaptureReport(
        total_records=len(parsed),
        learnable=len(learnable),
        halo_available=outcome.halo_available,
        auto_enforced=outcome.auto_enforced,
        staged=True,
        lessons=drafts,
        review=outcome.review,
        warnings=outcome.warnings,
    )


def list_lessons() -> list[dict[str, str]]:
    """The curated lessons already in the knowledge base (LL-NNN files)."""
    out: list[dict[str, str]] = []
    if LESSONS_DIR.exists():
        for f in sorted(LESSONS_DIR.glob("LL-*.md")):
            first = f.read_text(encoding="utf-8", errors="ignore").splitlines()
            title = first[0].lstrip("# ").strip() if first else f.stem
            out.append({"file": f.name, "title": title})
    return out


def _load_records(path: Path) -> list[dict[str, Any]]:
    """Load audit records from a .json array or a .jsonl (one object per line)."""
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("["):
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    records = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK closed-loop knowledge capture (audit → staged lessons)")
    parser.add_argument("--from", dest="src", metavar="FILE", help="Audit export (.json array or .jsonl).")
    parser.add_argument("--list", action="store_true", dest="list_only",
                        help="List the curated lessons already in the knowledge base.")
    parser.add_argument("--json", action="store_true", help="Emit the capture report as JSON.")
    args = parser.parse_args()

    if args.list_only or not args.src:
        lessons = list_lessons()
        if args.json:
            print(json.dumps(lessons, indent=2))
            return 0
        print(f"\n{ANSI_BOLD}Curated lessons ({len(lessons)}){ANSI_RESET}  {ANSI_DIM}knowledge/lessons-learned/{ANSI_RESET}")
        for lsn in lessons:
            print(f"  • {lsn['file']}  {ANSI_DIM}{lsn['title']}{ANSI_RESET}")
        if not args.src:
            print(f"\n  {ANSI_DIM}Draft new lessons from an audit export: eeik lessons --from audit.json{ANSI_RESET}\n")
        return 0

    src = Path(args.src).expanduser()
    if not src.exists():
        print(f"{ANSI_YELLOW}Audit file not found: {src}{ANSI_RESET}", file=sys.stderr)
        return 1

    report = capture_lessons(_load_records(src))
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return 0

    print(f"\n{ANSI_BOLD}EEIK Closed-Loop Capture{ANSI_RESET}")
    print(f"  audit records: {report.total_records}   learnable: {report.learnable}   "
          f"drafts: {len(report.lessons)}")
    print(f"  {ANSI_DIM}gate → auto_enforced:{ANSI_RESET} {report.auto_enforced}  "
          f"{ANSI_DIM}(SUGGEST: lessons are staged for human curation, never auto-committed){ANSI_RESET}")
    for lsn in report.lessons:
        print(f"  {ANSI_GREEN}✓ staged{ANSI_RESET} {lsn.lesson_id} [{lsn.severity}/{lsn.category}] "
              f"{ANSI_DIM}{lsn.staged_path}{ANSI_RESET}")
    if report.warnings:
        for w in report.warnings:
            print(f"  {ANSI_YELLOW}⚠ {w}{ANSI_RESET}")
    print(f"\n  {ANSI_DIM}Curate a draft (fill Root Cause / Fix), move it into "
          f"knowledge/lessons-learned/, and update the index.{ANSI_RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
