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
from az_live_data_harness.capture_archive import load_capture_archive, save_capture_archive
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

    def read(self, size=-1):
        return self.raw if size < 0 else self.raw[:size]


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


def test_numeric_to_null_correction_is_persisted_and_replayed(tmp_path):
    first = capture()
    later = capture(feed(None), now=NOW + timedelta(minutes=5))
    from src.infrastructure.temporal_data import TemporalSnapshot, save_snapshot

    combined = TemporalSnapshot(
        "test-project", NOW + timedelta(minutes=5),
        first.snapshot.records + later.snapshot.records,
    )
    saved = save_snapshot(combined, tmp_path, owner_scope="test-project")
    restored = load_snapshot(tmp_path, combined.content_hash, owner_scope="test-project")
    common = dict(
        snapshot=restored, owner_scope="test-project", entity_id="earthquake-a",
        feature_names=("earthquake_magnitude",), allow_origins=("synthetic",),
    )
    before = point_in_time_features(**common, decision_time=NOW)[0]
    after = point_in_time_features(**common, decision_time=NOW + timedelta(minutes=5))[0]
    assert saved.is_file()
    assert before.value == 2.5
    assert after.value is None
    assert after.missing_reason == "source_value_missing"


def test_backward_event_time_revision_uses_latest_available_source_revision():
    first = capture()
    corrected = feed(3.0)
    corrected["features"][0]["properties"]["time"] = (
        NOW - timedelta(hours=2)
    ).timestamp() * 1000
    later = capture(corrected, now=NOW + timedelta(minutes=5))
    from src.infrastructure.temporal_data import TemporalSnapshot

    combined = TemporalSnapshot(
        "test-project", NOW + timedelta(minutes=5),
        first.snapshot.records + later.snapshot.records,
    )
    common = dict(
        snapshot=combined, owner_scope="test-project", entity_id="earthquake-a",
        feature_names=("earthquake_magnitude",), allow_origins=("synthetic",),
    )
    before = point_in_time_features(**common, decision_time=NOW)[0]
    after = point_in_time_features(
        **common, decision_time=NOW + timedelta(minutes=5),
    )[0]
    assert before.value == 2.5
    assert after.value == 3.0
    assert after.record.event_time == NOW - timedelta(hours=2)


def test_unknown_magnitude_is_reported_and_persisted_not_zero_filled():
    result = capture(feed(None))
    assert result.event_count == 1
    assert result.snapshot.records[0].value is None
    assert result.snapshot.records[0].missing_reason == "source_value_missing"
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


def test_raw_archive_preserves_exact_bytes_and_original_availability(monkeypatch, tmp_path):
    response = Response(feed(None))
    response.raw = json.dumps(feed(None), indent=3).encode() + b"\n\n"
    original = fetch_earthquake_snapshot(
        owner_scope="test-project", origin="synthetic",
        opener=lambda *_args, **_kwargs: response, now=NOW,
    )
    saved = save_capture_archive(original, tmp_path)
    assert saved == save_capture_archive(original, tmp_path)
    assert saved.stem == hashlib.sha256(saved.read_bytes()).hexdigest()

    def no_network(*_args, **_kwargs):
        raise AssertionError("Archive replay must not contact a transport")

    monkeypatch.setattr("urllib.request.urlopen", no_network)
    restored = load_capture_archive(tmp_path, saved.stem, owner_scope="test-project")
    assert restored == original
    assert restored.raw_payload == response.raw
    assert restored.snapshot.captured_at == NOW
    assert restored.snapshot.records[0].origin == "synthetic"
    assert restored.snapshot.records[0].missing_reason == "source_value_missing"
    before = point_in_time_features(
        restored.snapshot, owner_scope="test-project", entity_id="earthquake-a",
        feature_names=("earthquake_magnitude",), allow_origins=("synthetic",),
        decision_time=NOW - timedelta(seconds=1),
    )[0]
    assert before.missing_reason == "no_point_in_time_data"


@pytest.mark.parametrize("field,value", [
    ("raw_payload_sha256", "0" * 64),
    ("snapshot_sha256", "0" * 64),
    ("code_bundle_sha256", {}),
    ("origin", "invented"),
    ("observed_at", "2026-11-05T12:00:00"),
    ("raw_payload_base64", "***not-base64***"),
    ("schema_version", "future"),
    ("source_url", "https://example.invalid/"),
])
def test_archive_replay_rejects_resealed_invalid_bindings(tmp_path, field, value):
    saved = save_capture_archive(capture(), tmp_path)
    document = json.loads(saved.read_bytes())
    document[field] = value
    raw = json.dumps(document).encode()
    altered_id = hashlib.sha256(raw).hexdigest()
    (tmp_path / (altered_id + ".json")).write_bytes(raw)
    with pytest.raises(ValueError):
        load_capture_archive(tmp_path, altered_id, owner_scope="test-project")


