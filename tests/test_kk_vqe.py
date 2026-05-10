# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_kk_vqe.py
=========================
Tests for the KK mode VQE (Variational Quantum Eigensolver) module.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.core.kk_vqe import (
    kk_hamiltonian,
    kk_spectrum,
    vqe_ground_state,
    kk_mass_ratio_check,
    kk_tower_summary,
    KK_N_W,
    KK_K_CS,
    VQE_CONVERGENCE_TOL,
)


class TestKKHamiltonian:
    def test_returns_matrix_and_grid(self):
        H, z = kk_hamiltonian(N_grid=32)
        assert H.shape == (32, 32)
        assert len(z) == 32

    def test_matrix_is_symmetric(self):
        H, _ = kk_hamiltonian(N_grid=32)
        assert np.allclose(H, H.T, atol=1e-12)

    def test_diagonal_positive(self):
        H, _ = kk_hamiltonian(N_grid=32)
        assert np.all(np.diag(H) > 0)

    def test_grid_in_open_interval(self):
        _, z = kk_hamiltonian(N_grid=64)
        assert z[0] > 0
        assert z[-1] < np.pi

    def test_custom_n_w(self):
        H1, _ = kk_hamiltonian(N_grid=32, n_w=5)
        H2, _ = kk_hamiltonian(N_grid=32, n_w=3)
        assert not np.allclose(H1, H2)


class TestKKSpectrum:
    def test_returns_n_modes(self):
        ev = kk_spectrum(N_modes=4)
        assert len(ev) == 4

    def test_eigenvalues_positive(self):
        ev = kk_spectrum(N_modes=3)
        assert np.all(ev > 0)

    def test_eigenvalues_sorted_ascending(self):
        ev = kk_spectrum(N_modes=4)
        assert np.all(np.diff(ev) > 0)

    def test_canonical_n_w_5(self):
        ev = kk_spectrum(N_modes=2, n_w=KK_N_W, k_cs=KK_K_CS)
        assert ev[0] < ev[1]

    def test_higher_n_w_shifts_spectrum(self):
        ev5 = kk_spectrum(N_modes=1, n_w=5)
        ev7 = kk_spectrum(N_modes=1, n_w=7)
        # Different winding numbers give different ground-state energies
        assert ev5[0] != pytest.approx(ev7[0], rel=0.01)

    def test_single_mode(self):
        ev = kk_spectrum(N_modes=1)
        assert len(ev) == 1


class TestVQEGroundState:
    def setup_method(self):
        self.result = vqe_ground_state(N_grid=64)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_status_pass(self):
        assert self.result["status"] == "PASS", (
            f"VQE gap {self.result['gap_pct']:.2f}% exceeds tolerance"
        )

    def test_gap_below_tolerance(self):
        assert self.result["gap_pct"] < VQE_CONVERGENCE_TOL * 100

    def test_variational_upper_bound(self):
        """Variational energy must be >= exact (Rayleigh-Ritz variational principle)."""
        assert self.result["E_variational"] >= self.result["E_exact"] - 1e-6

    def test_exact_energy_positive(self):
        assert self.result["E_exact"] > 0

    def test_sigma_opt_positive(self):
        assert self.result["sigma_opt"] > 0

    def test_n_w_echoed(self):
        assert self.result["n_w"] == KK_N_W

    def test_k_cs_echoed(self):
        assert self.result["k_cs"] == KK_K_CS


class TestKKMassRatioCheck:
    def setup_method(self):
        self.result = kk_mass_ratio_check()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_status_not_fail(self):
        assert self.result["status"] in ("PASS", "WARN")

    def test_mass_hierarchy(self):
        """m²_1 > m²_0 (KK tower is ordered)."""
        assert self.result["m1_sq"] > self.result["m0_sq"]

    def test_ratio_greater_than_one(self):
        assert self.result["ratio_10"] > 1.0

    def test_m2_greater_than_m1(self):
        assert self.result["m2_sq"] > self.result["m1_sq"]

    def test_n_w_echoed(self):
        assert self.result["n_w"] == KK_N_W


class TestKKTowerSummary:
    def setup_method(self):
        self.result = kk_tower_summary()

    def test_overall_pass(self):
        assert self.result["overall_pass"] is True

    def test_has_five_eigenvalues(self):
        assert len(self.result["eigenvalues"]) == 5

    def test_eigenvalues_positive(self):
        assert all(ev > 0 for ev in self.result["eigenvalues"])

    def test_eigenvalues_ascending(self):
        evs = self.result["eigenvalues"]
        assert all(evs[i] < evs[i + 1] for i in range(len(evs) - 1))

    def test_vqe_present(self):
        assert "vqe" in self.result

    def test_mass_ratio_present(self):
        assert "mass_ratio" in self.result
