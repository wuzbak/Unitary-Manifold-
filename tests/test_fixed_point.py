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
