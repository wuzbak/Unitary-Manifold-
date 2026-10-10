# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Shared helper that locates the Unitary Manifold repository root and makes
`src.cold_fusion.*` / `src.physics.*` importable from this standalone product
without requiring the product to be installed as part of the monorepo package.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]


def ensure_repo_on_path() -> Path:
    """Insert the monorepo root onto ``sys.path`` (idempotent) and return it."""
    root_str = str(_REPO_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return _REPO_ROOT
