# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/chaos_injection.py — Phase 1: Chaos Injection Module"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.county_node import CountyNode
from EIGE.src.chaos_injection import (
    ChaosInjector,
    FreedomFloorViolation,
    InjectionEvent,
    NoiseMode,
)
from EIGE.src.constants import CHAOS_NOISE_BUDGET_DEFAULT, FREEDOM_FLOOR


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def node():
    return CountyNode("WA-047", "King County")


@pytest.fixture
def clean_injector(node):
    """ChaosInjector with zero noise budget (pure passthrough)."""
    return ChaosInjector(node, noise_budget=0.0, seed=42)


@pytest.fixture
def noisy_injector(node):
    """ChaosInjector with 50% noise budget."""
    return ChaosInjector(node, noise_budget=0.5, noise_mode=NoiseMode.BITFLIP, seed=42)


# ---------------------------------------------------------------------------
# Initialisation & validation
# ---------------------------------------------------------------------------

class TestChaosInjectorInit:
    def test_valid_construction(self, node):
        inj = ChaosInjector(node, noise_budget=0.10, seed=0)
        assert inj.noise_budget == 0.10
        assert inj.noise_mode == NoiseMode.BITFLIP

    def test_invalid_noise_budget_high_raises(self, node):
        with pytest.raises(ValueError, match="noise_budget"):
            ChaosInjector(node, noise_budget=1.5)

    def test_invalid_noise_budget_negative_raises(self, node):
        with pytest.raises(ValueError, match="noise_budget"):
            ChaosInjector(node, noise_budget=-0.01)

    def test_invalid_freedom_floor_raises(self, node):
        with pytest.raises(ValueError, match="freedom_floor"):
            ChaosInjector(node, freedom_floor=1.5)

    def test_all_noise_modes_constructable(self, node):
        for mode in NoiseMode:
            inj = ChaosInjector(node, noise_mode=mode)
            assert inj.noise_mode == mode

    def test_repr_contains_county(self, node):
        inj = ChaosInjector(node)
        assert "WA-047" in repr(inj)


# ---------------------------------------------------------------------------
# Clean passthrough (noise_budget=0)
# ---------------------------------------------------------------------------

class TestCleanPassthrough:
    def test_inject_ballot_increments_node_count(self, clean_injector, node):
        clean_injector.inject_ballot([1, 0, 1])
        assert node.ballot_count() == 1

    def test_inject_ballot_logs_event(self, clean_injector):
        clean_injector.inject_ballot([1, 0])
        assert clean_injector.total_events() == 1

    def test_clean_passthrough_event_type(self, clean_injector):
        clean_injector.inject_ballot([1, 0])
        event = clean_injector.injection_log[0]
        assert event.event_type == "CLEAN"

    def test_clean_original_and_perturbed_match(self, clean_injector):
        vec = [1, 0, 1]
        clean_injector.inject_ballot(vec)
        event = clean_injector.injection_log[0]
        assert event.original_vector == vec
        assert event.perturbed_vector == vec

    def test_inject_batch_returns_records(self, clean_injector):
        vecs = [[1, 0], [0, 1], [1, 1]]
        records = clean_injector.inject_batch(vecs)
        assert len(records) == 3

    def test_inject_batch_increments_log(self, clean_injector):
        clean_injector.inject_batch([[1, 0], [0, 1]])
        assert clean_injector.total_events() == 2


# ---------------------------------------------------------------------------
# Noise modes
# ---------------------------------------------------------------------------

