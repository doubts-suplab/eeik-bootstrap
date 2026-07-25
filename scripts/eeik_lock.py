#!/usr/bin/env python3
"""
EEIK Lockfile & Drift Detection — treat capability packs like versioned dependencies.

The historic EEIK adoption model is copy-once (``cp -r .claude``): the moment a project adopts a
pack it silently forks from the source and never sees improvements. This module closes that gap
(ADR-004):

    eeik lock       Record the pack versions + content digests a project adopted → eeik.lock
    eeik diff       Compare eeik.lock against the current packs → report drift
    eeik upgrade    Re-pin eeik.lock to current versions (optionally re-materialise)

``eeik.lock`` is the reproducible record of *what engineering intelligence this repo is running*.
Drift is any of: a pack added, a pack removed, a declared version change, or a content change with
an unchanged version (an un-versioned edit upstream).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pack_versions import all_pack_fingerprints  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
LOCK_SCHEMA_VERSION = 1
EEIK_VERSION = "1.4.0"  # keep in sync with ROADMAP milestone

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED = "\033[91m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"


def lock_path(explicit: str | None = None) -> Path:
    return Path(explicit) if explicit else (REPO_ROOT / "eeik.lock")


# ── build / read / write ────────────────────────────────────────────────────────

def build_lock(packs: list[str]) -> dict:
    """Assemble a lockfile document for the given resolved pack list."""
    return {
        "schemaVersion": LOCK_SCHEMA_VERSION,
        "eeikVersion": EEIK_VERSION,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "packs": all_pack_fingerprints(packs),
    }


def write_lock(doc: dict, path: Path) -> None:
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_lock(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ── drift ─────────────────────────────────────────────────────────────────────

def compute_drift(locked: dict, current: dict[str, dict[str, str]]) -> list[dict]:
    """Compare a lockfile's ``packs`` map against current fingerprints.

    Returns one entry per drifted pack: kind ∈ {added, removed, version-changed, content-changed}.
    """
    locked_packs: dict[str, dict[str, str]] = locked.get("packs", {})
    drift: list[dict] = []

    for name in sorted(set(locked_packs) | set(current)):
        was = locked_packs.get(name)
        now = current.get(name)
        if was is None:
            drift.append({"pack": name, "kind": "added", "from": None, "to": now["version"]})
        elif now is None:
            drift.append({"pack": name, "kind": "removed", "from": was["version"], "to": None})
        elif was.get("version") != now.get("version"):
            drift.append(
                {"pack": name, "kind": "version-changed", "from": was["version"], "to": now["version"]}
            )
        elif was.get("digest") != now.get("digest"):
            drift.append(
                {"pack": name, "kind": "content-changed", "from": was["version"], "to": now["version"]}
            )
    return drift


_KIND_STYLE = {
    "added": (ANSI_GREEN, "+ added         "),
    "removed": (ANSI_RED, "- removed       "),
    "version-changed": (ANSI_YELLOW, "~ version bump  "),
    "content-changed": (ANSI_CYAN, "! content drift "),
}


def print_drift(drift: list[dict]) -> None:
    if not drift:
        print(f"  {ANSI_GREEN}✓ No drift — eeik.lock matches the current capability packs.{ANSI_RESET}")
        return
    print(f"  {ANSI_BOLD}{len(drift)} pack(s) drifted from eeik.lock:{ANSI_RESET}\n")
    for d in drift:
        colour, label = _KIND_STYLE.get(d["kind"], (ANSI_RESET, d["kind"]))
        frm = d["from"] or "—"
        to = d["to"] or "—"
        print(f"    {colour}{label}{ANSI_RESET} {d['pack']:22}  {frm} → {to}")
    print()


# ── resolved-pack helper (reuses activate_packs resolution) ──────────────────────

def resolve_current_packs() -> list[str]:
    """Resolve packs from the manifest exactly as ``activate_packs.py`` does, when possible.

    Falls back to *all* packs on disk if no manifest is present, so ``lock``/``diff`` still work
    inside the EEIK repo itself (which has no project manifest).
    """
    from pack_versions import PACKS_DIR

    manifest_candidates = [
        REPO_ROOT / "project-manifest.yaml",
        REPO_ROOT / "bootstrap" / "manifests" / "project-manifest.yaml",
        Path("project-manifest.yaml"),
    ]
    if not any(c.exists() for c in manifest_candidates):
        # No project manifest (e.g. the EEIK repo itself) — lock every pack on disk.
        return sorted(p.name for p in PACKS_DIR.iterdir() if p.is_dir())

    import activate_packs  # noqa: E402  (same scripts/ dir, already on sys.path)

    manifest = activate_packs.load_manifest()
    matrix = activate_packs.load_matrix()
    return activate_packs.resolve_packs(manifest, matrix)


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_lock(args: argparse.Namespace) -> int:
    path = lock_path(args.file)
    packs = resolve_current_packs()
    doc = build_lock(packs)
    print(f"\n{ANSI_BOLD}EEIK Lock{ANSI_RESET}")
    print(f"  Pinning {len(doc['packs'])} pack(s) → {path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path}")
    for name, fp in sorted(doc["packs"].items()):
        print(f"    • {name:22}  v{fp['version']:8}  {fp['digest']}")
    write_lock(doc, path)
    print(f"\n  {ANSI_GREEN}✓ Wrote {path.name}{ANSI_RESET}\n")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    path = lock_path(args.file)
    locked = read_lock(path)
    print(f"\n{ANSI_BOLD}EEIK Drift Report{ANSI_RESET}")
    if locked is None:
        print(f"  {ANSI_YELLOW}⚠ No {path.name} found — run: eeik lock{ANSI_RESET}\n")
        return 1
    current = all_pack_fingerprints(resolve_current_packs())
    drift = compute_drift(locked, current)
    print(f"  Locked at : {locked.get('generatedAt', '?')}  (eeik {locked.get('eeikVersion', '?')})\n")
    print_drift(drift)
    if drift and args.exit_code:
        return 2  # CI-friendly: non-zero when drift exists
    return 0


def cmd_upgrade(args: argparse.Namespace) -> int:
    path = lock_path(args.file)
    locked = read_lock(path)
    current = all_pack_fingerprints(resolve_current_packs())
    print(f"\n{ANSI_BOLD}EEIK Upgrade{ANSI_RESET}")
    if locked is not None:
        drift = compute_drift(locked, current)
        print_drift(drift)
        if not drift:
            return 0
    packs = resolve_current_packs()
    write_lock(build_lock(packs), path)
    print(f"  {ANSI_GREEN}✓ Re-pinned {path.name} to current pack versions.{ANSI_RESET}")
    print(f"  {ANSI_CYAN}Next: eeik activate --apply --clean  (re-materialise packs into .claude/){ANSI_RESET}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK lockfile & drift detection")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_lock = sub.add_parser("lock", help="Write eeik.lock from resolved packs")
    p_lock.add_argument("--file", metavar="PATH", help="Lockfile path (default: eeik.lock)")
    p_lock.set_defaults(func=cmd_lock)

    p_diff = sub.add_parser("diff", help="Report drift between eeik.lock and current packs")
    p_diff.add_argument("--file", metavar="PATH", help="Lockfile path (default: eeik.lock)")
    p_diff.add_argument("--exit-code", action="store_true", help="Exit 2 when drift is found (CI gate)")
    p_diff.set_defaults(func=cmd_diff)

    p_up = sub.add_parser("upgrade", help="Re-pin eeik.lock to current versions")
    p_up.add_argument("--file", metavar="PATH", help="Lockfile path (default: eeik.lock)")
    p_up.set_defaults(func=cmd_upgrade)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
