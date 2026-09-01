# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Expose the existing top-level ``src`` package as ``EIGE.src``."""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[2] / "src")]
