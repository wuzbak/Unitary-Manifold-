# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/mp_me_geometric_prediction.py — P12 upgrade."""
from __future__ import annotations

import math
import pytest

from src.core.mp_me_geometric_prediction import (
    K_CS,
    N_W,
    PI_KR,
    N_C,
    MP_ME_GEO,
    MP_ME_PDG,
    MP_ME_RESIDUAL_PCT,
    NLO_ERROR_BOUND_PCT,
    GEOMETRIC_PREDICTION_THRESHOLD_PCT,
    mp_me_nlo_error_bound,
    p12_upgrade_certificate,
    mp_me_geometric_prediction_summary,
)


def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert N_C == 3
    assert GEOMETRIC_PREDICTION_THRESHOLD_PCT == 5.0


def test_mp_me_geo_value():
    """K_CS²/N_c = 74²/3 = 5476/3."""
    expected = 74**2 / 3.0
    assert abs(MP_ME_GEO - expected) < 1e-10


def test_mp_me_pdg_reasonable():
    """PDG value ≈ 1836."""
    assert 1830.0 < MP_ME_PDG < 1840.0


def test_residual_below_5pct():
    """0.59% residual must be below GEOMETRIC_PREDICTION threshold."""
    assert MP_ME_RESIDUAL_PCT < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_nlo_bound_below_5pct():
    """NLO bound O(1/37) ≈ 2.7% must be below threshold."""
    assert NLO_ERROR_BOUND_PCT < GEOMETRIC_PREDICTION_THRESHOLD_PCT


def test_residual_calculation():
    """Verify residual is computed correctly."""
    expected = abs(MP_ME_GEO - MP_ME_PDG) / MP_ME_PDG * 100.0
    assert abs(MP_ME_RESIDUAL_PCT - expected) < 1e-10


def test_nlo_bound_calculation():
    """NLO bound = 1/πkR × 100 = 1/37 × 100."""
    expected = 100.0 / 37.0
    assert abs(NLO_ERROR_BOUND_PCT - expected) < 1e-10


# NLO error bound analysis
def test_nlo_error_bound_returns_dict():
    result = mp_me_nlo_error_bound()
    assert isinstance(result, dict)
    for key in ("geo_value", "pdg_value", "residual_pct", "nlo_bound_pct",
                "residual_below_threshold", "nlo_bound_below_threshold",
                "c_lat_cancels_in_ratio", "upgrade_verdict"):
        assert key in result


def test_nlo_error_bound_residual_below_threshold():
    result = mp_me_nlo_error_bound()
    assert result["residual_below_threshold"] is True


def test_nlo_error_bound_nlo_below_threshold():
    result = mp_me_nlo_error_bound()
    assert result["nlo_bound_below_threshold"] is True


def test_nlo_error_bound_c_lat_cancels():
    result = mp_me_nlo_error_bound()
    assert result["c_lat_cancels_in_ratio"] is True


def test_nlo_error_bound_verdict():
    result = mp_me_nlo_error_bound()
    assert result["upgrade_verdict"] == "GEOMETRIC_PREDICTION"


# P12 certificate
def test_p12_certificate_returns_dict():
    cert = p12_upgrade_certificate()
    assert isinstance(cert, dict)
    for key in ("parameter", "new_status", "upgrade_criteria_met",
                "toe_score_delta", "previous_status"):
        assert key in cert


def test_p12_certificate_parameter():
    cert = p12_upgrade_certificate()
    assert cert["parameter"] == "P12"


def test_p12_certificate_previous_status():
    cert = p12_upgrade_certificate()
    assert cert["previous_status"] == "CONSTRAINED"


def test_p12_certificate_new_status():
    cert = p12_upgrade_certificate()
    assert cert["new_status"] == "GEOMETRIC_PREDICTION"


def test_p12_certificate_upgrade_granted():
    cert = p12_upgrade_certificate()
    assert cert["upgrade_criteria_met"] is True


def test_p12_certificate_toe_delta():
    cert = p12_upgrade_certificate()
    assert abs(cert["toe_score_delta"] - 0.3) < 1e-10


# Summary
def test_mp_me_summary_completeness():
    summary = mp_me_geometric_prediction_summary()
    for key in ("pillar", "parameter", "version", "result", "status", "toe_delta"):
        assert key in summary


def test_mp_me_summary_version():
    summary = mp_me_geometric_prediction_summary()
    assert summary["version"] == "v10.17"


def test_mp_me_summary_status():
    summary = mp_me_geometric_prediction_summary()
    assert summary["status"] == "GEOMETRIC_PREDICTION"


def test_mp_me_summary_result_keys():
    summary = mp_me_geometric_prediction_summary()
    result = summary["result"]
    assert "geo_value" in result
    assert "pdg_value" in result
    assert "residual_pct" in result
    assert "nlo_bound_pct" in result
