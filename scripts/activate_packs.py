#!/usr/bin/env python3
"""
EEIK Capability Pack Activator
Reads project-manifest.yaml, determines which capability packs to activate,
and materialises their agents/commands/standards/workflows into .claude/.

This is the bridge between the manifest (what you need) and .claude/ (what
Claude Code actually reads). Run this after any manifest change, or let the
GitHub Actions workflow do it automatically.

Usage:
    python3 scripts/activate_packs.py                  # dry-run (shows what would change)
    python3 scripts/activate_packs.py --apply          # apply changes to .claude/
    python3 scripts/activate_packs.py --apply --clean  # clean .claude/ managed dirs first
    python3 scripts/activate_packs.py --list           # list resolved packs only
"""

import sys
import shutil
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT   = Path(__file__).parent.parent
PACKS_DIR   = REPO_ROOT / "capability-packs"
CLAUDE_DIR  = REPO_ROOT / ".claude"
MATRIX_FILE = REPO_ROOT / "generators" / "capability-selector" / "capability-matrix.yaml"

ANSI_GREEN  = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN   = "\033[96m"
ANSI_RED    = "\033[91m"
ANSI_BOLD   = "\033[1m"
ANSI_RESET  = "\033[0m"

# Directories inside each capability pack that map into .claude/
PACK_SUBDIRS = {
    "agents":    CLAUDE_DIR / "agents",
    "commands":  CLAUDE_DIR / "commands",
    "standards": CLAUDE_DIR / "standards",
    "workflows": CLAUDE_DIR / "workflows",
}

# Marker prefix added to files managed by this script (so --clean knows what to remove)
MANAGED_MARKER = "# eeik-managed"


def log_copy(src: Path, dst: Path, dry: bool) -> None:
    verb = "Would copy" if dry else "Copying"
    print(f"  {ANSI_CYAN}{verb}{ANSI_RESET}  {src.relative_to(REPO_ROOT)}  →  {dst.relative_to(REPO_ROOT)}")


def log_skip(dst: Path, reason: str) -> None:
    print(f"  {ANSI_YELLOW}Skip{ANSI_RESET}     {dst.relative_to(REPO_ROOT)}  ({reason})")


def load_manifest() -> dict:
    candidates = [
        REPO_ROOT / "project-manifest.yaml",
        REPO_ROOT / "bootstrap" / "manifests" / "project-manifest.yaml",
        Path("project-manifest.yaml"),
    ]
    for p in candidates:
        if p.exists():
            with open(p) as f:
                return yaml.safe_load(f) or {}
    print(f"{ANSI_RED}ERROR: project-manifest.yaml not found.  Run /bootstrap first.{ANSI_RESET}")
    sys.exit(1)


def load_matrix() -> dict:
    if not MATRIX_FILE.exists():
        return {}
    with open(MATRIX_FILE) as f:
        return yaml.safe_load(f) or {}


def resolve_packs(manifest: dict, matrix: dict) -> list[str]:
    """Determine which packs to activate, in dependency order."""
    tech    = manifest.get("technology", {})
    gov     = manifest.get("governance", {})
    project = manifest.get("project", {})
    caps    = manifest.get("capability_packs", {})

    selected: set[str] = {"core"}  # core is always active

    # ── Technology-driven selection ───────────────────────────────────────────
    backend  = tech.get("backend", {})
    frontend = tech.get("frontend", {})
    cloud    = tech.get("cloud", {})
    mf       = tech.get("mainframe", {})

    lang      = backend.get("language", "none")
    framework = backend.get("framework", "")
    fe_fw     = frontend.get("framework", "none")
    provider  = cloud.get("provider", "none")
    mf_plat   = mf.get("platform", "none")

    if lang == "java":
        selected.add("java")
    if lang == "python":
        selected.add("python")
    if fe_fw == "angular":
        selected.add("angular") if (PACKS_DIR / "angular").exists() else None
    if fe_fw == "react":
        selected.add("react") if (PACKS_DIR / "react").exists() else None
    if provider in ("aws", "multi"):
        selected.add("aws")
    if tech.get("containerisation", {}).get("runtime", "none") != "none":
        selected.add("containers")
    if mf_plat != "none":
        selected.add("modernization")

    # ── Domain selection ──────────────────────────────────────────────────────
    domain = project.get("domain", "generic")
    if domain in ("insurance", "banking", "healthcare"):
        selected.add(domain)

    # ── Governance-driven ─────────────────────────────────────────────────────
    profile = gov.get("profile", "basic")
    if profile in ("regulated", "enterprise"):
        selected.add("governance")

    # ── Architecture / AI ─────────────────────────────────────────────────────
    if "sagemaker" in str(cloud.get("services", [])).lower() or "bedrock" in str(cloud.get("services", [])).lower():
        selected.add("ai-engineering")
    if (PACKS_DIR / "architecture").exists():
        selected.add("architecture")

    # ── Delivery pack always useful ───────────────────────────────────────────
    selected.add("delivery")

    # ── Manifest overrides ────────────────────────────────────────────────────
    if caps.get("explicit"):
        selected = set(caps.get("include", list(selected)))
    else:
        for inc in caps.get("include", []):
            selected.add(inc)
        for exc in caps.get("exclude", []):
            selected.discard(exc)

    # ── Filter to packs that actually exist ───────────────────────────────────
    existing = {p.name for p in PACKS_DIR.iterdir() if p.is_dir()}
    missing  = selected - existing
    for m in sorted(missing):
        print(f"  {ANSI_YELLOW}⚠ Pack '{m}' resolved but not found in capability-packs/ — skipping{ANSI_RESET}")
    resolved = sorted(selected & existing)

    # core must be first
    if "core" in resolved:
        resolved.remove("core")
        resolved.insert(0, "core")

    return resolved


