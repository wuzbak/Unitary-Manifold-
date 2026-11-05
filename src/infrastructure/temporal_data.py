# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Immutable temporal feature snapshots and point-in-time replay primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Iterable, Sequence

from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from .artifact_io import publish_immutable

TEMPORAL_DATA_SCHEMA_VERSION = "um_temporal_data_v2"
_LEGACY_TEMPORAL_DATA_SCHEMA_VERSION = "um_temporal_data_v1"
_SUPPORTED_TEMPORAL_DATA_SCHEMA_VERSIONS = (
    _LEGACY_TEMPORAL_DATA_SCHEMA_VERSION,
    TEMPORAL_DATA_SCHEMA_VERSION,
)
_ORIGINS = frozenset({"real", "synthetic", "fallback"})
_HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _require_text(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value


def _utc_datetime(name: str, value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be a timezone-aware datetime.")
    return value.astimezone(timezone.utc)


def _format_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_datetime(name: str, value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be an ISO-8601 datetime string.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} is not a valid ISO-8601 datetime.") from exc
    return _utc_datetime(name, parsed)


def _canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


@dataclass(frozen=True)
class TemporalFeatureRecord:
    """A feature observation or explicit source-value correction."""

    owner_scope: str
    entity_id: str
    feature_name: str
    value: float | None
    event_time: datetime
    available_at: datetime
    origin: str = "real"
    missing_reason: str | None = None
    revision_at: datetime | None = None

    def __post_init__(self) -> None:
        _require_text("owner_scope", self.owner_scope)
        _require_text("entity_id", self.entity_id)
        _require_text("feature_name", self.feature_name)
        if self.value is None:
            if not isinstance(self.missing_reason, str) or not self.missing_reason.strip():
                raise ValueError("missing values require an explicit missing_reason.")
            numeric_value = None
        else:
            if self.missing_reason is not None:
                raise ValueError("numeric values cannot carry a missing_reason.")
            if isinstance(self.value, bool) or not isinstance(self.value, (int, float)):
                raise ValueError("value must be a finite number or an explicit missing value.")
            numeric_value = float(self.value)
            if not math.isfinite(numeric_value):
                raise ValueError("value must be a finite number.")
        if not isinstance(self.origin, str) or self.origin not in _ORIGINS:
            raise ValueError(f"origin must be one of {sorted(_ORIGINS)}.")
        event_time = _utc_datetime("event_time", self.event_time)
        available_at = _utc_datetime("available_at", self.available_at)
        if available_at < event_time:
            raise ValueError("available_at cannot precede event_time.")
        revision_at = (
            _utc_datetime("revision_at", self.revision_at)
            if self.revision_at is not None else None
        )
        if revision_at is not None and revision_at > available_at:
            raise ValueError("revision_at cannot follow available_at.")
        object.__setattr__(self, "value", numeric_value)
        object.__setattr__(self, "event_time", event_time)
        object.__setattr__(self, "available_at", available_at)
        object.__setattr__(self, "revision_at", revision_at)


def _record_payload(record: TemporalFeatureRecord) -> dict[str, object]:
    payload = {
        "owner_scope": record.owner_scope,
        "entity_id": record.entity_id,
        "feature_name": record.feature_name,
        "value": record.value,
        "event_time": _format_datetime(record.event_time),
        "available_at": _format_datetime(record.available_at),
        "origin": record.origin,
    }
    if record.missing_reason is not None:
        payload["missing_reason"] = record.missing_reason
    if record.revision_at is not None:
        payload["revision_at"] = _format_datetime(record.revision_at)
    return payload


def _record_sort_key(record: TemporalFeatureRecord) -> str:
    return _canonical_json(_record_payload(record))


@dataclass(frozen=True)
class TemporalSnapshot:
    """Content-addressed immutable feature snapshot for exactly one owner scope."""

    owner_scope: str
    captured_at: datetime
    records: tuple[TemporalFeatureRecord, ...]
    schema_version: str = TEMPORAL_DATA_SCHEMA_VERSION

    def __post_init__(self) -> None:
        _require_text("owner_scope", self.owner_scope)
        if self.schema_version not in _SUPPORTED_TEMPORAL_DATA_SCHEMA_VERSIONS:
            raise ValueError(f"Unsupported temporal data schema version: {self.schema_version!r}.")
        captured_at = _utc_datetime("captured_at", self.captured_at)
        if isinstance(self.records, (str, bytes)):
            raise ValueError("records must be an iterable of TemporalFeatureRecord values.")
        try:
            records = tuple(self.records)
        except TypeError as exc:
            raise ValueError("records must be an iterable of TemporalFeatureRecord values.") from exc
        if any(not isinstance(record, TemporalFeatureRecord) for record in records):
            raise ValueError("records must contain only TemporalFeatureRecord values.")
        if any(record.owner_scope != self.owner_scope for record in records):
            raise ValueError("Every record must belong to the snapshot owner_scope.")
        if self.schema_version == _LEGACY_TEMPORAL_DATA_SCHEMA_VERSION and any(
            record.missing_reason is not None or record.revision_at is not None
            for record in records
        ):
            raise ValueError("Temporal data schema v1 cannot contain correction records.")

        seen: dict[tuple[object, ...], TemporalFeatureRecord] = {}
        for record in records:
            key = (
                record.owner_scope,
                record.entity_id,
                record.feature_name,
                record.event_time,
                record.available_at,
                record.revision_at,
            )
            previous = seen.get(key)
            if previous is not None and previous != record:
                raise ValueError("Conflicting records share an identical temporal key.")
            seen[key] = record
        object.__setattr__(self, "captured_at", captured_at)
        object.__setattr__(self, "records", tuple(sorted(seen.values(), key=_record_sort_key)))

    def _content_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "owner_scope": self.owner_scope,
            "captured_at": _format_datetime(self.captured_at),
            "records": [_record_payload(record) for record in self.records],
        }

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(_canonical_json(self._content_payload()).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class FeatureResult:
    """Point-in-time result; absent data always carries an explicit reason."""

    feature_name: str
    record: TemporalFeatureRecord | None
    missing_reason: str | None = None

    @property
    def value(self) -> float | None:
        return self.record.value if self.record is not None else None


def point_in_time_features(
    snapshot: TemporalSnapshot,
    *,
    owner_scope: str,
    entity_id: str,
    feature_names: Sequence[str],
    decision_time: datetime,
    freshness_ttl_seconds: float | None = None,
    allow_origins: Iterable[str] = ("real",),
) -> tuple[FeatureResult, ...]:
    """Replay latest eligible feature values without event-time or availability leakage."""
    _require_text("owner_scope", owner_scope)
    _require_text("entity_id", entity_id)
    if not isinstance(snapshot, TemporalSnapshot):
        raise ValueError("snapshot must be a TemporalSnapshot.")
    if snapshot.owner_scope != owner_scope:
        raise ValueError("Requested owner_scope does not match the snapshot.")
    decision = _utc_datetime("decision_time", decision_time)
    if freshness_ttl_seconds is not None:
        if (
            isinstance(freshness_ttl_seconds, bool)
            or not isinstance(freshness_ttl_seconds, (int, float))
            or not math.isfinite(float(freshness_ttl_seconds))
            or freshness_ttl_seconds < 0
        ):
            raise ValueError("freshness_ttl_seconds must be finite and non-negative.")
        freshness_ttl_seconds = float(freshness_ttl_seconds)
    if isinstance(feature_names, (str, bytes)):
        raise ValueError("feature_names must be a sequence of non-empty feature names.")
    requested = tuple(_require_text("feature_name", name) for name in feature_names)
    if len(set(requested)) != len(requested):
        raise ValueError("feature_names cannot contain duplicates.")
    if isinstance(allow_origins, (str, bytes)):
        raise ValueError("allow_origins must be an iterable of origin names.")
    try:
        allowed = frozenset(allow_origins)
    except TypeError as exc:
        raise ValueError("allow_origins must be an iterable of origin names.") from exc
    if not allowed <= _ORIGINS:
        raise ValueError(f"allow_origins may contain only {sorted(_ORIGINS)}.")

    results: list[FeatureResult] = []
    for feature_name in requested:
        eligible = [
            record
            for record in snapshot.records
            if record.entity_id == entity_id
            and record.feature_name == feature_name
            and record.event_time <= decision
            and record.available_at <= decision
        ]
        permitted = [record for record in eligible if record.origin in allowed]
        if not permitted:
            reason = "origin_not_allowed" if eligible else "no_point_in_time_data"
            results.append(FeatureResult(feature_name, None, reason))
            continue
        selected = max(
            permitted,
            key=lambda record: (
                record.revision_at or record.event_time,
                record.available_at,
                record.event_time,
            ),
        )
        if selected.value is None:
            results.append(FeatureResult(feature_name, selected, selected.missing_reason))
            continue
        if freshness_ttl_seconds is not None:
            age_seconds = (decision - selected.event_time).total_seconds()
            if age_seconds > freshness_ttl_seconds:
                results.append(FeatureResult(feature_name, None, "stale"))
                continue
        results.append(FeatureResult(feature_name, selected))
    return tuple(results)


def _snapshot_document(snapshot: TemporalSnapshot) -> dict[str, object]:
    return {**snapshot._content_payload(), "content_hash": snapshot.content_hash}


def save_snapshot(
    snapshot: TemporalSnapshot,
    directory: str | Path,
    *,
    owner_scope: str,
) -> Path:
    """Durably publish in an existing directory on a filesystem supporting fsync.

    The caller must create and durably establish the directory and its ancestors.
    """
    if not isinstance(snapshot, TemporalSnapshot):
        raise ValueError("snapshot must be a TemporalSnapshot.")
    if owner_scope != snapshot.owner_scope:
        raise ValueError("Requested owner_scope does not match the snapshot.")
    content = (_canonical_json(_snapshot_document(snapshot)) + "\n").encode("utf-8")
    return publish_immutable(directory, snapshot.content_hash, content)


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}.")
        result[key] = value
    return result


def _record_from_payload(payload: object) -> TemporalFeatureRecord:
    required = {
        "owner_scope",
        "entity_id",
        "feature_name",
        "value",
        "event_time",
        "available_at",
        "origin",
    }
    optional = {"missing_reason", "revision_at"}
    if (
        not isinstance(payload, dict)
        or not required <= set(payload)
        or set(payload) - required - optional
    ):
        raise ValueError("Malformed temporal feature record schema.")
    return TemporalFeatureRecord(
        owner_scope=payload["owner_scope"],
        entity_id=payload["entity_id"],
        feature_name=payload["feature_name"],
        value=payload["value"],
        event_time=_parse_datetime("event_time", payload["event_time"]),
        available_at=_parse_datetime("available_at", payload["available_at"]),
        origin=payload["origin"],
        missing_reason=payload.get("missing_reason"),
        revision_at=(
            _parse_datetime("revision_at", payload["revision_at"])
            if "revision_at" in payload else None
        ),
    )


def load_snapshot(
    directory: str | Path,
    content_hash: str,
    *,
    owner_scope: str,
) -> TemporalSnapshot:
    """Load and verify a snapshot by its SHA-256 identifier and explicit owner scope."""
    _require_text("owner_scope", owner_scope)
    if not isinstance(content_hash, str) or not _HASH_PATTERN.fullmatch(content_hash):
        raise ValueError("content_hash must be a lowercase SHA-256 digest.")
    path = Path(directory) / f"{content_hash}.json"
    if path.is_symlink():
        raise ValueError("Snapshot path cannot be a symbolic link.")
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Invalid JSON number: {value}")),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Unable to read a valid temporal snapshot.") from exc
    expected = {"schema_version", "owner_scope", "captured_at", "records", "content_hash"}
    if not isinstance(payload, dict) or set(payload) != expected:
        raise ValueError("Malformed temporal snapshot schema.")
    if payload["schema_version"] not in _SUPPORTED_TEMPORAL_DATA_SCHEMA_VERSIONS:
        raise ValueError("Unsupported temporal snapshot schema version.")
    if payload["owner_scope"] != owner_scope:
        raise ValueError("Requested owner_scope does not match the snapshot.")
    if payload["content_hash"] != content_hash:
        raise ValueError("Snapshot content hash does not match its address.")
    raw_records = payload["records"]
    if not isinstance(raw_records, list):
        raise ValueError("Snapshot records must be a JSON array.")
    snapshot = TemporalSnapshot(
        owner_scope=owner_scope,
        captured_at=_parse_datetime("captured_at", payload["captured_at"]),
        records=tuple(_record_from_payload(item) for item in raw_records),
        schema_version=payload["schema_version"],
    )
    if snapshot.content_hash != content_hash:
        raise ValueError("Snapshot content hash verification failed.")
    return snapshot


def build_execution_spine_receipt(snapshot: TemporalSnapshot) -> ExecutionSpineRecord:
    """Describe snapshot availability without promoting program or model readiness."""
    if not isinstance(snapshot, TemporalSnapshot):
        raise ValueError("snapshot must be a TemporalSnapshot.")
    return ExecutionSpineRecord(
        surface_id=f"temporal-data:{snapshot.content_hash[:16]}",
        surface_kind="temporal_data_snapshot",
        lane="az_ml_data",
        status="snapshot_available",
        summary="Immutable temporal feature snapshot is available for point-in-time replay.",
        sources=["src/infrastructure/temporal_data.py"],
        governance=build_fail_closed_governance(
            epistemic_label="data_foundation_only",
            promotion_rule="Snapshot availability does not establish live-data or model readiness.",
            residual_blockers=[
                "This primitive receipt does not attest live source adapters or source provenance.",
                "Snapshot availability does not certify production data quality.",
            ],
        ),
        promotion={
            "eligible": False,
            "reason": "Temporal data foundation is not a readiness or promotion signal.",
            "snapshot_hash": snapshot.content_hash,
        },
    )
