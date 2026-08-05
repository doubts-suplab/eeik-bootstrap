"""Tests for the seed mechanism — the explicit dual-purpose adapter boundary (ADR-011)."""

from __future__ import annotations

from pathlib import Path

import eeik
from eeik import seed as seed_mod


def test_seed_plan_has_three_kinds_and_is_disjoint():
    plan = eeik.seed_plan()
    assert set(plan) == {"seed", "generated", "engine"}
    paths = {kind: {e["path"] for e in entries} for kind, entries in plan.items()}
    # No path is classified two ways — the boundary is unambiguous.
    assert paths["seed"].isdisjoint(paths["generated"])
    assert paths["seed"].isdisjoint(paths["engine"])
    assert paths["generated"].isdisjoint(paths["engine"])


def test_engine_only_paths_are_never_in_the_seed_set():
    seed_paths = {e["path"] for e in eeik.seed_plan()["seed"]}
    # The things that must never be copied into an adopting project.
    for engine_only in ("eeik", "tests", "pyproject.toml", "capability-packs", "eeik.lock"):
        assert engine_only not in seed_paths


def test_seed_copies_only_the_seed_set(tmp_path: Path):
    copied = 0
    for entry in eeik.seed_plan()["seed"]:
        msg, did = seed_mod._copy_entry(entry["path"], tmp_path, dry=False, dest=entry["dest"])
        copied += int(did)
    # Every seed entry that exists in the repo was copied into the target.
    assert copied >= 3
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".github" / "workflows" / "quality-gate.yml").exists()
    # An engine-only path was NOT dragged along.
    assert not (tmp_path / "eeik").exists()
    assert not (tmp_path / "pyproject.toml").exists()


def test_seed_claude_md_is_the_template_not_eeiks_own(tmp_path: Path):
    """The CLAUDE.md footgun: the seed must plant the project template, never EEIK's own root CLAUDE.md."""
    entry = next(e for e in eeik.seed_plan()["seed"] if e["dest"] == "CLAUDE.md")
    assert entry["path"] == "templates/PROJECT-CLAUDE.md"  # renamed source, not root CLAUDE.md
    seed_mod._copy_entry(entry["path"], tmp_path, dry=False, dest=entry["dest"])
    planted = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Replace all" in planted or "TODO" in planted     # it is the fill-in-the-blanks template
    assert "bootstrap and seed repository" not in planted      # NOT EEIK's own root CLAUDE.md


def test_seed_entries_reference_real_paths():
    """Every declared path (any kind) points at something in the repo — no stale manifest entries."""
    repo_root = seed_mod.REPO_ROOT
    plan = eeik.seed_plan()
    for kind in ("seed", "engine"):  # 'generated' may be absent until `eeik activate` runs
        for entry in plan[kind]:
            assert (repo_root / entry["path"]).exists(), f"{kind} path missing: {entry['path']}"
