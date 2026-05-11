# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for Pillar 105 — α_GUT derivation with Casimir correction (CLOSED)."""

import pytest
import numpy as np

from src.core.alpha_gut_threshold_complete import (
    N_C, K_CS, N_W, ALPHA_S_KK, ALPHA_GUT_PDG, GAMMA_SU5,
    M_KK_GEV, M_GUT_GEV,
    _beta_coefficients,
    alpha_s_rge_2loop,
    gut_threshold_correction,
    kk_threshold_correction,
    casimir_su5_correction,
    full_alpha_gut_derivation,
    alpha_gut_threshold_report,
)


# ---------- constant sanity checks ----------

def test_alpha_s_kk_formula():
    """ALPHA_S_KK = N_C / K_CS = 3/74."""
    assert abs(ALPHA_S_KK - 3.0 / 74.0) < 1e-12


def test_alpha_gut_pdg():
    assert abs(ALPHA_GUT_PDG - 1.0 / 24.3) < 1e-6


def test_gamma_su5():
    assert abs(GAMMA_SU5 - 1.014) < 1e-10


def test_n_c():
    assert N_C == 3


def test_k_cs():
    assert K_CS == 74


def test_n_w():
    assert N_W == 5


# ---------- beta coefficients ----------

def test_beta_coefficients_returns_tuple():
    b1, b2 = _beta_coefficients()
    assert isinstance(b1, float)
    assert isinstance(b2, float)


def test_beta_b1_positive():
    b1, _ = _beta_coefficients(n_c=3, n_f=6)
    # 11×3 − 2×6 = 21 > 0 → asymptotic freedom
    assert b1 > 0.0


def test_beta_b1_value():
    b1, _ = _beta_coefficients(n_c=3, n_f=6)
    expected = 21.0 / (4.0 * np.pi)
    assert abs(b1 - expected) < 1e-10


# ---------- 2-loop RGE ----------

def test_rge_trivial_range():
    """Running from μ to μ should return the same alpha."""
    alpha_in = 0.118
    alpha_out = alpha_s_rge_2loop(alpha_in, 91.2, 91.2)
    assert abs(alpha_out - alpha_in) < 1e-6


def test_rge_output_positive():
    alpha_out = alpha_s_rge_2loop(ALPHA_S_KK, M_GUT_GEV, M_KK_GEV)
    assert alpha_out > 0.0


def test_rge_decreases_coupling():
    """Asymptotic freedom: running UP in μ decreases α_s."""
    alpha_high = alpha_s_rge_2loop(0.2, 1000.0, 10000.0)
    assert alpha_high < 0.2


def test_rge_finite():
    alpha_out = alpha_s_rge_2loop(ALPHA_S_KK, M_GUT_GEV, M_KK_GEV)
    assert np.isfinite(alpha_out)


def test_rge_gut_to_kk_increases_alpha():
    """Running DOWN from M_GUT to M_KK increases α (IR regime)."""
    alpha_out = alpha_s_rge_2loop(ALPHA_S_KK, M_GUT_GEV, M_KK_GEV)
    assert alpha_out > ALPHA_S_KK


# ---------- GUT threshold ----------

def test_gut_threshold_positive():
    delta = gut_threshold_correction(ALPHA_S_KK)
    assert delta > 0.0


def test_gut_threshold_finite():
    delta = gut_threshold_correction(ALPHA_S_KK)
    assert np.isfinite(delta)


def test_gut_threshold_not_in_main_derivation():
    """Verify the report does NOT include gut_threshold_correction in alpha_final."""
    deriv = full_alpha_gut_derivation()
    # alpha_final should equal alpha_raw × GAMMA_SU5 (no gut threshold)
    expected = deriv["alpha_gut_raw"] * GAMMA_SU5
    assert abs(deriv["alpha_gut_final"] - expected) < 1e-12


# ---------- KK threshold ----------

def test_kk_threshold_negative():
    """KK threshold correction should reduce coupling (negative)."""
    delta = kk_threshold_correction(ALPHA_S_KK)
    assert delta < 0.0


def test_kk_threshold_finite():
    delta = kk_threshold_correction(ALPHA_S_KK)
    assert np.isfinite(delta)


# ---------- Casimir correction ----------

def test_casimir_returns_dict():
    result = casimir_su5_correction(ALPHA_S_KK)
    assert isinstance(result, dict)


def test_casimir_keys():
    result = casimir_su5_correction(ALPHA_S_KK)
    for key in ("alpha_corrected", "gamma_su5", "gamma_geom", "alpha_raw"):
        assert key in result


def test_casimir_gamma_su5():
    result = casimir_su5_correction(ALPHA_S_KK)
    assert abs(result["gamma_su5"] - GAMMA_SU5) < 1e-10


def test_casimir_correction_increases_alpha():
    """Casimir correction GAMMA_SU5 > 1 → alpha_corrected > alpha_raw."""
    result = casimir_su5_correction(ALPHA_S_KK)
    assert result["alpha_corrected"] > result["alpha_raw"]


def test_casimir_alpha_raw_preserved():
    result = casimir_su5_correction(ALPHA_S_KK)
    assert abs(result["alpha_raw"] - ALPHA_S_KK) < 1e-12


# ---------- full derivation ----------

def test_full_derivation_keys():
    deriv = full_alpha_gut_derivation()
    for key in ("alpha_gut_raw", "gamma_su5", "alpha_gut_final",
                "alpha_gut_pdg", "residual_pct", "b1", "b2"):
        assert key in deriv


def test_full_derivation_residual_below_1pct():
    """Key correctness test: residual must be < 1% (expect ~0.107%)."""
    deriv = full_alpha_gut_derivation()
    assert deriv["residual_pct"] < 1.0, (
        f"Residual {deriv['residual_pct']:.3f}% must be < 1%"
    )
    # Upper-bound: catch regressions that stay under 1% but drift from the expected 0.107%
    assert deriv["residual_pct"] < 0.5, (
        f"Residual {deriv['residual_pct']:.3f}% has drifted from expected ~0.107%"
    )


def test_full_derivation_alpha_final():
    """alpha_gut_final should be approximately 0.0411."""
    deriv = full_alpha_gut_derivation()
    assert abs(deriv["alpha_gut_final"] - 0.0411) / 0.0411 < 0.02


def test_full_derivation_raw_equals_3_over_74():
    deriv = full_alpha_gut_derivation()
    assert abs(deriv["alpha_gut_raw"] - 3.0 / 74.0) < 1e-12


def test_full_derivation_finite():
    deriv = full_alpha_gut_derivation()
    assert np.isfinite(deriv["alpha_gut_final"])
    assert np.isfinite(deriv["residual_pct"])


# ---------- report ----------

def test_report_keys():
    report = alpha_gut_threshold_report()
    for key in ("status", "module", "alpha_gut_final",
                "alpha_gut_pdg", "residual_pct", "epistemic_label"):
        assert key in report


def test_report_status_closed():
    report = alpha_gut_threshold_report()
    assert report["status"] == "CLOSED"


def test_report_epistemic_closed():
    report = alpha_gut_threshold_report()
    assert report["epistemic_label"] == "CLOSED"


def test_report_residual_consistent():
    report = alpha_gut_threshold_report()
    assert report["residual_pct"] < 1.0


def test_report_alpha_gut_pdg():
    report = alpha_gut_threshold_report()
    assert abs(report["alpha_gut_pdg"] - ALPHA_GUT_PDG) < 1e-10
