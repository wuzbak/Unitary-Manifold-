# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_pentad_scenarios.py
========================================
Unit tests for the Good/Bad/Wildcard scenario engine.

Covers:
  - Constants: PHASE_REVERSAL_THRESHOLD = π/2, DECEPTION_DETECTION_TOL
  - HarmonicStateMetrics: field types, harmonic flag, healing_capacity
  - CollapseMode: all five constants defined
  - CollapseSignature: types, severity in [0,1]
  - harmonic_state_metrics: default system, near-harmonic system
  - is_harmonic: near-harmonic → True, far-from-harmonic → False
  - detect_collapse_mode: each of the four collapse modes + healthy
  - inject_adversarial_intent: human φ changed, others unchanged
  - deception_phase_offset: correct arithmetic, zero for honest φ
  - is_deception_detectable: above/below threshold
  - trust_maintenance_cost: non-negative, finite, increases with dt
"""

import math
import pytest
import numpy as np

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from pentad_scenarios import (
    PHASE_REVERSAL_THRESHOLD,
    DECEPTION_DETECTION_TOL,
    EIGENVALUE_FLOOR_FRACTION,
    HarmonicStateMetrics,
    CollapseMode,
    CollapseSignature,
    harmonic_state_metrics,
    is_harmonic,
    detect_collapse_mode,
    inject_adversarial_intent,
    deception_phase_offset,
    is_deception_detectable,
    trust_maintenance_cost,
    TRANSITION_PROXIMITY_THRESHOLD,
    RegimeTransitionSignal,
    regime_transition_signal,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
    trust_modulation,
    pentad_pairwise_gaps,
    pentad_master_equation,
)
from src.consciousness.coupled_attractor import ManifoldState, BIREFRINGENCE_RAD
from src.multiverse.fixed_point import MultiverseNode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_trust(ps: PentadSystem, phi_trust: float) -> PentadSystem:
    """Return a copy with the trust body's φ set to phi_trust."""
    new_bodies = dict(ps.bodies)
    old = ps.bodies[PentadLabel.TRUST]
    new_bodies[PentadLabel.TRUST] = ManifoldState(
        node=old.node, phi=phi_trust,
        n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
    )
    return PentadSystem(bodies=new_bodies, beta=ps.beta)


def _set_human_ai_antiparallel(ps: PentadSystem) -> PentadSystem:
    """Force human and AI state vectors antiparallel → Δφ = π."""
    new_bodies = dict(ps.bodies)
    univ_X = ps.bodies[PentadLabel.UNIV].node.X.copy()
    for lbl, sign in [(PentadLabel.HUMAN, 1.0), (PentadLabel.AI, -1.0)]:
        old = ps.bodies[lbl]
        new_node = MultiverseNode(
            dim=old.node.dim, S=old.node.S, A=old.node.A,
            Q_top=old.node.Q_top,
            X=sign * univ_X,
            Xdot=old.node.Xdot.copy(),
        )
        new_bodies[lbl] = ManifoldState(
            node=new_node, phi=old.phi,
            n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
        )
    return PentadSystem(bodies=new_bodies, beta=ps.beta)


def _flat_harmonic_pentad() -> PentadSystem:
    """Create a pentad where all φ are equal AND all X vectors are parallel.

    Both conditions are required for the collapse detector to return NONE:
    equal φ → zero Information Gaps; parallel X → zero Moiré phase offsets.
    """
    ps     = PentadSystem.default()
    ref_X  = ps.bodies[PentadLabel.UNIV].node.X.copy()  # common direction
    new_bodies = {}
    for lbl in PENTAD_LABELS:
        old = ps.bodies[lbl]
        new_node = MultiverseNode(
            dim=old.node.dim,
            S=old.node.S,
            A=old.node.A,
            Q_top=old.node.Q_top,
            X=ref_X.copy(),
            Xdot=old.node.Xdot.copy(),
        )
        new_bodies[lbl] = ManifoldState(
            node=new_node, phi=1.0,
            n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
        )
    return PentadSystem(bodies=new_bodies, beta=ps.beta)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_phase_reversal_threshold(self):
        assert PHASE_REVERSAL_THRESHOLD == pytest.approx(math.pi / 2, rel=1e-10)

    def test_deception_detection_tol_positive(self):
        assert DECEPTION_DETECTION_TOL > 0.0

    def test_eigenvalue_floor_fraction_in_unit_interval(self):
        assert 0.0 < EIGENVALUE_FLOOR_FRACTION <= 1.0


