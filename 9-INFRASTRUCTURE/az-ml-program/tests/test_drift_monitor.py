# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Independent fixtures for scoped distribution monitoring."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from itertools import combinations_with_replacement
import json
import math

import pytest

from src.infrastructure.drift_monitor import (
    DistributionSample, compare_distributions, empirical_ks, evaluate_drift,
    sample_from_snapshot,
)
from src.infrastructure.temporal_data import TemporalFeatureRecord, TemporalSnapshot

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def sample(values, **kwargs):
    return DistributionSample("dataset", "owner", "feature", NOW, NOW, values, **kwargs)


@pytest.mark.parametrize("left,right,expected", [
    ([0, 0, 1], [0, 1, 1], 1 / 3),
    ([0, 0, 2, 2], [0, 1, 1, 2], .25),
    ([1, 1], [1, 1, 1], 0),
    ([0, 1], [2, 3], 1),
    ([0, 2], [1, 2, 2], .5),
])
def test_exact_ecdf_ties_and_symmetry(left, right, expected):
    assert empirical_ks(left, right) == pytest.approx(expected)
    assert empirical_ks(right, left) == pytest.approx(expected)
    assert empirical_ks(reversed(left), reversed(right)) == pytest.approx(expected)


def test_conservative_bound_and_no_clipping():
    result = compare_distributions(sample([0]), sample([1]), min_sample_size=1)
    assert result.threshold == pytest.approx(2 * math.sqrt(math.log(80) / 2))
    assert result.threshold > 1
    assert result.statistic == 1
    assert result.status == "no_drift_detected"
    larger = compare_distributions(sample([0] * 100), sample([1] * 200))
    assert larger.threshold == pytest.approx(
        math.sqrt(math.log(80) / 200) + math.sqrt(math.log(80) / 400))
    assert larger.status == "drift_detected"
    assert (larger.reference_count, larger.current_count) == (100, 200)


def test_exhaustive_small_tied_samples_against_independent_rational_ecdfs():
    fixtures = [values for size in (1, 2, 3)
                for values in combinations_with_replacement((-1, 0, 1), size)]
    for left in fixtures:
        for right in fixtures:
            expected = max(
                abs(Fraction(sum(v <= x for v in left), len(left))
                    - Fraction(sum(v <= x for v in right), len(right)))
                for x in set(left + right)
            )
            assert empirical_ks(left, right) == pytest.approx(float(expected))


def test_cutoff_is_strict_and_non_alert_does_not_assert_stability():
    result = compare_distributions(sample([0] * 20), sample([1] * 20),
                                   alpha=4 * math.exp(-10))
    assert result.threshold == 1
    assert result.statistic == 1
    assert result.status == "no_drift_detected"


@pytest.mark.parametrize("alpha", [True, False, 0, 1, -1, float("nan"), float("inf"), ".05"])
def test_invalid_alpha(alpha):
    with pytest.raises(ValueError):
        compare_distributions(sample([0]), sample([0]), alpha=alpha)


@pytest.mark.parametrize("value", [True, False, float("nan"), float("inf"), "2"])
def test_invalid_sample(value):
    with pytest.raises(ValueError):
        sample([value])


@pytest.mark.parametrize("minimum", [True, 0, -1, 1.5])
def test_invalid_minimum(minimum):
    with pytest.raises(ValueError):
        compare_distributions(sample([1]), sample([2]), min_sample_size=minimum)


@pytest.mark.parametrize("left,right", [([], []), ([1], [2] * 20), ([1] * 20, [])])
def test_insufficient_data_is_not_stable(left, right):
    result = compare_distributions(sample(left), sample(right))
    assert result.status == "insufficient_data"
    assert result.statistic is result.threshold is None
    json.dumps(result.receipt().to_dict(), allow_nan=False)
    assert result.receipt().promotion["eligible"] is False


def test_immutable_identity_and_scope():
    values = [1, 2]
    capture = sample(values)
    values.append(3)
    assert capture.values == (1, 2)
    with pytest.raises(FrozenInstanceError):
        capture.values = ()
    assert replace(capture, dataset_id="other").content_hash != capture.content_hash
    assert replace(capture, decision_time=NOW + timedelta(days=1)).content_hash != capture.content_hash
    for changed in (replace(capture, owner_scope="other"), replace(capture, feature_name="other")):
        with pytest.raises(ValueError):
            compare_distributions(capture, changed)
    result = compare_distributions(sample([0] * 20), sample([0] * 20), alpha=5e-324)
    assert math.isfinite(result.threshold)


