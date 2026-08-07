#!/usr/bin/env python3
"""
eeik — EEIK Bootstrap CLI
Central entry point for all EEIK operations.

Installed as the ``eeik`` console script (see pyproject.toml). Equivalent invocations:
    eeik <command> [options]                 # after `pip install -e .`
    python3 -m eeik <command> [options]      # from the repo root, no install
    eeik <command>    # backwards-compatible shim

Commands:
    status              Show current EEIK state (manifest, active packs, adapters)
    validate            Validate project-manifest.yaml
    activate            Activate capability packs into .claude/
    generate-adapters   Generate .kiro/, AGENTS.md, .cursor/, GEMINI.md
    lock                Pin adopted pack versions → eeik.lock
    diff                Report capability-pack drift vs eeik.lock
    upgrade             Re-pin eeik.lock to current pack versions
    catalog             Query the capability-pack / agent / standard index
    architectures       List / show proven reference architectures (engine-surfaced blueprints)
    verify              Conformance gate — packs deliver what they declare
    contract            Emit a HALO Agent Contract from a blueprint (runtime-governed by construction)
    mcp                 Start the EEIK MCP server (read model over MCP)
    run <generator>     Run a generator via the HALO-governed harness
    demo                Offline governed-generation showcase (EEIK in action)
    seed                Copy the seed set (adapter shells + shared config) into an adopting project
    lessons             Closed-loop knowledge capture: draft staged lessons from HALO/APEX audit logs
    doctor              Diagnose common adoption/health problems with an actionable fix for each

Examples:
    eeik status
    eeik validate --strict
    eeik activate --apply
    eeik lock
    eeik diff --exit-code
    eeik demo
"""

import importlib
import json
import sys
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent

ANSI_BOLD   = "\033[1m"
ANSI_GREEN  = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED    = "\033[91m"
ANSI_CYAN   = "\033[96m"
ANSI_RESET  = "\033[0m"


def _mod(module: str, *prefix: str):
    """Dispatch to a package module's ``main()`` in-process.

    In-process (vs. spawning ``python -m eeik.<module>``) avoids re-executing an already-imported
    submodule — which Python warns about — and is faster. The submodule reads ``sys.argv``; we set it
    for the call and restore it afterwards.
    """
    def run(args: list[str]) -> int:
        mod = importlib.import_module(f"eeik.{module}")
        saved = sys.argv
        sys.argv = [f"eeik-{module}", *prefix, *args]
        try:
            return mod.main()
        finally:
            sys.argv = saved
    return run


# ── status ────────────────────────────────────────────────────────────────────

def _collect_status() -> dict:
    """Gather EEIK state as a plain dict — the shared source for text + --json rendering."""
    try:
        import yaml
    except ImportError:
        return {"error": "pyyaml required (pip install pyyaml jsonschema)"}

    manifest_path = REPO_ROOT / "project-manifest.yaml"
    manifest_info: dict | None = None
    if manifest_path.exists():
        m = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        project = m.get("project", {})
        manifest_info = {
            "name": project.get("name", "(unnamed)"),
            "type": project.get("type", project.get("project_type", "?")),
            "domain": project.get("domain", "?"),
            "profile": m.get("governance", {}).get("profile", "?"),
        }

    agents_dir = REPO_ROOT / ".claude" / "agents"
    managed: list[str] = []
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            first = f.read_text(encoding="utf-8", errors="ignore").splitlines()
            if first and first[0].startswith("# eeik-managed"):
                managed.append(first[0].split("pack=")[-1].strip() if "pack=" in first[0] else "unknown")

    adapters = {
        "Claude Code": REPO_ROOT / ".claude",
        "Kiro":        REPO_ROOT / ".kiro",
        "Codex CLI":   REPO_ROOT / "AGENTS.md",
        "Cursor":      REPO_ROOT / ".cursor" / "rules",
        "Gemini CLI":  REPO_ROOT / "GEMINI.md",
        "Copilot":     REPO_ROOT / ".github" / "instructions",
    }
    return {
        "manifest": manifest_info,
        "activePacks": sorted(set(managed)),
        "adapters": {name: path.exists() for name, path in adapters.items()},
    }