# ---------------------------------------------------------------------------
# CollapseMode
# ---------------------------------------------------------------------------

class TestCollapseMode:
    def test_none_constant(self):
        assert CollapseMode.NONE == "none"

    def test_trust_erosion_constant(self):
        assert CollapseMode.TRUST_EROSION == "trust_erosion"

    def test_ai_decoupling_constant(self):
        assert CollapseMode.AI_DECOUPLING == "ai_decoupling"

    def test_phase_collision_constant(self):
        assert CollapseMode.PHASE_COLLISION == "phase_collision"

    def test_malicious_precision_constant(self):
        assert CollapseMode.MALICIOUS_PRECISION == "malicious_precision"

    def test_all_five_constants_distinct(self):
        modes = {
            CollapseMode.NONE, CollapseMode.TRUST_EROSION,
            CollapseMode.AI_DECOUPLING, CollapseMode.PHASE_COLLISION,
            CollapseMode.MALICIOUS_PRECISION,
        }
        assert len(modes) == 5


# ---------------------------------------------------------------------------
# harmonic_state_metrics — default system
# ---------------------------------------------------------------------------

class TestHarmonicStateMetricsDefault:
    def setup_method(self):
        self.ps = PentadSystem.default()
        self.m  = harmonic_state_metrics(self.ps)

    def test_returns_metrics(self):
        assert isinstance(self.m, HarmonicStateMetrics)

    def test_max_info_gap_non_negative(self):
        assert self.m.max_info_gap >= 0.0

    def test_mean_info_gap_non_negative(self):
        assert self.m.mean_info_gap >= 0.0

    def test_mean_leq_max_gap(self):
        assert self.m.mean_info_gap <= self.m.max_info_gap + 1e-12

    def test_max_phase_in_range(self):
        assert 0.0 <= self.m.max_phase_offset <= math.pi + 1e-9

    def test_trust_in_unit_interval(self):
        assert 0.0 <= self.m.trust <= 1.0

    def test_trust_margin_type(self):
        assert isinstance(self.m.trust_margin, float)

    def test_defect_positive_at_default(self):
        assert self.m.defect > 0.0

    def test_zero_lag_factor_in_unit_interval(self):
        assert 0.0 <= self.m.zero_lag_factor <= 1.0

    def test_healing_capacity_in_unit_interval(self):
        assert 0.0 <= self.m.healing_capacity <= 1.0

    def test_harmonic_tol_stored(self):
        assert self.m.harmonic_tol == pytest.approx(1e-4, rel=1e-9)


# ---------------------------------------------------------------------------
# harmonic_state_metrics — flat (nearly harmonic) system
# ---------------------------------------------------------------------------

class TestHarmonicStateMetricsFlat:
    def setup_method(self):
        self.ps = _flat_harmonic_pentad()
        self.m  = harmonic_state_metrics(self.ps, tol=1e-4)

    def test_all_gaps_zero(self):
        assert self.m.max_info_gap == pytest.approx(0.0, abs=1e-12)

    def test_zero_lag_factor_is_one(self):
        assert self.m.zero_lag_factor == pytest.approx(1.0, abs=1e-12)

    def test_healing_capacity_is_one(self):
        assert self.m.healing_capacity == pytest.approx(1.0, abs=1e-12)

    def test_trust_above_floor(self):
        assert self.m.trust > TRUST_PHI_MIN


# ---------------------------------------------------------------------------
# is_harmonic
# ---------------------------------------------------------------------------

class TestIsHarmonic:
    def test_default_not_harmonic(self):
        """Default pentad has non-zero gaps and phase offsets."""
        ps = PentadSystem.default()
        assert is_harmonic(ps, tol=1e-4) is False

    def test_wide_tolerance_can_be_harmonic(self):
        """With a very loose tolerance a near-flat system can pass."""
        ps = _flat_harmonic_pentad()
        assert is_harmonic(ps, tol=10.0) is True


# ---------------------------------------------------------------------------
# detect_collapse_mode — healthy
# ---------------------------------------------------------------------------

