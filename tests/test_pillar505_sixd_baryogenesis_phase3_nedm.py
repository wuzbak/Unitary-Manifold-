# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 505 6D baryogenesis nEDM precision certificate."""

import math

import pytest

from src.core import pillar505_sixd_baryogenesis_phase3_nedm as p505


def test_constants():
    assert p505.PILLAR_NUMBER == 505
    assert p505.PILLAR_STATUS == "SIXD_BARYOGENESIS_PHASE3_NEDM_PRECISION_CERTIFIED"
    assert "ADJACENT" in p505.ADJACENCY_TRACK_LABEL


@pytest.mark.parametrize("nf", [3, 4, 5, 6])
def test_beta_coefficients_positive_beta0(nf):
    coeffs = p505.qcd_beta_coefficients(nf)
    assert coeffs["n_f"] == float(nf)
    assert coeffs["beta0"] > 0
    assert coeffs["beta1"] > 0


@pytest.mark.parametrize("mu", [100.0, 650.0, 1000.0, 5000.0])
def test_alpha_s_envelope_ordered(mu):
    env = p505.alpha_s_three_loop_envelope(mu)
    assert env["alpha_s_low"] < env["alpha_s_central"] < env["alpha_s_high"]
    assert 0 <= env["fractional_width"] <= 0.04


def test_hadronic_budget_sub_10pct():
    budget = p505.hadronic_matrix_budget()
    assert budget["combined_fractional"] < 0.10
    assert budget["qcd_sum_rule"] > budget["lattice_matching"]


@pytest.mark.parametrize("mass", [500.0, 650.0, 800.0])
def test_nedm_prediction_positive(mass):
    pred = p505.nedm_precision_prediction(m_sigma_gev=mass)
    assert pred["d_n_low_ecm"] > 0
    assert pred["d_n_low_ecm"] < pred["d_n_central_ecm"] < pred["d_n_high_ecm"]


def test_canonical_precision_sub_10pct():
    pred = p505.nedm_precision_prediction()
    assert pred["sub_10pct_precision"] is True
    assert pred["fractional_uncertainty"] < 0.10


def test_canonical_experimental_band():
    pred = p505.nedm_precision_prediction()
    assert pred["above_sns_sensitivity"] is True
    assert pred["below_current_bound"] is True


@pytest.mark.parametrize("theta", [math.pi / 8, math.pi / 4, math.pi / 2])
def test_theta_dependence(theta):
    pred = p505.nedm_precision_prediction(theta_6=theta)
    assert pred["d_n_central_ecm"] > 0


def test_sns_tripwire_shape():
    tripwire = p505.sns_tripwire()
    assert tripwire["experiment"] == "nEDM@SNS"
    assert tripwire["prediction_low_ecm"] < tripwire["prediction_high_ecm"]


def test_report_shape():
    report = p505.pillar_report()
    assert report["pillar"] == 505
    assert report["hardgate_score_delta"] == 0.0
    assert "prediction" in report
