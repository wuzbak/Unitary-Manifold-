# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/p28_lambda_first_principles.py."""
from __future__ import annotations

import math

from src.core.p28_lambda_first_principles import (
    DUAL_FLUX_MULTIPLICITY,
    SHADOW_BRANCH_OFFSET,
    p28_first_principles_components,
    p28_first_principles_report,
)


def test_components_partition_structure():
    d = p28_first_principles_components()
    assert d["dual_flux_multiplicity"] == DUAL_FLUX_MULTIPLICITY
    assert d["effective_flux_channels"] == d["n_flux_base"] * DUAL_FLUX_MULTIPLICITY
    assert d["shadow_branch_weight"] == d["n_w"] + SHADOW_BRANCH_OFFSET
    assert d["topological_partition"] == d["effective_flux_channels"] * d["shadow_branch_weight"]
    assert d["topological_partition"] == 518


def test_components_use_no_observational_seed_inputs():
    d = p28_first_principles_components()
    assert d["axiomzero_pdg_inputs"] == []


def test_lambda_prediction_is_positive_and_finite():
    d = p28_first_principles_components()
    assert d["lambda_pred_mplanck4"] > 0.0
    assert math.isfinite(d["lambda_pred_log10"])


def test_report_derivation_pass_and_status():
    report = p28_first_principles_report()
    assert report["derivation_pass"] is True
    assert report["status"] == "P28_FIRST_PRINCIPLES_DERIVED"
    assert report["components"]["c_uv_consistency_gate_pass"] is True
    assert report["components"]["c_uv_decision_closed"] is True


def test_report_prediction_is_close_to_observed():
    report = p28_first_principles_report()
    ratio = report["comparison_only"]["pred_to_obs_ratio"]
    assert 0.5 <= ratio <= 2.0
    assert report["comparison_only"]["abs_log10_residual"] < 0.31  # within ~factor 2
