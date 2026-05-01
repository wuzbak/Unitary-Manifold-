"""
tests/test_coupled_attractor.py
================================
Unit tests for src/consciousness/coupled_attractor.py.

Covers:
  - ManifoldState: factories, state_vector shape
  - CoupledSystem: tensor product, norm
  - information_gap: known values, symmetry, zero at equality
  - phase_offset: parallel → 0, antiparallel → π, orthogonal → π/2
  - resonance_ratio: known values
  - is_resonance_locked: pass/fail cases
  - coupled_defect: structure, non-negative, zero at exact FP
  - _apply_coupling: conservation law, antisymmetry
  - step_coupled: defect decreases after many steps
  - coupled_master_equation: converges, history shape, info_gap trends
  - BIREFRINGENCE_RAD: correct value
  - Information Gap monotonically decreases under coupling alone
"""

import math
import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.consciousness.coupled_attractor import (
    BIREFRINGENCE_DEG,
    BIREFRINGENCE_RAD,
    INTENTIONALITY_GAP_THRESHOLD,
    RESONANCE_RATIO,
    WINDING_N1,
    WINDING_N2,
    K_CS,
    ManifoldState,
    CoupledSystem,
    information_gap,
    intentionality_measure,
    intentionality_summary,
    is_intentional,
    is_resonance_locked,
    agency_threshold,
    coupled_defect,
    phase_offset,
    resonance_ratio,
    survival_drive,
    step_coupled,
    coupled_master_equation,
    _apply_coupling,
)
from src.multiverse.fixed_point import MultiverseNode


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_birefringence_deg(self):
        assert BIREFRINGENCE_DEG == pytest.approx(0.3513)

    def test_birefringence_rad_conversion(self):
        expected = 0.3513 * math.pi / 180.0
        assert BIREFRINGENCE_RAD == pytest.approx(expected, rel=1e-6)

    def test_birefringence_rad_magnitude(self):
        # β ≈ 6.132e-3 rad — small but nonzero coupling
        assert 5e-3 < BIREFRINGENCE_RAD < 8e-3

    def test_resonance_ratio(self):
        assert RESONANCE_RATIO == pytest.approx(5 / 7, rel=1e-10)

    def test_winding_numbers(self):
        assert WINDING_N1 == 5
        assert WINDING_N2 == 7

    def test_k_cs(self):
        assert K_CS == 5 ** 2 + 7 ** 2  # 74


# ---------------------------------------------------------------------------
# ManifoldState
# ---------------------------------------------------------------------------

class TestManifoldState:
    def test_universe_factory_label(self):
        ms = ManifoldState.universe(rng=np.random.default_rng(0))
        assert ms.label == "universe"

    def test_brain_factory_label(self):
        ms = ManifoldState.brain(rng=np.random.default_rng(0))
        assert ms.label == "brain"

    def test_universe_large_area(self):
        ms = ManifoldState.universe(rng=np.random.default_rng(0))
        assert ms.node.A >= 10.0

    def test_brain_positive_area(self):
        ms = ManifoldState.brain(rng=np.random.default_rng(0))
        assert ms.node.A >= 1.0

    def test_state_vector_length(self):
        ms = ManifoldState.universe(dim=4, rng=np.random.default_rng(0))
        sv = ms.state_vector()
        # node state: [S, A, Q_top] + X(4) + Xdot(4) = 11; +phi = 12
        assert sv.shape == (12,)

    def test_state_vector_phi_last(self):
        ms = ManifoldState.brain(phi=0.42, rng=np.random.default_rng(0))
        sv = ms.state_vector()
        assert sv[-1] == pytest.approx(0.42)

    def test_default_winding_numbers(self):
        ms = ManifoldState.universe(rng=np.random.default_rng(0))
        assert ms.n1 == 5
        assert ms.n2 == 7
        assert ms.k_cs == 74

    def test_phi_stored(self):
        ms = ManifoldState.brain(phi=0.9, rng=np.random.default_rng(0))
        assert ms.phi == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# CoupledSystem
# ---------------------------------------------------------------------------

class TestCoupledSystem:
    def _default_system(self):
        b = ManifoldState.brain(rng=np.random.default_rng(0))
        u = ManifoldState.universe(rng=np.random.default_rng(0))
        return CoupledSystem(brain=b, universe=u)

    def test_default_beta(self):
        sys = self._default_system()
        assert sys.beta == pytest.approx(BIREFRINGENCE_RAD)

    def test_tensor_product_state_shape(self):
        sys = self._default_system()
        tp = sys.tensor_product_state()
        # brain state_vector length 12, universe 12 → outer product 12×12 → 144
        assert tp.shape == (144,)

    def test_tensor_product_norm_positive(self):
        sys = self._default_system()
        assert sys.tensor_product_norm() > 0.0

    def test_custom_beta(self):
        b = ManifoldState.brain(rng=np.random.default_rng(0))
        u = ManifoldState.universe(rng=np.random.default_rng(0))
        sys = CoupledSystem(brain=b, universe=u, beta=0.1)
        assert sys.beta == pytest.approx(0.1)


