# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 139: Higgs VEV Exact Geometric Prediction (src/core/higgs_vev_exact.py)."""

import math
import pytest

from src.core.higgs_vev_exact import (
    higgs_vev_from_geometry,
    higgs_vev_rge_correction,
    higgs_vev_closure_status,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def result():
    return higgs_vev_from_geometry()


@pytest.fixture(scope="module")
def status():
    return higgs_vev_closure_status()


@pytest.fixture(scope="module")
def rge(result):
    return higgs_vev_rge_correction(result["y_t_used"], result["M_KK_gev"], result["v_pred_gev"])


# ---------------------------------------------------------------------------
# Return type and keys
# ---------------------------------------------------------------------------

def test_result_is_dict(result):
    assert isinstance(result, dict)


def test_result_has_lambda_tree(result):
    assert "lambda_tree" in result


def test_result_has_m_kk_gev(result):
    assert "M_KK_gev" in result


def test_result_has_delta_lambda(result):
    assert "delta_lambda" in result


def test_result_has_lambda_eff(result):
    assert "lambda_eff" in result


def test_result_has_v_pred_gev(result):
    assert "v_pred_gev" in result


def test_result_has_v_pdg_gev(result):
    assert "v_pdg_gev" in result


def test_result_has_pct_error(result):
    assert "pct_error" in result


def test_result_has_status(result):
    assert "status" in result


# ---------------------------------------------------------------------------
# Exact lambda_tree = 25/148
# ---------------------------------------------------------------------------

def test_lambda_tree_exact_fraction(result):
    assert abs(result["lambda_tree"] - 25 / 148) < 1e-12


def test_lambda_tree_numerical_value(result):
    assert abs(result["lambda_tree"] - 0.16891891891891891) < 1e-12


# ---------------------------------------------------------------------------
# M_KK in physical range
# ---------------------------------------------------------------------------

def test_m_kk_in_range(result):
    assert 900.0 < result["M_KK_gev"] < 1200.0


def test_m_kk_near_1042(result):
    assert abs(result["M_KK_gev"] - 1041.8) < 1.0


def test_m_kk_positive(result):
    assert result["M_KK_gev"] > 0


# ---------------------------------------------------------------------------
# RGE correction: delta_lambda
# ---------------------------------------------------------------------------

def test_delta_lambda_negative(result):
    assert result["delta_lambda"] < 0


def test_delta_lambda_magnitude(result):
    assert abs(abs(result["delta_lambda"]) - 0.03926) < 0.001


def test_delta_lambda_smaller_than_tree(result):
    assert abs(result["delta_lambda"]) < result["lambda_tree"]


# ---------------------------------------------------------------------------
# lambda_eff
# ---------------------------------------------------------------------------

def test_lambda_eff_less_than_lambda_tree(result):
    assert result["lambda_eff"] < result["lambda_tree"]


def test_lambda_eff_positive(result):
    assert result["lambda_eff"] > 0


def test_lambda_eff_value(result):
    assert abs(result["lambda_eff"] - 0.12966) < 0.001


def test_lambda_eff_equals_tree_plus_delta(result):
    reconstructed = result["lambda_tree"] + result["delta_lambda"]
    assert abs(reconstructed - result["lambda_eff"]) < 1e-10


# ---------------------------------------------------------------------------
# v_pred close to PDG 246.22 GeV
# ---------------------------------------------------------------------------

def test_v_pred_positive(result):
    assert result["v_pred_gev"] > 0


def test_v_pred_near_246(result):
    assert abs(result["v_pred_gev"] - 246.22) < 1.0


def test_v_pred_near_245_96(result):
    assert abs(result["v_pred_gev"] - 245.96) < 0.1


def test_v_pdg_value(result):
    assert abs(result["v_pdg_gev"] - 246.22) < 0.01


def test_pct_error_less_than_one(result):
    assert result["pct_error"] < 1.0


def test_pct_error_positive(result):
    assert result["pct_error"] > 0


def test_pct_error_value(result):
    assert abs(result["pct_error"] - 0.1048) < 0.005


# ---------------------------------------------------------------------------
# Status string
# ---------------------------------------------------------------------------

def test_status_contains_geometric_prediction(result):
    assert "GEOMETRIC PREDICTION" in result["status"]


def test_status_is_string(result):
    assert isinstance(result["status"], str)


# ---------------------------------------------------------------------------
# higgs_vev_rge_correction function
# ---------------------------------------------------------------------------

def test_rge_returns_float(rge):
    assert isinstance(rge, float)


def test_rge_negative(rge):
    assert rge < 0


def test_rge_magnitude_in_range(rge):
    assert 0.01 < abs(rge) < 0.1


def test_rge_matches_delta_lambda(result, rge):
    assert abs(rge - result["delta_lambda"]) < 0.001


# ---------------------------------------------------------------------------
# higgs_vev_closure_status
# ---------------------------------------------------------------------------

def test_closure_status_is_dict(status):
    assert isinstance(status, dict)


def test_closure_status_pillar_139(status):
    assert status["pillar"] == 139


def test_closure_status_geometric_prediction(status):
    assert "GEOMETRIC PREDICTION" in status["status"]


def test_closure_status_closed_true(status):
    assert status.get("closed") is True


def test_closure_status_has_formula(status):
    assert "formula" in status


def test_closure_status_has_inputs(status):
    assert "inputs" in status


def test_closure_status_predicted_gev(status):
    assert abs(status["predicted_gev"] - 245.96) < 0.1


def test_closure_status_pct_error_lt_one(status):
    assert status["pct_error"] < 1.0


def test_closure_status_formula_mentions_lambda(status):
    formula = status["formula"]
    assert "lambda" in formula.lower() or "λ" in formula
