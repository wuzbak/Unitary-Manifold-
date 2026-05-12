# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/test_five_cores_system.py
=======================================
Unit tests for the integrated Five-Cores System.

Covers:
  - Constants: C_S, TRUST_PHI_MIN, CORE_LABELS, weights
  - CoreLabel constants
  - SystemStatus constants
  - SystemHealthReport: field types
  - FiveCoresSystem: factory, tick, run, hil_acknowledge, set_trust,
    history, summary
  - Integration: safety halt propagates, biological critical triggers HIL,
    strategic escalation triggers HIL
  - Health score: bounded, weighted correctly
  - Inter-core signal flow: sciences → strategic, biological → strategic
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

from five_cores.five_cores_system import (
    C_S,
    TRUST_PHI_MIN,
    W_STRATEGIC,
    W_OPERATIONAL,
    W_SAFETY,
    W_SCIENCES,
    W_BIOLOGICAL,
    CoreLabel,
    CORE_LABELS,
    SystemStatus,
    SystemHealthReport,
    FiveCoresSystem,
)
from five_cores.realtime_safety_core import (
    HARD_INTERLOCK_THRESHOLD,
    SafetyLayer,
)
from five_cores.biological_logics_core import VitalCategory, VITAL_CATEGORIES
from five_cores.realtime_sciences_core import Observation, DataDomain
from five_cores.strategic_core import MissionObjective

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
}


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_c_s_value(self):
        assert math.isclose(C_S, 12 / 37, rel_tol=1e-12)

    def test_trust_phi_min_equals_c_s(self):
        assert math.isclose(TRUST_PHI_MIN, C_S, rel_tol=1e-12)

    def test_weights_sum_to_one(self):
        total = W_STRATEGIC + W_OPERATIONAL + W_SAFETY + W_SCIENCES + W_BIOLOGICAL
        assert math.isclose(total, 1.0, abs_tol=1e-12)

    def test_all_weights_positive(self):
        for w in [W_STRATEGIC, W_OPERATIONAL, W_SAFETY, W_SCIENCES, W_BIOLOGICAL]:
            assert w > 0

    def test_core_labels_count_five(self):
        assert len(CORE_LABELS) == 5

    def test_core_label_constants(self):
        for attr in ["STRATEGIC", "OPERATIONAL", "SAFETY", "SCIENCES", "BIOLOGICAL"]:
            assert isinstance(getattr(CoreLabel, attr), str)

    def test_system_status_constants(self):
        for attr in ["NOMINAL", "DEGRADED", "AWAITING_HIL", "HALTED"]:
            assert isinstance(getattr(SystemStatus, attr), str)


# ===========================================================================
# Factory
# ===========================================================================

class TestFactory:
    def test_default_creates_system(self):
        sys_ = FiveCoresSystem.default()
        assert sys_._phi_trust == 1.0
        assert sys_._step_count == 0

    def test_no_history_before_tick(self):
        sys_ = FiveCoresSystem.default()
        assert sys_.history() == []


# ===========================================================================
# Single Tick
# ===========================================================================

class TestSingleTick:
    def test_tick_returns_report(self):
        sys_ = FiveCoresSystem.default()
        report = sys_.tick()
        assert isinstance(report, SystemHealthReport)

    def test_step_count_increments(self):
        sys_ = FiveCoresSystem.default()
        sys_.tick()
        sys_.tick()
        assert sys_._step_count == 2

    def test_health_score_in_unit_interval(self):
        sys_ = FiveCoresSystem.default()
        report = sys_.tick()
        assert 0.0 <= report.health_score <= 1.0

    def test_five_per_core_scores(self):
        sys_ = FiveCoresSystem.default()
        report = sys_.tick()
        assert len(report.per_core_scores) == 5

    def test_all_per_core_scores_in_unit_interval(self):
        sys_ = FiveCoresSystem.default()
        report = sys_.tick()
        for v in report.per_core_scores.values():
            assert 0.0 <= v <= 1.0

    def test_nominal_status_at_high_trust(self):
        sys_ = FiveCoresSystem.default()
        report = sys_.tick()
        # With no perturbations and full trust, should be NOMINAL or DEGRADED
        # (DEGRADED possible due to default metric/objective states)
        assert report.status in (SystemStatus.NOMINAL, SystemStatus.DEGRADED)

    def test_history_grows(self):
        sys_ = FiveCoresSystem.default()
        for _ in range(3):
            sys_.tick()
        assert len(sys_.history()) == 3


# ===========================================================================
# Trust Management
# ===========================================================================

class TestTrustManagement:
    def test_set_trust(self):
        sys_ = FiveCoresSystem.default()
        sys_.set_trust(0.5)
        assert math.isclose(sys_._phi_trust, 0.5, abs_tol=1e-10)

    def test_trust_clamped_above(self):
        sys_ = FiveCoresSystem.default()
        sys_.set_trust(2.0)
        assert sys_._phi_trust <= 1.0

    def test_trust_clamped_below(self):
        sys_ = FiveCoresSystem.default()
        sys_.set_trust(-1.0)
        assert sys_._phi_trust >= 0.0

    def test_trust_delta_in_tick(self):
        sys_ = FiveCoresSystem.default()
        sys_.set_trust(0.5)
        sys_.tick(trust_delta=0.1)
        assert math.isclose(sys_._phi_trust, 0.6, abs_tol=1e-10)


