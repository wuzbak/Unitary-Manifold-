# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/xdiag_bridge/parity.py
==================================
Parity and accuracy gates for UM ↔ XDiag comparisons.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParityTolerance:
    energy_abs_tol: float = 1e-8
    gap_abs_tol: float = 1e-8
    observable_abs_tol: float = 1e-6


@dataclass(frozen=True)
class ParityDelta:
    metric: str
    um_value: float
    xdiag_value: float
    abs_delta: float


@dataclass(frozen=True)
class ParityReport:
    ok: bool
    deltas: list[ParityDelta]



def parity_report(
    um_metrics: dict[str, float],
    xdiag_metrics: dict[str, float],
    tolerance: ParityTolerance,
) -> ParityReport:
    checks = {
        "ground_energy": tolerance.energy_abs_tol,
        "first_gap": tolerance.gap_abs_tol,
        "staggered_magnetization": tolerance.observable_abs_tol,
    }
    deltas: list[ParityDelta] = []

    for metric, tol in checks.items():
        if metric not in um_metrics:
            raise ValueError(f"Missing metric in UM lane: {metric}")
        if metric not in xdiag_metrics:
            raise ValueError(f"Missing metric in XDiag lane: {metric}")

        um_val = float(um_metrics[metric])
        xd_val = float(xdiag_metrics[metric])
        abs_delta = abs(um_val - xd_val)
        deltas.append(ParityDelta(metric=metric, um_value=um_val, xdiag_value=xd_val, abs_delta=abs_delta))
        if abs_delta > tol:
            return ParityReport(ok=False, deltas=deltas)

    return ParityReport(ok=True, deltas=deltas)



def assert_parity(
    um_metrics: dict[str, float],
    xdiag_metrics: dict[str, float],
    tolerance: ParityTolerance,
) -> ParityReport:
    report = parity_report(um_metrics=um_metrics, xdiag_metrics=xdiag_metrics, tolerance=tolerance)
    if not report.ok:
        failed = report.deltas[-1]
        raise ValueError(
            f"Parity gate failed for {failed.metric}: "
            f"|UM-XDiag|={failed.abs_delta:.6e}"
        )
    return report
