# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 627 — F-theory Rung 10 certificate."""
import pytest
from src.core.pillar627_ftheory_rung10_certificate import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    RUNG_10_STATUS,
    GAP_B_STATUS,
    ALL_BLOCKING_RESIDUALS_RESOLVED,
    rung10_certificate,
    gap_b_advance,
    pillar_report,
)

STRING_CHECKS = [
    ("PILLAR_STATUS", PILLAR_STATUS, "FTHEORY_RUNG10_COMPLETE_AT_REFERENCE_CY4_ADJACENT"),
    ("RUNG_10_STATUS", RUNG_10_STATUS, "RUNG_10_COMPLETE_AT_REFERENCE_CY4"),
    ("GAP_B_STATUS", GAP_B_STATUS, "PROVED_WITH_GLOBAL_SECTIONS_AT_REFERENCE_CY4"),
]


@pytest.mark.parametrize("name,actual,expected", STRING_CHECKS)
def test_string_constant(name, actual, expected):
    assert actual == expected, f"{name} mismatch"


def test_pillar_number():
    assert PILLAR_NUMBER == 627


def test_all_blocking_residuals_resolved():
    assert ALL_BLOCKING_RESIDUALS_RESOLVED is True


def test_rung10_certificate_all_resolved():
    cert = rung10_certificate()
    residuals = cert["blocking_residuals_from_rung9"]
    for key, val in residuals.items():
        assert val["resolved"] is True, f"{key} not resolved"
    assert cert["all_blocking_residuals_resolved"] is True


def test_rung10_certificate_structure():
    cert = rung10_certificate()
    assert cert["rung"] == 10
    assert "honest_scope" in cert
    assert "reference_level" in cert


def test_gap_b_advance_structure():
    adv = gap_b_advance()
    assert adv["status_before"] == "PROVED_AT_REFERENCE_CY4"
    assert adv["status_after"] == GAP_B_STATUS
    assert adv["toe_score_change"] == 0.0
    assert adv["c_l_min"] == pytest.approx(0.917, rel=1e-6)


def test_pillar_report_structure():
    rpt = pillar_report()
    assert rpt["pillar"] == 627
    assert rpt["adjacent_track"] is True
    assert rpt["toe_score_delta"] == 0.0
    assert rpt["hardgate_score_delta"] == 0.0
    assert "rung10_certificate" in rpt
    assert "gap_b_advance" in rpt
