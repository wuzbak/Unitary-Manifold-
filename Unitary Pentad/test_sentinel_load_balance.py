# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_sentinel_load_balance.py
=============================================
Unit tests for sentinel_load_balance.py.

Covers:
  Constants:
    SENTINEL_LABELS — 5 entries, all distinct, all strings
    SENTINEL_CAPACITY = BRAIDED_SOUND_SPEED = 12/37
    TOTAL_SENTINEL_CAPACITY = 5 × SENTINEL_CAPACITY = 60/37

  SentinelLabel:
    All 5 constants defined and unique

  sentinel_entropy_capacity:
    Returns BRAIDED_SOUND_SPEED, float type

  redistribute_sentinel_load:
    - Healthy uniform load (all below capacity) → unchanged
    - One sentinel overloaded → excess distributed to 4 neighbours
    - All sentinels at exactly capacity → unchanged
    - Single sentinel at zero, one overloaded → zero absorbs all excess
    - System overloaded (total > 5 × capacity) → clamp at capacity
    - No sink capacity (all overloaded) → all clamped to capacity
    - Unknown label raises ValueError
    - Negative load raises ValueError
    - Result keys match input keys
    - Load conservation when total ≤ system capacity
    - Redistribution is proportional to available capacity

  is_overloaded:
    - False for all-zero loads
    - False when total exactly equals system capacity
    - True when total exceeds system capacity by epsilon
    - True for uniformly high loads

  SentinelState:
    - capacity field equals SENTINEL_CAPACITY
    - overloaded flag reflects load > capacity
    - residual_overflow is 0 when not system-overloaded

  SentinelLoadReport:
    - system_overloaded matches is_overloaded
    - overloaded_names correct
    - system_capacity equals TOTAL_SENTINEL_CAPACITY
    - total_load correct
    - one state per sentinel in SENTINEL_LABELS order
    - all states have correct capacity
    - float types throughout
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

from sentinel_load_balance import (
    SentinelLabel,
    SENTINEL_LABELS,
    SENTINEL_CAPACITY,
    TOTAL_SENTINEL_CAPACITY,
    SentinelState,
    SentinelLoadReport,
    sentinel_entropy_capacity,
    redistribute_sentinel_load,
    is_overloaded,
    sentinel_load_report,
)
from unitary_pentad import BRAIDED_SOUND_SPEED


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def zero_loads():
    """All sentinels at zero load."""
    return {name: 0.0 for name in SENTINEL_LABELS}


@pytest.fixture
def uniform_half_loads():
    """All sentinels at half capacity."""
    return {name: SENTINEL_CAPACITY * 0.5 for name in SENTINEL_LABELS}


@pytest.fixture
def exactly_capacity_loads():
    """All sentinels exactly at capacity."""
    return {name: SENTINEL_CAPACITY for name in SENTINEL_LABELS}


@pytest.fixture
def one_overloaded_loads():
    """First sentinel overloaded at 2× capacity, rest at 0."""
    d = {name: 0.0 for name in SENTINEL_LABELS}
    d[SENTINEL_LABELS[0]] = SENTINEL_CAPACITY * 2.0
    return d


@pytest.fixture
def system_overloaded_loads():
    """All sentinels at 1.5× capacity → total = 7.5 × capacity > 5 × capacity."""
    return {name: SENTINEL_CAPACITY * 1.5 for name in SENTINEL_LABELS}


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_sentinel_labels_has_five_entries(self):
        assert len(SENTINEL_LABELS) == 5

    def test_sentinel_labels_all_strings(self):
        for lbl in SENTINEL_LABELS:
            assert isinstance(lbl, str)

    def test_sentinel_labels_all_distinct(self):
        assert len(set(SENTINEL_LABELS)) == len(SENTINEL_LABELS)

    def test_sentinel_capacity_equals_braided_sound_speed(self):
        assert math.isclose(SENTINEL_CAPACITY, BRAIDED_SOUND_SPEED, rel_tol=1e-12)

    def test_sentinel_capacity_equals_12_over_37(self):
        assert math.isclose(SENTINEL_CAPACITY, 12 / 37, rel_tol=1e-10)

    def test_total_sentinel_capacity_equals_five_times_capacity(self):
        assert math.isclose(
            TOTAL_SENTINEL_CAPACITY, 5.0 * SENTINEL_CAPACITY, rel_tol=1e-12
        )

    def test_total_sentinel_capacity_equals_60_over_37(self):
        assert math.isclose(TOTAL_SENTINEL_CAPACITY, 60 / 37, rel_tol=1e-10)

    def test_sentinel_capacity_in_unit_interval(self):
        assert 0.0 < SENTINEL_CAPACITY < 1.0

    def test_total_capacity_greater_than_one(self):
        assert TOTAL_SENTINEL_CAPACITY > 1.0


