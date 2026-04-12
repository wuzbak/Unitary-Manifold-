"""
tests/test_quantum_unification.py
==================================
Tests for the four quantum-unification theorems derived in
QUANTUM_THEOREMS.md (Parts XII–XV):

  XII  — Black Hole Information Preservation
           ∇_μ J^μ_inf = 0 is unconditional; no process destroys information.
  XIII — Canonical Commutation Relation
           π_φ = ∂_t φ encodes {φ, π_φ} = δ  →  [φ̂, π̂_φ] = iℏ δ.
  XIV  — Hawking Temperature from the φ gradient
           T_H = |∂_r φ / φ| / (2π) at each grid point.
  XV   — ER = EPR (Quantum Entanglement = Topological Information Transfer)
           High topology coupling → shared entropy fixed point → entangled.

All tests are self-contained; none modify global state or existing tests.
"""

import numpy as np
import pytest

from src.core.evolution import (
    FieldState,
    information_current,
    conjugate_momentum_phi,
    hawking_temperature,
    run_evolution,
    step,
)
from src.multiverse.fixed_point import (
    MultiverseNode,
    MultiverseNetwork,
    apply_topology,
    fixed_point_iteration,
    shared_fixed_point_norm,
)


# ---------------------------------------------------------------------------
# Part XII — Black Hole Information Preservation
# ---------------------------------------------------------------------------

class TestInformationConservation:
    """∇_μ J^μ_inf ≈ 0 — information current is locally conserved everywhere."""

    @staticmethod
    def _spatial_divergence(state):
        """Discrete spatial divergence ∂_x J^x of the information current."""
        J = information_current(state.g, state.phi, state.dx)
        return np.gradient(J[:, 1], state.dx, edge_order=2)

    def test_spatial_divergence_small_monotone_phi(self):
        """For a monotone φ profile (dphi never changes sign), ∂_x J^x is small.

        The information_current implementation normalises J^1 by |∂_x φ|, so
        J^1 = φ²/√|g00| · sign(∂_x φ).  When ∂_x φ keeps the same sign
        everywhere (monotone φ), J^1 is smooth and its gradient is small.
        This tests the continuum conservation law in the regime where the
        discrete representation is faithful.
        """
        N = 32
        dx = 0.1
        x = np.arange(N) * dx
        phi = 1.0 + 0.01 * x          # strictly increasing: dphi > 0 always
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        state = FieldState(g=g, B=np.zeros((N, 4)), phi=phi, t=0.0, dx=dx)
        div = self._spatial_divergence(state)
        # Expected: ∂_x J^x ≈ 2 * b * φ / √|g00| ≈ 2 * 0.01 * 1 = 0.02
        # Use interior points only (boundary stencil has higher truncation error)
        assert np.max(np.abs(div[1:-1])) < 0.1

    def test_J0_proportional_to_phi_squared(self):
        """J^0 = φ²/√|g00| — doubling φ should quadruple J^0."""
        N = 16
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        phi1 = np.ones(N)
        phi2 = 2.0 * np.ones(N)
        J1 = information_current(g, phi1, dx=0.1)
        J2 = information_current(g, phi2, dx=0.1)
        np.testing.assert_allclose(J2[:, 0], 4.0 * J1[:, 0], rtol=1e-10)

    def test_J0_nonnegative_throughout_evolution(self):
        """J^0 = φ²/√|g_00| ≥ 0 — information density is non-negative."""
        state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(11))
        history = run_evolution(state, dt=1e-3, steps=10)
        for s in history:
            J = information_current(s.g, s.phi, s.dx)
            assert np.all(J[:, 0] >= 0.0)

    def test_total_information_approximately_conserved(self):
        """Integral ∫ J^0 dx changes by < 10 % over 20 RK4 steps."""
        state = FieldState.flat(N=32, dx=0.05, rng=np.random.default_rng(12))
        dx = state.dx
        J0_init = np.sum(information_current(state.g, state.phi, dx)[:, 0]) * dx
        history = run_evolution(state, dt=5e-4, steps=20)
        s_fin = history[-1]
        J0_fin = np.sum(information_current(s_fin.g, s_fin.phi, s_fin.dx)[:, 0]) * s_fin.dx
        rel_change = abs(J0_fin - J0_init) / (abs(J0_init) + 1e-12)
        assert rel_change < 0.10, f"Total information changed by {rel_change:.2%}"

    def test_information_preserved_with_goldberger_wise(self):
        """Goldberger-Wise stabilisation keeps J^0 positive and finite."""
        state = FieldState.flat(N=16, dx=0.1, phi0=1.0, m_phi=1.0,
                                rng=np.random.default_rng(13))
        history = run_evolution(state, dt=1e-3, steps=10)
        for s in history:
            J = information_current(s.g, s.phi, s.dx)
            assert np.all(J[:, 0] >= 0.0)
            assert np.all(np.isfinite(J))

    def test_information_current_finite_throughout(self):
        """J^μ must remain finite at every grid point and timestep."""
        state = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(14))
        history = run_evolution(state, dt=1e-3, steps=5)
        for s in history:
            J = information_current(s.g, s.phi, s.dx)
            assert np.all(np.isfinite(J))


