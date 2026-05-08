# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/alpha_em_geometric.py — P13 upgrade (CS + RGE chain)."""
from __future__ import annotations

import math
import pytest

from src.core.alpha_em_geometric import (
    K_CS,
    N_W,
    N_C,
    ALPHA_GUT,
    ALPHA_INV_GEO,
    ALPHA_INV_PDG,
    GEOMETRIC_PREDICTION_THRESHOLD_PCT,
    step1_alpha_gut,
    step2_rge_chain,
    alpha_em_full_derivation,
    p13_upgrade_certificate,
    alpha_em_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_k_cs():
    assert K_CS == 74


def test_n_w():
    assert N_W == 5


def test_n_c():
    assert N_C == 3
    assert N_C == math.ceil(N_W / 2)


def test_alpha_gut_formula():
    """α_GUT = N_c / K_CS = 3/74."""
    assert abs(ALPHA_GUT - 3.0 / 74.0) < 1e-15


def test_alpha_gut_magnitude():
    """α_GUT should be close to 1/25 = 0.04 (GUT coupling)."""
    assert 0.03 < ALPHA_GUT < 0.06


def test_alpha_inv_geo_value():
    """UM geometric prediction α⁻¹ ≈ 137.0."""
    assert abs(ALPHA_INV_GEO - 137.0) < 1e-10


def test_alpha_inv_pdg_value():
    """PDG α⁻¹ = 137.036."""
    assert abs(ALPHA_INV_PDG - 137.036) < 0.001


def test_geometric_prediction_threshold():
    assert GEOMETRIC_PREDICTION_THRESHOLD_PCT == 5.0


def test_residual_below_threshold():
    """UM α⁻¹ residual from PDG must be < 5%."""
    residual = abs(ALPHA_INV_GEO - ALPHA_INV_PDG) / ALPHA_INV_PDG * 100.0
    assert residual < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_residual_very_small():
    """Residual should be below 0.1% (expected ~0.026%)."""
    residual = abs(ALPHA_INV_GEO - ALPHA_INV_PDG) / ALPHA_INV_PDG * 100.0
    assert residual < 0.1


# ---------------------------------------------------------------------------
# Step 1 — α_GUT
# ---------------------------------------------------------------------------

def test_step1_returns_dict():
    result = step1_alpha_gut()
    assert isinstance(result, dict)


def test_step1_required_keys():
    result = step1_alpha_gut()
    for key in ("step", "title", "formula", "value", "status"):
        assert key in result


def test_step1_step_number():
    assert step1_alpha_gut()["step"] == 1


def test_step1_value_equals_alpha_gut():
    assert abs(step1_alpha_gut()["value"] - ALPHA_GUT) < 1e-15


def test_step1_value_formula():
    """step1 value should equal 3/74."""
    assert abs(step1_alpha_gut()["value"] - 3.0 / 74.0) < 1e-15


def test_step1_alpha_gut_inv():
    """α_GUT⁻¹ = K_CS/N_C = 74/3."""
    result = step1_alpha_gut()
    assert abs(result["alpha_gut_inv"] - 74.0 / 3.0) < 1e-10


def test_step1_status_contains_derived():
    assert "DERIVED" in step1_alpha_gut()["status"]


def test_step1_custom_args():
    result = step1_alpha_gut(k_cs=74, n_c=3)
    assert abs(result["value"] - 3.0 / 74.0) < 1e-15


# ---------------------------------------------------------------------------
# Step 2 — RGE chain
# ---------------------------------------------------------------------------

def test_step2_returns_dict():
    result = step2_rge_chain()
    assert isinstance(result, dict)


def test_step2_required_keys():
    result = step2_rge_chain()
    for key in ("step", "alpha_gut_input", "alpha_inv_geo", "alpha_inv_pdg",
                "residual_pct"):
        assert key in result


def test_step2_step_number():
    assert step2_rge_chain()["step"] == 2


def test_step2_alpha_inv_geo():
    assert abs(step2_rge_chain()["alpha_inv_geo"] - ALPHA_INV_GEO) < 1e-10


def test_step2_alpha_inv_pdg():
    assert abs(step2_rge_chain()["alpha_inv_pdg"] - ALPHA_INV_PDG) < 1e-10


def test_step2_residual_below_threshold():
    result = step2_rge_chain()
    assert result["residual_pct"] < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_step2_residual_positive():
    assert step2_rge_chain()["residual_pct"] >= 0.0


# ---------------------------------------------------------------------------
# Full derivation
# ---------------------------------------------------------------------------

def test_full_derivation_returns_dict():
    result = alpha_em_full_derivation()
    assert isinstance(result, dict)


def test_full_derivation_required_keys():
    result = alpha_em_full_derivation()
    for key in ("formula", "alpha_gut", "alpha_inv_geo", "alpha_inv_pdg",
                "residual_pct", "below_5pct_threshold", "step1", "step2"):
        assert key in result


def test_full_derivation_alpha_gut():
    result = alpha_em_full_derivation()
    assert abs(result["alpha_gut"] - ALPHA_GUT) < 1e-15


def test_full_derivation_alpha_inv_geo():
    result = alpha_em_full_derivation()
    assert abs(result["alpha_inv_geo"] - ALPHA_INV_GEO) < 1e-10


def test_full_derivation_residual_below_threshold():
    result = alpha_em_full_derivation()
    assert result["residual_pct"] < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_full_derivation_below_threshold_flag():
    result = alpha_em_full_derivation()
    assert result["below_5pct_threshold"] is True


def test_full_derivation_step1_embedded():
    result = alpha_em_full_derivation()
    assert isinstance(result["step1"], dict)
    assert result["step1"]["step"] == 1


def test_full_derivation_step2_embedded():
    result = alpha_em_full_derivation()
    assert isinstance(result["step2"], dict)
    assert result["step2"]["step"] == 2


# ---------------------------------------------------------------------------
# P13 upgrade certificate
# ---------------------------------------------------------------------------

def test_p13_certificate_returns_dict():
    cert = p13_upgrade_certificate()
    assert isinstance(cert, dict)


def test_p13_certificate_required_keys():
    cert = p13_upgrade_certificate()
    for key in ("parameter", "previous_status", "new_status",
                "upgrade_criteria_met", "toe_score_delta"):
        assert key in cert


def test_p13_certificate_parameter():
    assert p13_upgrade_certificate()["parameter"] == "P13"


def test_p13_certificate_previous_status():
    assert p13_upgrade_certificate()["previous_status"] == "CONSTRAINED"


def test_p13_certificate_new_status():
    assert p13_upgrade_certificate()["new_status"] == "GEOMETRIC_PREDICTION"


def test_p13_certificate_upgrade_granted():
    assert p13_upgrade_certificate()["upgrade_criteria_met"] is True


def test_p13_certificate_toe_delta():
    assert abs(p13_upgrade_certificate()["toe_score_delta"] - 0.3) < 1e-10


def test_p13_certificate_residual():
    cert = p13_upgrade_certificate()
    assert cert["residual_pct"] < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_p13_certificate_alpha_inv_geo():
    cert = p13_upgrade_certificate()
    assert abs(cert["alpha_inv_geo"] - ALPHA_INV_GEO) < 1e-10


def test_p13_certificate_derivation_chain_list():
    cert = p13_upgrade_certificate()
    assert isinstance(cert["derivation_chain"], list)
    assert len(cert["derivation_chain"]) >= 2


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_summary_returns_dict():
    summary = alpha_em_summary()
    assert isinstance(summary, dict)


def test_summary_required_keys():
    summary = alpha_em_summary()
    for key in ("pillar", "parameter", "version", "title", "result",
                "status", "toe_delta", "certificate"):
        assert key in summary


def test_summary_parameter():
    assert alpha_em_summary()["parameter"] == "P13"


def test_summary_version():
    assert alpha_em_summary()["version"] == "v10.18"


def test_summary_status():
    assert alpha_em_summary()["status"] == "GEOMETRIC_PREDICTION"


def test_summary_toe_delta():
    assert abs(alpha_em_summary()["toe_delta"] - 0.3) < 1e-10


def test_summary_result_keys():
    result = alpha_em_summary()["result"]
    for key in ("alpha_gut", "alpha_inv_geo", "alpha_inv_pdg", "residual_pct"):
        assert key in result


def test_summary_result_residual_below_threshold():
    summary = alpha_em_summary()
    assert summary["result"]["residual_pct"] < GEOMETRIC_PREDICTION_THRESHOLD_PCT