# ---------------------------------------------------------------------------
# information_gap
# ---------------------------------------------------------------------------

class TestInformationGap:
    def test_zero_when_equal_phi(self):
        b = ManifoldState.brain(phi=0.8, rng=np.random.default_rng(0))
        u = ManifoldState.universe(phi=0.8, rng=np.random.default_rng(0))
        assert information_gap(b, u) == pytest.approx(0.0)

    def test_nonzero_when_different_phi(self):
        b = ManifoldState.brain(phi=0.5, rng=np.random.default_rng(0))
        u = ManifoldState.universe(phi=1.0, rng=np.random.default_rng(0))
        assert information_gap(b, u) > 0.0

    def test_known_value(self):
        b = ManifoldState.brain(phi=0.5, rng=np.random.default_rng(0))
        u = ManifoldState.universe(phi=1.0, rng=np.random.default_rng(0))
        # |0.5² - 1.0²| = |0.25 - 1.0| = 0.75
        assert information_gap(b, u) == pytest.approx(0.75)

    def test_symmetric(self):
        b = ManifoldState.brain(phi=0.6, rng=np.random.default_rng(0))
        u = ManifoldState.universe(phi=0.9, rng=np.random.default_rng(0))
        assert information_gap(b, u) == pytest.approx(information_gap(u, b))

    def test_non_negative(self):
        for phi_b, phi_u in [(0.1, 0.9), (0.9, 0.1), (1.0, 1.0)]:
            b = ManifoldState.brain(phi=phi_b, rng=np.random.default_rng(0))
            u = ManifoldState.universe(phi=phi_u, rng=np.random.default_rng(0))
            assert information_gap(b, u) >= 0.0


# ---------------------------------------------------------------------------
# phase_offset
# ---------------------------------------------------------------------------

class TestPhaseOffset:
    def _ms(self, X, label="brain"):
        node = MultiverseNode(S=1.0, A=1.0, Q_top=0.0,
                              X=np.array(X, dtype=float),
                              Xdot=np.zeros(len(X)))
        return ManifoldState(node=node, phi=1.0, label=label)

    def test_parallel_vectors_zero(self):
        b = self._ms([1., 0., 0., 0.])
        u = self._ms([2., 0., 0., 0.], label="universe")
        assert phase_offset(b, u) == pytest.approx(0.0, abs=1e-10)

    def test_antiparallel_vectors_pi(self):
        b = self._ms([1., 0., 0., 0.])
        u = self._ms([-1., 0., 0., 0.], label="universe")
        assert phase_offset(b, u) == pytest.approx(math.pi, abs=1e-10)

    def test_orthogonal_vectors_half_pi(self):
        b = self._ms([1., 0., 0., 0.])
        u = self._ms([0., 1., 0., 0.], label="universe")
        assert phase_offset(b, u) == pytest.approx(math.pi / 2, abs=1e-10)

    def test_zero_vector_returns_zero(self):
        b = self._ms([0., 0., 0., 0.])
        u = self._ms([1., 0., 0., 0.], label="universe")
        assert phase_offset(b, u) == pytest.approx(0.0)

    def test_range_zero_to_pi(self):
        NUM_RANDOM_TRIALS = 20
        rng = np.random.default_rng(42)
        for _ in range(NUM_RANDOM_TRIALS):
            X_b = rng.standard_normal(4)
            X_u = rng.standard_normal(4)
            node_b = MultiverseNode(S=1., A=1., Q_top=0., X=X_b, Xdot=np.zeros(4))
            node_u = MultiverseNode(S=1., A=1., Q_top=0., X=X_u, Xdot=np.zeros(4))
            b = ManifoldState(node=node_b, phi=1.0)
            u = ManifoldState(node=node_u, phi=1.0)
            poff = phase_offset(b, u)
            assert 0.0 <= poff <= math.pi + 1e-10


# ---------------------------------------------------------------------------
# resonance_ratio
# ---------------------------------------------------------------------------

