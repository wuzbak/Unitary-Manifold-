# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 276 — T3 ADM Momentum-Constraint Sector with Radion Shift."""
from __future__ import annotations

import math

import pytest

from src.core.pillar276_t3_momentum_constraint_sector import (
    ADJACENCY_TRACK_LABEL,
    DEFAULT_BETA0,
    DEFAULT_DT,
    DEFAULT_ETA,
    DEFAULT_OMEGA,
    DEFAULT_STEPS,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    TWO_SECTOR_ACCEPTANCE_THRESHOLD,
    evolve_two_sector,
    next_open_sector,
    radion_shift_derivative,
    radion_shift_vector,
    separation_guard,
    two_sector_closure_assessment,
    two_sector_rhs,
)


def test_identity_and_separation():
    assert PILLAR_NUMBER == 276
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    g = separation_guard()
    assert g["is_hardgate"] is False
    assert g["extends_reduced_sector_only"] is True


def test_radion_shift_vector_zero_at_origin():
    assert radion_shift_vector(0.0) == pytest.approx(0.0)


def test_radion_shift_decays_at_late_times():
    early = abs(radion_shift_vector(0.5))
    late = abs(radion_shift_vector(20.0))
    assert late < early or late < 1.0e-6


def test_radion_shift_input_validation():
    with pytest.raises(ValueError):
        radion_shift_vector(1.0, eta=-0.1)
    with pytest.raises(ValueError):
        radion_shift_derivative(1.0, eta=-0.1)


def test_radion_shift_derivative_at_origin_equals_beta0_omega():
    # ∂_t β(0) = β₀ · ω
    val = radion_shift_derivative(0.0)
    assert val == pytest.approx(DEFAULT_BETA0 * DEFAULT_OMEGA)


def test_two_sector_rhs_zero_shift_reduces_to_pure_damping():
    rhs = two_sector_rhs(h_proxy=1e-10, m_proxy=1e-10, shift=0.0, shift_dot=0.0)
    # Pure damping: both derivatives must be strictly negative
    assert rhs["d_h"] < 0.0
    assert rhs["d_m"] < 0.0


def test_two_sector_rhs_nonzero_shift_couples_sectors():
    rhs_zero = two_sector_rhs(1e-10, 1e-10, 0.0, 0.0)
    rhs_active = two_sector_rhs(1e-10, 1e-10, 1e-3, 1.0)
    # Coupling changes the derivatives by a measurable amount
    assert rhs_active["d_h"] != rhs_zero["d_h"]
    assert rhs_active["d_m"] != rhs_zero["d_m"]


def test_evolve_two_sector_default_keys():
    e = evolve_two_sector()
    for key in (
        "steps",
        "dt",
        "trajectory_length",
        "final_h",
        "final_m",
        "final_metric",
        "max_metric",
        "monotone_decay",
        "metric_series_first_last",
    ):
        assert key in e
    assert e["steps"] == DEFAULT_STEPS
    assert e["dt"] == DEFAULT_DT
    assert e["trajectory_length"] == DEFAULT_STEPS + 1


def test_evolve_input_validation():
    with pytest.raises(ValueError):
        evolve_two_sector(steps=0)
    with pytest.raises(ValueError):
        evolve_two_sector(dt=0.0)


def test_max_metric_under_acceptance_threshold():
    e = evolve_two_sector()
    assert e["max_metric"] <= TWO_SECTOR_ACCEPTANCE_THRESHOLD
    assert e["final_metric"] <= TWO_SECTOR_ACCEPTANCE_THRESHOLD


def test_constraint_metric_decays_or_stays_bounded():
    e = evolve_two_sector()
    first, last = e["metric_series_first_last"]
    # The system must not blow up: last ≤ first within numerical tolerance
    assert last <= first + 1e-30


def test_two_sector_closure_assessment_pass():
    r = two_sector_closure_assessment()
    assert r["verdict"] == "PASS"
    assert r["status"] == "CLOSED_TWO_SECTORS"
    assert r["closure_blocker"] == "none_two_sectors_complete"
    assert r["acceptance_threshold"] == TWO_SECTOR_ACCEPTANCE_THRESHOLD
    assert r["max_metric"] <= TWO_SECTOR_ACCEPTANCE_THRESHOLD


def test_two_sector_assessment_fails_below_initial_amplitude_threshold():
    # If the threshold is set absurdly tight (below initial constraint
    # amplitude 1e-12), the assessment must report tension, not silently pass.
    r = two_sector_closure_assessment(threshold=1.0e-15)
    assert r["verdict"] == "TENSION"
    assert r["status"] == "PARTIALLY_CLOSED_TWO_SECTORS"


def test_next_open_sector_named():
    n = next_open_sector()
    assert n["id"] == "T3_INHOMOGENEOUS_LAPSE"
    assert "ADM_FULL_DYNAMICAL_5D" in n["remaining_open_foundational_boundary"]


def test_separation_guard_in_full_report():
    r = two_sector_closure_assessment()
    g = r["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False


def test_shift_parameters_match_defaults():
    r = two_sector_closure_assessment()
    p = r["shift_parameters"]
    assert p["beta0"] == DEFAULT_BETA0
    assert p["omega"] == DEFAULT_OMEGA
    assert p["eta"] == DEFAULT_ETA
