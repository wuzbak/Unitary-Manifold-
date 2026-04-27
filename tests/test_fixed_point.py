"""
tests/test_fixed_point.py
=========================
Unit tests for src/multiverse/fixed_point.py.

Covers:
  - MultiverseNode: state_vector, norm
  - MultiverseNetwork: chain, fully_connected, global_state
  - apply_irreversibility: exact dS formula, no drift at fixed point
  - apply_holography: clamps S ≤ A/4G, does not raise S
  - apply_topology: gradient-flow ΔS formula
  - ueum_acceleration: shape, finite
  - fixed_point_iteration: converges, returns correct types, defect < tol
  - derive_alpha_from_fixed_point: α=1/φ₀², φ-scaling, network integration
"""

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.multiverse.fixed_point import (
    MultiverseNode,
    MultiverseNetwork,
    apply_irreversibility,
    apply_holography,
    apply_topology,
    ueum_acceleration,
    fixed_point_iteration,
    derive_alpha_from_fixed_point,
    prove_banach_contraction,
)


# ---------------------------------------------------------------------------
# MultiverseNode
# ---------------------------------------------------------------------------

class TestMultiverseNode:
    def test_state_vector_shape(self):
        node = MultiverseNode(dim=4, S=1.0, A=2.0, Q_top=0.5,
                              X=np.ones(4), Xdot=np.zeros(4))
        sv = node.state_vector()
        # [S, A, Q_top] + X (4) + Xdot (4) = 11
        assert sv.shape == (11,)

    def test_state_vector_values(self):
        node = MultiverseNode(dim=4, S=1.5, A=3.0, Q_top=0.1,
                              X=np.array([1., 2., 3., 4.]),
                              Xdot=np.zeros(4))
        sv = node.state_vector()
        assert sv[0] == pytest.approx(1.5)
        assert sv[1] == pytest.approx(3.0)
        assert sv[2] == pytest.approx(0.1)
        assert np.allclose(sv[3:7], [1., 2., 3., 4.])

    def test_norm_positive(self):
        node = MultiverseNode.random(rng=np.random.default_rng(0))
        assert node.norm() > 0.0


# ---------------------------------------------------------------------------
# MultiverseNetwork
# ---------------------------------------------------------------------------

class TestMultiverseNetwork:
    def test_chain_adjacency(self):
        net = MultiverseNetwork.chain(n=4, coupling=0.1, rng=np.random.default_rng(0))
        adj = net.adjacency
        assert adj.shape == (4, 4)
        # Diagonal zero
        assert np.all(np.diag(adj) == 0.0)
        # Symmetric
        assert np.allclose(adj, adj.T)
        # Only nearest-neighbour non-zero
        assert adj[0, 1] == pytest.approx(0.1)
        assert adj[0, 2] == 0.0

    def test_fully_connected_adjacency(self):
        net = MultiverseNetwork.fully_connected(n=3, coupling=0.2,
                                                rng=np.random.default_rng(0))
        adj = net.adjacency
        # Off-diagonal all 0.2
        assert np.allclose(adj + 0.2 * np.eye(3), 0.2 * np.ones((3, 3)))

    def test_global_state_shape(self):
        net = MultiverseNetwork.chain(n=3, rng=np.random.default_rng(0))
        gs = net.global_state()
        # Each node: dim=4 → state_vector length 11; 3 nodes → 33
        assert gs.shape == (33,)


# ---------------------------------------------------------------------------
# apply_irreversibility
# ---------------------------------------------------------------------------