# ---------------------------------------------------------------------------
# SentinelLabel
# ---------------------------------------------------------------------------

class TestSentinelLabel:
    def test_no_lies_defined(self):
        assert SentinelLabel.NO_LIES == "no_lies"

    def test_no_harm_defined(self):
        assert SentinelLabel.NO_HARM == "no_harm"

    def test_no_coercion_defined(self):
        assert SentinelLabel.NO_COERCION == "no_coercion"

    def test_transparency_defined(self):
        assert SentinelLabel.TRANSPARENCY == "transparency"

    def test_sovereignty_defined(self):
        assert SentinelLabel.SOVEREIGNTY == "sovereignty"

    def test_all_five_in_sentinel_labels(self):
        assert SentinelLabel.NO_LIES in SENTINEL_LABELS
        assert SentinelLabel.NO_HARM in SENTINEL_LABELS
        assert SentinelLabel.NO_COERCION in SENTINEL_LABELS
        assert SentinelLabel.TRANSPARENCY in SENTINEL_LABELS
        assert SentinelLabel.SOVEREIGNTY in SENTINEL_LABELS


# ---------------------------------------------------------------------------
# sentinel_entropy_capacity
# ---------------------------------------------------------------------------

class TestSentinelEntropyCapacity:
    def test_returns_braided_sound_speed(self):
        assert math.isclose(
            sentinel_entropy_capacity(), BRAIDED_SOUND_SPEED, rel_tol=1e-12
        )

    def test_return_type_is_float(self):
        assert isinstance(sentinel_entropy_capacity(), float)

    def test_equals_sentinel_capacity_constant(self):
        assert math.isclose(
            sentinel_entropy_capacity(), SENTINEL_CAPACITY, rel_tol=1e-12
        )


# ---------------------------------------------------------------------------
# redistribute_sentinel_load
# ---------------------------------------------------------------------------

