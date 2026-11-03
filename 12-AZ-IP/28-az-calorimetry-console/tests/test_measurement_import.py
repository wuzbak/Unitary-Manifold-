# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Regression coverage for instrument-export validation and provenance."""

import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from uuid import uuid4

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT))

from az_calorimetry_console import import_measurements

SPEC = importlib.util.spec_from_file_location("calorimetry_cli", PRODUCT_ROOT / "run.py")
CLI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLI)

VALID_CSV = "timestamp_s,power_in_w,power_out_w\n0,100,100\n1,100,100\n10,200,400\n"
VALID_METADATA = {
    "schema_version": 1,
    "run_id": "lab-run-001",
    "instrument_id": "calorimeter-17",
    "calibration_id": "certificate-2026-08",
    "acquired_at": "2026-08-01T12:00:00+00:00",
    "source_reference": "lab-notebook-42/page-8",
    "units": {"timestamp_s": "s", "power_in_w": "W", "power_out_w": "W"},
}


@pytest.fixture
def files():
    workspace = PRODUCT_ROOT / (".measurement-test-" + uuid4().hex)
    workspace.mkdir()
    csv_path = workspace / "instrument.csv"
    metadata_path = workspace / "metadata.json"
    csv_path.write_text(VALID_CSV, encoding="utf-8")
    metadata_path.write_text(json.dumps(VALID_METADATA), encoding="utf-8")
    try:
        yield csv_path, metadata_path, workspace / "artifact.json"
    finally:
        shutil.rmtree(workspace)


