# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Repo-path helper plus the sibling Product 19 (Falsification Observatory)
package path, which this pipeline's fact-check layer imports directly.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PRODUCT_19_ROOT = _REPO_ROOT / "12-AZ-IP" / "19-falsification-observatory"


def ensure_repo_on_path() -> Path:
    root_str = str(_REPO_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    product_19_str = str(_PRODUCT_19_ROOT)
    if product_19_str not in sys.path:
        sys.path.insert(0, product_19_str)
    return _REPO_ROOT