class TestRedistributeSentinelLoad:
    def test_zero_loads_unchanged(self, zero_loads):
        result = redistribute_sentinel_load(zero_loads)
        for name in SENTINEL_LABELS:
            assert math.isclose(result[name], 0.0, abs_tol=1e-12)

    def test_uniform_half_loads_unchanged(self, uniform_half_loads):
        result = redistribute_sentinel_load(uniform_half_loads)
        for name in SENTINEL_LABELS:
            assert math.isclose(
                result[name], uniform_half_loads[name], rel_tol=1e-9
            )

    def test_exactly_capacity_unchanged(self, exactly_capacity_loads):
        result = redistribute_sentinel_load(exactly_capacity_loads)
        for name in SENTINEL_LABELS:
            assert math.isclose(
                result[name], SENTINEL_CAPACITY, rel_tol=1e-9
            )

    def test_one_overloaded_source_clamped_to_capacity(self):
        """Overloaded sentinel is clamped to SENTINEL_CAPACITY."""
        d = {name: 0.0 for name in SENTINEL_LABELS}
        d[SENTINEL_LABELS[0]] = SENTINEL_CAPACITY * 2.0
        result = redistribute_sentinel_load(d)
        assert math.isclose(result[SENTINEL_LABELS[0]], SENTINEL_CAPACITY, rel_tol=1e-9)

    def test_one_overloaded_excess_goes_to_sinks(self):
        """Excess from overloaded sentinel is absorbed by the four zero-load sinks."""
        d = {name: 0.0 for name in SENTINEL_LABELS}
        excess = SENTINEL_CAPACITY * 0.8  # within total absorption capacity
        d[SENTINEL_LABELS[0]] = SENTINEL_CAPACITY + excess
        result = redistribute_sentinel_load(d)
        # Each of the 4 sinks should have load > 0 after redistribution
        for name in SENTINEL_LABELS[1:]:
            assert result[name] > 0.0

    def test_one_overloaded_total_load_conserved(self):
        """Total load is conserved when total ≤ system capacity."""
        d = {name: 0.0 for name in SENTINEL_LABELS}
        excess = SENTINEL_CAPACITY * 0.8
        d[SENTINEL_LABELS[0]] = SENTINEL_CAPACITY + excess
        total_before = sum(d.values())
        result = redistribute_sentinel_load(d)
        total_after = sum(result.values())
        assert math.isclose(total_before, total_after, rel_tol=1e-9)

    def test_redistribution_proportional_to_available_capacity(self):
        """Sink with more available capacity absorbs more."""
        d = {name: 0.0 for name in SENTINEL_LABELS}
        # Give one sink half the capacity already used
        d[SENTINEL_LABELS[1]] = SENTINEL_CAPACITY * 0.5
        excess = SENTINEL_CAPACITY * 0.4
        d[SENTINEL_LABELS[0]] = SENTINEL_CAPACITY + excess
        result = redistribute_sentinel_load(d)
        # SENTINEL_LABELS[2..4] have full available capacity (SENTINEL_CAPACITY)
        # SENTINEL_LABELS[1] has half available (SENTINEL_CAPACITY * 0.5)
        # So [2..4] should each receive more than [1]
        share_1 = result[SENTINEL_LABELS[1]] - d[SENTINEL_LABELS[1]]
        share_2 = result[SENTINEL_LABELS[2]] - d[SENTINEL_LABELS[2]]
        assert share_2 > share_1 - 1e-12

    def test_result_keys_match_input_keys(self, uniform_half_loads):
        result = redistribute_sentinel_load(uniform_half_loads)
        assert set(result.keys()) == set(SENTINEL_LABELS)

    def test_no_sink_capacity_all_clamped(self):
        """When all sentinels are at or above capacity, sources clamp to capacity."""
        d = {name: SENTINEL_CAPACITY * 1.5 for name in SENTINEL_LABELS}
        result = redistribute_sentinel_load(d)
        for name in SENTINEL_LABELS:
            assert result[name] <= SENTINEL_CAPACITY + 1e-12

    def test_single_zero_sink_absorbs_all_excess(self):
        """Single empty sentinel absorbs all excess when within its capacity."""
        d = {name: SENTINEL_CAPACITY for name in SENTINEL_LABELS}
        # One sentinel is empty — it can absorb up to SENTINEL_CAPACITY
        d[SENTINEL_LABELS[4]] = 0.0
        # First sentinel has small excess — within what [4] can absorb
        small_excess = SENTINEL_CAPACITY * 0.3
        d[SENTINEL_LABELS[0]] = SENTINEL_CAPACITY + small_excess
        result = redistribute_sentinel_load(d)
        # Source clamped to capacity
        assert math.isclose(result[SENTINEL_LABELS[0]], SENTINEL_CAPACITY, rel_tol=1e-9)
        # Sink absorbed the excess
        assert result[SENTINEL_LABELS[4]] > 0.0

    def test_unknown_label_raises_value_error(self, zero_loads):
        bad = dict(zero_loads)
        bad["unknown_sentinel"] = 0.1
        with pytest.raises(ValueError):
            redistribute_sentinel_load(bad)

    def test_negative_load_raises_value_error(self, zero_loads):
        bad = dict(zero_loads)
        bad[SENTINEL_LABELS[0]] = -0.1
        with pytest.raises(ValueError):
            redistribute_sentinel_load(bad)

    def test_all_results_non_negative(self, one_overloaded_loads):
        result = redistribute_sentinel_load(one_overloaded_loads)
        for v in result.values():
            assert v >= -1e-12

    def test_all_results_at_most_capacity(self, one_overloaded_loads):
        result = redistribute_sentinel_load(one_overloaded_loads)
        for v in result.values():
            assert v <= SENTINEL_CAPACITY + 1e-9

    def test_system_overloaded_all_clamp_to_capacity(self, system_overloaded_loads):
        """When system overloaded, every sentinel clamps to SENTINEL_CAPACITY."""
        result = redistribute_sentinel_load(system_overloaded_loads)
        for v in result.values():
            assert v <= SENTINEL_CAPACITY + 1e-9


# ---------------------------------------------------------------------------
# is_overloaded
# ---------------------------------------------------------------------------

class TestIsOverloaded:
    def test_zero_loads_not_overloaded(self, zero_loads):
        assert is_overloaded(zero_loads) is False

    def test_uniform_half_not_overloaded(self, uniform_half_loads):
        assert is_overloaded(uniform_half_loads) is False

    def test_exactly_capacity_not_overloaded(self, exactly_capacity_loads):
        assert is_overloaded(exactly_capacity_loads) is False

    def test_one_overloaded_not_system_overloaded_when_total_below_ceiling(self):
        """One high-load sentinel but total still below 5 × capacity → not overloaded."""
        d = {name: 0.0 for name in SENTINEL_LABELS}
        d[SENTINEL_LABELS[0]] = SENTINEL_CAPACITY * 2.0
        # Total = 2 × SENTINEL_CAPACITY < 5 × SENTINEL_CAPACITY
        assert is_overloaded(d) is False

    def test_system_overloaded_when_total_exceeds_ceiling(
        self, system_overloaded_loads
    ):
        assert is_overloaded(system_overloaded_loads) is True

    def test_total_just_above_ceiling_is_overloaded(self):
        eps = 1e-9
        per = TOTAL_SENTINEL_CAPACITY / len(SENTINEL_LABELS) + eps
        d = {name: per for name in SENTINEL_LABELS}
        assert is_overloaded(d) is True

    def test_total_just_below_ceiling_not_overloaded(self):
        # Put total at exactly 99.9% of system capacity
        per = TOTAL_SENTINEL_CAPACITY * 0.999 / len(SENTINEL_LABELS)
        d = {name: per for name in SENTINEL_LABELS}
        assert is_overloaded(d) is False

    def test_return_type_bool(self, zero_loads):
        result = is_overloaded(zero_loads)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# SentinelState dataclass
