# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/test_strategic_core.py
===================================
Unit tests for the Strategic Core.

Covers:
  - Constants: C_S, ESCALATION_THRESHOLD, CRITICAL_OBJECTIVE_FLOOR,
               MAX_AUTONOMOUS_STEPS, TRUST_PHI_MIN
  - MissionObjective: construction, potential, is_critical
  - StrategicCore: factory, coherence, allocation, escalation, tick,
                   acknowledge_escalation, doctrine_summary
  - Edge cases: empty objectives, zero weights, full trust loss
"""

import math
import sys
import os

import pytest
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_PENTAD = os.path.dirname(_HERE)
_ROOT = os.path.dirname(_PENTAD)
for _p in [_HERE, _PENTAD, _ROOT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from five_cores.strategic_core import (
    C_S,
    ESCALATION_THRESHOLD,
    CRITICAL_OBJECTIVE_FLOOR,
    MAX_AUTONOMOUS_STEPS,
    TRUST_PHI_MIN,
    DEFAULT_TEMPERATURE,
    MAX_SINGLE_WEIGHT,
    MissionObjective,
    EscalationEvent,
    StrategicState,
    StrategicCore,
)

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
}


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_c_s_is_12_over_37(self):
        assert math.isclose(C_S, 12 / 37, rel_tol=1e-12)

    def test_c_s_approx(self):
        assert 0.32 < C_S < 0.33

    def test_escalation_threshold_below_half(self):
        assert 0 < ESCALATION_THRESHOLD < 0.5

    def test_critical_floor_equals_c_s(self):
        assert math.isclose(CRITICAL_OBJECTIVE_FLOOR, C_S, rel_tol=1e-12)

    def test_max_autonomous_steps(self):
        assert MAX_AUTONOMOUS_STEPS == 74  # k_cs resonance

    def test_trust_phi_min_equals_c_s(self):
        assert math.isclose(TRUST_PHI_MIN, C_S, rel_tol=1e-12)

    def test_default_temperature_positive(self):
        assert DEFAULT_TEMPERATURE > 0

    def test_max_single_weight_less_than_one(self):
        assert 0 < MAX_SINGLE_WEIGHT < 1.0


# ===========================================================================
# MissionObjective
# ===========================================================================

class TestMissionObjective:
    def test_construction_defaults(self):
        o = MissionObjective("GOAL_A")
        assert o.label == "GOAL_A"
        assert 0.0 <= o.phi <= 1.0
        assert o.weight >= 0.0

    def test_phi_clamp_above(self):
        o = MissionObjective("X", phi=2.0)
        assert o.phi == 1.0

    def test_phi_clamp_below(self):
        o = MissionObjective("X", phi=-1.0)
        assert o.phi == 0.0

    def test_potential_at_perfect(self):
        o = MissionObjective("X", phi=1.0, weight=1.0)
        assert math.isclose(o.potential, 0.0, abs_tol=1e-12)

    def test_potential_at_zero(self):
        o = MissionObjective("X", phi=0.0, weight=1.0)
        assert math.isclose(o.potential, 1.0, abs_tol=1e-12)

    def test_potential_midpoint(self):
        o = MissionObjective("X", phi=0.5, weight=1.0)
        assert math.isclose(o.potential, 0.25, abs_tol=1e-12)

    def test_is_critical_below_floor(self):
        o = MissionObjective("X", phi=0.1, critical_floor=C_S)
        assert o.is_critical

    def test_not_critical_above_floor(self):
        o = MissionObjective("X", phi=0.9, critical_floor=C_S)
        assert not o.is_critical

    def test_weight_normalisation_via_core(self):
        # Weights sum to 1 after adding to core
        sc = StrategicCore(objectives=[
            MissionObjective("A", weight=2.0),
            MissionObjective("B", weight=3.0),
        ])
        total = sum(o.weight for o in sc._objectives.values())
        assert math.isclose(total, 1.0, abs_tol=1e-12)


# ===========================================================================
# StrategicCore — factories
# ===========================================================================

class TestStrategicCoreFactory:
    def test_default_creates_three_objectives(self):
        sc = StrategicCore.default()
        assert len(sc._objectives) == 3

    def test_mission_profile_factory(self):
        sc = StrategicCore.mission_profile(
            ["NAV", "PROP", "LIFE"],
            [1.0, 2.0, 3.0],
        )
        assert set(sc._objectives.keys()) == {"NAV", "PROP", "LIFE"}
        total = sum(o.weight for o in sc._objectives.values())
        assert math.isclose(total, 1.0, abs_tol=1e-12)

    def test_add_objective(self):
        sc = StrategicCore.default()
        n_before = len(sc._objectives)
        sc.add_objective(MissionObjective("NEW_GOAL", weight=1.0))
        assert len(sc._objectives) == n_before + 1


# ===========================================================================
# Strategic Coherence
# ===========================================================================

class TestStrategicCoherence:
    def test_perfect_coherence_when_all_phi_one(self):
        sc = StrategicCore(objectives=[
            MissionObjective("A", phi=1.0, weight=1.0),
            MissionObjective("B", phi=1.0, weight=1.0),
        ])
        assert math.isclose(sc.strategic_coherence(), 1.0, abs_tol=1e-10)

    def test_zero_coherence_when_all_phi_zero(self):
        sc = StrategicCore(objectives=[
            MissionObjective("A", phi=0.0, weight=1.0),
        ])
        # coherence = 1 - 1*(1-0)^2 = 0
        assert math.isclose(sc.strategic_coherence(), 0.0, abs_tol=1e-10)

    def test_coherence_in_unit_interval(self):
        sc = StrategicCore.default()
        c = sc.strategic_coherence()
        assert 0.0 <= c <= 1.0

    def test_coherence_increases_after_positive_intent(self):
        sc = StrategicCore(objectives=[MissionObjective("A", phi=0.5, weight=1.0)])
        c_before = sc.strategic_coherence()
        sc.tick(intent_delta={"A": 0.3})
        c_after = sc.strategic_coherence()
        assert c_after >= c_before


# ===========================================================================
# Resource Allocation
# ===========================================================================

class TestResourceAllocation:
    def test_allocation_sums_to_one(self):
        sc = StrategicCore.default()
        alloc = sc.resource_allocation()
        assert math.isclose(sum(alloc.values()), 1.0, abs_tol=1e-10)

    def test_all_allocations_in_unit_interval(self):
        sc = StrategicCore.default()
        for v in sc.resource_allocation().values():
            assert 0.0 <= v <= 1.0

    def test_most_lagging_gets_most_resources(self):
        sc = StrategicCore(objectives=[
            MissionObjective("GOOD", phi=0.95, weight=0.5),
            MissionObjective("BAD", phi=0.05, weight=0.5),
        ])
        alloc = sc.resource_allocation(temperature=0.1)
        assert alloc["BAD"] > alloc["GOOD"]

    def test_allocation_with_empty_objectives(self):
        sc = StrategicCore(objectives=[])
        assert sc.resource_allocation() == {}


# ===========================================================================
# Escalation
# ===========================================================================

class TestEscalation:
    def test_no_escalation_at_high_coherence(self):
        sc = StrategicCore(objectives=[
            MissionObjective("A", phi=0.9, weight=1.0),
        ])
        assert not sc.escalation_required()

    def test_escalation_when_coherence_low(self):
        sc = StrategicCore(objectives=[
            MissionObjective("A", phi=0.0, weight=1.0),
        ])
        assert sc.escalation_required()

    def test_escalation_when_trust_below_floor(self):
        sc = StrategicCore(phi_trust=0.1)
        assert sc.escalation_required()

    def test_escalation_timer(self):
        sc = StrategicCore(objectives=[
            MissionObjective("A", phi=0.9, weight=1.0),
        ])
        # Run until max autonomous steps
        for _ in range(MAX_AUTONOMOUS_STEPS):
            sc.tick()
        assert sc.escalation_required()

    def test_acknowledge_resets_timer(self):
        sc = StrategicCore(objectives=[MissionObjective("A", phi=0.9, weight=1.0)])
        for _ in range(MAX_AUTONOMOUS_STEPS):
            sc.tick()
        sc.acknowledge_escalation()
        assert sc._steps_since_hil == 0
        assert not sc._escalation_pending


# ===========================================================================
# Tick and State
# ===========================================================================

class TestTick:
    def test_tick_returns_state(self):
        sc = StrategicCore.default()
        state = sc.tick()
        assert isinstance(state, StrategicState)

    def test_step_count_increments(self):
        sc = StrategicCore.default()
        sc.tick()
        sc.tick()
        assert sc._step_count == 2

    def test_intent_delta_applied(self):
        sc = StrategicCore(objectives=[MissionObjective("A", phi=0.5, weight=1.0)])
        sc.tick(intent_delta={"A": 0.2})
        # phi should be > 0.5 (plus natural drift)
        assert sc._objectives["A"].phi > 0.5

    def test_trust_update(self):
        sc = StrategicCore(phi_trust=0.5)
        sc.tick(trust_delta=0.1)
        assert math.isclose(sc._phi_trust, 0.6, abs_tol=1e-10)

    def test_trust_clamp_upper(self):
        sc = StrategicCore(phi_trust=0.95)
        sc.tick(trust_delta=0.5)
        assert sc._phi_trust <= 1.0

    def test_trust_clamp_lower(self):
        sc = StrategicCore(phi_trust=0.1)
        sc.tick(trust_delta=-1.0)
        assert sc._phi_trust >= 0.0

    def test_state_coherence_matches_core(self):
        sc = StrategicCore.default()
        state = sc.tick()
        assert math.isclose(state.coherence, sc.strategic_coherence(), abs_tol=1e-10)


# ===========================================================================
# Doctrine Summary
# ===========================================================================

class TestDoctrineSummary:
    def test_summary_is_string(self):
        sc = StrategicCore.default()
        s = sc.doctrine_summary()
        assert isinstance(s, str)
        assert len(s) > 0

    def test_summary_contains_coherence(self):
        sc = StrategicCore.default()
        s = sc.doctrine_summary()
        assert "Coherence" in s or "coherence" in s.lower()

    def test_summary_contains_escalation_when_pending(self):
        sc = StrategicCore(objectives=[MissionObjective("A", phi=0.0, weight=1.0)])
        sc.tick()
        s = sc.doctrine_summary()
        assert "ESCALATION" in s


# ===========================================================================
# Critical Objectives
# ===========================================================================

class TestCriticalObjectives:
    def test_no_critical_at_high_phi(self):
        sc = StrategicCore(objectives=[MissionObjective("A", phi=0.9, weight=1.0)])
        assert sc.critical_objectives() == []

    def test_critical_detected(self):
        sc = StrategicCore(objectives=[MissionObjective("A", phi=0.1, weight=1.0)])
        assert "A" in sc.critical_objectives()
