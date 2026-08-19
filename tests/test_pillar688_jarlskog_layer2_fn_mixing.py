# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 688 — Jarlskog Layer 2 FN mixing."""
from __future__ import annotations

import math
import pytest

from src.core.pillar688_jarlskog_layer2_fn_mixing import (
    EPSILON_FN,
    FN_CHARGES_D,
    FN_CHARGES_U,
    K_CS,
    N_W,
    W_RHOBAR_PDG,
    fn_phase_correction,
    jarlskog_layer2_result,
    layer2_closure_status,
    rho_bar_fn_corrected,
)


@pytest.fixture(scope="module")
def phase():
    return fn_phase_correction()


@pytest.fixture(scope="module")
def rho():
    return rho_bar_fn_corrected()


@pytest.fixture(scope="module")
def status():
    return layer2_closure_status()


@pytest.fixture(scope="module")
def report():
    return jarlskog_layer2_result()


def test_constants_are_canonical():
    assert N_W == 5
    assert K_CS == 74


def test_epsilon_fn_exact():
    assert EPSILON_FN == 5 / 74


def test_fn_charge_assignments():
    assert FN_CHARGES_U == (0, 2, 5)
    assert FN_CHARGES_D == (3, 2, 0)


def test_phase_is_dict(phase):
    assert isinstance(phase, dict)


def test_phase_has_expected_keys(phase):
    assert {"delta_fn_deg", "epsilon_fn", "numerator", "denominator"}.issubset(phase)


def test_harmonic_is_72_degrees(phase):
    assert abs(phase["harmonic_deg"] - 72.0) < 1e-12


def test_delta_fn_positive(phase):
    assert phase["delta_fn_deg"] > 0.0


def test_delta_fn_value(phase):
    assert abs(phase["delta_fn_deg"] - 3.7549893461) < 1e-9


def test_denominator_positive(phase):
    assert phase["denominator"] > 0.0


def test_rho_is_dict(rho):
    assert isinstance(rho, dict)


def test_r_b_value(rho):
    assert abs(rho["r_b"] - 0.3673006876) < 1e-10


def test_delta_sub_value(rho):
    assert abs(rho["delta_sub_deg"] - 71.0753555839) < 1e-9


def test_delta_eff_value(rho):
    assert abs(rho["delta_eff_deg"] - 74.8303449301) < 1e-9


def test_rho_bar_fn_value(rho):
    assert abs(rho["rho_bar_fn"] - 0.0961145280) < 1e-10


def test_rho_bar_fn_below_pdg(rho):
    assert rho["rho_bar_fn"] < W_RHOBAR_PDG


def test_layer2_worsens_layer1(rho):
    assert rho["improvement_vs_layer1_percent_points"] < 0.0


def test_residual_percent_value(rho):
    assert abs(rho["residual_percent"] - 39.5506113051) < 1e-8


def test_honest_note_mentions_away_from_pdg(rho):
    assert "away" in rho["honest_note"].lower() or "rather than toward" in rho["honest_note"].lower()


def test_status_is_dict(status):
    assert isinstance(status, dict)


def test_status_is_architecture_limit(status):
    assert status["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_status_fails_10_percent(status):
    assert status["passes_10_percent"] is False


def test_status_fails_5_percent(status):
    assert status["passes_5_percent"] is False


def test_status_gap_matches_rho(status, rho):
    assert abs(status["gap_percent"] - rho["residual_percent"]) < 1e-12


def test_report_is_dict(report):
    assert isinstance(report, dict)


def test_report_pillar(report):
    assert report["pillar"] == 688


def test_report_embeds_phase(report):
    assert report["fn_phase_correction"]["delta_fn_deg"] == pytest.approx(3.7549893461)


def test_report_embeds_status(report):
    assert report["layer2_closure_status"]["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"
