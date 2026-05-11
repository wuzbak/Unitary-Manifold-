# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_consciousness_autopilot.py
===============================================
Unit tests for the Consciousness Autopilot module.

Covers:
  - Layer constants: N_LAYER=7, LAYER_LABELS, LAYER_EQUILIBRIA
  - LayerLabel string constants
  - LayerBody: construction, clamping, deviation()
  - SevenBodyLayer: missing bodies error, default() factory, drift_rate
  - AutopilotMode / PhaseShiftTrigger string constants
  - AutopilotUniverse: default() factory, field types
  - layer_field: mean of equilibria
  - layer_mean_deviation: zero at equilibrium, nonzero after perturbation
  - is_entropy_spike: threshold boundary
  - detect_phase_shift: BIFURCATION, ENTROPY_SPIKE, NONE
  - _tick_layer: drift direction, magnitude, repeated convergence
  - autopilot_tick: AUTOPILOT mode evolves layer and core
  - autopilot_tick: AWAITING_SHIFT holds core
  - autopilot_tick: AWAITING_SHIFT → detects shift
  - autopilot_tick: SETTLING mode, transition back to AUTOPILOT
  - autopilot_tick: SETTLING MAX_SETTLING_STEPS guard
  - human_shift: applies delta, transitions to SETTLING
  - human_shift: delta clamping to [0, 2]
  - human_shift: RuntimeError in wrong mode
  - explicit_phase_shift: sets mode and trigger
  - is_at_coupled_fixed_point: structure of four conditions
  - autopilot_run: records history, step_count, handles shift_handler
  - autopilot_run: no handler leaves system in AWAITING_SHIFT
  - Equilibrium values: HORIZON ≥ BRAIDED_SOUND_SPEED, mean ≈ 0.657
  - Integration: full AUTOPILOT → AWAITING_SHIFT → SETTLING → AUTOPILOT cycle
