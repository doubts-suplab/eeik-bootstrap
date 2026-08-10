"""Pack-materialization tests — ``eeik activate`` copying pack content into ``.claude/``.

``activate(packs, dry, clean)`` is the adoption path: it copies a resolved pack's agents/standards/
commands/workflows into the shared ``.claude/`` layer, stamping each file with the ``# eeik-managed``
marker so a later ``--clean`` knows exactly what it owns. We redirect the target dirs
(``PACK_SUBDIRS``) to a temp tree — packs are still read from the real repo — and assert the copy,
the marker, dry-run safety, skip-on-exists, and clean semantics.
"""

from __future__ import annotations

import importlib

import pytest

packs = importlib.import_module("eeik.packs")


@pytest.fixture
def targets(tmp_path, monkeypatch):
    """Point every managed subdir at a temp tree; return the mapping."""
    mapping = {
        "agents": tmp_path / "agents",
        "commands": tmp_path / "commands",
        "standards": tmp_path / "standards",
        "workflows": tmp_path / "workflows",
    }
    monkeypatch.setattr(packs, "PACK_SUBDIRS", mapping)
    return mapping


def _md_files(d):
    return sorted(p.name for p in d.glob("*.md")) if d.exists() else []


# ── copy + managed marker ───────────────────────────────────────────────────────

def test_activate_copies_core_pack_files(targets):
    count = packs.activate(["core"], dry=False, clean=False)
    assert count > 0
    # core ships agents and standards.
    assert _md_files(targets["agents"]), "no agents materialised"
    assert _md_files(targets["standards"]), "no standards materialised"


def test_materialised_files_carry_the_managed_marker(targets):
    packs.activate(["core"], dry=False, clean=False)
    for f in targets["agents"].glob("*.md"):
        head = f.read_text(encoding="utf-8").splitlines()[0]
        assert head.startswith(packs.MANAGED_MARKER), f"{f.name} missing managed marker"
        assert "pack=core" in head


def test_activate_count_matches_files_written(targets):
    count = packs.activate(["core"], dry=False, clean=False)
    written = sum(len(_md_files(d)) for d in targets.values())
    assert count == written


# ── dry-run safety ──────────────────────────────────────────────────────────────

def test_dry_run_writes_nothing(targets):
    count = packs.activate(["core"], dry=True, clean=False)
    assert count > 0                       # it reports what it *would* copy
    for d in targets.values():
        assert _md_files(d) == []          # …but writes nothing


# ── skip-on-exists (no --clean) ─────────────────────────────────────────────────

def test_existing_unmanaged_file_is_not_overwritten(targets):
    # A hand-authored file already in the target layer must survive a plain activate.
    targets["agents"].mkdir(parents=True)
    keep = targets["agents"] / "architect.md"
    keep.write_text("hand-authored — do not touch\n", encoding="utf-8")

    packs.activate(["core"], dry=False, clean=False)

    assert keep.read_text(encoding="utf-8") == "hand-authored — do not touch\n"


# ── clean removes only managed files ────────────────────────────────────────────

def test_clean_removes_managed_but_keeps_unmanaged(targets):
    packs.activate(["core"], dry=False, clean=False)          # seed managed files
    targets["agents"].mkdir(parents=True, exist_ok=True)
    unmanaged = targets["agents"] / "my-custom-agent.md"
    unmanaged.write_text("mine\n", encoding="utf-8")

    before = set(_md_files(targets["agents"]))
    assert "my-custom-agent.md" in before and len(before) > 1

    packs.activate(["core"], dry=False, clean=True)           # clean + re-copy

    after = set(_md_files(targets["agents"]))
    assert "my-custom-agent.md" in after                      # unmanaged survived
    # managed files were removed then re-copied (still present, still marked)
    for f in targets["agents"].glob("*.md"):
        if f.name == "my-custom-agent.md":
            continue
        assert f.read_text(encoding="utf-8").startswith(packs.MANAGED_MARKER)


def test_activate_missing_pack_dir_does_not_crash(targets):
    # A pack with no directory on disk contributes nothing rather than raising.
    count = packs.activate(["no-such-pack"], dry=False, clean=False)
    assert count == 0