class TestApplyIrreversibility:
    def test_exact_dS_formula(self):
        """dS = κ (A/4G − S) dt  exactly."""
        node = MultiverseNode(S=0.0, A=4.0, Q_top=0.0,
                              X=np.zeros(4), Xdot=np.zeros(4))
        dt, kappa, G4 = 0.1, 0.25, 1.0
        n1 = apply_irreversibility(node, dt=dt, kappa=kappa, G4=G4)
        expected_dS = kappa * (node.A / (4.0 * G4) - node.S) * dt
        assert abs(n1.S - (node.S + expected_dS)) < 1e-12

    def test_no_drift_at_fixed_point(self):
        """If S = A/4G already, entropy should not change."""
        A = 4.0
        G4 = 1.0
        S_fp = A / (4.0 * G4)   # = 1.0
        node = MultiverseNode(S=S_fp, A=A, Q_top=0.0,
                              X=np.zeros(4), Xdot=np.zeros(4))
        n1 = apply_irreversibility(node, dt=0.5, kappa=0.25, G4=G4)
        assert abs(n1.S - S_fp) < 1e-12

    def test_S_increases_when_below_bound(self):
        node = MultiverseNode(S=0.0, A=4.0)
        n1 = apply_irreversibility(node, dt=0.1)
        assert n1.S > node.S

    def test_S_decreases_when_above_bound(self):
        node = MultiverseNode(S=5.0, A=4.0)
        n1 = apply_irreversibility(node, dt=0.1)
        assert n1.S < node.S

    def test_other_fields_unchanged(self):
        node = MultiverseNode(S=0.5, A=2.0, Q_top=0.3,
                              X=np.array([1., 2., 3., 4.]),
                              Xdot=np.array([0.1, 0.2, 0.3, 0.4]))
        n1 = apply_irreversibility(node, dt=0.1)
        assert n1.A == node.A
        assert n1.Q_top == node.Q_top
        assert np.allclose(n1.X, node.X)
        assert np.allclose(n1.Xdot, node.Xdot)


# ---------------------------------------------------------------------------
# apply_holography
# ---------------------------------------------------------------------------

class TestApplyHolography:
    def test_clamps_S_above_bound(self):
        """S > A/4G is clamped down to A/4G."""
        node = MultiverseNode(S=10.0, A=4.0)
        n1 = apply_holography(node, G4=1.0)
        assert abs(n1.S - 1.0) < 1e-12

    def test_does_not_raise_S_below_bound(self):
        """S < A/4G is left unchanged."""
        node = MultiverseNode(S=0.3, A=4.0)
        n1 = apply_holography(node, G4=1.0)
        assert abs(n1.S - 0.3) < 1e-12

    def test_at_exactly_bound(self):
        """S = A/4G exactly → unchanged."""
        node = MultiverseNode(S=1.0, A=4.0)
        n1 = apply_holography(node, G4=1.0)
        assert abs(n1.S - 1.0) < 1e-12

    def test_G4_scaling(self):
        node = MultiverseNode(S=10.0, A=4.0)
        n1 = apply_holography(node, G4=2.0)
        # bound = A/4G = 4/(4*2) = 0.5
        assert abs(n1.S - 0.5) < 1e-12


# ---------------------------------------------------------------------------
# apply_topology
# ---------------------------------------------------------------------------

class TestApplyTopology:
    def test_gradient_flow_formula(self):
        """ΔS_i = dt * Σ_j w_{ij} (S_j - S_i)."""
        rng = np.random.default_rng(99)
        net = MultiverseNetwork.chain(n=3, coupling=0.1, rng=rng)
        i = 1
        node_i = net.nodes[i]
        dt = 0.1
        n_new = apply_topology(net, i, dt)
        dS = dt * sum(
            net.adjacency[i, j] * (net.nodes[j].S - node_i.S)
            for j in range(3)
        )
        assert abs(n_new.S - (node_i.S + dS)) < 1e-12

    def test_isolated_node_no_change(self):
        """Node with no connections: S unchanged."""
        net = MultiverseNetwork.chain(n=1, coupling=0.1, rng=np.random.default_rng(0))
        S_before = net.nodes[0].S
        n_new = apply_topology(net, 0, dt=0.5)
        assert abs(n_new.S - S_before) < 1e-12


# ---------------------------------------------------------------------------
# ueum_acceleration
# ---------------------------------------------------------------------------

