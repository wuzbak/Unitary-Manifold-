# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1012 — 10D branch canonicality lift."""

from src.core.pillar1012_tend_branch_canonicality_lift import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    branch_canonicality_lift_report,
    branch_projection_table,
)


def test_identity_constants():
    assert PILLAR_NUMBER == 1012
    assert PILLAR_GATE == "TEN_D_BRANCH_CANONICALITY_LIFT"
    assert PILLAR_STATUS == "TEN_D_BRANCH_CANONICALITY_LIFT_COMPLETE"


def test_projection_table_pairs_and_flux_counts():
    rows = branch_projection_table()
    assert rows[0]["pair"] == (5, 7)
    assert rows[0]["k_cs"] == 74
    assert rows[0]["n_flux"] == 37
    assert rows[1]["pair"] == (5, 6)
    assert rows[1]["k_cs"] == 61
    assert rows[1]["n_flux"] == 30


def test_projection_pass_fail_pattern():
    rows = branch_projection_table()
    canonical = rows[0]
    shadow = rows[1]
    assert canonical["z2_odd_boundary_pass"] is True
    assert canonical["survives_uv_selection"] is True
    assert canonical["status"] == "PRESERVED_IN_10D_SELECTION_CHAIN"
    assert shadow["z2_odd_boundary_pass"] is False
    assert shadow["survives_uv_selection"] is False
    assert shadow["status"] == "SUPPRESSED_IN_10D_SELECTION_CHAIN"


def test_lift_report_valid():
    report = branch_canonicality_lift_report()
    assert report["selection_bridge"]["selected_n_w"] == 5
    assert report["birefringence_discriminator"]["gap_deg"] > 0.05
    assert report["valid"] is True
