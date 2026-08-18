# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 718 — KK VQE hardening."""
from __future__ import annotations

import math

import pytest

from src.quantum.pillar718_kk_vqe_hardening import (
    C_S,
    K_CS,
    N_W,
    PILLAR_NUMBER,
    THETA_TRIAL_HF,
    U_OVER_T_KK,
    kk_vqe_params,
    vqe_fidelity_estimate,
    vqe_hardening_checks,
)


PARAMS = kk_vqe_params()
FIDELITY = vqe_fidelity_estimate()
CHECKS = vqe_hardening_checks()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 718

    def test_core_constants(self) -> None:
        assert N_W == 5
        assert K_CS == 74
        assert C_S == pytest.approx(12.0 / 37.0, rel=1e-12)
        assert 45.5 < U_OVER_T_KK < 45.7


class TestParams:
    def test_layer_depth_matches_winding(self) -> None:
        assert PARAMS["n_layers"] == PARAMS["n_w"] == 5

    def test_theta_opt_formula(self) -> None:
        assert PARAMS["theta_opt"] == pytest.approx(math.atan(12.0 / 37.0), rel=1e-12)

    def test_theta_trial_is_hf_seed(self) -> None:
        assert PARAMS["theta_trial"] == pytest.approx(THETA_TRIAL_HF, rel=1e-12)

    def test_symmetry_sector(self) -> None:
        assert PARAMS["symmetry_sector"] == "U(1)_particle_number_conserving"


class TestFidelityEstimate:
    def test_fidelity_formula(self) -> None:
        expected = math.cos(math.atan(12.0 / 37.0) - math.pi / 6.0) ** 2
        assert FIDELITY["fidelity"] == pytest.approx(expected, rel=1e-12)

    def test_fidelity_high(self) -> None:
        assert FIDELITY["fidelity"] > 0.95
        assert FIDELITY["fidelity_regime"] == "HIGH_FIDELITY"

    def test_overlap_amplitude(self) -> None:
        assert 0.0 <= FIDELITY["overlap_amplitude"] <= 1.0

    def test_custom_theta_trial_changes_delta(self) -> None:
        alt = vqe_fidelity_estimate(theta_trial=0.0)
        assert alt["delta_theta"] != pytest.approx(FIDELITY["delta_theta"], rel=1e-12)


class TestHardeningChecks:
    def test_symmetry_check(self) -> None:
        assert CHECKS["u1_particle_number_conservation"] is True

    def test_depth_check(self) -> None:
        assert CHECKS["depth_matches_braid_winding"] is True
        assert CHECKS["n_layers"] == 5

    def test_convergence_check(self) -> None:
        assert CHECKS["converges_within_1pct"] is True
        assert CHECKS["relative_energy_error"] < 0.01

    def test_vqe_energy_close_to_exact(self) -> None:
        diff = abs(CHECKS["e_vqe_per_site"] - CHECKS["e_exact_per_site"])
        assert diff / abs(CHECKS["e_exact_per_site"]) == pytest.approx(
            CHECKS["relative_energy_error"],
            rel=1e-12,
        )

    def test_all_checks_pass(self) -> None:
        assert CHECKS["all_checks_pass"] is True

    def test_epistemic_status(self) -> None:
        assert CHECKS["epistemic_status"] == "ANALYTICAL_ESTIMATE"
