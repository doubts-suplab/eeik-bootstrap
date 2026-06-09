#!/usr/bin/env python3
"""
EEIK Claude Harness
Runs EEIK generator prompts non-interactively via the `claude -p` CLI.
This turns every markdown generator into a CI-executable step.

Usage:
    python3 scripts/claude_harness.py <generator-name> [options]
    python3 scripts/eeik_cli.py run <generator-name> [options]

Generators:
    repository-generator    Generate full repo scaffold from manifest
    project-analyzer        Analyse existing repo → draft manifest
    agent-generator         Generate a new agent from a blueprint
    knowledge-generator     Run a knowledge extraction workflow
    governance-generator    Generate governance artefacts

Options:
    --dry-run               Print assembled prompt, do not call claude
    --output <path>         Write claude output to file (default: stdout)
    --manifest <path>       Explicit manifest path
    --extra "text"          Append extra instructions to the prompt

Examples:
    # Dry-run: see what prompt would be sent
    python3 scripts/claude_harness.py repository-generator --dry-run

    # Generate repo scaffold (writes to stdout)
    python3 scripts/claude_harness.py repository-generator

    # Analyse project and write draft manifest
    python3 scripts/claude_harness.py project-analyzer --output project-manifest.yaml

Requirements:
    - claude CLI installed: npm install -g @anthropic-ai/claude-code
    - ANTHROPIC_API_KEY set in environment (or claude already authenticated)
"""

import sys
import os
import argparse
import subprocess
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT   = Path(__file__).parent.parent
GENERATORS  = REPO_ROOT / "generators"

ANSI_BOLD   = "\033[1m"
ANSI_GREEN  = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_RED    = "\033[91m"
ANSI_CYAN   = "\033[96m"
ANSI_RESET  = "\033[0m"


# ── Generator registry ────────────────────────────────────────────────────────
# Maps generator name → primary prompt file path (relative to GENERATORS/)

GENERATOR_REGISTRY: dict[str, str] = {
    "repository-generator": "repository-generator/prompts/generate-repo.md",
    "project-analyzer":     "project-analyzer/prompts/analyze-project.md",
    "agent-generator":      "agent-generator/prompts/generate-agent.md",
    "knowledge-generator":  "knowledge-generator/workflows/knowledge-capture.yaml",
    "governance-generator": "governance-generator/prompts/generate-governance.md",
}


def load_manifest(manifest_path: str | None) -> dict:
    candidates = [
        Path(manifest_path) if manifest_path else None,
        REPO_ROOT / "project-manifest.yaml",
        REPO_ROOT / "bootstrap" / "manifests" / "project-manifest.yaml",
    ]
    for p in candidates:
        if p and p.exists():
            with open(p) as f:
                return yaml.safe_load(f) or {}
    return {}


def load_prompt(generator: str) -> str:
    if generator not in GENERATOR_REGISTRY:
        print(f"{ANSI_RED}Unknown generator: {generator}{ANSI_RESET}", file=sys.stderr)
        print(f"Available: {', '.join(GENERATOR_REGISTRY)}", file=sys.stderr)
        sys.exit(1)

    prompt_path = GENERATORS / GENERATOR_REGISTRY[generator]
    if not prompt_path.exists():
        print(f"{ANSI_RED}Prompt file not found: {prompt_path}{ANSI_RESET}", file=sys.stderr)
        sys.exit(1)

    return prompt_path.read_text(encoding="utf-8")


def build_prompt(generator: str, manifest: dict, extra: str | None) -> str:
    """Assemble the full prompt to send to claude."""
    base_prompt = load_prompt(generator)

    sections = [
        "# EEIK Generator Run",
        f"Generator: {generator}",
        "",
        "## Project Manifest (source of truth)",
        "```yaml",
        yaml.dump(manifest, default_flow_style=False) if manifest else "(no manifest found — use defaults)",
        "```",
        "",
        "## Generator Instructions",
        base_prompt,
    ]

    if extra:
        sections += ["", "## Additional Instructions", extra]

    return "\n".join(sections)


def check_claude_available() -> bool:
    """Check if the claude CLI is installed and accessible."""
    result = subprocess.run(["claude", "--version"], capture_output=True, text=True)
    return result.returncode == 0


def run_claude(prompt: str, output_path: str | None) -> int:
    """Call claude -p with the assembled prompt."""
    if not check_claude_available():
        print(f"{ANSI_RED}ERROR: claude CLI not found.{ANSI_RESET}", file=sys.stderr)
        print("  Install via: npm install -g @anthropic-ai/claude-code", file=sys.stderr)
        print("  Then authenticate: claude login", file=sys.stderr)
        return 1

    # Write prompt to a temp file to avoid shell quoting issues
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tf:
        tf.write(prompt)
        prompt_file = tf.name

    try:
        cmd = ["claude", "-p", f"$(cat {prompt_file})"]

        # Use --output-format json for structured output when saving to file
        if output_path:
            cmd += ["--output-format", "text"]

        print(f"\n{ANSI_CYAN}Running: claude -p <prompt>{ANSI_RESET}")
        print(f"{ANSI_YELLOW}(This may take 30–120 seconds depending on generator complexity){ANSI_RESET}\n")

        # Simpler invocation: pipe prompt via stdin
        result = subprocess.run(
            ["claude", "--print"],
            input=prompt,
            capture_output=(output_path is not None),
            text=True,
            cwd=str(REPO_ROOT),
        )

        if output_path and result.stdout:
            Path(output_path).write_text(result.stdout, encoding="utf-8")
            print(f"{ANSI_GREEN}✓ Output written to: {output_path}{ANSI_RESET}")
        elif result.returncode != 0:
            print(f"{ANSI_RED}claude exited with code {result.returncode}{ANSI_RESET}", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

        return result.returncode
    finally:
        Path(prompt_file).unlink(missing_ok=True)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run EEIK generators via Claude harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available generators:\n" + "\n".join(f"  {k}" for k in GENERATOR_REGISTRY),
    )
    parser.add_argument("generator", nargs="?", help="Generator name")
    parser.add_argument("--dry-run",  action="store_true", help="Print prompt only, do not call claude")
    parser.add_argument("--output",   metavar="PATH",      help="Write output to file")
    parser.add_argument("--manifest", metavar="PATH",      help="Explicit manifest.yaml path")
    parser.add_argument("--extra",    metavar="TEXT",      help="Append extra instructions")
    parser.add_argument("--list",     action="store_true", help="List available generators")
    args = parser.parse_args()

    if args.list or not args.generator:
        print(f"\n{ANSI_BOLD}Available generators:{ANSI_RESET}")
        for name, path in GENERATOR_REGISTRY.items():
            exists = (GENERATORS / path).exists()
            icon   = f"{ANSI_GREEN}✓{ANSI_RESET}" if exists else f"{ANSI_YELLOW}✗{ANSI_RESET}"
            print(f"  {icon} {name}")
        return 0

    manifest = load_manifest(args.manifest)
    prompt   = build_prompt(args.generator, manifest, args.extra)

    if args.dry_run:
        print(f"\n{ANSI_BOLD}=== Assembled Prompt ({len(prompt)} chars) ==={ANSI_RESET}\n")
        # Print first 3000 chars to avoid flooding terminal
        print(prompt[:3000])
        if len(prompt) > 3000:
            print(f"\n{ANSI_YELLOW}... (truncated, full prompt is {len(prompt)} chars){ANSI_RESET}")
        return 0

    return run_claude(prompt, args.output)


if __name__ == "__main__":
    sys.exit(main())
