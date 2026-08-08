#!/usr/bin/env python3
"""
EEIK Lint — content-quality checks for capability-pack agents and standards.

Where ``eeik verify`` asks "does a pack deliver what it *declares*?" (do the files exist), ``eeik lint``
asks "is the content itself *well-formed*?": does every agent carry valid frontmatter (name matching the
file, a usable description, a model, a list of tools), and does every agent/standard have real body
content? It is the quality gate behind the catalog — a pack whose agent has a one-word description or a
mismatched name still "resolves", but reads badly to the tools that consume it.

Findings have a level — ``fail`` (malformed: no frontmatter, missing name/description) / ``warn``
(advisory: missing model, name≠filename, thin description, no heading) / ``pass``. Exit code: non-zero
on any ``fail``; ``--strict`` also fails on ``warn``.

    eeik lint                  # human-readable report
    eeik lint --json           # machine-readable
    eeik lint --exit-code      # non-zero on any FAIL (CI gate)
    eeik lint --strict --exit-code   # non-zero on any FAIL or WARN
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
PACKS_DIR = REPO_ROOT / "capability-packs"
CLAUDE_DIR = REPO_ROOT / ".claude"

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"

# Description length band (characters). Below MIN is a thin/placeholder description; above MAX is likely
# a whole prompt pasted into the trigger. Both are warnings, not failures.
DESC_MIN = 40
DESC_MAX = 900
_VALID_TOOLS = {"Read", "Write", "Edit", "MultiEdit", "Bash", "Glob", "Grep"}
_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# `eeik activate` prepends this marker to materialised copies in .claude/; ignore it when linting.
_MANAGED_MARKER = re.compile(r"\A# eeik-managed[^\n]*\n")


@dataclass(frozen=True)
class LintFinding:
    file: str
    level: str  # "pass" | "warn" | "fail"
    rule: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class LintReport:
    findings: list[LintFinding] = field(default_factory=list)

    @property
    def fails(self) -> list[LintFinding]:
        return [f for f in self.findings if f.level == "fail"]

    @property
    def warns(self) -> list[LintFinding]:
        return [f for f in self.findings if f.level == "warn"]

    @property
    def ok(self) -> bool:
        return not self.fails

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "counts": {
                "fail": len(self.fails),
                "warn": len(self.warns),
                "checked": len({f.file for f in self.findings}),
            },
            "findings": [f.to_dict() for f in self.findings],
        }


def _agent_dirs() -> list[Path]:
    dirs = [CLAUDE_DIR / "agents"]
    dirs += sorted(PACKS_DIR.glob("*/agents"))
    return [d for d in dirs if d.exists()]


def _standard_dirs() -> list[Path]:
    dirs = [CLAUDE_DIR / "standards"]
    dirs += sorted(PACKS_DIR.glob("*/standards"))
    return [d for d in dirs if d.exists()]


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return p.name


def lint_agent_file(path: Path) -> list[LintFinding]:
    findings: list[LintFinding] = []
    rel = _rel(path)
    text = _MANAGED_MARKER.sub("", path.read_text(encoding="utf-8", errors="ignore"), count=1)

    m = _FRONTMATTER.match(text)
    if not m:
        return [LintFinding(rel, "fail", "frontmatter", "no YAML frontmatter block (--- … ---) at the top")]

    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        return [LintFinding(rel, "fail", "frontmatter", f"frontmatter is not valid YAML: {exc}")]
    if not isinstance(fm, dict):
        return [LintFinding(rel, "fail", "frontmatter", "frontmatter is not a mapping")]

    name = fm.get("name")
    if not name:
        findings.append(LintFinding(rel, "fail", "name", "frontmatter has no 'name'"))
    elif name != path.stem:
        findings.append(LintFinding(rel, "warn", "name-matches-file",
                                    f"name '{name}' != filename '{path.stem}'"))

    desc = " ".join(str(fm.get("description", "")).split())
    if not desc:
        findings.append(LintFinding(rel, "fail", "description", "frontmatter has no 'description'"))
    elif len(desc) < DESC_MIN:
        findings.append(LintFinding(rel, "warn", "description-length",
                                    f"description is thin ({len(desc)} chars < {DESC_MIN})"))
    elif len(desc) > DESC_MAX:
        findings.append(LintFinding(rel, "warn", "description-length",
                                    f"description is very long ({len(desc)} chars > {DESC_MAX})"))

    if not fm.get("model"):
        findings.append(LintFinding(rel, "warn", "model", "no 'model' — the default will be used"))

    tools = fm.get("tools")
    if tools is not None:
        if not isinstance(tools, list):
            findings.append(LintFinding(rel, "warn", "tools", "'tools' should be a list"))
        else:
            unknown = [t for t in tools if t not in _VALID_TOOLS]
            if unknown:
                findings.append(LintFinding(rel, "warn", "tools",
                                            f"unknown tool(s): {', '.join(map(str, unknown))}"))

    body = text[m.end():]
    if not re.search(r"^#{1,3}\s+\S", body, re.MULTILINE):
        findings.append(LintFinding(rel, "warn", "body", "no Markdown heading in the body"))

    if not findings:
        findings.append(LintFinding(rel, "pass", "agent", "well-formed"))
    return findings


def lint_standard_file(path: Path) -> list[LintFinding]:
    rel = _rel(path)
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        return [LintFinding(rel, "fail", "empty", "standard file is empty")]
    findings: list[LintFinding] = []
    if not re.search(r"^#\s+\S", text, re.MULTILINE):
        findings.append(LintFinding(rel, "warn", "heading", "no top-level '# ' heading"))
    if len(text) < 200:
        findings.append(LintFinding(rel, "warn", "length", f"standard looks like a stub ({len(text)} chars)"))
    if not findings:
        findings.append(LintFinding(rel, "pass", "standard", "well-formed"))
    return findings


def lint_content() -> LintReport:
    """Lint every capability-pack (and shared .claude/) agent + standard markdown file."""
    findings: list[LintFinding] = []
    seen: set[Path] = set()
    for d in _agent_dirs():
        for f in sorted(d.glob("*.md")):
            if f.name.upper() == "README.MD" or f in seen:
                continue
            seen.add(f)
            findings.extend(lint_agent_file(f))
    for d in _standard_dirs():
        for f in sorted(d.glob("*.md")):
            if f.name.upper() == "README.MD" or f in seen:
                continue
            seen.add(f)
            findings.extend(lint_standard_file(f))
    return LintReport(findings=findings)


# ── CLI ────────────────────────────────────────────────────────────────────────

_ICON = {"pass": (ANSI_GREEN, "✓"), "warn": (ANSI_YELLOW, "⚠"), "fail": (ANSI_RED, "✗")}


def _print_report(report: LintReport, show_pass: bool) -> None:
    print(f"\n{ANSI_BOLD}EEIK Content Lint{ANSI_RESET}\n")
    for f in report.findings:
        if f.level == "pass" and not show_pass:
            continue
        colour, icon = _ICON.get(f.level, (ANSI_DIM, "?"))
        print(f"  {colour}{icon}{ANSI_RESET} {ANSI_DIM}[{f.rule}]{ANSI_RESET} {f.file}  {f.message}")
    c = report.to_dict()["counts"]
    verdict = f"{ANSI_GREEN}✓ clean{ANSI_RESET}" if report.ok else f"{ANSI_RED}✗ {c['fail']} fail{ANSI_RESET}"
    print(f"\n  {ANSI_BOLD}Summary{ANSI_RESET}  "
          f"{ANSI_RED}{c['fail']} fail{ANSI_RESET} · {ANSI_YELLOW}{c['warn']} warn{ANSI_RESET} · "
          f"{ANSI_DIM}{c['checked']} files checked{ANSI_RESET}   {verdict}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK content lint (agents + standards)")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--exit-code", action="store_true", dest="exit_code",
                        help="Exit non-zero on any FAIL (with --strict, also on WARN)")
    parser.add_argument("--show-pass", action="store_true", help="Also list files that passed")
    args = parser.parse_args()

    report = lint_content()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        _print_report(report, show_pass=args.show_pass)

    if args.exit_code and (report.fails or (args.strict and report.warns)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
