# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Regression tests for the fail-closed temporal data foundation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import stat
import uuid

import pytest

from src.infrastructure.temporal_data import (
    TemporalFeatureRecord,
    TemporalSnapshot,
    build_execution_spine_receipt,
    load_snapshot,
    point_in_time_features,
    save_snapshot,
)


UTC = timezone.utc
BASE = datetime(2026, 1, 1, tzinfo=UTC)


def record(
    *,
    scope: str = "tenant-a",
    entity: str = "entity-1",
    feature: str = "x",
    value: float = 1.0,
    event: datetime = BASE,
    available: datetime | None = None,
    origin: str = "real",
) -> TemporalFeatureRecord:
    return TemporalFeatureRecord(
        owner_scope=scope,
        entity_id=entity,
        feature_name=feature,
        value=value,
        event_time=event,
        available_at=available or event,
        origin=origin,
    )


def snapshot(*records: TemporalFeatureRecord, captured: datetime = BASE) -> TemporalSnapshot:
    return TemporalSnapshot("tenant-a", captured, tuple(records))


def test_snapshot_hash_is_stable_and_record_order_independent() -> None:
    first, second = record(feature="a"), record(feature="b", value=2.0)
    left = snapshot(first, second)
    right = snapshot(second, first)
    assert left.content_hash == right.content_hash
    assert left.records == right.records


def test_snapshot_is_immutable_and_rejects_mixed_scope_and_conflicting_keys() -> None:
    with pytest.raises(ValueError, match="owner_scope"):
        snapshot(record(scope="tenant-b"))
    with pytest.raises(ValueError, match="Conflicting"):
        snapshot(record(value=1), record(value=2))
    with pytest.raises((AttributeError, TypeError)):
        snapshot().records += (record(),)


def test_point_in_time_replay_blocks_future_event_and_late_availability() -> None:
    future = record(value=2, event=BASE + timedelta(hours=1), available=BASE + timedelta(hours=3))
    correction = record(value=3, event=BASE, available=BASE + timedelta(hours=2))
    data = snapshot(record(value=1), future, correction)
    before_event, before_correction, after_correction, after_event = point_in_time_features(
        data,
        owner_scope="tenant-a",
        entity_id="entity-1",
        feature_names=("x",),
        decision_time=BASE + timedelta(minutes=30),
    )[0], point_in_time_features(
        data,
        owner_scope="tenant-a",
        entity_id="entity-1",
        feature_names=("x",),
        decision_time=BASE + timedelta(hours=1),
    )[0], point_in_time_features(
        data,
        owner_scope="tenant-a",
        entity_id="entity-1",
        feature_names=("x",),
        decision_time=BASE + timedelta(hours=2, minutes=30),
    )[0], point_in_time_features(
        data,
        owner_scope="tenant-a",
        entity_id="entity-1",
        feature_names=("x",),
        decision_time=BASE + timedelta(hours=3, minutes=30),
    )[0]
    assert before_event.value == 1
    assert before_correction.value == 1
    assert after_correction.value == 3
    assert after_event.value == 2


def test_owner_scope_and_origin_restrictions_fail_closed() -> None:
    data = snapshot(record(origin="synthetic", value=7))
    with pytest.raises(ValueError, match="owner_scope"):
        point_in_time_features(
            data,
            owner_scope="tenant-b",
            entity_id="entity-1",
            feature_names=("x",),
            decision_time=BASE,
        )
    default = point_in_time_features(
        data,
        owner_scope="tenant-a",
        entity_id="entity-1",
        feature_names=("x",),
        decision_time=BASE,
    )[0]
    explicit = point_in_time_features(
        data,
        owner_scope="tenant-a",
        entity_id="entity-1",
        feature_names=("x",),
        decision_time=BASE,
        allow_origins=("real", "synthetic"),
    )[0]
    assert default.value is None and default.missing_reason == "origin_not_allowed"
    assert explicit.value == 7


def test_missing_features_and_freshness_have_explicit_reasons() -> None:
    data = snapshot(record(), record(entity="entity-2", feature="other", value=5))
    results = point_in_time_features(
        data,
        owner_scope="tenant-a",
        entity_id="entity-1",
        feature_names=("x", "missing"),
        decision_time=BASE + timedelta(seconds=5),
        freshness_ttl_seconds=2,
    )
    assert [(item.value, item.missing_reason) for item in results] == [
        (None, "stale"),
        (None, "no_point_in_time_data"),
    ]