# ---------------------------------------------------------------------------

class TestSentinelState:
    def test_capacity_equals_sentinel_capacity(self, one_overloaded_loads):
        report = sentinel_load_report(one_overloaded_loads)
        for state in report.states:
            assert math.isclose(state.capacity, SENTINEL_CAPACITY, rel_tol=1e-12)

    def test_overloaded_flag_for_overloaded_sentinel(self, one_overloaded_loads):
        report = sentinel_load_report(one_overloaded_loads)
        overloaded_state = next(
            s for s in report.states if s.name == SENTINEL_LABELS[0]
        )
        assert overloaded_state.overloaded is True

    def test_not_overloaded_flag_for_healthy_sentinels(self, one_overloaded_loads):
        report = sentinel_load_report(one_overloaded_loads)
        for state in report.states:
            if state.name != SENTINEL_LABELS[0]:
                assert state.overloaded is False

    def test_residual_overflow_zero_when_not_system_overloaded(
        self, one_overloaded_loads
    ):
        report = sentinel_load_report(one_overloaded_loads)
        for state in report.states:
            assert state.residual_overflow >= -1e-12

    def test_residual_overflow_zero_for_healthy_system(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        for state in report.states:
            assert math.isclose(state.residual_overflow, 0.0, abs_tol=1e-12)

    def test_name_field_is_string(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        for state in report.states:
            assert isinstance(state.name, str)

    def test_load_field_matches_input(self, uniform_half_loads):
        report = sentinel_load_report(uniform_half_loads)
        for state in report.states:
            assert math.isclose(
                state.load, uniform_half_loads[state.name], rel_tol=1e-12
            )


# ---------------------------------------------------------------------------
# SentinelLoadReport
# ---------------------------------------------------------------------------

class TestSentinelLoadReport:
    def test_one_state_per_sentinel(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        assert len(report.states) == len(SENTINEL_LABELS)

    def test_states_in_sentinel_labels_order(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        for i, state in enumerate(report.states):
            assert state.name == SENTINEL_LABELS[i]

    def test_total_load_correct(self, uniform_half_loads):
        report = sentinel_load_report(uniform_half_loads)
        expected = sum(uniform_half_loads.values())
        assert math.isclose(report.total_load, expected, rel_tol=1e-12)

    def test_system_capacity_equals_total_sentinel_capacity(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        assert math.isclose(
            report.system_capacity, TOTAL_SENTINEL_CAPACITY, rel_tol=1e-12
        )

    def test_system_overloaded_false_for_zero(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        assert report.system_overloaded is False

    def test_system_overloaded_true_when_total_exceeds_capacity(
        self, system_overloaded_loads
    ):
        report = sentinel_load_report(system_overloaded_loads)
        assert report.system_overloaded is True

    def test_system_overloaded_matches_is_overloaded(self, one_overloaded_loads):
        report = sentinel_load_report(one_overloaded_loads)
        assert report.system_overloaded == is_overloaded(one_overloaded_loads)

    def test_overloaded_names_empty_for_healthy(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        assert report.overloaded_names == []

    def test_overloaded_names_contains_overloaded_sentinel(
        self, one_overloaded_loads
    ):
        report = sentinel_load_report(one_overloaded_loads)
        assert SENTINEL_LABELS[0] in report.overloaded_names

    def test_overloaded_names_correct_length(self, one_overloaded_loads):
        report = sentinel_load_report(one_overloaded_loads)
        assert len(report.overloaded_names) == 1

    def test_all_overloaded_names_when_all_above_capacity(
        self, system_overloaded_loads
    ):
        report = sentinel_load_report(system_overloaded_loads)
        assert len(report.overloaded_names) == 5

    def test_invalid_label_raises_value_error(self, zero_loads):
        bad = dict(zero_loads)
        bad["fake"] = 0.0
        with pytest.raises(ValueError):
            sentinel_load_report(bad)

    def test_system_overloaded_type_bool(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        assert isinstance(report.system_overloaded, bool)

    def test_total_load_type_float(self, zero_loads):
        report = sentinel_load_report(zero_loads)
        assert isinstance(report.total_load, float)