class TestResonanceRatio:
    def _ms_with_velocity(self, X, Xdot):
        node = MultiverseNode(S=1., A=1., Q_top=0.,
                              X=np.array(X, dtype=float),
                              Xdot=np.array(Xdot, dtype=float))
        return ManifoldState(node=node, phi=1.0)

    def test_equal_precession_ratio_one(self):
        # |Xdot| = |X| for both → ω = 1 each → ratio = 1
        b = self._ms_with_velocity([1., 0., 0., 0.], [1., 0., 0., 0.])
        u = self._ms_with_velocity([1., 0., 0., 0.], [1., 0., 0., 0.])
        assert resonance_ratio(b, u) == pytest.approx(1.0, abs=1e-6)

    def test_nonnegative(self):
        b = self._ms_with_velocity([1., 0., 0., 0.], [0.5, 0., 0., 0.])
        u = self._ms_with_velocity([1., 0., 0., 0.], [0.7, 0., 0., 0.])
        assert resonance_ratio(b, u) >= 0.0

    def test_target_ratio(self):
        # Brain Xdot ∝ 5, universe Xdot ∝ 7 → ω_brain/ω_univ ≈ 5/7
        b = self._ms_with_velocity([1., 0., 0., 0.], [5., 0., 0., 0.])
        u = self._ms_with_velocity([1., 0., 0., 0.], [7., 0., 0., 0.])
        assert resonance_ratio(b, u) == pytest.approx(5 / 7, rel=1e-4)


# ---------------------------------------------------------------------------
# is_resonance_locked
# ---------------------------------------------------------------------------

class TestIsResonanceLocked:
    def _ms_omega(self, omega):
        """ManifoldState with |Xdot|/|X| = omega."""
        node = MultiverseNode(S=1., A=1., Q_top=0.,
                              X=np.array([1., 0., 0., 0.]),
                              Xdot=np.array([omega, 0., 0., 0.]))
        return ManifoldState(node=node, phi=1.0)

    def test_locked_at_5_7(self):
        b = self._ms_omega(5.0)
        u = self._ms_omega(7.0)
        assert is_resonance_locked(b, u, tol=0.05)

    def test_locked_at_7_5(self):
        b = self._ms_omega(7.0)
        u = self._ms_omega(5.0)
        assert is_resonance_locked(b, u, tol=0.05)

    def test_not_locked_ratio_half(self):
        b = self._ms_omega(1.0)
        u = self._ms_omega(2.0)
        assert not is_resonance_locked(b, u, tol=0.05)

    def test_tol_respected(self):
        # ratio = 0.80 is not within 0.05 of 5/7 ≈ 0.714
        b = self._ms_omega(0.80)
        u = self._ms_omega(1.0)
        assert not is_resonance_locked(b, u, tol=0.05)


# ---------------------------------------------------------------------------
# coupled_defect
# ---------------------------------------------------------------------------

class TestCoupledDefect:
    def test_non_negative(self):
        b = ManifoldState.brain(rng=np.random.default_rng(0))
        u = ManifoldState.universe(rng=np.random.default_rng(0))
        sys = CoupledSystem(brain=b, universe=u)
        assert coupled_defect(sys) >= 0.0

    def test_exact_fixed_point_entropy_only(self):
        """If both manifolds satisfy S = A/4G and φ_brain == φ_univ, defect = 0."""
        G4 = 1.0
        A_b, A_u = 4.0, 4.0
        S_b = A_b / (4.0 * G4)   # 1.0
        S_u = A_u / (4.0 * G4)   # 1.0
        node_b = MultiverseNode(S=S_b, A=A_b, Q_top=0.,
                                X=np.ones(4), Xdot=np.zeros(4))
        node_u = MultiverseNode(S=S_u, A=A_u, Q_top=0.,
                                X=np.ones(4), Xdot=np.zeros(4))
        phi_common = 1.0
        b = ManifoldState(node=node_b, phi=phi_common, label="brain")
        u = ManifoldState(node=node_u, phi=phi_common, label="universe")
        sys = CoupledSystem(brain=b, universe=u)
        assert coupled_defect(sys, G4=G4) == pytest.approx(0.0, abs=1e-12)

    def test_increases_with_phi_mismatch(self):
        """Larger φ mismatch → larger defect."""
        G4 = 1.0
        A = 4.0
        S = A / (4.0 * G4)
        node = MultiverseNode(S=S, A=A, Q_top=0., X=np.ones(4), Xdot=np.zeros(4))
        b1 = ManifoldState(node=node, phi=1.0, label="brain")
        b2 = ManifoldState(node=node, phi=0.5, label="brain")
        u = ManifoldState(node=node, phi=1.0, label="universe")
        d1 = coupled_defect(CoupledSystem(brain=b1, universe=u), G4=G4)
        d2 = coupled_defect(CoupledSystem(brain=b2, universe=u), G4=G4)
        # b2 has φ mismatch → larger ΔI → larger defect
        assert d2 > d1


# ---------------------------------------------------------------------------
# _apply_coupling  (conservation law and antisymmetry)
# ---------------------------------------------------------------------------

