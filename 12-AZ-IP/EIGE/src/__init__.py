# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Expose ``12-AZ-IP/03-eige/src`` as ``EIGE.src`` for legacy tests."""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[2] / "03-eige" / "src")]
