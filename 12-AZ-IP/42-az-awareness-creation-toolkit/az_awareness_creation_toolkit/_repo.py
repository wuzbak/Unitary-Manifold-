# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Repo-path helper plus the sibling Product 19 and Product 39 package
paths, which this toolkit's dashboard module imports directly to reuse
their already-tested health/verdict logic rather than reimplementing it.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PRODUCT_19_ROOT = _REPO_ROOT / "12-AZ-IP" / "19-falsification-observatory"
_PRODUCT_39_ROOT = _REPO_ROOT / "12-AZ-IP" / "39-az-research-debt-tracker"


def ensure_repo_on_path() -> Path:
    root_str = str(_REPO_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    for product_root in (_PRODUCT_19_ROOT, _PRODUCT_39_ROOT):
        product_str = str(product_root)
        if product_str not in sys.path:
            sys.path.insert(0, product_str)
    return _REPO_ROOT


def repo_root() -> Path:
    return _REPO_ROOT
