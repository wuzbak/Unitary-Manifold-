# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Univariate distribution monitoring, not prediction-performance monitoring.

The union DKW bound controls a single comparison under independent IID samples
from the same distribution. Repeated looks, dependent entities, and feature
selection require a separately declared monitoring policy. No labels are used
and no model changes or rollback decisions are made.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import random
from typing import Iterable

from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from .temporal_data import TemporalSnapshot, point_in_time_features


def _text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")


def _time(name: str, value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone aware")
    return value.astimezone(timezone.utc)


def _number(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


@dataclass(frozen=True)
class DistributionSample:
    """Immutable numerical capture; raw-array provenance is a caller assertion.

    Event bounds are inclusive. The snapshot adapter enforces temporal selection;
    this low-level container cannot verify timestamps absent from raw arrays.
    """

    dataset_id: str
    owner_scope: str
    feature_name: str
    captured_at: datetime
    decision_time: datetime
    values: tuple[float, ...]
    origins: tuple[str, ...] = ("real",)
    event_start: datetime | None = None
    event_end: datetime | None = None

    def __post_init__(self) -> None:
        for name in ("dataset_id", "owner_scope", "feature_name"):
            _text(name, getattr(self, name))
        for name in ("captured_at", "decision_time"):
            object.__setattr__(self, name, _time(name, getattr(self, name)))
        for name in ("event_start", "event_end"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, _time(name, value))
        if self.event_end is not None and self.event_end > self.decision_time:
            raise ValueError("event_end cannot exceed decision_time")
        if self.event_start is not None and self.event_start > self.decision_time:
            raise ValueError("event_start cannot exceed decision_time")
        if (self.event_start is not None and self.event_end is not None
                and self.event_start > self.event_end):
            raise ValueError("event_start cannot exceed event_end")
        if isinstance(self.values, (str, bytes)):
            raise ValueError("values must be numerical samples")
        object.__setattr__(self, "values", tuple(_number("value", v) for v in self.values))
        if isinstance(self.origins, (str, bytes)):
            raise ValueError("origins must be an iterable")
        origins = tuple(sorted(set(self.origins)))
        if not origins or not set(origins) <= {"real", "synthetic", "fallback"}:
            raise ValueError("origins must explicitly name permitted data origins")
        object.__setattr__(self, "origins", origins)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        for name in ("captured_at", "decision_time", "event_start", "event_end"):
            value = getattr(self, name)
            payload[name] = value.isoformat() if value is not None else None
        return payload

    @property
    def content_hash(self) -> str:
        encoded = json.dumps(self.to_dict(), sort_keys=True, allow_nan=False).encode()
        return hashlib.sha256(encoded).hexdigest()


def sample_from_snapshot(
    snapshot: TemporalSnapshot, *, owner_scope: str, feature_name: str,
    decision_time: datetime, event_start: datetime | None = None,
    event_end: datetime | None = None, allow_origins: Iterable[str] = ("real",),
) -> DistributionSample:
    """Select one latest eligible event/correction per entity, never count history.

    Windows are applied to the selected latest record, not used to resurrect an
    older event. Snapshot content hash identifies the immutable source dataset.
    """
    _text("feature_name", feature_name)
    if not isinstance(snapshot, TemporalSnapshot) or snapshot.owner_scope != owner_scope:
        raise ValueError("snapshot owner_scope mismatch")
    decision = _time("decision_time", decision_time)
    if isinstance(allow_origins, (str, bytes)):
        raise ValueError("allow_origins must be an iterable")
    origins = tuple(allow_origins)
    # Validate even empty snapshots and invalid windows before selecting records.
    scope = DistributionSample(snapshot.content_hash, owner_scope, feature_name,
                               snapshot.captured_at, decision, (), origins,
                               event_start, event_end)
    values = []
    for entity in sorted({r.entity_id for r in snapshot.records if r.feature_name == feature_name}):
        result = point_in_time_features(
            snapshot, owner_scope=owner_scope, entity_id=entity,
            feature_names=(feature_name,), decision_time=decision, allow_origins=origins,
        )[0]
        record = result.record
        if record is None:
            continue
        if scope.event_start is not None and record.event_time < scope.event_start:
            continue
        if scope.event_end is not None and record.event_time > scope.event_end:
            continue
        values.append(record.value)
    return DistributionSample(snapshot.content_hash, owner_scope, feature_name,
                              scope.captured_at, decision, tuple(values), scope.origins,
                              scope.event_start, scope.event_end)


def empirical_ks(reference: Iterable[float], current: Iterable[float]) -> float:
    """Exact empirical two-sample KS D, evaluating both CDFs after every tied value."""
    left = sorted(_number("value", v) for v in reference)
    right = sorted(_number("value", v) for v in current)
    if not left or not right:
        raise ValueError("KS requires two nonempty samples")
    i = j = 0
    distance = 0.0
    while i < len(left) or j < len(right):
        x = min(left[i] if i < len(left) else math.inf,
                right[j] if j < len(right) else math.inf)
        while i < len(left) and left[i] == x:
            i += 1
        while j < len(right) and right[j] == x:
            j += 1
        distance = max(distance, abs(i / len(left) - j / len(right)))
    return distance


@dataclass(frozen=True)
class DriftResult:
    status: str
    statistic: float | None
    threshold: float | None
    alpha: float
    min_sample_size: int
    reference_count: int
    current_count: int
    reference_hash: str
    current_hash: str
    owner_scope: str
    feature_name: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def receipt(self) -> ExecutionSpineRecord:
        return ExecutionSpineRecord(
            surface_id="az-ml-distribution-drift", surface_kind="statistical-monitor",
            lane="adjacent", status=self.status,
            summary="Single-feature distribution comparison; no performance or production claim.",
            sources=[self.reference_hash, self.current_hash],
            compatibility=self.to_dict(),
            governance=build_fail_closed_governance(
                epistemic_label="scoped statistical evidence",
                promotion_rule="Human review required; no automatic model changes.",
                residual_blockers=["No delayed labels or genuine production drift validation."],
            ),
            promotion={"eligible": False, "automatic_promotion": False},
        )


def compare_distributions(
    reference: DistributionSample, current: DistributionSample, *,
    alpha: float = 0.05, min_sample_size: int = 20,
) -> DriftResult:
    """Compare frozen samples; default minimum is 20 observations in EACH sample.

    Under H0, D <= epsilon_n + epsilon_m except with probability <= alpha:
    DKW gives each tail 2 exp(-2 n epsilon_n²) = alpha/2.
    Thresholds above one are intentionally NOT clipped. A non-alert is not proof
    of stability. This is not a p-value or a repeated-monitoring guarantee.
    """
    alpha = _number("alpha", alpha)
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    if isinstance(min_sample_size, bool) or not isinstance(min_sample_size, int) or min_sample_size < 1:
        raise ValueError("min_sample_size must be a positive integer")
    if not isinstance(reference, DistributionSample) or not isinstance(current, DistributionSample):
        raise ValueError("inputs must be DistributionSample captures")
    if (reference.owner_scope, reference.feature_name) != (current.owner_scope, current.feature_name):
        raise ValueError("owner and feature scope must match")
    if reference.origins != current.origins:
        raise ValueError("reference and current origin policies must match")
    n, m = len(reference.values), len(current.values)
    statistic = threshold = None
    status = "insufficient_data"
    if n >= min_sample_size and m >= min_sample_size:
        # log(4) - log(alpha) avoids overflowing 4/alpha for tiny valid alpha.
        log_bound = math.log(4) - math.log(alpha)
        threshold = math.sqrt(log_bound / (2 * n)) + math.sqrt(log_bound / (2 * m))
        statistic = empirical_ks(reference.values, current.values)
        status = "drift_detected" if statistic > threshold else "no_drift_detected"
    return DriftResult(status, statistic, threshold, alpha, min_sample_size, n, m,
                       reference.content_hash, current.content_hash,
                       reference.owner_scope, reference.feature_name)


def evaluate_drift(*, seed: int = 1729, trials: int = 20, sample_size: int = 256,
                   shift: float = 3.0, alpha: float = 0.05) -> dict[str, object]:
    """Bounded reproducible independent N(0,1)/N(shift,1) constructed-fixture replay."""
    for name, value, maximum in (("trials", trials, 1000), ("sample_size", sample_size, 10000)):
        if isinstance(value, bool) or not isinstance(value, int) or not 20 <= value <= maximum:
            raise ValueError(f"{name} must be an integer in [20, {maximum}]")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    shift = _number("shift", shift)
    rng = random.Random(seed)
    stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    false_alerts = detections = 0
    thresholds = []
    for trial in range(trials):
        captures = [
            DistributionSample(f"fixture-{trial}-{label}", "constructed-evaluation", "x",
                               stamp, stamp, tuple(rng.gauss(mean, 1) for _ in range(sample_size)),
                               ("synthetic",))
            for label, mean in (("reference", 0), ("stationary", 0), ("shifted", shift))
        ]
        stationary = compare_distributions(captures[0], captures[1], alpha=alpha)
        shifted = compare_distributions(captures[0], captures[2], alpha=alpha)
        false_alerts += stationary.status == "drift_detected"
        detections += shifted.status == "drift_detected"
        thresholds.append(stationary.threshold)
    return {
        "seed": seed, "trials": trials, "sample_size": sample_size, "shift": shift,
        "alpha": alpha, "threshold": thresholds[0], "false_alerts": false_alerts,
        "false_alert_fraction": false_alerts / trials, "detections": detections,
        "detection_rate": detections / trials,
        "scope": "Independent constructed Gaussian fixtures only; not production or performance drift.",
        "promotion_eligible": False,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_drift(), sort_keys=True, allow_nan=False))