class TestApplyCoupling:
    def _make_system(self, S_b=2.0, S_u=5.0, phi_b=0.5, phi_u=1.0):
        node_b = MultiverseNode(S=S_b, A=4.0, Q_top=0.,
                                X=np.array([1., 0., 0., 0.]),
                                Xdot=np.zeros(4))
        node_u = MultiverseNode(S=S_u, A=4.0, Q_top=0.,
                                X=np.array([0., 1., 0., 0.]),
                                Xdot=np.zeros(4))
        b = ManifoldState(node=node_b, phi=phi_b, label="brain")
        u = ManifoldState(node=node_u, phi=phi_u, label="universe")
        return CoupledSystem(brain=b, universe=u, beta=0.1)

    def test_entropy_conservation(self):
        """Total entropy S_brain + S_univ is conserved under coupling alone."""
        sys = self._make_system()
        S_total_before = sys.brain.node.S + sys.universe.node.S
        sys2 = _apply_coupling(sys, dt=0.5)
        S_total_after = sys2.brain.node.S + sys2.universe.node.S
        assert S_total_after == pytest.approx(S_total_before, abs=1e-12)

    def test_phi_conservation(self):
        """Total φ_brain + φ_univ is conserved under coupling alone."""
        sys = self._make_system()
        phi_total_before = sys.brain.phi + sys.universe.phi
        sys2 = _apply_coupling(sys, dt=0.5)
        phi_total_after = sys2.brain.phi + sys2.universe.phi
        assert phi_total_after == pytest.approx(phi_total_before, abs=1e-12)

    def test_X_conservation(self):
        """Total X_brain + X_univ is conserved under coupling alone."""
        sys = self._make_system()
        X_total_before = sys.brain.node.X + sys.universe.node.X
        sys2 = _apply_coupling(sys, dt=0.5)
        X_total_after = sys2.brain.node.X + sys2.universe.node.X
        assert np.allclose(X_total_after, X_total_before, atol=1e-12)

    def test_entropy_flows_brain_to_universe(self):
        """When S_univ > S_brain, brain entropy increases."""
        sys = self._make_system(S_b=1.0, S_u=5.0)
        sys2 = _apply_coupling(sys, dt=0.5)
        assert sys2.brain.node.S > sys.brain.node.S
        assert sys2.universe.node.S < sys.universe.node.S

    def test_entropy_flows_universe_to_brain(self):
        """When S_brain > S_univ, brain entropy decreases."""
        sys = self._make_system(S_b=5.0, S_u=1.0)
        sys2 = _apply_coupling(sys, dt=0.5)
        assert sys2.brain.node.S < sys.brain.node.S
        assert sys2.universe.node.S > sys.universe.node.S

    def test_no_change_when_equal_S(self):
        """When S_brain = S_univ, entropy coupling does nothing."""
        sys = self._make_system(S_b=3.0, S_u=3.0, phi_b=0.7, phi_u=0.7)
        sys2 = _apply_coupling(sys, dt=0.5)
        assert sys2.brain.node.S == pytest.approx(sys.brain.node.S, abs=1e-12)
        assert sys2.universe.node.S == pytest.approx(sys.universe.node.S, abs=1e-12)

    def test_beta_scales_exchange(self):
        """Larger β → larger entropy exchange per dt."""
        sys_lo = self._make_system(S_b=1.0, S_u=5.0)
        sys_lo = CoupledSystem(brain=sys_lo.brain, universe=sys_lo.universe, beta=0.01)
        sys_hi = CoupledSystem(brain=sys_lo.brain, universe=sys_lo.universe, beta=1.0)
        dS_lo = abs(_apply_coupling(sys_lo, dt=0.1).brain.node.S - sys_lo.brain.node.S)
        dS_hi = abs(_apply_coupling(sys_hi, dt=0.1).brain.node.S - sys_hi.brain.node.S)
        assert dS_hi > dS_lo


# ---------------------------------------------------------------------------
# step_coupled
# ---------------------------------------------------------------------------

