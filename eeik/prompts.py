#!/usr/bin/env python3
"""Generator prompt assembly — the shared seam between the runner and the governed generation path.

This module holds the generator registry and the manifest/prompt assembly used by both ``eeik run``
(``eeik/runner.py``) and the LLM-backed producer (``eeik/generation.py``). It imports neither of them,
so the two callers depend on it one-directionally — no import cycle (CodeQL py/import-cycle).
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml  # pyyaml is a core runtime dependency (see pyproject.toml)

REPO_ROOT = Path(__file__).parent.parent
GENERATORS = REPO_ROOT / "generators"

ANSI_RED = "\033[91m"
ANSI_RESET = "\033[0m"

# ── Generator registry ────────────────────────────────────────────────────────
# Maps generator name → primary prompt file path (relative to GENERATORS/).

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
    """Assemble the full prompt to send to the model."""
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