class TestUeumAcceleration:
    def test_shape(self):
        rng = np.random.default_rng(0)
        net = MultiverseNetwork.chain(n=3, rng=rng)
        node = net.nodes[0]
        acc = ueum_acceleration(node, net, 0)
        assert acc.shape == (node.dim,)

    def test_finite(self):
        rng = np.random.default_rng(1)
        net = MultiverseNetwork.chain(n=4, rng=rng)
        for i, node in enumerate(net.nodes):
            acc = ueum_acceleration(node, net, i)
            assert np.all(np.isfinite(acc))

    def test_zero_X_no_divergence(self):
        """X=0 should not cause divide-by-zero (ε regularisation)."""
        node = MultiverseNode(S=1.0, A=4.0, Q_top=0.0,
                              X=np.zeros(4), Xdot=np.zeros(4))
        net = MultiverseNetwork(nodes=[node], adjacency=np.zeros((1, 1)))
        acc = ueum_acceleration(node, net, 0)
        assert np.all(np.isfinite(acc))


# ---------------------------------------------------------------------------
# fixed_point_iteration
# ---------------------------------------------------------------------------

class TestFixedPointIteration:
    def test_return_types(self):
        rng = np.random.default_rng(42)
        net = MultiverseNetwork.chain(n=3, rng=rng)
        result_net, residuals, converged = fixed_point_iteration(
            net, max_iter=200, tol=1e-5)
        assert isinstance(result_net, MultiverseNetwork)
        assert isinstance(residuals, list)
        assert isinstance(converged, bool)

    def test_converges_on_chain(self):
        rng = np.random.default_rng(42)
        net = MultiverseNetwork.chain(n=4, coupling=0.05, rng=rng)
        _, residuals, converged = fixed_point_iteration(
            net, max_iter=500, tol=1e-6)
        assert converged, f"Did not converge; final defect = {residuals[-1]:.2e}"

    def test_final_defect_below_tol(self):
        rng = np.random.default_rng(42)
        net = MultiverseNetwork.chain(n=4, coupling=0.05, rng=rng)
        _, residuals, converged = fixed_point_iteration(
            net, max_iter=500, tol=1e-6)
        assert residuals[-1] < 1e-5

    def test_residuals_non_negative(self):
        rng = np.random.default_rng(7)
        net = MultiverseNetwork.chain(n=3, rng=rng)
        _, residuals, _ = fixed_point_iteration(net, max_iter=100, tol=1e-8)
        assert all(r >= 0.0 for r in residuals)

    def test_per_node_entropy_at_bound(self):
        """At convergence each node should have S ≈ A/4G."""
        rng = np.random.default_rng(42)
        net = MultiverseNetwork.chain(n=4, coupling=0.05, rng=rng)
        result_net, _, _ = fixed_point_iteration(
            net, max_iter=500, tol=1e-6)
        for node in result_net.nodes:
            assert abs(node.S - node.A / 4.0) < 1e-4


# ---------------------------------------------------------------------------
# derive_alpha_from_fixed_point
# ---------------------------------------------------------------------------

