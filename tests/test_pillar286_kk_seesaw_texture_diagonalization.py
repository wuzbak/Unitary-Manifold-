# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 286 — KK Seesaw Texture Diagonalization."""
import math
import pytest
from src.core.pillar286_kk_seesaw_texture_diagonalization import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    DM2_31_PDG_EV2,
    DM2_31_UM_BASELINE_EV2,
    M_KK_GEV,
    V_HIGGS_GEV,
    Y_TAU,
    Y_TOP,
    N_C,
    K_CS,
    PI_KR,
    N_W,
    PMNS_UPPER_BOUND,
    separation_guard,
    geometric_yukawa_ratio,
    orbifold_texture_factor,
    geometric_p_r_estimate,
    seesaw_mass_correction_factor,
    tightened_dm31_from_texture,
    p17_upgrade_assessment,
    pillar286_report,
)


# ---------------------------------------------------------------------------
# Identity and separation guard
# ---------------------------------------------------------------------------

def test_pillar_number():
    assert PILLAR_NUMBER == 286


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard_keys():
    g = separation_guard()
    assert g["pillar"] == 286
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False
    assert g["closes_seesaw_texture_gap"] is True


def test_separation_guard_adjacency():
    g = separation_guard()
    assert g["adjacency_label"] == "NON_HARDGATE_ADJACENT"


# ---------------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------------

def test_pmns_upper_bound_reasonable():
    # sin²(48.3°) × cos²(8.57°) ≈ 0.547
    assert 0.50 < PMNS_UPPER_BOUND < 0.60


def test_dm2_31_pdg_positive():
    assert DM2_31_PDG_EV2 > 0.0


def test_dm2_31_baseline_less_than_pdg():
    assert DM2_31_UM_BASELINE_EV2 < DM2_31_PDG_EV2


def test_yukawa_values_positive():
    assert Y_TAU > 0.0
    assert Y_TOP > 0.0
    assert Y_TAU < Y_TOP   # tau yukawa < top yukawa


def test_k_cs_value():
    assert K_CS == 74  # = 5² + 7²


def test_n_w_value():
    assert N_W == 5


# ---------------------------------------------------------------------------
# Geometric computation
# ---------------------------------------------------------------------------

def test_geometric_yukawa_ratio():
    ratio = geometric_yukawa_ratio()
    assert abs(ratio - Y_TAU / Y_TOP) < 1e-10
    assert 0.0 < ratio < 1.0


def test_orbifold_texture_factor_positive():
    f = orbifold_texture_factor()
    assert f > 0.0
    assert f < 1.0  # should be a suppression factor


def test_geometric_p_r_estimate_keys():
    est = geometric_p_r_estimate()
    for key in ("p_r_geom", "pmns_upper_bound", "in_pmns_window", "status"):
        assert key in est


def test_geometric_p_r_in_pmns_window():
    est = geometric_p_r_estimate()
    assert est["in_pmns_window"] is True


def test_geometric_p_r_positive():
    est = geometric_p_r_estimate()
    assert est["p_r_geom"] > 0.0


def test_geometric_p_r_below_pmns_bound():
    est = geometric_p_r_estimate()
    assert est["p_r_geom"] <= PMNS_UPPER_BOUND


def test_geometric_p_r_status_conditionally_closed():
    est = geometric_p_r_estimate()
    assert est["status"] == "SEESAW_TEXTURE_GAP_CLOSED_CONDITIONALLY"


# ---------------------------------------------------------------------------
# Seesaw correction and tightened prediction
# ---------------------------------------------------------------------------

def test_seesaw_mass_correction_zero_pr():
    assert seesaw_mass_correction_factor(0.0) == 0.0


def test_seesaw_mass_correction_positive():
    assert seesaw_mass_correction_factor(0.364) > 0.0


def test_seesaw_mass_correction_small():
    # (v/M_KK)² × p_R = (246.22/1000)² × 0.364 << 1
    c = seesaw_mass_correction_factor(0.364)
    assert c < 0.1


def test_seesaw_mass_correction_negative_raises():
    with pytest.raises(ValueError):
        seesaw_mass_correction_factor(-0.1)


def test_tightened_dm31_zero_pr():
    result = tightened_dm31_from_texture(0.0)
    assert abs(result["dm31_tightened_ev2"] - DM2_31_UM_BASELINE_EV2) < 1e-20


def test_tightened_dm31_residual_positive():
    result = tightened_dm31_from_texture(0.364)
    assert result["residual_pct"] >= 0.0


def test_tightened_dm31_residual_reasonable():
    result = tightened_dm31_from_texture(0.364)
    assert result["residual_pct"] < 5.0  # should be within 5%


def test_tightened_dm31_keys():
    result = tightened_dm31_from_texture(0.364)
    for key in ("p_r", "dm31_tightened_ev2", "residual_pct", "juno_verdict"):
        assert key in result


# ---------------------------------------------------------------------------
# P17 upgrade assessment
# ---------------------------------------------------------------------------

def test_p17_upgrade_assessment_keys():
    ua = p17_upgrade_assessment()
    for key in ("current_label", "upgrade_available", "upgrade_to", "p_r_geom", "residual_pct"):
        assert key in ua


def test_p17_current_label():
    ua = p17_upgrade_assessment()
    assert ua["current_label"] == "CONDITIONAL_DERIVATION"


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def test_pillar286_report_pillar_number():
    r = pillar286_report()
    assert r["pillar"] == 286


def test_pillar286_report_has_status():
    r = pillar286_report()
    assert "status" in r


def test_pillar286_report_adjacency():
    r = pillar286_report()
    assert r["adjacency_label"] == "NON_HARDGATE_ADJACENT"
