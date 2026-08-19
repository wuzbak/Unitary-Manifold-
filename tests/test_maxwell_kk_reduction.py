# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
from __future__ import annotations

import math

import pytest

from src.core.maxwell_kk_reduction import (
    K_CS,
    M_PL_GEV,
    N_W,
    PI_K_R,
    PILLAR,
    PILLAR_STATUS,
    kk_reduction_gauge_coupling,
    maxwell_equations_4d,
    maxwell_kk_reduction_report,
    metric_kk_decomposition,
    photon_z2_parity,
    photon_zero_mode_bc,
)


def test_constants_match_context():
    assert N_W == 5
    assert K_CS == 74
    assert PI_K_R == pytest.approx(37.0)
    assert M_PL_GEV > 1e18


def test_pillar_metadata():
    assert PILLAR == 773
    assert PILLAR_STATUS == "MAXWELL_REDUCTION_DERIVED"


def test_metric_decomposition_fields_present():
    result = metric_kk_decomposition()
    assert result["status"] == "DERIVED"
    assert result["fields"]["A_mu"].startswith("KK U(1)")
    assert "G_munu" in result["value"]
    assert "G_mu5" in result["value"]
    assert "G_55" in result["value"]


def test_zero_mode_bc_is_massless():
    result = photon_zero_mode_bc()
    assert result["photon_mass_zero_gev"] == 0.0
    assert result["zero_mode_profile"] == "constant"
    assert result["c2_forced"] == 0.0


def test_zero_mode_bc_requires_positive_pi_kr():
    with pytest.raises(ValueError):
        photon_zero_mode_bc(pi_kr=0.0)


def test_z2_parity_assignments():
    result = photon_z2_parity()
    assert result["a_mu_parity"] == 1
    assert result["g_mu5_parity"] == -1
    assert result["survives_orbifold"] is True


def test_gauge_coupling_returns_dict():
    result = kk_reduction_gauge_coupling()
    assert result["status"] == "CONSTRAINED"
    assert result["epistemic_status"] == "CONSTRAINED"


def test_tree_level_g4_sq_is_order_unity():
    result = kk_reduction_gauge_coupling()
    assert 0.9 < result["g4_tree_sq"] < 1.1


def test_effective_g4_sq_is_smaller_after_warp_overlap():
    result = kk_reduction_gauge_coupling()
    assert result["g4_effective_sq"] < result["g4_tree_sq"]
    assert 0.09 < result["g4_effective_sq"] < 0.10


def test_alpha_em_is_near_inverse_137_scale():
    result = kk_reduction_gauge_coupling()
    alpha = result["alpha_em_geometric"]
    assert 0.006 < alpha < 0.009
    assert 120.0 < result["inverse_alpha_em"] < 160.0


def test_custom_g5_sq_changes_coupling():
    default = kk_reduction_gauge_coupling()["g4_effective_sq"]
    modified = kk_reduction_gauge_coupling(g5_sq=2.0 * K_CS / M_PL_GEV)["g4_effective_sq"]
    assert modified == pytest.approx(2.0 * default, rel=1e-12)


def test_negative_g5_raises():
    with pytest.raises(ValueError):
        kk_reduction_gauge_coupling(g5_sq=-1.0)


def test_maxwell_equations_content():
    result = maxwell_equations_4d()
    assert result["mass_term"] == 0.0
    assert "partial_nu F^{mu nu}" in result["equation_of_motion"]
    assert "F_{mu nu}" in result["field_strength"]


def test_report_contains_sections():
    report = maxwell_kk_reduction_report()
    assert report["status"] == PILLAR_STATUS
    for key in ("decomposition", "boundary_value_problem", "parity", "gauge_coupling", "maxwell_equations"):
        assert key in report


def test_report_alpha_is_consistent_with_subreport():
    report = maxwell_kk_reduction_report()
    alpha = report["gauge_coupling"]["alpha_em_geometric"]
    assert report["value"]["alpha_em_geometric"] == pytest.approx(alpha, rel=1e-12)