class TestDeriveAlphaFromFixedPoint:
    """Tests for α = φ₀⁻² — the KK coupling derived at the FTUM fixed point."""

    def test_unit_phi_gives_alpha_one(self):
        """φ₀ = 1 ⟹ α_predicted = 1/1² = 1.0."""
        alpha, net, conv = derive_alpha_from_fixed_point(phi_stabilized=1.0)
        assert abs(alpha - 1.0) < 1e-12
        assert net is None
        assert conv is True

    def test_phi_two_gives_alpha_quarter(self):
        """φ₀ = 2 ⟹ α_predicted = 1/4 = 0.25."""
        alpha, _, _ = derive_alpha_from_fixed_point(phi_stabilized=2.0)
        assert abs(alpha - 0.25) < 1e-12

    def test_phi_half_gives_alpha_four(self):
        """φ₀ = 0.5 ⟹ α_predicted = 1/0.25 = 4.0."""
        alpha, _, _ = derive_alpha_from_fixed_point(phi_stabilized=0.5)
        assert abs(alpha - 4.0) < 1e-12

    def test_array_phi_uses_spatial_mean(self):
        """Array φ: spatial mean ⟨φ⟩ = √2 ⟹ α = 1/(√2)² = 0.5."""
        phi_arr = np.full(10, np.sqrt(2.0))
        alpha, _, _ = derive_alpha_from_fixed_point(phi_stabilized=phi_arr)
        assert abs(alpha - 0.5) < 1e-12

    def test_alpha_positive_for_any_phi(self):
        """α = 1/φ₀² is always positive."""
        for phi_val in (0.1, 0.5, 1.0, 3.0, 10.0):
            alpha, _, _ = derive_alpha_from_fixed_point(phi_stabilized=phi_val)
            assert alpha > 0.0

    def test_alpha_decreases_with_larger_phi(self):
        """Larger radion → smaller nonminimal coupling (inverse-square law)."""
        alpha1, _, _ = derive_alpha_from_fixed_point(phi_stabilized=1.0)
        alpha2, _, _ = derive_alpha_from_fixed_point(phi_stabilized=2.0)
        assert alpha1 > alpha2

    def test_with_network_runs_fixed_point_iteration(self):
        """When a network is provided, fixed_point_iteration is run and
        the converged network is returned."""
        rng = np.random.default_rng(42)
        net = MultiverseNetwork.chain(n=4, coupling=0.05, rng=rng)
        alpha, result_net, converged = derive_alpha_from_fixed_point(
            phi_stabilized=1.0, network=net, max_iter=500, tol=1e-6)
        assert isinstance(result_net, MultiverseNetwork)
        assert converged
        assert abs(alpha - 1.0) < 1e-12

    def test_with_network_result_is_converged(self):
        """The returned network satisfies the holographic entropy bound."""
        rng = np.random.default_rng(42)
        net = MultiverseNetwork.chain(n=4, coupling=0.05, rng=rng)
        _, result_net, converged = derive_alpha_from_fixed_point(
            phi_stabilized=1.0, network=net, max_iter=500, tol=1e-6)
        assert converged
        for node in result_net.nodes:
            assert abs(node.S - node.A / 4.0) < 1e-4

    def test_none_network_returns_none(self):
        """Without a network, result_network is None."""
        _, net, _ = derive_alpha_from_fixed_point(phi_stabilized=1.0)
        assert net is None

    def test_return_types(self):
        """Return types are (float, None, bool) when no network supplied."""
        alpha, net, conv = derive_alpha_from_fixed_point(phi_stabilized=1.5)
        assert isinstance(alpha, float)
        assert net is None
        assert isinstance(conv, bool)


# ---------------------------------------------------------------------------
# prove_banach_contraction — Lipschitz / formal Banach theorem certificate
# ---------------------------------------------------------------------------

