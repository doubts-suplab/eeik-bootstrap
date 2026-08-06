#!/usr/bin/env python3
"""
EEIK Reference Architectures — proven, engine-surfaced architectural blueprints (ADR-010).

Each reference architecture under ``knowledge/reference-architectures/<name>/`` is a *first-class,
machine-readable* blueprint, not just prose:

- ``reference.yaml`` — the descriptor (title, stack, components, tags, expected packs).
- ``project-manifest.yaml`` — a **schema-valid eeik manifest** you can feed straight to
  ``eeik resolve-packs`` / the repository-generator, or copy as a project starting point.
- ``architecture.md`` + ``runbook.md`` — the design and operations.

Because each ships a real manifest, the engine can *surface and check* it: list them, show what packs
each activates, and (via ``eeik verify``) assert the manifest still validates and resolves to the
packs the descriptor claims — so a reference architecture can never silently rot out of conformance.

    eeik architectures                 # list every blueprint
    eeik architectures order-management  # detail: stack, components, resolved packs, validity
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: pyyaml required.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
ARCH_DIR = REPO_ROOT / "knowledge" / "reference-architectures"

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"


@dataclass(frozen=True)
class ReferenceArchitecture:
    """A proven, machine-readable architectural blueprint."""

    name: str
    title: str
    summary: str
    maturity: str
    stack: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    expected_packs: list[str] = field(default_factory=list)
    components: list[dict[str, str]] = field(default_factory=list)
    key_decisions: list[str] = field(default_factory=list)
    manifest_path: str = ""
    deployment: dict[str, str] = field(default_factory=dict)  # {"cdk": path, "local_dev": path}

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_one(arch_dir: Path) -> ReferenceArchitecture | None:
    ref = arch_dir / "reference.yaml"
    if not ref.exists():
        return None
    d = yaml.safe_load(ref.read_text(encoding="utf-8")) or {}
    manifest = arch_dir / d.get("manifest", "project-manifest.yaml")
    return ReferenceArchitecture(
        name=d.get("name", arch_dir.name),
        title=d.get("title", arch_dir.name),
        summary=" ".join(str(d.get("summary", "")).split()),
        maturity=d.get("maturity", "unspecified"),
        stack=list(d.get("stack") or []),
        tags=list(d.get("tags") or []),
        expected_packs=list(d.get("expected_packs") or []),
        components=list(d.get("components") or []),
        key_decisions=list(d.get("key_decisions") or []),
        manifest_path=str(manifest.relative_to(REPO_ROOT)) if manifest.exists() else "",
        deployment={
            k: str((arch_dir / v).relative_to(REPO_ROOT))
            for k, v in (d.get("deployment") or {}).items()
            if (arch_dir / v).exists()
        },
    )


def load_all() -> list[ReferenceArchitecture]:
    """Every reference architecture on disk, sorted by name."""
    if not ARCH_DIR.exists():
        return []
    out = []
    for d in sorted(p for p in ARCH_DIR.iterdir() if p.is_dir()):
        arch = _load_one(d)
        if arch is not None:
            out.append(arch)
    return out


def get(name: str) -> ReferenceArchitecture | None:
    return next((a for a in load_all() if a.name == name), None)


def resolved_packs(arch: ReferenceArchitecture) -> list[str]:
    """The packs ``eeik resolve-packs`` actually produces for this architecture's manifest."""
    if not arch.manifest_path:
        return []
    from eeik import api

    manifest = yaml.safe_load((REPO_ROOT / arch.manifest_path).read_text(encoding="utf-8"))
    return api.resolve_packs(manifest=manifest)


# ── CLI ────────────────────────────────────────────────────────────────────────

def _print_list(archs: list[ReferenceArchitecture]) -> None:
    print(f"\n{ANSI_BOLD}EEIK Reference Architectures{ANSI_RESET}  {ANSI_DIM}({len(archs)}){ANSI_RESET}\n")
    for a in archs:
        print(f"  {ANSI_CYAN}{a.name}{ANSI_RESET}  {ANSI_DIM}[{a.maturity}]{ANSI_RESET}")
        print(f"    {a.title}")
        print(f"    {ANSI_DIM}{', '.join(a.stack)}{ANSI_RESET}\n")


def _print_detail(a: ReferenceArchitecture) -> None:
    print(f"\n{ANSI_BOLD}{a.title}{ANSI_RESET}  {ANSI_DIM}({a.name}, {a.maturity}){ANSI_RESET}\n")
    print(f"  {a.summary}\n")
    print(f"  {ANSI_BOLD}Stack{ANSI_RESET}      {', '.join(a.stack)}")
    print(f"  {ANSI_BOLD}Manifest{ANSI_RESET}   {a.manifest_path}")
    if a.deployment:
        depl = "  ".join(f"{k}={v}" for k, v in a.deployment.items())
        print(f"  {ANSI_BOLD}Deploy{ANSI_RESET}     {ANSI_DIM}{depl}{ANSI_RESET}")
    try:
        actual = resolved_packs(a)
        match = "✓" if actual == a.expected_packs else "≠"
        colour = ANSI_GREEN if actual == a.expected_packs else ANSI_YELLOW
        print(f"  {ANSI_BOLD}Packs{ANSI_RESET}      {colour}{match}{ANSI_RESET} {', '.join(actual)}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {ANSI_BOLD}Packs{ANSI_RESET}      {ANSI_YELLOW}(could not resolve: {exc}){ANSI_RESET}")
    if a.components:
        print(f"\n  {ANSI_BOLD}Components{ANSI_RESET}")
        for c in a.components:
            print(f"    • {c.get('name','?'):22} {ANSI_DIM}{c.get('tech','')}{ANSI_RESET}")
    if a.key_decisions:
        print(f"\n  {ANSI_BOLD}Key decisions{ANSI_RESET}")
        for k in a.key_decisions:
            print(f"    – {k}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK reference architectures")
    parser.add_argument("name", nargs="?", help="Show detail for one architecture")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    archs = load_all()
    if args.name:
        arch = get(args.name)
        if arch is None:
            print(f"unknown reference architecture '{args.name}'. "
                  f"Available: {', '.join(a.name for a in archs)}", file=sys.stderr)
            return 1
        if args.json:
            doc = arch.to_dict()
            try:
                doc["resolved_packs"] = resolved_packs(arch)
            except Exception:  # noqa: BLE001
                doc["resolved_packs"] = None
            print(json.dumps(doc, indent=2))
        else:
            _print_detail(arch)
        return 0

    if args.json:
        print(json.dumps([a.to_dict() for a in archs], indent=2))
    else:
        _print_list(archs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
