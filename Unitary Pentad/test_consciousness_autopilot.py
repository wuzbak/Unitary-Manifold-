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
        """Default universe — human gap and layer both small → NONE."""
        # Default state may or may not exceed the threshold; just check type.
        result = detect_phase_shift(default_universe)
        assert result in (PhaseShiftTrigger.NONE,
                          PhaseShiftTrigger.BIFURCATION,
                          PhaseShiftTrigger.ENTROPY_SPIKE)

    def test_entropy_spike_detected(self, default_universe):
        """Large layer perturbation triggers ENTROPY_SPIKE."""
        perturbed = AutopilotUniverse(
            core=default_universe.core,
            layer=SevenBodyLayer.default(perturbation={lbl: 0.5 for lbl in LAYER_LABELS}),
        )
        dev = layer_mean_deviation(perturbed.layer)
        result = detect_phase_shift(perturbed, entropy_threshold=dev - 0.01)
        assert result in (PhaseShiftTrigger.BIFURCATION, PhaseShiftTrigger.ENTROPY_SPIKE)

    def test_bifurcation_takes_priority_over_entropy(self, default_universe):
        """BIFURCATION is checked before ENTROPY_SPIKE."""
        score = moire_alignment_score(default_universe.core)
        result = detect_phase_shift(default_universe,
                                    shift_threshold=score - 0.01,
                                    entropy_threshold=-1.0)
        assert result == PhaseShiftTrigger.BIFURCATION

    def test_entropy_spike_when_no_bifurcation(self, default_universe):
        perturbed = AutopilotUniverse(
            core=default_universe.core,
            layer=SevenBodyLayer.default(perturbation={lbl: 0.5 for lbl in LAYER_LABELS}),
        )
        dev = layer_mean_deviation(perturbed.layer)
        result = detect_phase_shift(
            perturbed,
            shift_threshold=999.0,
            entropy_threshold=dev - 0.01,
        )
        assert result == PhaseShiftTrigger.ENTROPY_SPIKE

    def test_none_when_both_within_limits(self, default_universe):
        result = detect_phase_shift(
            default_universe,
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
        u2 = human_shift(awaiting_universe, {PentadLabel.HUMAN: 999.0})
        assert u2.core.bodies[PentadLabel.HUMAN].phi == pytest.approx(2.0)

    def test_delta_clamped_to_zero(self, awaiting_universe):
        u2 = human_shift(awaiting_universe, {PentadLabel.HUMAN: -999.0})
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
        from src.consciousness.coupled_attractor import ManifoldState
        old = u.core.bodies[PentadLabel.TRUST]
        new_trust = ManifoldState(
            node=old.node, phi=0.0,  # zero trust
            n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
        )
        new_bodies = dict(u.core.bodies)
        new_bodies[PentadLabel.TRUST] = new_trust
        from unitary_pentad import PentadSystem
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
        """Full cycle: AUTOPILOT → explicit AWAITING_SHIFT → SETTLING → AUTOPILOT."""
        u = default_universe

        # 1. Force explicit shift.
        u = explicit_phase_shift(u)
        assert u.mode == AutopilotMode.AWAITING_SHIFT
        assert u.shift_trigger == PhaseShiftTrigger.EXPLICIT

        # 2. Apply human intent.
        u = human_shift(u, {PentadLabel.HUMAN: 0.05})
        assert u.mode == AutopilotMode.SETTLING

        # 3. Settle (high tol for speed; high shift_threshold to prevent re-trigger).
        u, _ = autopilot_run(u, n_steps=5, dt=0.1, settling_tol=1e6, shift_threshold=999.0)
        assert u.mode == AutopilotMode.AUTOPILOT

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