def record(entity, value, event=-3, available=-2, origin="real", feature="feature"):
    return TemporalFeatureRecord("owner", entity, feature, value,
                                 NOW + timedelta(days=event),
                                 NOW + timedelta(days=available), origin)


def test_snapshot_temporal_origins_corrections_and_feature_scope():
    snapshot = TemporalSnapshot("owner", NOW, (
        record("a", 1, -4, -4), record("a", 2, -3, -3),
        record("a", 3, -3, -1), record("a", 999, -3, 1),
        record("b", 4), record("c", 900, origin="synthetic"),
        record("d", 901, origin="fallback"), record("e", 902, 1, 1),
        record("f", 903, feature="other"),
    ))
    capture = sample_from_snapshot(snapshot, owner_scope="owner", feature_name="feature", decision_time=NOW)
    assert capture.values == (3, 4)
    assert capture.dataset_id == snapshot.content_hash
    included = sample_from_snapshot(snapshot, owner_scope="owner", feature_name="feature",
                                    decision_time=NOW, allow_origins=("real", "synthetic", "fallback"))
    assert included.values == (3, 4, 900, 901)
    with pytest.raises(ValueError):
        sample_from_snapshot(snapshot, owner_scope="other", feature_name="feature", decision_time=NOW)
    with pytest.raises(ValueError):
        sample_from_snapshot(snapshot, owner_scope="owner", feature_name="", decision_time=NOW)
    window = sample_from_snapshot(snapshot, owner_scope="owner", feature_name="feature",
                                  decision_time=NOW, event_start=NOW - timedelta(days=2))
    assert window.values == ()


def test_window_validation_and_empty_snapshot_origins():
    with pytest.raises(ValueError):
        sample([], event_end=NOW + timedelta(seconds=1))
    with pytest.raises(ValueError, match="event_start cannot exceed decision_time"):
        sample([], event_start=NOW + timedelta(seconds=1))
    with pytest.raises(ValueError):
        sample([], event_start=NOW, event_end=NOW - timedelta(seconds=1))
    with pytest.raises(ValueError):
        sample_from_snapshot(TemporalSnapshot("owner", NOW, ()), owner_scope="owner",
                             feature_name="feature", decision_time=NOW, allow_origins=("unknown",))


@pytest.mark.parametrize("origins", [("synthetic",), ("fallback",), ("real", "synthetic")])
def test_comparison_rejects_mismatched_origin_policies(origins):
    with pytest.raises(ValueError, match="origin policies must match"):
        compare_distributions(sample([0] * 20), sample([0] * 20, origins=origins))


def test_comparison_accepts_identical_explicit_origin_policy():
    result = compare_distributions(
        sample([0] * 20, origins=("synthetic", "real")),
        sample([0] * 20, origins=("real", "synthetic")),
    )
    assert result.status == "no_drift_detected"


def test_snapshot_window_boundaries_and_no_history_resurrection():
    snapshot = TemporalSnapshot("owner", NOW, (
        record("a", 1, -4, -4), record("a", 2, -1, -1),
        record("b", 3, -3, -3), record("c", 4, -2, -2),
    ))
    capture = sample_from_snapshot(
        snapshot, owner_scope="owner", feature_name="feature", decision_time=NOW,
        event_start=NOW - timedelta(days=4), event_end=NOW - timedelta(days=2),
    )
    assert capture.values == (3, 4)
    missing = sample_from_snapshot(snapshot, owner_scope="owner", feature_name="missing",
                                   decision_time=NOW)
    assert compare_distributions(capture, replace(missing, feature_name="feature")).status == "insufficient_data"


@pytest.mark.parametrize("kwargs", [
    {"seed": True}, {"trials": True}, {"trials": 1001}, {"sample_size": 0},
    {"sample_size": 10001}, {"shift": float("nan")}, {"alpha": True},
])
def test_evaluation_rejects_invalid_or_unbounded_requests(kwargs):
    with pytest.raises(ValueError):
        evaluate_drift(**kwargs)


def test_constructed_evaluation_replay_and_receipt():
    report = evaluate_drift()
    assert report == evaluate_drift()
    assert report["false_alerts"] == 0
    assert report["detections"] == 20
    assert report["detection_rate"] == 1
    assert report["promotion_eligible"] is False
    assert "constructed" in report["scope"]
    json.dumps(report, allow_nan=False)
    payload = compare_distributions(sample([0] * 100), sample([1] * 100)).receipt().to_dict()
    assert payload["promotion"]["automatic_promotion"] is False
    json.dumps(payload, allow_nan=False)