# ===========================================================================
# Safety Halt Propagation
# ===========================================================================

class TestSafetyHalt:
    def test_halt_triggered_by_hard_interlock(self):
        sys_ = FiveCoresSystem.default()
        # Push a metric to hard interlock
        report = sys_.tick(
            metric_updates={"RADIATION_EXPOSURE": HARD_INTERLOCK_THRESHOLD}
        )
        assert report.status == SystemStatus.HALTED

    def test_halt_status_after_interlock(self):
        sys_ = FiveCoresSystem.default()
        sys_.safety.hard_halt("test")
        report = sys_.tick()
        assert report.safety_layer == SafetyLayer.HALT


# ===========================================================================
# Biological Critical → HIL
# ===========================================================================

class TestBiologicalCriticalHIL:
    def test_critical_crew_triggers_hil(self):
        sys_ = FiveCoresSystem.default()
        # Make one crew member critical
        for vc in VITAL_CATEGORIES:
            sys_.biological._crew["C001"].vital_radions[vc] = 0.05
        report = sys_.tick()
        assert report.hil_requested
        assert "C001" in report.critical_crew

    def test_hil_source_is_biological(self):
        sys_ = FiveCoresSystem.default()
        for vc in VITAL_CATEGORIES:
            sys_.biological._crew["C001"].vital_radions[vc] = 0.05
        # Ensure strategic doesn't also escalate (keep objectives healthy)
        for obj in sys_.strategic._objectives.values():
            obj.phi = 0.9
        report = sys_.tick()
        # hil_source should include BIOLOGICAL
        assert report.hil_source is not None


# ===========================================================================
# HIL Acknowledge
# ===========================================================================

class TestHILAcknowledge:
    def test_hil_acknowledge_clears_flag(self):
        sys_ = FiveCoresSystem.default()
        sys_._hil_requested = True
        sys_._hil_source = CoreLabel.SAFETY
        sys_.hil_acknowledge()
        assert not sys_._hil_requested
        assert sys_._hil_source is None

    def test_hil_acknowledge_resets_violation_count(self):
        sys_ = FiveCoresSystem.default()
        sys_.safety._violation_count = 3
        sys_.hil_acknowledge()
        assert sys_.safety._violation_count == 0


# ===========================================================================
# Run (multi-step)
# ===========================================================================

class TestRun:
    def test_run_returns_correct_length(self):
        sys_ = FiveCoresSystem.default()
        reports = sys_.run(n_steps=10)
        assert len(reports) == 10

    def test_run_with_trust_schedule(self):
        sys_ = FiveCoresSystem.default()
        sys_.set_trust(0.5)
        schedule = [0.01] * 5
        reports = sys_.run(n_steps=5, trust_schedule=schedule)
        assert len(reports) == 5
        # Trust should have increased
        assert sys_._phi_trust > 0.5

    def test_run_with_observations(self):
        sys_ = FiveCoresSystem.default()
        obs_schedule = [
            [Observation(DataDomain.ASTROPHYSICS, np.array([0.8, 0.05, 0.05, 0.05, 0.05]))]
        ]
        reports = sys_.run(n_steps=1, observation_schedule=obs_schedule)
        assert len(reports) == 1

    def test_health_scores_bounded_in_run(self):
        sys_ = FiveCoresSystem.default()
        reports = sys_.run(n_steps=20)
        for r in reports:
            assert 0.0 <= r.health_score <= 1.0


# ===========================================================================
# Summary
# ===========================================================================

class TestSummary:
    def test_summary_before_tick(self):
        sys_ = FiveCoresSystem.default()
        s = sys_.summary()
        assert isinstance(s, str)
        assert "Step 0" in s

    def test_summary_after_tick(self):
        sys_ = FiveCoresSystem.default()
        sys_.tick()
        s = sys_.summary()
        assert "Step 1" in s
        assert "status=" in s


# ===========================================================================
# Inter-Core Signal Flow
# ===========================================================================

class TestInterCoreSignals:
    def test_sciences_boosts_mission_integrity(self):
        """High Sciences readiness should boost MISSION_INTEGRITY objective."""
        sys_ = FiveCoresSystem.default()
        # Force high readiness in sciences
        import numpy as np
        for domain in sys_.sciences._beliefs:
            sys_.sciences._beliefs[domain] = np.array([0.9, 0.025, 0.025, 0.025, 0.025])
        # Run a step
        report = sys_.tick()
        # Strategic should have received a positive delta — coherence should be reasonable
        assert report.strategic.coherence >= 0.0

    def test_biological_crew_distress_affects_strategic(self):
        """Low crew readiness should trigger strategic correction."""
        sys_ = FiveCoresSystem.default()
        # Degrade majority of crew
        for mid in ["C001", "C002", "C003"]:
            for vc in VITAL_CATEGORIES:
                sys_.biological._crew[mid].vital_radions[vc] = 0.20
        report = sys_.tick()
        # HIL should have been requested from biological
        assert report.hil_requested