@pytest.mark.parametrize("ttl", [-1, True, float("inf"), float("nan")])
def test_invalid_ttl_is_rejected(ttl: float) -> None:
    with pytest.raises(ValueError, match="freshness_ttl_seconds"):
        point_in_time_features(
            snapshot(record()),
            owner_scope="tenant-a",
            entity_id="entity-1",
            feature_names=("x",),
            decision_time=BASE,
            freshness_ttl_seconds=ttl,
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"value": float("nan")},
        {"value": float("inf")},
        {"event_time": datetime(2026, 1, 1)},
        {"available_at": BASE - timedelta(seconds=1)},
    ],
)
def test_invalid_record_values_and_times_are_rejected(changes: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        TemporalFeatureRecord(
            owner_scope="tenant-a",
            entity_id="entity-1",
            feature_name="x",
            value=changes.get("value", 1.0),  # type: ignore[arg-type]
            event_time=changes.get("event_time", BASE),  # type: ignore[arg-type]
            available_at=changes.get("available_at", BASE),  # type: ignore[arg-type]
        )


def _storage_dir() -> Path:
    path = Path(__file__).parent / f".temporal-data-test-{uuid.uuid4().hex}"
    path.mkdir()
    return path


def test_content_addressed_snapshot_round_trip_and_existing_publication() -> None:
    directory = _storage_dir()
    try:
        original = snapshot(record(), record(feature="y", value=4))
        path = save_snapshot(original, directory, owner_scope="tenant-a")
        assert path.name == f"{original.content_hash}.json"
        assert save_snapshot(original, directory, owner_scope="tenant-a") == path
        assert load_snapshot(directory, original.content_hash, owner_scope="tenant-a") == original
        assert sorted(item.name for item in directory.iterdir()) == [path.name]
    finally:
        shutil.rmtree(directory)


def test_snapshot_publication_fsyncs_directory_after_link_and_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = _storage_dir()
    events: list[str] = []
    real_fsync, real_link, real_unlink = os.fsync, os.link, Path.unlink
    try:
        def tracked_fsync(fd: int) -> None:
            events.append("directory_fsync" if stat.S_ISDIR(os.fstat(fd).st_mode) else "file_fsync")
            real_fsync(fd)

        def tracked_link(source: str | Path, target: str | Path) -> None:
            events.append("link")
            real_link(source, target)

        def tracked_unlink(path: Path, *args: object, **kwargs: object) -> None:
            if path.suffix == ".tmp":
                events.append("temporary_unlink")
            real_unlink(path, *args, **kwargs)

        monkeypatch.setattr(os, "fsync", tracked_fsync)
        monkeypatch.setattr(os, "link", tracked_link)
        monkeypatch.setattr(Path, "unlink", tracked_unlink)

        original = snapshot(record())
        save_snapshot(original, directory, owner_scope="tenant-a")
        assert events == ["file_fsync", "link", "temporary_unlink", "directory_fsync"]
        events.clear()
        save_snapshot(original, directory, owner_scope="tenant-a")
        assert events == [
            "file_fsync",
            "link",
            "file_fsync",
            "temporary_unlink",
            "directory_fsync",
        ]
    finally:
        shutil.rmtree(directory)


def test_directory_fsync_failure_propagates_after_publication_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = _storage_dir()
    real_fsync = os.fsync
    try:
        def fail_directory_fsync(fd: int) -> None:
            if stat.S_ISDIR(os.fstat(fd).st_mode):
                raise OSError("directory sync failed")
            real_fsync(fd)

        monkeypatch.setattr(os, "fsync", fail_directory_fsync)
        original = snapshot(record())
        with pytest.raises(OSError, match="directory sync failed"):
            save_snapshot(original, directory, owner_scope="tenant-a")
        assert (directory / f"{original.content_hash}.json").exists()
        assert not list(directory.glob("*.tmp"))
    finally:
        shutil.rmtree(directory)


def test_snapshot_save_requires_existing_directory() -> None:
    parent = _storage_dir()
    missing = parent / "not-created"
    try:
        with pytest.raises(FileNotFoundError):
            save_snapshot(snapshot(record()), missing, owner_scope="tenant-a")
        assert not missing.exists()
    finally:
        shutil.rmtree(parent)


def test_snapshot_loader_rejects_scope_tampering_schema_and_traversal() -> None:
    directory = _storage_dir()
    try:
        original = snapshot(record())
        path = save_snapshot(original, directory, owner_scope="tenant-a")
        with pytest.raises(ValueError, match="owner_scope"):
            load_snapshot(directory, original.content_hash, owner_scope="tenant-b")
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["records"][0]["value"] = 99
        tampered_content = json.dumps(payload)
        path.write_text(tampered_content, encoding="utf-8")
        with pytest.raises(ValueError, match="does not match"):
            save_snapshot(original, directory, owner_scope="tenant-a")
        assert path.read_text(encoding="utf-8") == tampered_content
        with pytest.raises(ValueError, match="hash"):
            load_snapshot(directory, original.content_hash, owner_scope="tenant-a")
        with pytest.raises(ValueError, match="content_hash"):
            load_snapshot(directory, "../outside", owner_scope="tenant-a")
    finally:
        shutil.rmtree(directory)


@pytest.mark.parametrize(
    ("field", "value"),
    [("schema_version", "unknown"), ("captured_at", "2026-01-01T00:00:00")],
)
def test_snapshot_loader_rejects_malformed_schema_and_naive_time(
    field: str, value: str
) -> None:
    directory = _storage_dir()
    try:
        original = snapshot(record())
        path = save_snapshot(original, directory, owner_scope="tenant-a")
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[field] = value
        path.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError):
            load_snapshot(directory, original.content_hash, owner_scope="tenant-a")
    finally:
        shutil.rmtree(directory)


def test_receipt_is_an_execution_spine_record_but_never_promotion_eligible() -> None:
    receipt = build_execution_spine_receipt(snapshot(record()))
    assert receipt.surface_kind == "temporal_data_snapshot"
    assert receipt.promotion["eligible"] is False
    assert receipt.governance["fail_closed"] is True
    assert "live source adapters" in receipt.governance["residual_blockers"][0]
