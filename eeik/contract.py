#!/usr/bin/env python3
"""
EEIK Agent Contracts — emit HALO-conformant Agent Contracts from agent blueprints (ADR-009).

Closes the last conceptual gap: every agent EEIK generates is born **runtime-governed by construction**.
Where the agent-generator produces a `.agent.md` *persona* (prompt/behaviour), this module produces the
machine-readable **Agent Contract** — the static governance envelope a HALO runtime loads at startup:
authority ceiling, allowed DecisionActions, confidence-gate threshold + escalation path, a default-deny
tool allowlist, and safe failure behaviour. Conforms to
`agent-harness/docs/spec/agent-contract.schema.json` (spec §10).

The build is **deterministic** (no LLM): a blueprint's archetype fixes the authority level, and the
authority fixes the permitted capabilities and the gate threshold — so a generated contract cannot, by
construction, declare a capability beyond its ceiling or a threshold below the 0.80 floor. Contracts are
emitted with an **unsigned** governance block: they are drafts a human signs off (AI drafts, human approves).

    eeik contract --blueprint reviewer --name java-reviewer --param language=java --validate

Validation reuses HALO's own `agent_harness.contract.validate_contract` (schema + the §3.3 binding rule)
when the harness + schema are locatable; otherwise generation still works and validation is reported as
skipped (fail-safe).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: pyyaml required.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
BLUEPRINTS_DIR = REPO_ROOT / "generators" / "agent-generator" / "blueprints"

# Blueprint archetype → static authority ceiling (spec §3.1). Coordinators are supervisors (hold no tools).
_AUTHORITY: dict[str, str] = {
    "investigator": "OBSERVE",   # read-only analysis (RCA, forensics)
    "architect": "SUGGEST",
    "engineer": "SUGGEST",
    "specialist": "SUGGEST",
    "planner": "SUGGEST",
    "coordinator": "SUGGEST",    # supervisor — toolAccess MUST be empty (T-4)
    "reviewer": "ALERT",         # advisory findings; may auto-enforce when confident
    "auditor": "BLOCK",          # security/compliance gate
}

# DecisionActions permitted at each authority (every action within the ceiling, spec §3.3).
_CAPABILITIES: dict[str, list[str]] = {
    "OBSERVE": ["ALLOW", "DEFER"],
    "SUGGEST": ["ALLOW", "SUGGEST", "DEFER"],
    "ALERT": ["ALLOW", "SUGGEST", "ALERT", "DEFER"],
    "RATE_LIMIT": ["ALLOW", "SUGGEST", "ALERT", "DEFER"],
    "BLOCK": ["ALLOW", "SUGGEST", "ALERT", "BLOCK", "DEFER"],
}

# Auto-enforce threshold per authority (spec §4); never below the 0.80 floor (G-3).
_THRESHOLD: dict[str, float] = {"ALERT": 0.80, "RATE_LIMIT": 0.85, "BLOCK": 0.95}

# Claude-Code tool name → harness permission + side effect.
_TOOL_PERMISSION = {
    "Read": "Read", "Glob": "Read", "Grep": "Read", "LS": "Read", "NotebookRead": "Read",
    "Edit": "Write", "MultiEdit": "Write", "Write": "Write", "NotebookEdit": "Write",
    "Bash": "Invoke", "WebFetch": "Invoke", "WebSearch": "Invoke",
}
_SIDE_EFFECT = {"Read": "read", "Write": "write", "Invoke": "external"}

_CONTEXT_KEYS = {
    "reviewer": ["changeset"], "auditor": ["target"], "architect": ["requirements"],
    "engineer": ["ticket"], "specialist": ["task"], "investigator": ["incident"],
    "planner": ["scope"], "coordinator": ["objective"],
}


def _slug(name: str) -> str:
    """Slugify to the identity.agentName pattern ^[a-z][a-z0-9-]*$."""
    s = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    return s or "agent"


def load_blueprint(blueprint: str) -> dict:
    path = BLUEPRINTS_DIR / f"{blueprint}.yaml"
    if not path.exists():
        available = sorted(p.stem for p in BLUEPRINTS_DIR.glob("*.yaml"))
        raise ValueError(f"unknown blueprint '{blueprint}'. Available: {', '.join(available)}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _tool_access(blueprint: str, tools: list[str]) -> list[dict]:
    # Supervisors hold no tools (spec §5, T-4).
    if blueprint == "coordinator":
        return []
    access = []
    for tool in tools:
        perm = _TOOL_PERMISSION.get(tool, "Read")
        access.append({
            "tool": tool,
            "permission": perm,
            "purpose": f"{perm} access for {blueprint} tasks",
            "sideEffect": _SIDE_EFFECT[perm],
        })
    return access


def build_contract(blueprint: str, *, name: str, params: dict | None = None, version: str = "1.0.0") -> dict:
    """Build a HALO-conformant Agent Contract for an agent generated from ``blueprint``.

    Authority is fixed by the archetype; capabilities and the gate threshold are then derived so the
    contract cannot declare more than its ceiling. The governance sign-off is left unsigned (draft).
    """
    bp = load_blueprint(blueprint)
    params = params or {}
    authority = _AUTHORITY.get(blueprint, "SUGGEST")
    agent_name = _slug(name)
    tools = (bp.get("fixed", {}) or {}).get("tools_allowed", []) or []

    purpose = (bp.get("description") or f"{blueprint} agent").strip()
    if params:
        purpose += " (" + ", ".join(f"{k}={v}" for k, v in params.items()) + ")"
    purpose += ". Generated by EEIK from the '" + blueprint + "' blueprint; runtime-governed on HALO."

    contract = {
        "schemaVersion": "1.0",
        "identity": {
            "agentName": agent_name,
            "agentClass": f"{blueprint.capitalize()}Agent",
            "capabilityEnum": blueprint.upper(),
            "ownerService": "eeik-generated",
            "version": version,
        },
        "purpose": purpose,
        "authorityLevel": authority,
        "capabilities": _CAPABILITIES[authority],
        "confidenceGate": {
            "threshold": _THRESHOLD.get(authority, 0.80),
            "escalationPath": f"{agent_name}-human-review",
        },
        "toolAccess": _tool_access(blueprint, tools),
        "inputContract": {
            "tenantScoped": True,
            "requiredContextKeys": _CONTEXT_KEYS.get(blueprint, ["task"]),
        },
        "outputContract": {"emitsDecision": True, "rationaleAlwaysPresent": True},
        "failureBehaviour": [
            {"failure": "LLM unavailable", "action": "DEFER", "confidence": 0.5, "autoEnforced": False},
            {"failure": "required context missing", "action": "DEFER", "confidence": 0.5, "autoEnforced": False},
        ],
        "testingRequirements": [
            "fast-path: required context missing -> DEFER",
            "LLM-path: high-confidence decision auto-enforces within authority",
            "LLM-failure: falls back to DEFER, autoEnforced=false",
            f"low-confidence: decision below {_THRESHOLD.get(authority, 0.80)} routes to human review",
            "capability-declaration: emitted action is within authorityLevel",
        ],
        "governance": {"signoff": [{"role": "Agent Engineer"}]},  # unsigned draft — human approves
    }
    return contract


# ── validation (best-effort, via HALO's own validator) ────────────────────────

def _locate_schema() -> Path | None:
    """Find agent-contract.schema.json: env var, HALO editable install, or a sibling agent-harness repo."""
    env = os.environ.get("AGENT_CONTRACT_SCHEMA")
    if env and Path(env).is_file():
        return Path(env)
    try:
        from agent_harness.contract import _default_schema_path

        return _default_schema_path()
    except Exception:
        pass
    for base in (REPO_ROOT.parent, Path.home()):
        cand = base / "agent-harness" / "docs" / "spec" / "agent-contract.schema.json"
        if cand.is_file():
            return cand
    return None


def validate_contract(contract: dict) -> tuple[bool, str]:
    """Validate a contract against HALO's schema + the §3.3 binding rule. Best-effort.

    Returns (ok, message). If the harness or schema cannot be located, returns (False, 'skipped: …')
    rather than raising — generation never hard-depends on the harness being present.
    """
    try:
        from agent_harness.contract import validate_contract as halo_validate
    except ImportError:
        return (False, "skipped: agent-harness not installed")
    schema = _locate_schema()
    if schema is None:
        return (False, "skipped: agent-contract.schema.json not found (set AGENT_CONTRACT_SCHEMA)")
    try:
        halo_validate(contract, schema_path=schema)
        return (True, "valid against agent-contract.schema.json + §3.3 binding rule")
    except Exception as exc:
        return (False, f"invalid: {exc}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a HALO Agent Contract from an EEIK blueprint")
    parser.add_argument("--blueprint", required=True, help="Blueprint archetype (reviewer, engineer, …)")
    parser.add_argument("--name", required=True, help="Agent name (e.g. java-reviewer)")
    parser.add_argument("--param", action="append", default=[], metavar="k=v",
                        help="Blueprint parameter (repeatable), e.g. --param language=java")
    parser.add_argument("--validate", action="store_true", help="Validate against HALO's schema")
    parser.add_argument("--output", metavar="PATH", help="Write the contract JSON to a file")
    args = parser.parse_args()

    params = {}
    for kv in args.param:
        if "=" in kv:
            k, v = kv.split("=", 1)
            params[k.strip()] = v.strip()

    try:
        contract = build_contract(args.blueprint, name=args.name, params=params)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(contract, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(f"✓ Wrote {args.output}", file=sys.stderr)
    else:
        print(text)

    if args.validate:
        ok, msg = validate_contract(contract)
        stream = sys.stderr
        mark = "✓" if ok else "⚠"
        print(f"{mark} {msg}", file=stream)
        if not ok and msg.startswith("invalid"):
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
