# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 628 — F-theory DBP Rungs 1-10 combined certificate."""
import pytest
from src.core.pillar628_ftheory_dbp_rungs_1_10_combined import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RUNGS_COMPLETED,
    RUNGS_TOTAL,
    COMBINED_STATUS,
    CL_MIN,
    K_CS,
    N_D3_TADPOLE,
    combined_certificate,
    rung_ladder_summary,
    five_d_seed_consistency,
    pillar_report,
)

NUMERIC_CHECKS = [
    ("PILLAR_NUMBER", PILLAR_NUMBER, 628),
    ("RUNGS_COMPLETED", RUNGS_COMPLETED, 10),
    ("RUNGS_TOTAL", RUNGS_TOTAL, 12),
    ("CL_MIN", CL_MIN, 0.917),
    ("K_CS", K_CS, 74),
    ("N_D3_TADPOLE", N_D3_TADPOLE, 75_840),
]

STRING_CHECKS = [
    ("PILLAR_STATUS", PILLAR_STATUS, "FTHEORY_DBP_RUNGS_1_10_COMBINED_CERTIFICATE_ADJACENT"),
    ("COMBINED_STATUS", COMBINED_STATUS, "RUNGS_1_10_COMPLETE_AT_REFERENCE_CY4"),
]


@pytest.mark.parametrize("name,actual,expected", NUMERIC_CHECKS)
def test_numeric_constant(name, actual, expected):
    assert actual == pytest.approx(expected, rel=1e-10), f"{name} mismatch"


@pytest.mark.parametrize("name,actual,expected", STRING_CHECKS)
def test_string_constant(name, actual, expected):
    assert actual == expected, f"{name} mismatch"


def test_not_fully_closed():
    assert RUNGS_COMPLETED < RUNGS_TOTAL


def test_fraction_complete():
    cert = combined_certificate()
    assert cert["fraction_complete"] == pytest.approx(10 / 12, rel=1e-10)
    assert cert["full_dbp_closure"] is False


def test_combined_certificate_structure():
    cert = combined_certificate()
    assert cert["rungs_completed"] == 10
    assert "key_results" in cert
    assert "braid_topological_invariant" in cert["key_results"]
    assert "d3_tadpole" in cert["key_results"]


def test_rung_ladder_summary():
    summary = rung_ladder_summary()
    assert summary["completed"] == RUNGS_COMPLETED
    assert summary["remaining"] == RUNGS_TOTAL - RUNGS_COMPLETED
    assert summary["full_closure"] is False
    assert len(summary["remaining_open"]) == 2


def test_five_d_seed_consistency():
    result = five_d_seed_consistency()
    assert result["five_d_metric_preserved"] is True
    assert result["k_cs"] == 74
    assert result["kill_switch_pass"] is True
    assert len(result["kill_switch_checks"]) >= 3


def test_pillar_report_structure():
    rpt = pillar_report()
    assert rpt["pillar"] == 628
    assert rpt["adjacent_track"] is True
    assert rpt["toe_score_delta"] == 0.0
    assert rpt["hardgate_score_delta"] == 0.0
    assert "combined_certificate" in rpt
    assert "rung_ladder_summary" in rpt
    assert "five_d_seed_consistency" in rpt
