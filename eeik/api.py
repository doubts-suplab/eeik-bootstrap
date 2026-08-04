"""
EEIK public API (SDK) — the stable, typed, in-process surface for consuming the engine.

This is the counterpart to the MCP server (ADR-006): the MCP server serves the read model *over a
protocol*; this module serves the same read model *in-process*, so a consumer (e.g. apex-sdlc) can
``import eeik`` and call the engine as a library instead of shelling out to the CLI (ADR-007).

Everything here is re-exported from ``eeik`` — ``import eeik; eeik.validate_manifest(path=...)``. Return
values are frozen dataclasses with a ``.to_dict()`` for JSON; the CLI and the MCP tools are thin
adapters over these same functions, so there is one source of truth for behaviour.

Stability: the names and return shapes in ``__all__`` are the supported contract. Everything else in the
``eeik`` package is internal and may change.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from eeik import architectures as _architectures
from eeik import catalog as _catalog
from eeik import contract as _contract
from eeik import lock as _lock
from eeik import manifest as _manifest
from eeik import packs as _packs
from eeik.architectures import ReferenceArchitecture
from eeik.verify import Finding, VerifyReport, verify
from eeik.versions import all_pack_fingerprints

__version__ = "1.4.0"


# ── typed results ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Pack:
    """One capability pack and what it provides."""

    pack: str
    name: str
    version: str
    category: str
    description: str
    tags: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    standards: list[str] = field(default_factory=list)
    digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Provider:
    """A pack that provides a named agent/command/standard."""

    pack: str
    kind: str  # "agent" | "command" | "standard"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DriftEntry:
    pack: str
    kind: str  # added | removed | version-changed | content-changed
    from_version: str | None
    to_version: str | None

    def to_dict(self) -> dict[str, Any]:
        # Keep the wire/JSON keys stable ("from"/"to") regardless of the Python field names.
        return {"pack": self.pack, "kind": self.kind, "from": self.from_version, "to": self.to_version}


@dataclass(frozen=True)
class DriftReport:
    lock_present: bool
    entries: list[DriftEntry] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.entries)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lockPresent": self.lock_present,
            "driftCount": len(self.entries),
            "drift": [e.to_dict() for e in self.entries],
        }


# ── manifest input handling ───────────────────────────────────────────────────

def _resolve_manifest(
    manifest: dict | None, content: str | None, path: str | Path | None
) -> dict:
    """Accept an already-parsed dict, inline YAML, or a file path (precedence: manifest > content > path)."""
    if manifest is not None:
        doc = manifest
    elif content is not None:
        doc = yaml.safe_load(content)
    elif path is not None:
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    else:
        raise ValueError("provide one of: manifest (dict), content (YAML str), or path")
    if not isinstance(doc, dict):
        raise ValueError("manifest is not a YAML mapping")
    return doc


# ── public functions ──────────────────────────────────────────────────────────

def _to_pack(entry: dict) -> Pack:
    return Pack(
        pack=entry["pack"], name=entry["name"], version=entry["version"],
        category=entry["category"], description=entry["description"], tags=entry["tags"],
        agents=entry["agents"], commands=entry["commands"], standards=entry["standards"],
        digest=entry["digest"],
    )


def find_packs(*, tag: str | None = None, query: str | None = None) -> list[Pack]:
    """Every capability pack (optionally filtered by tag and/or free-text query)."""
    entries = _catalog.build_catalog()["packs"]
    if tag:
        entries = _catalog.filter_by_tag(entries, tag)
    if query:
        entries = _catalog.filter_by_query(entries, query)
    return [_to_pack(e) for e in entries]


def providers_of(name: str) -> list[Provider]:
    """Which pack(s) provide an agent/command/standard called ``name``."""
    entries = _catalog.build_catalog()["packs"]
    return [Provider(pack=p, kind=k) for p, k in _catalog.find_providers(entries, name)]


def validate_manifest(
    *, manifest: dict | None = None, content: str | None = None, path: str | Path | None = None
) -> ValidationResult:
    """Validate a manifest against the canonical schema + governance rules."""
    doc = _resolve_manifest(manifest, content, path)
    errors, warnings = _manifest.validate_document(doc)
    return ValidationResult(valid=not errors, errors=errors, warnings=warnings)


def resolve_packs(
    *, manifest: dict | None = None, content: str | None = None, path: str | Path | None = None
) -> list[str]:
    """The ordered capability packs a manifest activates (same logic as ``eeik activate``)."""
    doc = _resolve_manifest(manifest, content, path)
    return _packs.resolve_packs(doc, _packs.load_matrix())


def pack_drift(*, lockfile: str | Path | None = None) -> DriftReport:
    """Drift between ``eeik.lock`` and the packs on disk."""
    lock_p = _lock.lock_path(str(lockfile) if lockfile else None)
    locked = _lock.read_lock(lock_p)
    if locked is None:
        return DriftReport(lock_present=False)
    current = all_pack_fingerprints(_lock.resolve_current_packs())
    entries = [
        DriftEntry(pack=d["pack"], kind=d["kind"], from_version=d["from"], to_version=d["to"])
        for d in _lock.compute_drift(locked, current)
    ]
    return DriftReport(lock_present=True, entries=entries)


def write_lock(*, lockfile: str | Path | None = None) -> Path:
    """Pin the currently-resolved packs to a lockfile and return its path."""
    lock_p = _lock.lock_path(str(lockfile) if lockfile else None)
    _lock.write_lock(_lock.build_lock(_lock.resolve_current_packs()), lock_p)
    return lock_p


def agent_contract(blueprint: str, name: str, **params: str) -> dict:
    """Build a HALO-conformant Agent Contract for an agent generated from ``blueprint`` (ADR-009).

    Deterministic: the archetype fixes the authority ceiling, which fixes the permitted capabilities and
    the gate threshold — so a generated agent is runtime-governed by construction.
    """
    return _contract.build_contract(blueprint, name=name, params=params or None)


def validate_agent_contract(contract: dict) -> tuple[bool, str]:
    """Validate a contract against HALO's schema + the §3.3 binding rule (best-effort). (ok, message)."""
    return _contract.validate_contract(contract)


def reference_architectures() -> list[ReferenceArchitecture]:
    """Every proven, engine-surfaced architectural blueprint (ADR-010)."""
    return _architectures.load_all()


def reference_architecture(name: str) -> ReferenceArchitecture | None:
    """One reference architecture by name, or None."""
    return _architectures.get(name)


__all__ = [
    "Pack",
    "Provider",
    "ValidationResult",
    "DriftEntry",
    "DriftReport",
    "Finding",
    "VerifyReport",
    "find_packs",
    "providers_of",
    "validate_manifest",
    "resolve_packs",
    "pack_drift",
    "write_lock",
    "verify",
    "agent_contract",
    "validate_agent_contract",
    "ReferenceArchitecture",
    "reference_architectures",
    "reference_architecture",
    "__version__",
]
