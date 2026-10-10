# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]


def ensure_repo_on_path() -> Path:
    root_str = str(_REPO_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return _REPO_ROOT
