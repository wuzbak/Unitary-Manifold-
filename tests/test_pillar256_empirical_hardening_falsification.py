# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 256 — Empirical Hardening & Falsification."""

from __future__ import annotations

import pytest

from src.core.pillar256_empirical_hardening_falsification import (
    ADJACENCY_TRACK_LABEL,
    C_S,
    FERMILAB_A_MU_EXP_1E11,
    FERMILAB_A_MU_SIGMA_1E11,
    K_CS,
    N_W,
    OMEGA_LAMBDA_TARGET,
    PLANCK_R_UPPER_95CL,
    PROTON_RADIUS_CREMA_FM,
    PROTON_RADIUS_LEGACY_FM,
    R_FALSIFICATION_WINDOW,
    R_PREDICTION,
    derive_muon_g2_from_5d_constraint,
    tensor_to_scalar_prediction_test,
    vacuum_catastrophe_resolution_test,
    proton_radius_puzzle_test,
    black_box_falsification_threshold,
    pillar256_empirical_hardening_report,
)


def test_constants_and_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert N_W == 5
    assert K_CS == 74
    assert C_S == pytest.approx(12.0 / 37.0)
    assert FERMILAB_A_MU_EXP_1E11 == pytest.approx(116_592_059.0)
    assert FERMILAB_A_MU_SIGMA_1E11 == pytest.approx(22.0)


def test_muon_g2_records_tension_and_refinement_requirement():
    row = derive_muon_g2_from_5d_constraint()
    assert row["observable"] == "a_mu"
    assert row["sigma_distance"] > 5.0
    assert row["verdict"] == "REFINE_LEPTON_CONSTRAINT_REQUIRED"
    assert "5σ+ tension" in row["explanation"]


def test_tensor_to_scalar_prediction_is_fixed_and_falsifiable():
    row = tensor_to_scalar_prediction_test()
    lo, hi = R_FALSIFICATION_WINDOW

    assert row["observable"] == "r"
    assert row["predicted_r"] == pytest.approx(R_PREDICTION)
    assert row["predicted_r"] < PLANCK_R_UPPER_95CL
    assert row["currently_allowed"] is True
    assert row["falsification_window"]["min"] == pytest.approx(lo)
    assert row["falsification_window"]["max"] == pytest.approx(hi)
    assert row["falsified_if_litebird_reports_zero"] is True


def test_vacuum_catastrophe_resolution_hits_120_order_and_omega_target():
    row = vacuum_catastrophe_resolution_test()

    assert row["observable"] == "Lambda"
    assert row["passes_120_order_requirement"] is True
    assert row["hierarchy_orders_resolved"] >= 120.0
    assert row["omega_lambda_derived"] == pytest.approx(OMEGA_LAMBDA_TARGET, abs=0.01)
    assert row["rho_lambda_observed_mev4"] == pytest.approx(2.3**4)


def test_proton_radius_derivation_is_not_curve_fit_and_prefers_crema():
    row = proton_radius_puzzle_test()

    assert row["observable"] == "proton_charge_radius"
    assert row["derived_radius_fm"] == pytest.approx(PROTON_RADIUS_CREMA_FM, abs=0.002)
    assert row["closer_to_crema_than_legacy"] is True
    assert abs(row["derived_radius_fm"] - PROTON_RADIUS_CREMA_FM) < abs(
        row["derived_radius_fm"] - PROTON_RADIUS_LEGACY_FM
    )
    assert row["no_data_tuning"] is True


def test_black_box_falsification_threshold_links_required_file():
    row = black_box_falsification_threshold()
    assert row["critical_failure_file"] == "9-INFRASTRUCTURE/CRITICAL_FAILURE.md"
    assert row["count_expected"] == 3


def test_integrated_report_contains_all_five_stress_tests():
    report = pillar256_empirical_hardening_report()
    assert report["pillar"] == 256
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL

    tests = report["stress_tests"]
    for key in (
        "muon_g2",
        "tensor_to_scalar",
        "vacuum_catastrophe",
        "proton_radius",
        "black_box_falsification",
    ):
        assert key in tests

    verdict = report["hardening_verdict"]
    assert verdict["lepton_constraint_refinement_required"] is True
    assert verdict["r_prediction_committed"] is True
    assert verdict["vacuum_hierarchy_resolved"] is True
    assert verdict["anti_curve_fit_guard_passed"] is True
