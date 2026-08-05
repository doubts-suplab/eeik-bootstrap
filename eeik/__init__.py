"""eeik — the EEIK bootstrap engine.

An installable Python package: the executable core of EEIK (manifest validation, capability-pack
activation, multi-tool adapter generation, pack versioning + drift detection, and HALO-governed
generation). The engine operates on the repository's *content* layers (``capability-packs/``,
``knowledge/``, ``templates/``, ``generators/``, ``bootstrap/``), which are data, not code.

Console entry point ``eeik`` (see pyproject.toml); also runnable as ``python -m eeik``.
"""

from __future__ import annotations

__version__ = "1.4.0"

# Public SDK surface (ADR-007) — `import eeik; eeik.validate_manifest(...)`. These names and their
# return shapes are the supported contract; everything else in the package is internal. (The CLI
# dispatches subcommands in-process — see cli.py — so this eager import does not trigger the
# `python -m` re-execution warning.)
from eeik.api import (
    DriftEntry,
    DriftReport,
    Finding,
    GenerationOutcome,
    Pack,
    Provider,
    ReferenceArchitecture,
    ValidationResult,
    VerifyReport,
    agent_contract,
    find_packs,
    generate,
    pack_drift,
    providers_of,
    reference_architecture,
    reference_architectures,
    resolve_packs,
    seed_plan,
    validate_agent_contract,
    validate_manifest,
    verify,
    write_lock,
)

__all__ = [
    "__version__",
    "Pack",
    "Provider",
    "ValidationResult",
    "DriftEntry",
    "DriftReport",
    "Finding",
    "VerifyReport",
    "GenerationOutcome",
    "ReferenceArchitecture",
    "find_packs",
    "providers_of",
    "validate_manifest",
    "resolve_packs",
    "pack_drift",
    "write_lock",
    "verify",
    "agent_contract",
    "validate_agent_contract",
    "generate",
    "seed_plan",
    "reference_architectures",
    "reference_architecture",
]