class TestStepCoupled:
    def test_returns_coupled_system(self):
        b = ManifoldState.brain(rng=np.random.default_rng(0))
        u = ManifoldState.universe(rng=np.random.default_rng(0))
        sys = CoupledSystem(brain=b, universe=u)
        sys2 = step_coupled(sys, dt=0.1)
        assert isinstance(sys2, CoupledSystem)

    def test_defect_decreases_after_many_steps(self):
        """After 200 steps the defect should be strictly smaller.

        Uses equal boundary areas (A=4) so both manifolds share the same
        holographic fixed-point φ* = A/4G = 1.0; initial entropy defects
        are non-trivial so the FTUM+coupling iteration can reduce them.
        """
        # Equal areas → same φ* = 1.0; start well below the holographic bound
        node_b = MultiverseNode(S=0.0, A=4.0, Q_top=0.0,
                                X=np.ones(4), Xdot=0.1 * np.ones(4))
        node_u = MultiverseNode(S=0.0, A=4.0, Q_top=0.0,
                                X=np.ones(4), Xdot=0.1 * np.ones(4))
        b = ManifoldState(node=node_b, phi=0.5, label="brain")
        u = ManifoldState(node=node_u, phi=0.5, label="universe")
        sys = CoupledSystem(brain=b, universe=u)
        d0 = coupled_defect(sys)
        for _ in range(200):
            sys = step_coupled(sys, dt=0.1)
        d_final = coupled_defect(sys)
        assert d_final < d0

    def test_state_is_finite(self):
        b = ManifoldState.brain(rng=np.random.default_rng(0))
        u = ManifoldState.universe(rng=np.random.default_rng(0))
        sys = CoupledSystem(brain=b, universe=u)
        for _ in range(10):
            sys = step_coupled(sys, dt=0.1)
        assert np.isfinite(sys.brain.phi)
        assert np.isfinite(sys.universe.phi)
        assert np.isfinite(sys.brain.node.S)
        assert np.isfinite(sys.universe.node.S)

    def test_labels_preserved(self):
        b = ManifoldState.brain(rng=np.random.default_rng(0))
        u = ManifoldState.universe(rng=np.random.default_rng(0))
        sys = CoupledSystem(brain=b, universe=u)
        sys2 = step_coupled(sys, dt=0.1)
        assert sys2.brain.label == "brain"
        assert sys2.universe.label == "universe"

    def test_winding_numbers_preserved(self):
        b = ManifoldState.brain(rng=np.random.default_rng(0))
        u = ManifoldState.universe(rng=np.random.default_rng(0))
        sys = CoupledSystem(brain=b, universe=u)
        sys2 = step_coupled(sys, dt=0.1)
        assert sys2.brain.n1 == 5 and sys2.brain.n2 == 7
        assert sys2.universe.n1 == 5 and sys2.universe.n2 == 7


# ---------------------------------------------------------------------------
# coupled_master_equation
# ---------------------------------------------------------------------------

class TestCoupledMasterEquation:
    def _make_sys(self, phi_b=0.5, phi_u=0.8, seed=42):
        # Use equal boundary areas (A=4) so both φ values converge to the
        # same holographic fixed point φ* = A/4G = 1.0, making ΔI → 0.
        node_b = MultiverseNode(S=0.0, A=4.0, Q_top=0.0,
                                X=np.ones(4), Xdot=np.zeros(4))
        node_u = MultiverseNode(S=0.0, A=4.0, Q_top=0.0,
                                X=np.ones(4), Xdot=np.zeros(4))
        b = ManifoldState(node=node_b, phi=phi_b, label="brain")
        u = ManifoldState(node=node_u, phi=phi_u, label="universe")
        return CoupledSystem(brain=b, universe=u)

    def test_returns_correct_types(self):
        sys = self._make_sys()
        result, history, converged = coupled_master_equation(
            sys, max_iter=20, tol=1e-6, dt=0.1)
        assert isinstance(result, CoupledSystem)
        assert isinstance(history, list)
        assert isinstance(converged, bool)

    def test_history_length(self):
        sys = self._make_sys()
        _, history, _ = coupled_master_equation(sys, max_iter=50, tol=0.0, dt=0.1)
        # tol=0 means it never declares convergence early → runs all 50 iters
        assert len(history) == 50

    def test_history_keys(self):
        sys = self._make_sys()
        _, history, _ = coupled_master_equation(sys, max_iter=5, tol=0.0, dt=0.1)
        for rec in history:
            assert "defect" in rec
            assert "info_gap" in rec
            assert "phase_offset" in rec
            assert "S_brain" in rec
            assert "S_univ" in rec
            assert "phi_brain" in rec
            assert "phi_univ" in rec

    def test_defect_first_entry_nonnegative(self):
        sys = self._make_sys()
        _, history, _ = coupled_master_equation(sys, max_iter=5, tol=0.0, dt=0.1)
        assert history[0]["defect"] >= 0.0

    def test_converges_with_high_tol(self):
        """With a generous tolerance, the system should converge quickly."""
        sys = self._make_sys()
        _, history, converged = coupled_master_equation(
            sys, max_iter=1000, tol=0.5, dt=0.1)
        assert converged

    def test_info_gap_decreases_overall(self):
        """Information Gap at end should be ≤ Information Gap at start.

        Uses equal areas so both manifolds converge to the same φ* = A/4G = 1.0;
        the initial gap ΔI = |0.3² − 1.2²| = |0.09 − 1.44| = 1.35 should
        decrease as each φ relaxes toward 1.0.
        """
        sys = self._make_sys(phi_b=0.3, phi_u=1.2)
        _, history, _ = coupled_master_equation(
            sys, max_iter=200, tol=0.0, dt=0.1)
        assert history[-1]["info_gap"] <= history[0]["info_gap"] + 1e-9

    def test_defect_values_finite(self):
        sys = self._make_sys()
        _, history, _ = coupled_master_equation(sys, max_iter=30, tol=0.0, dt=0.1)
        for rec in history:
            assert math.isfinite(rec["defect"])
            assert math.isfinite(rec["info_gap"])
            assert math.isfinite(rec["phase_offset"])

    def test_max_iter_respected(self):
        """Never exceeds max_iter iterations."""
        sys = self._make_sys()
        _, history, _ = coupled_master_equation(
            sys, max_iter=7, tol=0.0, dt=0.1)
        assert len(history) <= 7

    def test_entropy_finite_after_convergence(self):
        sys = self._make_sys()
        result, _, _ = coupled_master_equation(
            sys, max_iter=100, tol=0.5, dt=0.1)
        assert math.isfinite(result.brain.node.S)
        assert math.isfinite(result.universe.node.S)


