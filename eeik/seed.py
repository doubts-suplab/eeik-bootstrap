#!/usr/bin/env python3
"""
EEIK Seed — make the dual-purpose adapter boundary explicit and copyable.

EEIK's root adapter dirs (`.claude/`, `.github/`, `.cursor/`, `.kiro/`, root tool contexts) are both
EEIK's own dogfood config *and* the seed an adopting project takes (ADR-005). A naive `cp -r` of the
whole repo drags the engine, tests, and EEIK's own agents into a product. This module reads the single
source of truth — ``bootstrap/seed-manifest.yaml`` — which classifies every root entry as ``seed``
(copy), ``generated`` (regenerate via the engine, never hand-copy), or ``engine`` (never copied), and
copies exactly the ``seed`` set into a target project.

    eeik seed --list                 # print the seed / generated / engine taxonomy
    eeik seed --into ../my-project   # dry-run: show what would be copied
    eeik seed --into ../my-project --apply   # copy the seed set into the target

The command is additive to the ``cp -r`` ergonomics, not a replacement: it just copies the *right*
subset, so an adopter no longer has to know which directories are engine-only.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - yaml is a hard dependency of the engine
    print("ERROR: pyyaml required.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
SEED_MANIFEST = REPO_ROOT / "bootstrap" / "seed-manifest.yaml"

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"


def load_seed_manifest(path: Path | None = None) -> dict[str, Any]:
    """Parse the seed manifest (bootstrap/seed-manifest.yaml)."""
    p = path or SEED_MANIFEST
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def seed_plan(path: Path | None = None) -> dict[str, list[dict[str, str]]]:
    """Return the seed taxonomy as ``{"seed": [...], "generated": [...], "engine": [...]}``.

    Each entry is ``{"path": str, "note": str}``. This is the JSON-friendly view the CLI and the SDK
    share, so "what does an adopting project copy?" has one answer.
    """
    manifest = load_seed_manifest(path)
    out: dict[str, list[dict[str, str]]] = {}
    for kind in ("seed", "generated", "engine"):
        entries = manifest.get(kind) or []
        out[kind] = [
            {"path": e["path"], "dest": e.get("dest", e["path"]), "note": e.get("note", "")}
            for e in entries
        ]
    return out


def _print_list(plan: dict[str, list[dict[str, str]]]) -> None:
    labels = {
        "seed": (ANSI_GREEN, "COPY into your project"),
        "generated": (ANSI_CYAN, "REGENERATE via the engine — do not hand-copy"),
        "engine": (ANSI_YELLOW, "ENGINE-only — never copied"),
    }
    print(f"\n{ANSI_BOLD}EEIK Seed Taxonomy{ANSI_RESET}  {ANSI_DIM}(bootstrap/seed-manifest.yaml){ANSI_RESET}")
    for kind, (colour, blurb) in labels.items():
        entries = plan.get(kind, [])
        print(f"\n  {colour}{ANSI_BOLD}{kind}{ANSI_RESET} — {blurb}  ({len(entries)})")
        for e in entries:
            note = f"  {ANSI_DIM}{e['note']}{ANSI_RESET}" if e["note"] else ""
            rename = f" → {e['dest']}" if e.get("dest") and e["dest"] != e["path"] else ""
            print(f"    • {e['path']}{rename}{note}")
    print()


def _copy_entry(rel_path: str, target_root: Path, *, dry: bool, dest: str | None = None) -> tuple[str, bool]:
    """Copy one seed entry (file or directory) into ``target_root``. Returns (message, copied).

    ``dest`` lets a source seed to a different target path (e.g. templates/PROJECT-CLAUDE.md → CLAUDE.md),
    so the seed can rename without dragging EEIK's own equivalently-named file.
    """
    src = REPO_ROOT / rel_path
    dst = target_root / (dest or rel_path)
    label = rel_path if (dest is None or dest == rel_path) else f"{rel_path} → {dest}"
    if not src.exists():
        return (f"{ANSI_YELLOW}skip{ANSI_RESET} {label}  (not present in this repo)", False)
    if dry:
        kind = "dir/" if src.is_dir() else "file"
        return (f"{ANSI_DIM}would copy{ANSI_RESET} {kind} {label} → {dst}", False)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return (f"{ANSI_GREEN}copied{ANSI_RESET} {rel_path} → {dst}", True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy EEIK's seed set (adapter shells + shared config) into an adopting project.",
    )
    parser.add_argument("--into", metavar="DIR", help="Target project directory to seed.")
    parser.add_argument("--apply", action="store_true", help="Copy (default is dry-run).")
    parser.add_argument("--list", action="store_true", dest="list_only",
                        help="Print the seed/generated/engine taxonomy and exit.")
    args = parser.parse_args()

    plan = seed_plan()

    if args.list_only or not args.into:
        _print_list(plan)
        if not args.into and not args.list_only:
            print(f"  {ANSI_DIM}Pass --into <dir> to copy the 'seed' set into a project "
                  f"(add --apply to write).{ANSI_RESET}\n")
        return 0

    target_root = Path(args.into).expanduser().resolve()
    if args.apply and not target_root.exists():
        target_root.mkdir(parents=True, exist_ok=True)

    dry = not args.apply
    print(f"\n{ANSI_BOLD}EEIK Seed{ANSI_RESET}  →  {target_root}")
    print(f"  Mode: {'dry-run (pass --apply to write)' if dry else 'APPLY'}\n")

    copied = 0
    for entry in plan["seed"]:
        msg, did = _copy_entry(entry["path"], target_root, dry=dry, dest=entry["dest"])
        print(f"  {msg}")
        copied += int(did)

    print(f"\n  {ANSI_BOLD}Done{ANSI_RESET}")
    if dry:
        print(f"  {len(plan['seed'])} seed entr(ies) would be copied.  Pass --apply to execute.")
    else:
        print(f"  {copied} seed entr(ies) copied.")
    print(f"  {ANSI_DIM}Next: `pip install eeik`, write your project-manifest.yaml, then "
          f"`eeik activate --apply` to materialise the packs you selected.{ANSI_RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