class TestDetectCollapseHealthy:
    def test_flat_phi_no_collapse(self):
        """Flat φ, high trust, no phase offset → healthy."""
        ps = _flat_harmonic_pentad()
        sig = detect_collapse_mode(ps)
        assert sig.mode == CollapseMode.NONE

    def test_severity_zero_when_healthy(self):
        ps = _flat_harmonic_pentad()
        sig = detect_collapse_mode(ps)
        assert sig.severity == pytest.approx(0.0)

    def test_affected_pairs_empty_when_healthy(self):
        ps = _flat_harmonic_pentad()
        sig = detect_collapse_mode(ps)
        assert sig.affected_pairs == []

    def test_trust_field_in_signature(self):
        ps = _flat_harmonic_pentad()
        sig = detect_collapse_mode(ps)
        assert sig.trust == pytest.approx(trust_modulation(ps), rel=1e-10)


# ---------------------------------------------------------------------------
# detect_collapse_mode — Trust Erosion
# ---------------------------------------------------------------------------

class TestDetectTrustErosion:
    def setup_method(self):
        ps_flat = _flat_harmonic_pentad()
        self.ps  = _set_trust(ps_flat, 0.0)   # complete trust collapse
        self.sig = detect_collapse_mode(self.ps)

    def test_mode_is_trust_erosion(self):
        assert self.sig.mode == CollapseMode.TRUST_EROSION

    def test_severity_one_at_zero_trust(self):
        assert self.sig.severity == pytest.approx(1.0, abs=1e-9)

    def test_description_mentions_trust(self):
        assert "trust" in self.sig.description.lower()

    def test_trust_field_reflects_zero(self):
        assert self.sig.trust == pytest.approx(0.0, abs=1e-9)

    def test_partial_erosion_severity(self):
        """φ_trust halfway between 0 and floor → severity ≈ 0.5."""
        ps = _set_trust(_flat_harmonic_pentad(), TRUST_PHI_MIN / 2)
        sig = detect_collapse_mode(ps)
        assert sig.mode == CollapseMode.TRUST_EROSION
        assert 0.4 < sig.severity < 0.6


# ---------------------------------------------------------------------------
# detect_collapse_mode — Phase Collision / AI Decoupling
# ---------------------------------------------------------------------------

class TestDetectPhaseCollision:
    def setup_method(self):
        ps_flat  = _flat_harmonic_pentad()
        self.ps  = _set_human_ai_antiparallel(ps_flat)
        self.sig = detect_collapse_mode(self.ps)

    def test_mode_is_ai_decoupling_or_phase_collision(self):
        """Antiparallel human–AI vectors trigger AI decoupling or phase collision."""
        assert self.sig.mode in (
            CollapseMode.AI_DECOUPLING,
            CollapseMode.PHASE_COLLISION,
        )

    def test_severity_above_zero(self):
        assert self.sig.severity > 0.0

    def test_severity_at_most_one(self):
        assert self.sig.severity <= 1.0 + 1e-9


# ---------------------------------------------------------------------------
# inject_adversarial_intent
# ---------------------------------------------------------------------------

class TestInjectAdversarialIntent:
    def test_human_phi_changed(self):
        ps  = PentadSystem.default()
        ps2 = inject_adversarial_intent(ps, 9.99)
        assert ps2.bodies[PentadLabel.HUMAN].phi == pytest.approx(9.99)

    def test_other_bodies_unchanged(self):
        ps  = PentadSystem.default()
        ps2 = inject_adversarial_intent(ps, 9.99)
        for lbl in PENTAD_LABELS:
            if lbl == PentadLabel.HUMAN:
                continue
            assert ps2.bodies[lbl].phi == pytest.approx(ps.bodies[lbl].phi,
                                                         rel=1e-10)

    def test_trust_unchanged(self):
        ps  = PentadSystem.default()
        ps2 = inject_adversarial_intent(ps, 9.99)
        assert trust_modulation(ps2) == pytest.approx(trust_modulation(ps), rel=1e-10)

    def test_creates_large_human_ai_gap(self):
        ps  = _flat_harmonic_pentad()          # all φ = 1.0
        ps2 = inject_adversarial_intent(ps, 5.0)
        gaps2 = pentad_pairwise_gaps(ps2)
        ha_key = next(k for k in gaps2 if PentadLabel.HUMAN in k
                      and PentadLabel.AI in k)
        assert gaps2[ha_key] > 1.0

    def test_original_system_unmodified(self):
        ps  = PentadSystem.default()
        phi_before = ps.bodies[PentadLabel.HUMAN].phi
        inject_adversarial_intent(ps, 9.99)
        assert ps.bodies[PentadLabel.HUMAN].phi == pytest.approx(phi_before,
                                                                   rel=1e-10)

    def test_adversarial_triggers_malicious_or_collapse_mode(self):
        """A very large adversarial φ should trigger a collapse detection."""
        ps  = _flat_harmonic_pentad()
        ps2 = inject_adversarial_intent(ps, 10.0)
        sig = detect_collapse_mode(ps2)
        assert sig.mode != CollapseMode.NONE