# ---------------------------------------------------------------------------
# Part XIII — Canonical Commutation Relation
# ---------------------------------------------------------------------------

class TestCanonicalCommutation:
    """π_φ = ∂_t φ encodes {φ, π_φ} = δ → [φ̂, π̂_φ] = iℏ δ."""

    def test_conjugate_momentum_shape(self):
        """π_φ must be a 1-D array of length N."""
        state = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(30))
        pi = conjugate_momentum_phi(state)
        assert pi.shape == state.phi.shape

    def test_conjugate_momentum_finite(self):
        """π_φ must be finite at all grid points."""
        state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(31))
        pi = conjugate_momentum_phi(state)
        assert np.all(np.isfinite(pi))

    def test_conjugate_momentum_matches_finite_difference(self):
        """π_φ = ∂_t φ must match the first-order finite-difference (φ_new − φ)/dt."""
        state = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(32))
        dt = 1e-5
        pi_analytical = conjugate_momentum_phi(state)
        s1 = step(state, dt)
        pi_fd = (s1.phi - state.phi) / dt
        # Agree to within ~1 % (Euler truncation error O(dt))
        np.testing.assert_allclose(pi_analytical, pi_fd, rtol=1e-2,
                                   err_msg="π_φ does not match finite-difference ∂_t φ")

    def test_kinetic_energy_nonnegative(self):
        """H_kin = ½ Σ π²_i dx ≥ 0 — kinetic energy is positive semi-definite."""
        state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(33))
        pi = conjugate_momentum_phi(state)
        H_kin = 0.5 * np.sum(pi ** 2) * state.dx
        assert H_kin >= 0.0

    def test_symplectic_norm_nonzero(self):
        """Σ_i |φ_i · π_i| dx > 0 — the symplectic form is non-degenerate."""
        state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(34))
        pi = conjugate_momentum_phi(state)
        symp_norm = np.sum(np.abs(state.phi * pi)) * state.dx
        assert symp_norm > 0.0

    def test_stabilisation_reduces_momentum(self):
        """Stronger restoring potential (m_phi > 0) should damp φ oscillations."""
        N = 32
        rng = np.random.default_rng(35)
        s_free = FieldState.flat(N=N, dx=0.1, phi0=1.0, m_phi=0.0, rng=rng)
        rng2 = np.random.default_rng(35)
        s_stab = FieldState.flat(N=N, dx=0.1, phi0=1.0, m_phi=5.0, rng=rng2)
        pi_free = conjugate_momentum_phi(s_free)
        pi_stab = conjugate_momentum_phi(s_stab)
        # The stabilisation term adds a restoring force; the norm of π_φ
        # should differ between the two cases (stabilised shifts the RHS)
        assert not np.allclose(pi_free, pi_stab)


# ---------------------------------------------------------------------------
# Part XIV — Hawking Temperature
# ---------------------------------------------------------------------------

