# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/p28_lambda_10d_closure.py."""
from __future__ import annotations

import pytest

from src.core.p28_lambda_10d_closure import (
    BASE_N_FLUX,
    DUAL_FLUX_MULTIPLICITY,
    REQUIRED_N_FLUX_MIN,
    effective_flux_sufficiency,
    explicit_vacuum_selection,
    p28_10d_closure_report,
)


def test_flux_sufficiency_reaches_threshold():
    report = effective_flux_sufficiency()
    assert report["base_n_flux"] == BASE_N_FLUX
    assert report["dual_flux_multiplicity"] == DUAL_FLUX_MULTIPLICITY
    assert report["effective_n_flux"] == BASE_N_FLUX * DUAL_FLUX_MULTIPLICITY
    assert report["effective_n_flux"] >= REQUIRED_N_FLUX_MIN
    assert report["meets_bp_threshold"] is True
    assert report["spacing_below_lambda_obs"] is True


def test_flux_sufficiency_input_validation():
    with pytest.raises(ValueError, match="base_n_flux must be positive, got 0"):
        effective_flux_sufficiency(base_n_flux=0)
    with pytest.raises(ValueError, match="dual_flux_multiplicity must be positive, got 0"):
        effective_flux_sufficiency(dual_flux_multiplicity=0)


def test_explicit_vacuum_selection_is_unique():
    report = explicit_vacuum_selection()
    assert report["explicit_selection_pass"] is True
    summary = report["selection_summary"]
    assert summary["status"] == "UNIQUE_UV_FLUX_SELECTION"
    assert summary["unique_flux_selected_n_w"] == 5
    assert summary["surviving_candidates"] == [5]


def test_p28_10d_closure_report_is_promotion_ready():
    report = p28_10d_closure_report()
    assert report["parameter"] == "P28"
    assert report["closure_dimension"] == "10D"
    assert report["effective_n_flux"] >= REQUIRED_N_FLUX_MIN
    assert report["first_principles_derivation_pass"] is True
    assert report["first_principles_lambda_pred_mplanck4"] > 0.0
    assert report["first_principles_topological_partition"] == 518
    assert report["first_principles_status"] == "P28_FIRST_PRINCIPLES_DERIVED"
    assert report["all_closure_gates_pass"] is True
    assert report["promotion_ready"] is True
    assert report["status"] == "P28_10D_CLOSURE_READY"
