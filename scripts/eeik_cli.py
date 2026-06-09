#!/usr/bin/env python3
"""
eeik — EEIK Bootstrap CLI
Central entry point for all EEIK operations.

Usage:
    python3 scripts/eeik_cli.py <command> [options]

Commands:
    status              Show current EEIK state (manifest, active packs, adapters)
    validate            Validate project-manifest.yaml
    activate            Activate capability packs into .claude/
    generate-adapters   Generate .kiro/, AGENTS.md, .cursor/, GEMINI.md
    analyze             Scan repo and generate a draft manifest
    run <generator>     Run a generator via Claude harness (requires claude CLI)

Examples:
    python3 scripts/eeik_cli.py status
    python3 scripts/eeik_cli.py validate --strict
    python3 scripts/eeik_cli.py activate --apply
    python3 scripts/eeik_cli.py generate-adapters --apply
    python3 scripts/eeik_cli.py run repository-generator
"""

import sys
import subprocess
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent
SCRIPTS    = Path(__file__).parent

ANSI_BOLD   = "\033[1m"
ANSI_GREEN  = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED    = "\033[91m"
ANSI_CYAN   = "\033[96m"
ANSI_RESET  = "\033[0m"


def _run(cmd: list[str]) -> int:
    return subprocess.call(cmd)


# ── status ────────────────────────────────────────────────────────────────────

def cmd_status(_args: list[str]) -> int:
    try:
        import yaml
    except ImportError:
        print(f"{ANSI_RED}pyyaml required.  Run: pip install pyyaml jsonschema{ANSI_RESET}")
        return 1

    print(f"\n{ANSI_BOLD}EEIK Status{ANSI_RESET}\n")

    # Manifest
    manifest_path = REPO_ROOT / "project-manifest.yaml"
    if manifest_path.exists():
        with open(manifest_path) as f:
            m = yaml.safe_load(f) or {}
        project = m.get("project", {})
        print(f"  {ANSI_GREEN}✓{ANSI_RESET} Manifest found")
        print(f"      Project  : {project.get('name', '(unnamed)')}")
        print(f"      Type     : {project.get('type', '?')}")
        print(f"      Domain   : {project.get('domain', '?')}")
        print(f"      Profile  : {m.get('governance', {}).get('profile', '?')}")
    else:
        print(f"  {ANSI_YELLOW}⚠{ANSI_RESET} No project-manifest.yaml — run /bootstrap or eeik analyze")

    # Active packs (agents in .claude/agents/ with managed marker)
    agents_dir = REPO_ROOT / ".claude" / "agents"
    managed    = []
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            first = f.read_text(encoding="utf-8", errors="ignore").splitlines()
            if first and first[0].startswith("# eeik-managed"):
                pack = first[0].split("pack=")[-1].strip() if "pack=" in first[0] else "unknown"
                managed.append(pack)
    active_packs = sorted(set(managed))
    if active_packs:
        print(f"\n  {ANSI_BOLD}Active packs ({len(active_packs)}){ANSI_RESET}")
        for p in active_packs:
            print(f"    • {p}")
    else:
        print(f"\n  {ANSI_YELLOW}⚠{ANSI_RESET} No managed packs activated — run: eeik activate --apply")

    # Adapters
    print(f"\n  {ANSI_BOLD}Adapters{ANSI_RESET}")
    adapters = {
        "Claude Code": REPO_ROOT / ".claude",
        "Kiro":        REPO_ROOT / ".kiro",
        "Codex CLI":   REPO_ROOT / "AGENTS.md",
        "Cursor":      REPO_ROOT / ".cursor" / "rules",
        "Gemini CLI":  REPO_ROOT / "GEMINI.md",
        "Copilot":     REPO_ROOT / ".github" / "instructions",
    }
    for name, path in adapters.items():
        exists = path.exists()
        icon   = f"{ANSI_GREEN}✓{ANSI_RESET}" if exists else f"{ANSI_YELLOW}—{ANSI_RESET}"
        print(f"    {icon} {name}")

    print()
    return 0


# ── dispatch ──────────────────────────────────────────────────────────────────

COMMANDS = {
    "status":            cmd_status,
    "validate":          lambda a: _run([sys.executable, str(SCRIPTS / "validate_manifest.py")] + a),
    "activate":          lambda a: _run([sys.executable, str(SCRIPTS / "activate_packs.py")] + a),
    "generate-adapters": lambda a: _run([sys.executable, str(SCRIPTS / "generate_adapters.py")] + a),
    "analyze":           lambda a: _run([sys.executable, str(SCRIPTS / "analyze_project.py")] + a),
    "run":               lambda a: _run([sys.executable, str(SCRIPTS / "claude_harness.py")] + a),
}

HELP = """
{bold}eeik — EEIK Bootstrap CLI{reset}

{bold}Usage:{reset}
  python3 scripts/eeik_cli.py <command> [options]

{bold}Commands:{reset}
  status              Show EEIK state (manifest, active packs, adapters)
  validate            Validate project-manifest.yaml  [--strict]
  activate            Activate capability packs        [--apply] [--clean] [--list]
  generate-adapters   Generate multi-tool adapters     [--apply] [--tools kiro,codex,cursor,gemini]
  analyze             Scan repo → draft manifest       [--output path]
  run <generator>     Run generator via Claude harness [--dry-run]

{bold}Quick start:{reset}
  1. python3 scripts/eeik_cli.py analyze --output project-manifest.yaml
  2. python3 scripts/eeik_cli.py validate
  3. python3 scripts/eeik_cli.py activate --apply
  4. python3 scripts/eeik_cli.py generate-adapters --apply
""".format(bold=ANSI_BOLD, reset=ANSI_RESET)


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print(HELP)
        return 0

    command = args[0]
    rest    = args[1:]

    if command not in COMMANDS:
        print(f"{ANSI_RED}Unknown command: {command}{ANSI_RESET}\n")
        print(HELP)
        return 1

    return COMMANDS[command](rest)


if __name__ == "__main__":
    sys.exit(main())