# ---------------------------------------------------------------------------
# Information Gap coupling: conservation under _apply_coupling alone
# ---------------------------------------------------------------------------

class TestInformationGapAlignment:
    def test_coupling_reduces_info_gap(self):
        """Repeated coupling steps drive ΔI toward zero."""
        node_b = MultiverseNode(S=1., A=4., Q_top=0., X=np.ones(4), Xdot=np.zeros(4))
        node_u = MultiverseNode(S=1., A=4., Q_top=0., X=np.ones(4), Xdot=np.zeros(4))
        b = ManifoldState(node=node_b, phi=0.3, label="brain")
        u = ManifoldState(node=node_u, phi=1.0, label="universe")
        sys = CoupledSystem(brain=b, universe=u, beta=0.1)
        dI_initial = information_gap(sys.brain, sys.universe)
        for _ in range(100):
            sys = _apply_coupling(sys, dt=0.5)
        dI_final = information_gap(sys.brain, sys.universe)
        assert dI_final < dI_initial

    def test_coupling_preserves_total_phi(self):
        """φ_brain + φ_univ (linear sum) is conserved; φ²_brain + φ²_univ is NOT."""
        node_b = MultiverseNode(S=1., A=4., Q_top=0., X=np.ones(4), Xdot=np.zeros(4))
        node_u = MultiverseNode(S=1., A=4., Q_top=0., X=np.ones(4), Xdot=np.zeros(4))
        b = ManifoldState(node=node_b, phi=0.5, label="brain")
        u = ManifoldState(node=node_u, phi=1.0, label="universe")
        sys = CoupledSystem(brain=b, universe=u, beta=0.05)
        phi_total_before = sys.brain.phi + sys.universe.phi
        sys2 = _apply_coupling(sys, dt=1.0)
        phi_total_after = sys2.brain.phi + sys2.universe.phi
        # φ total (linear) is conserved
        assert phi_total_after == pytest.approx(phi_total_before, abs=1e-12)


# ---------------------------------------------------------------------------
# Gap 3 — Intentionality / Agency tests
# ---------------------------------------------------------------------------

def _intentional_system():
    """Build a system with large ΔI and approximate 5:7 resonance."""
    node_b = MultiverseNode(
        S=1.0, A=4.0, Q_top=0.0,
        X=np.array([1.0, 0.0, 0.0, 0.0]),
        Xdot=np.array([5.0, 0.0, 0.0, 0.0]),
    )
    node_u = MultiverseNode(
        S=5.0, A=40.0, Q_top=0.0,
        X=np.array([1.0, 0.0, 0.0, 0.0]),
        Xdot=np.array([7.0, 0.0, 0.0, 0.0]),
    )
    # Large ΔI: |0.8² − 0.1²| = 0.63 > threshold=1/49≈0.0204
    b = ManifoldState(node=node_b, phi=0.8, label="brain")
    u = ManifoldState(node=node_u, phi=0.1, label="universe")
    return CoupledSystem(brain=b, universe=u)


def _rock_system():
    """Build a system with tiny ΔI — rock-like, no agency."""
    node = MultiverseNode(
        S=1.0, A=4.0, Q_top=0.0,
        X=np.array([1.0, 0.0, 0.0, 0.0]),
        Xdot=np.ones(4) * 0.5,
    )
    # ΔI ≈ 0 (same φ) — rock
    b = ManifoldState(node=node, phi=1.0, label="brain")
    u = ManifoldState(node=node, phi=1.0, label="universe")
    return CoupledSystem(brain=b, universe=u)


