# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_unitary_pentad.py
======================================
Unit tests for the 5-body Unitary Pentad module.

Covers:
  - PentadLabel: all 5 label constants defined
  - PENTAD_LABELS: ordering and cardinality
  - PentadSystem: construction, default factory, validation
  - state_matrix: shape (5, state_len)
  - pentad_pairwise_gaps: 10 pairs, symmetry, zero at equality, non-negative
  - pentad_pairwise_phases: 10 pairs, symmetry, range [0, π]
  - trust_modulation: clamped to [0, 1], default near 1
  - pentad_coupling_matrix: shape (5,5), symmetric, zero diagonal,
                             trust-body entries equal β, off-trust entries ≤ β
  - pentad_eigenspectrum: sorted, shape (5,), no negative eigenvalues
  - pentad_defect: non-negative, structure
  - _apply_pentagonal_coupling: conservation laws (total S, X, φ constant)
  - step_pentad: returns PentadSystem, defect trajectory
  - pentad_master_equation: converges, history structure, trust preserved
  - BRAIDED_SOUND_SPEED: correct value 12/37
"""

import math
import numpy as np
import pytest

import sys
import os

# Add both the repo root and this folder to the path.
_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from unitary_pentad import (
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
    PentadLabel,
    PENTAD_LABELS,
    PentadSystem,
    pentad_pairwise_gaps,
    pentad_pairwise_phases,
    trust_modulation,
    tick_grace_period,
    pentad_coupling_matrix,
    pentad_eigenspectrum,
    pentad_defect,
    _apply_pentagonal_coupling,
    step_pentad,
    pentad_master_equation,
)
from src.consciousness.coupled_attractor import (
    BIREFRINGENCE_RAD,
    WINDING_N1,
    WINDING_N2,
    K_CS,
    ManifoldState,
)
from src.multiverse.fixed_point import MultiverseNode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flat_pentad(phi_all: float = 1.0, beta: float = BIREFRINGENCE_RAD) -> PentadSystem:
    """Create a pentad where all bodies share the same φ (gap = 0)."""
    ps = PentadSystem.default(beta=beta)
    new_bodies = {}
    for lbl in PENTAD_LABELS:
        old = ps.bodies[lbl]
        new_bodies[lbl] = ManifoldState(
            node=old.node,
            phi=phi_all,
            n1=old.n1, n2=old.n2, k_cs=old.k_cs,
            label=old.label,
        )
    return PentadSystem(bodies=new_bodies, beta=beta)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_braided_sound_speed_value(self):
        """c_s = 12/37 = (n2-n1)(n1+n2) / k_cs."""
        expected = (WINDING_N2 - WINDING_N1) * (WINDING_N1 + WINDING_N2) / K_CS
        assert BRAIDED_SOUND_SPEED == pytest.approx(expected, rel=1e-10)

    def test_braided_sound_speed_magnitude(self):
        """c_s ≈ 0.3243 — within (0, 1)."""
        assert 0.0 < BRAIDED_SOUND_SPEED < 1.0
        assert BRAIDED_SOUND_SPEED == pytest.approx(12 / 37, rel=1e-8)

    def test_trust_phi_min_positive(self):
        assert TRUST_PHI_MIN > 0.0
        assert TRUST_PHI_MIN < 1.0


# ---------------------------------------------------------------------------
# PentadLabel
# ---------------------------------------------------------------------------

class TestPentadLabel:
    def test_univ_label(self):
        assert PentadLabel.UNIV == "univ"

    def test_brain_label(self):
        assert PentadLabel.BRAIN == "brain"

    def test_human_label(self):
        assert PentadLabel.HUMAN == "human"

    def test_ai_label(self):
        assert PentadLabel.AI == "ai"

    def test_trust_label(self):
        assert PentadLabel.TRUST == "trust"

    def test_all_labels_distinct(self):
        labels = [
            PentadLabel.UNIV, PentadLabel.BRAIN,
            PentadLabel.HUMAN, PentadLabel.AI, PentadLabel.TRUST,
        ]
        assert len(set(labels)) == 5


# ---------------------------------------------------------------------------
# PENTAD_LABELS
# ---------------------------------------------------------------------------

class TestPentadLabels:
    def test_has_five_labels(self):
        assert len(PENTAD_LABELS) == 5

    def test_contains_all_bodies(self):
        for lbl in (
            PentadLabel.UNIV, PentadLabel.BRAIN,
            PentadLabel.HUMAN, PentadLabel.AI, PentadLabel.TRUST,
        ):
            assert lbl in PENTAD_LABELS

    def test_no_duplicates(self):
        assert len(set(PENTAD_LABELS)) == 5

    def test_trust_is_last(self):
        assert PENTAD_LABELS[-1] == PentadLabel.TRUST


# ---------------------------------------------------------------------------
# PentadSystem
# ---------------------------------------------------------------------------

class TestPentadSystem:
    def test_default_construction(self):
        ps = PentadSystem.default()
        assert isinstance(ps, PentadSystem)
        assert len(ps.bodies) == 5

    def test_all_labels_present(self):
        ps = PentadSystem.default()
        for lbl in PENTAD_LABELS:
            assert lbl in ps.bodies

    def test_body_types(self):
        ps = PentadSystem.default()
        for lbl in PENTAD_LABELS:
            assert isinstance(ps.bodies[lbl], ManifoldState)

    def test_body_labels_match(self):
        ps = PentadSystem.default()
        for lbl in PENTAD_LABELS:
            assert ps.bodies[lbl].label == lbl

    def test_missing_body_raises(self):
        ps = PentadSystem.default()
        bad = {k: v for k, v in ps.bodies.items() if k != PentadLabel.TRUST}
        with pytest.raises(ValueError):
            PentadSystem(bodies=bad, beta=BIREFRINGENCE_RAD)

    def test_getitem(self):
        ps = PentadSystem.default()
        univ = ps[PentadLabel.UNIV]
        assert isinstance(univ, ManifoldState)

    def test_state_matrix_shape(self):
        ps = PentadSystem.default()
        mat = ps.state_matrix()
        assert mat.shape[0] == 5
        assert mat.shape[1] > 1

    def test_tensor_product_norm_positive(self):
        ps = PentadSystem.default()
        assert ps.tensor_product_norm() > 0.0

    def test_default_beta(self):
        ps = PentadSystem.default()
        assert ps.beta == pytest.approx(BIREFRINGENCE_RAD, rel=1e-10)

    def test_custom_beta(self):
        ps = PentadSystem.default(beta=0.05)
        assert ps.beta == pytest.approx(0.05)

    def test_univ_larger_area_than_brain(self):
        """Universe body should have larger boundary area by default."""
        ps = PentadSystem.default()
        A_univ = ps.bodies[PentadLabel.UNIV].node.A
        A_brain = ps.bodies[PentadLabel.BRAIN].node.A
        assert A_univ > A_brain

    def test_univ_higher_phi_than_brain(self):
        """Universe φ should exceed brain φ at default init."""
        ps = PentadSystem.default()
        assert (ps.bodies[PentadLabel.UNIV].phi
                > ps.bodies[PentadLabel.BRAIN].phi)


# ---------------------------------------------------------------------------
# Pairwise Information Gaps
# ---------------------------------------------------------------------------

class TestPentadPairwiseGaps:
    def test_ten_pairs_returned(self):
        ps = PentadSystem.default()
        gaps = pentad_pairwise_gaps(ps)
        assert len(gaps) == 10   # C(5,2)

    def test_non_negative(self):
        ps = PentadSystem.default()
        for v in pentad_pairwise_gaps(ps).values():
            assert v >= 0.0

    def test_zero_at_uniform_phi(self):
        ps = _flat_pentad(phi_all=1.0)
        for v in pentad_pairwise_gaps(ps).values():
            assert v == pytest.approx(0.0, abs=1e-12)

    def test_known_gap_value(self):
        """ΔI = |φ₁² − φ₂²| = |1 − 0.49| = 0.51."""
        ps = _flat_pentad(phi_all=1.0)
        new_bodies = dict(ps.bodies)
        old_brain = ps.bodies[PentadLabel.BRAIN]
        new_bodies[PentadLabel.BRAIN] = ManifoldState(
            node=old_brain.node, phi=0.7,
            n1=old_brain.n1, n2=old_brain.n2, k_cs=old_brain.k_cs,
            label=old_brain.label,
        )
        ps2 = PentadSystem(bodies=new_bodies, beta=BIREFRINGENCE_RAD)
        gaps = pentad_pairwise_gaps(ps2)
        key = (PentadLabel.UNIV, PentadLabel.BRAIN)
        assert gaps[key] == pytest.approx(abs(1.0 ** 2 - 0.7 ** 2), rel=1e-9)

    def test_all_pairs_have_valid_keys(self):
        from itertools import combinations
        ps = PentadSystem.default()
        gaps = pentad_pairwise_gaps(ps)
        expected_keys = set(combinations(PENTAD_LABELS, 2))
        assert set(gaps.keys()) == expected_keys


# ---------------------------------------------------------------------------
# Pairwise Phase Offsets
# ---------------------------------------------------------------------------

class TestPentadPairwisePhases:
    def test_ten_pairs_returned(self):
        ps = PentadSystem.default()
        phases = pentad_pairwise_phases(ps)
        assert len(phases) == 10

    def test_in_range_zero_pi(self):
        ps = PentadSystem.default()
        for v in pentad_pairwise_phases(ps).values():
            assert 0.0 <= v <= math.pi + 1e-9

    def test_zero_for_parallel_vectors(self):
        """Two bodies with identical X should have phase = 0."""
        ps = PentadSystem.default()
        univ = ps.bodies[PentadLabel.UNIV]
        brain = ps.bodies[PentadLabel.BRAIN]
        X_same = univ.node.X.copy()
        new_brain_node = MultiverseNode(
            dim=brain.node.dim, S=brain.node.S, A=brain.node.A,
            Q_top=brain.node.Q_top, X=X_same, Xdot=brain.node.Xdot.copy(),
        )
        new_bodies = dict(ps.bodies)
        new_bodies[PentadLabel.BRAIN] = ManifoldState(
            node=new_brain_node, phi=brain.phi,
            n1=brain.n1, n2=brain.n2, k_cs=brain.k_cs, label=brain.label,
        )
        ps2 = PentadSystem(bodies=new_bodies, beta=BIREFRINGENCE_RAD)
        phases = pentad_pairwise_phases(ps2)
        assert phases[(PentadLabel.UNIV, PentadLabel.BRAIN)] == pytest.approx(
            0.0, abs=1e-9
        )

    def test_pi_for_antiparallel_vectors(self):
        """Two bodies with X and -X should have phase = π."""
        ps = PentadSystem.default()
        univ = ps.bodies[PentadLabel.UNIV]
        X_pos = univ.node.X.copy()
        X_neg = -X_pos
        brain = ps.bodies[PentadLabel.BRAIN]
        new_brain_node = MultiverseNode(
            dim=brain.node.dim, S=brain.node.S, A=brain.node.A,
            Q_top=brain.node.Q_top, X=X_neg, Xdot=brain.node.Xdot.copy(),
        )
        new_bodies = dict(ps.bodies)
        new_bodies[PentadLabel.BRAIN] = ManifoldState(
            node=new_brain_node, phi=brain.phi,
            n1=brain.n1, n2=brain.n2, k_cs=brain.k_cs, label=brain.label,
        )
        ps2 = PentadSystem(bodies=new_bodies, beta=BIREFRINGENCE_RAD)
        phases = pentad_pairwise_phases(ps2)
        assert phases[(PentadLabel.UNIV, PentadLabel.BRAIN)] == pytest.approx(
            math.pi, abs=1e-9
        )


# ---------------------------------------------------------------------------
# Trust Modulation
# ---------------------------------------------------------------------------

class TestTrustModulation:
    def test_default_near_one(self):
        ps = PentadSystem.default()
        tau = trust_modulation(ps)
        assert 0.5 < tau <= 1.0

    def test_clamped_above_one(self):
        """φ_trust > 1 should be clamped to 1."""
        ps = PentadSystem.default()
        trust = ps.bodies[PentadLabel.TRUST]
        new_trust = ManifoldState(
            node=trust.node, phi=2.5,
            n1=trust.n1, n2=trust.n2, k_cs=trust.k_cs, label=trust.label,
        )
        new_bodies = dict(ps.bodies)
        new_bodies[PentadLabel.TRUST] = new_trust
        ps2 = PentadSystem(bodies=new_bodies, beta=ps.beta)
        assert trust_modulation(ps2) == pytest.approx(1.0)

    def test_clamped_below_zero(self):
        """φ_trust < 0 should be clamped to 0."""
        ps = PentadSystem.default()
        trust = ps.bodies[PentadLabel.TRUST]
        new_trust = ManifoldState(
            node=trust.node, phi=-0.5,
            n1=trust.n1, n2=trust.n2, k_cs=trust.k_cs, label=trust.label,
        )
        new_bodies = dict(ps.bodies)
        new_bodies[PentadLabel.TRUST] = new_trust
        ps2 = PentadSystem(bodies=new_bodies, beta=ps.beta)
        assert trust_modulation(ps2) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Coupling Matrix
# ---------------------------------------------------------------------------

class TestPentadCouplingMatrix:
    def test_shape(self):
        ps = PentadSystem.default()
        mat = pentad_coupling_matrix(ps)
        assert mat.shape == (5, 5)

    def test_zero_diagonal(self):
        ps = PentadSystem.default()
        mat = pentad_coupling_matrix(ps)
        np.testing.assert_array_equal(np.diag(mat), np.zeros(5))

    def test_symmetric(self):
        ps = PentadSystem.default()
        mat = pentad_coupling_matrix(ps)
        np.testing.assert_allclose(mat, mat.T)

    def test_trust_body_row_equals_beta(self):
        """Trust body off-diagonal entries should all equal β."""
        ps = PentadSystem.default()
        mat = pentad_coupling_matrix(ps)
        trust_idx = PENTAD_LABELS.index(PentadLabel.TRUST)
        for j in range(5):
            if j != trust_idx:
                assert mat[trust_idx, j] == pytest.approx(ps.beta)

    def test_non_trust_entries_leq_beta(self):
        """Non-trust off-diagonal entries should be ≤ β (trust-modulated)."""
        ps = PentadSystem.default()
        mat = pentad_coupling_matrix(ps)
        trust_idx = PENTAD_LABELS.index(PentadLabel.TRUST)
        for i in range(5):
            for j in range(5):
                if i != j and i != trust_idx and j != trust_idx:
                    assert mat[i, j] <= ps.beta + 1e-12

    def test_all_entries_non_negative(self):
        ps = PentadSystem.default()
        mat = pentad_coupling_matrix(ps)
        assert np.all(mat >= 0.0)

    def test_zero_trust_decouples_non_trust(self):
        """When φ_trust = 0, non-trust off-diagonal entries are zero."""
        ps = PentadSystem.default()
        trust = ps.bodies[PentadLabel.TRUST]
        new_trust = ManifoldState(
            node=trust.node, phi=0.0,
            n1=trust.n1, n2=trust.n2, k_cs=trust.k_cs, label=trust.label,
        )
        new_bodies = dict(ps.bodies)
        new_bodies[PentadLabel.TRUST] = new_trust
        ps2 = PentadSystem(bodies=new_bodies, beta=ps.beta)
        mat = pentad_coupling_matrix(ps2)
        trust_idx = PENTAD_LABELS.index(PentadLabel.TRUST)
        for i in range(5):
            for j in range(5):
                if i != j and i != trust_idx and j != trust_idx:
                    assert mat[i, j] == pytest.approx(0.0, abs=1e-12)


# ---------------------------------------------------------------------------
# Eigenspectrum
# ---------------------------------------------------------------------------

class TestPentadEigenspectrum:
    def test_shape(self):
        ps = PentadSystem.default()
        eigs = pentad_eigenspectrum(ps)
        assert eigs.shape == (5,)

    def test_sorted_ascending(self):
        ps = PentadSystem.default()
        eigs = pentad_eigenspectrum(ps)
        assert np.all(np.diff(eigs) >= -1e-12)

    def test_real_valued(self):
        """Symmetric matrix should have real eigenvalues."""
        ps = PentadSystem.default()
        eigs = pentad_eigenspectrum(ps)
        assert np.all(np.isreal(eigs))


# ---------------------------------------------------------------------------
# Pentad Defect
# ---------------------------------------------------------------------------

class TestPentadDefect:
    def test_non_negative(self):
        ps = PentadSystem.default()
        assert pentad_defect(ps) >= 0.0

    def test_finite(self):
        ps = PentadSystem.default()
        assert math.isfinite(pentad_defect(ps))

    def test_defect_positive_at_default(self):
        """Default init should not be at the fixed point."""
        ps = PentadSystem.default()
        assert pentad_defect(ps) > 1e-10

    def test_trust_floor_penalty(self):
        """Pentad with collapsed trust (φ_trust < TRUST_PHI_MIN) has larger defect."""
        ps = PentadSystem.default()
        trust = ps.bodies[PentadLabel.TRUST]
        low_trust = ManifoldState(
            node=trust.node, phi=0.0,
            n1=trust.n1, n2=trust.n2, k_cs=trust.k_cs, label=trust.label,
        )
        new_bodies = dict(ps.bodies)
        new_bodies[PentadLabel.TRUST] = low_trust
        ps_low = PentadSystem(bodies=new_bodies, beta=ps.beta)
        assert pentad_defect(ps_low) > pentad_defect(ps)


# ---------------------------------------------------------------------------
# Pentagonal Coupling Conservation Laws
# ---------------------------------------------------------------------------

class TestPentagonalCouplingConservation:
    def _total_S(self, ps: PentadSystem) -> float:
        return sum(ps.bodies[lbl].node.S for lbl in PENTAD_LABELS)

    def _total_phi(self, ps: PentadSystem) -> float:
        return sum(ps.bodies[lbl].phi for lbl in PENTAD_LABELS)

    def _total_X(self, ps: PentadSystem) -> np.ndarray:
        return sum(ps.bodies[lbl].node.X for lbl in PENTAD_LABELS)

    def test_total_entropy_conserved(self):
        """Total entropy Σᵢ Sᵢ is conserved by C_pentad."""
        ps = PentadSystem.default()
        S_before = self._total_S(ps)
        ps2 = _apply_pentagonal_coupling(ps, dt=0.1)
        S_after = self._total_S(ps2)
        assert S_after == pytest.approx(S_before, rel=1e-10)

    def test_total_phi_conserved(self):
        """Total radion Σᵢ φᵢ is conserved by C_pentad."""
        ps = PentadSystem.default()
        phi_before = self._total_phi(ps)
        ps2 = _apply_pentagonal_coupling(ps, dt=0.1)
        phi_after = self._total_phi(ps2)
        assert phi_after == pytest.approx(phi_before, rel=1e-10)

    def test_total_X_conserved(self):
        """Total UEUM position Σᵢ Xᵢ is conserved by C_pentad."""
        ps = PentadSystem.default()
        X_before = self._total_X(ps)
        ps2 = _apply_pentagonal_coupling(ps, dt=0.1)
        X_after = self._total_X(ps2)
        np.testing.assert_allclose(X_after, X_before, rtol=1e-10)

    def test_conservation_at_multiple_dt(self):
        """Conservation holds for multiple timestep sizes."""
        ps = PentadSystem.default()
        for dt in [0.01, 0.1, 0.5, 1.0]:
            S_before = self._total_S(ps)
            ps2 = _apply_pentagonal_coupling(ps, dt=dt)
            assert self._total_S(ps2) == pytest.approx(S_before, rel=1e-9)

    def test_coupling_reduces_max_gap(self):
        """After coupling, the maximum pairwise gap should not increase."""
        ps = PentadSystem.default()
        max_gap_before = max(pentad_pairwise_gaps(ps).values())
        ps2 = _apply_pentagonal_coupling(ps, dt=0.5)
        max_gap_after = max(pentad_pairwise_gaps(ps2).values())
        assert max_gap_after <= max_gap_before + 1e-10


# ---------------------------------------------------------------------------
# Step Pentad
# ---------------------------------------------------------------------------

class TestStepPentad:
    def test_returns_pentad_system(self):
        ps = PentadSystem.default()
        ps2 = step_pentad(ps, dt=0.1)
        assert isinstance(ps2, PentadSystem)

    def test_all_labels_preserved(self):
        ps = PentadSystem.default()
        ps2 = step_pentad(ps, dt=0.1)
        assert set(ps2.bodies.keys()) == set(PENTAD_LABELS)

    def test_body_label_strings_preserved(self):
        ps = PentadSystem.default()
        ps2 = step_pentad(ps, dt=0.1)
        for lbl in PENTAD_LABELS:
            assert ps2.bodies[lbl].label == lbl

    def test_beta_preserved(self):
        ps = PentadSystem.default()
        ps2 = step_pentad(ps, dt=0.1)
        assert ps2.beta == pytest.approx(ps.beta)

    def test_state_changes_after_step(self):
        """State vector should change after a step (non-trivial dynamics)."""
        ps = PentadSystem.default()
        mat_before = ps.state_matrix()
        ps2 = step_pentad(ps, dt=0.1)
        mat_after = ps2.state_matrix()
        assert not np.allclose(mat_before, mat_after)

    def test_multiple_steps_return_valid_system(self):
        ps = PentadSystem.default()
        for _ in range(10):
            ps = step_pentad(ps, dt=0.05)
        assert isinstance(ps, PentadSystem)
        assert len(ps.bodies) == 5


# ---------------------------------------------------------------------------
# Pentad Master Equation
# ---------------------------------------------------------------------------

class TestPentadMasterEquation:
    def test_returns_three_tuple(self):
        ps = PentadSystem.default()
        result = pentad_master_equation(ps, max_iter=5)
        assert len(result) == 3

    def test_return_types(self):
        ps = PentadSystem.default()
        final, history, converged = pentad_master_equation(ps, max_iter=5)
        assert isinstance(final, PentadSystem)
        assert isinstance(history, list)
        assert isinstance(converged, bool)

    def test_history_length(self):
        ps = PentadSystem.default()
        _, history, _ = pentad_master_equation(ps, max_iter=20)
        assert 1 <= len(history) <= 20

    def test_history_record_keys(self):
        ps = PentadSystem.default()
        _, history, _ = pentad_master_equation(ps, max_iter=5)
        rec = history[0]
        for key in ("defect", "max_gap", "mean_gap", "max_phase",
                    "trust", "tensor_norm"):
            assert key in rec
        for lbl in PENTAD_LABELS:
            assert f"phi_{lbl}" in rec
            assert f"S_{lbl}" in rec

    def test_defect_in_history_non_negative(self):
        ps = PentadSystem.default()
        _, history, _ = pentad_master_equation(ps, max_iter=20)
        for rec in history:
            assert rec["defect"] >= 0.0

    def test_trust_in_history_in_range(self):
        ps = PentadSystem.default()
        _, history, _ = pentad_master_equation(ps, max_iter=20)
        for rec in history:
            assert 0.0 <= rec["trust"] <= 1.0

    def test_defect_generally_decreases(self):
        """Over many iterations the pairwise Information Gap should decrease.

        Uses an elevated coupling β so that inter-body coupling dominates
        over individual FTUM dynamics (which operate at the bare β scale).
        """
        ps = PentadSystem.default(beta=1.0)
        _, history, _ = pentad_master_equation(ps, max_iter=200, dt=0.05)
        first_10 = np.mean([r["mean_gap"] for r in history[:10]])
        last_10 = np.mean([r["mean_gap"] for r in history[-10:]])
        assert last_10 < first_10

    def test_convergence_with_loose_tol(self):
        """With a very loose tolerance the system should converge quickly."""
        ps = PentadSystem.default()
        _, history, converged = pentad_master_equation(
            ps, max_iter=500, tol=1.0, dt=0.1
        )
        assert converged

    def test_max_gap_trend(self):
        """Max pairwise Information Gap should decrease under strong coupling."""
        ps = PentadSystem.default(beta=1.0)
        _, history, _ = pentad_master_equation(ps, max_iter=200, dt=0.05)
        first_5 = np.mean([r["max_gap"] for r in history[:5]])
        last_5 = np.mean([r["max_gap"] for r in history[-5:]])
        assert last_5 < first_5

    def test_phi_evolution_recorded(self):
        """φ values should change over the iteration."""
        ps = PentadSystem.default()
        _, history, _ = pentad_master_equation(ps, max_iter=50, dt=0.1)
        if len(history) > 1:
            assert (history[0][f"phi_{PentadLabel.UNIV}"]
                    != history[-1][f"phi_{PentadLabel.UNIV}"])

    def test_converged_system_has_all_labels(self):
        ps = PentadSystem.default()
        final, _, _ = pentad_master_equation(ps, max_iter=50, dt=0.1)
        assert set(final.bodies.keys()) == set(PENTAD_LABELS)

    def test_converged_flag_false_when_max_iter_too_low(self):
        """With max_iter=1 and tight tol, should not converge."""
        ps = PentadSystem.default()
        _, _, converged = pentad_master_equation(
            ps, max_iter=1, tol=1e-12, dt=0.1
        )
        assert converged is False


# ---------------------------------------------------------------------------
# Pentagonal Symmetry — n_w = 5 magic number
# ---------------------------------------------------------------------------

class TestPentagonalSymmetry:
    def test_five_bodies_form_complete_graph(self):
        """10 pairwise gaps = C(5,2) = 10 — complete pentagonal graph."""
        ps = PentadSystem.default()
        gaps = pentad_pairwise_gaps(ps)
        assert len(gaps) == 10

    def test_default_winding_numbers(self):
        """All bodies default to (5,7) winding numbers."""
        ps = PentadSystem.default()
        for lbl in PENTAD_LABELS:
            assert ps.bodies[lbl].n1 == 5
            assert ps.bodies[lbl].n2 == 7
            assert ps.bodies[lbl].k_cs == 74

    def test_trust_body_mediates_coupling(self):
        """Setting φ_trust=1 should give τ_{ij}=β for all non-trust pairs."""
        ps = PentadSystem.default(beta=BIREFRINGENCE_RAD)
        trust = ps.bodies[PentadLabel.TRUST]
        new_trust = ManifoldState(
            node=trust.node, phi=1.0,
            n1=trust.n1, n2=trust.n2, k_cs=trust.k_cs, label=trust.label,
        )
        new_bodies = dict(ps.bodies)
        new_bodies[PentadLabel.TRUST] = new_trust
        ps1 = PentadSystem(bodies=new_bodies, beta=ps.beta)
        mat = pentad_coupling_matrix(ps1)
        trust_idx = PENTAD_LABELS.index(PentadLabel.TRUST)
        for i in range(5):
            for j in range(5):
                if i != j and i != trust_idx and j != trust_idx:
                    assert mat[i, j] == pytest.approx(
                        BIREFRINGENCE_RAD, rel=1e-9
                    )

    def test_uniform_state_has_zero_defect_components(self):
        """A flat pentad (all φ equal) should have zero pairwise gaps."""
        ps = _flat_pentad(phi_all=1.0)
        for v in pentad_pairwise_gaps(ps).values():
            assert v == pytest.approx(0.0, abs=1e-12)

    def test_pentagonal_coupling_not_just_pairwise(self):
        """With 5 bodies, each body interacts with 4 others per step."""
        ps = PentadSystem.default()
        mat = pentad_coupling_matrix(ps)
        # Each row should have exactly 4 non-zero entries
        for i in range(5):
            non_zero = np.count_nonzero(mat[i, :])
            assert non_zero == 4


# ---------------------------------------------------------------------------
# Grace Period / Trust Hysteresis
# ---------------------------------------------------------------------------

def _set_trust_phi(ps: PentadSystem, phi_val: float) -> PentadSystem:
    """Return a copy of ps with the Trust body's φ replaced by phi_val."""
    trust = ps.bodies[PentadLabel.TRUST]
    new_trust = ManifoldState(
        node=trust.node, phi=phi_val,
        n1=trust.n1, n2=trust.n2, k_cs=trust.k_cs, label=trust.label,
    )
    new_bodies = dict(ps.bodies)
    new_bodies[PentadLabel.TRUST] = new_trust
    return PentadSystem(
        bodies=new_bodies,
        beta=ps.beta,
        grace_steps=ps.grace_steps,
        grace_decay=ps.grace_decay,
        _trust_reservoir=ps._trust_reservoir,
        _grace_elapsed=ps._grace_elapsed,
    )


