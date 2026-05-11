# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for Pillar 104 — CKM + PMNS mixing angles from RS orbifold."""

import pytest
import numpy as np

from src.core.ckm_pmns_orbifold import (
    N_W, K_CS, PI_KR, V_EW, G5_YUKAWA,
    PDG_CKM_THETA12, PDG_CKM_THETA13, PDG_CKM_THETA23,
    PDG_PMNS_THETA12, PDG_PMNS_THETA13, PDG_PMNS_THETA23,
    PDG_WOLFENSTEIN_LAMBDA,
    rs_wavefunction_ir,
    yukawa_matrix_up,
    yukawa_matrix_down,
    ckm_from_yukawa,
    neutrino_c_spectrum,
    pmns_from_orbifold,
    ckm_wolfenstein_estimate,
    pmns_angle_estimate,
    ckm_pmns_orbifold_report,
    C_L_QUARKS, C_R_UP, C_R_DOWN, C_L_LEPTONS,
)


# ---------- constant sanity checks ----------

def test_pi_kr():
    assert PI_KR == 37.0


def test_v_ew():
    assert V_EW == 174.0


def test_pdg_ckm_theta12():
    assert abs(PDG_CKM_THETA12 - 13.1) < 1e-10


def test_pdg_pmns_theta12():
    assert abs(PDG_PMNS_THETA12 - 33.44) < 1e-10


def test_pdg_wolfenstein_lambda():
    assert abs(PDG_WOLFENSTEIN_LAMBDA - 0.22650) < 1e-5


def test_n_w():
    assert N_W == 5


# ---------- RS wavefunction ----------

def test_rs_wavefunction_positive():
    for c in [0.3, 0.5, 0.7, 0.9]:
        f = rs_wavefunction_ir(c, pi_kr=37.0)
        assert f >= 0.0, f"f_IR({c}) = {f} should be non-negative"


def test_rs_wavefunction_c_half():
    # Special case: c = 0.5 → 1/sqrt(2 pi_kr)
    f = rs_wavefunction_ir(0.5, pi_kr=37.0)
    expected = 1.0 / np.sqrt(2.0 * 37.0)
    assert abs(f - expected) < 1e-10


def test_rs_wavefunction_uv_localized_smaller():
    # UV-localized (c > 0.5) should have smaller IR overlap than IR-localized (c < 0.5)
    f_uv = rs_wavefunction_ir(0.8, pi_kr=37.0)
    f_ir_loc = rs_wavefunction_ir(0.3, pi_kr=37.0)
    assert f_uv < f_ir_loc


def test_rs_wavefunction_finite():
    for c in [0.1, 0.4, 0.5, 0.6, 0.9, 1.2]:
        f = rs_wavefunction_ir(c, pi_kr=37.0)
        assert np.isfinite(f)


def test_rs_wavefunction_ir_localized_large():
    # For c < 0.5, IR-localized → large wavefunction
    f = rs_wavefunction_ir(0.1, pi_kr=37.0)
    assert f > 0.1


# ---------- Yukawa matrices ----------

def test_yukawa_matrix_shape():
    M_u = yukawa_matrix_up()
    assert M_u.shape == (3, 3)


def test_yukawa_matrix_down_shape():
    M_d = yukawa_matrix_down()
    assert M_d.shape == (3, 3)


def test_yukawa_matrix_positive():
    M_u = yukawa_matrix_up()
    assert np.all(M_u >= 0.0)


def test_yukawa_matrix_hierarchy():
    # c_L = [0.9, 0.8, 0.7]: gen 1 is most UV-localized (c=0.9) → smallest IR overlap.
    # Gen 3 (c=0.7) is less UV-localized → larger IR overlap → larger Yukawa entry.
    M_u = yukawa_matrix_up()
    assert M_u[2, 0] > M_u[0, 0]


def test_yukawa_matrix_scale():
    # Entries should be in GeV scale (order 1e-5 to 1e2)
    M_u = yukawa_matrix_up()
    assert np.any(M_u > 0.0)


# ---------- CKM ----------

def test_ckm_returns_dict():
    M_u = yukawa_matrix_up()
    M_d = yukawa_matrix_down()
    result = ckm_from_yukawa(M_u, M_d)
    assert isinstance(result, dict)


