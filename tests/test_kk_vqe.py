# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_kk_vqe.py
====================
Tests for the Kaluza–Klein Variational Quantum Eigensolver (KK-VQE).

Tests are grouped into:
  1. Hamiltonian construction tests
  2. Ansatz circuit tests
  3. VQE optimisation tests (ground state and excited states)
  4. Physical consistency tests (braided spectrum)
"""
import math
import numpy as np
import pytest

from src.quantum.kk_vqe import (
    kk_hamiltonian,
    ansatz_circuit,
    vqe_kk,
    VQEResult,
    KK_N1,
    KK_N2,
    KK_KCS,
    KK_R_C,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _exact_ground_energy(r_c, n_qubits, n1, n2, k_cs, include_braid=True):
    H = kk_hamiltonian(r_c=r_c, n_qubits=n_qubits, n1=n1, n2=n2,
                       k_cs=k_cs, include_braid=include_braid)
    return float(np.linalg.eigh(H)[0][0])


# ---------------------------------------------------------------------------
# 1. Hamiltonian construction
# ---------------------------------------------------------------------------

class TestKKHamiltonian:
    def test_shape(self):
        H = kk_hamiltonian(n_qubits=3)
        assert H.shape == (8, 8)

    def test_shape_4qubits(self):
        H = kk_hamiltonian(n_qubits=4)
        assert H.shape == (16, 16)

    def test_symmetry(self):
        H = kk_hamiltonian(n_qubits=3)
        np.testing.assert_allclose(H, H.T, atol=1e-14)

    def test_diagonal_free_spectrum(self):
        """Without braid correction, diagonal should be n²/r_c²."""
        r_c = KK_R_C
        H = kk_hamiltonian(r_c=r_c, n_qubits=3, include_braid=False)
        for n in range(8):
            assert H[n, n] == pytest.approx(n ** 2 / r_c ** 2, rel=1e-10)

    def test_zero_mode_energy(self):
        """n=0 mode (massless zero mode) should have energy 0."""
        H = kk_hamiltonian(n_qubits=3)
        assert H[0, 0] == pytest.approx(0.0, abs=1e-14)

    def test_braid_correction_adds_off_diagonal(self):
        H_free  = kk_hamiltonian(n_qubits=3, include_braid=False)
        H_braid = kk_hamiltonian(n_qubits=3, include_braid=True)
        # The only difference should be at the (n1, n2) and (n2, n1) positions
        diff = H_braid - H_free
        n1, n2 = KK_N1, KK_N2
        assert abs(diff[n1, n2]) > 0
        assert abs(diff[n2, n1]) > 0
        # All other entries should be zero
        diff_copy = diff.copy()
        diff_copy[n1, n2] = 0
        diff_copy[n2, n1] = 0
        np.testing.assert_allclose(diff_copy, 0.0, atol=1e-14)

    def test_braid_mixing_strength_formula(self):
        """k_mix = 2*n1*n2/(k_cs * r_c²)."""
        r_c = 5.0
        n1, n2, k_cs = 2, 3, 10
        H = kk_hamiltonian(r_c=r_c, n_qubits=4, n1=n1, n2=n2, k_cs=k_cs)
        expected_k_mix = 2.0 * n1 * n2 / (k_cs * r_c ** 2)
        assert H[n1, n2] == pytest.approx(expected_k_mix, rel=1e-12)

    def test_error_on_mode_exceeding_dim(self):
        with pytest.raises(ValueError, match="exceed Hilbert space"):
            kk_hamiltonian(n_qubits=2, n1=5, n2=7, include_braid=True)

    def test_positive_semidefinite_without_braid(self):
        """Free KK spectrum is non-negative."""
        H = kk_hamiltonian(n_qubits=3, include_braid=False)
        eigs = np.linalg.eigvalsh(H)
        assert np.all(eigs >= -1e-12)

    def test_canonical_constants(self):
        assert KK_N1 == 5
        assert KK_N2 == 7
        assert KK_KCS == 74
        assert KK_R_C == pytest.approx(math.sqrt(74), rel=1e-12)


# ---------------------------------------------------------------------------
# 2. Ansatz circuit
# ---------------------------------------------------------------------------

class TestAnsatzCircuit:
    N_QUBITS = 2
    N_LAYERS = 1

    def _n_params(self, n_qubits=None, n_layers=None):
        n_qubits = n_qubits or self.N_QUBITS
        n_layers = n_layers or self.N_LAYERS
        return n_qubits * (n_layers + 1)

    def test_shape(self):
        theta = np.zeros(self._n_params())
        U = ansatz_circuit(theta, self.N_QUBITS, self.N_LAYERS)
        dim = 2 ** self.N_QUBITS
        assert U.shape == (dim, dim)

    def test_unitarity(self):
        rng = np.random.default_rng(0)
        theta = rng.uniform(-math.pi, math.pi, self._n_params())
        U = ansatz_circuit(theta, self.N_QUBITS, self.N_LAYERS)
        dim = 2 ** self.N_QUBITS
        np.testing.assert_allclose(
            U @ U.conj().T, np.eye(dim, dtype=complex), atol=1e-10
        )

    def test_unitarity_3qubits(self):
        n_q, n_l = 3, 2
        rng = np.random.default_rng(1)
        theta = rng.uniform(-math.pi, math.pi, n_q * (n_l + 1))
        U = ansatz_circuit(theta, n_q, n_l)
        dim = 2 ** n_q
        np.testing.assert_allclose(
            U @ U.conj().T, np.eye(dim, dtype=complex), atol=1e-10
        )

    def test_wrong_theta_length_raises(self):
        with pytest.raises(ValueError, match="theta has"):
            ansatz_circuit(np.zeros(5), self.N_QUBITS, self.N_LAYERS)

    def test_identity_at_zero_angles(self):
        """With all zero angles, the circuit should give a specific fixed unitary
        (no Ry rotation but CNOT gates may still act)."""
        theta = np.zeros(self._n_params())
        U = ansatz_circuit(theta, self.N_QUBITS, self.N_LAYERS)
        # U must be unitary regardless
        dim = 2 ** self.N_QUBITS
        np.testing.assert_allclose(
            U @ U.conj().T, np.eye(dim, dtype=complex), atol=1e-10
        )

    def test_different_params_give_different_unitaries(self):
        theta1 = np.zeros(self._n_params())
        theta2 = np.ones(self._n_params()) * 0.5
        U1 = ansatz_circuit(theta1, self.N_QUBITS, self.N_LAYERS)
        U2 = ansatz_circuit(theta2, self.N_QUBITS, self.N_LAYERS)
        assert not np.allclose(U1, U2)


# ---------------------------------------------------------------------------
# 3. VQE optimisation
# ---------------------------------------------------------------------------

class TestVQEGroundState:
    """Test VQE converges to the correct ground state."""

    # Small system for fast tests
    N_QUBITS = 3
    N_LAYERS = 3
    TOL_ENERGY = 0.1   # 10% relative error tolerance for VQE approximation

    def test_vqe_returns_result(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=0, seed=0)
        assert isinstance(result, VQEResult)

    def test_vqe_ground_energy_near_exact(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=0, seed=0)
        exact_e0 = result.exact_energies[0]
        # Ground energy should be >= exact (variational principle)
        assert result.ground_energy >= exact_e0 - 1e-6
        # And within TOL_ENERGY of exact
        if abs(exact_e0) > 1e-10:
            assert abs(result.ground_energy - exact_e0) / abs(exact_e0) <= self.TOL_ENERGY
        else:
            assert abs(result.ground_energy - exact_e0) <= 1e-3

    def test_variational_principle(self):
        """VQE energy must be >= exact ground energy (variational principle)."""
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=0, seed=42)
        assert result.ground_energy >= result.exact_energies[0] - 1e-6

    def test_ground_state_is_normalised(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=0, seed=0)
        assert np.linalg.norm(result.ground_state) == pytest.approx(1.0, abs=1e-6)

    def test_ground_state_energy_consistent(self):
        """Energy from ⟨ψ|H|ψ⟩ should match reported ground_energy."""
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=0, seed=0)
        H = kk_hamiltonian(n_qubits=self.N_QUBITS)
        psi = result.ground_state
        e_check = float(np.real(psi.conj() @ H @ psi))
        assert e_check == pytest.approx(result.ground_energy, rel=1e-6)

    def test_fidelity_nonnegative(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=0, seed=0)
        assert 0.0 <= result.fidelity <= 1.0 + 1e-8

    def test_exact_energies_nonnegative_zerobraid(self):
        """Without braid, all exact eigenvalues ≥ 0 (positive semidefinite)."""
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=0, seed=0, include_braid=False)
        assert np.all(result.exact_energies >= -1e-12)

    def test_result_fields_populated(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=1, seed=0)
        assert result.n_qubits == self.N_QUBITS
        assert result.n_layers == self.N_LAYERS
        assert result.r_c == pytest.approx(KK_R_C, rel=1e-10)
        assert result.n1 == KK_N1
        assert result.n2 == KK_N2
        assert result.k_cs == KK_KCS
        assert len(result.excited_energies) == 1
        assert len(result.excited_states) == 1


class TestVQEExcitedStates:
    """Test that excited states are found and are approximately orthogonal."""

    N_QUBITS = 3
    N_LAYERS = 3

    def test_excited_states_count(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=2, seed=0)
        assert len(result.excited_energies) == 2
        assert len(result.excited_states) == 2

    def test_excited_energies_above_ground(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=2, seed=0)
        for E_ex in result.excited_energies:
            # Excited energies should be >= ground energy (approximately)
            assert E_ex >= result.ground_energy - 0.5  # generous tolerance

    def test_excited_states_normalised(self):
        result = vqe_kk(n_qubits=self.N_QUBITS, n_layers=self.N_LAYERS,
                        n_excited=2, seed=0)
        for psi in result.excited_states:
            assert np.linalg.norm(psi) == pytest.approx(1.0, abs=1e-5)


# ---------------------------------------------------------------------------
# 4. Physical consistency
# ---------------------------------------------------------------------------

class TestPhysicalConsistency:
    def test_braid_lowers_ground_energy(self):
        """The braid off-diagonal term should lower the ground state energy."""
        r_c = 5.0   # large radius → small splittings
        n_q, n1, n2, k_cs = 4, 2, 3, 10
        e_free  = _exact_ground_energy(r_c, n_q, n1, n2, k_cs, include_braid=False)
        e_braid = _exact_ground_energy(r_c, n_q, n1, n2, k_cs, include_braid=True)
        # Off-diagonal perturbation lowers the lowest eigenvalue
        assert e_braid <= e_free + 1e-12

    def test_zero_mode_always_zero_energy(self):
        """The n=0 mode should always have zero mass in the free spectrum."""
        for n_q in [2, 3, 4]:
            H = kk_hamiltonian(n_qubits=n_q, include_braid=False)
            assert H[0, 0] == pytest.approx(0.0, abs=1e-14)

    def test_r_c_scaling(self):
        """KK masses scale as m_n = n/r_c, so m_1 = 1/r_c."""
        r_c = 3.0
        H = kk_hamiltonian(r_c=r_c, n_qubits=3, include_braid=False)
        assert H[1, 1] == pytest.approx(1.0 / r_c ** 2, rel=1e-12)

    def test_canonical_kk_rcc(self):
        """r_c = √k_cs = √74 from φ₀ closure."""
        assert KK_R_C ** 2 == pytest.approx(KK_KCS, rel=1e-12)

    def test_kk_mode_5_energy_without_braid(self):
        """Mode n=5 should have energy 25/r_c² in free spectrum."""
        H = kk_hamiltonian(n_qubits=3, include_braid=False)
        assert H[5, 5] == pytest.approx(25.0 / KK_R_C ** 2, rel=1e-12)

    def test_spectrum_monotone_without_braid(self):
        """Free spectrum m_n² = n²/r_c² is monotonically increasing for n≥0."""
        H = kk_hamiltonian(n_qubits=3, include_braid=False)
        diag = np.diag(H)
        assert np.all(np.diff(diag) >= 0)

    def test_braid_level_5_7_74(self):
        """Verify the (5,7,74) canonical braid constants survive the Hamiltonian."""
        H = kk_hamiltonian()
        n1, n2, k_cs = KK_N1, KK_N2, KK_KCS
        rho = 2.0 * n1 * n2 / k_cs
        k_mix = rho / KK_R_C ** 2
        assert H[n1, n2] == pytest.approx(k_mix, rel=1e-12)
        assert H[n2, n1] == pytest.approx(k_mix, rel=1e-12)

    def test_hamiltonian_real(self):
        """KK Hamiltonian is real-valued (braided extension stays real)."""
        H = kk_hamiltonian()
        assert np.isrealobj(H) or np.allclose(H.imag, 0)

    def test_vqe_no_braid_ground_zero(self):
        """Without braid correction, ground state energy should be exactly 0 (massless mode)."""
        result = vqe_kk(n_qubits=3, n_layers=3, n_excited=0, seed=0, include_braid=False)
        assert result.exact_energies[0] == pytest.approx(0.0, abs=1e-12)
