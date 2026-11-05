# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Transport, historical-availability and product-entrypoint integration tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import threading
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT))

from az_live_data_harness.api import dispatch_api_request
from az_live_data_harness.app.server import build_server
from az_live_data_harness.temporal_adapter import fetch_earthquake_snapshot
from az_live_data_harness.usgs_adapter import LiveDataError, USGS_FEED_URL
from src.infrastructure.temporal_data import load_snapshot, point_in_time_features
from src.infrastructure.data_lineage import LineageGraph, load_graph

NOW = datetime(2026, 11, 5, 12, tzinfo=timezone.utc)


def feed(magnitude=2.5):
    return {
        "type": "FeatureCollection",
        "metadata": {"generated": int((NOW - timedelta(minutes=1)).timestamp() * 1000)},
        "features": [{
            "id": "earthquake-a",
            "properties": {
                "time": int((NOW - timedelta(hours=1)).timestamp() * 1000),
                "mag": magnitude,
            },
        }],
    }


class Response:
    def __init__(self, payload):
        self.raw = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.raw


def capture(payload=None, *, now=NOW):
    response = Response(feed() if payload is None else payload)
    return fetch_earthquake_snapshot(
        owner_scope="test-project", origin="synthetic",
        opener=lambda *_args, **_kwargs: response, now=now,
    )


def test_capture_uses_existing_transport_once_and_preserves_exact_source_identity():
    response = Response(feed())
    calls = []

    def opener(req, timeout):
        calls.append((req.full_url, timeout))
        return response

    result = fetch_earthquake_snapshot(
        owner_scope="test-project", origin="synthetic", opener=opener, now=NOW,
    )
    assert calls == [(USGS_FEED_URL, 10)]
    assert result.raw_payload_sha256 == hashlib.sha256(response.raw).hexdigest()
    assert result.event_count == 1
    assert result.snapshot.records[0].available_at == NOW
    assert result.snapshot.records[0].origin == "synthetic"
    receipt = result.receipt().to_dict()
    assert receipt["promotion"]["eligible"] is False
    assert receipt["compatibility"]["origin_counts"] == {"real": 0, "synthetic": 1, "fallback": 0}
    assert json.loads(json.dumps(result.to_dict()))["snapshot"]["records"][0]["value"] == 2.5
    graph = LineageGraph.from_json(json.dumps(result.to_dict()["lineage"]))
    source = next(node for node in graph.nodes if node.kind == "source")
    derived = next(node for node in graph.nodes if node.kind == "temporal_snapshot")
    assert source.payload_sha256 == result.raw_payload_sha256
    assert derived.payload_sha256 == result.snapshot.content_hash
    assert derived.parent_ids == (source.node_id,)
    assert derived.origins == ("synthetic",)
    assert graph.affected_by_deletion((source.node_id,)).remove_ids == tuple(sorted((source.node_id, derived.node_id)))
    assert receipt["compatibility"]["lineage_graph_id"] == graph.content_hash


def test_old_event_cannot_be_retrieved_before_local_observation():
    result = capture()
    kwargs = dict(
        snapshot=result.snapshot, owner_scope="test-project", entity_id="earthquake-a",
        feature_names=("earthquake_magnitude",), allow_origins=("synthetic",),
    )
    before = point_in_time_features(**kwargs, decision_time=NOW - timedelta(seconds=1))[0]
    after = point_in_time_features(**kwargs, decision_time=NOW)[0]
    assert before.missing_reason == "no_point_in_time_data"
    assert after.value == 2.5
    with pytest.raises(ValueError, match="owner_scope"):
        point_in_time_features(**{**kwargs, "owner_scope": "another-owner"}, decision_time=NOW)


def test_capture_pins_transform_identity_instead_of_rehashing_sources_later(monkeypatch):
    observed = capture()
    before = observed.lineage().content_hash

    def no_later_reads(*_args, **_kwargs):
        raise AssertionError("A captured transform identity must not read later working files")

    monkeypatch.setattr(Path, "read_bytes", no_later_reads)
    assert observed.lineage().content_hash == before


def test_later_capture_preserves_later_correction_availability():
    first = capture()
    later = capture(feed(3.0), now=NOW + timedelta(minutes=5))
    from src.infrastructure.temporal_data import TemporalSnapshot

    combined = TemporalSnapshot(
        "test-project", NOW + timedelta(minutes=5),
        first.snapshot.records + later.snapshot.records,
    )
    common = dict(
        snapshot=combined, owner_scope="test-project", entity_id="earthquake-a",
        feature_names=("earthquake_magnitude",), allow_origins=("synthetic",),
    )
    assert point_in_time_features(**common, decision_time=NOW)[0].value == 2.5
    assert point_in_time_features(
        **common, decision_time=NOW + timedelta(minutes=5),
    )[0].value == 3.0
    assert first.snapshot.content_hash != later.snapshot.content_hash