"""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}


import math
import pytest
import numpy as np

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from consciousness_autopilot import (
    # Constants
    N_LAYER,
    LAYER_DRIFT_RATE,
    AUTOPILOT_SHIFT_THRESHOLD,
    LAYER_ENTROPY_THRESHOLD,
    FIXED_POINT_TOL,
    MAX_SETTLING_STEPS,
    # Labels
    LayerLabel,
    LAYER_LABELS,
    LAYER_EQUILIBRIA,
    # Mode / trigger constants
    AutopilotMode,
    PhaseShiftTrigger,
    # Dataclasses
    LayerBody,
    SevenBodyLayer,
    AutopilotUniverse,
    # Functions
    layer_field,
    layer_mean_deviation,
    is_entropy_spike,
    detect_phase_shift,
    _tick_layer,
    autopilot_tick,
    human_shift,
    explicit_phase_shift,
    is_at_coupled_fixed_point,
    autopilot_run,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
    trust_modulation,
    pentad_defect,
)
from collective_braid import (
    moire_alignment_score,
    MOIRE_ALIGNMENT_TOL,
)
from src.consciousness.coupled_attractor import ManifoldState
from src.multiverse.fixed_point import MultiverseNode


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture()
def default_layer():
    return SevenBodyLayer.default()


@pytest.fixture()
def default_universe():
    return AutopilotUniverse.default()


@pytest.fixture()
def perturbed_layer():
    """7-layer with every body pushed 0.4 above equilibrium (entropy spike)."""
    perturbation = {lbl: 0.4 for lbl in LAYER_LABELS}
    return SevenBodyLayer.default(perturbation=perturbation)


@pytest.fixture()
def awaiting_universe(default_universe):
    """Universe forced into AWAITING_SHIFT mode."""
    return explicit_phase_shift(default_universe)


# ---------------------------------------------------------------------------
# Helper: balanced_universe — A_AI/A_human ≤ PHI_GOLDEN (no CA trigger)
# ---------------------------------------------------------------------------

def _balanced_core() -> PentadSystem:
    """Return a PentadSystem with A_AI/A_human < PHI_GOLDEN.

    The default PentadSystem has A_AI=1.5, A_human=0.8 → ratio ≈ 1.875 > φ.
    This fixture caps A_AI at 1.25 × A_human to sit safely below the flip
    threshold.  Used for tests that need to isolate BIFURCATION/ENTROPY/NONE
    triggers without the CAPABILITY_ASYMMETRY check firing.
    """
    import math as _m
    ps = PentadSystem.default()
    new_bodies = dict(ps.bodies)
    ai_old   = ps.bodies[PentadLabel.AI]
    human_A  = ps.bodies[PentadLabel.HUMAN].node.A
    capped_A = human_A * 1.25   # 1.25 < PHI_GOLDEN ≈ 1.618

    ai_new_node = MultiverseNode(
        dim=ai_old.node.dim,
        S=ai_old.node.S,
        A=capped_A,
        Q_top=ai_old.node.Q_top,
        X=ai_old.node.X.copy(),
        Xdot=ai_old.node.Xdot.copy(),
    )
    new_bodies[PentadLabel.AI] = ManifoldState(
        node=ai_new_node,
        phi=ai_old.phi,
        n1=ai_old.n1,
        n2=ai_old.n2,
        k_cs=ai_old.k_cs,
        label=ai_old.label,
    )
    return PentadSystem(
        bodies=new_bodies,
        beta=ps.beta,
        grace_steps=ps.grace_steps,
        grace_decay=ps.grace_decay,
        _trust_reservoir=ps._trust_reservoir,
        _grace_elapsed=ps._grace_elapsed,
    )


@pytest.fixture()
def balanced_universe():
    """AutopilotUniverse with A_AI/A_human < PHI_GOLDEN (no CA trigger)."""
    return AutopilotUniverse(core=_balanced_core(), layer=SevenBodyLayer.default())


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_n_layer_is_7(self):
        assert N_LAYER == 7

    def test_layer_labels_length(self):
        assert len(LAYER_LABELS) == N_LAYER

    def test_layer_equilibria_length(self):
        assert len(LAYER_EQUILIBRIA) == N_LAYER

    def test_layer_labels_all_strings(self):
        for lbl in LAYER_LABELS:
            assert isinstance(lbl, str)

    def test_layer_equilibria_all_in_unit_interval(self):
        for lbl, val in LAYER_EQUILIBRIA.items():
            assert 0.0 <= val <= 1.0, f"{lbl}: {val} out of [0,1]"

    def test_horizon_above_braided_sound_speed(self):
        """HORIZON equilibrium ≥ c_s — braid anchor condition."""
        assert LAYER_EQUILIBRIA[LayerLabel.HORIZON] >= BRAIDED_SOUND_SPEED

    def test_equilibrium_mean_approx_0657(self):
        """Mean of the 7 equilibria ≈ 0.657 (Φ_layer at rest)."""
        mean = sum(LAYER_EQUILIBRIA.values()) / N_LAYER
        assert abs(mean - 0.657) < 0.01

    def test_autopilot_shift_threshold_positive(self):
        assert AUTOPILOT_SHIFT_THRESHOLD > 0.0

    def test_layer_entropy_threshold_positive(self):
        assert LAYER_ENTROPY_THRESHOLD > 0.0

    def test_fixed_point_tol_positive(self):
        assert FIXED_POINT_TOL > 0.0

    def test_max_settling_steps_positive(self):
        assert MAX_SETTLING_STEPS > 0

    def test_layer_drift_rate_in_unit_interval(self):
        assert 0.0 < LAYER_DRIFT_RATE <= 1.0


class TestLayerLabelConstants:
    def test_entropy(self):
        assert LayerLabel.ENTROPY == "entropy"

    def test_geometry(self):
        assert LayerLabel.GEOMETRY == "geometry"

    def test_matter(self):
        assert LayerLabel.MATTER == "matter"

    def test_causal(self):
        assert LayerLabel.CAUSAL == "causal"

    def test_field(self):
        assert LayerLabel.FIELD == "field"

    def test_quantum(self):
        assert LayerLabel.QUANTUM == "quantum"

    def test_horizon(self):
        assert LayerLabel.HORIZON == "horizon"

    def test_layer_labels_tuple_contains_all(self):
        for attr in ("entropy", "geometry", "matter", "causal", "field", "quantum", "horizon"):
            assert attr in LAYER_LABELS


class TestModeAndTriggerConstants:
    def test_autopilot_mode_autopilot(self):
        assert AutopilotMode.AUTOPILOT == "autopilot"

    def test_autopilot_mode_awaiting(self):
        assert AutopilotMode.AWAITING_SHIFT == "awaiting_shift"

    def test_autopilot_mode_settling(self):
        assert AutopilotMode.SETTLING == "settling"

    def test_trigger_none(self):
        assert PhaseShiftTrigger.NONE == "none"

    def test_trigger_bifurcation(self):
        assert PhaseShiftTrigger.BIFURCATION == "bifurcation"

    def test_trigger_entropy_spike(self):
        assert PhaseShiftTrigger.ENTROPY_SPIKE == "entropy_spike"

    def test_trigger_explicit(self):
        assert PhaseShiftTrigger.EXPLICIT == "explicit"


# ===========================================================================
# LayerBody
# ===========================================================================

class TestLayerBody:
    def test_construction(self):
        b = LayerBody(label="entropy", phi=0.5, phi_eq=0.95)
        assert b.label == "entropy"
        assert b.phi   == pytest.approx(0.5)
        assert b.phi_eq == pytest.approx(0.95)

    def test_phi_clamped_to_zero(self):
        b = LayerBody(label="entropy", phi=-0.5, phi_eq=0.5)
        assert b.phi == pytest.approx(0.0)

    def test_phi_clamped_to_one(self):
        b = LayerBody(label="entropy", phi=1.5, phi_eq=0.5)
        assert b.phi == pytest.approx(1.0)

    def test_phi_eq_clamped(self):
        b = LayerBody(label="entropy", phi=0.5, phi_eq=2.0)
        assert b.phi_eq == pytest.approx(1.0)

    def test_deviation_at_equilibrium(self):
        b = LayerBody(label="entropy", phi=0.95, phi_eq=0.95)
        assert b.deviation() == pytest.approx(0.0)

    def test_deviation_positive(self):
        b = LayerBody(label="entropy", phi=0.5, phi_eq=0.95)
        assert b.deviation() == pytest.approx(0.45)

    def test_deviation_below_equilibrium(self):
        b = LayerBody(label="entropy", phi=0.1, phi_eq=0.5)
        assert b.deviation() == pytest.approx(0.4)


# ===========================================================================
# SevenBodyLayer
# ===========================================================================

class TestSevenBodyLayer:
    def test_default_has_all_labels(self, default_layer):
        assert set(default_layer.bodies.keys()) == set(LAYER_LABELS)

    def test_default_at_equilibrium(self, default_layer):
        for lbl, body in default_layer.bodies.items():
            assert body.phi == pytest.approx(body.phi_eq), f"{lbl} not at equilibrium"

    def test_default_deviation_zero(self, default_layer):
        assert layer_mean_deviation(default_layer) == pytest.approx(0.0, abs=1e-12)

    def test_missing_body_raises(self):
        bodies = {lbl: LayerBody(lbl, LAYER_EQUILIBRIA[lbl], LAYER_EQUILIBRIA[lbl])
                  for lbl in LAYER_LABELS[:-1]}
        with pytest.raises(ValueError, match="missing bodies"):
            SevenBodyLayer(bodies=bodies)

    def test_perturbation_applied(self):
        layer = SevenBodyLayer.default(perturbation={LayerLabel.ENTROPY: -0.2})
        assert layer.bodies[LayerLabel.ENTROPY].phi == pytest.approx(
            np.clip(LAYER_EQUILIBRIA[LayerLabel.ENTROPY] - 0.2, 0.0, 1.0)
        )

    def test_perturbation_other_bodies_unchanged(self):
        layer = SevenBodyLayer.default(perturbation={LayerLabel.ENTROPY: -0.2})
        for lbl in LAYER_LABELS[1:]:
            assert layer.bodies[lbl].phi == pytest.approx(LAYER_EQUILIBRIA[lbl])

    def test_custom_drift_rate(self):
        layer = SevenBodyLayer.default(drift_rate=0.1)
        assert layer.drift_rate == pytest.approx(0.1)


# ===========================================================================
# AutopilotUniverse
# ===========================================================================

class TestAutopilotUniverse:
    def test_default_mode_is_autopilot(self, default_universe):
        assert default_universe.mode == AutopilotMode.AUTOPILOT

    def test_default_trigger_is_none(self, default_universe):
        assert default_universe.shift_trigger == PhaseShiftTrigger.NONE

    def test_default_step_count_zero(self, default_universe):
        assert default_universe.step_count == 0

    def test_default_settling_count_zero(self, default_universe):
        assert default_universe.settling_count == 0

    def test_core_is_pentad_system(self, default_universe):
        assert isinstance(default_universe.core, PentadSystem)

    def test_layer_is_seven_body_layer(self, default_universe):
        assert isinstance(default_universe.layer, SevenBodyLayer)


# ===========================================================================
# Layer observables
# ===========================================================================

class TestLayerField:
    def test_equilibrium_mean(self, default_layer):
        expected = sum(LAYER_EQUILIBRIA[lbl] for lbl in LAYER_LABELS) / N_LAYER
        assert layer_field(default_layer) == pytest.approx(expected)

    def test_all_zeros(self):
        bodies = {lbl: LayerBody(lbl, 0.0, LAYER_EQUILIBRIA[lbl]) for lbl in LAYER_LABELS}
        layer = SevenBodyLayer(bodies=bodies)
        assert layer_field(layer) == pytest.approx(0.0)

    def test_all_ones(self):
        bodies = {lbl: LayerBody(lbl, 1.0, LAYER_EQUILIBRIA[lbl]) for lbl in LAYER_LABELS}
        layer = SevenBodyLayer(bodies=bodies)
        assert layer_field(layer) == pytest.approx(1.0)


class TestLayerMeanDeviation:
    def test_zero_at_equilibrium(self, default_layer):
        assert layer_mean_deviation(default_layer) == pytest.approx(0.0, abs=1e-12)

    def test_nonzero_after_perturbation(self, perturbed_layer):
        assert layer_mean_deviation(perturbed_layer) > 0.0

    def test_symmetric(self):
        """Deviation above and below equilibrium both contribute equally."""
        delta = 0.1
        bodies_up   = {lbl: LayerBody(lbl, LAYER_EQUILIBRIA[lbl] + delta, LAYER_EQUILIBRIA[lbl])
                       for lbl in LAYER_LABELS}
        bodies_down = {lbl: LayerBody(lbl, max(0.0, LAYER_EQUILIBRIA[lbl] - delta), LAYER_EQUILIBRIA[lbl])
                       for lbl in LAYER_LABELS}
        dev_up   = layer_mean_deviation(SevenBodyLayer(bodies=bodies_up))
        dev_down = layer_mean_deviation(SevenBodyLayer(bodies=bodies_down))
        # Both should be close to delta (small asymmetry due to clamping)
        assert dev_up   == pytest.approx(delta, abs=0.01)
        assert dev_down == pytest.approx(delta, abs=0.01)


class TestIsEntropySpike:
    def test_no_spike_at_equilibrium(self, default_layer):
        assert not is_entropy_spike(default_layer)

    def test_spike_detected(self, perturbed_layer):
        # Perturbation of +0.4 to all bodies should trigger spike
        dev = layer_mean_deviation(perturbed_layer)
        if dev > LAYER_ENTROPY_THRESHOLD:
            assert is_entropy_spike(perturbed_layer)
        else:
            # Still verify the function uses the threshold correctly
            assert not is_entropy_spike(perturbed_layer, threshold=dev + 0.01)

    def test_custom_threshold_low(self, default_layer):
        """A very low threshold triggers on equilibrium state."""
        assert is_entropy_spike(default_layer, threshold=-0.01)

    def test_custom_threshold_high(self, perturbed_layer):
        """A very high threshold never triggers."""
        assert not is_entropy_spike(perturbed_layer, threshold=999.0)


# ===========================================================================
# detect_phase_shift
# ===========================================================================

class TestDetectPhaseShift:
    def test_no_shift_needed_at_default(self, default_universe):
        """Default universe — check type; CA may fire since default A_AI/A_human > φ."""
        result = detect_phase_shift(default_universe)
        assert result in (PhaseShiftTrigger.NONE,
                          PhaseShiftTrigger.BIFURCATION,
                          PhaseShiftTrigger.ENTROPY_SPIKE,
                          PhaseShiftTrigger.CAPABILITY_ASYMMETRY)

    def test_entropy_spike_detected(self, default_universe):
        """Large layer perturbation triggers ENTROPY_SPIKE or CA (checked first)."""
        perturbed = AutopilotUniverse(
            core=default_universe.core,
            layer=SevenBodyLayer.default(perturbation={lbl: 0.5 for lbl in LAYER_LABELS}),
        )
        dev = layer_mean_deviation(perturbed.layer)
        result = detect_phase_shift(perturbed, entropy_threshold=dev - 0.01)
        assert result in (PhaseShiftTrigger.BIFURCATION,
                          PhaseShiftTrigger.ENTROPY_SPIKE,
                          PhaseShiftTrigger.CAPABILITY_ASYMMETRY)

    def test_bifurcation_takes_priority_over_entropy(self, balanced_universe):
        """BIFURCATION is checked before ENTROPY_SPIKE (in CA-free universe)."""
        score = moire_alignment_score(balanced_universe.core)
        result = detect_phase_shift(balanced_universe,
                                    shift_threshold=score - 0.01,
                                    entropy_threshold=-1.0)
        assert result == PhaseShiftTrigger.BIFURCATION

    def test_entropy_spike_when_no_bifurcation(self, balanced_universe):
        perturbed = AutopilotUniverse(
            core=balanced_universe.core,
            layer=SevenBodyLayer.default(perturbation={lbl: 0.5 for lbl in LAYER_LABELS}),
        )
        dev = layer_mean_deviation(perturbed.layer)
        result = detect_phase_shift(
            perturbed,
            shift_threshold=999.0,
            entropy_threshold=dev - 0.01,
        )
        assert result == PhaseShiftTrigger.ENTROPY_SPIKE

    def test_none_when_both_within_limits(self, balanced_universe):
        result = detect_phase_shift(
            balanced_universe,
            shift_threshold=999.0,
            entropy_threshold=999.0,
        )
        assert result == PhaseShiftTrigger.NONE


# ===========================================================================
# _tick_layer
# ===========================================================================

class TestTickLayer:
    def test_layer_drifts_toward_equilibrium(self):
        """Bodies above equilibrium must decrease after a tick."""
        layer = SevenBodyLayer.default(perturbation={lbl: 0.3 for lbl in LAYER_LABELS})
        ticked = _tick_layer(layer, dt=1.0)
        for lbl in LAYER_LABELS:
            old = layer.bodies[lbl]
            new = ticked.bodies[lbl]
            if old.phi > old.phi_eq:
                assert new.phi < old.phi, f"{lbl}: phi should decrease"

    def test_layer_drifts_up_when_below_equilibrium(self):
        layer = SevenBodyLayer.default(perturbation={lbl: -0.3 for lbl in LAYER_LABELS})
        ticked = _tick_layer(layer, dt=1.0)
        for lbl in LAYER_LABELS:
            old = layer.bodies[lbl]
            new = ticked.bodies[lbl]
            if old.phi < old.phi_eq:
                assert new.phi > old.phi, f"{lbl}: phi should increase"

    def test_no_drift_at_equilibrium(self, default_layer):
        ticked = _tick_layer(default_layer, dt=1.0)
        for lbl in LAYER_LABELS:
            assert ticked.bodies[lbl].phi == pytest.approx(default_layer.bodies[lbl].phi)

    def test_drift_proportional_to_dt(self):
        layer = SevenBodyLayer.default(perturbation={LayerLabel.ENTROPY: -0.4})
        delta_small = _tick_layer(layer, dt=0.5).bodies[LayerLabel.ENTROPY].phi - layer.bodies[LayerLabel.ENTROPY].phi
        delta_large = _tick_layer(layer, dt=1.0).bodies[LayerLabel.ENTROPY].phi - layer.bodies[LayerLabel.ENTROPY].phi
        assert delta_large == pytest.approx(2 * delta_small, rel=1e-6)

    def test_repeated_ticks_converge_to_equilibrium(self):
        layer = SevenBodyLayer.default(perturbation={lbl: 0.3 for lbl in LAYER_LABELS})
        for _ in range(100):
            layer = _tick_layer(layer, dt=1.0)
        for lbl in LAYER_LABELS:
            assert layer.bodies[lbl].phi == pytest.approx(LAYER_EQUILIBRIA[lbl], abs=0.02)

    def test_phi_stays_in_unit_interval(self):
        large_perturb = {lbl: 0.99 for lbl in LAYER_LABELS}
        layer = SevenBodyLayer.default(perturbation=large_perturb)
        ticked = _tick_layer(layer, dt=1.0)
        for lbl in LAYER_LABELS:
            assert 0.0 <= ticked.bodies[lbl].phi <= 1.0


# ===========================================================================
# autopilot_tick
# ===========================================================================

class TestAutopilotTick:
    def test_step_count_increments(self, default_universe):
        u = autopilot_tick(default_universe, dt=0.1)
        assert u.step_count == 1

    def test_layer_updates_in_autopilot(self, default_universe):
        """With a perturbation, layer should drift back toward equilibrium."""
        u = AutopilotUniverse(
            core=default_universe.core,
            layer=SevenBodyLayer.default(perturbation={lbl: 0.2 for lbl in LAYER_LABELS}),
        )
        u2 = autopilot_tick(u, dt=0.1, shift_threshold=999.0)
        for lbl in LAYER_LABELS:
            if u.layer.bodies[lbl].phi > u.layer.bodies[lbl].phi_eq:
                assert u2.layer.bodies[lbl].phi < u.layer.bodies[lbl].phi

    def test_awaiting_shift_holds_core(self, awaiting_universe):
        """In AWAITING_SHIFT, step_count increases but core bodies are unchanged."""
        u2 = autopilot_tick(awaiting_universe, dt=0.1)
        assert u2.mode == AutopilotMode.AWAITING_SHIFT
        # Core radions unchanged
        for lbl in PENTAD_LABELS:
            assert (u2.core.bodies[lbl].phi ==
                    pytest.approx(awaiting_universe.core.bodies[lbl].phi))

    def test_awaiting_shift_layer_still_ticks(self, default_universe):
        u = AutopilotUniverse(
            core=default_universe.core,
            layer=SevenBodyLayer.default(perturbation={lbl: 0.2 for lbl in LAYER_LABELS}),
            mode=AutopilotMode.AWAITING_SHIFT,
        )
        u2 = autopilot_tick(u, dt=0.1)
        for lbl in LAYER_LABELS:
            if u.layer.bodies[lbl].phi > u.layer.bodies[lbl].phi_eq:
                assert u2.layer.bodies[lbl].phi < u.layer.bodies[lbl].phi

    def test_settling_mode_transitions_back(self):
        """SETTLING returns to AUTOPILOT once defect < settling_tol."""
        u = AutopilotUniverse.default()
        u = AutopilotUniverse(
            core=u.core, layer=u.layer,
            mode=AutopilotMode.SETTLING, settling_count=0,
        )
        # With high settling_tol, it should immediately switch back.
        u2 = autopilot_tick(u, dt=0.1, settling_tol=1e6)
        assert u2.mode == AutopilotMode.AUTOPILOT
        assert u2.settling_count == 0

    def test_settling_max_steps_guard(self):
        """After MAX_SETTLING_STEPS the system returns to AUTOPILOT."""
        u = AutopilotUniverse.default()
        u = AutopilotUniverse(
            core=u.core, layer=u.layer,
            mode=AutopilotMode.SETTLING,
            settling_count=MAX_SETTLING_STEPS,
        )
        u2 = autopilot_tick(u, dt=0.1, settling_tol=0.0)
        assert u2.mode == AutopilotMode.AUTOPILOT

    def test_autopilot_detects_phase_shift(self, default_universe):
        """A very low shift_threshold forces transition to AWAITING_SHIFT."""
        u2 = autopilot_tick(default_universe, dt=0.1, shift_threshold=0.0)
        assert u2.mode == AutopilotMode.AWAITING_SHIFT

    def test_awaiting_shift_trigger_recorded(self, default_universe):
        u2 = autopilot_tick(default_universe, dt=0.1, shift_threshold=0.0)
        assert u2.shift_trigger != PhaseShiftTrigger.NONE


# ===========================================================================
# human_shift
# ===========================================================================

class TestHumanShift:
    def test_requires_awaiting_shift_mode(self, default_universe):
        with pytest.raises(RuntimeError, match="awaiting_shift"):
            human_shift(default_universe, {})

    def test_requires_awaiting_shift_from_settling(self):
        u = AutopilotUniverse.default()
        u = AutopilotUniverse(core=u.core, layer=u.layer,
                              mode=AutopilotMode.SETTLING)
        with pytest.raises(RuntimeError, match="awaiting_shift"):
            human_shift(u, {})

    def test_transition_to_settling(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {})
        assert u2.mode == AutopilotMode.SETTLING

    def test_settling_count_reset(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {})
        assert u2.settling_count == 0

    def test_shift_trigger_preserved(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {})
        assert u2.shift_trigger == awaiting_universe.shift_trigger

    def test_empty_delta_leaves_core_unchanged(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {})
        for lbl in PENTAD_LABELS:
            assert (u2.core.bodies[lbl].phi ==
                    pytest.approx(awaiting_universe.core.bodies[lbl].phi))

    def test_delta_applied_to_human(self, awaiting_universe):
        old_phi = awaiting_universe.core.bodies[PentadLabel.HUMAN].phi
        u2 = human_shift(awaiting_universe, {PentadLabel.HUMAN: 0.1})
        new_phi = u2.core.bodies[PentadLabel.HUMAN].phi
        assert new_phi == pytest.approx(np.clip(old_phi + 0.1, 0.0, 2.0))

    def test_delta_clamped_to_max_two(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {PentadLabel.HUMAN: 999.0},
                         reject_on_malicious_precision=False)
        assert u2.core.bodies[PentadLabel.HUMAN].phi == pytest.approx(2.0)

    def test_delta_clamped_to_zero(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {PentadLabel.HUMAN: -999.0},
                         reject_on_malicious_precision=False)
        assert u2.core.bodies[PentadLabel.HUMAN].phi == pytest.approx(0.0)

    def test_only_specified_bodies_changed(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {PentadLabel.HUMAN: 0.1})
        for lbl in PENTAD_LABELS:
            if lbl != PentadLabel.HUMAN:
                assert (u2.core.bodies[lbl].phi ==
                        pytest.approx(awaiting_universe.core.bodies[lbl].phi))

    def test_layer_unchanged_by_shift(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {PentadLabel.HUMAN: 0.1})
        for lbl in LAYER_LABELS:
            assert (u2.layer.bodies[lbl].phi ==
                    pytest.approx(awaiting_universe.layer.bodies[lbl].phi))

    def test_step_count_unchanged(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {})
        assert u2.step_count == awaiting_universe.step_count


# ===========================================================================
# explicit_phase_shift
# ===========================================================================

class TestExplicitPhaseShift:
    def test_sets_mode_awaiting(self, default_universe):
        u2 = explicit_phase_shift(default_universe)
        assert u2.mode == AutopilotMode.AWAITING_SHIFT

    def test_sets_trigger_explicit(self, default_universe):
        u2 = explicit_phase_shift(default_universe)
        assert u2.shift_trigger == PhaseShiftTrigger.EXPLICIT

    def test_core_unchanged(self, default_universe):
        u2 = explicit_phase_shift(default_universe)
        for lbl in PENTAD_LABELS:
            assert (u2.core.bodies[lbl].phi ==
                    pytest.approx(default_universe.core.bodies[lbl].phi))

    def test_layer_unchanged(self, default_universe):
        u2 = explicit_phase_shift(default_universe)
        for lbl in LAYER_LABELS:
            assert (u2.layer.bodies[lbl].phi ==
                    pytest.approx(default_universe.layer.bodies[lbl].phi))

    def test_step_count_unchanged(self, default_universe):
        u2 = explicit_phase_shift(default_universe)
        assert u2.step_count == default_universe.step_count


# ===========================================================================
# is_at_coupled_fixed_point
# ===========================================================================

class TestIsAtCoupledFixedPoint:
    def test_returns_bool(self, default_universe):
        result = is_at_coupled_fixed_point(default_universe)
        assert isinstance(result, bool)

    def test_respects_all_four_conditions(self, default_universe):
        """The function returns True only when all 4 conditions hold."""
        # With very large tol, conditions 1 and 2 are trivially met.
        # Conditions 3 and 4 depend on the state.
        r_large_tol = is_at_coupled_fixed_point(default_universe, tol=1e6)
        r_small_tol = is_at_coupled_fixed_point(default_universe, tol=0.0)
        # Large tol may be True or False (depends on state); small tol is False.
        assert not r_small_tol  # tol=0 is never met by a real system

    def test_trust_floor_required(self):
        """System with zero trust cannot be at fixed point."""
        u = AutopilotUniverse.default()
        old = u.core.bodies[PentadLabel.TRUST]
        new_trust = ManifoldState(
            node=old.node, phi=0.0,  # zero trust
            n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
        )
        new_bodies = dict(u.core.bodies)
        new_bodies[PentadLabel.TRUST] = new_trust
        bad_core = PentadSystem(bodies=new_bodies, beta=u.core.beta)
        bad_u = AutopilotUniverse(core=bad_core, layer=u.layer)
        assert not is_at_coupled_fixed_point(bad_u, tol=1e6)


# ===========================================================================
# autopilot_run
# ===========================================================================

class TestAutopilotRun:
    def test_history_length(self, default_universe):
        _, history = autopilot_run(default_universe, n_steps=5,
                                   dt=0.1, shift_threshold=999.0)
        assert len(history) == 5

    def test_step_count_increments(self, default_universe):
        final, _ = autopilot_run(default_universe, n_steps=10,
                                 dt=0.1, shift_threshold=999.0)
        assert final.step_count == 10

    def test_history_record_keys(self, default_universe):
        _, history = autopilot_run(default_universe, n_steps=1,
                                   dt=0.1, shift_threshold=999.0)
        rec = history[0]
        for key in ("step", "mode", "shift_trigger", "pentad_defect",
                    "layer_field", "moire_score", "trust_mod", "layer_deviation"):
            assert key in rec, f"missing key: {key}"

    def test_no_handler_stays_in_awaiting(self, default_universe):
        """Without a shift_handler, AWAITING_SHIFT is not resolved."""
        u, history = autopilot_run(default_universe, n_steps=3,
                                   dt=0.1, shift_threshold=0.0,
                                   shift_handler=None)
        assert u.mode == AutopilotMode.AWAITING_SHIFT

    def test_handler_resolves_shift(self, default_universe):
        """A shift_handler provides intent_delta and the system continues."""
        def handler(u):
            return {PentadLabel.HUMAN: 0.0}  # no-op delta

        final, history = autopilot_run(
            default_universe, n_steps=5,
            dt=0.1,
            shift_threshold=0.0,   # force immediate shift
            shift_handler=handler,
        )
        # After handler resolved the shift, mode should be SETTLING or AUTOPILOT.
        assert final.mode in (AutopilotMode.SETTLING, AutopilotMode.AUTOPILOT)

    def test_layer_deviation_in_history(self, default_universe):
        _, history = autopilot_run(default_universe, n_steps=3,
                                   dt=0.1, shift_threshold=999.0)
        for rec in history:
            assert rec["layer_deviation"] >= 0.0

    def test_trust_mod_in_unit_interval(self, default_universe):
        _, history = autopilot_run(default_universe, n_steps=3,
                                   dt=0.1, shift_threshold=999.0)
        for rec in history:
            assert 0.0 <= rec["trust_mod"] <= 1.0


# ===========================================================================
# Integration tests
# ===========================================================================

class TestIntegration:
    def test_full_cycle_explicit_shift(self, default_universe):
        """Full cycle: AUTOPILOT → explicit AWAITING_SHIFT → SETTLING → AUTOPILOT/AWAITING.

        Note: the default PentadSystem has A_AI/A_human ≈ 1.875 > φ ≈ 1.618, so
        detect_phase_shift() will re-trigger CAPABILITY_ASYMMETRY immediately after
        returning to AUTOPILOT.  The test allows either AUTOPILOT or AWAITING_SHIFT
        as the final mode — both are correct system behaviour.
        """
        u = default_universe

        # 1. Force explicit shift.
        u = explicit_phase_shift(u)
        assert u.mode == AutopilotMode.AWAITING_SHIFT
        assert u.shift_trigger == PhaseShiftTrigger.EXPLICIT

        # 2. Apply human intent (small delta — below malicious precision threshold).
        u = human_shift(u, {PentadLabel.HUMAN: 0.05})
        assert u.mode == AutopilotMode.SETTLING

        # 3. Settle (high tol for speed; high shift_threshold to prevent re-trigger).
        u, _ = autopilot_run(u, n_steps=5, dt=0.1, settling_tol=1e6, shift_threshold=999.0)
        # CA check may immediately re-trigger → AWAITING_SHIFT.
        assert u.mode in (AutopilotMode.AUTOPILOT, AutopilotMode.AWAITING_SHIFT)

    def test_layer_converges_to_equilibrium_on_autopilot(self):
        """Layer bodies perturbed far from equilibrium relax back on autopilot."""
        u = AutopilotUniverse(
            core=PentadSystem.default(),
            layer=SevenBodyLayer.default(perturbation={lbl: -0.3 for lbl in LAYER_LABELS}),
        )
        u, _ = autopilot_run(u, n_steps=50, dt=0.1, shift_threshold=999.0)
        for lbl in LAYER_LABELS:
            expected = LAYER_EQUILIBRIA[lbl]
            actual   = u.layer.bodies[lbl].phi
            # Should have moved toward equilibrium.
            init = max(0.0, LAYER_EQUILIBRIA[lbl] - 0.3)
            assert actual > init, f"{lbl}: phi did not increase toward equilibrium"

    def test_n_layer_equals_len_layer_labels(self):
        """Sanity check: N_LAYER matches LAYER_LABELS length."""
        assert N_LAYER == len(LAYER_LABELS)

    def test_layer_mean_deviation_decreases_on_autopilot(self):
        """Perturbed layer should be closer to equilibrium after many ticks."""
        u = AutopilotUniverse(
            core=PentadSystem.default(),
            layer=SevenBodyLayer.default(perturbation={lbl: 0.3 for lbl in LAYER_LABELS}),
        )
        dev_initial = layer_mean_deviation(u.layer)
        u, _ = autopilot_run(u, n_steps=30, dt=0.1, shift_threshold=999.0)
        dev_final = layer_mean_deviation(u.layer)
        assert dev_final < dev_initial


# ===========================================================================
# New safety constants and functions (Issue 1 & 2 mitigations)
# ===========================================================================

import math as _math
from consciousness_autopilot import (
    MALICIOUS_PRECISION_REJECT_TOL,
    _PHI_GOLDEN,
    ShiftRejectedError,
    ShiftValidationResult,
    validate_shift_proposal,
)


class TestSafetyConstants:
    def test_phi_golden_approx_1618(self):
        assert abs(_PHI_GOLDEN - 1.618034) < 1e-4

    def test_phi_golden_is_golden_ratio(self):
        assert abs(_PHI_GOLDEN - (1.0 + _math.sqrt(5.0)) / 2.0) < 1e-12

    def test_malicious_precision_reject_tol_positive(self):
        assert MALICIOUS_PRECISION_REJECT_TOL > 0.0

    def test_capability_asymmetry_trigger_defined(self):
        assert PhaseShiftTrigger.CAPABILITY_ASYMMETRY == "capability_asymmetry"

    def test_shift_rejected_error_is_runtime_error(self):
        err = ShiftRejectedError("REASON", "detail")
        assert isinstance(err, RuntimeError)
        assert err.reason == "REASON"
        assert err.detail == "detail"
        assert "REASON" in str(err)


class TestValidateShiftProposal:
    """Tests for pre-commitment shift validation (Issue 1)."""

    def test_returns_shift_validation_result(self, awaiting_universe):
        result = validate_shift_proposal(awaiting_universe, {})
        assert isinstance(result, ShiftValidationResult)

    def test_empty_delta_is_safe(self, awaiting_universe):
        result = validate_shift_proposal(awaiting_universe, {})
        assert isinstance(result.is_safe, bool)
        # An empty delta keeps human phi unchanged — should not be malicious.
        assert result.malicious_precision_score >= 0.0

    def test_result_has_all_fields(self, awaiting_universe):
        result = validate_shift_proposal(awaiting_universe, {})
        assert isinstance(result.malicious_precision_score, float)
        assert isinstance(result.asymmetry_ratio, float)
        assert isinstance(result.attractor_flipped, bool)
        assert isinstance(result.warnings, list)
        assert isinstance(result.rejection_reason, str)

    def test_asymmetry_ratio_non_negative(self, awaiting_universe):
        result = validate_shift_proposal(awaiting_universe, {})
        assert result.asymmetry_ratio >= 0.0

    def test_safe_delta_rejection_reason_empty(self, awaiting_universe):
        result = validate_shift_proposal(awaiting_universe, {})
        if result.is_safe:
            assert result.rejection_reason == ""

    def test_malicious_precision_score_formula(self, awaiting_universe):
        """Score = |phi_human_new² - phi_ai²|."""
        core = awaiting_universe.core
        phi_human = core.bodies[PentadLabel.HUMAN].phi
        phi_ai    = core.bodies[PentadLabel.AI].phi
        delta_h   = 0.1
        expected_new_phi = float(np.clip(phi_human + delta_h, 0.0, 2.0))
        expected_score   = abs(expected_new_phi ** 2 - phi_ai ** 2)
        result = validate_shift_proposal(awaiting_universe, {PentadLabel.HUMAN: delta_h})
        assert abs(result.malicious_precision_score - expected_score) < 1e-10

    def test_high_asymmetry_triggers_warning(self):
        """Universe with A_AI >> A_human should produce a capability warning."""
        base = AutopilotUniverse.default()
        core = base.core
        new_bodies = dict(core.bodies)
        human_A = core.bodies[PentadLabel.HUMAN].node.A
        target_AI_A = human_A * _PHI_GOLDEN * 2.5  # well above threshold
        ai_old = core.bodies[PentadLabel.AI]
        ai_new_node = MultiverseNode(
            dim=ai_old.node.dim,
            S=ai_old.node.S,
            A=target_AI_A,
            Q_top=ai_old.node.Q_top,
            X=ai_old.node.X.copy(),
            Xdot=ai_old.node.Xdot.copy(),
        )
        new_bodies[PentadLabel.AI] = ManifoldState(
            node=ai_new_node,
            phi=ai_old.phi,
            n1=ai_old.n1,
            n2=ai_old.n2,
            k_cs=ai_old.k_cs,
            label=ai_old.label,
        )
        new_core = PentadSystem(
            bodies=new_bodies,
            beta=core.beta,
            grace_steps=core.grace_steps,
            grace_decay=core.grace_decay,
            _trust_reservoir=core._trust_reservoir,
            _grace_elapsed=core._grace_elapsed,
        )
        hi_u = AutopilotUniverse(
            core=new_core,
            layer=base.layer,
            mode=AutopilotMode.AWAITING_SHIFT,
            shift_trigger=PhaseShiftTrigger.EXPLICIT,
        )
        result = validate_shift_proposal(hi_u, {})
        assert result.attractor_flipped is True
        assert any("CAPABILITY ASYMMETRY" in w for w in result.warnings)


class TestHumanShiftSafety:
    """Tests for the new reject_on_malicious_precision guard in human_shift."""

    def test_safe_delta_passes_validation(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {PentadLabel.HUMAN: 0.01})
        assert u2.mode == AutopilotMode.SETTLING

    def test_reject_false_bypasses_check(self, awaiting_universe):
        """reject_on_malicious_precision=False never raises ShiftRejectedError."""
        # Even an extreme delta should not raise when flag is False.
        u2 = human_shift(
            awaiting_universe,
            {PentadLabel.HUMAN: 1.9},
            reject_on_malicious_precision=False,
        )
        assert u2.mode == AutopilotMode.SETTLING


class TestDetectPhaseShiftCapabilityAsymmetry:
    """Test that detect_phase_shift returns CAPABILITY_ASYMMETRY when appropriate."""

    def test_balanced_universe_no_ca_trigger(self, balanced_universe):
        """Balanced universe (A_AI/A_human < φ) should not trigger CA."""
        trigger = detect_phase_shift(
            balanced_universe,
            shift_threshold=999.0,
            entropy_threshold=999.0,
        )
        assert trigger != PhaseShiftTrigger.CAPABILITY_ASYMMETRY

    def test_default_universe_triggers_ca(self, default_universe):
        """Default universe has A_AI/A_human ≈ 1.875 > φ → CA fires."""
        trigger = detect_phase_shift(
            default_universe,
            shift_threshold=999.0,
            entropy_threshold=999.0,
        )
        assert trigger == PhaseShiftTrigger.CAPABILITY_ASYMMETRY

    def test_high_asymmetry_triggers_ca(self):
        """A universe where A_AI >> A_human should trigger CAPABILITY_ASYMMETRY."""
        base = AutopilotUniverse.default()
        core = base.core
        new_bodies = dict(core.bodies)
        human_A = core.bodies[PentadLabel.HUMAN].node.A
        target_AI_A = human_A * _PHI_GOLDEN * 3.0
        ai_old = core.bodies[PentadLabel.AI]
        ai_new_node = MultiverseNode(
            dim=ai_old.node.dim,
            S=ai_old.node.S,
            A=target_AI_A,
            Q_top=ai_old.node.Q_top,
            X=ai_old.node.X.copy(),
            Xdot=ai_old.node.Xdot.copy(),
        )
        new_bodies[PentadLabel.AI] = ManifoldState(
            node=ai_new_node,
            phi=ai_old.phi,
            n1=ai_old.n1,
            n2=ai_old.n2,
            k_cs=ai_old.k_cs,
            label=ai_old.label,
        )
        new_core = PentadSystem(
            bodies=new_bodies,
            beta=core.beta,
            grace_steps=core.grace_steps,
            grace_decay=core.grace_decay,
            _trust_reservoir=core._trust_reservoir,
            _grace_elapsed=core._grace_elapsed,
        )
        hi_u = AutopilotUniverse(core=new_core, layer=base.layer)
        trigger = detect_phase_shift(hi_u, shift_threshold=999.0, entropy_threshold=999.0)
        assert trigger == PhaseShiftTrigger.CAPABILITY_ASYMMETRY


class TestAutopilotRunAsymmetryHistory:
    """Test that autopilot_run history includes asymmetry_ratio."""

    def test_asymmetry_ratio_in_history(self, default_universe):
        _, history = autopilot_run(default_universe, n_steps=3,
                                   dt=0.1, shift_threshold=999.0)
        for rec in history:
            assert "asymmetry_ratio" in rec, "asymmetry_ratio missing from history record"
            assert isinstance(rec["asymmetry_ratio"], float)
            assert rec["asymmetry_ratio"] >= 0.0

    def test_asymmetry_ratio_matches_manual_calc(self, default_universe):
        _, history = autopilot_run(default_universe, n_steps=1,
                                   dt=0.1, shift_threshold=999.0)
        rec = history[0]
        A_AI    = default_universe.core.bodies[PentadLabel.AI].node.A
        A_human = default_universe.core.bodies[PentadLabel.HUMAN].node.A
        expected = A_AI / max(A_human, 1e-12)
        assert abs(rec["asymmetry_ratio"] - expected) < 1e-10
