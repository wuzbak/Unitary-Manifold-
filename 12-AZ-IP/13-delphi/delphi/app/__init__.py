# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Compatibility package exposing the legacy DelPhi app modules."""
from __future__ import annotations

from pathlib import Path

_pkg_dir = Path(__file__).resolve().parent
_legacy_app_dir = _pkg_dir.parents[1] / 'app'
__path__ = [str(_pkg_dir), str(_legacy_app_dir)]