def cmd_status(args: list[str]) -> int:
    state = _collect_status()
    if "error" in state:
        print(f"{ANSI_RED}{state['error']}{ANSI_RESET}")
        return 1

    if "--json" in args:
        print(json.dumps(state, indent=2))
        return 0

    print(f"\n{ANSI_BOLD}EEIK Status{ANSI_RESET}\n")
    mi = state["manifest"]
    if mi:
        print(f"  {ANSI_GREEN}✓{ANSI_RESET} Manifest found")
        print(f"      Project  : {mi['name']}")
        print(f"      Type     : {mi['type']}")
        print(f"      Domain   : {mi['domain']}")
        print(f"      Profile  : {mi['profile']}")
    else:
        print(f"  {ANSI_YELLOW}⚠{ANSI_RESET} No project-manifest.yaml — run /bootstrap or eeik seed")

    active_packs = state["activePacks"]
    if active_packs:
        print(f"\n  {ANSI_BOLD}Active packs ({len(active_packs)}){ANSI_RESET}")
        for p in active_packs:
            print(f"    • {p}")
    else:
        print(f"\n  {ANSI_YELLOW}⚠{ANSI_RESET} No managed packs activated — run: eeik activate --apply")

    print(f"\n  {ANSI_BOLD}Adapters{ANSI_RESET}")
    for name, exists in state["adapters"].items():
        icon = f"{ANSI_GREEN}✓{ANSI_RESET}" if exists else f"{ANSI_YELLOW}—{ANSI_RESET}"
        print(f"    {icon} {name}")

    print()
    return 0


# ── dispatch ──────────────────────────────────────────────────────────────────

COMMANDS = {
    "status":            cmd_status,
    "validate":          _mod("manifest"),
    "activate":          _mod("packs"),
    "generate-adapters": _mod("adapters"),
    "lock":              _mod("lock", "lock"),
    "diff":              _mod("lock", "diff"),
    "upgrade":           _mod("lock", "upgrade"),
    "catalog":           _mod("catalog"),
    "architectures":     _mod("architectures"),
    "verify":            _mod("verify"),
    "contract":          _mod("contract"),
    "mcp":               _mod("mcp_server"),
    "run":               _mod("runner"),
    "demo":              _mod("generation", "demo"),
    "seed":              _mod("seed"),
    "lessons":           _mod("lessons"),
    "doctor":            _mod("doctor"),
}

HELP = """
{bold}eeik — EEIK Bootstrap CLI{reset}

{bold}Usage:{reset}
  eeik <command> [options]        (or: python3 -m eeik <command>)

{bold}Commands:{reset}
  status              Show EEIK state (manifest, active packs, adapters)  [--json]
  validate            Validate project-manifest.yaml  [--strict] [--json]
  activate            Activate capability packs        [--apply] [--clean] [--list]
  generate-adapters   Generate multi-tool adapters     [--apply] [--tools kiro,codex,cursor,gemini]
  lock                Pin pack versions → eeik.lock    [--file path]
  diff                Report pack drift vs eeik.lock   [--exit-code] [--json]
  upgrade             Re-pin eeik.lock to current      [--file path]
  catalog             Query the pack/agent index       [--tag t] [--query x] [--provides n] [--json]
  architectures       List/show reference architectures [<name>] [--json]
  verify              Conformance gate                 [--strict] [--exit-code] [--json]
  contract            Emit a HALO Agent Contract       --blueprint <t> --name <n> [--param k=v] [--validate]
  mcp                 Start the EEIK MCP server        (read model over Model Context Protocol)
  run <generator>     Run generator on HALO harness    [--governed] [--dry-run]
  demo                Governed-generation showcase     (offline, no API key)
  seed                Copy the seed set into a project [--into DIR] [--apply] [--list]
  lessons             Capture lessons from audit logs  [--from FILE] [--list] [--json]
  doctor              Diagnose adoption/health problems [--json] [--strict] [--exit-code]

{bold}Quick start:{reset}
  1. eeik validate
  2. eeik activate --apply
  3. eeik generate-adapters --apply
  4. eeik lock          # pin adopted pack versions
  5. eeik diff          # later: detect drift from upstream
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
