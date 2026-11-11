#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""UOS Kernel — loopback workbench launcher: ``python run.py --port 8005``."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "lib"))

from library_console import serve

if __name__ == "__main__":
    raise SystemExit(serve("uos_kernel", "UOS Kernel", ROOT))
