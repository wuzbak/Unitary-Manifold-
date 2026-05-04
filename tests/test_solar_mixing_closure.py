# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 138: Solar Mixing Angle Closure (src/core/solar_mixing_closure.py)."""

import math
import pytest

from src.core.solar_mixing_closure import (
    solar_mixing_angle_corrected,
    solar_mixing_decomposition,
    solar_mixing_closure_status,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def result():
    return solar_mixing_angle_corrected()


@pytest.fixture(scope="module")
def decomp():
    return solar_mixing_decomposition()


@pytest.fixture(scope="module")
def status():
    return solar_mixing_closure_status()


# ---------------------------------------------------------------------------
# solar_mixing_angle_corrected — return type and keys
# ---------------------------------------------------------------------------

def test_result_is_dict(result):
    assert isinstance(result, dict)


def test_result_has_sin2_th12_key(result):
    assert "sin2_th12" in result


def test_result_has_pct_error_key(result):
    assert "pct_error" in result


def test_result_has_tbm_term_key(result):
    assert "tbm_term" in result


def test_result_has_nw_correction_key(result):
    assert "nw_correction" in result


def test_result_has_kcs_correction_key(result):
    assert "kcs_correction" in result


def test_result_has_derivation_key(result):
    assert "derivation" in result


# ---------------------------------------------------------------------------
# Exact fractional values
# ---------------------------------------------------------------------------

def test_sin2_th12_exact_formula(result):
    expected = 1 / 3 - 1 / 30 + 1 / 444
    assert abs(result["sin2_th12"] - expected) < 1e-12


def test_sin2_th12_numerical_value(result):
    assert abs(result["sin2_th12"] - 0.30225225225225225) < 1e-12


def test_tbm_term_exact(result):
    assert abs(result["tbm_term"] - 1 / 3) < 1e-14


def test_nw_correction_exact(result):
    assert abs(result["nw_correction"] - (-1 / 30)) < 1e-14


def test_kcs_correction_exact(result):
    assert abs(result["kcs_correction"] - (1 / 444)) < 1e-14


def test_tbm_plus_corrections_equals_sin2(result):
    reconstructed = result["tbm_term"] + result["nw_correction"] + result["kcs_correction"]
    assert abs(reconstructed - result["sin2_th12"]) < 1e-14


# ---------------------------------------------------------------------------
# Percent error bounds
# ---------------------------------------------------------------------------

def test_pct_error_positive(result):
    assert result["pct_error"] > 0


def test_pct_error_less_than_two(result):
    assert result["pct_error"] < 2.0


def test_pct_error_greater_than_one(result):
    assert result["pct_error"] > 1.0


def test_pct_error_value(result):
    assert abs(result["pct_error"] - 1.5464976) < 0.0001


# ---------------------------------------------------------------------------
# Physics sanity checks
# ---------------------------------------------------------------------------

def test_sin2_less_than_pdg(result):
    # PDG value is 0.307; we predict 0.3023
    assert result["sin2_th12"] < 0.307


def test_sin2_in_physical_range(result):
    assert 0.0 < result["sin2_th12"] < 1.0


def test_nw_correction_negative(result):
    assert result["nw_correction"] < 0


def test_kcs_correction_positive(result):
    assert result["kcs_correction"] > 0


def test_nw_correction_magnitude_smaller_than_tbm(result):
    assert abs(result["nw_correction"]) < abs(result["tbm_term"])


def test_kcs_correction_magnitude_smallest(result):
    assert abs(result["kcs_correction"]) < abs(result["nw_correction"])


# ---------------------------------------------------------------------------
# Derivation string
# ---------------------------------------------------------------------------

def test_derivation_is_string(result):
    assert isinstance(result["derivation"], str)


def test_derivation_non_empty(result):
    assert len(result["derivation"]) > 0


def test_derivation_mentions_pdg(result):
    assert "PDG" in result["derivation"] or "pdg" in result["derivation"].lower()


# ---------------------------------------------------------------------------
# solar_mixing_decomposition
# ---------------------------------------------------------------------------

def test_decomp_is_dict(decomp):
    assert isinstance(decomp, dict)


def test_decomp_has_three_terms(decomp):
    # tbm_term, nw_correction, kcs_correction
    assert "tbm_term" in decomp
    assert "nw_correction" in decomp
    assert "kcs_correction" in decomp


def test_decomp_total_matches_formula(decomp):
    assert "total" in decomp
    expected = 1 / 3 - 1 / 30 + 1 / 444
    assert abs(decomp["total"] - expected) < 1e-12


def test_decomp_tbm_value(decomp):
    entry = decomp["tbm_term"]
    val = entry["value"] if isinstance(entry, dict) else entry
    assert abs(val - 1 / 3) < 1e-14


def test_decomp_nw_value(decomp):
    entry = decomp["nw_correction"]
    val = entry["value"] if isinstance(entry, dict) else entry
    assert abs(val - (-1 / 30)) < 1e-14


def test_decomp_kcs_value(decomp):
    entry = decomp["kcs_correction"]
    val = entry["value"] if isinstance(entry, dict) else entry
    assert abs(val - (1 / 444)) < 1e-14


def test_decomp_has_pdg_key(decomp):
    assert "pdg" in decomp


def test_decomp_pdg_is_float(decomp):
    assert isinstance(decomp["pdg"], float)


# ---------------------------------------------------------------------------
# solar_mixing_closure_status
# ---------------------------------------------------------------------------

def test_status_is_dict(status):
    assert isinstance(status, dict)


def test_status_pillar_is_138(status):
    assert status["pillar"] == 138


def test_status_contains_geometric_prediction(status):
    assert "GEOMETRIC PREDICTION" in status["status"]


def test_status_has_predicted_value(status):
    assert "predicted" in status


def test_status_predicted_matches(status):
    assert abs(status["predicted"] - (1 / 3 - 1 / 30 + 1 / 444)) < 1e-12


def test_status_closed_true(status):
    assert status.get("closed") is True


def test_status_has_formula(status):
    assert "formula" in status


def test_status_has_inputs(status):
    assert "inputs" in status


def test_status_inputs_non_empty(status):
    assert len(status["inputs"]) >= 2


def test_status_pct_error_matches(status):
    assert abs(status["pct_error"] - 1.5464976) < 0.0001


# ---------------------------------------------------------------------------
# Custom parameters check (if API supports n_w, k_cs arguments)
# ---------------------------------------------------------------------------

def test_custom_nw_changes_result():
    # n_w=7 should give nw_correction = -1/(6*7)
    r = solar_mixing_angle_corrected(n_w=7)
    assert abs(r["nw_correction"] - (-1 / 42)) < 1e-14


def test_custom_kcs_changes_result():
    # k_cs=100 should give kcs_correction = 1/(6*100)
    r = solar_mixing_angle_corrected(k_cs=100)
    assert abs(r["kcs_correction"] - (1 / 600)) < 1e-14


def test_custom_params_sum_correctly():
    r = solar_mixing_angle_corrected(n_w=7, k_cs=100)
    reconstructed = r["tbm_term"] + r["nw_correction"] + r["kcs_correction"]
    assert abs(reconstructed - r["sin2_th12"]) < 1e-14
