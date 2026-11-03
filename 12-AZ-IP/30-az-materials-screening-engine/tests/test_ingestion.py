# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Synthetic contract fixtures, not measured material data."""

import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_materials_screening_engine import MaterialCandidate, screen_candidate, screen_file
from az_materials_screening_engine.ingestion import MAX_INPUT_BYTES, MAX_RECORDS, REQUIRED_FIELDS


@pytest.fixture
def workspace():
    directory = PRODUCT_ROOT / "tests" / f".ingestion-test-{uuid4().hex}"
    directory.mkdir()
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


@pytest.fixture
def record():
    return {
        "name": "synthetic contract fixture",
        "alpha": 0.5,
        "omega_lo_mev": 100.0,
        "m_band_me": 0.2,
        "epsilon_r": 3.0,
        "source": "test fixture only (not a publication)",
        "source_record_id": "test-001",
        "conditions": "synthetic scalar values for software tests only",
    }


def write_records(workspace, records, file_format="json"):
    path = workspace / f"records.{file_format}"
    if file_format == "json":
        path.write_text(json.dumps(records), encoding="utf-8")
    else:
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=REQUIRED_FIELDS)
            writer.writeheader()
            writer.writerows(records)
    return path


@pytest.mark.parametrize("file_format", ["csv", "json"])
def test_report_preserves_provenance_inputs_and_ranking(workspace, record, file_format):
    second = dict(record, source_record_id="test-002", alpha=0.1)
    path = write_records(workspace, [record, second], file_format)
    report = screen_file(path)
    assert report["input"] == {
        "filename": path.name,
        "format": file_format,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "record_count": 2,
    }
    results = report["candidates"]
    assert [r["input_record"] for r in results] == [2, 1]
    assert [r["rank"] for r in results] == [1, 2]
    result = results[1]
    expected = screen_candidate(MaterialCandidate(record["name"], 0.5, 100, 0.2, 3))
    for key, value in expected.items():
        assert result[key] == value
    assert result["provenance"] == {key: record[key] for key in ("source", "source_record_id", "conditions")}
    assert result["properties"]["omega_lo_mev"] == 100
    assert result["properties"]["mu_r"] == 1
    assert result["assumptions"] == ["mu_r omitted; assumed 1.0"]
    assert "not experimental validation" in report["screening_notice"]
    assert "not independently verified" in report["provenance_status"]
    json.dumps(report, allow_nan=False)


def test_explicit_mu_and_stable_ties(workspace, record):
    first = dict(record, mu_r=-1, epsilon_r=-2)
    second = dict(first, source_record_id="test-002")
    result = screen_file(write_records(workspace, [first, second]))["candidates"]
    assert [r["input_record"] for r in result] == [1, 2]
    assert result[0]["negative_phi_index"] < 0
    assert result[0]["assumptions"] == []


def test_outside_weak_coupling_is_reported_not_silently_validated(workspace, record):
    record["alpha"] = 6
    result = screen_file(write_records(workspace, [record]))["candidates"][0]
    assert "outside the stated weak-coupling range" in result["warnings"][0]


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_missing_fields_rejected(workspace, record, field):
    del record[field]
    with pytest.raises(ValueError, match="missing fields"):
        screen_file(write_records(workspace, [record]))


@pytest.mark.parametrize("field", ["name", "source", "source_record_id", "conditions"])
@pytest.mark.parametrize("value", ["", "  ", None, 42])
def test_metadata_requires_nonblank_text(workspace, record, field, value):
    record[field] = value
    with pytest.raises(ValueError, match=field):
        screen_file(write_records(workspace, [record]))


@pytest.mark.parametrize("field", ["alpha", "omega_lo_mev", "m_band_me", "epsilon_r", "mu_r"])
@pytest.mark.parametrize("value", [True, None, "1.2", float("nan"), float("inf"), float("-inf")])
def test_invalid_json_property_types_or_nonfinite_rejected(workspace, record, field, value):
    record[field] = value
    with pytest.raises(ValueError):
        screen_file(write_records(workspace, [record]))


@pytest.mark.parametrize("field", ["alpha", "omega_lo_mev", "m_band_me"])
@pytest.mark.parametrize("value", [0, -0.1])
def test_positive_property_domain(workspace, record, field, value):
    record[field] = value
    with pytest.raises(ValueError, match=field):
        screen_file(write_records(workspace, [record]))


@pytest.mark.parametrize("value", ["", "unknown", "NaN", "Infinity", "-Infinity"])
def test_invalid_csv_numbers(workspace, record, value):
    record["alpha"] = value
    with pytest.raises(ValueError, match="alpha"):
        screen_file(write_records(workspace, [record], "csv"))


