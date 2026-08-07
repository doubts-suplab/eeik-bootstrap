"""`--json` parity across inspection commands (status / validate / diff)."""

from __future__ import annotations

import json
from pathlib import Path

from eeik import lock as lock_mod
from eeik import manifest as manifest_mod
from eeik.cli import cmd_status


def _run_json(capsys, fn) -> dict:
    fn()
    out = capsys.readouterr().out
    return json.loads(out)


def test_status_json(capsys):
    data = _run_json(capsys, lambda: cmd_status(["--json"]))
    assert set(data) == {"manifest", "activePacks", "adapters"}
    assert isinstance(data["adapters"], dict) and "Claude Code" in data["adapters"]


def test_validate_json_valid(capsys, monkeypatch):
    monkeypatch.setattr(
        "sys.argv", ["eeik-manifest", "bootstrap/examples/greenfield-java-aws.yaml", "--json"]
    )
    rc = manifest_mod.main()
    data = json.loads(capsys.readouterr().out)
    assert data == {"valid": True, "errors": [], "warnings": []}
    assert rc == 0


def test_validate_json_invalid(capsys, monkeypatch, tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("project:\n  name: x\n")  # missing required sections
    monkeypatch.setattr("sys.argv", ["eeik-manifest", str(bad), "--json"])
    rc = manifest_mod.main()
    data = json.loads(capsys.readouterr().out)
    assert data["valid"] is False and data["errors"]
    assert rc == 1


def test_diff_json(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["eeik-lock", "diff", "--json"])
    lock_mod.main()
    data = json.loads(capsys.readouterr().out)
    assert set(data) == {"lockPresent", "driftCount", "drift"}
    # Shape matches eeik.pack_drift().to_dict() — one drift schema everywhere.
    assert isinstance(data["drift"], list)


def test_diff_json_shape_matches_sdk():
    import eeik

    sdk = eeik.pack_drift().to_dict()
    assert set(sdk) == {"lockPresent", "driftCount", "drift"}
