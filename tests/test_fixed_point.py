"""
tests/test_fixed_point.py
=========================
Tests for src/multiverse/fixed_point.py — MultiverseNode, MultiverseNetwork,
individual U operators (I, H, T), and the FTUM fixed-point iteration.
"""

import numpy as np
import pytest

from src.multiverse.fixed_point import (
    MultiverseNode,
    MultiverseNetwork,
    apply_irreversibility,
    apply_holography,
    apply_topology,
    ueum_acceleration,
    fixed_point_iteration,
    _apply_U,
)


# ---------------------------------------------------------------------------
# MultiverseNode
# ---------------------------------------------------------------------------

class TestMultiverseNode:
    def test_default_state_vector_length(self):
        node = MultiverseNode(dim=4)
        sv = node.state_vector()
        # 3 scalars (S, A, Q_top) + 4 X + 4 Xdot = 11
        assert sv.shape == (11,)

    def test_random_node_finite(self):
        node = MultiverseNode.random(rng=np.random.default_rng(0))
        assert np.all(np.isfinite(node.state_vector()))

    def test_norm_non_negative(self):
        node = MultiverseNode.random(rng=np.random.default_rng(1))
        assert node.norm() >= 0.0


# ---------------------------------------------------------------------------
# MultiverseNetwork
# ---------------------------------------------------------------------------

class TestMultiverseNetwork:
    def test_chain_adjacency_symmetric(self, chain_network):
        adj = chain_network.adjacency
        np.testing.assert_array_equal(adj, adj.T)

    def test_chain_adjacency_zero_diagonal(self, chain_network):
        np.testing.assert_array_equal(
            np.diag(chain_network.adjacency), np.zeros(chain_network.n_nodes())
        )

    def test_chain_n_nodes(self, chain_network):
        assert chain_network.n_nodes() == 5

    def test_fully_connected_all_nonzero_off_diag(self, full_network):
        n = full_network.n_nodes()
        adj = full_network.adjacency
        for i in range(n):
            for j in range(n):
                if i != j:
                    assert adj[i, j] > 0.0

    def test_global_state_length(self, chain_network):
        gs = chain_network.global_state()
        # Each node: 3 + 4 + 4 = 11 components; 5 nodes → 55
        assert gs.shape == (55,)


# ---------------------------------------------------------------------------
# Operator I — apply_irreversibility
# ---------------------------------------------------------------------------

class TestApplyIrreversibility:
    def test_entropy_increases(self):
        node = MultiverseNode(S=1.0, A=2.0, Q_top=0.0)
        node_new = apply_irreversibility(node, dt=0.1, kappa=0.25)
        assert node_new.S > node.S

    def test_other_fields_unchanged(self):
        node = MultiverseNode(S=1.0, A=2.0, Q_top=0.5,
                              X=np.array([1., 2., 3., 4.]),
                              Xdot=np.array([0.1, 0.2, 0.3, 0.4]))
        node_new = apply_irreversibility(node, dt=0.1)
        assert node_new.A == node.A
        assert node_new.Q_top == node.Q_top
        np.testing.assert_array_equal(node_new.X, node.X)

    def test_zero_area_no_entropy_growth(self):
        node = MultiverseNode(S=1.0, A=0.0)
        node_new = apply_irreversibility(node, dt=0.1, kappa=0.25)
        assert node_new.S == node.S


# ---------------------------------------------------------------------------
# Operator H — apply_holography
# ---------------------------------------------------------------------------

class TestApplyHolography:
    def test_entropy_clamped_to_holographic_bound(self):
        node = MultiverseNode(S=100.0, A=1.0)
        node_new = apply_holography(node, G4=1.0)
        assert node_new.S <= node.A / 4.0 + 1e-12

    def test_entropy_below_bound_unchanged(self):
        node = MultiverseNode(S=0.01, A=1.0)
        node_new = apply_holography(node, G4=1.0)
        assert abs(node_new.S - 0.01) < 1e-14

    def test_entropy_non_negative(self):
        node = MultiverseNode(S=0.0, A=4.0)
        node_new = apply_holography(node, G4=1.0)
        assert node_new.S >= 0.0


# ---------------------------------------------------------------------------
# Operator T — apply_topology
# ---------------------------------------------------------------------------

class TestApplyTopology:
    def test_isolated_node_no_change(self):
        """A node with no connections (all adjacency = 0) should not change."""
        nodes = [MultiverseNode(S=1.0), MultiverseNode(S=2.0)]
        adj = np.zeros((2, 2))
        net = MultiverseNetwork(nodes=nodes, adjacency=adj)
        node_new = apply_topology(net, 0, dt=0.1)
        assert abs(node_new.S - 1.0) < 1e-14

    def test_entropy_flows_from_high_to_low(self):
        """Information should flow from high-entropy to low-entropy node."""
        nodes = [MultiverseNode(S=0.0), MultiverseNode(S=10.0)]
        adj = np.array([[0.0, 1.0], [1.0, 0.0]])
        net = MultiverseNetwork(nodes=nodes, adjacency=adj)
        node_0_new = apply_topology(net, 0, dt=0.1)
        assert node_0_new.S > 0.0   # entropy increased for low-S node

    def test_returns_correct_type(self, chain_network):
        result = apply_topology(chain_network, 0, dt=0.01)
        assert isinstance(result, MultiverseNode)


