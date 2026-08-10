#!/usr/bin/env python3
"""EEIK opt-in telemetry — strictly opt-in, local-first, no network.

The engine can, *only when you turn it on*, keep local counts of which packs and generators you use, so
a maintainer of a shared EEIK fork can prioritise the catalog from real usage. Three non-negotiable
properties (ROADMAP §8):

- **Opt-in.** Off by default. Nothing is recorded until you run ``eeik telemetry --enable`` (or set
  ``EEIK_TELEMETRY=1``). ``record()`` is a hard no-op otherwise.
- **Local-first.** Counts live in a JSON file under ``~/.eeik/`` (override ``EEIK_TELEMETRY_DIR``). There
  is **no network code in this module** — nothing is ever sent anywhere. Inspect or delete it any time.
- **Non-identifying.** Only aggregate counters keyed by pack/generator name — no arguments, no manifest
  content, no paths, no timestamps beyond a coarse ``last_updated`` date.

CLI: ``eeik telemetry`` (status + summary), ``--enable`` / ``--disable`` / ``--clear`` / ``--json``.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_DIM = "\033[2m"
ANSI_RESET = "\033[0m"

_TRUTHY = {"1", "true", "yes", "on"}


def _dir() -> Path:
    return Path(os.environ.get("EEIK_TELEMETRY_DIR") or (Path.home() / ".eeik"))


def _data_file() -> Path:
    return _dir() / "telemetry.json"


def _optin_marker() -> Path:
    return _dir() / "telemetry-enabled"


def is_enabled() -> bool:
    """True only when telemetry was explicitly opted into (env flag or the opt-in marker file)."""
    if os.environ.get("EEIK_TELEMETRY", "").strip().lower() in _TRUTHY:
        return True
    try:
        return _optin_marker().exists()
    except OSError:
        return False


def enable() -> Path:
    """Persist opt-in (create the marker file). Returns the marker path."""
    d = _dir()
    d.mkdir(parents=True, exist_ok=True)
    marker = _optin_marker()
    marker.write_text("EEIK telemetry is opt-in and local-only. Delete this file to opt out.\n",
                      encoding="utf-8")
    return marker


def disable() -> None:
    """Remove opt-in. Existing local counts are left in place (use --clear to delete them)."""
    try:
        _optin_marker().unlink(missing_ok=True)
    except OSError:
        pass


def clear() -> None:
    """Delete all locally recorded counts."""
    try:
        _data_file().unlink(missing_ok=True)
    except OSError:
        pass


def _load() -> dict[str, Any]:
    try:
        return json.loads(_data_file().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def record(kind: str, name: str) -> None:
    """Increment the local counter for ``kind/name`` — a no-op unless telemetry is enabled.

    Never raises and never networks: a telemetry failure must never break an engine command.
    """
    if not is_enabled():
        return
    try:
        data = _load()
        counters = data.setdefault("counters", {})
        bucket = counters.setdefault(kind, {})
        bucket[name] = int(bucket.get(name, 0)) + 1
        data["last_updated"] = date.today().isoformat()
        d = _dir()
        d.mkdir(parents=True, exist_ok=True)
        _data_file().write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception:  # noqa: BLE001 - telemetry is best-effort; swallow everything
        pass


def summary() -> dict[str, Any]:
    """The current local state — enabled flag, file path, and counters (empty when never recorded)."""
    data = _load()
    return {
        "enabled": is_enabled(),
        "path": str(_data_file()),
        "last_updated": data.get("last_updated"),
        "counters": data.get("counters", {}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eeik telemetry",
                                     description="Opt-in, local-first usage telemetry (no network).")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--enable", action="store_true", help="Opt in (start recording locally)")
    g.add_argument("--disable", action="store_true", help="Opt out (stop recording; keeps existing data)")
    g.add_argument("--clear", action="store_true", help="Delete all locally recorded counts")
    parser.add_argument("--json", action="store_true", help="Emit the summary as JSON")
    args = parser.parse_args(argv)

    if args.enable:
        marker = enable()
        print(f"{ANSI_GREEN}✓ Telemetry enabled (local-only){ANSI_RESET}  {ANSI_DIM}{marker}{ANSI_RESET}")
        return 0
    if args.disable:
        disable()
        print(f"{ANSI_YELLOW}Telemetry disabled.{ANSI_RESET} Existing counts kept — run --clear to delete.")
        return 0
    if args.clear:
        clear()
        print("Local telemetry data cleared.")
        return 0

    info = summary()
    if args.json:
        print(json.dumps(info, indent=2, sort_keys=True))
        return 0

    state = f"{ANSI_GREEN}enabled{ANSI_RESET}" if info["enabled"] else f"{ANSI_DIM}disabled (opt-in){ANSI_RESET}"
    print(f"\n{ANSI_BOLD}EEIK Telemetry{ANSI_RESET}  ·  {state}")
    print(f"  {ANSI_DIM}local file:{ANSI_RESET} {info['path']}  {ANSI_DIM}(no network — inspect/delete any time){ANSI_RESET}")
    counters = info["counters"]
    if not counters:
        print(f"  {ANSI_DIM}no data recorded.{ANSI_RESET}")
        if not info["enabled"]:
            print(f"  {ANSI_DIM}enable with:{ANSI_RESET} eeik telemetry --enable   "
                  f"{ANSI_DIM}(or EEIK_TELEMETRY=1){ANSI_RESET}")
    else:
        for kind, bucket in sorted(counters.items()):
            print(f"\n  {ANSI_BOLD}{kind}{ANSI_RESET}")
            for name, count in sorted(bucket.items(), key=lambda kv: (-kv[1], kv[0])):
                print(f"    {count:>4}  {name}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
