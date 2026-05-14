# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/xdiag_bridge/parity.py
==================================
Parity and accuracy gates for UM ↔ XDiag comparisons.

Production-parity enhancement (v10.55)
---------------------------------------
Extended metric set: ground_energy, first_gap, charge_gap, spin_gap,
staggered_magnetization, double_occupancy (optional).

Multi-metric parity reports provide per-metric delta, tolerance, and
pass/fail status, with a comprehensive summary for diagnostics.
"""
from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Full set of metrics supported by the parity gate
# ---------------------------------------------------------------------------

#: Metrics that MUST be present in both UM and XDiag results.
REQUIRED_METRICS: tuple[str, ...] = (
    "ground_energy",
    "first_gap",
    "staggered_magnetization",
)

#: Optional metrics compared when present in both result dicts.
OPTIONAL_METRICS: tuple[str, ...] = (
    "charge_gap",
    "spin_gap",
    "double_occupancy",
)


@dataclass(frozen=True)
class ParityTolerance:
    """Per-metric absolute tolerances for the parity gate.

    Attributes
    ----------
    energy_abs_tol:
        Tolerance for energy values (ground_energy, first_gap, charge_gap,
        spin_gap).  Default 1e-8.
    observable_abs_tol:
        Tolerance for observables (staggered_magnetization,
        double_occupancy).  Default 1e-6.
    """

    energy_abs_tol: float = 1e-8
    gap_abs_tol: float = 1e-8
    observable_abs_tol: float = 1e-6

    def tol_for(self, metric: str) -> float:
        """Return the appropriate tolerance for *metric*."""
        if metric in ("ground_energy", "first_gap", "charge_gap", "spin_gap"):
            return self.energy_abs_tol
        return self.observable_abs_tol


@dataclass(frozen=True)
class ParityDelta:
    """Per-metric parity comparison result.

    Attributes
    ----------
    metric:
        Name of the metric compared.
    um_value:
        Value from the UM computation.
    xdiag_value:
        Value from the XDiag computation.
    abs_delta:
        Absolute difference |um_value − xdiag_value|.
    tolerance:
        The tolerance used for this metric.
    passed:
        True when abs_delta ≤ tolerance.
    """

    metric: str
    um_value: float
    xdiag_value: float
    abs_delta: float
    tolerance: float
    passed: bool


@dataclass(frozen=True)
class ParityReport:
    """Full parity report for a UM ↔ XDiag comparison.

    Attributes
    ----------
    ok:
        True when all required metrics pass and no optional metric fails.
    deltas:
        List of per-metric ParityDelta results (required first, then optional).
    n_metrics_checked:
        Total number of metrics evaluated.
    n_metrics_failed:
        Number of metrics that failed the tolerance check.
    summary:
        Human-readable one-line summary.
    """

    ok: bool
    deltas: list[ParityDelta]
    n_metrics_checked: int
    n_metrics_failed: int
    summary: str


def _make_delta(
    metric: str,
    um_metrics: dict[str, float],
    xdiag_metrics: dict[str, float],
    tolerance: ParityTolerance,
) -> ParityDelta:
    um_val = float(um_metrics[metric])
    xd_val = float(xdiag_metrics[metric])
    abs_delta = abs(um_val - xd_val)
    tol = tolerance.tol_for(metric)
    return ParityDelta(
        metric=metric,
        um_value=um_val,
        xdiag_value=xd_val,
        abs_delta=abs_delta,
        tolerance=tol,
        passed=abs_delta <= tol,
    )


def parity_report(
    um_metrics: dict[str, float],
    xdiag_metrics: dict[str, float],
    tolerance: ParityTolerance = ParityTolerance(),
) -> ParityReport:
    """Compute a full parity report comparing UM and XDiag metrics.

    Required metrics (ground_energy, first_gap, staggered_magnetization)
    must be present in both dicts.  Optional metrics (charge_gap, spin_gap,
    double_occupancy) are compared when available in both dicts.

    Parameters
    ----------
    um_metrics:
        Metrics from the UM computation.
    xdiag_metrics:
        Metrics from the XDiag computation.
    tolerance:
        Per-metric absolute tolerances.

    Returns
    -------
    ParityReport with ok=True when all present metrics pass.
    """
    deltas: list[ParityDelta] = []

    # Required metrics — must be present
    for metric in REQUIRED_METRICS:
        if metric not in um_metrics:
            raise ValueError(f"Missing required metric in UM lane: {metric!r}")
        if metric not in xdiag_metrics:
            raise ValueError(f"Missing required metric in XDiag lane: {metric!r}")
        deltas.append(_make_delta(metric, um_metrics, xdiag_metrics, tolerance))

    # Optional metrics — compared only when present in BOTH dicts
    for metric in OPTIONAL_METRICS:
        if metric in um_metrics and metric in xdiag_metrics:
            deltas.append(_make_delta(metric, um_metrics, xdiag_metrics, tolerance))

    n_failed = sum(1 for d in deltas if not d.passed)
    ok = n_failed == 0

    if ok:
        summary = (
            f"PARITY OK — {len(deltas)} metric(s) checked, all within tolerance."
        )
    else:
        failed_names = [d.metric for d in deltas if not d.passed]
        summary = (
            f"PARITY FAILED — {n_failed}/{len(deltas)} metric(s) out of tolerance: "
            + ", ".join(
                f"{d.metric}(|Δ|={d.abs_delta:.3e} > tol={d.tolerance:.3e})"
                for d in deltas
                if not d.passed
            )
        )

    return ParityReport(
        ok=ok,
        deltas=deltas,
        n_metrics_checked=len(deltas),
        n_metrics_failed=n_failed,
        summary=summary,
    )


def assert_parity(
    um_metrics: dict[str, float],
    xdiag_metrics: dict[str, float],
    tolerance: ParityTolerance = ParityTolerance(),
) -> ParityReport:
    """Assert parity between UM and XDiag metrics, raising on failure.

    Parameters
    ----------
    um_metrics, xdiag_metrics:
        Metric dicts to compare.
    tolerance:
        Per-metric tolerances.

    Returns
    -------
    ParityReport (ok=True).

    Raises
    ------
    ValueError
        If any required or optional metric exceeds tolerance.
    """
    report = parity_report(
        um_metrics=um_metrics,
        xdiag_metrics=xdiag_metrics,
        tolerance=tolerance,
    )
    if not report.ok:
        raise ValueError(f"XDiag bridge parity gate failed: {report.summary}")
    return report
