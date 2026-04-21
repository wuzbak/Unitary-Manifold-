# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_quantum_switch.py
============================
Tests for src/core/quantum_switch.py — Theorem XVI: Quantum Switch and
Indefinite Causal Order.

Physical claims under test
--------------------------
1. causal_switch: applying a unitary in an equal-weight superposition of
   forward (U) and backward (U†) causal orders preserves normalisation and
   von Neumann entropy.

2. time_rewind: applying U† to a state that was evolved by U returns the
   original state with fidelity = 1, without requiring knowledge of what U
   *did* — only *how* to invert it.

3. time_fastforward: concentrating N age-units from N systems into one
   system (Navascués "age theft" protocol) conserves total age.

4. braided_causal_mixing: the (5,7) resonance at k_cs = 74 gives ρ = 35/37
   and c_s = 12/37, connecting the quantum switch to the braided winding sector.

5. Holographic entropy constraint: every quantum-switch protocol leaves the
   von Neumann entropy (and therefore the holographic boundary entropy
   S_∂ = A_∂ / 4G₄) unchanged.

Test classes
------------
TestHelpers               — density_matrix, von_neumann_entropy, causal_fidelity
TestCausalSwitchBasic     — normalisation, alpha limits, identity unitary
TestCausalSwitchPhysics   — entropy preservation, fidelity bounds
TestTimeRewind            — exact inversion, double rewind, higher dimensions
TestTimeFastforward       — age conservation, N=1, N=3 state correctness
TestBraidedCausalMixing   — ρ, c_s, α values for (5,7); unit circle; scan
TestSwitchEntropyInvariant — invariant passes/fails; mixed states
TestCheckUnitary          — invalid U rejected; valid U accepted
TestNavascuésProtocol     — full end-to-end protocol recreating paper findings
"""

import numpy as np
import pytest

from src.core.quantum_switch import (
    QuantumSwitchResult,
    braided_causal_mixing,
    causal_fidelity,
    causal_switch,
    density_matrix,
    switch_entropy_invariant,
    time_fastforward,
    time_rewind,
    von_neumann_entropy,
    C_S_BRAIDED,
    RHO_BRAIDED,
    K_CS,
    WINDING_N1,
    WINDING_N2,
    _check_unitary,
)


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------

def _rotation_2d(theta: float) -> np.ndarray:
    """2×2 real rotation matrix (unitary)."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]], dtype=complex)


def _phase_gate(phi: float, d: int = 2) -> np.ndarray:
    """Diagonal unitary diag(1, e^{iφ}, e^{2iφ}, ...)."""
    return np.diag([np.exp(1j * k * phi) for k in range(d)]).astype(complex)


def _hadamard() -> np.ndarray:
    return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def _random_unitary(d: int, seed: int = 0) -> np.ndarray:
    """Haar-random unitary via QR decomposition."""
    rng = np.random.default_rng(seed)
    M = rng.standard_normal((d, d)) + 1j * rng.standard_normal((d, d))
    Q, R = np.linalg.qr(M)
    # Fix the phase convention so QR is unique
    Q = Q @ np.diag(np.exp(1j * np.angle(np.diag(R))))
    return Q


def _ket(d: int, k: int) -> np.ndarray:
    """Computational basis vector |k⟩ in d-dimensional space."""
    v = np.zeros(d, dtype=complex)
    v[k] = 1.0
    return v


def _mixed_state(d: int) -> np.ndarray:
    """Maximally mixed state ρ = I/d."""
    return np.eye(d, dtype=complex) / d


# ---------------------------------------------------------------------------
# TestHelpers
# ---------------------------------------------------------------------------

