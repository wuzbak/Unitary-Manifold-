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
    assert PILLAR_STATUS == "CIRCLE_MAXWELL_CONDITIONAL_ORBIFOLD_PHOTON_UNSUPPORTED"


def test_metric_decomposition_fields_present():
    result = metric_kk_decomposition()
    assert result["status"] == "DERIVED"
    assert result["fields"]["A_mu"].startswith("KK U(1)")
    assert "G_munu" in result["value"]
    assert "G_mu5" in result["value"]
    assert "G_55" in result["value"]


def test_metric_vector_constant_mode_is_projected_out_not_massless():
    result = photon_zero_mode_bc()
    assert result["status"] == "PROJECTED_OUT"
    assert result["value"] is None
    assert result["photon_mass_zero_gev"] is None
    assert result["zero_mode_survives"] is False
    assert result["boundary_conditions"] == ["f0(0)=0", "f0(pi R)=0"]
    assert result["observed_photon_identified"] is False


def test_independent_even_bulk_u1_retains_conditional_neumann_solution():
    result = photon_zero_mode_bc(field_origin="independent_bulk_u1")
    assert result["status"] == "CONDITIONAL"
    assert result["field_origin"] == "independent_bulk_u1"
    assert result["photon_mass_zero_gev"] == 0.0
    assert result["zero_mode_profile"] == "constant"
    assert result["c2_forced"] == 0.0
    assert result["boundary_conditions"] == ["f0'(0)=0", "f0'(pi R)=0"]
    assert result["zero_mode_survives"] is True
    assert result["observed_photon_identified"] is False


def test_field_origin_must_be_explicitly_supported():
    with pytest.raises(ValueError, match="field_origin"):
        photon_zero_mode_bc(field_origin="photon")


def test_zero_mode_bc_requires_positive_pi_kr():
    with pytest.raises(ValueError):
        photon_zero_mode_bc(pi_kr=0.0)


def test_z2_parity_assignments():
    result = photon_z2_parity()
    assert result["a_mu_parity"] == -1
    assert result["g_mu5_parity"] == -1
    assert result["g_55_parity"] == 1
    assert result["survives_orbifold"] is False
    assert result["a_mu_parity"] * result["g_55_parity"] == result["g_mu5_parity"]


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


def test_assigned_coupling_obeys_its_formula_not_an_em_prediction():
    result = kk_reduction_gauge_coupling()
    alpha = result["alpha_em_geometric"]
    assert alpha == pytest.approx(result["g4_effective_sq"] / (4 * math.pi))
    assert result["inverse_alpha_em"] == pytest.approx(1 / alpha)
    assert result["observed_photon_identified"] is False
    assert result["coupling_derivation_complete"] is False
    assert "independent bulk U(1)" in result["model_scope"]


def test_custom_g5_sq_changes_coupling():
    default = kk_reduction_gauge_coupling()["g4_effective_sq"]
    modified = kk_reduction_gauge_coupling(g5_sq=2.0 * K_CS / M_PL_GEV)["g4_effective_sq"]
    assert modified == pytest.approx(2.0 * default, rel=1e-12)


def test_negative_g5_raises():
    with pytest.raises(ValueError):
        kk_reduction_gauge_coupling(g5_sq=-1.0)


def test_maxwell_equations_content():
    result = maxwell_equations_4d()
    assert result["status"] == "CONDITIONAL"
    assert result["metric_orbifold_zero_mode"] is False
    assert result["mass_term"] == 0.0
    assert "partial_nu F^{mu nu}" in result["equation_of_motion"]
    assert "F_{mu nu}" in result["field_strength"]


def test_report_contains_sections():
    report = maxwell_kk_reduction_report()
    assert report["status"] == PILLAR_STATUS
    for key in ("decomposition", "boundary_value_problem", "parity", "gauge_coupling", "maxwell_equations"):
        assert key in report


def test_report_does_not_promote_conditional_coupling_to_observed_photon():
    report = maxwell_kk_reduction_report()
    assert report["gauge_coupling"]["alpha_em_geometric"] > 0
    assert report["value"]["alpha_em_geometric"] is None
    assert report["value"]["photon_mass_zero_gev"] is None
    assert report["observed_photon_identified"] is False
    assert report["closure_earned"] is False


@pytest.mark.parametrize("pi_kr", [1.0, 10.0, 37.0, 50.0])
def test_varying_warp_parameter_cannot_reverse_orbifold_projection(pi_kr):
    metric = photon_zero_mode_bc(pi_kr)
    independent = photon_zero_mode_bc(pi_kr, field_origin="independent_bulk_u1")
    assert metric["zero_mode_survives"] is False
    assert independent["zero_mode_survives"] is True


@pytest.mark.parametrize("pi_kr", [float("nan"), float("inf")])
def test_nonfinite_geometry_is_rejected(pi_kr):
    with pytest.raises(ValueError, match="finite"):
        photon_zero_mode_bc(pi_kr)
