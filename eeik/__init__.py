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
# return shapes are the supported contract; everything else in the package is internal.
from eeik.api import (
    DriftEntry,
    DriftReport,
    Pack,
    Provider,
    ValidationResult,
    find_packs,
    pack_drift,
    providers_of,
    resolve_packs,
    validate_manifest,
    write_lock,
)

__all__ = [
    "__version__",
    "Pack",
    "Provider",
    "ValidationResult",
    "DriftEntry",
    "DriftReport",
    "find_packs",
    "providers_of",
    "validate_manifest",
    "resolve_packs",
    "pack_drift",
    "write_lock",
]
