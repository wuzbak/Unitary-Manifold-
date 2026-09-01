# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Path setup for EIGE tests when run from the repository root."""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_ROOT_STR = str(PRODUCT_ROOT)

if PRODUCT_ROOT_STR in sys.path:
    sys.path.remove(PRODUCT_ROOT_STR)
sys.path.insert(0, PRODUCT_ROOT_STR)
