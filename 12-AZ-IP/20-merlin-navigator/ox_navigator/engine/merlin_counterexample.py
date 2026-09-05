# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Contradiction and counterexample digest helpers for Merlin."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from .merlin_memory import MerlinSession


def _digest_id(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _sort_key(item: dict[str, Any], index: int) -> tuple[datetime, int]:
    stamp = str(item.get("detected_at", "") or "")
    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        parsed = datetime.min
    return parsed, index


def build_counterexample_digest(*, session: MerlinSession, limit: int = 10) -> dict[str, Any]:
    cap = max(1, min(int(limit or 10), 25))
    events = list(session.contradiction_events)[-cap:]
    quarantined = list(session.quarantined_insights)[-cap:]
    kind_counts: dict[str, int] = {}
    items: list[dict[str, Any]] = []

    for event in events:
        kind = str(event.get("kind") or "gate_drift")
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        payload = {
            "kind": kind,
            "query": str(event.get("query", "")),
            "detected_at": str(event.get("detected_at", "")),
            "conflicts": list(event.get("conflicts") or []),
        }
        items.append(
            {
                "digest_id": _digest_id(payload),
                **payload,
                "source": "contradiction_event",
                "training_signal_class": "counterexample",
            }
        )

    for insight in quarantined:
        conflicts = list(insight.get("contradictions") or [])
        kind = "quarantined_insight"
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        payload = {
            "kind": kind,
            "query": str(insight.get("source_query", "")),
            "detected_at": str(insight.get("ingested_at", "")),
            "conflicts": conflicts,
        }
        items.append(
            {
                "digest_id": _digest_id(payload),
                **payload,
                "source": "quarantined_insight",
                "training_signal_class": "counterexample",
                "status": str(insight.get("status", "")),
            }
        )

    items = [item for _, item in sorted(enumerate(items), key=lambda pair: _sort_key(pair[1], pair[0]))]
    items = items[-cap:]
    summarized_kind_counts: dict[str, int] = {}
    event_count = 0
    quarantined_count = 0
    for item in items:
        kind = str(item.get("kind") or "gate_drift")
        summarized_kind_counts[kind] = summarized_kind_counts.get(kind, 0) + 1
        if item.get("source") == "contradiction_event":
            event_count += 1
        if item.get("source") == "quarantined_insight":
            quarantined_count += 1
    return {
        "ok": True,
        "total_events": event_count,
        "quarantined_insight_count": quarantined_count,
        "kind_counts": summarized_kind_counts,
        "items": items,
        "stage_b_refresh_ready": bool(items),
    }
