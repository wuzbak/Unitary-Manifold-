# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for Pillar 108 — PMNS geometric see-saw closure."""

from __future__ import annotations

import numpy as np
import pytest

from src.core.pmns_seesaw_geometric import (
    N_W,
    K_CS,
    PI_KR,
    V_EW,
    PDG_PMNS_THETA12,
    PDG_PMNS_THETA13,
    PDG_PMNS_THETA23,
    DEFAULT_C_L,
    DEFAULT_C_NU_R,
    DEFAULT_PHASES,
    M_R0_GEV,
    rs_wavefunction_ir,
    majorana_mass_matrix_from_scherk_schwarz,
    dirac_mass_matrix_from_rs,
    seesaw_light_neutrino_matrix,
    pmns_from_seesaw_geometric,
    pillar108_report,
)


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert PI_KR == 37.0
    assert V_EW > 0.0


def test_rs_wavefunction_ir_positive():
    for c in (0.4, 0.5, 0.7, 0.9):
        assert rs_wavefunction_ir(c) >= 0.0


def test_rs_wavefunction_ir_half_special_case():
    expected = 1.0 / np.sqrt(2.0 * PI_KR)
    assert abs(rs_wavefunction_ir(0.5) - expected) < 1e-12


def test_majorana_matrix_shape():
    m_r = majorana_mass_matrix_from_scherk_schwarz()
    assert m_r.shape == (3, 3)


def test_majorana_matrix_symmetric():
    m_r = majorana_mass_matrix_from_scherk_schwarz()
    assert np.allclose(m_r, m_r.T, atol=1e-12)


def test_majorana_matrix_invalid_phase_length_raises():
    with pytest.raises(ValueError):
        majorana_mass_matrix_from_scherk_schwarz(phases=(0.0, 1.0))


def test_majorana_matrix_positive_scale_raises_for_negative():
    with pytest.raises(ValueError):
        majorana_mass_matrix_from_scherk_schwarz(m_r0_gev=-1.0)


def test_dirac_matrix_shape():
    m_d = dirac_mass_matrix_from_rs()
    assert m_d.shape == (3, 3)


def test_dirac_matrix_finite():
    m_d = dirac_mass_matrix_from_rs()
    assert np.all(np.isfinite(m_d))


def test_dirac_matrix_nontrivial_entries():
    m_d = dirac_mass_matrix_from_rs()
    assert np.any(np.abs(m_d) > 0.0)


def test_dirac_invalid_vector_lengths_raise():
    with pytest.raises(ValueError):
        dirac_mass_matrix_from_rs(c_l=(0.8, 0.7))
    with pytest.raises(ValueError):
        dirac_mass_matrix_from_rs(c_nu_r=(0.8, 0.7))
    with pytest.raises(ValueError):
        dirac_mass_matrix_from_rs(phases=(0.0, 1.0))


def test_seesaw_light_matrix_shape():
    m_d = dirac_mass_matrix_from_rs()
    m_r = majorana_mass_matrix_from_scherk_schwarz()
    m_nu = seesaw_light_neutrino_matrix(m_d, m_r)
    assert m_nu.shape == (3, 3)


def test_seesaw_light_matrix_invalid_shape_raises():
    with pytest.raises(ValueError):
        seesaw_light_neutrino_matrix(np.eye(2), np.eye(3))


def test_pmns_result_keys():
    result = pmns_from_seesaw_geometric()
    for key in (
        "U_pmns",
        "theta_12_deg",
        "theta_13_deg",
        "theta_23_deg",
        "light_masses_ev",
        "sum_mnu_ev",
    ):
        assert key in result


def test_pmns_unitary_like_columns():
    result = pmns_from_seesaw_geometric()
    u = result["U_pmns"]
    ident = u.conj().T @ u
    assert np.allclose(ident, np.eye(3), atol=1e-8)


def test_pmns_angles_nonnegative():
    result = pmns_from_seesaw_geometric()
    assert result["theta_12_deg"] >= 0.0
    assert result["theta_13_deg"] >= 0.0
    assert result["theta_23_deg"] >= 0.0


def test_pmns_large_angles_emerge():
    """Ensure large-angle (non-identity) PMNS structure emerges in the seesaw lane."""
    result = pmns_from_seesaw_geometric()
    assert result["theta_12_deg"] > 10.0
    assert result["theta_23_deg"] > 10.0


def test_pmns_residuals_reasonable_scale():
    result = pmns_from_seesaw_geometric()
    assert result["theta12_residual_abs_deg"] < 25.0
    assert result["theta13_residual_abs_deg"] < 15.0
    assert result["theta23_residual_abs_deg"] < 25.0


def test_mass_spectrum_nonnegative_and_sorted_by_construction():
    result = pmns_from_seesaw_geometric()
    masses = result["light_masses_ev"]
    assert np.all(masses >= 0.0)
    assert np.all(np.diff(masses) >= -1e-12)


def test_sum_mnu_planck_safe_order():
    result = pmns_from_seesaw_geometric()
    assert result["sum_mnu_ev"] < 0.20


def test_custom_inputs_still_run():
    result = pmns_from_seesaw_geometric(
        c_l=(0.81, 0.71, 0.61),
        c_nu_r=(0.85, 0.80, 0.75),
        phases=(0.0, 1.2, 2.4),
        m_r0_gev=8.0e13,
    )
    assert np.all(np.isfinite(result["light_masses_ev"]))


def test_report_shape():
    report = pillar108_report()
    for key in ("pillar", "module", "status", "epistemic_label", "residual_unknowns"):
        assert key in report


def test_report_semantics():
    report = pillar108_report()
    assert report["pillar"] == 108
    assert report["module"] == "pmns_seesaw_geometric"
    assert "SUBSTANTIALLY_CLOSED" in report["status"]
    assert len(report["residual_unknowns"]) >= 2


def test_defaults_are_length_three():
    assert len(DEFAULT_C_L) == 3
    assert len(DEFAULT_C_NU_R) == 3
    assert len(DEFAULT_PHASES) == 3
    assert M_R0_GEV > 0


def test_pdg_constants_positive():
    assert PDG_PMNS_THETA12 > 0.0
    assert PDG_PMNS_THETA13 > 0.0
    assert PDG_PMNS_THETA23 > 0.0