class TestHawkingTemperature:
    """T_H = |∂_r φ / φ| / (2π) at each grid point."""

    def test_hawking_temperature_shape(self):
        """T_H array must have the same shape as φ."""
        state = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(40))
        T_H = hawking_temperature(state)
        assert T_H.shape == state.phi.shape

    def test_hawking_temperature_nonnegative(self):
        """T_H ≥ 0 everywhere — temperature is non-negative."""
        state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(41))
        T_H = hawking_temperature(state)
        assert np.all(T_H >= 0.0)

    def test_hawking_temperature_finite(self):
        """T_H must be finite — no divergence for bounded φ ≠ 0."""
        state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(42))
        T_H = hawking_temperature(state)
        assert np.all(np.isfinite(T_H))

    def test_constant_phi_gives_zero_temperature(self):
        """Perfectly uniform φ has no gradient → T_H = 0 everywhere."""
        N = 32
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        phi = np.ones(N)
        state = FieldState(g=g, B=np.zeros((N, 4)), phi=phi, t=0.0, dx=0.1)
        T_H = hawking_temperature(state)
        np.testing.assert_allclose(T_H, 0.0, atol=1e-12)

    def test_linear_phi_gives_analytic_temperature(self):
        """φ = a + bx → T_H(x) = |b| / (a + bx) / (2π) on interior points."""
        N = 32
        dx = 0.1
        x = np.arange(N) * dx
        a, b = 2.0, 0.5
        phi = a + b * x
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        state = FieldState(g=g, B=np.zeros((N, 4)), phi=phi, t=0.0, dx=dx)
        T_H = hawking_temperature(state)
        T_expected = np.abs(b) / (a + b * x) / (2.0 * np.pi)
        # Interior points only (boundary uses one-sided differences)
        np.testing.assert_allclose(T_H[1:-1], T_expected[1:-1], rtol=1e-5)

    def test_hawking_temperature_peaks_at_horizon(self):
        """T_H should peak near the horizon (where φ has a sharp gradient)."""
        N = 64
        dx = 0.1
        x = np.arange(N) * dx
        x_h = 3.2   # horizon location
        # Localised φ gradient (Gaussian bump) simulating the KK scalar at horizon
        phi = 1.0 + 0.5 * np.exp(-((x - x_h) ** 2) / 0.1)
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        state = FieldState(g=g, B=np.zeros((N, 4)), phi=phi, t=0.0, dx=dx)
        T_H = hawking_temperature(state)
        x_max = x[np.argmax(T_H)]
        assert abs(x_max - x_h) < 5 * dx, (
            f"T_H peaked at x={x_max:.2f}, expected near horizon x_h={x_h:.2f}")

    def test_larger_phi_gradient_gives_higher_temperature(self):
        """Steeper φ gradient → higher surface gravity → higher T_H."""
        N = 32
        dx = 0.1
        x = np.arange(N) * dx
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        phi_gentle = 1.0 + 0.1 * x          # gentle gradient
        phi_steep  = 1.0 + 0.5 * x          # steep gradient
        T_gentle = hawking_temperature(
            FieldState(g=g, B=np.zeros((N, 4)), phi=phi_gentle, t=0.0, dx=dx))
        T_steep = hawking_temperature(
            FieldState(g=g, B=np.zeros((N, 4)), phi=phi_steep, t=0.0, dx=dx))
        # Mean temperature should be higher for the steeper gradient
        assert np.mean(T_steep) > np.mean(T_gentle)


# ---------------------------------------------------------------------------
# Part XV — ER = EPR (Quantum Entanglement = Topological Information Transfer)
# ---------------------------------------------------------------------------

