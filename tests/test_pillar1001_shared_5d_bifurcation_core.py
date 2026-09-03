# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1001 — shared 5D bifurcation core."""

from __future__ import annotations

from src.core.pillar1001_shared_5d_bifurcation_core import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    shared_5d_bifurcation_core,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1001
    assert PILLAR_GATE == "SHARED_5D_BIFURCATION_CORE"
    assert PILLAR_STATUS == "SHARED_5D_BIFURCATION_CORE_COMPLETE"
    assert PILLAR_VALID is True


def test_shared_core_locks_five_six_seven() -> None:
    report = shared_5d_bifurcation_core()
    assert report["shared_core"]["n_w"] == 5
    assert report["shared_core"]["parent_integer"] == 6
    assert report["shared_core"]["branch_second_coordinates"] == [6, 7]


def test_all_consistency_gates_pass() -> None:
    report = shared_5d_bifurcation_core()
    assert report["valid"] is True
    assert all(report["non_negotiable_consistency_gates"].values())