def test_archive_rejects_corruption_scope_escape_and_symlinks(tmp_path):
    saved = save_capture_archive(capture(), tmp_path)
    with pytest.raises(ValueError, match="owner_scope"):
        load_capture_archive(tmp_path, saved.stem, owner_scope="different-project")
    with pytest.raises(ValueError, match="identifier"):
        load_capture_archive(tmp_path, "../escape", owner_scope="test-project")
    saved.write_bytes(saved.read_bytes() + b" ")
    with pytest.raises(ValueError, match="hash"):
        load_capture_archive(tmp_path, saved.stem, owner_scope="test-project")
    saved.unlink()
    outside = tmp_path / "outside.json"
    outside.write_bytes(b"{}")
    saved.symlink_to(outside)
    with pytest.raises(OSError):
        load_capture_archive(tmp_path, saved.stem, owner_scope="test-project")


def test_archive_rejects_oversized_and_nonregular_objects(tmp_path):
    from az_live_data_harness.capture_archive import MAX_ARCHIVE_BYTES
    import os

    archive_id = "0" * 64
    target = tmp_path / (archive_id + ".json")
    with target.open("wb") as stream:
        stream.truncate(MAX_ARCHIVE_BYTES + 1)
    with pytest.raises(ValueError, match="bounded"):
        load_capture_archive(tmp_path, archive_id, owner_scope="test-project")
    target.unlink()
    os.mkfifo(target)
    with pytest.raises(ValueError, match="regular"):
        load_capture_archive(tmp_path, archive_id, owner_scope="test-project")


def test_archive_publication_failure_is_explicit_and_never_reports_success(monkeypatch, tmp_path):
    def fail(*_args, **_kwargs):
        raise OSError("archive fsync failed")

    monkeypatch.setattr("az_live_data_harness.capture_archive.publish_immutable", fail)
    with pytest.raises(OSError, match="fsync"):
        save_capture_archive(capture(), tmp_path)
    assert not list(tmp_path.iterdir())


def test_cli_archive_replay_is_explicit_and_never_fetches(monkeypatch, tmp_path, capsys):
    spec = importlib.util.spec_from_file_location("p40_archive_run", PRODUCT_ROOT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = capture()
    monkeypatch.setattr(
        "az_live_data_harness.temporal_adapter.fetch_earthquake_snapshot",
        lambda **_kwargs: original,
    )
    args = ["--temporal", "--owner-scope", "test-project", "--archive-dir", str(tmp_path)]
    assert module.main(args) == 0
    output = json.loads(capsys.readouterr().out)
    archive_id = Path(output["archive_path"]).stem
    assert output["mode"] == "live_capture"

    def no_fetch(**_kwargs):
        raise AssertionError("Explicit replay must not fetch")

    monkeypatch.setattr("az_live_data_harness.temporal_adapter.fetch_earthquake_snapshot", no_fetch)
    assert module.main(args + ["--replay-archive", archive_id]) == 0
    replay = json.loads(capsys.readouterr().out)
    assert replay["mode"] == "archive_replay"
    assert replay["snapshot"] == output["snapshot"]
    assert replay["receipt"]["promotion"]["eligible"] is False
    assert module.main(args + ["--replay-archive", "0" * 64]) == 1
    assert "error" in json.loads(capsys.readouterr().err)
    with pytest.raises(SystemExit) as error:
        module.main(["--temporal", "--owner-scope", "test-project", "--replay-archive", archive_id])
    assert error.value.code == 2
    with pytest.raises(SystemExit) as error:
        module.main(args + ["--replay-archive", ""])
    assert error.value.code == 2


@pytest.mark.parametrize("option", ["--archive-dir", "--snapshot-dir"])
@pytest.mark.parametrize("target", ["missing", "symlink", "file"])
def test_cli_validates_output_destination_before_live_fetch(
    monkeypatch, tmp_path, capsys, option, target,
):
    spec = importlib.util.spec_from_file_location("p40_archive_preflight_run", PRODUCT_ROOT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = tmp_path / "archive"
    if target == "symlink":
        path.symlink_to(tmp_path, target_is_directory=True)
    elif target == "file":
        path.write_text("not a directory", encoding="utf-8")

    def forbidden_fetch(**_kwargs):
        raise AssertionError("Invalid capture destination must fail before network access")

    monkeypatch.setattr(
        "az_live_data_harness.temporal_adapter.fetch_earthquake_snapshot", forbidden_fetch,
    )
    assert module.main([
        "--temporal", "--owner-scope", "test-project", option, str(path),
    ]) == 1
    output = capsys.readouterr()
    assert not output.out
    assert str(path) in json.loads(output.err)["error"]
