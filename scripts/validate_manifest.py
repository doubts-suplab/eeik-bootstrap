#!/usr/bin/env python3
"""
EEIK Manifest Validator
Validates project-manifest.yaml against the JSON Schema plus EEIK-specific
governance rules that can't be expressed in schema alone.

Usage:
    python3 scripts/validate_manifest.py                        # auto-detects manifest
    python3 scripts/validate_manifest.py path/to/manifest.yaml  # explicit path
    python3 scripts/validate_manifest.py --strict               # treat warnings as errors
"""

import sys
import json
import re
from pathlib import Path

# ── dependency check ──────────────────────────────────────────────────────────
try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required.  Run: pip install pyyaml jsonschema", file=sys.stderr)
    sys.exit(1)

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("ERROR: jsonschema is required.  Run: pip install pyyaml jsonschema", file=sys.stderr)
    sys.exit(1)

# ── paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
REPO_ROOT    = SCRIPT_DIR.parent
SCHEMA_FILE  = SCRIPT_DIR / "schemas" / "project-manifest.schema.json"
PACKS_DIR    = REPO_ROOT / "capability-packs"

ANSI_RED     = "\033[91m"
ANSI_YELLOW  = "\033[93m"
ANSI_GREEN   = "\033[92m"
ANSI_CYAN    = "\033[96m"
ANSI_RESET   = "\033[0m"
ANSI_BOLD    = "\033[1m"


def err(msg: str)  -> None: print(f"{ANSI_RED}  ✗ {msg}{ANSI_RESET}")
def warn(msg: str) -> None: print(f"{ANSI_YELLOW}  ⚠ {msg}{ANSI_RESET}")
def ok(msg: str)   -> None: print(f"{ANSI_GREEN}  ✓ {msg}{ANSI_RESET}")
def info(msg: str) -> None: print(f"{ANSI_CYAN}  ℹ {msg}{ANSI_RESET}")


# ── governance rules (beyond JSON Schema) ────────────────────────────────────