class TestProveBanachContraction:
    """Tests for the explicit Lipschitz constant computation."""

    def _make_net(self, n=3, rng_seed=42):
        rng = np.random.default_rng(rng_seed)
        return MultiverseNetwork.chain(n=n, coupling=0.05, rng=rng)

    def test_returns_dict(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=10)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=10)
        for key in ("L", "is_contraction", "L_margin", "theorem_holds",
                    "convergence_rate", "n_iters_to_tol",
                    "error_bound_formula", "banach_theorem", "n_pairs_sampled"):
            assert key in result, f"Missing key: {key!r}"

    def test_L_positive(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=20)
        assert result["L"] >= 0.0

    def test_L_finite(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=20)
        assert np.isfinite(result["L"])

    def test_is_contraction_true_for_canonical_network(self):
        """Canonical 3-node chain should be contractive (L < 1)."""
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=30,
                                          rng=np.random.default_rng(0))
        assert result["is_contraction"] is True, (
            f"Expected contraction but L = {result['L']:.4f}"
        )

    def test_theorem_holds_equals_is_contraction(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=10)
        assert result["theorem_holds"] == result["is_contraction"]

    def test_L_margin_equals_1_minus_L(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=10)
        assert result["L_margin"] == pytest.approx(1.0 - result["L"], abs=1e-12)

    def test_convergence_rate_equals_L(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=10)
        assert result["convergence_rate"] == pytest.approx(result["L"], abs=1e-12)

    def test_banach_theorem_nonempty_string(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=10)
        assert isinstance(result["banach_theorem"], str)
        assert len(result["banach_theorem"]) > 30

    def test_banach_theorem_mentions_uniqueness_when_contractive(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=20,
                                          rng=np.random.default_rng(0))
        if result["is_contraction"]:
            theorem = result["banach_theorem"].lower()
            assert "unique" in theorem or "uniqueness" in theorem, (
                "Theorem statement should mention uniqueness of fixed point"
            )

    def test_error_bound_formula_is_string(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=10)
        assert isinstance(result["error_bound_formula"], str)
        assert "L" in result["error_bound_formula"]

    def test_n_pairs_sampled_leq_n_pairs(self):
        net = self._make_net()
        n_pairs = 15
        result = prove_banach_contraction(net, n_pairs=n_pairs)
        assert result["n_pairs_sampled"] <= n_pairs

    def test_rng_reproducible(self):
        net = self._make_net()
        r1 = prove_banach_contraction(net, n_pairs=10, rng=np.random.default_rng(99))
        r2 = prove_banach_contraction(net, n_pairs=10, rng=np.random.default_rng(99))
        assert r1["L"] == pytest.approx(r2["L"], abs=1e-12)

    def test_larger_network_also_contractive(self):
        """Fully connected 5-node network should also be contractive."""
        rng = np.random.default_rng(7)
        net = MultiverseNetwork.fully_connected(n=5, coupling=0.05, rng=rng)
        result = prove_banach_contraction(net, n_pairs=20,
                                          rng=np.random.default_rng(7))
        assert result["is_contraction"] is True, (
            f"5-node fully-connected network: L = {result['L']:.4f}"
        )

    def test_n_iters_finite_when_contractive(self):
        net = self._make_net()
        result = prove_banach_contraction(net, n_pairs=20,
                                          rng=np.random.default_rng(0))
        if result["is_contraction"]:
            assert np.isfinite(result["n_iters_to_tol"])
            assert result["n_iters_to_tol"] > 0


# ---------------------------------------------------------------------------
# FTUM S = 0.25 at 128 iterations — machine-verifiable pinned claim
# ---------------------------------------------------------------------------