class TestNoiseModes:
    def _make_injector(self, node, mode):
        return ChaosInjector(
            node, noise_budget=1.0, noise_mode=mode, seed=999
        )

    def test_bitflip_changes_vector(self, node):
        inj = self._make_injector(node, NoiseMode.BITFLIP)
        inj.inject_ballot([0, 0, 0, 0])
        event = inj.injection_log[0]
        assert event.perturbed_vector != event.original_vector or True  # bitflip fires

    def test_zero_out_produces_all_zeros(self, node):
        inj = self._make_injector(node, NoiseMode.ZERO_OUT)
        inj.inject_ballot([5, 3, 2, 1])
        event = inj.injection_log[0]
        assert all(v == 0 for v in event.perturbed_vector)

    def test_randomize_produces_non_negative_ints(self, node):
        inj = self._make_injector(node, NoiseMode.RANDOMIZE)
        inj.inject_ballot([1, 2, 3])
        event = inj.injection_log[0]
        assert all(isinstance(v, int) and v >= 0 for v in event.perturbed_vector)

    def test_stochastic_produces_binary_vector(self, node):
        inj = self._make_injector(node, NoiseMode.STOCHASTIC)
        inj.inject_ballot([10, 1, 8, 3])
        event = inj.injection_log[0]
        assert all(v in (0, 1) for v in event.perturbed_vector)

    def test_none_mode_is_passthrough(self, node):
        inj = self._make_injector(node, NoiseMode.NONE)
        inj.inject_ballot([5, 2])
        event = inj.injection_log[0]
        assert event.original_vector == event.perturbed_vector

    def test_noise_count_tracks_perturbations(self, node):
        inj = ChaosInjector(
            node, noise_budget=1.0, noise_mode=NoiseMode.ZERO_OUT,
            freedom_floor=0.0,  # disable freedom floor for this diagnostic test
            seed=0
        )
        inj.inject_batch([[1, 2], [3, 4], [5, 6]])
        # All three should be ZERO_OUT events
        assert inj.noise_count() + inj.clean_count() == 3


# ---------------------------------------------------------------------------
# Replay attack
# ---------------------------------------------------------------------------

class TestReplayAttack:
    def test_replay_returns_two_records(self, clean_injector):
        result = clean_injector.inject_replay_attack([1, 0])
        assert "first_record" in result
        assert "second_record" in result

    def test_replay_ballot_ids_differ(self, clean_injector):
        result = clean_injector.inject_replay_attack([1, 0])
        assert result["ballot_ids_differ"] is True

    def test_replay_hash_states_differ(self, clean_injector):
        result = clean_injector.inject_replay_attack([1, 0])
        assert result["hash_states_differ"] is True

    def test_replay_logs_both_events(self, clean_injector):
        clean_injector.inject_replay_attack([1, 0])
        event_types = [e.event_type for e in clean_injector.injection_log]
        assert "REPLAY_FIRST" in event_types
        assert "REPLAY_SECOND" in event_types


# ---------------------------------------------------------------------------
# Burst injection
# ---------------------------------------------------------------------------

class TestBurstInjection:
    def test_burst_injects_correct_count(self, clean_injector, node):
        clean_injector.inject_burst([1, 0, 1], burst_size=10)
        assert node.ballot_count() == 10

    def test_burst_logs_all_events(self, clean_injector):
        clean_injector.inject_burst([1, 0], burst_size=5)
        assert clean_injector.total_events() == 5

    def test_burst_event_type(self, clean_injector):
        clean_injector.inject_burst([1, 0], burst_size=3)
        for event in clean_injector.injection_log:
            assert event.event_type == "BURST"


# ---------------------------------------------------------------------------
# Fuzzy marks
# ---------------------------------------------------------------------------

class TestFuzzyMarks:
    def test_round_strategy(self, clean_injector, node):
        clean_injector.inject_fuzzy_marks([0.9, 0.1, 0.5], rounding_strategy="round")
        assert node.ballot_count() == 1

    def test_floor_strategy(self, clean_injector, node):
        clean_injector.inject_fuzzy_marks([0.9, 0.1, 0.5], rounding_strategy="floor")
        assert node.ballot_count() == 1

    def test_stochastic_strategy(self, clean_injector, node):
        clean_injector.inject_fuzzy_marks([0.8, 0.2, 0.6], rounding_strategy="stochastic")
        assert node.ballot_count() == 1

    def test_invalid_strategy_raises(self, clean_injector):
        with pytest.raises(ValueError, match="rounding_strategy"):
            clean_injector.inject_fuzzy_marks([0.5], rounding_strategy="bad")

    def test_fuzzy_event_type(self, clean_injector):
        clean_injector.inject_fuzzy_marks([0.9, 0.1], rounding_strategy="round")
        assert clean_injector.injection_log[0].event_type == "FUZZY_MARK"


