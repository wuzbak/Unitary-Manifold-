# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 975 — G1 CMB A_s Lower Bound Sharpening."""

import math
import pytest

from src.core.pillar975_cmb_as_floor_sharpening import (
    PILLAR_STATUS,
    PILLAR_VALID,
    K_CS,
    N_W,
    C_S,
    S_WARP_LOW,
    S_WARP_HIGH,
    S_WARP_CENTRAL,
    CMB_S4_L_BINS_OLD,
    CMB_S4_L_BINS_NEW,
    CMB_S4_SIGMA_REL_OLD,
    CMB_S4_SIGMA_REL_NEW,
    CMB_AS_GAP,
    g1_floor_bounds,
    cmb_s4_updated_falsification_bins,
    g1_lower_bound_improvement,
    cmb_as_floor_certificate,
    fallibility_update,
    pillar975_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "CMB_AS_LOWER_BOUND_SHARPENED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_basic_constants():
    assert K_CS == 74
    assert N_W == 5
    assert abs(C_S - 12.0 / 37.0) < 1e-12


def test_s_warp_bounds_values():
    assert S_WARP_LOW == 4.0
    assert S_WARP_HIGH == 7.0


def test_s_warp_central_matches_rounding():
    assert abs(S_WARP_CENTRAL - 5.292) < 1e-12


def test_s_warp_central_close_to_geometric_mean():
    assert abs(S_WARP_CENTRAL - math.sqrt(28.0)) < 1e-3


def test_gap_value():
    assert abs(CMB_AS_GAP - 0.336) < 1e-12


def test_g1_floor_bounds_structure():
    result = g1_floor_bounds()
    assert result["S_warp_low"] == 4.0
    assert result["S_warp_high"] == 7.0
    assert result["central_in_interval"] is True


def test_g1_floor_width():
    result = g1_floor_bounds()
    assert result["interval_width"] == 3.0


def test_old_bins_constant():
    assert CMB_S4_L_BINS_OLD == [[200, 800], [800, 2000], [2000, 5000]]


def test_new_bins_constant():
    assert CMB_S4_L_BINS_NEW == [[200, 500], [500, 1500], [1500, 3000]]


def test_updated_bins_function():
    result = cmb_s4_updated_falsification_bins()
    assert result["old_l_bins"] == CMB_S4_L_BINS_OLD
    assert result["new_l_bins"] == CMB_S4_L_BINS_NEW
    assert result["shape_characterized_analytically"] is True


def test_new_bins_are_tighter():
    result = cmb_s4_updated_falsification_bins()
    new_spans = [b[1] - b[0] for b in result["new_l_bins"]]
    old_spans = [b[1] - b[0] for b in result["old_l_bins"]]
    assert max(new_spans) < max(old_spans)


def test_precision_constants():
    assert CMB_S4_SIGMA_REL_OLD == 0.02
    assert CMB_S4_SIGMA_REL_NEW == 0.008
    assert CMB_S4_SIGMA_REL_NEW < CMB_S4_SIGMA_REL_OLD


def test_improvement_factor():
    result = g1_lower_bound_improvement()
    assert result["old_precision"] == 0.02
    assert result["new_precision"] == 0.008
    assert abs(result["improvement_factor"] - 2.5) < 1e-12


def test_certificate_is_type_b_and_not_closed():
    cert = cmb_as_floor_certificate()
    assert cert["gap_label"] == "G1"
    assert cert["type_b_classification"] == "TYPE_B_STRUCTURAL_FLOOR"
    assert cert["closure_claimed"] is False
    assert cert["architecture_limit_only"] is True


def test_certificate_tracks_gap():
    cert = cmb_as_floor_certificate()
    assert abs(cert["residual_gap_fraction"] - CMB_AS_GAP) < 1e-12


def test_fallibility_update():
    fb = fallibility_update()
    assert fb["pillar"] == 975
    assert "0.8%" in fb["new_status"]
    assert "33.6%" in fb["residual_gap"]


def test_summary_structure():
    summary = pillar975_summary()
    assert summary["pillar"] == 975
    assert summary["valid"] is True
    assert len(summary["derivation_chain"]) >= 5

