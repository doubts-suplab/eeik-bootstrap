#!/usr/bin/env python3
"""
EEIK Doctor — diagnose common adoption + health problems, with an actionable fix for each.

``eeik verify`` answers "is this repo *conformant*?". ``eeik doctor`` answers the earlier, more
practical question an adopter asks: "is my environment set up correctly, and if not, what do I run to
fix it?". It composes the engine's existing internals (dependency + version probes, manifest
validation, pack resolution, adapter materialisation, lockfile drift, and the conformance gate) into
one health check that never throws — every problem becomes a finding with a remedy.

Each diagnostic has a level — ``pass`` / ``warn`` / ``fail`` / ``skip`` (not applicable) — a message,
and a ``fix`` hint. Exit code: non-zero on any ``fail``; ``--strict`` also fails on ``warn``.

    eeik doctor                 # human-readable health report
    eeik doctor --json          # machine-readable
    eeik doctor --exit-code     # non-zero on any FAIL (CI / setup gate)
    eeik doctor --strict --exit-code   # non-zero on any FAIL or WARN
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CLAUDE_DIR = REPO_ROOT / ".claude"
MANIFEST = REPO_ROOT / "project-manifest.yaml"
LOCKFILE = REPO_ROOT / "eeik.lock"

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_CYAN = "\033[96m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"

MIN_PYTHON = (3, 11)


@dataclass(frozen=True)
class Diagnostic:
    check: str
    level: str  # "pass" | "warn" | "fail" | "skip"
    message: str
    fix: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class DoctorReport:
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def fails(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.level == "fail"]

    @property
    def warns(self) -> list[Diagnostic]:
        return [d for d in self.diagnostics if d.level == "warn"]

    @property
    def healthy(self) -> bool:
        return not self.fails and not self.warns

    @property
    def ok(self) -> bool:
        """No hard failures (warnings are tolerated unless --strict)."""
        return not self.fails

    def to_dict(self) -> dict:
        return {
            "healthy": self.healthy,
            "ok": self.ok,
            "counts": {
                "fail": len(self.fails),
                "warn": len(self.warns),
                "pass": len([d for d in self.diagnostics if d.level == "pass"]),
                "skip": len([d for d in self.diagnostics if d.level == "skip"]),
            },
            "diagnostics": [d.to_dict() for d in self.diagnostics],
        }


def _installed(module: str) -> bool:
    """True if an import of ``module`` would succeed, without importing it."""
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


# ── checks (each returns a Diagnostic; none throw) ──────────────────────────────

def check_python() -> Diagnostic:
    v = sys.version_info
    if (v.major, v.minor) >= MIN_PYTHON:
        return Diagnostic("python", "pass", f"Python {v.major}.{v.minor} (>= 3.11)")
    return Diagnostic(
        "python", "fail",
        f"Python {v.major}.{v.minor} is too old — the engine needs 3.11+",
        fix="Install Python 3.11 or newer and re-create the virtualenv.",
    )


def check_core_deps() -> Diagnostic:
    missing = [m for m in ("yaml", "jsonschema") if not _installed(m)]
    if not missing:
        return Diagnostic("dependencies", "pass", "core deps present (pyyaml, jsonschema)")
    return Diagnostic(
        "dependencies", "fail",
        f"missing core dependency: {', '.join(missing)}",
        fix="Install the engine and its deps:  pip install -e .",
    )


def check_halo() -> Diagnostic:
    """HALO (agent-harness) is optional; without it, governed generation runs fail-safe."""
    if not _installed("agent_harness"):
        return Diagnostic(
            "halo", "warn",
            "HALO (agent-harness) not installed — governed generation will run fail-safe "
            "(staged, ungoverned) and `eeik demo` runs offline",
            fix="Install it for a certified gate:  pip install agent-harness  (or  pip install -e \".[test]\")",
        )
    try:
        import agent_harness as halo  # noqa: PLC0415
        if all(hasattr(halo, s) for s in ("AgentInput", "Harness", "DecisionAction")):
            return Diagnostic("halo", "pass", "HALO runtime available — generation is fully governed")
        return Diagnostic(
            "halo", "warn",
            "an 'agent_harness' is installed but does not expose the HALO API (AgentInput/Harness)",
            fix="Install the real runtime:  pip install agent-harness  (from doubts-suplab/agent-harness)",
        )
    except Exception:  # noqa: BLE001 - a broken dep must not crash the doctor
        return Diagnostic(
            "halo", "warn",
            "'agent_harness' is installed but failed to import",
            fix="Reinstall it:  pip install --force-reinstall agent-harness",
        )


def check_mcp() -> Diagnostic:
    if _installed("mcp"):
        return Diagnostic("mcp", "pass", "MCP SDK available — `eeik mcp` can serve the read model")
    return Diagnostic(
        "mcp", "skip",
        "MCP SDK not installed (optional) — `eeik mcp` unavailable",
        fix="Install the extra to serve over MCP:  pip install -e \".[mcp]\"",
    )


def check_manifest() -> Diagnostic:
    from eeik import api  # noqa: PLC0415

    if not MANIFEST.exists():
        return Diagnostic(
            "manifest", "skip",
            "no project-manifest.yaml (expected for the seed/engine repo itself)",
            fix="In an adopting project: run /bootstrap, or start from bootstrap/manifests/manifest-template.yaml",
        )
    result = api.validate_manifest(path=str(MANIFEST))
    if result.valid:
        return Diagnostic("manifest", "pass", "project-manifest.yaml validates against the canonical schema")
    first = result.errors[0] if result.errors else "unknown error"
    return Diagnostic(
        "manifest", "fail",
        f"project-manifest.yaml is invalid: {first}",
        fix="Fix the manifest, then:  eeik validate",
    )


def check_pack_resolution() -> Diagnostic:
    from eeik import api  # noqa: PLC0415
    from eeik.versions import PACKS_DIR  # noqa: PLC0415

    if not MANIFEST.exists():
        return Diagnostic("pack-resolution", "skip", "no manifest to resolve packs from")
    try:
        resolved = api.resolve_packs(path=str(MANIFEST))
    except Exception as exc:  # noqa: BLE001
        return Diagnostic("pack-resolution", "fail", f"could not resolve packs: {exc}",
                          fix="Check the manifest is valid:  eeik validate")
    missing = [p for p in resolved if not (PACKS_DIR / p).exists()]
    if missing:
        return Diagnostic(
            "pack-resolution", "fail",
            f"manifest resolves to packs with no directory: {', '.join(missing)}",
            fix="These packs are not shipped; adjust the manifest or add the pack under capability-packs/.",
        )
    return Diagnostic("pack-resolution", "pass",
                      f"manifest resolves to {len(resolved)} pack(s), all present")


def check_adapters() -> Diagnostic:
    agents_dir = CLAUDE_DIR / "agents"
    if agents_dir.exists() and any(agents_dir.glob("*.md")):
        n = len(list(agents_dir.glob("*.md")))
        return Diagnostic("adapters", "pass", f".claude/ adapters present ({n} agent file(s))")
    if not MANIFEST.exists():
        return Diagnostic("adapters", "skip", "no manifest — nothing to materialise yet")
    return Diagnostic(
        "adapters", "warn",
        ".claude/ has no materialised agents",
        fix="Materialise the packs your manifest selects:  eeik activate --apply",
    )


def check_lockfile() -> Diagnostic:
    from eeik import api  # noqa: PLC0415

    if not LOCKFILE.exists():
        return Diagnostic(
            "lockfile", "warn",
            "no eeik.lock — adopted pack versions are unpinned (copy-once drift risk)",
            fix="Pin them:  eeik lock",
        )
    report = api.pack_drift()
    if report.has_drift:
        kinds = ", ".join(sorted({e.kind for e in report.entries}))
        return Diagnostic(
            "lockfile", "warn",
            f"{len(report.entries)} pack(s) drifted from eeik.lock ({kinds})",
            fix="Review the drift then re-pin:  eeik diff   ·   eeik upgrade",
        )
    return Diagnostic("lockfile", "pass", "eeik.lock present and matches the packs on disk")


def check_conformance() -> Diagnostic:
    from eeik import api  # noqa: PLC0415

    report = api.verify()
    d = report.to_dict()
    fails, warns = d["counts"]["fail"], d["counts"]["warn"]
    if fails:
        return Diagnostic(
            "conformance", "fail",
            f"conformance gate: {fails} fail · {warns} warn",
            fix="See the detail:  eeik verify",
        )
    if warns:
        return Diagnostic(
            "conformance", "warn",
            f"conformance gate: 0 fail · {warns} warn",
            fix="See the advisories:  eeik verify",
        )
    return Diagnostic("conformance", "pass",
                      f"conformance gate clean ({d['counts']['pass']} pass)")


_CHECKS = (
    check_python,
    check_core_deps,
    check_halo,
    check_mcp,
    check_manifest,
    check_pack_resolution,
    check_adapters,
    check_lockfile,
    check_conformance,
)


def doctor() -> DoctorReport:
    """Run every diagnostic and aggregate. Never throws — problems become findings."""
    diagnostics: list[Diagnostic] = []
    for check in _CHECKS:
        try:
            diagnostics.append(check())
        except Exception as exc:  # noqa: BLE001 - a check bug must not break the doctor
            diagnostics.append(Diagnostic(check.__name__, "warn",
                                          f"diagnostic errored: {exc}", fix="Report this as a bug."))
    return DoctorReport(diagnostics=diagnostics)


# ── CLI ────────────────────────────────────────────────────────────────────────

_ICON = {
    "pass": (ANSI_GREEN, "✓"),
    "warn": (ANSI_YELLOW, "⚠"),
    "fail": (ANSI_RED, "✗"),
    "skip": (ANSI_DIM, "–"),
}


def _print_report(report: DoctorReport) -> None:
    print(f"\n{ANSI_BOLD}EEIK Doctor{ANSI_RESET}\n")
    for d in report.diagnostics:
        colour, icon = _ICON.get(d.level, (ANSI_DIM, "?"))
        print(f"  {colour}{icon}{ANSI_RESET} {ANSI_BOLD}{d.check}{ANSI_RESET}  {d.message}")
        if d.fix and d.level in ("fail", "warn"):
            print(f"      {ANSI_DIM}fix:{ANSI_RESET} {d.fix}")
    c = report.to_dict()["counts"]
    verdict = (
        f"{ANSI_GREEN}✓ healthy{ANSI_RESET}" if report.healthy
        else f"{ANSI_RED}✗ {len(report.fails)} problem(s){ANSI_RESET}" if report.fails
        else f"{ANSI_YELLOW}⚠ {len(report.warns)} advisory(ies){ANSI_RESET}"
    )
    print(f"\n  {ANSI_BOLD}Summary{ANSI_RESET}  "
          f"{ANSI_RED}{c['fail']} fail{ANSI_RESET} · {ANSI_YELLOW}{c['warn']} warn{ANSI_RESET} · "
          f"{ANSI_GREEN}{c['pass']} pass{ANSI_RESET} · {ANSI_DIM}{c['skip']} skip{ANSI_RESET}")
    print(f"  {verdict}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK Doctor — diagnose adoption/health problems")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--exit-code", action="store_true", dest="exit_code",
                        help="Exit non-zero on any FAIL (with --strict, also on WARN)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()

    report = doctor()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        _print_report(report)

    if args.exit_code:
        if report.fails or (args.strict and report.warns):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
