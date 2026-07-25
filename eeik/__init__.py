"""eeik — the EEIK bootstrap engine.

An installable Python package: the executable core of EEIK (manifest validation, capability-pack
activation, multi-tool adapter generation, pack versioning + drift detection, and HALO-governed
generation). The engine operates on the repository's *content* layers (``capability-packs/``,
``knowledge/``, ``templates/``, ``generators/``, ``bootstrap/``), which are data, not code.

Console entry point ``eeik`` (see pyproject.toml); also runnable as ``python -m eeik``.
"""

from __future__ import annotations

__version__ = "1.4.0"

__all__ = ["__version__"]