def test_irregular_sampling_uses_energy_ratio_not_sample_mean(files):
    report = import_measurements(*files[:2])
    summary = report["summary"]
    assert summary["energy_in_j"] == pytest.approx(1450)
    assert summary["energy_out_j"] == pytest.approx(2350)
    assert summary["energy_cop"] == pytest.approx(2350 / 1450)
    assert summary["energy_cop"] != pytest.approx((1 + 1 + 2) / 3)
    assert summary["duration_s"] == 10
    assert summary["threshold_screen"] == "ABOVE_THRESHOLD"
    assert "verdict" not in summary
    assert report["metadata"] == VALID_METADATA
    assert [row["source_line"] for row in report["samples"]] == [2, 3, 4]
    assert report["samples"][2]["power_out_w"] == 400
    for key, path in zip(("csv", "metadata"), files[:2]):
        assert report["provenance"][key] == {
            "filename": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    assert any("not evidence" in item for item in report["limitations"])
    json.dumps(report, allow_nan=False)


@pytest.mark.parametrize("output,screen", [(101, "NOT_ABOVE_THRESHOLD"), (102, "ABOVE_THRESHOLD"), (0, "NOT_ABOVE_THRESHOLD")])
def test_threshold_is_strict_and_zero_output_is_valid(files, output, screen):
    files[0].write_text(f"timestamp_s,power_in_w,power_out_w\n0,100,{output}\n2,100,{output}\n")
    assert import_measurements(*files[:2])["summary"]["threshold_screen"] == screen


@pytest.mark.parametrize("body", [
    "",
    "timestamp_s,power_in_w,power_out_w\n",
    "timestamp_s,power_in_w,power_out_w\n0,1,1\n",
    "timestamp_ms,power_in_w,power_out_w\n0,1,1\n1,1,1\n",
    "timestamp_s,power_in_w,power_in_w\n0,1,1\n1,1,1\n",
    "power_in_w,timestamp_s,power_out_w\n1,0,1\n1,1,1\n",
    "timestamp_s,power_in_w,power_out_w,extra\n0,1,1,0\n1,1,1,0\n",
    "timestamp_s,power_in_w,power_out_w\n0,1,1\n\n1,1,1\n",
    "timestamp_s,power_in_w,power_out_w\n0,1\n1,1,1\n",
    "timestamp_s,power_in_w,power_out_w\n0,1,1,extra\n1,1,1\n",
    'timestamp_s,power_in_w,power_out_w\n0,1,1\n1,1,"1\n',
])
def test_rejects_malformed_csv_without_artifact(files, body):
    files[0].write_text(body)
    with pytest.raises(ValueError):
        import_measurements(*files[:2])
    assert not files[2].exists()


@pytest.mark.parametrize("row", [
    "-1,1,1", "0,1,1", "1,0,1", "1,-1,1", "1,1,-1", "1,,1",
    "1,watts,1", "nan,1,1", "inf,1,1", "1,nan,1", "1,inf,1",
    "1,1,nan", "1,1,-inf", "1,5e-324,1e308", "1e308,1e308,1e308",
])
def test_rejects_bad_sample_with_line_number_or_numeric_range(files, row):
    files[0].write_text("timestamp_s,power_in_w,power_out_w\n0,1,1\n" + row + "\n")
    with pytest.raises(ValueError, match="CSV line 3|numeric range"):
        import_measurements(*files[:2])


@pytest.mark.parametrize("change", [
    {"schema_version": True}, {"schema_version": 2}, {"schema_version": "1"},
    {"run_id": ""}, {"instrument_id": None}, {"calibration_id": " "},
    {"source_reference": 1}, {"acquired_at": "2026-08-01"},
    {"acquired_at": "not-a-date"}, {"acquired_at": "2026-08-01T12:00:00"},
    {"units": {"timestamp_s": "ms", "power_in_w": "W", "power_out_w": "W"}},
    {"unexpected": "value"},
])
def test_rejects_invalid_metadata(files, change):
    files[1].write_text(json.dumps({**VALID_METADATA, **change}))
    with pytest.raises(ValueError):
        import_measurements(*files[:2])


@pytest.mark.parametrize("raw", [
    "[]", "null", "{}", "{", '{"schema_version": 1, "schema_version": 1}',
    '{"x": NaN}', '{"x": Infinity}',
])
def test_rejects_missing_duplicate_or_nonstandard_metadata(files, raw):
    files[1].write_text(raw)
    with pytest.raises(ValueError):
        import_measurements(*files[:2])


def test_bom_crlf_and_quoted_values_preserve_raw_hash(files):
    files[0].write_bytes(b'\xef\xbb\xbftimestamp_s,power_in_w,power_out_w\r\n"3","100","100"\r\n"5","100","100"\r\n')
    report = import_measurements(*files[:2])
    assert report["summary"]["duration_s"] == 2
    assert report["provenance"]["csv"]["sha256"] == hashlib.sha256(files[0].read_bytes()).hexdigest()


def test_hash_changes_when_measurement_bytes_change(files):
    first = import_measurements(*files[:2])
    files[0].write_text(VALID_CSV.replace("400", "401"))
    second = import_measurements(*files[:2])
    assert first["provenance"]["csv"]["sha256"] != second["provenance"]["csv"]["sha256"]
    assert first["provenance"]["metadata"] == second["provenance"]["metadata"]


def test_cli_persists_complete_artifact_and_refuses_overwrite(files, capsys):
    args = ["import-run", "--csv", str(files[0]), "--metadata", str(files[1]), "--output", str(files[2])]
    assert CLI.main(args) == 0
    assert json.loads(files[2].read_text()) == import_measurements(*files[:2])
    original = files[2].read_bytes()
    with pytest.raises(SystemExit) as exc:
        CLI.main(args)
    assert exc.value.code == 2
    assert files[2].read_bytes() == original
    assert "import-run:" in capsys.readouterr().err
    assert not list(files[2].parent.glob("*.pending"))


@pytest.mark.parametrize("operation", ["fsync", "link"])
def test_cli_output_failure_cleans_staging_and_publishes_nothing(files, monkeypatch, operation):
    def fail(*args):
        raise OSError("injected filesystem failure")

    monkeypatch.setattr(CLI.os, operation, fail)
    with pytest.raises(SystemExit) as exc:
        CLI.main(["import-run", "--csv", str(files[0]), "--metadata", str(files[1]), "--output", str(files[2])])
    assert exc.value.code == 2
    assert not files[2].exists()
    assert not list(files[2].parent.glob("*.pending"))


@pytest.mark.parametrize("source_index", [0, 1])
def test_cli_cannot_overwrite_either_source(files, source_index):
    original = files[source_index].read_bytes()
    with pytest.raises(SystemExit) as exc:
        CLI.main([
            "import-run", "--csv", str(files[0]), "--metadata", str(files[1]),
            "--output", str(files[source_index]),
        ])
    assert exc.value.code == 2
    assert files[source_index].read_bytes() == original


@pytest.mark.parametrize("failure", ["missing_csv", "bad_last_row", "invalid_utf8"])
def test_cli_failure_creates_no_partial_artifact(files, failure, capsys):
    if failure == "missing_csv":
        files[0].unlink()
    elif failure == "bad_last_row":
        files[0].write_text(VALID_CSV + "11,1,nan\n")
    else:
        files[0].write_bytes(b"\xff")
    with pytest.raises(SystemExit) as exc:
        CLI.main(["import-run", "--csv", str(files[0]), "--metadata", str(files[1]), "--output", str(files[2])])
    assert exc.value.code == 2
    assert not files[2].exists()
    assert "import-run:" in capsys.readouterr().err