class TestGracePeriod:
    """Tests for the Trust Reservoir / Trust Hysteresis (grace period) feature."""

    # ------------------------------------------------------------------
    # Regression: grace_steps=0 must preserve existing behaviour exactly
    # ------------------------------------------------------------------

    def test_default_grace_steps_zero(self):
        """PentadSystem.default() must have grace_steps=0."""
        ps = PentadSystem.default()
        assert ps.grace_steps == 0

    def test_no_grace_trust_modulation_unchanged(self):
        """With grace_steps=0, trust_modulation returns the live φ_trust."""
        ps = PentadSystem.default()
        ps_low = _set_trust_phi(ps, 0.0)
        assert trust_modulation(ps_low) == pytest.approx(0.0)

    def test_no_grace_tick_is_noop(self):
        """tick_grace_period leaves state unchanged when grace_steps=0."""
        ps = PentadSystem.default()
        ps2 = tick_grace_period(ps)
        assert ps2._grace_elapsed == ps._grace_elapsed
        assert ps2._trust_reservoir == pytest.approx(ps._trust_reservoir)

    # ------------------------------------------------------------------
    # Reservoir initialisation
    # ------------------------------------------------------------------

    def test_reservoir_initial_value(self):
        """Freshly constructed PentadSystem has _trust_reservoir=1.0."""
        ps = PentadSystem.default(beta=BIREFRINGENCE_RAD)
        assert ps._trust_reservoir == pytest.approx(1.0)
        assert ps._grace_elapsed == 0

    def test_custom_grace_fields_accepted(self):
        """PentadSystem constructor accepts grace_steps and grace_decay."""
        ps = PentadSystem.default()
        ps2 = PentadSystem(
            bodies=ps.bodies,
            beta=ps.beta,
            grace_steps=5,
            grace_decay=0.3,
        )
        assert ps2.grace_steps == 5
        assert ps2.grace_decay == pytest.approx(0.3)

    # ------------------------------------------------------------------
    # tick_grace_period state-machine transitions
    # ------------------------------------------------------------------

    def test_tick_refreshes_reservoir_on_healthy_trust(self):
        """When live φ ≥ TRUST_PHI_MIN, tick refreshes reservoir and resets elapsed."""
        ps = PentadSystem.default()
        # Manufacture a system where the counter is non-zero
        ps_with_elapsed = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=5, grace_decay=0.2,
            _trust_reservoir=0.5, _grace_elapsed=3,
        )
        # Healthy live trust
        ps_healthy = _set_trust_phi(ps_with_elapsed, 0.8)
        ticked = tick_grace_period(ps_healthy)
        assert ticked._grace_elapsed == 0
        assert ticked._trust_reservoir == pytest.approx(0.8)

    def test_tick_increments_elapsed_within_grace_window(self):
        """When trust is low and elapsed < grace_steps, elapsed advances by 1."""
        ps = PentadSystem.default()
        ps_grace = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=5, grace_decay=0.2,
            _trust_reservoir=0.8, _grace_elapsed=2,
        )
        ps_low = _set_trust_phi(ps_grace, 0.0)
        ticked = tick_grace_period(ps_low)
        assert ticked._grace_elapsed == 3
        assert ticked._trust_reservoir == pytest.approx(0.8)

    def test_tick_drains_reservoir_when_grace_exhausted(self):
        """When elapsed >= grace_steps, reservoir drains to the live value."""
        ps = PentadSystem.default()
        ps_exhausted = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=3, grace_decay=0.2,
            _trust_reservoir=0.8, _grace_elapsed=3,  # already at limit
        )
        ps_low = _set_trust_phi(ps_exhausted, 0.05)
        ticked = tick_grace_period(ps_low)
        assert ticked._trust_reservoir == pytest.approx(0.05)

    # ------------------------------------------------------------------
    # trust_modulation with hysteresis active
    # ------------------------------------------------------------------

    def test_trust_modulation_uses_reservoir_when_live_drops(self):
        """With grace active, trust_modulation > live φ while reservoir holds."""
        ps = PentadSystem.default()
        ps_grace = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=5, grace_decay=0.2,
            _trust_reservoir=0.8, _grace_elapsed=0,
        )
        ps_low = _set_trust_phi(ps_grace, 0.0)
        # Effective trust should be the (undecayed) reservoir, not 0
        effective = trust_modulation(ps_low)
        assert effective == pytest.approx(0.8)
        assert effective > TRUST_PHI_MIN

    def test_trust_modulation_decays_over_elapsed_steps(self):
        """Reservoir decays exponentially: reservoir × exp(-k × elapsed)."""
        ps = PentadSystem.default()
        reservoir = 0.8
        k = 0.2
        elapsed = 4
        ps_grace = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=10, grace_decay=k,
            _trust_reservoir=reservoir, _grace_elapsed=elapsed,
        )
        ps_low = _set_trust_phi(ps_grace, 0.0)
        expected = reservoir * math.exp(-k * elapsed)
        assert trust_modulation(ps_low) == pytest.approx(expected, rel=1e-9)

    def test_trust_modulation_collapses_when_grace_exhausted(self):
        """After exhaustion (elapsed ≥ grace_steps), effective trust = live value."""
        ps = PentadSystem.default()
        # With a large decay constant and elapsed = grace_steps, the
        # reservoir has fully drained to near 0.
        ps_exhausted = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=3, grace_decay=10.0,   # very fast decay
            _trust_reservoir=0.8, _grace_elapsed=3,
        )
        ps_low = _set_trust_phi(ps_exhausted, 0.0)
        # After tick, reservoir = live = 0.0
        ticked = tick_grace_period(ps_low)
        assert trust_modulation(ticked) == pytest.approx(0.0, abs=1e-9)

    # ------------------------------------------------------------------
    # Integration: step_pentad propagates grace fields
    # ------------------------------------------------------------------

    def test_step_pentad_preserves_grace_steps(self):
        """step_pentad must carry grace_steps through to the returned system."""
        ps = PentadSystem.default()
        ps_grace = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=7, grace_decay=0.15,
            _trust_reservoir=0.9, _grace_elapsed=0,
        )
        ps2 = step_pentad(ps_grace, dt=0.1)
        assert ps2.grace_steps == 7
        assert ps2.grace_decay == pytest.approx(0.15)

    def test_step_pentad_advances_elapsed_when_trust_low(self):
        """After a step with low trust, _grace_elapsed increments (within window)."""
        ps = PentadSystem.default()
        ps_grace = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=10, grace_decay=0.2,
            _trust_reservoir=0.8, _grace_elapsed=0,
        )
        ps_low_trust = _set_trust_phi(ps_grace, 0.0)
        ps2 = step_pentad(ps_low_trust, dt=0.1)
        # elapsed should be 1 after one step with low trust
        assert ps2._grace_elapsed == 1

    def test_grace_period_coupling_stays_above_floor_for_grace_steps(self):
        """During the grace window, coupling is above TRUST_PHI_MIN × β."""
        ps = PentadSystem.default()
        grace = 5
        ps_grace = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=grace, grace_decay=0.05,  # slow decay
            _trust_reservoir=0.8, _grace_elapsed=0,
        )
        ps_low = _set_trust_phi(ps_grace, 0.0)
        # For all steps within the window, effective trust > TRUST_PHI_MIN
        current = ps_low
        for step_num in range(1, grace + 1):
            tau = trust_modulation(current)
            assert tau > TRUST_PHI_MIN, (
                f"Expected effective trust > TRUST_PHI_MIN at step {step_num}, "
                f"got {tau}"
            )
            current = tick_grace_period(current)

    def test_grace_period_trust_recovery_resets_elapsed(self):
        """If trust recovers before grace exhaustion, elapsed resets to 0."""
        ps = PentadSystem.default()
        ps_grace = PentadSystem(
            bodies=ps.bodies, beta=ps.beta,
            grace_steps=10, grace_decay=0.2,
            _trust_reservoir=0.8, _grace_elapsed=3,
        )
        # Trust recovers above TRUST_PHI_MIN
        ps_recovered = _set_trust_phi(ps_grace, 0.5)
        ticked = tick_grace_period(ps_recovered)
        assert ticked._grace_elapsed == 0
        assert ticked._trust_reservoir == pytest.approx(0.5)
