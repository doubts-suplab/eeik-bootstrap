#!/usr/bin/env python3
"""
EEIK Verify — the conformance gate. Completes the loop: generate → govern → **verify**.

Where the generators *produce* config and the harness *governs* production, ``eeik verify`` asserts a
repository is actually **conformant**:

- **pack-conformance** — every agent/standard a pack declares in ``metadata.yaml`` resolves to a real
  file (in the pack, or in the shared ``.claude/`` layer), and every file a pack ships is declared.
  Keeps the catalog/SDK honest — no phantom agents.
- **manifest** — if a ``project-manifest.yaml`` exists, it validates against the canonical schema
  (schema errors are hard failures).
- **lock-drift** — if an ``eeik.lock`` exists, the adopted packs still match it.

Findings have a level: ``fail`` (hard correctness), ``warn`` (advisory / pre-existing content gap), or
``pass``. Exit code: non-zero on any ``fail``; ``--strict`` also fails on ``warn`` (for CI gating).

    eeik verify                 # human-readable report
    eeik verify --exit-code     # non-zero if any FAIL (CI gate)
    eeik verify --strict --exit-code   # non-zero if any FAIL or WARN
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from eeik.versions import PACKS_DIR, read_pack_metadata

REPO_ROOT = Path(__file__).parent.parent
CLAUDE_DIR = REPO_ROOT / ".claude"

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"


@dataclass(frozen=True)
class Finding:
    check: str
    level: str  # "pass" | "warn" | "fail"
    subject: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class VerifyReport:
    findings: list[Finding] = field(default_factory=list)

    @property
    def fails(self) -> list[Finding]:
        return [f for f in self.findings if f.level == "fail"]

    @property
    def warns(self) -> list[Finding]:
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
                "pass": len([f for f in self.findings if f.level == "pass"]),
            },
            "findings": [f.to_dict() for f in self.findings],
        }


def _norm(name: str) -> str:
    return str(name).lstrip("/").strip()


def _resolves(name: str, sub: str, pack_dir: Path) -> bool:
    """A declared agent/standard resolves if the file exists in the pack or the shared .claude/ layer."""
    fname = f"{_norm(name)}.md"
    return (pack_dir / sub / fname).exists() or (CLAUDE_DIR / sub / fname).exists()


# ── checks ────────────────────────────────────────────────────────────────────

def check_pack_conformance() -> list[Finding]:
    """Declared agents/standards resolve to files; shipped files are declared."""
    findings: list[Finding] = []
    for pack_dir in sorted(p for p in PACKS_DIR.iterdir() if p.is_dir()):
        meta = read_pack_metadata(pack_dir)
        pack = pack_dir.name
        pack_ok = True
        for kind, sub in (("agents_provided", "agents"), ("standards_provided", "standards")):
            declared = [_norm(n) for n in (meta.get(kind) or [])]
            for name in declared:
                if not _resolves(name, sub, pack_dir):
                    pack_ok = False
                    findings.append(Finding(
                        "pack-conformance", "warn", f"{pack}:{name}",
                        f"declares {sub[:-1]} '{name}' but no matching file was found",
                    ))
            # files shipped in the pack but not declared
            src = pack_dir / sub
            if src.exists():
                for f in sorted(src.glob("*.md")):
                    if f.stem not in declared:
                        pack_ok = False
                        findings.append(Finding(
                            "pack-conformance", "warn", f"{pack}:{f.stem}",
                            f"ships {sub}/{f.name} but metadata does not declare it",
                        ))
        if pack_ok:
            findings.append(Finding("pack-conformance", "pass", pack, "declarations match files"))
    return findings


def check_manifest() -> list[Finding]:
    """If a project-manifest.yaml exists, it must validate against the canonical schema."""
    candidates = [REPO_ROOT / "project-manifest.yaml", Path("project-manifest.yaml")]
    manifest_path = next((p for p in candidates if p.exists()), None)
    if manifest_path is None:
        return [Finding("manifest", "pass", "(none)", "no project-manifest.yaml (bootstrap repo) — skipped")]
    from eeik import api

    result = api.validate_manifest(path=str(manifest_path))
    findings = [
        Finding("manifest", "fail", manifest_path.name, e) for e in result.errors
    ] + [Finding("manifest", "warn", manifest_path.name, w) for w in result.warnings]
    if result.valid and not result.warnings:
        findings.append(Finding("manifest", "pass", manifest_path.name, "valid"))
    return findings


def check_lock_drift() -> list[Finding]:
    """If an eeik.lock exists, the adopted packs must still match it."""
    from eeik import api

    report = api.pack_drift()
    if not report.lock_present:
        return [Finding("lock-drift", "pass", "eeik.lock", "no lockfile — skipped")]
    if not report.entries:
        return [Finding("lock-drift", "pass", "eeik.lock", "no drift")]
    return [
        Finding("lock-drift", "warn", e.pack, f"{e.kind}: {e.from_version} → {e.to_version}")
        for e in report.entries
    ]


def check_reference_architectures() -> list[Finding]:
    """Each reference architecture's manifest validates and resolves to the packs it declares."""
    from eeik import api

    findings: list[Finding] = []
    archs = api.reference_architectures()
    if not archs:
        return [Finding("reference-architectures", "pass", "(none)", "no reference architectures — skipped")]
    for arch in archs:
        subject = f"ref-arch:{arch.name}"
        if not arch.manifest_path:
            findings.append(Finding("reference-architectures", "warn", subject, "no manifest declared"))
            continue
        manifest_file = REPO_ROOT / arch.manifest_path
        result = api.validate_manifest(path=str(manifest_file))
        if not result.valid:
            findings.append(Finding("reference-architectures", "fail", subject,
                                    f"manifest invalid: {result.errors[0] if result.errors else '?'}"))
            continue
        actual = api.resolve_packs(path=str(manifest_file))
        if arch.expected_packs and actual != arch.expected_packs:
            findings.append(Finding(
                "reference-architectures", "warn", subject,
                f"resolves to {actual} but declares expected_packs {arch.expected_packs}",
            ))
        else:
            findings.append(Finding("reference-architectures", "pass", subject, "manifest valid; packs match"))
    return findings


