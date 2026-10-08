# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Shared import paths for AXIOM Journalist tests."""
from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PRODUCT_ROOT / 'app'
for import_root in (str(APP_ROOT), str(PRODUCT_ROOT)):
    if import_root in sys.path:
        sys.path.remove(import_root)
sys.path[:0] = [str(APP_ROOT), str(PRODUCT_ROOT)]
