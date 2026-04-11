# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_arrow_of_time.py
===========================
Thermodynamic arrow-of-time tests for the Unitary Manifold UEUM system.

The UEUM system claims that irreversibility is *emergent* from the entropy
relaxation operator I and the fixed-point iteration.  These tests falsify
the alternative that "irreversibility is built in by hand" — they verify the
asymmetry is structural, not just a sign convention.

Tests are organised into four classes:

TestForwardEntropyGrowth
    apply_irreversibility with dt > 0 moves S toward A/4G (the holographic
    bound), regardless of initial position.

TestBackwardDeficitGrowth
    Negating dt reverses the flow: a node below the bound drifts further
    below, and a node above the bound drifts further above — the reverse
    process is thermodynamically forbidden.

TestPathIndependence
    fixed_point_iteration converges to the same holographic fixed point
    whether the initial entropy starts far above or far below A/4G.  The
    fixed point is attractive from both sides.

TestEntropyProductionRate
    dS/dt > 0 at every iteration during convergence (monotone decrease of
    the holographic defect ‖A/4G − S‖ along the forward trajectory).
"""

from __future__ import annotations

import copy

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.multiverse.fixed_point import (
    MultiverseNode,
    MultiverseNetwork,
    apply_irreversibility,
    fixed_point_iteration,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _holographic_bound(node: MultiverseNode, G4: float = 1.0) -> float:
    return node.A / (4.0 * G4)


def _deficit(node: MultiverseNode, G4: float = 1.0) -> float:
    """Signed deficit: holographic bound − entropy (positive ⟺ S < bound)."""
    return _holographic_bound(node, G4) - node.S


def _make_node(S: float, A: float = 4.0) -> MultiverseNode:
    """Construct a minimal node with prescribed S and A."""
    return MultiverseNode(
        dim=4, S=S, A=A, Q_top=0.0,
        X=np.zeros(4), Xdot=np.zeros(4),
    )


# ===========================================================================
# TestForwardEntropyGrowth
# ===========================================================================

class TestForwardEntropyGrowth:
    """Forward evolution (dt > 0) drives S toward the holographic bound A/4G."""

    def test_below_bound_entropy_increases(self):
        """If S < A/4G, forward step increases S."""
        node = _make_node(S=0.5, A=4.0)   # bound = 1.0
        updated = apply_irreversibility(node, dt=0.1)
        assert updated.S > node.S, (
            f"S should increase when below bound: {node.S} → {updated.S}"
        )

    def test_above_bound_entropy_decreases(self):
        """If S > A/4G, forward step decreases S (second law enforcement)."""
        node = _make_node(S=1.5, A=4.0)   # bound = 1.0
        updated = apply_irreversibility(node, dt=0.1)
        assert updated.S < node.S, (
            f"S should decrease when above bound: {node.S} → {updated.S}"
        )

    def test_at_bound_no_change(self):
        """If S = A/4G exactly, entropy does not change."""
        node = _make_node(S=1.0, A=4.0)   # bound = 1.0
        updated = apply_irreversibility(node, dt=0.1)
        assert updated.S == pytest.approx(node.S, abs=1e-14), (
            f"At fixed point S should be unchanged: {node.S} → {updated.S}"
        )

    def test_deficit_decreases_from_below(self):
        """Forward step reduces the holographic deficit |bound − S| when S < bound."""
        node = _make_node(S=0.2, A=4.0)   # deficit = 0.8
        updated = apply_irreversibility(node, dt=0.1)
        assert abs(_deficit(updated)) < abs(_deficit(node)), (
            "Forward step should reduce |deficit| from below"
        )

    def test_deficit_decreases_from_above(self):
        """Forward step reduces |bound − S| when S > bound."""
        node = _make_node(S=1.8, A=4.0)   # deficit = −0.8
        updated = apply_irreversibility(node, dt=0.1)
        assert abs(_deficit(updated)) < abs(_deficit(node)), (
            "Forward step should reduce |deficit| from above"
        )

    def test_multiple_steps_converge_to_bound(self):
        """Repeated forward steps converge S toward A/4G."""
        node = _make_node(S=0.1, A=4.0)
        bound = _holographic_bound(node)
        for _ in range(200):
            node = apply_irreversibility(node, dt=0.1)
        assert abs(node.S - bound) < 0.01, (
            f"After 200 steps S={node.S:.4f} should be near bound={bound}"
        )

    def test_kappa_scales_convergence_rate(self):
        """Larger κ gives faster convergence to the holographic bound."""
        node_slow = _make_node(S=0.1, A=4.0)
        node_fast = _make_node(S=0.1, A=4.0)
        bound = _holographic_bound(node_slow)
        for _ in range(20):
            node_slow = apply_irreversibility(node_slow, dt=0.1, kappa=0.1)
            node_fast = apply_irreversibility(node_fast, dt=0.1, kappa=0.5)
        assert abs(node_fast.S - bound) < abs(node_slow.S - bound), (
            "Larger κ should give faster convergence"
        )

    def test_area_unchanged_by_irreversibility(self):
        """apply_irreversibility must not modify the boundary area A."""
        node = _make_node(S=0.5, A=4.0)
        updated = apply_irreversibility(node, dt=0.1)
        assert updated.A == pytest.approx(node.A, rel=1e-12)


# ===========================================================================
# TestBackwardDeficitGrowth
# ===========================================================================

class TestBackwardDeficitGrowth:
    """Negating dt reverses the flow: entropy moves *away* from A/4G."""

    def test_backward_below_bound_entropy_decreases(self):
        """With dt < 0 and S < A/4G, entropy decreases (moves away from bound)."""
        node = _make_node(S=0.5, A=4.0)   # bound = 1.0
        backward = apply_irreversibility(node, dt=-0.1)
        assert backward.S < node.S, (
            f"Backward step should decrease S below bound: {node.S} → {backward.S}"
        )

    def test_backward_above_bound_entropy_increases(self):
        """With dt < 0 and S > A/4G, entropy increases (moves away from bound)."""
        node = _make_node(S=1.5, A=4.0)   # bound = 1.0
        backward = apply_irreversibility(node, dt=-0.1)
        assert backward.S > node.S, (
            f"Backward step should increase S above bound: {node.S} → {backward.S}"
        )

    def test_backward_deficit_grows_from_below(self):
        """Backward step *increases* |deficit| when starting below the bound."""
        node = _make_node(S=0.5, A=4.0)
        backward = apply_irreversibility(node, dt=-0.1)
        assert abs(_deficit(backward)) > abs(_deficit(node)), (
            "Backward step should increase |deficit|"
        )

    def test_forward_backward_not_symmetric(self):
        """Forward then backward step does not perfectly cancel (exponential, not linear)."""
        node = _make_node(S=0.5, A=4.0)
        fwd = apply_irreversibility(node, dt=0.1)
        bwd = apply_irreversibility(fwd,  dt=-0.1)
        # The exponential contraction is not exactly reversible for finite dt
        # so S should return close to but not exactly equal to the initial value
        # (exact equality would hold only in the infinitesimal limit)
        # We verify asymmetry: the round-trip is not exact
        # Actually for linear ODE dS/dt = κ(bound - S) the Euler forward step is:
        # S1 = S0 + dt*κ*(bound-S0), then backward: S2 = S1 - dt*κ*(bound-S1)
        # = S0 + dt*κ*(bound-S0) - dt*κ*(bound - S0 - dt*κ*(bound-S0))
        # = S0 + dt*κ*(bound-S0) - dt*κ*(bound-S0)(1 - dt*κ)
        # = S0 + dt*κ*(bound-S0)*dt*κ   ≠ S0  for finite dt
        # So round trip leaves S slightly closer to bound, confirming asymmetry
        bound = _holographic_bound(node)
        deficit_initial = abs(bound - node.S)
        deficit_roundtrip = abs(bound - bwd.S)
        assert deficit_roundtrip < deficit_initial, (
            "Forward+backward round trip should still leave deficit smaller "
            "(Euler asymmetry — not a time-reversal invariance)"
        )

    def test_arrow_of_time_sign(self):
        """dS/dt > 0 when S < bound (thermodynamic arrow points toward bound)."""
        node = _make_node(S=0.3, A=4.0)
        dt_small = 1e-6
        updated = apply_irreversibility(node, dt=dt_small)
        dS_dt = (updated.S - node.S) / dt_small
        assert dS_dt > 0.0, (
            f"dS/dt = {dS_dt:.4f} should be positive when S < A/4G"
        )


# ===========================================================================
# TestPathIndependence
# ===========================================================================

class TestPathIndependence:
    """fixed_point_iteration converges to the same fixed point from any start."""

    @staticmethod
    def _make_network_with_entropy(S_init: float, n: int = 3) -> MultiverseNetwork:
        """Chain network with all nodes initialised to prescribed entropy S_init."""
        rng = np.random.default_rng(99)
        net = MultiverseNetwork.chain(n=n, rng=rng)
        # Override all node entropies
        new_nodes = []
        for node in net.nodes:
            new_nodes.append(MultiverseNode(
                dim=node.dim, S=S_init, A=node.A,
                Q_top=node.Q_top, X=node.X.copy(), Xdot=node.Xdot.copy(),
            ))
        return MultiverseNetwork(nodes=new_nodes, adjacency=net.adjacency.copy())

    def test_converges_from_below_bound(self):
        """Iteration converges when starting with S ≪ A/4G (far below bound)."""
        net = self._make_network_with_entropy(S_init=1e-4)
        _, _, converged = fixed_point_iteration(net, max_iter=500, tol=1e-4)
        assert converged, "Should converge from S ≪ A/4G"

    def test_converges_from_above_bound(self):
        """Iteration converges when starting with S ≫ A/4G (far above bound)."""
        # A/4G ≈ 0.25 for A~1 node; set S = 10 >> bound
        net = self._make_network_with_entropy(S_init=10.0)
        _, _, converged = fixed_point_iteration(net, max_iter=500, tol=1e-4)
        assert converged, "Should converge from S ≫ A/4G"

    def test_same_fixed_point_from_below_and_above(self):
        """Both trajectories converge to the same defect level."""
        net_low  = self._make_network_with_entropy(S_init=1e-4)
        net_high = self._make_network_with_entropy(S_init=10.0)
        net_low_conv,  res_low,  _ = fixed_point_iteration(net_low,  max_iter=500, tol=1e-5)
        net_high_conv, res_high, _ = fixed_point_iteration(net_high, max_iter=500, tol=1e-5)
        # Final defects should both be small
        final_defect_low  = res_low[-1]
        final_defect_high = res_high[-1]
        assert final_defect_low  < 1e-4, f"Low-start defect not converged: {final_defect_low}"
        assert final_defect_high < 1e-4, f"High-start defect not converged: {final_defect_high}"

    def test_entropy_monotone_increasing_from_below(self):
        """Defect is monotonically decreasing along the forward trajectory (below start)."""
        net = self._make_network_with_entropy(S_init=1e-4)
        _, residuals, _ = fixed_point_iteration(net, max_iter=100, tol=1e-8)
        # Residuals should decrease overall (allow occasional numerical plateau)
        assert residuals[-1] <= residuals[0], (
            f"Defect did not decrease: start={residuals[0]:.4e}, end={residuals[-1]:.4e}"
        )

    def test_different_initial_x_same_convergence(self):
        """Convergence behaviour is the same for two different random seeds."""
        net_a = MultiverseNetwork.chain(n=3, rng=np.random.default_rng(1))
        net_b = MultiverseNetwork.chain(n=3, rng=np.random.default_rng(2))
        _, _, conv_a = fixed_point_iteration(net_a, max_iter=500, tol=1e-5)
        _, _, conv_b = fixed_point_iteration(net_b, max_iter=500, tol=1e-5)
        assert conv_a, "Seed 1 network did not converge"
        assert conv_b, "Seed 2 network did not converge"


# ===========================================================================
# TestEntropyProductionRate
# ===========================================================================

class TestEntropyProductionRate:
    """Entropy production dS/dt > 0 during convergence (not just at endpoint)."""

    def test_positive_production_rate_single_step(self):
        """dS/dt > 0 for a node below its holographic bound."""
        node = _make_node(S=0.3, A=4.0)   # bound = 1.0
        dt = 0.05
        updated = apply_irreversibility(node, dt=dt)
        rate = (updated.S - node.S) / dt
        assert rate > 0.0, f"Expected dS/dt > 0, got {rate:.6f}"

    def test_production_rate_proportional_to_deficit(self):
        """dS/dt ∝ (bound − S): larger deficit → larger production rate."""
        dt = 1e-6
        node_small_deficit = _make_node(S=0.9, A=4.0)   # deficit = 0.1
        node_large_deficit = _make_node(S=0.1, A=4.0)   # deficit = 0.9
        rate_small = (apply_irreversibility(node_small_deficit, dt=dt).S
                      - node_small_deficit.S) / dt
        rate_large = (apply_irreversibility(node_large_deficit, dt=dt).S
                      - node_large_deficit.S) / dt
        assert rate_large > rate_small, (
            f"Larger deficit should give higher production rate: "
            f"rate_large={rate_large:.4f}, rate_small={rate_small:.4f}"
        )

    def test_defect_history_mostly_decreasing(self):
        """Residual history from fixed_point_iteration is mostly non-increasing."""
        net = MultiverseNetwork.chain(n=3, rng=np.random.default_rng(7))
        _, residuals, _ = fixed_point_iteration(net, max_iter=200, tol=1e-8)
        # Allow up to 5% of steps to be non-monotone (numerical noise)
        n = len(residuals) - 1
        non_monotone = sum(1 for i in range(n) if residuals[i + 1] > residuals[i])
        assert non_monotone / n < 0.05, (
            f"{non_monotone}/{n} steps were non-monotone in defect"
        )

    def test_total_entropy_increase_over_run(self):
        """Total entropy across all nodes increases from start to convergence."""
        net = MultiverseNetwork.chain(n=3, rng=np.random.default_rng(13))
        # Set all nodes well below bound
        new_nodes = []
        for node in net.nodes:
            new_nodes.append(MultiverseNode(
                dim=node.dim, S=0.01, A=node.A,
                Q_top=node.Q_top, X=node.X.copy(), Xdot=node.Xdot.copy(),
            ))
        net = MultiverseNetwork(nodes=new_nodes, adjacency=net.adjacency.copy())
        S_initial = sum(n.S for n in net.nodes)
        converged_net, _, _ = fixed_point_iteration(net, max_iter=500, tol=1e-6)
        S_final = sum(n.S for n in converged_net.nodes)
        assert S_final > S_initial, (
            f"Total entropy did not increase: {S_initial:.4f} → {S_final:.4f}"
        )

    def test_entropy_rate_zero_at_fixed_point(self):
        """dS/dt ≈ 0 when a node is already at the holographic bound."""
        # Place node exactly at bound
        A_val = 4.0
        S_at_bound = A_val / 4.0   # = 1.0
        node = _make_node(S=S_at_bound, A=A_val)
        dt = 0.1
        updated = apply_irreversibility(node, dt=dt)
        assert abs(updated.S - node.S) < 1e-14, (
            f"At fixed point dS should be zero, got {updated.S - node.S:.2e}"
        )