def check_governance_rules(manifest: dict) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings)."""
    errors:   list[str] = []
    warnings: list[str] = []

    gov     = manifest.get("governance", {})
    tech    = manifest.get("technology", {})
    project = manifest.get("project", {})
    profile = gov.get("profile", "basic")
    domain  = project.get("domain", "generic")

    # ── Rule G001: regulated profile requires compliance frameworks
    if profile == "regulated":
        frameworks = gov.get("compliance_frameworks", [])
        if not frameworks or frameworks == ["none"]:
            errors.append(
                "governance.profile=regulated requires at least one compliance_framework "
                "(gdpr, pci-dss, hipaa, etc.)"
            )

    # ── Rule G002: domain-compliance alignment
    DOMAIN_REQUIRED = {
        "banking":    ["pci-dss", "basel-iii"],
        "healthcare": ["hipaa", "gdpr"],
        "insurance":  ["solvency-ii", "gdpr"],
    }
    if domain in DOMAIN_REQUIRED:
        frameworks = gov.get("compliance_frameworks", [])
        missing = [f for f in DOMAIN_REQUIRED[domain] if f not in frameworks]
        if missing:
            warnings.append(
                f"Domain '{domain}' typically requires: {', '.join(missing)} — "
                "add to governance.compliance_frameworks or confirm not applicable"
            )

    # ── Rule G003: enterprise profile needs ADR
    if profile == "enterprise" and not gov.get("adr_required", False):
        warnings.append(
            "governance.profile=enterprise: recommend setting adr_required: true"
        )

    # ── Rule G004: coverage threshold for regulated / enterprise
    threshold = gov.get("coverage_threshold", 0)
    if profile in ("regulated", "enterprise") and threshold < 80:
        warnings.append(
            f"governance.coverage_threshold={threshold} — regulated/enterprise projects "
            "should target ≥80%"
        )

    # ── Rule T001: Java version in Spring Boot 3 context
    backend = tech.get("backend", {})
    if backend.get("language") == "java":
        version_str = str(backend.get("version", "0"))
        try:
            major = int(version_str.split(".")[0])
            if major < 17:
                warnings.append(
                    f"technology.backend.version={version_str} — Spring Boot 3.x requires Java 17+; "
                    "consider upgrading"
                )
        except ValueError:
            warnings.append(f"technology.backend.version='{version_str}' — could not parse Java version")

    # ── Rule T002: IaC required when cloud provider is set
    cloud = tech.get("cloud", {})
    if cloud.get("provider", "none") not in ("none", "") and cloud.get("iac_tool", "none") == "none":
        warnings.append(
            "technology.cloud.provider is set but technology.cloud.iac_tool is 'none' — "
            "specify cdk, terraform, or pulumi"
        )

    # ── Rule T003: secret store required for production environments
    envs         = project.get("environments", [])
    integrations = manifest.get("integrations", {})
    if "prod" in envs and integrations.get("secret_store", "none") == "none":
        errors.append(
            "integrations.secret_store must be set when environments includes 'prod' — "
            "use aws-secrets-manager, azure-key-vault, or hashicorp-vault"
        )

    # ── Rule P001: project name — no spaces, URL-safe
    name = project.get("name", "")
    if name and not re.match(r'^[a-zA-Z0-9_\-]+$', name):
        errors.append(
            f"project.name='{name}' — use kebab-case or snake_case (no spaces or special chars)"
        )

    # ── Rule P002: mainframe platform with no languages
    mf = tech.get("mainframe", {})
    if mf.get("platform", "none") != "none" and not mf.get("languages"):
        warnings.append(
            "technology.mainframe.platform is set but no languages listed — "
            "add rpg, cobol, cl, jcl as applicable"
        )

    return errors, warnings


# ── capability pack existence check ──────────────────────────────────────────

def check_pack_overrides(manifest: dict) -> list[str]:
    """Warn if explicitly listed packs don't exist in the repo."""
    warnings: list[str] = []
    cap = manifest.get("capability_packs", {})
    for pack_name in cap.get("include", []):
        pack_path = PACKS_DIR / pack_name
        if not pack_path.exists():
            warnings.append(
                f"capability_packs.include: '{pack_name}' not found in capability-packs/ — "
                "check spelling or create the pack"
            )
    return warnings


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    strict = "--strict" in sys.argv
    args   = [a for a in sys.argv[1:] if not a.startswith("--")]

    # Locate manifest
    if args:
        manifest_path = Path(args[0])
    else:
        candidates = [
            REPO_ROOT / "project-manifest.yaml",
            REPO_ROOT / "bootstrap" / "manifests" / "project-manifest.yaml",
            Path("project-manifest.yaml"),
        ]
        manifest_path = next((p for p in candidates if p.exists()), None)
        if manifest_path is None:
            print(f"{ANSI_RED}ERROR: No project-manifest.yaml found.{ANSI_RESET}")
            print("  Run /bootstrap to generate one, or pass the path explicitly.")
            return 1

    print(f"\n{ANSI_BOLD}EEIK Manifest Validator{ANSI_RESET}")
    print(f"  Manifest : {manifest_path}")
    print(f"  Schema   : {SCHEMA_FILE}")
    print(f"  Mode     : {'strict' if strict else 'normal'}\n")

    # Load YAML
    try:
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        err(f"YAML parse error: {exc}")
        return 1

    if not isinstance(manifest, dict):
        err("Manifest is not a YAML mapping (dict at root level)")
        return 1

    # Load schema
    with open(SCHEMA_FILE) as f:
        schema = json.load(f)

    # ── Phase 1: JSON Schema validation ───────────────────────────────────────
    print(f"{ANSI_BOLD}Phase 1: Schema validation{ANSI_RESET}")
    validator    = Draft7Validator(schema)
    schema_errors = sorted(validator.iter_errors(manifest), key=lambda e: e.path)
    if schema_errors:
        for e in schema_errors:
            path = ".".join(str(p) for p in e.absolute_path) or "(root)"
            err(f"[{path}] {e.message}")
        print()
    else:
        ok("Schema valid")

    # ── Phase 2: Governance rules ─────────────────────────────────────────────
    print(f"\n{ANSI_BOLD}Phase 2: Governance rules{ANSI_RESET}")
    gov_errors, gov_warnings = check_governance_rules(manifest)
    pack_warnings             = check_pack_overrides(manifest)
    all_warnings = gov_warnings + pack_warnings

    for e in gov_errors:
        err(e)
    for w in all_warnings:
        warn(w)
    if not gov_errors and not all_warnings:
        ok("All governance rules passed")
    elif not gov_errors:
        ok(f"No errors — {len(all_warnings)} warning(s)")

    # ── Summary ───────────────────────────────────────────────────────────────
    total_errors   = len(schema_errors) + len(gov_errors)
    total_warnings = len(all_warnings)

    print(f"\n{ANSI_BOLD}Summary{ANSI_RESET}")
    print(f"  Errors   : {total_errors}")
    print(f"  Warnings : {total_warnings}")

    if total_errors == 0 and total_warnings == 0:
        print(f"\n{ANSI_GREEN}{ANSI_BOLD}✓ Manifest is valid.{ANSI_RESET}\n")
        return 0
    elif total_errors == 0 and not strict:
        print(f"\n{ANSI_YELLOW}{ANSI_BOLD}⚠ Manifest valid with warnings.  Use --strict to treat as errors.{ANSI_RESET}\n")
        return 0
    else:
        print(f"\n{ANSI_RED}{ANSI_BOLD}✗ Validation failed.{ANSI_RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