# ---------------------------------------------------------------------------
# ueum_acceleration
# ---------------------------------------------------------------------------

class TestUeumAcceleration:
    def test_shape(self, chain_network):
        node = chain_network.nodes[0]
        Xddot = ueum_acceleration(node, chain_network, 0)
        assert Xddot.shape == (node.dim,)

    def test_finite(self, chain_network):
        node = chain_network.nodes[0]
        Xddot = ueum_acceleration(node, chain_network, 0)
        assert np.all(np.isfinite(Xddot))


# ---------------------------------------------------------------------------
# fixed_point_iteration (FTUM)
# ---------------------------------------------------------------------------

class TestFixedPointIteration:
    def test_converges_chain(self, chain_network):
        _, residuals, converged = fixed_point_iteration(
            chain_network, max_iter=5000, tol=5e-2
        )
        assert converged, f"Did not converge; final residual = {residuals[-1]:.2e}"

    def test_converges_fully_connected(self, full_network):
        _, residuals, converged = fixed_point_iteration(
            full_network, max_iter=5000, tol=5e-2
        )
        assert converged, f"Did not converge; final residual = {residuals[-1]:.2e}"

    def test_residuals_decrease(self, chain_network):
        _, residuals, _ = fixed_point_iteration(chain_network, max_iter=200, tol=1e-8)
        # Residuals should be non-increasing on a smoothed basis (last < first)
        assert residuals[-1] < residuals[0]

    def test_returns_network(self, chain_network):
        result, _, _ = fixed_point_iteration(chain_network, max_iter=50, tol=1e-6)
        assert isinstance(result, MultiverseNetwork)

    def test_entropy_finite_after_iteration(self, chain_network):
        result, _, _ = fixed_point_iteration(chain_network, max_iter=100, tol=1e-6)
        for node in result.nodes:
            assert np.isfinite(node.S)

    def test_holographic_bound_respected(self, chain_network):
        """After FTUM iteration, S ≤ A / 4G for every node."""
        result, _, _ = fixed_point_iteration(chain_network, max_iter=200, tol=1e-6)
        for node in result.nodes:
            bound = node.A / 4.0
            assert node.S <= bound + 1e-10, \
                f"Holographic bound violated: S={node.S:.4f} > A/4G={bound:.4f}"

    def test_residual_list_non_empty(self, chain_network):
        _, residuals, _ = fixed_point_iteration(chain_network, max_iter=10, tol=1e-12)
        assert len(residuals) == 10   # didn't converge at such tight tol in 10 iters


# ---------------------------------------------------------------------------
# FTUM physics: second law and self-consistency
# ---------------------------------------------------------------------------

class TestFTUMDynamics:
    def test_irreversibility_monotone_entropy(self):
        """Total network entropy is strictly non-decreasing under pure I steps."""
        rng = np.random.default_rng(55)
        net = MultiverseNetwork.chain(n=4, coupling=0.1, rng=rng)
        S_prev = sum(nd.S for nd in net.nodes)
        for _ in range(10):
            new_nodes = [apply_irreversibility(nd, dt=0.01) for nd in net.nodes]
            net = MultiverseNetwork(nodes=new_nodes, adjacency=net.adjacency.copy())
            S_curr = sum(nd.S for nd in net.nodes)
            assert S_curr >= S_prev - 1e-12, \
                f"Entropy decreased: {S_prev:.6f} → {S_curr:.6f}"
            S_prev = S_curr

    def test_convergence_residuals_overall_decrease(self, chain_network):
        """Average of last 10 residuals must be less than average of first 10."""
        _, residuals, _ = fixed_point_iteration(
            chain_network, max_iter=100, tol=1e-10
        )
        assert len(residuals) >= 20
        assert sum(residuals[-10:]) < sum(residuals[:10])

    def test_fixed_point_self_consistent(self, chain_network):
        """One more U step after convergence changes the state by less than 10×tol."""
        tol = 5e-2
        converged_net, _, converged = fixed_point_iteration(
            chain_network, max_iter=5000, tol=tol
        )
        if not converged:
            pytest.skip("Network did not converge — skip self-consistency check")
        state_before = converged_net.global_state()
        net_after = _apply_U(converged_net, dt=1e-3)
        state_after = net_after.global_state()
        residual = float(np.linalg.norm(state_after - state_before))
        assert residual < tol * 10, \
            f"Fixed point not self-consistent: residual={residual:.4e}"

    def test_topology_conserves_total_entropy(self):
        """T operator redistributes entropy without net creation or loss."""
        nodes = [MultiverseNode(S=float(i + 1)) for i in range(4)]
        adj = np.array([[0, 1, 0, 0],
                        [1, 0, 1, 0],
                        [0, 1, 0, 1],
                        [0, 0, 1, 0]], dtype=float)
        net = MultiverseNetwork(nodes=nodes, adjacency=adj)
        S_before = sum(nd.S for nd in net.nodes)
        # Apply T to all nodes simultaneously (using original states)
        new_nodes = [apply_topology(net, i, dt=0.01) for i in range(4)]
        S_after = sum(nd.S for nd in new_nodes)
        # T is a gradient flow: it redistributes but conserves total entropy
        assert abs(S_after - S_before) < 1e-10, \
            f"T operator changed total entropy by {abs(S_after - S_before):.2e}"
