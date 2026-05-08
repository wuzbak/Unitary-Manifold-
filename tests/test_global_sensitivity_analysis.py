# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Post-MAS Track 2 global sensitivity analysis."""

from __future__ import annotations

from src.core.global_sensitivity_analysis import (
    DEFAULT_PARAMETER_BOUNDS,
    saltelli_sobol_indices,
    core_solver_model,
    ranked_influence_table,
    track2_gsa_artifact,
)


def test_default_bounds_include_two_parameters():
    assert "phi0_scale" in DEFAULT_PARAMETER_BOUNDS
    assert "cs_scale" in DEFAULT_PARAMETER_BOUNDS


def test_sobol_output_structure():
    result = saltelli_sobol_indices(core_solver_model, n_samples=128, seed=7)
    assert "outputs" in result
    assert "n_s" in result["outputs"]
    assert "r_braided" in result["outputs"]
    assert "w_KK" in result["outputs"]


def test_ranked_influence_table_sorted():
    result = saltelli_sobol_indices(core_solver_model, n_samples=128, seed=7)
    ranked = ranked_influence_table(result)
    for out_name, rows in ranked.items():
        assert len(rows) >= 2
        assert rows[0]["total_effect"] >= rows[1]["total_effect"]


def test_track2_artifact_pass():
    artifact = track2_gsa_artifact(n_samples=128, seed=7)
    assert artifact["track"] == "T2"
    assert artifact["robustness_verdict"] == "PASS"
    assert not artifact["critical_failures"]

