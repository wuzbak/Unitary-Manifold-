# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/architecture_limit_tier5_package.py."""
from __future__ import annotations

from src.core.architecture_limit_tier5_package import tier5_architecture_package


def test_tier5_package_structure():
    pkg = tier5_architecture_package()
    assert pkg["package"]
    assert set(pkg["parameters"].keys()) == {"P27", "P28"}
    assert pkg["all_gates_pass"] is True


def test_tier5_no_promotion_no_inflation():
    pkg = tier5_architecture_package()
    assert pkg["parameters"]["P27"]["status_decision"] == "no_promotion_claimed"
    assert pkg["parameters"]["P28"]["status_decision"] == "no_promotion_claimed"
    assert pkg["toe_score_delta"] == 0.0
