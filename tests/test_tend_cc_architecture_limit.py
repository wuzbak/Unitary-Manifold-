# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/tend/cc_architecture_limit.py — P28 cosmological constant."""
from __future__ import annotations

import math
import pytest

from src.tend.cc_architecture_limit import (
    K_CS,
    N_W,
    PI_KR,
    N_FLUX,
    LAMBDA_OBS_MPLANCK4,
    LAYER1_REDUCTION_ORDERS,
    LAYER2_KK_MASS_ORDERS,
    LAYER2_RESIDUAL_ORDERS,
    LAYER3_VACUA_COUNT_LOG10,
    ARCHITECTURE_DIMENSION,
    layer1_rs1_cancellation,
    layer2_casimir_energy,
    layer3_flux_landscape,
    gap_reduction_chain,
    p28_architecture_certificate,
    cc_architecture_summary,
)


def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert N_FLUX == 37
    assert ARCHITECTURE_DIMENSION == "10D"


def test_n_flux_is_half_k_cs():
    assert N_FLUX == K_CS // 2


def test_lambda_obs_order_of_magnitude():
    """Λ_obs should be ~10^{-122} M_Pl^4."""
    assert 1e-125 < LAMBDA_OBS_MPLANCK4 < 1e-119


def test_layer1_reduction_about_64_orders():
    """RS1 reduces the problem by ~64 orders (exp(-4πkR))."""
    assert 60.0 < LAYER1_REDUCTION_ORDERS < 70.0


def test_layer2_kk_mass_orders_negative():
    """M_KK^4/M_Pl^4 is a large negative log10."""
    assert LAYER2_KK_MASS_ORDERS < -60.0


def test_layer2_residual_positive():
    """After RS1+Casimir, a residual gap remains."""
    assert LAYER2_RESIDUAL_ORDERS > 50.0


def test_layer3_vacua_count():
    """BP vacua count: 10^{2×N_flux} = 10^{74}."""
    assert abs(LAYER3_VACUA_COUNT_LOG10 - 74.0) < 1.0


# Layer 1 tests
def test_layer1_rs1_cancellation_returns_dict():
    result = layer1_rs1_cancellation()
    assert isinstance(result, dict)
    for key in ("mechanism", "naive_gap_log10", "warp_suppression_log10", "residual_gap_log10"):
        assert key in result


def test_layer1_reduces_problem():
    result = layer1_rs1_cancellation()
    assert result["residual_gap_log10"] < result["naive_gap_log10"]
    assert result["residual_gap_log10"] > 0.0


def test_layer1_warp_suppression_consistent_with_pi_kr():
    result = layer1_rs1_cancellation()
    expected = 4.0 * PI_KR / math.log(10.0)
    assert abs(result["warp_suppression_log10"] - expected) < 0.1


# Layer 2 tests
def test_layer2_casimir_energy_returns_dict():
    result = layer2_casimir_energy()
    assert isinstance(result, dict)
    for key in ("formula", "casimir_coefficient", "casimir_sign", "residual_gap_log10"):
        assert key in result


def test_layer2_casimir_coefficient_positive():
    result = layer2_casimir_energy()
    assert result["casimir_coefficient"] > 0.0


def test_layer2_casimir_sign_negative():
    result = layer2_casimir_energy()
    assert "negative" in result["casimir_sign"].lower()


def test_layer2_residual_gap_positive():
    result = layer2_casimir_energy()
    assert result["residual_gap_log10"] > 50.0


# Layer 3 tests
def test_layer3_flux_landscape_returns_dict():
    result = layer3_flux_landscape()
    assert isinstance(result, dict)
    for key in ("mechanism", "n_flux", "n_vacua_log10", "architecture_dimension"):
        assert key in result


def test_layer3_n_flux_correct():
    result = layer3_flux_landscape()
    assert result["n_flux"] == 37


def test_layer3_architecture_dimension():
    result = layer3_flux_landscape()
    assert result["architecture_dimension"] == "10D"


def test_layer3_vacua_count_correct():
    result = layer3_flux_landscape()
    assert abs(result["n_vacua_log10"] - 74.0) < 1.0


# Gap reduction chain
def test_gap_reduction_chain_returns_dict():
    chain = gap_reduction_chain()
    assert isinstance(chain, dict)
    assert "initial_gap_log10" in chain
    assert "final_status" in chain


def test_gap_reduction_chain_final_status():
    chain = gap_reduction_chain()
    assert "ARCHITECTURE_LIMIT_CERTIFIED" in chain["final_status"]
    assert "10D" in chain["final_status"]


def test_gap_reduction_chain_initial_gap():
    chain = gap_reduction_chain()
    assert abs(chain["initial_gap_log10"] - 122.0) < 1.0


# P28 certificate
def test_p28_architecture_certificate_returns_dict():
    cert = p28_architecture_certificate()
    assert isinstance(cert, dict)
    for key in ("parameter", "toe_label", "architecture_dimension", "status"):
        assert key in cert


def test_p28_certificate_parameter():
    cert = p28_architecture_certificate()
    assert cert["parameter"] == "P28"


def test_p28_certificate_label():
    cert = p28_architecture_certificate()
    assert cert["toe_label"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_p28_certificate_toe_score():
    cert = p28_architecture_certificate()
    assert cert["current_toe_score"] == 0.1


def test_p28_certificate_n_flux_identification():
    cert = p28_architecture_certificate()
    assert "37" in cert["n_flux_identification"]


# Summary
def test_cc_architecture_summary_completeness():
    summary = cc_architecture_summary()
    for key in ("pillar", "version", "status", "k_cs", "n_flux", "architecture_dimension"):
        assert key in summary


def test_cc_architecture_summary_version():
    summary = cc_architecture_summary()
    assert summary["version"] == "v10.17"


def test_cc_architecture_summary_status():
    summary = cc_architecture_summary()
    assert "ARCHITECTURE_LIMIT_CERTIFIED" in summary["status"]
    assert "10D" in summary["status"]