class TestIntentionalityConstants:
    def test_gap_threshold_value(self):
        # INTENTIONALITY_GAP_THRESHOLD = 1/(k_cs - n_w²) = 1/49
        expected = 1.0 / (74 - 25)
        assert abs(INTENTIONALITY_GAP_THRESHOLD - expected) < 1e-12

    def test_gap_threshold_positive(self):
        assert INTENTIONALITY_GAP_THRESHOLD > 0.0


class TestIntentionalityMeasure:
    def test_intentional_system_measure_gt_1(self):
        sys = _intentional_system()
        assert intentionality_measure(sys) > 1.0

    def test_rock_system_measure_small(self):
        sys = _rock_system()
        assert intentionality_measure(sys) < 1.0

    def test_non_negative(self):
        for sys in [_intentional_system(), _rock_system()]:
            assert intentionality_measure(sys) >= 0.0

    def test_scales_with_info_gap(self):
        """Larger ΔI → higher intentionality measure."""
        node_b = MultiverseNode(
            S=1.0, A=4.0, Q_top=0.0,
            X=np.array([1.0, 0.0, 0.0, 0.0]),
            Xdot=np.array([5.0, 0.0, 0.0, 0.0]),
        )
        node_u = MultiverseNode(
            S=5.0, A=40.0, Q_top=0.0,
            X=np.array([1.0, 0.0, 0.0, 0.0]),
            Xdot=np.array([7.0, 0.0, 0.0, 0.0]),
        )
        b_small = ManifoldState(node=node_b, phi=0.5, label="brain")
        b_large = ManifoldState(node=node_b, phi=0.9, label="brain")
        u = ManifoldState(node=node_u, phi=0.1, label="universe")
        sys_small = CoupledSystem(brain=b_small, universe=u)
        sys_large = CoupledSystem(brain=b_large, universe=u)
        i_small = intentionality_measure(sys_small)
        i_large = intentionality_measure(sys_large)
        # larger phi_brain → larger ΔI → higher intentionality
        assert i_large > i_small


class TestIsIntentional:
    def test_intentional_system_is_intentional(self):
        sys = _intentional_system()
        assert is_intentional(sys) is True

    def test_rock_not_intentional(self):
        sys = _rock_system()
        assert is_intentional(sys) is False

    def test_no_resonance_not_intentional(self):
        """High ΔI but no resonance lock → not intentional."""
        node_b = MultiverseNode(
            S=1.0, A=4.0, Q_top=0.0,
            X=np.array([1.0, 0.0, 0.0, 0.0]),
            Xdot=np.array([100.0, 0.0, 0.0, 0.0]),  # far from 5:7
        )
        node_u = MultiverseNode(
            S=5.0, A=40.0, Q_top=0.0,
            X=np.array([1.0, 0.0, 0.0, 0.0]),
            Xdot=np.array([1.0, 0.0, 0.0, 0.0]),
        )
        b = ManifoldState(node=node_b, phi=0.9, label="brain")
        u = ManifoldState(node=node_u, phi=0.1, label="universe")
        sys = CoupledSystem(brain=b, universe=u)
        # ΔI > threshold but resonance not locked
        assert not is_intentional(sys)


class TestSurvivalDrive:
    def test_positive(self):
        sys = _intentional_system()
        assert survival_drive(sys) > 0.0

    def test_rock_drive_small(self):
        sys = _rock_system()
        # Rock: φ²_brain tiny → small drive
        node = MultiverseNode(S=1.0, A=4.0, Q_top=0.0,
                              X=np.ones(4), Xdot=np.zeros(4))
        b = ManifoldState(node=node, phi=1e-6, label="brain")
        u = ManifoldState(node=node, phi=1.0, label="universe")
        rock = CoupledSystem(brain=b, universe=u)
        assert survival_drive(rock) < survival_drive(_intentional_system())

    def test_larger_phi_brain_larger_drive(self):
        node = MultiverseNode(S=0.0, A=4.0, Q_top=0.0,
                              X=np.ones(4), Xdot=np.zeros(4))
        u = ManifoldState(node=node, phi=0.0, label="universe")
        b1 = ManifoldState(node=node, phi=1.0, label="brain")
        b2 = ManifoldState(node=node, phi=2.0, label="brain")
        s1 = CoupledSystem(brain=b1, universe=u)
        s2 = CoupledSystem(brain=b2, universe=u)
        assert survival_drive(s2) > survival_drive(s1)


class TestAgencyThreshold:
    def test_positive(self):
        thresh = agency_threshold()
        assert thresh > 0.0

    def test_formula(self):
        c_s = 12.0 / 37.0
        gap = 74 - 25  # k_cs - n_w^2 = 49
        expected = c_s / gap
        assert abs(agency_threshold() - expected) < 1e-12

    def test_less_than_intentionality_gap_threshold(self):
        # agency_threshold (c_s/49) < INTENTIONALITY_GAP_THRESHOLD (1/49)
        assert agency_threshold() < INTENTIONALITY_GAP_THRESHOLD


