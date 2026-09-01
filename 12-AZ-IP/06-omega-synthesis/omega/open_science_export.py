# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Open-science export helpers for derived Standard Model parameters."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

try:
    from omega.omega_synthesis import UniversalEngine  # type: ignore
    from omega.yukawa_explorer import compute_yukawa_svd, parse_bc_parameters  # type: ignore
except Exception:
    from omega_synthesis import UniversalEngine  # type: ignore
    from yukawa_explorer import compute_yukawa_svd, parse_bc_parameters  # type: ignore


def collect_derived_sm_parameters(bc_params: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    """Collect derived SM observables plus Yukawa-sector matrices."""
    engine = UniversalEngine(version="v25.5 OMEGA SPRINT BA")
    particle_physics = asdict(engine.particle_physics())
    yukawa = compute_yukawa_svd(bc_params)
    return {
        "metadata": {
            "app": "06-omega-synthesis",
            "repository_version": "v25.5",
            "sprint": "BA",
            "export": "derived-sm-parameters",
        },
        "particle_physics": particle_physics,
        "yukawa": yukawa,
    }


def flatten_export_payload(payload: Any, prefix: str = "") -> list[tuple[str, Any]]:
    """Flatten nested dict/list payloads into dotted key-value rows."""
    rows: list[tuple[str, Any]] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(flatten_export_payload(value, next_prefix))
        return rows
    if isinstance(payload, list):
        for index, value in enumerate(payload):
            next_prefix = f"{prefix}.{index}" if prefix else str(index)
            rows.extend(flatten_export_payload(value, next_prefix))
        return rows
    rows.append((prefix, payload))
    return rows


def export_sm_parameters(json_path: str | Path, csv_path: str | Path, bc_params: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    """Write derived SM parameters to JSON and CSV files."""
    payload = collect_derived_sm_parameters(bc_params)
    json_path = Path(json_path)
    csv_path = Path(csv_path)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    rows = flatten_export_payload(payload)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "value"])
        for key, value in rows:
            writer.writerow([key, value])
    return payload


def main(argv: list[str] | None = None) -> int:
    """Run the export CLI."""
    parser = argparse.ArgumentParser(description="Export derived Standard Model parameters to JSON and CSV.")
    parser.add_argument("--json-path", default="omega_sm_parameters.json")
    parser.add_argument("--csv-path", default="omega_sm_parameters.csv")
    parser.add_argument("--bc", default="", help="Boundary-condition overrides, e.g. alpha=0.1,beta=0.2")
    args = parser.parse_args(argv)
    export_sm_parameters(args.json_path, args.csv_path, parse_bc_parameters(args.bc))
    print(f"Wrote {args.json_path} and {args.csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
