"""Enable ``python -m eeik <command>``."""

from __future__ import annotations

import sys

from eeik.cli import main

if __name__ == "__main__":
    sys.exit(main())
