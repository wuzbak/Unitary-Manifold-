# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 235 — Solar Physics Open Questions Engine."""

from __future__ import annotations

import math

import pytest

from src.core.pillar235_solar_physics_open_questions_engine import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    SOLAR_CONSTANT_W_M2,
    STEFAN_BOLTZMANN,
    SolarObservables,
    __provenance__,
    solar_observables_reference,
    question_diagnostics,
    solar_question_portfolio,
    monte_carlo_question_stability,
    pillar235_solar_open_questions_report,
)


def test_provenance_pillar_number():
    assert __provenance__["pillar"] == 235
    assert __provenance__["title"] == "Solar Physics Open Questions Engine"
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_framework_constants():
    assert N_W == 5
    assert K_CS == 74
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_physical_constants_positive():
    assert SOLAR_CONSTANT_W_M2 > 1000
    assert STEFAN_BOLTZMANN > 0


def test_reference_observables_instance():
    obs = solar_observables_reference()
    assert isinstance(obs, SolarObservables)
    assert obs.corona_temp_k > obs.photosphere_temp_k


def test_question_diagnostics_returns_12_items():
    rows = question_diagnostics()
    assert len(rows) == 12


def test_question_diagnostics_have_required_keys():
    row = question_diagnostics()[0]
    for key in ["question", "diagnostic", "derived_solution", "epistemic_status", "falsification_condition"]:
        assert key in row


def test_each_closure_score_in_unit_interval():
    for row in question_diagnostics():
        score = row["diagnostic"]["closure_score"]
        assert 0.0 <= score <= 1.0


def test_portfolio_shape():
    p = solar_question_portfolio()
    assert p["n_questions"] == 12
    assert 0 <= p["mean_closure_score"] <= 1
    assert 0 <= p["median_closure_score"] <= 1
    assert 0 <= p["minimum_closure_score"] <= 1


def test_portfolio_weakest_question_is_present():
    rows = question_diagnostics()
    names = {r["question"] for r in rows}
    p = solar_question_portfolio()
    assert p["weakest_question"] in names


def test_higher_forcing_improves_faint_young_sun_score():
    base = solar_observables_reference()
    low = SolarObservables(**{**base.__dict__, "greenhouse_forcing_wm2": 10.0})
    high = SolarObservables(**{**base.__dict__, "greenhouse_forcing_wm2": 120.0})

    def get_score(obs):
        for row in question_diagnostics(obs):
            if row["question"] == "Faint young Sun paradox":
                return row["diagnostic"]["closure_score"]
        raise AssertionError("Question not found")

    assert get_score(high) >= get_score(low)


def test_worse_sep_spectrum_match_reduces_sep_score():
    base = solar_observables_reference()
    near = SolarObservables(**{**base.__dict__, "sep_observed_spectral_index": 2.3})
    far = SolarObservables(**{**base.__dict__, "sep_observed_spectral_index": 4.5})

    def get_sep_score(obs):
        for row in question_diagnostics(obs):
            if row["question"].startswith("Particle acceleration"):
                return row["diagnostic"]["closure_score"]
        raise AssertionError("Question not found")

    assert get_sep_score(near) > get_sep_score(far)


def test_invalid_damping_fraction_raises():
    obs = SolarObservables(alfven_damping_fraction=1.5)
    with pytest.raises(ValueError):
        question_diagnostics(obs)


def test_invalid_reconnection_rate_raises():
    obs = SolarObservables(reconnection_rate=-0.1)
    with pytest.raises(ValueError):
        question_diagnostics(obs)


def test_invalid_mach_raises():
    obs = SolarObservables(sep_shock_mach=1.0)
    with pytest.raises(ValueError):
        question_diagnostics(obs)


def test_monte_carlo_shape_and_keys():
    mc = monte_carlo_question_stability(samples=30, relative_sigma=0.03, seed=42)
    assert mc["samples"] == 30
    assert len(mc["per_question"]) == 12
    q_row = next(iter(mc["per_question"].values()))
    for key in ["mean", "std", "min", "max"]:
        assert key in q_row


def test_monte_carlo_reproducible_with_same_seed():
    mc1 = monte_carlo_question_stability(samples=20, relative_sigma=0.02, seed=99)
    mc2 = monte_carlo_question_stability(samples=20, relative_sigma=0.02, seed=99)
    assert mc1 == mc2


def test_monte_carlo_invalid_samples_raises():
    with pytest.raises(ValueError):
        monte_carlo_question_stability(samples=0)


def test_integrated_report_contains_sections():
    report = pillar235_solar_open_questions_report(samples=20, relative_sigma=0.02, seed=7)
    for key in ["diagnostics", "portfolio", "stability", "status", "falsification_condition"]:
        assert key in report
    assert len(report["diagnostics"]) == 12
    assert report["portfolio"]["n_questions"] == 12