@pytest.mark.parametrize("records", [[], {}, [None], [1]])
def test_empty_or_wrong_json_structure(workspace, records):
    with pytest.raises(ValueError):
        screen_file(write_records(workspace, records))


def test_unknown_fields_and_duplicate_identity_rejected(workspace, record):
    with pytest.raises(ValueError, match="unknown fields"):
        screen_file(write_records(workspace, [dict(record, omega_lo_ev=0.1)]))
    with pytest.raises(ValueError, match=r"record 2: duplicate"):
        screen_file(write_records(workspace, [record, dict(record)]))
    with pytest.raises(ValueError, match="duplicate"):
        screen_file(write_records(workspace, [record, dict(record, source_record_id=" test-001 ")]))


@pytest.mark.parametrize("text", [
    "",
    '{"incomplete":',
    '[{"name": "first", "name": "duplicate"}]',
])
def test_malformed_or_duplicate_json_keys_rejected(workspace, text):
    path = workspace / "records.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        screen_file(path)


@pytest.mark.parametrize("text", [
    "",
    ",".join(REQUIRED_FIELDS),
    ",".join((*REQUIRED_FIELDS, "alpha")) + "\n",
    ",".join((*REQUIRED_FIELDS, "extra")) + "\n",
    ",".join(REQUIRED_FIELDS) + "\nshort,row\n",
    ",".join(REQUIRED_FIELDS) + "\n" + ",".join(["x"] * (len(REQUIRED_FIELDS) + 1)),
    ",".join(REQUIRED_FIELDS) + '\n"unclosed',
    ",".join(REQUIRED_FIELDS) + "\n\n",
])
def test_malformed_csv_rejected(workspace, text):
    path = workspace / "records.csv"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        screen_file(path)


def test_csv_quoted_provenance_and_utf8_bom(workspace, record):
    record["conditions"] = '298 K, scalar test\nquoted "condition"; not measured'
    path = write_records(workspace, [record], "csv")
    path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
    report = screen_file(path)
    assert report["candidates"][0]["provenance"]["conditions"] == record["conditions"]


def test_unsupported_extension_and_bad_encoding(workspace):
    with pytest.raises(ValueError, match="extension"):
        screen_file(workspace / "records.txt")
    path = workspace / "records.json"
    path.write_bytes(b"\xff")
    with pytest.raises(ValueError, match="invalid json"):
        screen_file(path)
    with pytest.raises(OSError):
        screen_file(workspace / "missing.json")


def test_oversized_input_rejected(workspace):
    path = workspace / "oversized.json"
    path.write_bytes(b" " * (MAX_INPUT_BYTES + 1))
    with pytest.raises(ValueError, match="byte limit"):
        screen_file(path)


def test_record_count_is_bounded(workspace):
    path = workspace / "too-many.json"
    path.write_text("[" + ",".join(["{}"] * (MAX_RECORDS + 1)) + "]", encoding="utf-8")
    with pytest.raises(ValueError, match="candidate records"):
        screen_file(path)


@pytest.mark.parametrize("properties", [
    {"alpha": 1e308, "omega_lo_mev": 1e308},
    {"omega_lo_mev": 5e-324},
    {"epsilon_r": 1e308, "mu_r": 1e308},
    {"epsilon_r": 5e-324, "mu_r": 5e-324},
    {"alpha": 5e-324, "omega_lo_mev": 5e-324},
])
def test_numerical_overflow_or_underflow_fails_closed(workspace, record, properties):
    record.update(properties)
    with pytest.raises(ValueError, match="record 1:"):
        screen_file(write_records(workspace, [record]))


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(PRODUCT_ROOT / "run.py"), *map(str, args)],
        cwd=PRODUCT_ROOT, capture_output=True, text=True, timeout=30,
    )


@pytest.mark.parametrize("file_format", ["json", "csv"])
def test_cli_end_to_end_json_stdout(workspace, record, file_format):
    path = write_records(workspace, [record], file_format)
    completed = run_cli("screen", path)
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert json.loads(completed.stdout) == screen_file(path)


def test_cli_invalid_later_record_has_no_partial_report(workspace, record):
    invalid = dict(record, source_record_id="test-002", alpha=-1)
    completed = run_cli("screen", write_records(workspace, [record, invalid]))
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "record 2:" in completed.stderr
    assert "demo" not in completed.stderr.lower()


def test_cli_missing_file_has_no_success_output(workspace):
    completed = run_cli("screen", workspace / "missing.json")
    assert completed.returncode == 2
    assert completed.stdout == ""
    assert "screen:" in completed.stderr


def test_original_no_argument_demo_still_explicit():
    completed = run_cli()
    assert completed.returncode == 0
    assert "Demo candidates only" in completed.stdout
