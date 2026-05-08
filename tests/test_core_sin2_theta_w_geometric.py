# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/sin2_theta_w_geometric.py — P4 upgrade (SU(5)+RGE)."""
from __future__ import annotations

import math
import pytest

from src.core.sin2_theta_w_geometric import (
    K_CS,
    N_W,
    N_GEN,
    N_C,
    SIN2_TW_PDG,
    SIN2_TW_GUT,
    M_GUT_GEV,
    M_Z_GEV,
    LOG_MGUT_MZ,
    COEFF_RGE,
    DELTA_SIN2_RGE,
    SIN2_TW_1LOOP,
    GEOMETRIC_PREDICTION_THRESHOLD_PCT,
    step1_gut_boundary,
    step2_rge_running,
    sin2_theta_w_full_derivation,
    p4_upgrade_certificate,
    sin2_theta_w_summary,
)


def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert N_GEN == 3
    assert N_C == 3
    assert GEOMETRIC_PREDICTION_THRESHOLD_PCT == 5.0


def test_sin2_tw_gut_exact():
    """SU(5) GUT boundary: sin²θ_W(M_GUT) = 3/8 = 0.375."""
    assert abs(SIN2_TW_GUT - 3.0 / 8.0) < 1e-15


def test_sin2_tw_pdg_reasonable():
    """PDG value ≈ 0.231."""
    assert 0.228 < SIN2_TW_PDG < 0.234


def test_m_gut_order_of_magnitude():
    """M_GUT should be around 10^12 — 10^16 GeV."""
    assert 1e12 < M_GUT_GEV < 1e17


def test_log_mgut_mz_positive():
    """log(M_GUT/M_Z) > 0 since M_GUT >> M_Z."""
    assert LOG_MGUT_MZ > 0.0
    expected = math.log(M_GUT_GEV / M_Z_GEV)
    assert abs(LOG_MGUT_MZ - expected) < 1e-10


def test_delta_sin2_rge_negative():
    """RGE correction is negative (runs sin²θ_W from 0.375 toward 0.23)."""
    assert DELTA_SIN2_RGE < 0.0


def test_sin2_tw_1loop_formula():
    """sin²θ_W(M_Z) = 3/8 + δ."""
    expected = SIN2_TW_GUT + DELTA_SIN2_RGE
    assert abs(SIN2_TW_1LOOP - expected) < 1e-15


def test_sin2_tw_1loop_close_to_pdg():
    """1-loop result within 1% of PDG."""
    residual = abs(SIN2_TW_1LOOP - SIN2_TW_PDG) / SIN2_TW_PDG * 100.0
    assert residual < 1.0


def test_sin2_tw_1loop_below_threshold():
    """Must be below 5% GEOMETRIC_PREDICTION threshold."""
    residual = abs(SIN2_TW_1LOOP - SIN2_TW_PDG) / SIN2_TW_PDG * 100.0
    assert residual < GEOMETRIC_PREDICTION_THRESHOLD_PCT


# Step 1 — GUT boundary
def test_step1_returns_dict():
    result = step1_gut_boundary()
    assert isinstance(result, dict)
    for key in ("step", "title", "formula", "value", "status"):
        assert key in result


def test_step1_step_number():
    assert step1_gut_boundary()["step"] == 1


def test_step1_value():
    assert abs(step1_gut_boundary()["value"] - 3.0 / 8.0) < 1e-15


def test_step1_status_derived():
    assert "DERIVED" in step1_gut_boundary()["status"]


# Step 2 — RGE running
def test_step2_returns_dict():
    result = step2_rge_running()
    assert isinstance(result, dict)
    for key in ("step", "delta_sin2_rge", "sin2_tw_mz", "log_ratio", "residual_pct"):
        assert key in result


def test_step2_step_number():
    assert step2_rge_running()["step"] == 2


def test_step2_log_ratio_positive():
    assert step2_rge_running()["log_ratio"] > 0.0


def test_step2_delta_negative():
    assert step2_rge_running()["delta_sin2_rge"] < 0.0


def test_step2_sin2_mz_reasonable():
    """M_Z result should be in [0.20, 0.25]."""
    result = step2_rge_running()
    assert 0.20 < result["sin2_tw_mz"] < 0.25


def test_step2_residual_below_5pct():
    result = step2_rge_running()
    assert result["residual_pct"] < 5.0


# Full derivation
def test_full_derivation_returns_dict():
    result = sin2_theta_w_full_derivation()
    assert isinstance(result, dict)
    for key in ("formula", "sin2_tw_gut", "sin2_tw_1loop", "sin2_tw_pdg",
                "residual_pct", "below_5pct_threshold"):
        assert key in result


def test_full_derivation_residual_below_threshold():
    result = sin2_theta_w_full_derivation()
    assert result["residual_pct"] < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_full_derivation_below_threshold_flag():
    result = sin2_theta_w_full_derivation()
    assert result["below_5pct_threshold"] is True


def test_full_derivation_internal_consistency():
    result = sin2_theta_w_full_derivation()
    expected = result["sin2_tw_gut"] + result["delta_sin2_rge"]
    assert abs(result["sin2_tw_1loop"] - expected) < 1e-12


# P4 certificate
def test_p4_certificate_returns_dict():
    cert = p4_upgrade_certificate()
    assert isinstance(cert, dict)
    for key in ("parameter", "previous_status", "new_status",
                "upgrade_criteria_met", "toe_score_delta"):
        assert key in cert


def test_p4_certificate_parameter():
    assert p4_upgrade_certificate()["parameter"] == "P4"


def test_p4_certificate_previous_status():
    assert p4_upgrade_certificate()["previous_status"] == "CONSTRAINED"


def test_p4_certificate_new_status():
    assert p4_upgrade_certificate()["new_status"] == "GEOMETRIC_PREDICTION"


def test_p4_certificate_upgrade_granted():
    assert p4_upgrade_certificate()["upgrade_criteria_met"] is True


def test_p4_certificate_toe_delta():
    assert abs(p4_upgrade_certificate()["toe_score_delta"] - 0.3) < 1e-10


# Summary
def test_summary_completeness():
    summary = sin2_theta_w_summary()
    for key in ("pillar", "parameter", "version", "result", "status", "toe_delta"):
        assert key in summary


def test_summary_version():
    assert sin2_theta_w_summary()["version"] == "v10.17"


def test_summary_status():
    assert sin2_theta_w_summary()["status"] == "GEOMETRIC_PREDICTION"


def test_summary_result_keys():
    result = sin2_theta_w_summary()["result"]
    for key in ("sin2_tw_gut", "delta_sin2_rge", "sin2_tw_1loop",
                "sin2_tw_pdg", "residual_pct"):
        assert key in result
