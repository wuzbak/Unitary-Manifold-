# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

from src.core.ew_precision_oblique import (
    compute_oblique_parameters,
    compute_rho_parameter,
    compute_w_width,
    compute_z_pole_observables,
    ew_precision_report,
)


def test_oblique_parameters_keys():
    result = compute_oblique_parameters()
    for key in ("S_pred", "T_pred", "U_pred", "S_sigma", "T_sigma", "U_sigma"):
        assert key in result


def test_oblique_parameters_are_finite():
    result = compute_oblique_parameters()
    assert result["S_pred"] == result["S_pred"]
    assert result["T_pred"] == result["T_pred"]
    assert result["U_pred"] == result["U_pred"]


def test_oblique_invalid_inputs_raise():
    with pytest.raises(ValueError):
        compute_oblique_parameters(v_ew_gev=-1.0)


def test_z_pole_observables_keys():
    result = compute_z_pole_observables()
    for key in ("Gamma_Z_pred_GeV", "R_l_pred", "A_FB_l_pred", "sin2_theta_eff_pred"):
        assert key in result


def test_w_width_residual_small():
    result = compute_w_width()
    assert result["Gamma_W_residual_pct"] < 5.0


def test_rho_parameter_reasonable():
    result = compute_rho_parameter()
    assert 0.95 < result["rho_pred"] < 1.05


def test_ew_precision_report_structure():
    report = ew_precision_report()
    for key in ("module", "status", "oblique", "z_pole", "w_width", "rho", "in_band"):
        assert key in report


def test_ew_precision_report_in_band_flags():
    report = ew_precision_report()
    assert report["in_band"]["S"] is True
    assert report["in_band"]["T"] is True
    assert report["in_band"]["U"] is True