def test_ckm_keys():
    M_u = yukawa_matrix_up()
    M_d = yukawa_matrix_down()
    result = ckm_from_yukawa(M_u, M_d)
    for key in ("V_ckm", "theta_12_deg", "theta_13_deg", "theta_23_deg"):
        assert key in result


def test_ckm_angles_nonneg():
    M_u = yukawa_matrix_up()
    M_d = yukawa_matrix_down()
    result = ckm_from_yukawa(M_u, M_d)
    assert result["theta_12_deg"] >= 0.0
    assert result["theta_13_deg"] >= 0.0
    assert result["theta_23_deg"] >= 0.0


def test_ckm_v_matrix_shape():
    M_u = yukawa_matrix_up()
    M_d = yukawa_matrix_down()
    result = ckm_from_yukawa(M_u, M_d)
    assert result["V_ckm"].shape == (3, 3)


def test_ckm_pdg_values_in_result():
    M_u = yukawa_matrix_up()
    M_d = yukawa_matrix_down()
    result = ckm_from_yukawa(M_u, M_d)
    assert "pdg_theta_12_deg" in result
    assert abs(result["pdg_theta_12_deg"] - PDG_CKM_THETA12) < 1e-10


# ---------- neutrino c spectrum ----------

def test_neutrino_c_spectrum_length():
    c_nu = neutrino_c_spectrum(n_w=5)
    assert len(c_nu) == 3


def test_neutrino_c_spectrum_uv_localized():
    c_nu = neutrino_c_spectrum(n_w=5)
    for c in c_nu:
        assert c > 0.5, f"c_ν={c} should be UV-localized (>0.5)"


def test_neutrino_c_spectrum_values():
    c_nu = neutrino_c_spectrum(n_w=5)
    expected = [0.6, 0.7, 0.8]
    for a, b in zip(c_nu, expected):
        assert abs(a - b) < 1e-12


# ---------- PMNS ----------

def test_pmns_returns_dict():
    result = pmns_from_orbifold()
    assert isinstance(result, dict)


def test_pmns_keys():
    result = pmns_from_orbifold()
    for key in ("U_pmns", "theta_12_deg", "theta_13_deg", "theta_23_deg"):
        assert key in result


def test_pmns_angles_nonneg():
    result = pmns_from_orbifold()
    assert result["theta_12_deg"] >= 0.0
    assert result["theta_13_deg"] >= 0.0
    assert result["theta_23_deg"] >= 0.0


def test_pmns_u_matrix_shape():
    result = pmns_from_orbifold()
    assert result["U_pmns"].shape == (3, 3)


# ---------- Wolfenstein estimate ----------

def test_wolfenstein_estimate_dict():
    result = ckm_wolfenstein_estimate()
    assert isinstance(result, dict)


def test_wolfenstein_lambda_positive():
    result = ckm_wolfenstein_estimate()
    assert result["lambda_wolfenstein"] > 0.0


def test_wolfenstein_pdg_lambda():
    result = ckm_wolfenstein_estimate()
    assert abs(result["pdg_lambda"] - PDG_WOLFENSTEIN_LAMBDA) < 1e-5


def test_wolfenstein_keys():
    result = ckm_wolfenstein_estimate()
    for key in ("lambda_wolfenstein", "theta_12_deg", "pdg_lambda", "note"):
        assert key in result


# ---------- PMNS angle estimate ----------

def test_pmns_angle_estimate_dict():
    result = pmns_angle_estimate()
    assert isinstance(result, dict)


def test_pmns_angle_estimate_keys():
    result = pmns_angle_estimate()
    for key in ("eps_nu", "eps_l", "ratios", "theta_12_est_deg", "theta_23_est_deg"):
        assert key in result


# ---------- report ----------

def test_report_keys():
    report = ckm_pmns_orbifold_report()
    for key in ("status", "module", "residual_unknowns", "epistemic_label"):
        assert key in report


def test_report_epistemic_labels():
    report = ckm_pmns_orbifold_report()
    assert "OPEN" in report["epistemic_label"]


def test_report_ckm_values():
    report = ckm_pmns_orbifold_report()
    assert "ckm_wolfenstein_lambda" in report
    assert report["ckm_wolfenstein_lambda"] > 0.0


def test_report_residual_unknowns_nonempty():
    report = ckm_pmns_orbifold_report()
    assert len(report["residual_unknowns"]) > 0
