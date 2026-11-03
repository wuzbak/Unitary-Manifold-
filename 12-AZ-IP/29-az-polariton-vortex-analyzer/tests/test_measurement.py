# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Contract and workflow tests with hand-constructed fixtures, not lab data."""

import hashlib
import http.client
import json
import subprocess
import sys
import threading
import uuid
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_polariton_vortex_analyzer import (
    FeatureVelocityCurve,
    PumpProbeFrame,
    analyze_measurement,
    analyze_measurement_file,
    compare_to_prediction,
    extract_feature_velocity_curve,
)
from az_polariton_vortex_analyzer.api import dispatch_api_request
from az_polariton_vortex_analyzer.app.server import build_server
from az_polariton_vortex_analyzer.measurement import MAX_INPUT_BYTES, MAX_FRAMES


@pytest.fixture
def document():
    return {
        "schema_version": 1,
        "dataset_id": "hand-constructed-test-fixture",
        "source": "unit test, not laboratory measurements",
        "frames": [
            {"position_um": x, "timestamp_fs": t, "half_angle_deg": 20}
            for t, x in [(3, 3), (0, 0), (2, 0), (1, 5)]
        ],
    }


@pytest.fixture
def input_path():
    # Keep test-created files inside Product 29 and remove them even on failure.
    path = PRODUCT_ROOT / f".measurement-test-{uuid.uuid4().hex}.json"
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)
        path.with_suffix(".csv").unlink(missing_ok=True)


def encode(document):
    return json.dumps(document).encode()


def test_json_analysis_uses_all_samples_and_preserves_provenance(document):
    raw = encode(document)
    result = analyze_measurement(raw, "json", c_s=0.5)
    assert result["provenance"]["input_sha256"] == hashlib.sha256(raw).hexdigest()
    assert result["provenance"]["input_bytes"] == len(raw)
    assert result["provenance"]["frame_count"] == 4
    assert result["provenance"]["dataset_id"] == document["dataset_id"]
    assert result["provenance"]["source"] == document["source"]
    assert "not_independently_verified" in result["provenance"]["source_verification"]
    assert result["measured"]["v_over_c"] == pytest.approx([0.4 / 0.299792458])
    fit = result["measured"]["fit_diagnostics"][0]
    assert fit["frame_count"] == 4
    assert fit["time_span_fs"] == 3
    assert fit["position_fit_rmse_um"] == pytest.approx(4.3 ** 0.5)
    residual = result["comparison"]["residuals"][0]
    assert result["comparison"]["rmse_v_over_c"] == pytest.approx(abs(residual))
    assert result["c_s"] == 0.5
    assert "not evidence validating UM" in result["epistemic_note"]
    json.dumps(result, allow_nan=False)


def test_csv_and_json_have_identical_derived_features(document):
    rows = ["timestamp_fs,half_angle_deg,position_um"]
    rows += [f'{f["timestamp_fs"]},{f["half_angle_deg"]},{f["position_um"]}' for f in document["frames"]]
    csv_result = analyze_measurement(
        ("\n".join(rows) + "\n").encode(), "csv",
        dataset_id=document["dataset_id"], source=document["source"],
    )
    json_result = analyze_measurement(encode(document), "json")
    assert csv_result["measured"] == json_result["measured"]
    assert csv_result["comparison"] == json_result["comparison"]


@pytest.mark.parametrize("key,value", [
    ("schema_version", 2), ("schema_version", True), ("schema_version", 1.0),
    ("dataset_id", ""), ("dataset_id", None), ("source", "  "),
    ("frames", []), ("frames", {}), ("frames", [None, None]),
    ("unexpected", "not permitted"),
])
def test_invalid_document_metadata_rejected(document, key, value):
    document[key] = value
    with pytest.raises(ValueError):
        analyze_measurement(encode(document), "json")


@pytest.mark.parametrize("key,value", [
    ("position_um", "1.0"), ("position_um", True), ("position_um", None),
    ("timestamp_fs", float("nan")), ("timestamp_fs", float("inf")),
    ("position_um", float("-inf")), ("half_angle_deg", 0), ("half_angle_deg", -1),
    ("half_angle_deg", 90), ("half_angle_deg", 100), ("unknown", 1),
])
def test_invalid_frame_rejected(document, key, value):
    document["frames"][0][key] = value
    with pytest.raises(ValueError):
        analyze_measurement(encode(document), "json")


def test_missing_frame_field_rejected(document):
    del document["frames"][0]["position_um"]
    with pytest.raises(ValueError, match="requires exactly"):
        analyze_measurement(encode(document), "json")


