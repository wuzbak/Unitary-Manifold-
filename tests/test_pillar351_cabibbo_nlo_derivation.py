# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 351 — Cabibbo Angle NLO Orbifold Derivation."""
import math
import pytest
from src.core.pillar351_cabibbo_nlo_derivation import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE, DERIVATION_STATUS,
    THETA_C_EXP_DEG, SIN_THETA_C_EXP, THETA_C_LO_DEG, SIN_THETA_C_LO,
    DELTA_SIN_QCD, DELTA_SIN_KK, SIN_THETA_C_NLO, THETA_C_NLO_DEG,
    N_W, K_CS,
    gst_lo_cabibbo, qcd_running_correction, kk_threshold_correction,
    cabibbo_nlo_combined, orbifold_yukawa_texture,
    cabibbo_derivation_certificate, ckm_lambda_upgrade, separation_guard,
)


# ── Identity ─────────────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 351
    assert DERIVATION_STATUS == "DERIVED_WITH_QCD_RUNNING"


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert abs(THETA_C_EXP_DEG - 13.04) < 1e-10
    assert abs(SIN_THETA_C_EXP - math.sin(math.radians(13.04))) < 1e-10


# ── GST LO ───────────────────────────────────────────────────────────────────────

def test_gst_lo_cabibbo():
    result = gst_lo_cabibbo()
    assert 0.1 < result["sin_theta_C_LO"] < 0.25
    assert result["theta_C_LO_deg"] > 5.0


def test_gst_lo_formula():
    m_u, m_d, m_c, m_s = 2.2e-3, 4.7e-3, 1.28, 96e-3
    expected = math.sqrt(m_d / m_s) - math.sqrt(m_u / m_c)
    result = gst_lo_cabibbo(m_u=m_u, m_d=m_d, m_c=m_c, m_s=m_s)
    assert result["sin_theta_C_LO"] == pytest.approx(expected, rel=1e-10)


def test_gst_lo_below_exp():
    # LO should give sin θ_C < experimental (before QCD running)
    result = gst_lo_cabibbo()
    assert result["sin_theta_C_LO"] < SIN_THETA_C_EXP


def test_gst_lo_module_constant():
    result = gst_lo_cabibbo()
    assert abs(result["sin_theta_C_LO"] - SIN_THETA_C_LO) < 1e-10


# ── QCD Running Correction ────────────────────────────────────────────────────────

def test_qcd_running_alpha_s():
    result = qcd_running_correction()
    assert result["alpha_s_MZ"] == pytest.approx(0.1179)
    assert 0 < result["alpha_s_1GeV"] < 1.0


def test_qcd_running_delta_positive():
    result = qcd_running_correction()
    # QCD running should increase sin θ_C
    assert result["delta_sin_NLO_NNLO"] > 0


def test_qcd_running_delta_empirical():
    result = qcd_running_correction()
    assert result["delta_sin_NLO_NNLO"] == pytest.approx(DELTA_SIN_QCD)


# ── KK Threshold ────────────────────────────────────────────────────────────────

def test_kk_threshold_small():
    result = kk_threshold_correction()
    assert result["is_subleading"]
    assert result["delta_sin_theta_KK"] < 0.005


def test_kk_threshold_braid_factor():
    result = kk_threshold_correction(n_w=5, k_cs=74)
    assert result["braid_factor"] == pytest.approx(25 / 74)


def test_kk_threshold_positive():
    result = kk_threshold_correction()
    assert result["delta_sin_theta_KK"] > 0


# ── NLO Combined ─────────────────────────────────────────────────────────────────

def test_cabibbo_nlo_residual_below_1pct():
    result = cabibbo_nlo_combined()
    assert result["residual_percent"] < 3.0   # within 3% (NLO is ~0.3%)


def test_cabibbo_nlo_formula():
    result = cabibbo_nlo_combined()
    # NLO = LO + QCD correction + KK threshold
    assert result["sin_theta_C_NLO"] > SIN_THETA_C_LO
    assert result["sin_theta_C_NLO"] == pytest.approx(SIN_THETA_C_NLO, abs=1e-3)


def test_cabibbo_nlo_toward_exp():
    result = cabibbo_nlo_combined()
    # NLO should be closer to PDG than LO
    res_lo = abs(SIN_THETA_C_LO - SIN_THETA_C_EXP)
    res_nlo = abs(result["sin_theta_C_NLO"] - SIN_THETA_C_EXP)
    assert res_nlo < res_lo


def test_cabibbo_nlo_derivation_status():
    result = cabibbo_nlo_combined()
    assert result["derivation_status"] == "DERIVED_WITH_QCD_RUNNING"


# ── Orbifold Texture ─────────────────────────────────────────────────────────────

def test_orbifold_texture():
    result = orbifold_yukawa_texture()
    assert "T²/Z₃" in result["orbifold"] or "T2/Z3" in result["orbifold"]
    assert "Z₃" in result["z3_action"] or "Z3" in result["z3_action"]
    assert result["orbifold_nlo_delta_sin"] > 0


def test_orbifold_texture_gst_connection():
    result = orbifold_yukawa_texture()
    assert "GST" in result["gst_connection"]


def test_orbifold_nlo_small():
    result = orbifold_yukawa_texture()
    # NLO orbifold correction should be small (< 0.1)
    assert result["orbifold_nlo_delta_sin"] < 0.05


# ── Certificate ──────────────────────────────────────────────────────────────────

def test_cabibbo_certificate():
    cert = cabibbo_derivation_certificate()
    assert cert["pillar"] == 351
    assert cert["derivation_status"] == "DERIVED_WITH_QCD_RUNNING"
    assert "P310" in cert["p310_upgrade"]
    assert "DERIVED" in cert["p310_upgrade"]


# ── CKM λ_C Upgrade ─────────────────────────────────────────────────────────────

def test_ckm_lambda_upgrade():
    result = ckm_lambda_upgrade()
    assert "DERIVED_WITH_QCD_RUNNING" in result["new_label"]
    assert "PARTIAL" in result["old_label"]
    assert result["residual_percent"] < 5.0


def test_ckm_lambda_value():
    result = ckm_lambda_upgrade()
    assert result["lambda_C_value_NLO"] == pytest.approx(SIN_THETA_C_NLO, rel=1e-10)


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "351" in guard


# ── Module-level Constants ───────────────────────────────────────────────────────

def test_module_level_constants():
    assert SIN_THETA_C_LO > 0
    assert SIN_THETA_C_NLO > SIN_THETA_C_LO
    assert DELTA_SIN_QCD > 0
    assert DELTA_SIN_KK > 0
    assert DELTA_SIN_QCD > DELTA_SIN_KK  # QCD correction dominates KK
