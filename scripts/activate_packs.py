#!/usr/bin/env python3
"""Backward-compatible shim. The EEIK engine now lives in the `eeik` package;
this forwards to `eeik.packs`. Prefer `eeik` (console script) or `python -m eeik`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eeik.packs import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
