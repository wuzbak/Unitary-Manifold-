# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_prebigbang.py
========================
Tests for Pillar 111 — Pre-Big Bang Geometry (src/core/prebigbang.py).
"""

import math
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.prebigbang import (
    pre_braid_metric_signature,
    cs_locking_temperature,
    braid_phase_transition_width,
    pre_bigbang_efolds,
    winding_lock_condition,
    prebigbang_summary,
    K_CS,
    WINDING_NUMBER,
    BRAIDED_SOUND_SPEED,
)


# ---------------------------------------------------------------------------
# pre_braid_metric_signature
# ---------------------------------------------------------------------------

class TestPreBraidMetricSignature:
    def test_returns_tuple(self):
        assert isinstance(pre_braid_metric_signature(), tuple)

    def test_length_5(self):
        assert len(pre_braid_metric_signature()) == 5

    def test_first_element_positive(self):
        sig = pre_braid_metric_signature()
        assert sig[0] == 1

    def test_spatial_elements_negative(self):
        sig = pre_braid_metric_signature()
        for i in range(1, 4):
            assert sig[i] == -1

    def test_fifth_element_positive(self):
        sig = pre_braid_metric_signature()
        assert sig[4] == 1

    def test_exact_signature(self):
        assert pre_braid_metric_signature() == (1, -1, -1, -1, 1)

    def test_sum_of_signature(self):
        sig = pre_braid_metric_signature()
        assert sum(sig) == -1

    def test_positive_count(self):
        sig = pre_braid_metric_signature()
        assert sig.count(1) == 2

    def test_negative_count(self):
        sig = pre_braid_metric_signature()
        assert sig.count(-1) == 3

    def test_reproducible(self):
        assert pre_braid_metric_signature() == pre_braid_metric_signature()


# ---------------------------------------------------------------------------
# cs_locking_temperature
# ---------------------------------------------------------------------------

class TestCsLockingTemperature:
    def test_returns_float(self):
        assert isinstance(cs_locking_temperature(), float)

    def test_positive(self):
        assert cs_locking_temperature() > 0

    def test_default_value_approx(self):
        expected = 74 / (25 * 2 * math.pi)
        assert abs(cs_locking_temperature() - expected) < 1e-12

    def test_default_value_range(self):
        T = cs_locking_temperature()
        assert 0.4 < T < 0.55

    def test_scales_with_kcs(self):
        T1 = cs_locking_temperature(k_cs=37, n_w=5)
        T2 = cs_locking_temperature(k_cs=74, n_w=5)
        assert abs(T2 / T1 - 2.0) < 1e-12

    def test_scales_with_nw(self):
        T1 = cs_locking_temperature(k_cs=74, n_w=5)
        T2 = cs_locking_temperature(k_cs=74, n_w=10)
        assert abs(T1 / T2 - 4.0) < 1e-12

    def test_decreases_with_nw(self):
        assert cs_locking_temperature(n_w=10) < cs_locking_temperature(n_w=5)

    def test_increases_with_kcs(self):
        assert cs_locking_temperature(k_cs=100) > cs_locking_temperature(k_cs=74)

    def test_formula_exact(self):
        k, n = 74, 5
        assert abs(cs_locking_temperature(k, n) - k / (n ** 2 * 2 * math.pi)) < 1e-15

    def test_nw1(self):
        T = cs_locking_temperature(k_cs=74, n_w=1)
        assert abs(T - 74 / (2 * math.pi)) < 1e-12


# ---------------------------------------------------------------------------
# braid_phase_transition_width
# ---------------------------------------------------------------------------

class TestBraidPhaseTransitionWidth:
    def test_returns_float(self):
        assert isinstance(braid_phase_transition_width(), float)

    def test_positive(self):
        assert braid_phase_transition_width() > 0

    def test_less_than_one(self):
        assert braid_phase_transition_width() < 1

    def test_default_approx(self):
        expected = 1.0 / math.sqrt(74)
        assert abs(braid_phase_transition_width() - expected) < 1e-12

    def test_default_range(self):
        w = braid_phase_transition_width()
        assert 0.10 < w < 0.13

    def test_scales_correctly(self):
        w1 = braid_phase_transition_width(k_cs=1)
        assert abs(w1 - 1.0) < 1e-12

    def test_decreases_with_kcs(self):
        assert braid_phase_transition_width(k_cs=200) < braid_phase_transition_width(k_cs=74)

    def test_formula(self):
        for k in [10, 74, 100, 200]:
            assert abs(braid_phase_transition_width(k) - 1 / math.sqrt(k)) < 1e-12


# ---------------------------------------------------------------------------
# pre_bigbang_efolds
# ---------------------------------------------------------------------------

class TestPreBigbangEfolds:
    def test_returns_float(self):
        assert isinstance(pre_bigbang_efolds(), float)

    def test_positive(self):
        assert pre_bigbang_efolds() > 0

    def test_default_approx(self):
        expected = 74 / (2 * math.pi)
        assert abs(pre_bigbang_efolds(phi0=1.0) - expected) < 1e-12

    def test_default_range(self):
        N = pre_bigbang_efolds()
        assert 10 < N < 14

    def test_scales_with_phi0_squared(self):
        N1 = pre_bigbang_efolds(phi0=1.0)
        N2 = pre_bigbang_efolds(phi0=2.0)
        assert abs(N2 / N1 - 4.0) < 1e-12

    def test_zero_phi0(self):
        assert pre_bigbang_efolds(phi0=0.0) == 0.0

    def test_formula(self):
        for phi in [0.5, 1.0, 1.5, 2.0]:
            expected = phi ** 2 * 74 / (2 * math.pi)
            assert abs(pre_bigbang_efolds(phi) - expected) < 1e-12

    def test_phi0_half(self):
        N = pre_bigbang_efolds(phi0=0.5)
        assert N > 0


# ---------------------------------------------------------------------------
# winding_lock_condition
# ---------------------------------------------------------------------------

class TestWindingLockCondition:
    def test_returns_bool(self):
        assert isinstance(winding_lock_condition(), bool)

    def test_default_true(self):
        assert winding_lock_condition() is True

    def test_nw5_kcs74_true(self):
        assert winding_lock_condition(n_w=5, k_cs=74) is True

    def test_nw5_kcs73_false(self):
        assert winding_lock_condition(n_w=5, k_cs=73) is False

    def test_nw5_kcs75_false(self):
        assert winding_lock_condition(n_w=5, k_cs=75) is False

    def test_nw7_kcs74_false(self):
        assert winding_lock_condition(n_w=7, k_cs=74) is False

    def test_nw3_resonance(self):
        # 3² + 5² = 9 + 25 = 34
        assert winding_lock_condition(n_w=3, k_cs=34) is True

    def test_nw1_resonance(self):
        # 1² + 3² = 1 + 9 = 10
        assert winding_lock_condition(n_w=1, k_cs=10) is True

    def test_arithmetic_check(self):
        # verify 5² + 7² = 74
        assert 5 ** 2 + 7 ** 2 == 74


# ---------------------------------------------------------------------------
# prebigbang_summary
# ---------------------------------------------------------------------------

class TestPrebigbangSummary:
    def setup_method(self):
        self.s = prebigbang_summary()

    def test_returns_dict(self):
        assert isinstance(self.s, dict)

    def test_key_metric_signature(self):
        assert "metric_signature" in self.s

    def test_key_locking_temperature(self):
        assert "locking_temperature" in self.s

    def test_key_transition_width(self):
        assert "transition_width" in self.s

    def test_key_pre_efolds(self):
        assert "pre_efolds" in self.s

    def test_key_braid_locked(self):
        assert "braid_locked" in self.s

    def test_metric_signature_correct(self):
        assert self.s["metric_signature"] == (1, -1, -1, -1, 1)

    def test_locking_temperature_positive(self):
        assert self.s["locking_temperature"] > 0

    def test_transition_width_in_01(self):
        w = self.s["transition_width"]
        assert 0 < w < 1

    def test_pre_efolds_positive(self):
        assert self.s["pre_efolds"] > 0

    def test_braid_locked_true(self):
        assert self.s["braid_locked"] is True

    def test_exactly_5_keys(self):
        assert len(self.s) == 5

    def test_module_constants(self):
        assert K_CS == 74
        assert WINDING_NUMBER == 5
        assert abs(BRAIDED_SOUND_SPEED - 12 / 37) < 1e-12