def verify() -> VerifyReport:
    """Run every conformance check and aggregate the findings."""
    findings = (
        check_pack_conformance()
        + check_manifest()
        + check_lock_drift()
        + check_reference_architectures()
    )
    return VerifyReport(findings=findings)


# ── rendering ───────────────────────────────────────────────────────────────────

_LEVEL = {
    "pass": (ANSI_GREEN, "✓ pass"),
    "warn": (ANSI_YELLOW, "⚠ warn"),
    "fail": (ANSI_RED, "✗ fail"),
}


def _render(report: VerifyReport) -> None:
    print(f"\n{ANSI_BOLD}EEIK Conformance Report{ANSI_RESET}\n")
    # Show fails and warns in full; collapse passes to a count.
    for f in report.findings:
        if f.level == "pass":
            continue
        colour, label = _LEVEL[f.level]
        print(f"  {colour}{label}{ANSI_RESET}  {ANSI_DIM}[{f.check}]{ANSI_RESET} {f.subject}: {f.message}")
    passes = len([f for f in report.findings if f.level == "pass"])
    print(f"\n  {ANSI_BOLD}Summary{ANSI_RESET}  "
          f"{ANSI_RED}{len(report.fails)} fail{ANSI_RESET} · "
          f"{ANSI_YELLOW}{len(report.warns)} warn{ANSI_RESET} · "
          f"{ANSI_GREEN}{passes} pass{ANSI_RESET}")
    verdict = ANSI_GREEN + "✓ conformant" if report.ok else ANSI_RED + "✗ non-conformant"
    print(f"  {verdict}{ANSI_RESET}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK conformance gate")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--exit-code", action="store_true", help="Non-zero exit on failure (CI gate)")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON")
    args = parser.parse_args()

    report = verify()
    if args.json:
        import json

        print(json.dumps(report.to_dict(), indent=2))
    else:
        _render(report)

    failed = bool(report.fails) or (args.strict and bool(report.warns))
    return 2 if (failed and args.exit_code) else 0


if __name__ == "__main__":
    sys.exit(main())