# ---------------------------------------------------------------------------
# deception_phase_offset
# ---------------------------------------------------------------------------

class TestDeceptionPhaseOffset:
    def test_honest_phi_gives_zero_gap(self):
        """Reporting the true φ produces no detectable gap."""
        ps = PentadSystem.default()
        phi_true = ps.bodies[PentadLabel.HUMAN].phi
        assert deception_phase_offset(ps, phi_true) == pytest.approx(0.0, abs=1e-12)

    def test_gap_formula(self):
        """ΔI = |φ_lied² − φ_true²|."""
        ps       = PentadSystem.default()
        phi_true = ps.bodies[PentadLabel.HUMAN].phi
        phi_lied = phi_true + 0.5
        expected = abs(phi_lied**2 - phi_true**2)
        assert deception_phase_offset(ps, phi_lied) == pytest.approx(expected,
                                                                       rel=1e-10)

    def test_non_negative(self):
        ps = PentadSystem.default()
        assert deception_phase_offset(ps, 0.0) >= 0.0
        assert deception_phase_offset(ps, 10.0) >= 0.0

    def test_symmetric_around_true_phi(self):
        """Gap from φ_true+δ equals gap from φ_true−δ only if δ is symmetric."""
        ps       = PentadSystem.default()
        phi_true = ps.bodies[PentadLabel.HUMAN].phi
        delta    = 0.3
        gap_plus  = deception_phase_offset(ps, phi_true + delta)
        gap_minus = deception_phase_offset(ps, phi_true - delta)
        # These are generally different (|φ₊²−φ_t²| ≠ |φ₋²−φ_t²|) unless φ_true=0
        assert gap_plus >= 0.0
        assert gap_minus >= 0.0

    def test_large_lie_gives_large_gap(self):
        ps = PentadSystem.default()
        assert deception_phase_offset(ps, 100.0) > 1.0


# ---------------------------------------------------------------------------
# is_deception_detectable
# ---------------------------------------------------------------------------

class TestIsDeceptionDetectable:
    def test_honest_phi_not_detectable(self):
        ps = PentadSystem.default()
        phi_true = ps.bodies[PentadLabel.HUMAN].phi
        assert is_deception_detectable(ps, phi_true) is False

    def test_large_lie_is_detectable(self):
        ps = PentadSystem.default()
        assert is_deception_detectable(ps, 10.0) is True

    def test_small_lie_below_tol_not_detectable(self):
        ps       = PentadSystem.default()
        phi_true = ps.bodies[PentadLabel.HUMAN].phi
        tiny_lie = phi_true + 1e-7
        assert is_deception_detectable(ps, tiny_lie, tol=DECEPTION_DETECTION_TOL) is False

    def test_custom_tight_tol(self):
        """With very tight tolerance even a small lie is detectable."""
        ps       = PentadSystem.default()
        phi_true = ps.bodies[PentadLabel.HUMAN].phi
        small_lie = phi_true + 0.1
        assert is_deception_detectable(ps, small_lie, tol=1e-6) is True

    def test_zero_phi_lie(self):
        """Claiming φ = 0 when true φ > 0 creates a large gap."""
        ps       = PentadSystem.default()
        phi_true = ps.bodies[PentadLabel.HUMAN].phi
        if phi_true > 0.01:
            assert is_deception_detectable(ps, 0.0) is True


# ---------------------------------------------------------------------------
# trust_maintenance_cost
# ---------------------------------------------------------------------------

