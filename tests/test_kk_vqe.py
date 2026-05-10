# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_kk_vqe.py
==========================
Combined KK-VQE tests covering both backends:
  Part A — src/core/kk_vqe.py  (1-D Sturm-Liouville VQE on z-grid)
  Part B — src/quantum/kk_vqe.py (qubit Hamiltonian + CNOT ansatz VQE)
"""

from __future__ import annotations

import math
import numpy as np
import pytest

# Part A imports
from src.core.kk_vqe import (
    kk_hamiltonian as core_kk_hamiltonian,
    kk_spectrum,
    vqe_ground_state,
    kk_mass_ratio_check,
    kk_tower_summary,
    KK_N_W,
    KK_K_CS,
    VQE_CONVERGENCE_TOL,
)

# Part B imports
from src.quantum.kk_vqe import (
    kk_hamiltonian as quantum_kk_hamiltonian,
    ansatz_circuit,
    vqe_kk,
    VQEResult,
    KK_N1,
    KK_N2,
    KK_KCS,
    KK_R_C,
)


# ===========================================================================
# Part A: src/core/kk_vqe.py  (Sturm-Liouville z-grid VQE)
# ===========================================================================

class TestCoreKKHamiltonian:
    def test_returns_matrix_and_grid(self):
        H, z = core_kk_hamiltonian(N_grid=32)
        assert H.shape == (32, 32)
        assert len(z) == 32

    def test_matrix_is_symmetric(self):
        H, _ = core_kk_hamiltonian(N_grid=32)
        assert np.allclose(H, H.T, atol=1e-12)

    def test_diagonal_positive(self):
        H, _ = core_kk_hamiltonian(N_grid=32)
        assert np.all(np.diag(H) > 0)

    def test_grid_in_open_interval(self):
        _, z = core_kk_hamiltonian(N_grid=64)
        assert z[0] > 0
        assert z[-1] < np.pi

    def test_custom_n_w(self):
        H1, _ = core_kk_hamiltonian(N_grid=32, n_w=5)
        H2, _ = core_kk_hamiltonian(N_grid=32, n_w=3)
        assert not np.allclose(H1, H2)


class TestKKSpectrum:
    def test_returns_n_modes(self):
        assert len(kk_spectrum(N_modes=4)) == 4

    def test_eigenvalues_positive(self):
        assert np.all(kk_spectrum(N_modes=3) > 0)

    def test_eigenvalues_sorted_ascending(self):
        ev = kk_spectrum(N_modes=4)
        assert np.all(np.diff(ev) > 0)

    def test_canonical_n_w_5(self):
        ev = kk_spectrum(N_modes=2, n_w=KK_N_W, k_cs=KK_K_CS)
        assert ev[0] < ev[1]

    def test_higher_n_w_shifts_spectrum(self):
        ev5 = kk_spectrum(N_modes=1, n_w=5)
        ev7 = kk_spectrum(N_modes=1, n_w=7)
        assert ev5[0] != pytest.approx(ev7[0], rel=0.01)

    def test_single_mode(self):
        assert len(kk_spectrum(N_modes=1)) == 1


class TestCoreVQEGroundState:
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
        assert self.result["E_variational"] >= self.result["E_exact"] - 1e-6

    def test_exact_energy_positive(self):
        assert self.result["E_exact"] > 0

    def test_ansatz_param_positive(self):
        assert self.result["ansatz_param"] > 0

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


# ===========================================================================
# Part B: src/quantum/kk_vqe.py  (qubit Hamiltonian + CNOT-ansatz VQE)
# ===========================================================================

def _exact_ground_energy(r_c, n_qubits, n1, n2, k_cs, include_braid=True):
    H = quantum_kk_hamiltonian(r_c=r_c, n_qubits=n_qubits, n1=n1, n2=n2,
                               k_cs=k_cs, include_braid=include_braid)
    return float(np.linalg.eigh(H)[0][0])


class TestQuantumKKHamiltonian:
    def test_shape(self):
        assert quantum_kk_hamiltonian(n_qubits=3).shape == (8, 8)

    def test_shape_4qubits(self):
        assert quantum_kk_hamiltonian(n_qubits=4).shape == (16, 16)

    def test_symmetry(self):
        H = quantum_kk_hamiltonian(n_qubits=3)
        np.testing.assert_allclose(H, H.T, atol=1e-14)

    def test_diagonal_free_spectrum(self):
        r_c = KK_R_C
        H = quantum_kk_hamiltonian(r_c=r_c, n_qubits=3, include_braid=False)
        for n in range(8):
            assert H[n, n] == pytest.approx(n ** 2 / r_c ** 2, rel=1e-10)

    def test_zero_mode_energy(self):
        assert quantum_kk_hamiltonian(n_qubits=3)[0, 0] == pytest.approx(0.0, abs=1e-14)

    def test_braid_adds_off_diagonal(self):
        H_free = quantum_kk_hamiltonian(n_qubits=3, include_braid=False)
        H_braid = quantum_kk_hamiltonian(n_qubits=3, include_braid=True)
        diff = H_braid - H_free
        n1, n2 = KK_N1, KK_N2
        assert abs(diff[n1, n2]) > 0
        diff[n1, n2] = diff[n2, n1] = 0
        np.testing.assert_allclose(diff, 0.0, atol=1e-14)

    def test_braid_mixing_formula(self):
        r_c, n1, n2, k_cs = 5.0, 2, 3, 10
        H = quantum_kk_hamiltonian(r_c=r_c, n_qubits=4, n1=n1, n2=n2, k_cs=k_cs)
        assert H[n1, n2] == pytest.approx(2.0 * n1 * n2 / (k_cs * r_c ** 2), rel=1e-12)

    def test_error_on_mode_exceeding_dim(self):
        with pytest.raises(ValueError, match="exceed Hilbert space"):
            quantum_kk_hamiltonian(n_qubits=2, n1=5, n2=7, include_braid=True)

    def test_positive_semidefinite_without_braid(self):
        eigs = np.linalg.eigvalsh(quantum_kk_hamiltonian(n_qubits=3, include_braid=False))
        assert np.all(eigs >= -1e-12)

    def test_canonical_constants(self):
        assert KK_N1 == 5
        assert KK_N2 == 7
        assert KK_KCS == 74
        assert KK_R_C == pytest.approx(math.sqrt(74), rel=1e-12)


class TestAnsatzCircuit:
    N_QUBITS = 2
    N_LAYERS = 1

    def _n_params(self, n_qubits=None, n_layers=None):
        nq = n_qubits or self.N_QUBITS
        nl = n_layers or self.N_LAYERS
        return nq * (nl + 1)

    def test_shape(self):
        U = ansatz_circuit(np.zeros(self._n_params()), self.N_QUBITS, self.N_LAYERS)
        assert U.shape == (4, 4)

    def test_unitarity(self):
        rng = np.random.default_rng(0)
        theta = rng.uniform(-math.pi, math.pi, self._n_params())
        U = ansatz_circuit(theta, self.N_QUBITS, self.N_LAYERS)
        np.testing.assert_allclose(U @ U.conj().T, np.eye(4, dtype=complex), atol=1e-10)

    def test_unitarity_3qubits(self):
        nq, nl = 3, 2
        rng = np.random.default_rng(1)
        theta = rng.uniform(-math.pi, math.pi, nq * (nl + 1))
        U = ansatz_circuit(theta, nq, nl)
        np.testing.assert_allclose(U @ U.conj().T, np.eye(8, dtype=complex), atol=1e-10)

    def test_wrong_theta_length_raises(self):
        with pytest.raises(ValueError, match="theta has"):
            ansatz_circuit(np.zeros(5), self.N_QUBITS, self.N_LAYERS)

    def test_different_params_give_different_unitaries(self):
        U1 = ansatz_circuit(np.zeros(self._n_params()), self.N_QUBITS, self.N_LAYERS)
        U2 = ansatz_circuit(np.ones(self._n_params()) * 0.5, self.N_QUBITS, self.N_LAYERS)
        assert not np.allclose(U1, U2)


class TestQuantumVQEGroundState:
    N_QUBITS = 3
    N_LAYERS = 3
    TOL = 0.1

    def test_vqe_returns_result(self):
        assert isinstance(vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS, seed=0), VQEResult)

    def test_vqe_ground_energy_near_exact(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS, seed=0)
        exact = result.exact_energies[0]
        assert result.ground_energy >= exact - 1e-6
        if abs(exact) > 1e-10:
            assert abs(result.ground_energy - exact) / abs(exact) <= self.TOL

    def test_variational_principle(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS, seed=42)
        assert result.ground_energy >= result.exact_energies[0] - 1e-6

    def test_ground_state_normalised(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS, seed=0)
        assert np.linalg.norm(result.ground_state) == pytest.approx(1.0, abs=1e-6)

    def test_ground_state_energy_consistent(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS, seed=0)
        H = quantum_kk_hamiltonian(n_qubits=self.N_QUBITS)
        psi = result.ground_state
        assert float(np.real(psi.conj() @ H @ psi)) == pytest.approx(result.ground_energy, rel=1e-6)

    def test_fidelity_nonnegative(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS, seed=0)
        assert 0.0 <= result.fidelity <= 1.0 + 1e-8


class TestQuantumPhysicalConsistency:
    def test_braid_lowers_ground_energy(self):
        r_c = 5.0
        e_free = _exact_ground_energy(r_c, 4, 2, 3, 10, include_braid=False)
        e_braid = _exact_ground_energy(r_c, 4, 2, 3, 10, include_braid=True)
        assert e_braid <= e_free + 1e-12

    def test_zero_mode_always_zero(self):
        for nq in [2, 3, 4]:
            H = quantum_kk_hamiltonian(n_qubits=nq, include_braid=False)
            assert H[0, 0] == pytest.approx(0.0, abs=1e-14)

    def test_r_c_scaling(self):
        r_c = 3.0
        H = quantum_kk_hamiltonian(r_c=r_c, n_qubits=3, include_braid=False)
        assert H[1, 1] == pytest.approx(1.0 / r_c ** 2, rel=1e-12)

    def test_canonical_kk_rcc(self):
        assert KK_R_C ** 2 == pytest.approx(KK_KCS, rel=1e-12)

    def test_braid_level_5_7_74(self):
        H = quantum_kk_hamiltonian()
        rho = 2.0 * KK_N1 * KK_N2 / KK_KCS
        k_mix = rho / KK_R_C ** 2
        assert H[KK_N1, KK_N2] == pytest.approx(k_mix, rel=1e-12)

    def test_hamiltonian_real(self):
        H = quantum_kk_hamiltonian()
        assert np.isrealobj(H) or np.allclose(H.imag, 0)
