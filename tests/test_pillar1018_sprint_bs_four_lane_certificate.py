# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1018 — Sprint BS four-lane certificate."""

from src.core.pillar1018_sprint_bs_four_lane_certificate import (
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SPRINT_NAME,
    SPRINT_PILLARS,
    VERSION,
    pillar1018_summary,
    sprint_bs_lane_table,
    sprint_bs_master_report,
)


def test_identity():
    assert PILLAR_NUMBER == 1018
    assert PILLAR_STATUS == "SPRINT_BS_FOUR_LANE_CERTIFICATE_COMPLETE"


def test_metadata():
    assert SPRINT_NAME == "BS"
    assert VERSION == "v34.9"
    assert SPRINT_PILLARS == [1014, 1015, 1016, 1017, 1018]
    assert NEXT_PILLAR_SLOT == 1019


def test_lean4_chain():
    assert LEAN4_END - LEAN4_START == LEAN4_DELTA
    assert LEAN4_DELTA == 0


def test_lane_table_shape():
    lanes = sprint_bs_lane_table()
    assert len(lanes) == 4
    assert {row["lane"] for row in lanes} == {"8D", "9D", "11D", "12D"}


def test_report_and_summary():
    report = sprint_bs_master_report()
    assert report["all_valid"] is True
    assert report["next_pillar_slot"] == 1019
    assert "DESI_DR3_MONITORING (~2027)" in report["remaining_open"]
    assert pillar1018_summary()["version"] == "v34.9"
