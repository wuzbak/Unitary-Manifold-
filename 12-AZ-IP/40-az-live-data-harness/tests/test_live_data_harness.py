# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_live_data_harness import (
    FetchSource,
    fetch_with_fallback,
    VerdictLabel,
    compute_verdict,
    LiveDataError,
    USGS_FEED_URL,
    fetch_earthquake_summary,
)
from az_live_data_harness import usgs_adapter


def test_fetch_with_fallback_returns_live_on_success():
    result = fetch_with_fallback(lambda: 42, fallback_value=0)
    assert result.value == 42
    assert result.source == FetchSource.LIVE
    assert result.error is None


def test_fetch_with_fallback_returns_fallback_on_failure():
    def _boom():
        raise RuntimeError("network down")

    result = fetch_with_fallback(_boom, fallback_value=99)
    assert result.value == 99
    assert result.source == FetchSource.FALLBACK
    assert "network down" in result.error


def test_compute_verdict_awaiting_data_when_measured_none():
    verdict = compute_verdict(predicted=1.0, measured=None)
    assert verdict.label == VerdictLabel.AWAITING_DATA


def test_compute_verdict_consistent_within_sigma():
    verdict = compute_verdict(predicted=1.0, measured=1.01, sigma=0.1)
    assert verdict.label == VerdictLabel.CONSISTENT
    assert verdict.sigma_pull == pytest.approx(0.1)


def test_compute_verdict_inconsistent_beyond_sigma():
    verdict = compute_verdict(predicted=1.0, measured=2.0, sigma=0.1, sigma_threshold=2.0)
    assert verdict.label == VerdictLabel.INCONSISTENT


def test_compute_verdict_without_sigma_uses_exact_residual():
    assert compute_verdict(predicted=1.0, measured=1.0).label == VerdictLabel.CONSISTENT
    assert compute_verdict(predicted=1.0, measured=1.5).label == VerdictLabel.INCONSISTENT


def _usgs_payload(generated_at, features=None):
    return {
        "type": "FeatureCollection",
        "metadata": {
            "generated": int(generated_at.timestamp() * 1000),
            "title": "USGS All Earthquakes, Past Day",
        },
        "features": features if features is not None else [
            {
                "id": "test-event",
                "properties": {
                    "time": int((generated_at - timedelta(minutes=5)).timestamp() * 1000),
                    "mag": 2.4,
                    "place": "10 km test",
                    "url": "https://earthquake.usgs.gov/test-event",
                },
            }
        ],
    }


class _Response:
    def __init__(self, payload):
        import json

        self.body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


def test_usgs_adapter_returns_live_provenance_and_latest_event():
    now = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
    payload = _usgs_payload(now - timedelta(minutes=15))
    calls = []

    def opener(req, timeout):
        calls.append((req.full_url, timeout))
        return _Response(payload)

    result = fetch_earthquake_summary(opener=opener, now=now)
    assert calls == [(USGS_FEED_URL, usgs_adapter.REQUEST_TIMEOUT_SECONDS)]
    assert result["source"] == "live"
    assert result["source_url"] == USGS_FEED_URL
    assert result["feed_title"] == "USGS All Earthquakes, Past Day"
    assert result["generated_at"] == "2026-11-02T11:45:00Z"
    assert result["fetched_at"] == "2026-11-02T12:00:00Z"
    assert result["age_seconds"] == 900
    assert result["stale"] is False
    assert result["event_count"] == 1
    assert result["latest_event"]["id"] == "test-event"


def test_usgs_adapter_marks_old_feed_stale():
    now = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
    payload = _usgs_payload(now - timedelta(hours=3))
    result = fetch_earthquake_summary(opener=lambda *_a, **_kw: _Response(payload), now=now)
    assert result["stale"] is True
    assert result["age_seconds"] == 10800


def test_usgs_adapter_surfaces_fetch_failure_without_fallback():
    def offline(*_args, **_kwargs):
        raise OSError("network unavailable")

    with pytest.raises(LiveDataError, match="network unavailable"):
        fetch_earthquake_summary(opener=offline)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"type": "FeatureCollection", "metadata": {}, "features": []},
    ],
)
def test_usgs_adapter_rejects_malformed_or_unverifiable_feed(payload):
    now = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
    with pytest.raises(LiveDataError):
        fetch_earthquake_summary(opener=lambda *_a, **_kw: _Response(payload), now=now)


def test_usgs_adapter_rejects_malformed_event_and_future_feed_timestamp():
    now = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
    malformed_event = _usgs_payload(now, features=[{"id": "missing-properties"}])
    future_feed = _usgs_payload(now + timedelta(minutes=1), features=[])
    for payload in (malformed_event, future_feed):
        with pytest.raises(LiveDataError):
            fetch_earthquake_summary(opener=lambda *_a, **_kw: _Response(payload), now=now)
