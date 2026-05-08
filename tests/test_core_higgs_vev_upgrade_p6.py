# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/higgs_vev_upgrade_p6.py — P6 upgrade (Pillar 139 certificate)."""
from __future__ import annotations

import pytest

from src.core.higgs_vev_upgrade_p6 import (
    V_HIGGS_PDG,
    GEOMETRIC_PREDICTION_THRESHOLD_PCT,
    p6_derivation,
    p6_upgrade_certificate,
    higgs_vev_p6_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_v_higgs_pdg():
    """PDG Higgs VEV = 246.22 GeV."""
    assert abs(V_HIGGS_PDG - 246.22) < 1e-10


def test_geometric_prediction_threshold():
    assert GEOMETRIC_PREDICTION_THRESHOLD_PCT == 5.0


# ---------------------------------------------------------------------------
# P6 derivation
# ---------------------------------------------------------------------------

def test_p6_derivation_returns_dict():
    result = p6_derivation()
    assert isinstance(result, dict)


def test_p6_derivation_required_keys():
    result = p6_derivation()
    for key in ("pillar", "module", "v_pred_gev", "v_pdg_gev",
                "residual_pct", "below_5pct_threshold", "converged"):
        assert key in result


def test_p6_derivation_pillar_number():
    assert p6_derivation()["pillar"] == 139


def test_p6_derivation_v_pred_range():
    """v_pred from Pillar 139 should be in [244, 248] GeV."""
    result = p6_derivation()
    assert 244.0 < result["v_pred_gev"] < 248.0


def test_p6_derivation_v_pred_close_to_pdg():
    """v_pred should be within 1% of PDG 246.22 GeV."""
    result = p6_derivation()
    pct = abs(result["v_pred_gev"] - V_HIGGS_PDG) / V_HIGGS_PDG * 100.0
    assert pct < 1.0


def test_p6_derivation_residual_below_threshold():
    result = p6_derivation()
    assert result["residual_pct"] < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_p6_derivation_below_threshold_flag():
    result = p6_derivation()
    assert result["below_5pct_threshold"] is True


def test_p6_derivation_converged():
    result = p6_derivation()
    assert result["converged"] is True


def test_p6_derivation_residual_consistent():
    """residual_pct should match |v_pred - v_pdg| / v_pdg × 100."""
    result = p6_derivation()
    expected = abs(result["v_pred_gev"] - result["v_pdg_gev"]) / result["v_pdg_gev"] * 100.0
    assert abs(result["residual_pct"] - expected) < 1e-8


def test_p6_derivation_lambda_tree_positive():
    """Tree-level quartic coupling must be positive."""
    result = p6_derivation()
    assert result["lambda_tree"] > 0.0


def test_p6_derivation_lambda_eff_positive():
    """Effective quartic coupling (after RGE) must still be positive."""
    result = p6_derivation()
    assert result["lambda_eff"] > 0.0


def test_p6_derivation_lambda_eff_less_than_tree():
    """Top-Yukawa RGE correction reduces λ, so λ_eff < λ_tree."""
    result = p6_derivation()
    assert result["lambda_eff"] < result["lambda_tree"]


def test_p6_derivation_m_kk_range():
    """M_KK ≈ 1042 GeV (πkR=37)."""
    result = p6_derivation()
    assert 900.0 < result["m_kk_gev"] < 1200.0


# ---------------------------------------------------------------------------
# P6 upgrade certificate
# ---------------------------------------------------------------------------

def test_p6_certificate_returns_dict():
    cert = p6_upgrade_certificate()
    assert isinstance(cert, dict)


def test_p6_certificate_required_keys():
    cert = p6_upgrade_certificate()
    for key in ("parameter", "previous_status", "new_status",
                "upgrade_criteria_met", "toe_score_delta"):
        assert key in cert


def test_p6_certificate_parameter():
    assert p6_upgrade_certificate()["parameter"] == "P6"


def test_p6_certificate_previous_status():
    assert p6_upgrade_certificate()["previous_status"] == "CONSTRAINED"


def test_p6_certificate_new_status():
    assert p6_upgrade_certificate()["new_status"] == "GEOMETRIC_PREDICTION"


def test_p6_certificate_upgrade_granted():
    assert p6_upgrade_certificate()["upgrade_criteria_met"] is True


def test_p6_certificate_toe_delta():
    assert abs(p6_upgrade_certificate()["toe_score_delta"] - 0.3) < 1e-10


def test_p6_certificate_residual_below_threshold():
    cert = p6_upgrade_certificate()
    assert cert["residual_pct"] < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_p6_certificate_v_pred_close_to_pdg():
    cert = p6_upgrade_certificate()
    assert abs(cert["v_pred_gev"] - cert["v_pdg_gev"]) / cert["v_pdg_gev"] < 0.05


def test_p6_certificate_conditions_list():
    cert = p6_upgrade_certificate()
    assert isinstance(cert["certification_conditions"], list)
    assert len(cert["certification_conditions"]) >= 3


def test_p6_certificate_derivation_chain_list():
    cert = p6_upgrade_certificate()
    assert isinstance(cert["derivation_chain"], list)
    assert len(cert["derivation_chain"]) >= 3


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_summary_returns_dict():
    summary = higgs_vev_p6_summary()
    assert isinstance(summary, dict)


def test_summary_required_keys():
    summary = higgs_vev_p6_summary()
    for key in ("pillar", "parameter", "version", "title", "result",
                "status", "toe_delta", "certificate"):
        assert key in summary


def test_summary_parameter():
    assert higgs_vev_p6_summary()["parameter"] == "P6"


def test_summary_version():
    assert higgs_vev_p6_summary()["version"] == "v10.18"


def test_summary_status():
    assert higgs_vev_p6_summary()["status"] == "GEOMETRIC_PREDICTION"


def test_summary_toe_delta():
    assert abs(higgs_vev_p6_summary()["toe_delta"] - 0.3) < 1e-10


def test_summary_result_keys():
    result = higgs_vev_p6_summary()["result"]
    for key in ("v_pred_gev", "v_pdg_gev", "residual_pct"):
        assert key in result


def test_summary_result_v_pred_reasonable():
    summary = higgs_vev_p6_summary()
    assert 240.0 < summary["result"]["v_pred_gev"] < 252.0


def test_summary_result_residual_below_threshold():
    summary = higgs_vev_p6_summary()
    assert summary["result"]["residual_pct"] < GEOMETRIC_PREDICTION_THRESHOLD_PCT
