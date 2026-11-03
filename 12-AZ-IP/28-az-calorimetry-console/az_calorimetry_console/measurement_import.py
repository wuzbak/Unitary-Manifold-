# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Validated instrument-export ingestion; no inference of physical excess heat."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from datetime import datetime
from pathlib import Path

from .cop_tracker import DEFAULT_COP_THRESHOLD

CSV_COLUMNS = ("timestamp_s", "power_in_w", "power_out_w")
METADATA_KEYS = {
    "schema_version", "run_id", "instrument_id", "calibration_id",
    "acquired_at", "source_reference", "units",
}
UNITS = {"timestamp_s": "s", "power_in_w": "W", "power_out_w": "W"}


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate metadata key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant: {value}")


def _validate_metadata(raw: bytes) -> dict:
    metadata = json.loads(
        raw.decode("utf-8-sig"),
        object_pairs_hook=_unique_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(metadata, dict) or set(metadata) != METADATA_KEYS:
        raise ValueError(f"metadata requires exactly these keys: {sorted(METADATA_KEYS)}")
    if type(metadata["schema_version"]) is not int or metadata["schema_version"] != 1:
        raise ValueError("metadata schema_version must be integer 1")
    for key in METADATA_KEYS - {"schema_version", "units"}:
        if not isinstance(metadata[key], str) or not metadata[key].strip():
            raise ValueError(f"metadata {key} must be a nonempty string")
    if metadata["units"] != UNITS:
        raise ValueError(f"metadata units must be exactly {UNITS}; convert explicitly before import")
    try:
        acquired = datetime.fromisoformat(metadata["acquired_at"])
    except ValueError as exc:
        raise ValueError("acquired_at must be an ISO-8601 datetime with timezone") from exc
    if acquired.utcoffset() is None:
        raise ValueError("acquired_at must include a timezone")
    return metadata


def import_measurements(csv_path: str | Path, metadata_path: str | Path) -> dict:
    """Read both files once, validate the entire run, then return a JSON-safe artifact.

    Timestamps are elapsed seconds from acquisition start. Powers must already
    be calibrated watts. Calibration identifiers are declarations, not verified
    certificates. No partial run is returned on any malformed sample.
    """
    csv_path, metadata_path = Path(csv_path), Path(metadata_path)
    raw_csv, raw_metadata = csv_path.read_bytes(), metadata_path.read_bytes()
    metadata = _validate_metadata(raw_metadata)
    reader = csv.reader(io.StringIO(raw_csv.decode("utf-8-sig"), newline=""), strict=True)
    samples = []
    try:
        if next(reader, None) != list(CSV_COLUMNS):
            raise ValueError(f"CSV header must be exactly {','.join(CSV_COLUMNS)}")
        for row in reader:
            line = reader.line_num
            if len(row) != len(CSV_COLUMNS):
                raise ValueError(f"CSV line {line}: expected three fields (blank rows are invalid)")
            try:
                values = [float(value) for value in row]
            except ValueError as exc:
                raise ValueError(f"CSV line {line}: all fields must be numeric") from exc
            timestamp, power_in, power_out = values
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"CSV line {line}: all fields must be finite")
            if timestamp < 0 or (samples and timestamp <= samples[-1]["timestamp_s"]):
                raise ValueError(f"CSV line {line}: timestamps must be nonnegative and strictly increasing")
            if power_in <= 0 or power_out < 0:
                raise ValueError(f"CSV line {line}: input power must be positive; output power nonnegative")
            if not math.isfinite(power_out / power_in):
                raise ValueError(f"CSV line {line}: COP exceeds numeric range")
            samples.append({"source_line": line, **dict(zip(CSV_COLUMNS, values))})
    except csv.Error as exc:
        raise ValueError(f"CSV line {reader.line_num}: malformed CSV: {exc}") from exc
    if len(samples) < 2:
        raise ValueError("at least two samples are required for time integration")

    energies = {}
    for column in ("power_in_w", "power_out_w"):
        try:
            # Half each endpoint first to avoid overflowing a finite average.
            energy = math.fsum(
                (left[column] / 2 + right[column] / 2)
                * (right["timestamp_s"] - left["timestamp_s"])
                for left, right in zip(samples, samples[1:])
            )
        except (OverflowError, ValueError) as exc:
            raise ValueError("integrated energy exceeds numeric range") from exc
        if not math.isfinite(energy):
            raise ValueError("integrated energy exceeds numeric range")
        energies[column] = energy
    if energies["power_in_w"] <= 0:
        raise ValueError("integrated input energy must be positive within numeric range")
    energy_cop = energies["power_out_w"] / energies["power_in_w"]
    if not math.isfinite(energy_cop):
        raise ValueError("energy COP exceeds numeric range")
    return {
        "schema": "az-calorimetry-measurements/v1",
        "metadata": metadata,
        "provenance": {
            "csv": {"filename": csv_path.name, "sha256": hashlib.sha256(raw_csv).hexdigest()},
            "metadata": {
                "filename": metadata_path.name,
                "sha256": hashlib.sha256(raw_metadata).hexdigest(),
            },
        },
        "samples": samples,
        "summary": {
            "n_readings": len(samples),
            "duration_s": samples[-1]["timestamp_s"] - samples[0]["timestamp_s"],
            "energy_in_j": energies["power_in_w"],
            "energy_out_j": energies["power_out_w"],
            "energy_cop": energy_cop,
            "integration_method": "trapezoidal; no extrapolation",
            "threshold": DEFAULT_COP_THRESHOLD,
            "threshold_screen": (
                "ABOVE_THRESHOLD" if energy_cop > DEFAULT_COP_THRESHOLD
                else "NOT_ABOVE_THRESHOLD"
            ),
        },
        "limitations": [
            "Imported values and calibration metadata are user-supplied, not independently verified.",
            "No uncertainty propagation, baseline subtraction, or sensor-to-power conversion performed.",
            "Threshold screening is not evidence of excess heat or physical validation.",
        ],
    }
