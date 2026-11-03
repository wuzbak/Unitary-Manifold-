# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Strict, provenance-preserving ingestion of user-supplied property records."""

from __future__ import annotations

import csv
from dataclasses import asdict
import hashlib
import io
import json
from pathlib import Path

from .screening import MaterialCandidate, SCREENING_NOTICE, screen_candidate

PROPERTY_FIELDS = ("alpha", "omega_lo_mev", "m_band_me", "epsilon_r", "mu_r")
PROVENANCE_FIELDS = ("source", "source_record_id", "conditions")
REQUIRED_FIELDS = ("name", *PROPERTY_FIELDS[:-1], *PROVENANCE_FIELDS)
ALLOWED_FIELDS = {*REQUIRED_FIELDS, "mu_r"}
MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_RECORDS = 10_000


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonstandard JSON numeric constant: {value}")


def _parse_records(text: str, file_format: str) -> list:
    if file_format == "json":
        records = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
        if not isinstance(records, list):
            raise ValueError("JSON input must be an array of candidate record objects")
        return records
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    header = next(reader, None)
    if not header:
        raise ValueError("CSV input requires a header")
    if len(set(header)) != len(header):
        raise ValueError("duplicate CSV headers")
    _validate_fields(set(header), "CSV header")
    records = []
    for row in reader:
        if len(row) != len(header):
            raise ValueError(f"CSV line {reader.line_num}: expected {len(header)} fields, got {len(row)}")
        records.append(dict(zip(header, row)))
    return records


def _validate_fields(fields: set, location: str) -> None:
    missing = set(REQUIRED_FIELDS) - fields
    unknown = fields - ALLOWED_FIELDS
    if missing or unknown:
        raise ValueError(
            f"{location}: missing fields {sorted(missing)}; unknown fields {sorted(unknown)}"
        )


def screen_file(path: str | Path) -> dict:
    """Validate an entire CSV/JSON batch, then return an auditable screening report.

    Provenance is supplied by the caller, retained verbatim, and never verified
    remotely. No records are skipped and no replacement properties are generated.
    """
    path = Path(path)
    file_format = path.suffix.lower().lstrip(".")
    if file_format not in ("csv", "json"):
        raise ValueError("input filename must have a .csv or .json extension")
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds the {MAX_INPUT_BYTES}-byte limit")
    try:
        records = _parse_records(raw.decode("utf-8-sig"), file_format)
    except (UnicodeError, csv.Error, RecursionError) as exc:
        raise ValueError(f"invalid {file_format} input: {exc}") from exc
    if not 1 <= len(records) <= MAX_RECORDS:
        raise ValueError(f"input must contain 1..{MAX_RECORDS} candidate records")

    results = []
    identities = set()
    for index, record in enumerate(records, start=1):
        try:
            if not isinstance(record, dict):
                raise ValueError("expected a candidate record object")
            _validate_fields(set(record), "record")
            for field in ("name", *PROVENANCE_FIELDS):
                if not isinstance(record[field], str) or not record[field].strip():
                    raise ValueError(f"{field} must be a nonblank string")
            identity = (record["source"].strip(), record["source_record_id"].strip())
            if identity in identities:
                raise ValueError("duplicate (source, source_record_id)")
            identities.add(identity)
            properties = {}
            for field in PROPERTY_FIELDS:
                if field == "mu_r" and field not in record:
                    properties[field] = 1.0
                    continue
                value = record[field]
                if file_format == "csv":
                    try:
                        value = float(value)
                    except (ValueError, OverflowError) as exc:
                        raise ValueError(f"{field} must be numeric") from exc
                properties[field] = value
            candidate = MaterialCandidate(record["name"], **properties)
            result = screen_candidate(candidate)
            result.update({
                "input_record": index,
                "properties": asdict(candidate),
                "provenance": {field: record[field] for field in PROVENANCE_FIELDS},
                "assumptions": ["mu_r omitted; assumed 1.0"] if "mu_r" not in record else [],
            })
            results.append(result)
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError(f"record {index}: {exc}") from exc

    results.sort(key=lambda result: result["alpha_divergence_from_um"], reverse=True)
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank
    return {
        "schema_version": "1.0",
        "screening_notice": SCREENING_NOTICE,
        "provenance_status": "user-supplied; sources and property accuracy not independently verified",
        "ranking": "absolute alpha divergence from canonical UM value, descending; ties preserve input order",
        "formula_notes": [
            "Binding energy and mass use weak-coupling formulas (alpha < 6).",
            "Radius uses canonical UM coupling, not the supplied candidate alpha.",
            "Critical angle is a fixed framework value, not material-specific evidence.",
            "Scalar real dielectric/magnetic inputs do not model dispersion, loss, or anisotropy.",
        ],
        "input": {
            "filename": path.name,
            "format": file_format,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "record_count": len(records),
        },
        "candidates": results,
    }