def test_unknown_magnitude_is_reported_not_zero_filled():
    result = capture(feed(None))
    assert result.event_count == 1
    assert result.snapshot.records == ()
    assert result.missing_magnitude_ids == ("earthquake-a",)


@pytest.mark.parametrize("magnitude", [True, "2", float("nan"), float("inf")])
def test_invalid_magnitude_is_explicit_failure(magnitude):
    with pytest.raises(LiveDataError):
        capture(feed(magnitude))


@pytest.mark.parametrize("bad_time", [True, float("nan"), float("inf")])
def test_invalid_source_timestamps_rejected(bad_time):
    for location in ("generated", "time"):
        payload = feed()
        if location == "generated":
            payload["metadata"]["generated"] = bad_time
        else:
            payload["features"][0]["properties"]["time"] = bad_time
        with pytest.raises(LiveDataError):
            capture(payload)


def test_duplicate_ids_and_future_event_are_not_silently_discarded():
    payload = feed()
    payload["features"] *= 2
    with pytest.raises(LiveDataError, match="unique"):
        capture(payload)
    payload = feed()
    payload["features"][0]["properties"]["time"] = (NOW + timedelta(seconds=1)).timestamp() * 1000
    with pytest.raises(LiveDataError, match="observation"):
        capture(payload)


def test_stale_feed_remains_explicitly_stale():
    result = capture(now=NOW + timedelta(hours=3))
    assert result.stale
    assert result.receipt().status == "captured_stale"


@pytest.mark.parametrize("scope", ["", " ", None])
def test_scope_required_before_fetch(scope):
    with pytest.raises(ValueError, match="owner_scope"):
        fetch_earthquake_snapshot(owner_scope=scope)


def test_temporal_endpoint_requires_single_scope_and_propagates_transport_failure(monkeypatch):
    for query in ({}, {"owner_scope": [""]}, {"owner_scope": ["a", "b"]}):
        with pytest.raises(ValueError, match="owner_scope"):
            dispatch_api_request("/api/temporal-result", query)
    expected = capture()
    monkeypatch.setattr(
        "az_live_data_harness.temporal_adapter.fetch_earthquake_snapshot",
        lambda **kwargs: expected,
    )
    assert dispatch_api_request(
        "/api/temporal-result", {"owner_scope": ["test-project"]},
    )["snapshot"]["content_hash"] == expected.snapshot.content_hash

    def fail(**_kwargs):
        raise LiveDataError("offline")

    monkeypatch.setattr("az_live_data_harness.temporal_adapter.fetch_earthquake_snapshot", fail)
    with pytest.raises(LiveDataError, match="offline"):
        dispatch_api_request("/api/temporal-result", {"owner_scope": ["test-project"]})


def test_http_surface_returns_400_for_missing_scope_and_502_for_feed_failure(monkeypatch):
    def fail(**_kwargs):
        raise LiveDataError("transport unavailable")

    monkeypatch.setattr("az_live_data_harness.temporal_adapter.fetch_earthquake_snapshot", fail)
    server = build_server(port=0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        for path, status in (
            ("/api/temporal-result", 400),
            ("/api/temporal-result?owner_scope=test-project", 502),
        ):
            with pytest.raises(HTTPError) as error:
                urlopen(base + path, timeout=5)
            assert error.value.code == status
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert not thread.is_alive()


def test_cli_saves_verifiable_snapshot_and_requires_explicit_scope(monkeypatch, tmp_path, capsys):
    spec = importlib.util.spec_from_file_location("p40_temporal_run", PRODUCT_ROOT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(SystemExit) as error:
        module.main(["--temporal"])
    assert error.value.code == 2
    capsys.readouterr()
    expected = capture()
    monkeypatch.setattr(
        "az_live_data_harness.temporal_adapter.fetch_earthquake_snapshot",
        lambda **_kwargs: expected,
    )
    assert module.main([
        "--temporal", "--owner-scope", "test-project", "--snapshot-dir", str(tmp_path),
    ]) == 0
    output = json.loads(capsys.readouterr().out)
    assert Path(output["snapshot_path"]).is_file()
    assert load_graph(output["lineage_path"]).content_hash == expected.lineage().content_hash
    assert load_snapshot(tmp_path, expected.snapshot.content_hash, owner_scope="test-project") == expected.snapshot
    assert module.main([
        "--temporal", "--owner-scope", "test-project", "--snapshot-dir", str(tmp_path / "absent"),
    ]) == 1
    assert "error" in json.loads(capsys.readouterr().err)
