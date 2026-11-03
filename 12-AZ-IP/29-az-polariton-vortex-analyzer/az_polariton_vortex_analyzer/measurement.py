# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Strict ingestion of user-supplied tracked-feature exports, never raw images."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

from .pipeline import (
    C_S_CANONICAL,
    PumpProbeFrame,
    compare_to_prediction,
    extract_feature_velocity_curve,
)

SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_FRAMES = 20_000
FRAME_FIELDS = ("position_um", "timestamp_fs", "half_angle_deg")
EPISTEMIC_NOTE = (
    "User-supplied tracked-feature analysis; source and calibration are not independently "
    "verified. Comparison is descriptive, not evidence validating UM or any hardgate "
    "physics claim. Fit residuals are not calibrated measurement uncertainties."
)


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 1024:
        raise ValueError(f"{name} must be a nonblank string of at most 1024 characters")
    return value


def _unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON value: {value}")


def analyze_measurement(
    content: bytes,
    input_format: str,
    *,
    dataset_id: str | None = None,
    source: str | None = None,
    c_s: float = C_S_CANONICAL,
) -> dict:
    """Parse UTF-8 JSON/CSV and return a provenance-bearing analysis report."""
    if not isinstance(content, bytes) or not content or len(content) > MAX_INPUT_BYTES:
        raise ValueError(f"input must contain 1..{MAX_INPUT_BYTES} bytes")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("input must be UTF-8") from exc
    if input_format == "json":
        if dataset_id is not None or source is not None:
            raise ValueError("JSON metadata must be supplied in the document, not overridden")
        try:
            document = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
        except (json.JSONDecodeError, RecursionError) as exc:
            raise ValueError(f"invalid JSON: {exc}") from exc
        if not isinstance(document, dict) or set(document) != {"schema_version", "dataset_id", "source", "frames"}:
            raise ValueError("JSON requires exactly schema_version, dataset_id, source and frames")
        if type(document["schema_version"]) is not int or document["schema_version"] != SCHEMA_VERSION:
            raise ValueError(f"schema_version must be integer {SCHEMA_VERSION}")
        dataset_id, source, records = document["dataset_id"], document["source"], document["frames"]
    elif input_format == "csv":
        try:
            reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
            if reader.fieldnames is None or len(reader.fieldnames) != 3 or set(reader.fieldnames) != set(FRAME_FIELDS):
                raise ValueError(f"CSV header must contain exactly {', '.join(FRAME_FIELDS)}")
            records = []
            for row_number, row in enumerate(reader, start=2):
                if None in row or any(v is None or not v.strip() for v in row.values()):
                    raise ValueError(f"CSV row {row_number} must contain exactly three numeric values")
                try:
                    records.append({key: float(value) for key, value in row.items()})
                except ValueError as exc:
                    raise ValueError(f"CSV row {row_number} contains a nonnumeric value") from exc
                if len(records) > MAX_FRAMES:
                    raise ValueError(f"input must contain 2..{MAX_FRAMES} frames")
        except csv.Error as exc:
            raise ValueError(f"invalid CSV: {exc}") from exc
    else:
        raise ValueError("input format must be json or csv")
    dataset_id, source = _text(dataset_id, "dataset_id"), _text(source, "source")
    if not isinstance(records, list) or not 2 <= len(records) <= MAX_FRAMES:
        raise ValueError(f"frames must be a list of 2..{MAX_FRAMES} records")
    frames = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict) or set(record) != set(FRAME_FIELDS):
            raise ValueError(f"frame {index} requires exactly {', '.join(FRAME_FIELDS)}")
        frames.append(PumpProbeFrame(**record))
    measured = extract_feature_velocity_curve(frames)
    comparison = compare_to_prediction(measured, c_s=c_s)
    warnings = []
    if any(group["frame_count"] == 2 for group in measured.fit_diagnostics):
        warnings.append("Two-frame fits have no independent fit-quality degrees of freedom.")
    if comparison["crossing_status"] == "not_bracketed":
        warnings.append("No v/c=1 crossing observed; no crossing is extrapolated.")
    elif comparison["crossing_status"] == "multiple":
        warnings.append("Multiple v/c=1 crossings: do not interpret the first as a unique critical angle.")
    if any(v < 0 for v in measured.v_over_c):
        warnings.append("Negative velocities are retained; check the tracked-axis sign convention.")
    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_kind": "user_supplied_measurement",
        "analyzed_at_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "dataset_id": dataset_id,
            "source": source,
            "source_verification": "user_asserted_not_independently_verified",
            "input_format": input_format,
            "input_sha256": hashlib.sha256(content).hexdigest(),
            "input_bytes": len(content),
            "frame_count": len(frames),
        },
        "units": {"position": "um", "time": "fs", "half_angle": "deg", "velocity": "v/c"},
        "extraction_method": "ordinary_least_squares_position_vs_time_per_exact_angle",
        "c_um_per_fs": 0.299792458,
        "c_s": c_s,
        "measured": {
            "half_angles_deg": measured.half_angles_deg,
            "v_over_c": measured.v_over_c,
            "fit_diagnostics": measured.fit_diagnostics,
        },
        "comparison": comparison,
        "warnings": warnings,
        "epistemic_note": EPISTEMIC_NOTE,
    }


def analyze_measurement_file(path: str | Path, **kwargs) -> dict:
    """Infer format from .csv/.json; cap reads and never substitute demo data."""
    path = Path(path)
    input_format = path.suffix.lower().lstrip(".")
    if input_format not in {"csv", "json"}:
        raise ValueError("input file must have a .csv or .json extension")
    with path.open("rb") as stream:
        content = stream.read(MAX_INPUT_BYTES + 1)
    return analyze_measurement(content, input_format, **kwargs)