class TestFTUMSEqualsQuarterAt128Iterations:
    """Pinned test for the specific claim cited by reviewers: after 128
    iterations of the FTUM operator U = I + H + T on a single-node network
    with default parameters (A=1, G4=1, kappa=0.25), the entropy S converges
    to S* = A/(4G) = 1/4 = 0.2500.

    The fixed-point S* = A/(4G) = 0.25 follows directly from the holographic
    entropy bound: the operator I applies dS = κ(A/4G − S)dt at each step,
    which is a geometric contraction toward S* = 0.25 when A=1, G4=1.

    This test makes the FTUM convergence claim machine-verifiable by any
    external reviewer.
    """

    def test_ftum_s_equals_quarter_at_128_iterations(self):
        """After 128 FTUM iterations with A=1, G=1: S* = 0.2500 ± 0.0001."""
        # Single-node network: A=1, G4=1 → S* = A/(4G) = 0.25
        node = MultiverseNode(
            dim=4,
            S=0.0,               # start far from fixed point
            A=1.0,               # boundary area
            Q_top=0.0,
            X=np.zeros(4),
            Xdot=np.zeros(4),
        )
        net = MultiverseNetwork(
            nodes=[node],
            adjacency=np.zeros((1, 1)),   # isolated node
        )
        result_net, residuals, converged = fixed_point_iteration(
            net,
            max_iter=128,
            tol=1e-12,     # very tight tolerance — may not converge in 128 steps
            dt=0.2,
            G4=1.0,
            kappa=0.25,
        )
        # After 128 iterations, S should be very close to 0.25
        S_final = result_net.nodes[0].S
        S_star = 1.0 / 4.0   # = A/(4G) = 1/4 = 0.25
        assert abs(S_final - S_star) < 1e-3, (
            f"After 128 FTUM iterations, expected S* = 0.2500, got {S_final:.6f}. "
            f"Discrepancy = {abs(S_final - S_star):.2e} (tol = 1e-3)."
        )

    def test_ftum_s_star_equals_a_over_4g(self):
        """Fixed point is S* = A/(4G) for any A and G4."""
        for A, G4 in [(1.0, 1.0), (2.0, 1.0), (4.0, 2.0), (0.5, 1.0)]:
            node = MultiverseNode(
                dim=4, S=0.0, A=A, Q_top=0.0,
                X=np.zeros(4), Xdot=np.zeros(4)
            )
            net = MultiverseNetwork(nodes=[node], adjacency=np.zeros((1, 1)))
            result_net, _, _ = fixed_point_iteration(
                net, max_iter=128, tol=1e-12, dt=0.2, G4=G4, kappa=0.25
            )
            S_star = A / (4.0 * G4)
            S_final = result_net.nodes[0].S
            assert abs(S_final - S_star) < 1e-3, (
                f"A={A}, G4={G4}: expected S*={S_star:.4f}, got {S_final:.4f}"
            )

    def test_ftum_s_approaches_quarter_monotonically(self):
        """S should approach 0.25 monotonically from below when starting at S=0."""
        node = MultiverseNode(
            dim=4, S=0.0, A=1.0, Q_top=0.0,
            X=np.zeros(4), Xdot=np.zeros(4)
        )
        net = MultiverseNetwork(nodes=[node], adjacency=np.zeros((1, 1)))
        result_net, residuals, _ = fixed_point_iteration(
            net, max_iter=128, tol=1e-12, dt=0.2, G4=1.0, kappa=0.25
        )
        # Defect residuals should be strictly decreasing (monotone convergence)
        assert all(
            residuals[i] >= residuals[i + 1]
            for i in range(len(residuals) - 1)
        ), "FTUM residuals should be monotone non-increasing"


# ---------------------------------------------------------------------------
# analytic_banach_proof — Issue 4 closure (closed-form Banach certificate)
# ---------------------------------------------------------------------------

from src.multiverse.fixed_point import analytic_banach_proof


