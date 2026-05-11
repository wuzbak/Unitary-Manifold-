# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/benchmarks.py
=========================
Benchmark layer for Fermi–Hubbard adjacent research:
spin/charge observables, TDVP parity metrics, and wall-clock scaling curves.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .execution import ExecutionConfig, ExecutionResult, run_time_evolution
from .fermi_hubbard import FermiHubbardHamiltonian


@dataclass(frozen=True)
class TDVPReference:
    times: np.ndarray
    charge_density_series: np.ndarray  # shape [T, n_sites]
    spin_density_series: np.ndarray    # shape [T, n_sites]


@dataclass(frozen=True)
class TDVPParityReport:
    charge_rmse: float
    spin_rmse: float
    charge_max_abs: float
    spin_max_abs: float


@dataclass(frozen=True)
class ScalingPoint:
    n_sites: int
    wall_clock_seconds: float
    trotter_steps: int


@dataclass(frozen=True)
class ScalingCurve:
    points: list[ScalingPoint]
    loglog_slope: float


def _series_from_result(result: ExecutionResult) -> tuple[np.ndarray, np.ndarray]:
    charge = np.array([s.charge_density for s in result.observable_history], dtype=float)
    spin = np.array([s.spin_density for s in result.observable_history], dtype=float)
    return charge, spin


def tdvp_parity_report(result: ExecutionResult, reference: TDVPReference) -> TDVPParityReport:
    sim_charge, sim_spin = _series_from_result(result)

    if sim_charge.shape != reference.charge_density_series.shape:
        raise ValueError("Charge series shape mismatch between simulation and TDVP reference")
    if sim_spin.shape != reference.spin_density_series.shape:
        raise ValueError("Spin series shape mismatch between simulation and TDVP reference")

    d_charge = sim_charge - reference.charge_density_series
    d_spin = sim_spin - reference.spin_density_series

    return TDVPParityReport(
        charge_rmse=float(np.sqrt(np.mean(d_charge**2))),
        spin_rmse=float(np.sqrt(np.mean(d_spin**2))),
        charge_max_abs=float(np.max(np.abs(d_charge))),
        spin_max_abs=float(np.max(np.abs(d_spin))),
    )


def run_observable_benchmark(
    model: FermiHubbardHamiltonian,
    total_time: float,
    trotter_steps: int,
    mapping: str = "jw",
    backend: str = "simulator",
) -> ExecutionResult:
    cfg = ExecutionConfig(
        total_time=total_time,
        trotter_steps=trotter_steps,
        mapping=mapping,  # type: ignore[arg-type]
        backend=backend,
    )
    return run_time_evolution(model=model, config=cfg)


def build_scaling_curve(
    models: list[FermiHubbardHamiltonian],
    total_time: float,
    trotter_steps: int,
    mapping: str = "jw",
    backend: str = "simulator",
) -> ScalingCurve:
    points: list[ScalingPoint] = []
    for m in models:
        res = run_observable_benchmark(
            model=m,
            total_time=total_time,
            trotter_steps=trotter_steps,
            mapping=mapping,
            backend=backend,
        )
        points.append(
            ScalingPoint(
                n_sites=m.n_sites,
                wall_clock_seconds=res.wall_clock_seconds,
                trotter_steps=trotter_steps,
            )
        )

    x = np.log(np.array([p.n_sites for p in points], dtype=float))
    y = np.log(np.array([p.wall_clock_seconds for p in points], dtype=float) + 1e-15)
    slope = float(np.polyfit(x, y, 1)[0]) if len(points) >= 2 else 0.0

    return ScalingCurve(points=points, loglog_slope=slope)