def activate(packs: list[str], dry: bool, clean: bool) -> int:
    """Copy pack files into .claude/.  Returns file count."""
    copied = 0

    if clean and not dry:
        # Remove only files we previously managed (marked with MANAGED_MARKER)
        for subdir in PACK_SUBDIRS.values():
            if subdir.exists():
                for f in subdir.glob("*.md"):
                    try:
                        if f.read_text(encoding="utf-8", errors="ignore").startswith(MANAGED_MARKER):
                            f.unlink()
                    except OSError:
                        pass

    for pack_name in packs:
        pack_dir = PACKS_DIR / pack_name
        print(f"\n  {ANSI_BOLD}[{pack_name}]{ANSI_RESET}")
        any_file = False

        for subdir_name, target_dir in PACK_SUBDIRS.items():
            src_dir = pack_dir / subdir_name
            if not src_dir.exists():
                continue

            target_dir.mkdir(parents=True, exist_ok=True)

            for src_file in sorted(src_dir.glob("*.md")):
                dst_file = target_dir / src_file.name
                if dst_file.exists() and not clean:
                    log_skip(dst_file, "exists — use --clean to overwrite")
                    continue
                log_copy(src_file, dst_file, dry)
                if not dry:
                    content = src_file.read_text(encoding="utf-8")
                    # Prepend managed marker (first line only, won't break YAML frontmatter)
                    if not content.startswith(MANAGED_MARKER):
                        content = f"{MANAGED_MARKER} pack={pack_name}\n{content}"
                    dst_file.write_text(content, encoding="utf-8")
                copied += 1
                any_file = True

        if not any_file:
            print(f"    {ANSI_YELLOW}(no agent/command/standard/workflow files to copy){ANSI_RESET}")

    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description="EEIK Capability Pack Activator")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--clean", action="store_true", help="Remove previously managed files before copying")
    parser.add_argument("--list",  action="store_true", help="List resolved packs and exit")
    args = parser.parse_args()

    dry = not args.apply

    print(f"\n{ANSI_BOLD}EEIK Capability Pack Activator{ANSI_RESET}")
    print(f"  Mode: {'dry-run (pass --apply to write)' if dry else 'APPLY'}\n")

    manifest = load_manifest()
    matrix   = load_matrix()
    packs    = resolve_packs(manifest, matrix)

    print(f"{ANSI_BOLD}Resolved packs ({len(packs)}){ANSI_RESET}")
    for p in packs:
        print(f"  • {p}")

    if args.list:
        return 0

    print(f"\n{ANSI_BOLD}File operations{ANSI_RESET}")
    count = activate(packs, dry=dry, clean=args.clean)

    print(f"\n{ANSI_BOLD}Done{ANSI_RESET}")
    if dry:
        print(f"  {count} file(s) would be copied.  Pass --apply to execute.")
    else:
        print(f"  {ANSI_GREEN}{count} file(s) copied into .claude/{ANSI_RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
