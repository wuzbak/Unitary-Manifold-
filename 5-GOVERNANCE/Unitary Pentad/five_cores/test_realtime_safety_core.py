# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/test_realtime_safety_core.py
=========================================
Unit tests for the Real-Time Safety Core.

Covers:
  - Constants and trust thresholds
  - SafetyLayer severity ordering and comparison
  - SafetyMetric: construction, advisory/warning thresholds, is_critical
  - RealTimeSafetyCore: factory, register_metric, update_metric,
    hard_halt, release_halt, is_operation_permitted, tick
  - Alert generation and recent_alerts
  - Life-support domain always permitted
  - Edge cases: max violations, trust floor enforcement
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

from five_cores.realtime_safety_core import (
    C_S,
    TRUST_NOMINAL,
    TRUST_ADVISORY,
    TRUST_CAUTION,
    TRUST_WARNING,
    METRIC_ADVISORY_FRACTION,
    HARD_INTERLOCK_THRESHOLD,
    MAX_VIOLATIONS_BEFORE_HALT,
    LIFE_SUPPORT_DOMAINS,
    SafetyLayer,
    SafetyMetric,
    SafetyAlert,
    SafetyState,
    RealTimeSafetyCore,
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
    def test_c_s_value(self):
        assert math.isclose(C_S, 12 / 37, rel_tol=1e-12)

    def test_trust_caution_equals_c_s(self):
        assert math.isclose(TRUST_CAUTION, C_S, rel_tol=1e-12)

    def test_trust_ordering(self):
        assert TRUST_WARNING < TRUST_CAUTION < TRUST_ADVISORY < TRUST_NOMINAL

    def test_hard_interlock_near_one(self):
        assert 0.9 <= HARD_INTERLOCK_THRESHOLD <= 1.0

    def test_max_violations_positive(self):
        assert MAX_VIOLATIONS_BEFORE_HALT > 0

    def test_life_support_domains_not_empty(self):
        assert len(LIFE_SUPPORT_DOMAINS) > 0


# ===========================================================================
# SafetyLayer
# ===========================================================================

class TestSafetyLayer:
    def test_severity_ordering(self):
        layers = ["NOMINAL", "ADVISORY", "CAUTION", "WARNING", "HOLD", "HALT"]
        sevs = [SafetyLayer.severity(l) for l in layers]
        assert sevs == sorted(sevs)

    def test_more_severe_returns_worse(self):
        assert SafetyLayer.more_severe("HALT", "NOMINAL") == "HALT"
        assert SafetyLayer.more_severe("NOMINAL", "HALT") == "HALT"

    def test_same_severity(self):
        assert SafetyLayer.more_severe("WARNING", "WARNING") == "WARNING"

    def test_unknown_severity_minus_one(self):
        assert SafetyLayer.severity("UNKNOWN") == -1


# ===========================================================================
# SafetyMetric
# ===========================================================================

class TestSafetyMetric:
    def test_construction_defaults(self):
        m = SafetyMetric("RADIATION")
        assert m.value == 0.0
        assert m.threshold > 0

    def test_value_clamp(self):
        m = SafetyMetric("X", value=2.0)
        assert m.value == 1.0

    def test_layer_nominal_at_low_value(self):
        m = SafetyMetric("X", value=0.0, threshold=0.7)
        assert m.layer == SafetyLayer.NOMINAL

    def test_layer_advisory_near_threshold(self):
        m = SafetyMetric("X", value=0.55, threshold=0.70)  # 0.55 > 0.70*0.75=0.525
        assert m.layer == SafetyLayer.ADVISORY

    def test_layer_warning_at_threshold(self):
        m = SafetyMetric("X", value=0.70, threshold=0.70)
        assert m.layer == SafetyLayer.WARNING

    def test_layer_halt_at_hard_interlock(self):
        m = SafetyMetric("X", value=HARD_INTERLOCK_THRESHOLD)
        assert m.layer == SafetyLayer.HALT

    def test_advisory_threshold_calculation(self):
        m = SafetyMetric("X", threshold=0.80)
        assert math.isclose(m.advisory_threshold, 0.80 * METRIC_ADVISORY_FRACTION, rel_tol=1e-9)


# ===========================================================================
# RealTimeSafetyCore — factory
# ===========================================================================

class TestSafetyCoreFactory:
    def test_default_creates_core(self):
        sc = RealTimeSafetyCore.default()
        assert sc._phi_trust == 1.0

    def test_default_has_metrics(self):
        sc = RealTimeSafetyCore.default()
        assert len(sc._metrics) > 0


# ===========================================================================
# Register / Update metrics
# ===========================================================================

class TestMetricManagement:
    def test_register_new_metric(self):
        sc = RealTimeSafetyCore.default()
        n_before = len(sc._metrics)
        sc.register_metric(SafetyMetric("NEW_METRIC", value=0.1))
        assert len(sc._metrics) == n_before + 1

    def test_update_metric_changes_value(self):
        sc = RealTimeSafetyCore.default()
        sc.register_metric(SafetyMetric("TEST", value=0.1))
        sc.update_metric("TEST", 0.8)
        assert math.isclose(sc._metrics["TEST"].value, 0.8, abs_tol=1e-10)

    def test_update_metric_clamps_above(self):
        sc = RealTimeSafetyCore.default()
        sc.update_metric("RADIATION_EXPOSURE", 2.0)
        assert sc._metrics["RADIATION_EXPOSURE"].value <= 1.0

    def test_update_nonexistent_creates_metric(self):
        sc = RealTimeSafetyCore.default()
        sc.update_metric("BRAND_NEW", 0.5)
        assert "BRAND_NEW" in sc._metrics


# ===========================================================================
# Hard Halt / Release
# ===========================================================================

class TestHaltLogic:
    def test_hard_halt_sets_flag(self):
        sc = RealTimeSafetyCore.default()
        sc.hard_halt("test")
        assert sc._halt_active

    def test_release_halt_succeeds_with_good_trust(self):
        sc = RealTimeSafetyCore.default()
        sc.hard_halt()
        released = sc.release_halt(phi_trust_required=0.0)
        assert released
        assert not sc._halt_active

    def test_release_halt_fails_with_low_trust(self):
        sc = RealTimeSafetyCore(phi_trust=0.1)
        sc.hard_halt()
        released = sc.release_halt(phi_trust_required=0.5)
        assert not released
        assert sc._halt_active


# ===========================================================================
# Operation Permitted
# ===========================================================================

class TestOperationPermitted:
    def test_life_support_always_permitted(self):
        sc = RealTimeSafetyCore.default()
        sc.hard_halt()
        for domain in LIFE_SUPPORT_DOMAINS:
            assert sc.is_operation_permitted(domain)

    def test_non_essential_blocked_when_halted(self):
        sc = RealTimeSafetyCore.default()
        sc.hard_halt()
        assert not sc.is_operation_permitted("NAVIGATION")

    def test_operation_permitted_at_nominal(self):
        sc = RealTimeSafetyCore.default()
        assert sc.is_operation_permitted("NAVIGATION")


# ===========================================================================
# Tick and Alerts
# ===========================================================================

class TestTick:
    def test_tick_returns_state(self):
        sc = RealTimeSafetyCore.default()
        state = sc.tick()
        assert isinstance(state, SafetyState)

    def test_step_count_increments(self):
        sc = RealTimeSafetyCore.default()
        sc.tick()
        sc.tick()
        assert sc._step_count == 2

    def test_metric_update_in_tick(self):
        sc = RealTimeSafetyCore.default()
        state = sc.tick(metric_updates={"RADIATION_EXPOSURE": 0.8})
        # Should generate advisory or warning alert
        assert any(a.metric_label == "RADIATION_EXPOSURE" for a in state.alerts)

    def test_violation_count_increments(self):
        sc = RealTimeSafetyCore.default()
        # Push a metric over threshold
        sc.tick(metric_updates={"RADIATION_EXPOSURE": 0.9})
        assert sc._violation_count >= 1

    def test_hard_interlock_triggers_halt(self):
        sc = RealTimeSafetyCore.default()
        sc.tick(metric_updates={"RADIATION_EXPOSURE": HARD_INTERLOCK_THRESHOLD})
        assert sc._halt_active

    def test_max_violations_triggers_halt_layer(self):
        sc = RealTimeSafetyCore.default()
        sc._violation_count = MAX_VIOLATIONS_BEFORE_HALT
        state = sc.tick()
        assert state.layer == SafetyLayer.HALT

    def test_recent_alerts(self):
        sc = RealTimeSafetyCore.default()
        sc.tick(metric_updates={"RADIATION_EXPOSURE": 0.8})
        alerts = sc.recent_alerts(5)
        assert isinstance(alerts, list)

    def test_trust_updates(self):
        sc = RealTimeSafetyCore(phi_trust=0.5)
        sc.tick(trust_delta=0.1)
        assert math.isclose(sc._phi_trust, 0.6, abs_tol=1e-10)

    def test_reset_violation_count(self):
        sc = RealTimeSafetyCore.default()
        sc._violation_count = 10
        sc.reset_violation_count()
        assert sc._violation_count == 0