@pytest.mark.parametrize("raw", [
    b"", b"\xff", b"[]", b"{bad", b'{"a":1,"a":2}',
    b'{"frames":[{"position_um":1,"position_um":2}]}',
    b'{"schema_version":1,"dataset_id":"x","source":"y","frames":[],"c_s":0.5}',
    b" " * (MAX_INPUT_BYTES + 1),
])
def test_malformed_json_rejected(raw):
    with pytest.raises(ValueError):
        analyze_measurement(raw, "json")


def test_too_many_frames_rejected(document):
    document["frames"] = [document["frames"][0]] * (MAX_FRAMES + 1)
    with pytest.raises(ValueError, match="frames"):
        analyze_measurement(encode(document), "json")


@pytest.mark.parametrize("raw", [
    b"position_um,timestamp_fs\n1,2\n2,3",
    b"position_um,timestamp_fs,half_angle_deg\n1,2,20,extra\n2,3,20",
    b"position_um,timestamp_fs,half_angle_deg\n1,,20\n2,3,20",
    b"position_um,timestamp_fs,half_angle_deg\n1,2\n2,3,20",
    b"position_um,timestamp_fs,half_angle_deg\nword,2,20\n2,3,20",
    b"position_um,timestamp_fs,half_angle_deg\nnan,2,20\n2,3,20",
    b"position_um,position_um,half_angle_deg\n1,2,20\n2,3,20",
])
def test_invalid_csv_rejected(raw):
    with pytest.raises(ValueError):
        analyze_measurement(raw, "csv", dataset_id="test", source="fixture")


def test_csv_requires_metadata_and_json_forbids_overrides(document):
    with pytest.raises(ValueError, match="dataset_id"):
        analyze_measurement(b"position_um,timestamp_fs,half_angle_deg\n0,0,20\n1,1,20", "csv")
    with pytest.raises(ValueError, match="not overridden"):
        analyze_measurement(encode(document), "json", dataset_id="override")
    with pytest.raises(ValueError, match="format"):
        analyze_measurement(encode(document), "yaml")


def test_invalid_groups_never_silently_discarded():
    with pytest.raises(ValueError, match="duplicate timestamps"):
        extract_feature_velocity_curve([PumpProbeFrame(0, 0, 10), PumpProbeFrame(1, 0, 10)])
    with pytest.raises(ValueError, match="requires at least two"):
        extract_feature_velocity_curve([
            PumpProbeFrame(0, 0, 10), PumpProbeFrame(1, 1, 10), PumpProbeFrame(1, 0, 10.0000001)
        ])


@pytest.mark.parametrize("c_s", [0, 1, -0.5, 2, float("nan"), float("inf"), True])
def test_invalid_model_parameter_rejected(document, c_s):
    with pytest.raises(ValueError, match="c_s"):
        analyze_measurement(encode(document), "json", c_s=c_s)


@pytest.mark.parametrize("angles,speeds", [
    ([], []), ([10], []), ([20, 10], [1, 2]), ([10, 10], [1, 2]),
    ([0], [1]), ([10], [float("nan")]),
])
def test_direct_comparison_validates_curve(angles, speeds):
    with pytest.raises(ValueError):
        compare_to_prediction(FeatureVelocityCurve(angles, speeds))


def test_unrepresentable_numerical_ranges_fail_explicitly():
    with pytest.raises(ValueError):
        compare_to_prediction(FeatureVelocityCurve([5e-324], [1]))
    with pytest.raises(ValueError, match="unrepresentable fit"):
        extract_feature_velocity_curve([
            PumpProbeFrame(-1e308, 0, 20), PumpProbeFrame(1e308, 1, 20)
        ])


def test_crossings_and_residual_metrics():
    result = compare_to_prediction(FeatureVelocityCurve([10, 20, 30], [2, 0, 2]))
    assert result["measured_crossing_angles_deg"] == [15, 25]
    assert result["crossing_status"] == "multiple"
    residuals = result["residuals"]
    assert result["rmse_v_over_c"] == pytest.approx((sum(r * r for r in residuals) / 3) ** 0.5)
    assert result["mean_abs_residual"] == pytest.approx(sum(abs(r) for r in residuals) / 3)
    exact = compare_to_prediction(FeatureVelocityCurve([20], [1]))
    assert exact["measured_crossing_angle_deg"] == 20
    outside = compare_to_prediction(FeatureVelocityCurve([10, 20], [0.2, 0.3]))
    assert outside["measured_crossing_angle_deg"] is None


def test_sign_preserved_and_warnings(document):
    document["frames"] = [
        {"position_um": x, "timestamp_fs": t, "half_angle_deg": 20}
        for t, x in [(0, 0), (1, -1)]
    ]
    result = analyze_measurement(encode(document), "json")
    assert result["measured"]["v_over_c"][0] < 0
    assert any("Negative" in w for w in result["warnings"])
    assert any("Two-frame" in w for w in result["warnings"])
    assert any("No v/c=1" in w for w in result["warnings"])