class TestHelpers:
    """density_matrix, von_neumann_entropy, causal_fidelity."""

    def test_density_matrix_pure_is_rank_one(self):
        psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
        rho = density_matrix(psi)
        assert rho.shape == (2, 2)
        # rank-1: only one non-zero eigenvalue
        eigs = np.linalg.eigvalsh(rho)
        assert np.sum(eigs > 1e-10) == 1

    def test_density_matrix_trace_one(self):
        psi = np.array([1, 1j, -1], dtype=complex) / np.sqrt(3)
        rho = density_matrix(psi)
        assert abs(np.trace(rho) - 1.0) < 1e-12

    def test_density_matrix_hermitian(self):
        psi = _ket(4, 2)
        rho = density_matrix(psi)
        assert np.allclose(rho, rho.conj().T)

    def test_density_matrix_normalises_input(self):
        """density_matrix must normalise the input before forming the outer product."""
        psi = np.array([3.0, 4.0], dtype=complex)   # norm = 5
        rho = density_matrix(psi)
        assert abs(np.trace(rho) - 1.0) < 1e-12

    def test_von_neumann_entropy_pure_state_zero(self):
        psi = np.array([1, 0], dtype=complex)
        rho = density_matrix(psi)
        assert von_neumann_entropy(rho) < 1e-12

    def test_von_neumann_entropy_superposition_pure(self):
        psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
        rho = density_matrix(psi)
        assert von_neumann_entropy(rho) < 1e-12

    def test_von_neumann_entropy_maximally_mixed_2d(self):
        rho = _mixed_state(2)
        S = von_neumann_entropy(rho)
        assert abs(S - np.log(2)) < 1e-10

    def test_von_neumann_entropy_maximally_mixed_4d(self):
        rho = _mixed_state(4)
        S = von_neumann_entropy(rho)
        assert abs(S - np.log(4)) < 1e-10

    def test_von_neumann_entropy_nonnegative(self):
        for d in [2, 3, 5]:
            rho = _mixed_state(d)
            assert von_neumann_entropy(rho) >= 0.0

    def test_causal_fidelity_identical_states(self):
        psi = np.array([1, 1j], dtype=complex) / np.sqrt(2)
        assert abs(causal_fidelity(psi, psi) - 1.0) < 1e-12

    def test_causal_fidelity_orthogonal_states(self):
        psi_a = _ket(2, 0)
        psi_b = _ket(2, 1)
        assert causal_fidelity(psi_a, psi_b) < 1e-12

    def test_causal_fidelity_global_phase_invariant(self):
        psi = np.array([1, 0], dtype=complex)
        psi_phase = np.exp(1j * 0.7) * psi
        assert abs(causal_fidelity(psi, psi_phase) - 1.0) < 1e-12

    def test_causal_fidelity_in_range(self):
        for seed in range(5):
            rng = np.random.default_rng(seed)
            a = rng.standard_normal(4) + 1j * rng.standard_normal(4)
            b = rng.standard_normal(4) + 1j * rng.standard_normal(4)
            F = causal_fidelity(a, b)
            assert 0.0 <= F <= 1.0 + 1e-12

    def test_causal_fidelity_unnormalised_input(self):
        """causal_fidelity normalises internally."""
        psi = np.array([3, 4], dtype=complex)
        psi_unit = psi / np.linalg.norm(psi)
        assert abs(causal_fidelity(psi, psi_unit) - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# TestCheckUnitary
# ---------------------------------------------------------------------------

class TestCheckUnitary:
    """_check_unitary rejects non-unitaries, accepts valid ones."""

    def test_identity_accepted(self):
        _check_unitary(np.eye(3, dtype=complex))  # must not raise

    def test_rotation_accepted(self):
        _check_unitary(_rotation_2d(0.5))

    def test_hadamard_accepted(self):
        _check_unitary(_hadamard())

    def test_random_unitary_accepted(self):
        _check_unitary(_random_unitary(4, seed=1))

    def test_non_unitary_rejected(self):
        M = np.array([[2, 0], [0, 1]], dtype=complex)  # not unitary
        with pytest.raises(ValueError, match="not unitary"):
            _check_unitary(M)

    def test_scaling_rejected(self):
        U = 2 * _rotation_2d(0.3)
        with pytest.raises(ValueError, match="not unitary"):
            _check_unitary(U)


# ---------------------------------------------------------------------------
# TestCausalSwitchBasic
# ---------------------------------------------------------------------------

class TestCausalSwitchBasic:
    """Basic properties of causal_switch."""

    def test_returns_QuantumSwitchResult(self):
        psi = _ket(2, 0)
        result = causal_switch(psi, _hadamard())
        assert isinstance(result, QuantumSwitchResult)

    def test_output_is_normalised(self):
        psi = _ket(2, 0)
        result = causal_switch(psi, _rotation_2d(0.3), alpha=0.5)
        assert abs(np.linalg.norm(result.state_out) - 1.0) < 1e-12

    def test_alpha_1_is_pure_forward(self):
        """alpha=1 → U|ψ⟩."""
        psi = _ket(2, 0)
        U = _rotation_2d(0.6)
        result = causal_switch(psi, U, alpha=1.0)
        expected = U @ psi
        assert causal_fidelity(result.state_out, expected) > 1 - 1e-10

    def test_alpha_0_is_pure_backward(self):
        """alpha=0 → U†|ψ⟩."""
        psi = _ket(2, 0)
        U = _rotation_2d(0.6)
        result = causal_switch(psi, U, alpha=0.0)
        expected = U.conj().T @ psi
        assert causal_fidelity(result.state_out, expected) > 1 - 1e-10

    def test_identity_unitary_returns_input(self):
        """U = I → U and U† both give |ψ⟩ → output = |ψ⟩ regardless of alpha."""
        psi = np.array([1, 1j], dtype=complex) / np.sqrt(2)
        result = causal_switch(psi, np.eye(2, dtype=complex), alpha=0.5)
        assert causal_fidelity(result.state_out, psi) > 1 - 1e-10

    def test_non_unitary_raises(self):
        psi = _ket(2, 0)
        M = np.array([[2, 0], [0, 1]], dtype=complex)
        with pytest.raises(ValueError, match="not unitary"):
            causal_switch(psi, M)

    def test_dimension_mismatch_raises(self):
        psi = _ket(2, 0)
        U = np.eye(3, dtype=complex)
        with pytest.raises(ValueError, match="dimensions"):
            causal_switch(psi, U)

    def test_zero_state_raises(self):
        psi = np.zeros(2, dtype=complex)
        with pytest.raises(ValueError, match="zero norm"):
            causal_switch(psi, np.eye(2, dtype=complex))

    def test_4d_state(self):
        psi = _ket(4, 2)
        U = _random_unitary(4, seed=7)
        result = causal_switch(psi, U, alpha=0.5)
        assert result.state_out.shape == (4,)
        assert abs(np.linalg.norm(result.state_out) - 1.0) < 1e-12

    def test_real_input_works(self):
        psi = np.array([1.0, 0.0])   # real dtype
        U = _rotation_2d(np.pi / 4)
        result = causal_switch(psi, U, alpha=0.5)
        assert result.state_out.shape == (2,)


# ---------------------------------------------------------------------------
# TestCausalSwitchPhysics
# ---------------------------------------------------------------------------

class TestCausalSwitchPhysics:
    """Entropy preservation and fidelity bounds."""

    def test_entropy_preserved_pure_state(self):
        """Pure → pure under unitary: S = 0 before and after."""
        psi = _ket(2, 0)
        result = causal_switch(psi, _hadamard(), alpha=0.5)
        assert result.entropy_before < 1e-12
        assert result.entropy_after < 1e-12
        assert result.entropy_preserved

    def test_entropy_preserved_various_alphas(self):
        psi = np.array([1, 1j], dtype=complex) / np.sqrt(2)
        U = _rotation_2d(1.2)
        for alpha in [0.1, 0.3, 0.5, 0.7, 0.9]:
            result = causal_switch(psi, U, alpha=alpha)
            assert result.entropy_preserved, f"Failed at alpha={alpha}"

    def test_causal_fidelity_perfect_rewind(self):
        """alpha=0 → U†(U|ψ₀⟩) = |ψ₀⟩ — output equals pre-evolution state."""
        psi0 = _ket(2, 0)
        U = _rotation_2d(0.9)
        psi_evolved = U @ psi0
        # Rewind the evolved state: apply U† via alpha=0 pure-backward channel
        result = causal_switch(psi_evolved, U, alpha=0.0)
        # Expected: U†(U|ψ₀⟩) = |ψ₀⟩
        # Note: result.rewound compares output to switch-*input* (psi_evolved),
        # not to psi0, so we check fidelity with psi0 directly.
        assert causal_fidelity(result.state_out, psi0) > 1 - 1e-10

    def test_rewound_flag_set_for_identity(self):
        psi = np.array([0.6, 0.8], dtype=complex)
        result = causal_switch(psi, np.eye(2, dtype=complex), alpha=0.5)
        assert result.rewound

    def test_fidelity_not_one_for_generic_rotation(self):
        """For a non-trivial rotation the output differs from the input."""
        psi = _ket(2, 0)
        U = _rotation_2d(0.7)   # not identity
        result = causal_switch(psi, U, alpha=1.0)  # pure forward
        # U|0⟩ ≠ |0⟩ for a rotation by 0.7 rad
        assert result.causal_fidelity < 1.0 - 1e-6


# ---------------------------------------------------------------------------
# TestTimeRewind
# ---------------------------------------------------------------------------

class TestTimeRewind:
    """time_rewind: U†U = I recovery."""

    def test_rewind_rotation(self):
        psi0 = np.array([1, 0], dtype=complex)
        U = _rotation_2d(1.1)
        psi_evolved = U @ psi0
        psi_back = time_rewind(psi_evolved, U)
        assert causal_fidelity(psi_back, psi0) > 1 - 1e-10

    def test_rewind_hadamard(self):
        psi0 = _ket(2, 1)
        H = _hadamard()
        psi_back = time_rewind(H @ psi0, H)
        assert causal_fidelity(psi_back, psi0) > 1 - 1e-10

    def test_double_rewind_returns_forward(self):
        """Rewinding the rewind restores the once-evolved state."""
        psi0 = _ket(2, 0)
        U = _rotation_2d(0.5)
        psi1 = U @ psi0
        psi_back = time_rewind(psi1, U)      # = psi0
        psi_fwd_again = time_rewind(psi_back, U.conj().T)   # = psi1
        assert causal_fidelity(psi_fwd_again, psi1) > 1 - 1e-10

    def test_rewind_4d(self):
        psi0 = _ket(4, 3)
        U = _random_unitary(4, seed=42)
        psi_back = time_rewind(U @ psi0, U)
        assert causal_fidelity(psi_back, psi0) > 1 - 1e-10

    def test_rewind_output_normalised(self):
        psi0 = np.array([1, 1, 1], dtype=complex) / np.sqrt(3)
        U = _random_unitary(3, seed=2)
        psi_back = time_rewind(U @ psi0, U)
        assert abs(np.linalg.norm(psi_back) - 1.0) < 1e-12

    def test_rewind_non_unitary_raises(self):
        psi = _ket(2, 0)
        M = np.array([[1, 1], [0, 1]], dtype=complex)  # shear — not unitary
        with pytest.raises(ValueError, match="not unitary"):
            time_rewind(psi, M)

    def test_rewind_phase_gate(self):
        psi0 = np.array([1, 1], dtype=complex) / np.sqrt(2)
        U = _phase_gate(np.pi / 3, d=2)
        psi_back = time_rewind(U @ psi0, U)
        assert causal_fidelity(psi_back, psi0) > 1 - 1e-10

    def test_rewind_without_knowing_internal_dynamics(self):
        """Key physics claim: rewind works even if we don't know what U *did*.
        
        We apply a random unitary that scrambles the state completely,
        then rewind using only U (not the detailed action U had on the state).
        """
        psi0 = np.array([0.5, 0.5 + 0.5j, 0.5j, 0.0], dtype=complex)
        psi0 /= np.linalg.norm(psi0)
        U = _random_unitary(4, seed=99)
        # evolve — we don't inspect what happened to the state
        psi_scrambled = U @ psi0
        # rewind using only U
        psi_back = time_rewind(psi_scrambled, U)
        assert causal_fidelity(psi_back, psi0) > 1 - 1e-10


# ---------------------------------------------------------------------------
# TestTimeFastforward
# ---------------------------------------------------------------------------

class TestTimeFastforward:
    """time_fastforward: Navascués age-theft protocol."""

    def test_N1_aged_state_is_U_psi(self):
        """N=1: aged_state = U|ψ₀⟩, no reverted states."""
        psi0 = _ket(2, 0)
        U = _rotation_2d(0.4)
        aged, reverted = time_fastforward(psi0, U, N=1)
        assert len(reverted) == 0
        assert causal_fidelity(aged, U @ psi0) > 1 - 1e-10

    def test_N3_aged_state_is_U3_psi(self):
        psi0 = _ket(2, 0)
        U = _rotation_2d(0.3)
        aged, reverted = time_fastforward(psi0, U, N=3)
        U3 = np.linalg.matrix_power(U, 3)
        assert causal_fidelity(aged, U3 @ psi0) > 1 - 1e-10

    def test_N3_reverted_count(self):
        psi0 = _ket(2, 1)
        aged, reverted = time_fastforward(psi0, _hadamard(), N=3)
        assert len(reverted) == 2

    def test_reverted_equal_initial(self):
        """The N-1 donor systems must return to |ψ₀⟩."""
        psi0 = np.array([1, 1j], dtype=complex) / np.sqrt(2)
        U = _rotation_2d(0.5)
        aged, reverted = time_fastforward(psi0, U, N=4)
        for psi_rev in reverted:
            assert causal_fidelity(psi_rev, psi0) > 1 - 1e-10

    def test_age_conservation_N10(self):
        """Total age before = 10; after = 10 (all in one system, rest at 0).

        'Age' here is defined as the number of unitary evolution steps.
        The aged system has been evolved N=10 times; the 9 donors have
        returned to age 0.  10 = 10, age is conserved.
        """
        psi0 = _ket(4, 1)
        U = _random_unitary(4, seed=5)
        N = 10
        aged, reverted = time_fastforward(psi0, U, N=N)
        # aged = U^10 psi0
        UN = np.linalg.matrix_power(U, N)
        assert causal_fidelity(aged, UN @ psi0) > 1 - 1e-10
        # all donors at age 0
        assert len(reverted) == N - 1
        for r in reverted:
            assert causal_fidelity(r, psi0) > 1 - 1e-10

    def test_aged_state_normalised(self):
        psi0 = _ket(3, 0)
        U = _random_unitary(3, seed=6)
        aged, _ = time_fastforward(psi0, U, N=7)
        assert abs(np.linalg.norm(aged) - 1.0) < 1e-12

    def test_N0_raises(self):
        with pytest.raises(ValueError, match="positive integer"):
            time_fastforward(_ket(2, 0), np.eye(2, dtype=complex), N=0)

    def test_negative_N_raises(self):
        with pytest.raises(ValueError, match="positive integer"):
            time_fastforward(_ket(2, 0), np.eye(2, dtype=complex), N=-3)

    def test_non_unitary_U_raises(self):
        M = np.array([[2, 0], [0, 1]], dtype=complex)
        with pytest.raises(ValueError, match="not unitary"):
            time_fastforward(_ket(2, 0), M, N=2)

    def test_zero_initial_state_raises(self):
        with pytest.raises(ValueError, match="zero norm"):
            time_fastforward(np.zeros(2, dtype=complex), np.eye(2, dtype=complex), N=2)


# ---------------------------------------------------------------------------
# TestBraidedCausalMixing
# ---------------------------------------------------------------------------

class TestBraidedCausalMixing:
    """braided_causal_mixing connects quantum switch to (5,7) braid geometry."""

    def test_canonical_rho_57(self):
        """ρ = 2×5×7/74 = 70/74 = 35/37."""
        params = braided_causal_mixing(5, 7, 74)
        assert abs(params["rho"] - 70 / 74) < 1e-12

    def test_canonical_cs_57(self):
        """c_s = (49−25)/74 = 24/74 = 12/37."""
        params = braided_causal_mixing(5, 7, 74)
        assert abs(params["c_s"] - 24 / 74) < 1e-12

    def test_sum_of_squares_check_passes(self):
        params = braided_causal_mixing(5, 7, 74)
        assert params["sum_of_squares_check"]

    def test_sum_of_squares_check_fails_wrong_kcs(self):
        params = braided_causal_mixing(5, 7, 75)
        assert not params["sum_of_squares_check"]

    def test_alpha_canonical(self):
        """α = (1 + 12/37) / 2 = 49/74."""
        params = braided_causal_mixing(5, 7, 74)
        assert abs(params["alpha"] - 49 / 74) < 1e-12

    def test_unit_circle_identity(self):
        """ρ² + c_s² ≤ 1 (mixing and sound speed lie inside the unit circle)."""
        params = braided_causal_mixing(5, 7, 74)
        assert params["rho"] ** 2 + params["c_s"] ** 2 <= 1.0 + 1e-12

    def test_module_constants_consistent_with_function(self):
        params = braided_causal_mixing(WINDING_N1, WINDING_N2, K_CS)
        assert abs(params["rho"] - RHO_BRAIDED) < 1e-12
        assert abs(params["c_s"] - C_S_BRAIDED) < 1e-12

    def test_zero_kcs_raises(self):
        with pytest.raises(ValueError, match="positive"):
            braided_causal_mixing(5, 7, 0)

    def test_n1_equals_n2(self):
        """Equal winding numbers → c_s = 0 (no causal asymmetry)."""
        params = braided_causal_mixing(5, 5, 50)
        assert abs(params["c_s"]) < 1e-12

    def test_small_winding_numbers(self):
        params = braided_causal_mixing(1, 2, 5)
        assert abs(params["rho"] - 4 / 5) < 1e-12
        assert abs(params["c_s"] - 3 / 5) < 1e-12

    def test_alpha_in_unit_interval(self):
        for n1, n2, k in [(5, 7, 74), (3, 4, 25), (1, 2, 5)]:
            params = braided_causal_mixing(n1, n2, k)
            assert 0.0 <= params["alpha"] <= 1.0


# ---------------------------------------------------------------------------
# TestSwitchEntropyInvariant
# ---------------------------------------------------------------------------

class TestSwitchEntropyInvariant:
    """switch_entropy_invariant verifies holographic entropy is preserved."""

    def test_pure_states_invariant(self):
        rho = density_matrix(_ket(2, 0))
        assert switch_entropy_invariant(rho, rho)

    def test_unitary_preserves_mixed(self):
        rho_in = _mixed_state(3)
        U = _random_unitary(3, seed=10)
        rho_out = U @ rho_in @ U.conj().T
        assert switch_entropy_invariant(rho_in, rho_out)

    def test_non_unitary_fails(self):
        """A non-unitary (e.g. partial trace) changes entropy."""
        rho_in = density_matrix(_ket(2, 0))   # S=0
        rho_out = _mixed_state(2)              # S=ln2 ≠ 0
        assert not switch_entropy_invariant(rho_in, rho_out)

    def test_tolerance_respected(self):
        rho_in = density_matrix(_ket(4, 0))
        rho_out = density_matrix(_ket(4, 1))  # both pure → S=0
        assert switch_entropy_invariant(rho_in, rho_out, tol=1e-10)

    def test_tight_tolerance_fails(self):
        """Mixed state with slightly different entropy fails at tight tol."""
        rho1 = _mixed_state(2)                        # S = ln 2
        eps = 0.01
        # Perturb slightly off maximally mixed
        rho2 = np.array([[0.5 + eps, 0], [0, 0.5 - eps]], dtype=complex)
        rho2 /= np.trace(rho2)
        assert not switch_entropy_invariant(rho1, rho2, tol=1e-12)


# ---------------------------------------------------------------------------
# TestNavascuésProtocol
# ---------------------------------------------------------------------------

class TestNavascuésProtocol:
    """End-to-end recreation of the ÖAW/Vienna experimental findings."""

    def test_photon_rewind_full_protocol(self):
        """A 'photon' evolves through a 'crystal' (U), then the switch returns
        it to its initial state without the apparatus learning the crystal's
        internal structure (only U is needed, not the state of the crystal).
        """
        # Initial photon state (horizontal polarisation)
        psi0 = np.array([1, 0], dtype=complex)

        # 'Crystal' = arbitrary unitary mixing of polarisation modes
        # (internal structure unknown to the rewind apparatus)
        U_crystal = _random_unitary(2, seed=2026)

        # After passing through the crystal
        psi_after_crystal = U_crystal @ psi0

        # Quantum switch rewinds without reading out the crystal's action
        psi_rewound = time_rewind(psi_after_crystal, U_crystal)

        # Claim: rewound state equals original polarisation state
        assert causal_fidelity(psi_rewound, psi0) > 1 - 1e-10

    def test_age_theft_10_systems(self):
        """10 systems each with one evolution step → one system aged 10,
        nine systems returned to initial state.
        """
        N = 10
        psi0 = np.array([0.6, 0.8j], dtype=complex)
        psi0 /= np.linalg.norm(psi0)
        U = _rotation_2d(np.pi / 37)   # small rotation (one "year")

        aged, donors = time_fastforward(psi0, U, N=N)

        # Target is 10 years older
        U10 = np.linalg.matrix_power(U, N)
        assert causal_fidelity(aged, U10 @ psi0) > 1 - 1e-10

        # All 9 donors are back at age 0
        assert len(donors) == N - 1
        for d_state in donors:
            assert causal_fidelity(d_state, psi0) > 1 - 1e-10

    def test_switch_preserves_information_current(self):
        """The analogue of ∫ J^0 d³x: the squared norm ‖ψ‖² = 1 is preserved
        by every switch operation — information is redistributed, not destroyed.
        """
        psi = np.array([1, 1, 1, 1], dtype=complex) / 2.0
        U = _random_unitary(4, seed=3)
        result = causal_switch(psi, U, alpha=0.5)
        # ‖ψ_out‖² = 1 (information conserved)
        assert abs(np.dot(result.state_out.conj(), result.state_out) - 1.0) < 1e-12

    def test_causal_switch_forward_backward_average(self):
        """Equal-weight switch (alpha=0.5): if U = rotation(θ), the output is
        the cosine-averaged state (since U + U† is a scaling of the identity
        in the eigenspace decomposition).
        """
        theta = np.pi / 6
        psi = np.array([1, 0], dtype=complex)
        U = _rotation_2d(theta)

        result = causal_switch(psi, U, alpha=0.5)

        # U|0⟩ = (cos θ, sin θ);  U†|0⟩ = (cos θ, -sin θ)
        # Average (before normalisation): (cos θ, 0) → normalised: (1, 0)
        expected = np.array([1, 0], dtype=complex)
        assert causal_fidelity(result.state_out, expected) > 1 - 1e-10

    def test_braided_switch_uses_canonical_alpha(self):
        """Using the canonical (5,7) alpha from braided_causal_mixing,
        the switch produces a well-defined normalised output.
        """
        params = braided_causal_mixing(WINDING_N1, WINDING_N2, K_CS)
        alpha = params["alpha"]
        psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
        U = _phase_gate(np.pi / 5, d=2)
        result = causal_switch(psi, U, alpha=alpha)
        assert abs(np.linalg.norm(result.state_out) - 1.0) < 1e-12
        assert result.entropy_preserved