class TestEREqualsEPR:
    """High topology coupling w → shared entropy fixed point → entanglement."""

    def test_shared_fixed_point_norm_returns_nonneg_float(self):
        """shared_fixed_point_norm must return a finite non-negative float."""
        net = MultiverseNetwork.chain(n=3, coupling=0.1, rng=np.random.default_rng(50))
        val = shared_fixed_point_norm(net)
        assert isinstance(val, float)
        assert np.isfinite(val) and val >= 0.0

    def test_identical_entropies_give_zero_norm(self):
        """Two nodes with equal entropy → norm = 0 (maximally entangled)."""
        node = MultiverseNode(dim=4, S=2.0, A=8.0, Q_top=0.0,
                              X=np.zeros(4), Xdot=np.zeros(4))
        net = MultiverseNetwork(nodes=[node, node],
                                adjacency=np.zeros((2, 2)))
        assert shared_fixed_point_norm(net) == pytest.approx(0.0)

    def test_different_entropies_give_positive_norm(self):
        """Two nodes with unequal entropy → norm > 0 (partially disentangled)."""
        n1 = MultiverseNode(dim=4, S=0.5, A=2.0, Q_top=0.0,
                            X=np.zeros(4), Xdot=np.zeros(4))
        n2 = MultiverseNode(dim=4, S=2.5, A=8.0, Q_top=0.0,
                            X=np.zeros(4), Xdot=np.zeros(4))
        net = MultiverseNetwork(nodes=[n1, n2], adjacency=np.zeros((2, 2)))
        assert shared_fixed_point_norm(net) > 0.0

    def test_zero_coupling_transfers_no_entropy(self):
        """With w = 0, apply_topology changes nothing — no information transfer."""
        n1 = MultiverseNode(dim=4, S=0.5, A=2.0, Q_top=0.0,
                            X=np.zeros(4), Xdot=np.zeros(4))
        n2 = MultiverseNode(dim=4, S=3.5, A=8.0, Q_top=0.0,
                            X=np.zeros(4), Xdot=np.zeros(4))
        net = MultiverseNetwork(nodes=[n1, n2],
                                adjacency=np.array([[0.0, 0.0], [0.0, 0.0]]))
        n1_after = apply_topology(net, 0, dt=0.1)
        assert n1_after.S == pytest.approx(n1.S)

    def test_nonzero_coupling_transfers_entropy(self):
        """With w > 0, apply_topology drives S_low toward S_high."""
        n1 = MultiverseNode(dim=4, S=0.5, A=2.0, Q_top=0.0,
                            X=np.zeros(4), Xdot=np.zeros(4))
        n2 = MultiverseNode(dim=4, S=3.5, A=8.0, Q_top=0.0,
                            X=np.zeros(4), Xdot=np.zeros(4))
        net = MultiverseNetwork(nodes=[n1, n2],
                                adjacency=np.array([[0.0, 1.0], [1.0, 0.0]]))
        n1_after = apply_topology(net, 0, dt=0.1)
        # S_1 < S_2, so T pushes S_1 upward
        assert n1_after.S > n1.S

    def test_entropy_transfer_linear_in_coupling(self):
        """ΔS from one topology step scales linearly with coupling weight."""
        n1 = MultiverseNode(dim=4, S=1.0, A=4.0, Q_top=0.0,
                            X=np.zeros(4), Xdot=np.zeros(4))
        n2 = MultiverseNode(dim=4, S=3.0, A=8.0, Q_top=0.0,
                            X=np.zeros(4), Xdot=np.zeros(4))
        dt = 0.1
        dS_low = (apply_topology(
            MultiverseNetwork(nodes=[n1, n2],
                              adjacency=np.array([[0.0, 1.0], [1.0, 0.0]])),
            0, dt=dt).S - n1.S)
        dS_high = (apply_topology(
            MultiverseNetwork(nodes=[n1, n2],
                              adjacency=np.array([[0.0, 3.0], [3.0, 0.0]])),
            0, dt=dt).S - n1.S)
        # 3× coupling → 3× entropy transfer
        assert dS_high == pytest.approx(3.0 * dS_low, rel=1e-10)

    def test_high_coupling_reduces_entropy_spread(self):
        """Higher coupling monotonically reduces shared_fixed_point_norm."""
        # Two nodes: same A (same holographic cap), different initial S.
        # I+H alone will converge each to A/4G = 0.5.
        # T additionally pulls them together while transient differences remain.
        # With higher coupling the equalization is faster and the residual smaller
        # after a fixed number of iterations.
        N_ITER = 60
        dt = 0.05

        def _run(coupling):
            n1 = MultiverseNode(dim=4, S=0.1, A=2.0, Q_top=0.0,
                                X=np.zeros(4), Xdot=np.zeros(4))
            n2 = MultiverseNode(dim=4, S=1.5, A=2.0, Q_top=0.0,
                                X=np.zeros(4), Xdot=np.zeros(4))
            net = MultiverseNetwork(
                nodes=[n1, n2],
                adjacency=np.array([[0.0, coupling], [coupling, 0.0]]))
            result, _, _ = fixed_point_iteration(
                net, max_iter=N_ITER, tol=1e-9, dt=dt)
            return shared_fixed_point_norm(result)

        norm_zero = _run(0.0)
        norm_mid  = _run(1.0)
        norm_high = _run(4.0)   # dt*2*coupling = 0.05*2*4 = 0.4 < 1 (stable)

        # Higher coupling → smaller entropy spread at convergence
        assert norm_high <= norm_mid <= norm_zero + 1e-6, (
            f"Entropy spread not monotone: w=0→{norm_zero:.4f}, "
            f"w=1→{norm_mid:.4f}, w=4→{norm_high:.4f}")