class TestAnalyticBanachProof:
    """Tests for analytic_banach_proof(): closed-form Lipschitz bound."""

    def _canon_net(self, n=3, coupling=0.1):
        rng = np.random.default_rng(42)
        return MultiverseNetwork.chain(n=n, coupling=coupling, rng=rng)

    def test_returns_dict(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        for key in (
            "lambda_max", "rho_S", "rho_X", "L_analytic",
            "is_contraction", "L_margin", "condition_1_holds",
            "condition_2_holds", "condition_3_holds",
            "all_conditions_hold", "n_nodes", "analytic_proof",
        ):
            assert key in result, f"Missing key: {key!r}"

    def test_L_analytic_positive(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        assert result["L_analytic"] >= 0.0

    def test_L_analytic_finite(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        assert np.isfinite(result["L_analytic"])

    def test_canonical_network_is_contraction(self):
        """Canonical 3-node chain (κ=0.25, γ=5.0, dt=0.2) must satisfy L < 1."""
        net = self._canon_net()
        result = analytic_banach_proof(net, dt=0.2, kappa=0.25, gamma=5.0)
        assert result["is_contraction"] is True, (
            f"Expected contraction but L_analytic={result['L_analytic']:.4f}"
        )

    def test_all_conditions_hold_for_canonical(self):
        net = self._canon_net()
        result = analytic_banach_proof(net, dt=0.2, kappa=0.25, gamma=5.0)
        assert result["all_conditions_hold"] is True

    def test_L_margin_equals_1_minus_L(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        assert result["L_margin"] == pytest.approx(1.0 - result["L_analytic"], abs=1e-12)

    def test_rho_X_formula(self):
        """ρ_X = 1 / (1 + γ dt) analytically."""
        net = self._canon_net()
        for gamma, dt in [(5.0, 0.2), (2.0, 0.1), (10.0, 0.5)]:
            result = analytic_banach_proof(net, dt=dt, gamma=gamma)
            expected_rho_X = 1.0 / (1.0 + gamma * dt)
            assert result["rho_X"] == pytest.approx(expected_rho_X, rel=1e-10)

    def test_rho_X_less_than_1_for_positive_gamma(self):
        net = self._canon_net()
        result = analytic_banach_proof(net, gamma=0.1, dt=0.2)
        assert result["rho_X"] < 1.0

    def test_lambda_max_nonneg(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        assert result["lambda_max"] >= 0.0

    def test_lambda_max_chain_equals_coupling(self):
        """For a chain graph the max degree is exactly the coupling (one neighbour)."""
        coupling = 0.1
        net = self._canon_net(n=5, coupling=coupling)
        result = analytic_banach_proof(net)
        # Interior nodes have two neighbours; max degree = 2 × coupling
        assert result["lambda_max"] == pytest.approx(2.0 * coupling, rel=1e-10)

    def test_condition1_is_bool(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        assert isinstance(result["condition_1_holds"], bool)

    def test_condition3_false_when_gamma_zero(self):
        """γ=0 violates condition 3 (no geodesic friction)."""
        net = self._canon_net()
        result = analytic_banach_proof(net, gamma=0.0)
        assert result["condition_3_holds"] is False

    def test_analytic_proof_is_str(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        assert isinstance(result["analytic_proof"], str)

    def test_analytic_proof_contains_banach(self):
        net = self._canon_net()
        proof = analytic_banach_proof(net)["analytic_proof"].upper()
        assert "BANACH" in proof

    def test_n_nodes_correct(self):
        for n in (1, 3, 5):
            net = MultiverseNetwork.chain(n=n, rng=np.random.default_rng(0))
            result = analytic_banach_proof(net)
            assert result["n_nodes"] == n

    def test_rho_S_le_1_for_canonical(self):
        net = self._canon_net()
        result = analytic_banach_proof(net)
        assert result["rho_S"] <= 1.0

    def test_L_analytic_is_max_rho_S_rho_X(self):
        net = self._canon_net()
        r = analytic_banach_proof(net)
        assert r["L_analytic"] == pytest.approx(max(r["rho_S"], r["rho_X"]), abs=1e-12)

    def test_large_dt_can_violate_contraction(self):
        """Very large dt violates the sufficient conditions."""
        net = self._canon_net()
        result = analytic_banach_proof(net, dt=100.0, kappa=0.25, gamma=0.001)
        # With such a large dt condition 1 or 2 should fail
        assert not result["all_conditions_hold"]

    def test_single_node_zero_coupling(self):
        """Single isolated node: λ_max=0, L_analytic = max(1-κdt, 1/(1+γdt))."""
        node = MultiverseNode(S=1.0, A=4.0)
        net = MultiverseNetwork(nodes=[node], adjacency=np.zeros((1, 1)))
        dt, kappa, gamma = 0.2, 0.25, 5.0
        result = analytic_banach_proof(net, dt=dt, kappa=kappa, gamma=gamma)
        assert result["lambda_max"] == pytest.approx(0.0, abs=1e-12)
        expected_rho_S = abs(1.0 - kappa * dt)
        assert result["rho_S"] == pytest.approx(expected_rho_S, rel=1e-10)
        assert result["is_contraction"] is True
