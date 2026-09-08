# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Dedicated energy-ledger surface for Merlin."""

from __future__ import annotations

from typing import Any

from .merlin_telemetry import build_energy_ledger


def build_merlin_energy_ledger(runs: list[dict[str, Any]], *, limit: int = 10) -> dict[str, Any]:
    payload = build_energy_ledger(runs, limit=limit)
    entries = list(payload.get("entries") or [])
    selected_runs = list(runs)[-len(entries):] if entries else []
    by_kernel: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(entries):
        run = selected_runs[index] if index < len(selected_runs) else {}
        kernel = str((((run.get("kernel") or {}).get("id")) if isinstance(run, dict) else "") or "kernel_s")
        bucket = by_kernel.setdefault(
            kernel,
            {"count": 0, "merlin_energy_joules": 0.0, "incumbent_baseline_joules": 0.0},
        )
        bucket["count"] += 1
        bucket["merlin_energy_joules"] += float(item.get("merlin_energy_joules") or 0.0)
        bucket["incumbent_baseline_joules"] += float(item.get("incumbent_baseline_joules") or 0.0)
    for bucket in by_kernel.values():
        bucket["delta_joules"] = round(
            float(bucket["merlin_energy_joules"]) - float(bucket["incumbent_baseline_joules"]),
            6,
        )
        bucket["lower_than_incumbent"] = float(bucket["merlin_energy_joules"]) <= float(
            bucket["incumbent_baseline_joules"]
        )
        bucket["merlin_energy_joules"] = round(float(bucket["merlin_energy_joules"]), 6)
        bucket["incumbent_baseline_joules"] = round(float(bucket["incumbent_baseline_joules"]), 6)
    payload["kernel_breakdown"] = by_kernel
    payload["deterministic_measurement_mode"] = "deterministic_estimate"
    return payload
