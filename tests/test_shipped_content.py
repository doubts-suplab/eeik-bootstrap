"""Smoke tests over the *shipped* capability-pack content (not just engine logic).

These guard the repository's content layer: every pack that ships is well-formed, declares what it
provides, and passes the conformance gate. If someone adds a pack with a broken metadata.yaml or a
phantom agent, these fail — before the catalog/SDK advertise something that doesn't exist.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import eeik
from eeik.versions import PACKS_DIR

_PACK_DIRS = sorted(p for p in PACKS_DIR.iterdir() if p.is_dir() and (p / "metadata.yaml").exists())


def test_every_pack_has_wellformed_metadata():
    assert len(_PACK_DIRS) >= 22, "expected at least 22 shipped packs"
    for pack in _PACK_DIRS:
        meta = yaml.safe_load((pack / "metadata.yaml").read_text(encoding="utf-8"))
        assert meta.get("name"), f"{pack.name}: metadata has no name"
        assert str(meta.get("version", "")).strip(), f"{pack.name}: metadata has no version"


def test_catalog_covers_all_shipped_packs_with_digests():
    packs = eeik.find_packs()
    assert len(packs) >= 22
    assert all(p.digest for p in packs), "every catalog entry carries a content digest"
    # Language + domain enrichments are advertised.
    names = {p.pack for p in packs}
    assert {"go", "node", "retail"} <= names


def test_declared_agents_resolve_for_every_pack():
    """Every agent a pack declares in metadata resolves to a real file (via the catalog surface)."""
    for pack in _PACK_DIRS:
        meta = yaml.safe_load((pack / "metadata.yaml").read_text(encoding="utf-8"))
        for agent in meta.get("agents_provided", []) or []:
            providers = eeik.providers_of(agent)
            assert providers, f"{pack.name}: declared agent '{agent}' resolves to no provider"


def test_conformance_gate_is_clean_on_shipped_content():
    report = eeik.verify()
    fails = [f.to_dict() for f in report.findings if f.level == "fail"]
    assert not fails, f"shipped content fails conformance: {fails}"


def test_engine_repo_is_healthy():
    # The doctor should report the engine repo itself as set up correctly (no hard failures).
    assert eeik.doctor().ok is True


def test_representative_manifests_resolve_cleanly():
    examples = Path("bootstrap/examples")
    for ex in sorted(examples.glob("*.yaml")):
        result = eeik.validate_manifest(path=str(ex))
        assert result.valid, f"{ex.name}: {result.errors}"
        resolved = eeik.resolve_packs(path=str(ex))
        assert "core" in resolved  # core is always active
