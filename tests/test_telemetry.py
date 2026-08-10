"""Opt-in telemetry tests — off by default, local-only, non-identifying, never raises.

Every test points ``EEIK_TELEMETRY_DIR`` at a temp dir so nothing touches the real ``~/.eeik``.
"""

from __future__ import annotations

import importlib

import pytest

telemetry = importlib.import_module("eeik.telemetry")


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    monkeypatch.setenv("EEIK_TELEMETRY_DIR", str(tmp_path))
    monkeypatch.delenv("EEIK_TELEMETRY", raising=False)
    return tmp_path


# ── off by default ──────────────────────────────────────────────────────────────

def test_disabled_by_default(isolated_home):
    assert telemetry.is_enabled() is False


def test_record_is_noop_when_disabled(isolated_home):
    telemetry.record("pack", "core")
    assert telemetry.summary()["counters"] == {}
    # No data file is created while disabled.
    assert not (isolated_home / "telemetry.json").exists()


def test_env_flag_enables(isolated_home, monkeypatch):
    monkeypatch.setenv("EEIK_TELEMETRY", "1")
    assert telemetry.is_enabled() is True


# ── enable → record → summary ─────────────────────────────────────────────────────

def test_enable_then_record_counts(isolated_home):
    telemetry.enable()
    assert telemetry.is_enabled() is True
    telemetry.record("pack", "core")
    telemetry.record("pack", "core")
    telemetry.record("pack", "java")
    telemetry.record("generator", "agent-generator")

    counters = telemetry.summary()["counters"]
    assert counters["pack"] == {"core": 2, "java": 1}
    assert counters["generator"] == {"agent-generator": 1}
    assert telemetry.summary()["last_updated"]  # a coarse date is stamped


def test_disable_keeps_data_but_stops_recording(isolated_home):
    telemetry.enable()
    telemetry.record("pack", "core")
    telemetry.disable()
    assert telemetry.is_enabled() is False
    telemetry.record("pack", "core")                 # ignored now
    assert telemetry.summary()["counters"]["pack"] == {"core": 1}


def test_clear_deletes_local_data(isolated_home):
    telemetry.enable()
    telemetry.record("pack", "core")
    telemetry.clear()
    assert telemetry.summary()["counters"] == {}


# ── robustness ───────────────────────────────────────────────────────────────────

def test_record_never_raises_on_bad_state(isolated_home):
    telemetry.enable()
    # Corrupt the data file — record must swallow the error, not propagate it.
    (isolated_home / "telemetry.json").write_text("{ not json", encoding="utf-8")
    telemetry.record("pack", "core")   # must not raise


def test_no_network_import():
    # Local-first guarantee: the module must not import any networking library.
    import inspect
    src = inspect.getsource(telemetry)
    for banned in ("import requests", "import urllib", "import http", "socket", "httpx"):
        assert banned not in src, f"telemetry must not use {banned}"
