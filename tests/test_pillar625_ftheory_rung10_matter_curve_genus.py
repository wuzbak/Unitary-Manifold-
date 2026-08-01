# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 625 — F-theory Rung 10 matter-curve genus CY4."""
import pytest
from src.core.pillar625_ftheory_rung10_matter_curve_genus_cy4 import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    K_CS,
    N_SHEETS,
    DEG_L1,
    G_GENERIC_B5,
    G_KK_LIMIT,
    BLOCKING_RESIDUAL_RESOLVED,
    MATTER_CURVE_GENUS_STATUS,
    matter_curve_genus,
    adjunction_formula,
    genus_resolution_certificate,
    pillar_report,
)

NUMERIC_CHECKS = [
    ("PILLAR_NUMBER", PILLAR_NUMBER, 625),
    ("K_CS", K_CS, 74),
    ("G_GENERIC_B5", G_GENERIC_B5, 38),
    ("G_KK_LIMIT", G_KK_LIMIT, 0),
]

STRING_CHECKS = [
    ("PILLAR_STATUS", PILLAR_STATUS, "FTHEORY_RUNG10_MATTER_CURVE_GENUS_CY4_ADJACENT"),
    ("MATTER_CURVE_GENUS_STATUS", MATTER_CURVE_GENUS_STATUS, "GENUS_0_AT_KK_LIMIT_PROVED"),
]


@pytest.mark.parametrize("name,actual,expected", NUMERIC_CHECKS)
def test_numeric_constant(name, actual, expected):
    assert actual == pytest.approx(expected, rel=1e-10), f"{name} mismatch"


@pytest.mark.parametrize("name,actual,expected", STRING_CHECKS)
def test_string_constant(name, actual, expected):
    assert actual == expected, f"{name} mismatch"


def test_blocking_residual_resolved():
    assert BLOCKING_RESIDUAL_RESOLVED is True


def test_kk_limit_genus_zero():
    assert G_KK_LIMIT == 0


def test_generic_genus_positive():
    assert G_GENERIC_B5 > 0


def test_matter_curve_genus_structure():
    result = matter_curve_genus()
    assert isinstance(result, dict)
    assert result["g_generic_b5"] == G_GENERIC_B5
    assert result["g_kk_limit"] == G_KK_LIMIT


def test_adjunction_formula_structure():
    result = adjunction_formula()
    assert isinstance(result, dict)
    assert result["g_generic_b5"] == G_GENERIC_B5
    assert result["g_kk_limit"] == G_KK_LIMIT
    assert "formula" in result


def test_genus_resolution_certificate():
    cert = genus_resolution_certificate()
    assert cert["blocking_residual_resolved"] is True
    assert cert["g_kk_limit"] == 0
    assert "honest_scope" in cert


def test_pillar_report_structure():
    rpt = pillar_report()
    assert rpt["pillar"] == 625
    assert rpt["adjacent_track"] is True
    assert rpt["toe_score_delta"] == 0.0
    assert rpt["hardgate_score_delta"] == 0.0
    assert "matter_curve_genus" in rpt
    assert "adjunction_formula" in rpt
    assert "genus_resolution_certificate" in rpt
