# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Import user reference dimensions and produce provenance-preserving reports."""

from __future__ import annotations

import csv
import io
import math
from dataclasses import asdict

from .comparator import HolographicBenchmark, compare_kk_tower_to_all_benchmarks

MAX_CSV_BYTES = 65536
MAX_REFERENCES = 100
REPORT_SCOPE = (
    "Dimension-only numerical comparison, not a material match or physics validation. "
    "UM dimensions are approximate spin-2 scaffold values (Delta_n = 4 + 2n). "
    "2*Delta is a scaling exponent only; no tensor structure is compared. "
    "User sources and dimensions are unverified, not independently retrieved or checked."
)


def parse_reference_csv(csv_text: str) -> list[HolographicBenchmark]:
    """Require a complete UTF-8 CSV with name, delta, source and no extra columns."""
    if not isinstance(csv_text, str):
        raise ValueError("csv_text must be a string")
    if len(csv_text.encode("utf-8")) > MAX_CSV_BYTES:
        raise ValueError(f"CSV must be at most {MAX_CSV_BYTES} UTF-8 bytes")
    reader = csv.reader(io.StringIO(csv_text.lstrip("\ufeff"), newline=""), strict=True)
    references = []
    seen = set()
    try:
        header = next(reader, [])
        if len(header) != 3 or set(header) != {"name", "delta", "source"}:
            raise ValueError("CSV headers must be exactly name,delta,source (any order)")
        for values in reader:
            if not values:
                continue
            line = reader.line_num
            if len(values) != 3:
                raise ValueError(f"CSV line {line}: expected exactly 3 fields")
            row = dict(zip(header, (value.strip() for value in values)))
            if not row["name"] or not row["source"]:
                raise ValueError(f"CSV line {line}: name and source must not be blank")
            if row["name"] in seen:
                raise ValueError(f"CSV line {line}: duplicate name {row['name']!r}")
            try:
                delta = float(row["delta"])
            except ValueError:
                raise ValueError(f"CSV line {line}: delta must be a finite positive number") from None
            if delta <= 0 or not math.isfinite(delta) or not math.isfinite(2 * delta):
                raise ValueError(f"CSV line {line}: delta and 2*delta must be finite and positive")
            references.append(HolographicBenchmark(
                row["name"], delta, row["source"], provenance="user_supplied_unverified",
            ))
            seen.add(row["name"])
            if len(references) > MAX_REFERENCES:
                raise ValueError(f"CSV must contain at most {MAX_REFERENCES} references")
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV: {exc}") from exc
    if not references:
        raise ValueError("CSV must contain at least one reference")
    return references


def compare_reference_csv(csv_text: str, n_max: int = 3) -> dict:
    """Create a JSON-ready report; ties for nearest reference use CSV row order."""
    references = parse_reference_csv(csv_text)
    comparisons = compare_kk_tower_to_all_benchmarks(n_max, benchmarks=references)
    closest = [
        min(comparisons[start:start + len(references)], key=lambda row: abs(row["delta_gap"]))
        for start in range(0, len(comparisons), len(references))
    ]
    return {
        "schema_version": "1.0",
        "scope": REPORT_SCOPE,
        "n_max": n_max,
        "reference_count": len(references),
        "references": [asdict(reference) for reference in references],
        "comparisons": comparisons,
        "closest_by_level": closest,
        "tie_break": "first reference in CSV row order",
    }
