#!/usr/bin/env python3
"""
EEIK Pack Versions — read and normalise capability-pack versions.

Every capability pack carries a ``metadata.yaml`` with a ``version`` field. EEIK treats
packs like versioned dependencies (see ADR-004): a project records which pack *versions*
it adopted in ``eeik.lock``, and drift detection compares that lock against the current
packs. This module is the single place that reads, normalises, and digests pack versions
so the lockfile and the drift detector agree on what a pack "is".

Used by ``eeik_lock.py`` and by ``eeik_cli.py`` (the ``lock`` / ``diff`` / ``upgrade`` commands).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    import sys

    print("ERROR: pyyaml required.  Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
PACKS_DIR = REPO_ROOT / "capability-packs"

# Subdirectories whose Markdown content defines a pack's materialised surface. A change to any
# of these files is a content change even when the declared version is untouched (drift).
CONTENT_SUBDIRS = ("agents", "commands", "standards", "workflows")


def normalise_version(raw: object) -> str:
    """Return a stable string version regardless of how YAML parsed it.

    ``version: 1.0`` parses to a float, ``version: "1.0"`` to a string, ``version: 1`` to an int.
    We normalise so ``1.0`` (float) and ``"1.0"`` (string) compare equal.
    """
    if raw is None:
        return "0.0.0"
    if isinstance(raw, float):
        # 1.0 -> "1.0", 1.10 -> "1.1" (float loses trailing zero; acceptable for semver-lite packs)
        text = repr(raw)
    else:
        text = str(raw).strip()
    return text or "0.0.0"


def read_pack_metadata(pack_dir: Path) -> dict:
    """Load a pack's ``metadata.yaml`` (empty dict if absent or unreadable)."""
    meta_path = pack_dir / "metadata.yaml"
    if not meta_path.exists():
        return {}
    try:
        with open(meta_path) as fh:
            return yaml.safe_load(fh) or {}
    except (OSError, yaml.YAMLError):
        return {}


def read_pack_version(pack_dir: Path) -> str:
    """The declared, normalised version of the pack at ``pack_dir``."""
    return normalise_version(read_pack_metadata(pack_dir).get("version"))


def content_digest(pack_dir: Path) -> str:
    """A stable SHA-256 over the pack's materialised Markdown surface.

    Detects content drift independent of the declared version: if a maintainer edits a standard
    or agent without bumping ``version``, the digest still changes and ``eeik diff`` flags it.
    """
    hasher = hashlib.sha256()
    for subdir in CONTENT_SUBDIRS:
        src = pack_dir / subdir
        if not src.exists():
            continue
        for md in sorted(src.rglob("*.md")):
            rel = md.relative_to(pack_dir).as_posix()
            hasher.update(rel.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(md.read_bytes())
            hasher.update(b"\0")
    return hasher.hexdigest()[:16]


def pack_fingerprint(pack_dir: Path) -> dict[str, str]:
    """The (version, digest) pair recorded for a pack in the lockfile."""
    return {"version": read_pack_version(pack_dir), "digest": content_digest(pack_dir)}


def all_pack_fingerprints(packs: list[str] | None = None) -> dict[str, dict[str, str]]:
    """Fingerprint every requested pack (or all packs on disk when ``packs`` is None)."""
    if packs is None:
        names = sorted(p.name for p in PACKS_DIR.iterdir() if p.is_dir())
    else:
        names = list(packs)
    result: dict[str, dict[str, str]] = {}
    for name in names:
        pack_dir = PACKS_DIR / name
        if pack_dir.is_dir():
            result[name] = pack_fingerprint(pack_dir)
    return result


if __name__ == "__main__":
    for pack_name, fp in all_pack_fingerprints().items():
        print(f"{pack_name:22}  v{fp['version']:8}  {fp['digest']}")
