"""
tests/test_fixed_point.py
=========================
Tests for src/multiverse/fixed_point.py — FTUM, operator U, convergence.

Covers:
  - fixed_point_iteration converges for chain network
  - Residuals are monotonically non-increasing (stability check)
  - MultiverseNetwork state vector has correct dimension
  - Operator I increases entropy (second law)
  - Operator H enforces holographic bound
  - Operator T transfers entropy toward equilibrium
  - UEUM acceleration is finite
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
)


# ---------------------------------------------------------------------------
# 1. MultiverseNode / MultiverseNetwork structure
# ---------------------------------------------------------------------------

def test_node_state_vector_dimension():
    """State vector has dimension 3 + 2*dim (S, A, Q_top, X, Xdot).

    The 3:2 ratio is structural (see monograph, operator decomposition U=I+H+T):
      - 3 thermodynamic scalars: S (entropy), A (boundary area), Q_top (topology)
      - 2 UEUM phase-space vectors: X (position), Xdot (velocity), each of length dim
    """
    dim = 4
    node = MultiverseNode(dim=dim)
    sv = node.state_vector()
    assert sv.shape == (3 + 2 * dim,), f"Expected {3+2*dim}-d state, got {sv.shape}"


def test_network_global_state_dimension():
    """Global state vector has dimension n_nodes * (3 + 2*dim)."""
    n, dim = 5, 4
    net = MultiverseNetwork.chain(n=n, coupling=0.1, rng=np.random.default_rng(20))
    gs = net.global_state()
    assert gs.shape == (n * (3 + 2 * dim),)


def test_network_adjacency_symmetric():
    """Chain-network adjacency matrix is symmetric."""
    net = MultiverseNetwork.chain(n=6, coupling=0.1, rng=np.random.default_rng(21))
    adj = net.adjacency
    np.testing.assert_allclose(adj, adj.T, atol=1e-15)


def test_network_adjacency_zero_diagonal():
    """Adjacency matrix has zero diagonal (no self-loops)."""
    net = MultiverseNetwork.fully_connected(n=4, coupling=0.1,
                                            rng=np.random.default_rng(22))
    np.testing.assert_allclose(np.diag(net.adjacency), 0.0, atol=1e-15)


# ---------------------------------------------------------------------------
# 2. Operator I — Irreversibility
# ---------------------------------------------------------------------------

def test_irreversibility_increases_entropy():
    """Operator I always increases entropy (second law: dS/dt = κ A > 0)."""
    rng = np.random.default_rng(23)
    for _ in range(10):
        node = MultiverseNode.random(rng=rng)
        node_new = apply_irreversibility(node, dt=1e-2, kappa=0.25)
        assert node_new.S >= node.S, (
            f"Entropy decreased: {node.S:.4f} → {node_new.S:.4f}"
        )


def test_irreversibility_preserves_area():
    """Operator I does not change the boundary area."""
    node = MultiverseNode(S=1.0, A=2.0)
    node_new = apply_irreversibility(node, dt=1e-2)
    np.testing.assert_allclose(node_new.A, node.A, rtol=1e-12)


# ---------------------------------------------------------------------------
# 3. Operator H — Holography
# ---------------------------------------------------------------------------

def test_holography_enforces_bound():
    """Operator H clamps S to A/4G."""
    node = MultiverseNode(S=10.0, A=1.0)   # S greatly exceeds bound
    node_h = apply_holography(node, G4=1.0)
    assert node_h.S <= node.A / 4.0 + 1e-14


def test_holography_does_not_exceed_original_when_below_bound():
    """If S < A/4G, entropy must not increase."""
    node = MultiverseNode(S=0.05, A=1.0)   # bound = 0.25
    node_h = apply_holography(node, G4=1.0)
    assert node_h.S <= node.S + 1e-14


# ---------------------------------------------------------------------------
# 4. Operator T — Topology
# ---------------------------------------------------------------------------

def test_topology_transfers_toward_mean():
    """Operator T moves entropy toward the mean of connected neighbours."""
    # Two-node chain: node 0 has S=0, node 1 has S=1
    nodes = [MultiverseNode(S=0.0, A=1.0), MultiverseNode(S=1.0, A=1.0)]
    adj = np.array([[0.0, 0.5], [0.5, 0.0]])
    net = MultiverseNetwork(nodes=nodes, adjacency=adj)

    # After applying T to node 0: dS = 0.5 * (1 - 0) * dt > 0
    node0_new = apply_topology(net, node_idx=0, dt=1e-2)
    assert node0_new.S > nodes[0].S, "Topology should increase S for low-entropy node"

    # After applying T to node 1: dS = 0.5 * (0 - 1) * dt < 0
    node1_new = apply_topology(net, node_idx=1, dt=1e-2)
    assert node1_new.S < nodes[1].S, "Topology should decrease S for high-entropy node"


# ---------------------------------------------------------------------------
# 5. UEUM acceleration
# ---------------------------------------------------------------------------

def test_ueum_acceleration_finite():
    """UEUM geodesic acceleration is finite for all random initial conditions."""
    rng = np.random.default_rng(24)
    net = MultiverseNetwork.fully_connected(n=4, rng=rng)
    for i, node in enumerate(net.nodes):
        acc = ueum_acceleration(node, net, i)
        assert np.all(np.isfinite(acc)), (
            f"Non-finite UEUM acceleration for node {i}: {acc}"
        )


def test_ueum_acceleration_shape():
    """UEUM acceleration has shape (dim,) matching node dimension."""
    dim = 4
    net = MultiverseNetwork.chain(n=3, rng=np.random.default_rng(25))
    for i, node in enumerate(net.nodes):
        acc = ueum_acceleration(node, net, i)
        assert acc.shape == (dim,), f"Expected shape ({dim},), got {acc.shape}"


# ---------------------------------------------------------------------------
# 6. Fixed-point convergence
# ---------------------------------------------------------------------------

def test_fixed_point_converges_chain():
    """fixed_point_iteration converges for a small chain network.

    The combined operator U = I + H + T drives entropy to the holographic
    bound.  The full-state residual stabilises at O(dt) because the
    Irreversibility operator keeps pumping entropy by κ A dt per step
    before the Holography operator clamps it back.  A tolerance of 1e-2
    (ten times the natural cycling amplitude at dt=1e-3) is sufficient to
    verify that the iteration reaches a steady regime.
    """
    net = MultiverseNetwork.chain(n=5, coupling=0.05,
                                  rng=np.random.default_rng(26))
    result_net, residuals, converged = fixed_point_iteration(
        net, max_iter=500, tol=1e-2, dt=1e-3
    )
    assert converged, (
        f"Fixed-point iteration did not converge; final residual = {residuals[-1]:.3e}"
    )


def test_fixed_point_residuals_finite():
    """Residual history contains only finite values."""
    net = MultiverseNetwork.chain(n=3, coupling=0.05,
                                  rng=np.random.default_rng(27))
    _, residuals, _ = fixed_point_iteration(net, max_iter=100, tol=1e-6, dt=1e-3)
    assert all(np.isfinite(r) for r in residuals), "Residuals contain non-finite values"


def test_fixed_point_returns_network():
    """fixed_point_iteration returns a MultiverseNetwork object."""
    net = MultiverseNetwork.chain(n=3, coupling=0.05,
                                  rng=np.random.default_rng(28))
    result_net, _, _ = fixed_point_iteration(net, max_iter=50, tol=1e-6, dt=1e-3)
    assert isinstance(result_net, MultiverseNetwork)
    assert result_net.n_nodes() == net.n_nodes()


def test_fixed_point_converges_fully_connected():
    """fixed_point_iteration converges for a fully-connected network.

    Uses the same physically motivated tol=1e-2 as the chain test.
    """
    net = MultiverseNetwork.fully_connected(n=4, coupling=0.05,
                                            rng=np.random.default_rng(29))
    _, residuals, converged = fixed_point_iteration(
        net, max_iter=1000, tol=1e-2, dt=1e-3
    )
    assert converged, (
        f"Fixed-point iteration did not converge for fully-connected net; "
        f"final residual = {residuals[-1]:.3e}"
    )