class TestIntentionalitySummary:
    def setup_method(self):
        self.summary = intentionality_summary(_intentional_system())

    def test_keys_present(self):
        for key in [
            "information_gap", "gap_threshold", "agency_threshold",
            "intentionality_measure", "is_intentional", "survival_drive",
            "resonance_locked", "resonance_ratio", "coupled_defect", "summary"
        ]:
            assert key in self.summary

    def test_is_intentional_bool(self):
        assert isinstance(self.summary["is_intentional"], bool)

    def test_gap_threshold_value(self):
        assert abs(self.summary["gap_threshold"] - INTENTIONALITY_GAP_THRESHOLD) < 1e-12

    def test_summary_string(self):
        s = self.summary["summary"]
        assert isinstance(s, str)
        assert len(s) > 0

    def test_rock_summary_not_intentional(self):
        rock_sum = intentionality_summary(_rock_system())
        assert rock_sum["is_intentional"] is False

    def test_survival_drive_positive(self):
        assert self.summary["survival_drive"] > 0.0

    def test_information_gap_non_negative(self):
        assert self.summary["information_gap"] >= 0.0


# ===========================================================================
# Falsifiability: grid_cell_falsification_test
# ===========================================================================

from src.consciousness.coupled_attractor import grid_cell_falsification_test


class TestGridCellFalsificationTest:
    """Tests for the one quantitatively falsifiable prediction of this module."""

    def test_returns_dict(self):
        r = grid_cell_falsification_test()
        assert isinstance(r, dict)

    def test_predicted_ratio_is_7_over_5(self):
        r = grid_cell_falsification_test()
        assert abs(r["predicted_ratio"] - 7.0 / 5.0) < 1e-10

    def test_predicted_ratio_is_1_4(self):
        r = grid_cell_falsification_test()
        assert abs(r["predicted_ratio"] - 1.4) < 1e-10

    def test_default_data_stensola(self):
        r = grid_cell_falsification_test()
        assert r["n_ratios"] == 5

    def test_default_mean_near_1_4(self):
        r = grid_cell_falsification_test()
        assert abs(r["mean_observed"] - 1.4) < 0.05

    def test_default_not_falsified(self):
        r = grid_cell_falsification_test()
        assert r["verdict"] == "NOT-FALSIFIED"

    def test_z_score_near_zero_default(self):
        r = grid_cell_falsification_test()
        assert abs(r["z_score"]) < 2.0

    def test_chi2_non_negative(self):
        r = grid_cell_falsification_test()
        assert r["chi2"] >= 0.0

    def test_p_value_in_range(self):
        r = grid_cell_falsification_test()
        assert 0.0 <= r["p_value_approx"] <= 1.0

    def test_custom_ratios_accepted(self):
        r = grid_cell_falsification_test(observed_ratios=[1.4, 1.4, 1.4])
        assert r["n_ratios"] == 3
        assert abs(r["mean_observed"] - 1.4) < 1e-10

    def test_falsified_when_far_from_prediction(self):
        r = grid_cell_falsification_test(observed_ratios=[1.9, 2.0, 2.1, 2.0, 1.95],
                                          tol_sigma=2.0)
        assert r["verdict"] == "FALSIFIED"

    def test_falsified_z_score_large(self):
        r = grid_cell_falsification_test(observed_ratios=[1.9, 2.0, 2.1, 2.0, 1.95])
        assert abs(r["z_score"]) > 2.0

    def test_reference_mentions_stensola(self):
        r = grid_cell_falsification_test()
        assert "Stensola" in r["reference"]

    def test_reference_mentions_barry(self):
        r = grid_cell_falsification_test()
        assert "Barry" in r["reference"]

    def test_epistemic_note_present(self):
        r = grid_cell_falsification_test()
        assert len(r["epistemic_note"]) > 20

    def test_epistemic_note_says_analogy(self):
        r = grid_cell_falsification_test()
        assert "analogy" in r["epistemic_note"] or "phenomenological" in r["epistemic_note"]

    def test_tol_sigma_stored(self):
        r = grid_cell_falsification_test(tol_sigma=3.0)
        assert r["tol_sigma"] == 3.0

    def test_std_non_negative(self):
        r = grid_cell_falsification_test()
        assert r["std_observed"] >= 0.0

    def test_sem_non_negative(self):
        r = grid_cell_falsification_test()
        assert r["sem_observed"] >= 0.0

    def test_observed_ratios_stored(self):
        custom = [1.4, 1.41, 1.39]
        r = grid_cell_falsification_test(observed_ratios=custom)
        assert r["observed_ratios"] == custom