def test_file_and_cli_end_to_end(document, input_path):
    raw = encode(document)
    input_path.write_bytes(raw)
    result = analyze_measurement_file(input_path)
    command = [sys.executable, str(PRODUCT_ROOT / "run.py"), "analyze", str(input_path)]
    cli = subprocess.run(command, capture_output=True, text=True, check=False)
    assert cli.returncode == 0, cli.stderr
    report = json.loads(cli.stdout)
    assert report["measured"] == result["measured"]
    assert report["provenance"]["input_sha256"] == hashlib.sha256(raw).hexdigest()
    input_path.write_text('{"frames":[]}')
    invalid = subprocess.run(command, capture_output=True, text=True, check=False)
    assert invalid.returncode == 2
    assert invalid.stdout == ""
    assert "failed" in invalid.stderr
    input_path.unlink()
    missing = subprocess.run(command, capture_output=True, text=True, check=False)
    assert missing.returncode == 2
    assert missing.stdout == ""


def test_csv_cli_requires_metadata(input_path):
    path = input_path.with_suffix(".csv")
    path.write_text("position_um,timestamp_fs,half_angle_deg\n0,0,20\n1,1,20\n")
    command = [sys.executable, str(PRODUCT_ROOT / "run.py"), "analyze", str(path)]
    missing = subprocess.run(command, capture_output=True, text=True, check=False)
    assert missing.returncode == 2
    valid = subprocess.run(command + ["--dataset-id", "fixture", "--source", "unit-test"],
                           capture_output=True, text=True, check=False)
    assert valid.returncode == 0, valid.stderr
    assert json.loads(valid.stdout)["provenance"]["input_format"] == "csv"


@pytest.fixture
def live_server():
    server = build_server(port=0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield server.server_address
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request(address, method, path, body=None, headers=None):
    connection = http.client.HTTPConnection(*address, timeout=5)
    try:
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        return response.status, json.loads(response.read())
    finally:
        connection.close()


def test_live_measurement_http_end_to_end(document, live_server):
    status, health = request(live_server, "GET", "/api/status")
    assert status == 200 and health["product"] == "AZ Polariton Vortex Analyzer"
    raw = encode(document)
    status, result = request(live_server, "POST", "/api/analyze?c_s=0.5", raw,
                             {"Content-Type": "application/json"})
    assert status == 200
    assert result["measured"] == analyze_measurement(raw, "json")["measured"]
    assert result["provenance"]["input_sha256"] == hashlib.sha256(raw).hexdigest()
    assert result["c_s"] == 0.5
    assert "not evidence validating UM" in result["epistemic_note"]


@pytest.mark.parametrize("method,path,body,headers,expected", [
    ("GET", "/api/analyze", None, {}, 405),
    ("POST", "/api/missing", b"{}", {}, 404),
    ("POST", "/api/prediction", b"{}", {}, 405),
    ("POST", "/api/analyze", b"{}", {"Content-Type": "text/plain"}, 415),
    ("POST", "/api/analyze", b"not-json", {"Content-Type": "application/json"}, 400),
    ("POST", "/api/analyze?c_s=nan", b"{}", {"Content-Type": "application/json"}, 400),
    ("POST", "/api/analyze", b"", {"Content-Type": "application/json"}, 413),
    ("POST", "/api/analyze", b"{}", {"Content-Type": "application/json", "Content-Length": "-1"}, 400),
    ("POST", "/api/analyze", b"{}", {"Content-Type": "application/json", "Content-Length": str(MAX_INPUT_BYTES + 1)}, 413),
    ("POST", "/api/analyze", b"{}", {"Content-Type": "application/json", "Transfer-Encoding": "chunked"}, 400),
    ("GET", "/api/prediction?c_s=nan", None, {}, 400),
    ("POST", "/api/analyze?c_s=0.3&c_s=0.5", b"{}", {"Content-Type": "application/json"}, 400),
])
def test_http_errors_never_return_success(live_server, method, path, body, headers, expected):
    status, result = request(live_server, method, path, body, headers)
    assert status == expected
    assert "error" in result
    assert "measured" not in result


def test_dispatch_accepts_only_post_and_documented_parameters(document):
    with pytest.raises(ValueError, match="POST"):
        dispatch_api_request("/api/analyze", {})
    with pytest.raises(ValueError, match="only"):
        dispatch_api_request("/api/analyze", {"unused": ["1"]}, method="POST", body=encode(document))