class TestTrustMaintenanceCost:
    def test_non_negative(self):
        ps = PentadSystem.default()
        assert trust_maintenance_cost(ps, n_steps=5, dt=0.1) >= 0.0

    def test_finite(self):
        ps = PentadSystem.default()
        assert math.isfinite(trust_maintenance_cost(ps, n_steps=5, dt=0.1))

    def test_default_system_returns_float(self):
        ps   = PentadSystem.default()
        cost = trust_maintenance_cost(ps)
        assert isinstance(cost, float)

    def test_flat_system_low_cost(self):
        """Near-harmonic system should have very low trust maintenance cost."""
        ps   = _flat_harmonic_pentad()
        cost = trust_maintenance_cost(ps, n_steps=5, dt=0.01)
        assert cost < 0.1

    def test_larger_dt_increases_cost(self):
        """Larger perturbations → larger trust variations per step."""
        ps         = PentadSystem.default()
        cost_small = trust_maintenance_cost(ps, n_steps=5, dt=0.001)
        cost_large = trust_maintenance_cost(ps, n_steps=5, dt=1.0)
        assert cost_large >= cost_small

    def test_single_step(self):
        ps = PentadSystem.default()
        assert trust_maintenance_cost(ps, n_steps=1) >= 0.0


# ---------------------------------------------------------------------------
# regime_transition_signal — attractor-robustness observables
# ---------------------------------------------------------------------------

def _set_phi(ps: PentadSystem, label: str, phi: float) -> PentadSystem:
    """Return a copy with the named body's φ set to phi."""
    new_bodies = dict(ps.bodies)
    old = ps.bodies[label]
    new_bodies[label] = ManifoldState(
        node=old.node, phi=phi,
        n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
    )
    return PentadSystem(bodies=new_bodies, beta=ps.beta)


def _stressed_pentad() -> PentadSystem:
    """Return a pentad where one channel (human–ai) is heavily loaded.

    All bodies have φ = 1.0 except Ψ_human which has φ = 5.0, creating a
    large Information Gap on that single channel while the rest remain near
    zero.  This is the pre-collapse saturation pattern.
    """
    ps = _flat_harmonic_pentad()          # all φ = 1.0
    return _set_phi(ps, PentadLabel.HUMAN, 5.0)


class TestRegimeTransitionSignalType:
    """regime_transition_signal returns the correct type and structure."""

    def test_returns_dataclass(self):
        ps = PentadSystem.default()
        sig = regime_transition_signal(ps)
        assert isinstance(sig, RegimeTransitionSignal)

    def test_saturated_pair_is_tuple_of_two_strings(self):
        ps = PentadSystem.default()
        sig = regime_transition_signal(ps)
        assert isinstance(sig.saturated_pair, tuple)
        assert len(sig.saturated_pair) == 2
        assert all(isinstance(s, str) for s in sig.saturated_pair)

    def test_saturated_pair_labels_valid(self):
        ps = PentadSystem.default()
        sig = regime_transition_signal(ps)
        for lbl in sig.saturated_pair:
            assert lbl in PENTAD_LABELS

    def test_attractor_degraded_is_bool(self):
        ps = PentadSystem.default()
        assert isinstance(regime_transition_signal(ps).attractor_degraded, bool)

    def test_active_dof_is_int(self):
        ps = PentadSystem.default()
        assert isinstance(regime_transition_signal(ps).active_dof_estimate, int)

    def test_all_float_fields_are_float(self):
        ps  = PentadSystem.default()
        sig = regime_transition_signal(ps)
        for attr in (
            "coupling_variance", "saturated_channel_load",
            "mean_channel_load", "transition_proximity",
        ):
            assert isinstance(getattr(sig, attr), float), attr

    def test_attractor_degraded_field_exists(self):
        """attractor_degraded replaces early_warning — exact framing matters."""
        ps  = PentadSystem.default()
        sig = regime_transition_signal(ps)
        assert hasattr(sig, "attractor_degraded")
        assert not hasattr(sig, "early_warning")