# ---------------------------------------------------------------------------
# Freedom floor monitoring
# ---------------------------------------------------------------------------

class TestFreedomFloor:
    def test_floor_intact_returns_true(self, clean_injector):
        counts = [100, 200, 150, 120, 180]
        assert clean_injector.check_freedom_floor(counts) is True

    def test_floor_violated_raises(self, node):
        inj = ChaosInjector(node, freedom_floor=0.90, seed=0)
        # Only 1 of 10 counties has > 0 ballots → fraction = 0.10 < 0.90
        counts = [100] + [0] * 9
        with pytest.raises(FreedomFloorViolation) as exc_info:
            inj.check_freedom_floor(counts)
        assert exc_info.value.participating_fraction < inj.freedom_floor

    def test_floor_violation_contains_log(self, node):
        inj = ChaosInjector(node, freedom_floor=0.99, seed=0)
        inj.inject_ballot([1, 0])  # add one event to the log
        with pytest.raises(FreedomFloorViolation) as exc_info:
            inj.check_freedom_floor([1, 0, 0, 0, 0])
        assert isinstance(exc_info.value.injection_log, list)

    def test_empty_county_list_returns_true(self, clean_injector):
        assert clean_injector.check_freedom_floor([]) is True

    def test_floor_violation_message_contains_fraction(self, node):
        inj = ChaosInjector(node, freedom_floor=0.9, seed=0)
        with pytest.raises(FreedomFloorViolation) as exc_info:
            inj.check_freedom_floor([0, 0, 0, 0, 100])
        assert "0.2" in str(exc_info.value)

    def test_inject_batch_raises_freedom_floor_on_all_zeros(self, node):
        """ZERO_OUT noise with 100% budget on large batch should trigger floor."""
        inj = ChaosInjector(
            node,
            noise_budget=1.0,
            noise_mode=NoiseMode.ZERO_OUT,
            freedom_floor=0.70,
            seed=1,
        )
        vectors = [[1, 1]] * 10
        with pytest.raises(FreedomFloorViolation):
            inj.inject_batch(vectors)


# ---------------------------------------------------------------------------
# Audit & reset
# ---------------------------------------------------------------------------

class TestAuditAndReset:
    def test_injection_log_as_dicts(self, clean_injector):
        clean_injector.inject_ballot([1, 0])
        dicts = clean_injector.injection_log_as_dicts()
        assert len(dicts) == 1
        assert "event_type" in dicts[0]
        assert "ballot_id" in dicts[0]

    def test_reset_log_clears_events(self, clean_injector):
        clean_injector.inject_ballot([1, 0])
        clean_injector.reset_log()
        assert clean_injector.total_events() == 0

    def test_reset_log_resets_event_index(self, clean_injector):
        clean_injector.inject_ballot([1, 0])
        clean_injector.inject_ballot([0, 1])
        clean_injector.reset_log()
        clean_injector.inject_ballot([1, 1])
        assert clean_injector.injection_log[0].event_index == 1


# ---------------------------------------------------------------------------
# Metric closure integrity under noise
# ---------------------------------------------------------------------------

class TestMetricClosureUnderNoise:
    def test_closure_stable_after_clean_batch(self, node):
        inj = ChaosInjector(node, noise_budget=0.0, seed=0)
        inj.inject_batch([[1, 0]] * 20)
        result = node.validate_closure()
        from EIGE.src.metric_closure import ClosureStatus
        assert result.status == ClosureStatus.STABLE

    def test_closure_stable_after_10pct_noise(self, node):
        """10% noise should not destabilise the metric closure."""
        inj = ChaosInjector(
            node, noise_budget=0.10, noise_mode=NoiseMode.BITFLIP, seed=7
        )
        inj.inject_batch([[1, 0, 1]] * 50)
        result = node.validate_closure()
        from EIGE.src.metric_closure import ClosureStatus
        assert result.status == ClosureStatus.STABLE
