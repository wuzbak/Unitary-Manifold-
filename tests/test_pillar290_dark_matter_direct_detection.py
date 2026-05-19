# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 290 — Dark Matter Direct Detection Constraints."""
import math
import pytest
from src.core.pillar290_dark_matter_direct_detection import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    M_KK_GEV,
    M_N_GEV,
    N_W,
    K_CS,
    LZ_YEAR2_SIGMA_LIMIT_CM2,
    LZ_YEAR3_PROJECTED_LIMIT_CM2,
    separation_guard,
    kk_graviton_si_cross_section,
    lz_year2_exclusion_limit,
    consistency_verdict,
    lz_year3_projection,
    dm_detection_preregistration_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 290


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard_keys():
    g = separation_guard()
    assert g["pillar"] == 290
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False
    assert "experiments" in g


def test_separation_guard_experiments():
    g = separation_guard()
    assert "LZ" in g["experiments"]


def test_constants_physical():
    assert M_KK_GEV == 1.0e3
    assert M_N_GEV > 0.0
    assert N_W == 5
    assert K_CS == 74


def test_lz_year2_limit_value():
    assert abs(LZ_YEAR2_SIGMA_LIMIT_CM2 - 6.6e-48) < 1e-50


def test_kk_graviton_si_positive():
    sigma = kk_graviton_si_cross_section(1.0)
    assert sigma > 0.0


def test_kk_graviton_si_finite():
    sigma = kk_graviton_si_cross_section(1.0)
    assert math.isfinite(sigma)


def test_kk_graviton_si_below_lz():
    sigma = kk_graviton_si_cross_section(1.0)
    assert sigma < LZ_YEAR2_SIGMA_LIMIT_CM2


def test_kk_graviton_si_very_small():
    # Should be << 10^-48 cm²
    sigma = kk_graviton_si_cross_section(1.0)
    assert sigma < 1.0e-48


def test_kk_graviton_si_raises_non_positive():
    with pytest.raises(ValueError):
        kk_graviton_si_cross_section(0.0)


def test_kk_graviton_si_scales_with_mass():
    # Higher M_KK → smaller sigma
    sigma_1 = kk_graviton_si_cross_section(1.0)
    sigma_2 = kk_graviton_si_cross_section(2.0)
    assert sigma_2 < sigma_1


def test_lz_year2_exclusion_limit_keys():
    r = lz_year2_exclusion_limit()
    for key in ("sigma_limit_cm2", "m_chi_gev", "confidence_level", "reference"):
        assert key in r


def test_lz_year2_exclusion_confidence():
    r = lz_year2_exclusion_limit()
    assert "90%" in r["confidence_level"]


def test_consistency_verdict_consistent():
    v = consistency_verdict()
    assert v["verdict"] == "CONSISTENT_BELOW_LIMIT"


def test_consistency_verdict_margin_large():
    v = consistency_verdict()
    assert v["margin_factors"] > 1e5  # should be many orders of magnitude


def test_consistency_verdict_keys():
    v = consistency_verdict()
    for key in ("um_sigma_cm2", "lz_limit_cm2", "verdict", "margin_factors"):
        assert key in v


def test_lz_year3_projection_consistent():
    r = lz_year3_projection()
    assert "CONSISTENT" in r["verdict"]


def test_lz_year3_projection_keys():
    r = lz_year3_projection()
    for key in ("projected_limit_cm2", "um_sigma_cm2", "verdict", "note"):
        assert key in r


def test_dm_report_pillar():
    r = dm_detection_preregistration_report()
    assert r["pillar"] == 290


def test_dm_report_has_sections():
    r = dm_detection_preregistration_report()
    for key in ("kk_graviton_sigma_cm2", "lz_year2_limit", "consistency", "lz_year3"):
        assert key in r
