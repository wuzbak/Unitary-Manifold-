# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Availability-aware earthquake magnitude snapshots using the existing transport."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from src.infrastructure.execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from src.infrastructure.data_lineage import LineageGraph, LineageNode
from src.infrastructure.temporal_data import TemporalFeatureRecord, TemporalSnapshot

from .usgs_adapter import LiveDataError, USGS_FEED_URL, _fetch_validated_feed, _parse_utc


@dataclass(frozen=True)
class EarthquakeCapture:
    snapshot: TemporalSnapshot
    raw_payload_sha256: str
    feed_generated_at: datetime
    event_count: int
    missing_magnitude_ids: tuple[str, ...]
    stale: bool
    origin: str
    code_bundle_sha256: tuple[tuple[str, str], ...]

    def lineage(self) -> LineageGraph:
        policy = "USGS source terms require caller review; no training-rights certification"
        purpose = "Geophysical observation and availability-aware replay"
        root = LineageNode(
            owner_scope=self.snapshot.owner_scope, kind="source",
            payload_sha256=self.raw_payload_sha256, origins=(self.origin,),
            rights_assertion=policy, purpose_assertion=purpose, source=USGS_FEED_URL,
            metadata=(("observed_at", self.snapshot.captured_at.isoformat()),),
        )
        code_bundle = dict(self.code_bundle_sha256)
        config = {
            "availability": "local_observation", "feature": "earthquake_magnitude",
            "missing_magnitude": "explicitly_reported_not_filled",
        }
        derived = LineageNode(
            owner_scope=self.snapshot.owner_scope, kind="temporal_snapshot",
            payload_sha256=self.snapshot.content_hash, origins=(self.origin,),
            rights_assertion=policy, purpose_assertion=purpose, parent_ids=(root.node_id,),
            transform="usgs_magnitude_temporal_capture_v1",
            code_sha256=hashlib.sha256(json.dumps(code_bundle, sort_keys=True).encode()).hexdigest(),
            config_sha256=hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
            metadata=(("code_bundle_sha256", json.dumps(code_bundle, sort_keys=True)),),
        )
        return LineageGraph(self.snapshot.owner_scope, (root, derived))

    def receipt(self) -> ExecutionSpineRecord:
        return ExecutionSpineRecord(
            surface_id=f"usgs-temporal:{self.snapshot.content_hash}",
            surface_kind="source_bound_temporal_capture",
            lane="az_ml_data",
            status="captured_stale" if self.stale else "captured",
            summary="USGS magnitudes available no earlier than local observation time.",
            canonical_paths=[
                "12-AZ-IP/40-az-live-data-harness/az_live_data_harness/temporal_adapter.py",
            ],
            sources=[USGS_FEED_URL],
            governance=build_fail_closed_governance(
                epistemic_label="observed_data_not_prediction",
                promotion_rule="Capture is not feature-service or prediction-drift qualification.",
                residual_blockers=[
                    "Caller scope is not authenticated multi-user authorization.",
                    "Historical first-publication time is unknown; availability is local observation.",
                ],
            ),
            compatibility={
                "snapshot_sha256": self.snapshot.content_hash,
                "raw_payload_sha256": self.raw_payload_sha256,
                "feed_generated_at": self.feed_generated_at.isoformat(),
                "observed_at": self.snapshot.captured_at.isoformat(),
                "event_count": self.event_count,
                "missing_magnitude_ids": list(self.missing_magnitude_ids),
                "origin_counts": {
                    origin: sum(record.origin == origin for record in self.snapshot.records)
                    for origin in ("real", "synthetic", "fallback")
                },
                "stale": self.stale,
                "availability_policy": "local_observation",
                "feature": "earthquake_magnitude",
                "units": "USGS reported magnitude; magnitude types may differ",
                "revision_selection": "latest locally observed revision for the source event ID",
                "lineage_graph_id": self.lineage().content_hash,
            },
            promotion={"eligible": False, "reason": "Data capture only; no model evaluation."},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt": self.receipt().to_dict(),
            "lineage": json.loads(self.lineage().to_json()),
            "snapshot": {
                "schema_version": self.snapshot.schema_version,
                "content_hash": self.snapshot.content_hash,
                "owner_scope": self.snapshot.owner_scope,
                "captured_at": self.snapshot.captured_at.isoformat(),
                "records": [
                    {
                        "owner_scope": record.owner_scope,
                        "entity_id": record.entity_id,
                        "feature_name": record.feature_name,
                        "value": record.value,
                        "event_time": record.event_time.isoformat(),
                        "available_at": record.available_at.isoformat(),
                        "origin": record.origin,
                        **(
                            {"missing_reason": record.missing_reason}
                            if record.missing_reason is not None else {}
                        ),
                        **(
                            {"revision_at": record.revision_at.isoformat()}
                            if record.revision_at is not None else {}
                        ),
                    }
                    for record in self.snapshot.records
                ],
            },
        }