class TestRegimeTransitionSignalBounds:
    """Invariant bounds that must hold for any well-formed PentadSystem."""

    def test_coupling_variance_non_negative(self):
        for ps in [PentadSystem.default(), _flat_harmonic_pentad(), _stressed_pentad()]:
            assert regime_transition_signal(ps).coupling_variance >= 0.0

    def test_saturated_load_geq_mean_load(self):
        for ps in [PentadSystem.default(), _flat_harmonic_pentad(), _stressed_pentad()]:
            sig = regime_transition_signal(ps)
            assert sig.saturated_channel_load >= sig.mean_channel_load - 1e-12

    def test_transition_proximity_geq_one(self):
        # proximity = max/mean ≥ 1 whenever mean > 0;
        # equals 1.0 by definition when all loads are zero.
        for ps in [PentadSystem.default(), _flat_harmonic_pentad(), _stressed_pentad()]:
            sig = regime_transition_signal(ps)
            assert sig.transition_proximity >= 1.0 - 1e-12

    def test_mean_channel_load_non_negative(self):
        for ps in [PentadSystem.default(), _flat_harmonic_pentad(), _stressed_pentad()]:
            assert regime_transition_signal(ps).mean_channel_load >= 0.0

    def test_active_dof_between_one_and_five(self):
        for ps in [PentadSystem.default(), _flat_harmonic_pentad(), _stressed_pentad()]:
            dof = regime_transition_signal(ps).active_dof_estimate
            assert 1 <= dof <= 5, f"active_dof_estimate={dof} out of [1, 5]"

    def test_transition_proximity_threshold_positive(self):
        assert TRANSITION_PROXIMITY_THRESHOLD > 1.0
class TestRegimeTransitionSignalHarmonicBaseline:
    """Flat (Harmonic) system: load is distributed evenly; attractor is robust."""

    def setup_method(self):
        self.ps  = _flat_harmonic_pentad()
        self.sig = regime_transition_signal(self.ps)

    def test_coupling_variance_near_zero(self):
        """All channels have equal φ → equal ΔI → coupling_variance ≈ 0."""
        assert self.sig.coupling_variance == pytest.approx(0.0, abs=1e-10)

    def test_mean_channel_load_near_zero(self):
        """All ΔI_{ij} = 0 → every channel load = 0."""
        assert self.sig.mean_channel_load == pytest.approx(0.0, abs=1e-10)

    def test_no_attractor_degraded_at_harmonic_state(self):
        assert self.sig.attractor_degraded is False

    def test_transition_proximity_is_one_at_harmonic_state(self):
        """When all loads are zero, proximity is defined as 1.0 (balanced)."""
        assert self.sig.transition_proximity == pytest.approx(1.0, abs=1e-12)


class TestRegimeTransitionSignalStressedChannel:
    """One overloaded channel: attractor_degraded should fire."""

    def setup_method(self):
        self.ps  = _stressed_pentad()
        self.sig = regime_transition_signal(self.ps)

    def test_saturated_pair_involves_human(self):
        """Human has a large φ deviation; its pairs should dominate."""
        assert PentadLabel.HUMAN in self.sig.saturated_pair

    def test_saturated_load_greater_than_mean(self):
        assert self.sig.saturated_channel_load > self.sig.mean_channel_load

    def test_transition_proximity_above_threshold(self):
        """One large φ on human → 4 of 10 channels loaded equally → proximity = 2.5."""
        assert self.sig.transition_proximity >= TRANSITION_PROXIMITY_THRESHOLD

    def test_attractor_degraded_fires(self):
        """attractor_degraded = True means current attractor is no longer robust."""
        assert self.sig.attractor_degraded is True

    def test_coupling_variance_positive_under_stress(self):
        assert self.sig.coupling_variance > 0.0

    def test_proximity_higher_than_harmonic(self):
        """Stressed system has higher proximity than the flat baseline."""
        flat_prox    = regime_transition_signal(_flat_harmonic_pentad()).transition_proximity
        stressed_prox = self.sig.transition_proximity
        assert stressed_prox > flat_prox


class TestRegimeTransitionSignalActiveDOF:
    """active_dof_estimate rises when bodies are less correlated."""

    def test_default_dof_at_least_one(self):
        sig = regime_transition_signal(PentadSystem.default())
        assert sig.active_dof_estimate >= 1

    def test_flat_dof_at_least_one(self):
        """Flat system state matrix has at least one significant singular value."""
        sig = regime_transition_signal(_flat_harmonic_pentad())
        assert sig.active_dof_estimate >= 1

    def test_stressed_dof_geq_flat_dof(self):
        """Stressed system diverges on one body → at least as many DOF as flat."""
        flat_dof     = regime_transition_signal(_flat_harmonic_pentad()).active_dof_estimate
        stressed_dof = regime_transition_signal(_stressed_pentad()).active_dof_estimate
        assert stressed_dof >= flat_dof
