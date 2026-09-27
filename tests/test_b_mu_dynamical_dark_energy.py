# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.b_mu_dynamical_dark_energy import (
    evaluate_gamma_models_for_wa,
    gamma_model_logarithmic,
    gamma_model_powerlaw,
    gamma_model_scaling,
)


def test_gamma_models_are_finite_positive():
    for a in (1.0, 0.5, 0.1, 0.01):
        assert gamma_model_scaling(a) > 0.0
        assert gamma_model_powerlaw(a) > 0.0
        assert gamma_model_logarithmic(a) > 0.0


def test_gamma_model_wa_selection():
    out = evaluate_gamma_models_for_wa()
    assert out["best_model"] == "powerlaw_n_-0.5"
    assert abs(out["best_wa"] - out["target_wa"]) < 0.2
    assert out["status"] == "FITTED"


def test_candidate_scores_are_explicit():
    out = evaluate_gamma_models_for_wa()
    c = out["candidates"]
    assert c["scaling_1_over_a"] < c["powerlaw_n_-0.5"] < 0.0
    assert abs(c["logarithmic"]) < 0.5