def fetch_earthquake_snapshot(
    *,
    owner_scope: str,
    origin: str = "real",
    opener: Callable[..., Any] | None = None,
    now: datetime | None = None,
) -> EarthquakeCapture:
    """Fetch once; preserve source identity and never backdate availability.

    Injected/constructed responses must be labeled synthetic by their caller.
    No event is converted into an earlier historical observation simply because
    its earthquake timestamp predates retrieval.
    """
    if not isinstance(owner_scope, str) or not owner_scope.strip():
        raise ValueError("owner_scope must be nonempty text")
    if origin not in ("real", "synthetic", "fallback"):
        raise ValueError("origin must be real, synthetic or fallback")
    payload, summary, raw_hash = _fetch_validated_feed(opener=opener, now=now)
    observed_at = _parse_utc(summary["fetched_at"])
    records: list[TemporalFeatureRecord] = []
    missing: list[str] = []
    seen: set[str] = set()
    try:
        for feature in payload["features"]:
            event_id = feature.get("id")
            if not isinstance(event_id, str) or not event_id.strip() or event_id in seen:
                raise ValueError("Every earthquake needs a unique nonempty source ID")
            seen.add(event_id)
            properties = feature["properties"]
            milliseconds = properties["time"]
            if (
                isinstance(milliseconds, bool)
                or not isinstance(milliseconds, (int, float))
                or not math.isfinite(milliseconds)
            ):
                raise ValueError("Event time must be finite milliseconds, not a boolean")
            event_time = datetime.fromtimestamp(milliseconds / 1000, observed_at.tzinfo)
            if event_time > observed_at:
                raise ValueError("Earthquake time cannot exceed observation time")
            magnitude = properties.get("mag")
            if magnitude is None:
                missing.append(event_id)
                records.append(TemporalFeatureRecord(
                    owner_scope=owner_scope,
                    entity_id=event_id,
                    feature_name="earthquake_magnitude",
                    value=None,
                    event_time=event_time,
                    available_at=observed_at,
                    origin=origin,
                    missing_reason="source_value_missing",
                    revision_at=observed_at,
                ))
                continue
            records.append(TemporalFeatureRecord(
                owner_scope=owner_scope,
                entity_id=event_id,
                feature_name="earthquake_magnitude",
                value=magnitude,
                event_time=event_time,
                available_at=observed_at,
                origin=origin,
                revision_at=observed_at,
            ))
    except (ValueError, KeyError, TypeError, OverflowError, OSError) as exc:
        raise LiveDataError(f"USGS temporal capture invalid: {exc}") from exc
    from src.infrastructure import temporal_data
    from . import usgs_adapter

    modules = (Path(__file__), Path(temporal_data.__file__), Path(usgs_adapter.__file__))
    code_bundle = tuple(sorted(
        (path.name, hashlib.sha256(path.read_bytes()).hexdigest()) for path in modules
    ))
    return EarthquakeCapture(
        snapshot=TemporalSnapshot(owner_scope, observed_at, tuple(records)),
        raw_payload_sha256=raw_hash,
        feed_generated_at=_parse_utc(summary["generated_at"]),
        event_count=summary["event_count"],
        missing_magnitude_ids=tuple(sorted(missing)),
        stale=summary["stale"],
        origin=origin,
        code_bundle_sha256=code_bundle,
    )
