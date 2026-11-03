# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Reproduce the scoped planar Einstein--radion acceptance experiment.

This is numerical evidence, not a proof of global existence or general 5D
evolution. The direct Ricci audit differentiates saved spacetime metrics without
calling the evolution RHS. A failed gate produces a nonzero process status.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import scipy
from scipy.special import j0, j1
import sympy

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.physics.planar_radion.evolution import (
    PlanarRadionState,
    constrained_areal_initial_data,
    evolve_planar_radion,
    planar_constraint_diagnostic,
)
from src.physics.planar_radion.geometry import evaluate_planar_ricci


RESOLUTIONS = (32, 64, 128, 256)
T_INITIAL = 1.0
T_FINAL = 1.5
CFL = 0.1
MIN_ORDER = 1.8
MAX_ORDER = 2.2
FIELD_TOLERANCE = 1e-4
RESIDUAL_TOLERANCE = 1e-3


def bessel_state(
    n: int, time: float, amplitudes: tuple[float, ...]
) -> PlanarRadionState:
    """Sample an exact standing-wave family, including nonlinear backreaction.

    The spatial primitive of sigma_x is spectral. The independent analytic mean
    follows by integrating the orthogonal scalar-mode energies. No numerical
    evolution equation is used to construct this reference solution.
    """
    if n < 8 or not amplitudes or 4 * len(amplitudes) >= n:
        raise ValueError("the reference grid must resolve all quadratic harmonics")
    if not math.isfinite(time) or time <= 0:
        raise ValueError("Bessel time must be finite and positive")
    dx = 2 * np.pi / n
    x = dx * np.arange(n)
    modes = np.arange(1, len(amplitudes) + 1, dtype=float)
    amp = np.asarray(amplitudes, dtype=float)
    if not np.all(np.isfinite(amp)):
        raise ValueError("amplitudes must be finite")
    phase = modes[:, None] * x
    b0, b1 = j0(modes * time), j1(modes * time)
    psi = np.sum((amp * b0)[:, None] * np.cos(phase), axis=0)
    psi_t = -np.sum((amp * modes * b1)[:, None] * np.cos(phase), axis=0)
    psi_x = -np.sum((amp * modes * b0)[:, None] * np.sin(phase), axis=0)
    source = 1.5 * time * psi_t * psi_x
    frequencies = np.fft.fftfreq(n, d=dx) * 2 * np.pi
    sigma_hat = np.zeros(n, dtype=complex)
    sigma_hat[1:] = np.fft.fft(source)[1:] / (1j * frequencies[1:])
    mean = -0.25 * np.log(time) + np.sum(
        0.375 * amp**2
        * ((modes * time)**2 * (b0**2 + b1**2) - modes * time * b0 * b1)
    )
    sigma = mean + np.fft.ifft(sigma_hat).real
    return PlanarRadionState(
        time, dx, np.full(n, np.sqrt(time)), sigma, psi,
        np.full(n, 0.5 / np.sqrt(time)),
        -0.25 / time + 0.75 * time * (psi_t**2 + psi_x**2), psi_t,
    )


def _norm(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(values)**2)))


def gauge_wave_state(n: int, time: float) -> PlanarRadionState:
    """Exact null-coordinate pullback; spatial area variation here is gauge.

    U=u+.08 sin(u), V=v+.08 sin(v), with u=t-x and v=t+x.
    The seed has r=sqrt(T), psi=.4 log(T), sigma=(3*.4^2-1)log(T)/4.
    """
    dx = 2 * np.pi / n
    x = dx * np.arange(n)
    amplitude, charge = 0.08, 0.4
    u, v = time - x, time + x
    up, vp = 1 + amplitude * np.cos(u), 1 + amplitude * np.cos(v)
    seed_time = time + amplitude * np.sin(time) * np.cos(x)
    seed_time_t = 1 + amplitude * np.cos(time) * np.cos(x)
    if np.any(seed_time <= 0):
        raise ValueError("the gauge benchmark left its positive-area patch")
    coefficient = (3 * charge**2 - 1) / 4
    sigma = coefficient * np.log(seed_time) + 0.5 * np.log(up * vp)
    sigma_t = coefficient * seed_time_t / seed_time - 0.5 * amplitude * (
        np.sin(u) / up + np.sin(v) / vp
    )
    return PlanarRadionState(
        time, dx, np.sqrt(seed_time), sigma, charge * np.log(seed_time),
        seed_time_t / (2 * np.sqrt(seed_time)), sigma_t,
        charge * seed_time_t / seed_time,
    )


def _fields(state: PlanarRadionState) -> np.ndarray:
    return np.stack(
        (state.r, state.sigma, state.psi, state.r_t, state.sigma_t, state.psi_t)
    )


def _orders(errors: list[float]) -> list[float]:
    if any(not math.isfinite(error) or error <= 0 for error in errors):
        raise ValueError("convergence requires finite positive errors")
    return [math.log2(a / b) for a, b in zip(errors, errors[1:])]


def _audit_window(trajectory) -> float:
    # Nine interior snapshots bound oracle work and avoid a shortened final step.
    center = len(trajectory.states) // 2
    states = trajectory.states[center - 4:center + 5]
    if len(states) != 9:
        raise ValueError("the acceptance trajectory needs nine interior snapshots")
    x = np.arange(states[0].n) * states[0].dx
    residual = evaluate_planar_ricci(
        np.array([state.t for state in states]), x,
        *(np.stack([getattr(state, name) for state in states])
          for name in ("r", "sigma", "psi")),
    )
    return float(np.max(residual.frame_norm))


def _measure(initial: PlanarRadionState):
    trajectory = evolve_planar_radion(initial, T_FINAL, CFL * initial.dx)
    maximum_constraint = max(
        float(np.max(np.abs(value)))
        for state in trajectory.states
        for name, value in planar_constraint_diagnostic(state).items()
        if name in ("Cu", "Cv")
    )
    return trajectory, {
        "n": initial.n,
        "steps": len(trajectory.states) - 1,
        "maximum_null_constraint_over_trajectory": maximum_constraint,
        "maximum_orthonormal_5d_ricci_in_interior_window": _audit_window(trajectory),
    }


def _bessel_case(amplitudes: tuple[float, ...]) -> dict:
    rows = []
    for n in RESOLUTIONS:
        trajectory, row = _measure(bessel_state(n, T_INITIAL, amplitudes))
        reference = bessel_state(n, T_FINAL, amplitudes)
        row["six_field_rms_error"] = _norm(
            _fields(trajectory.states[-1]) - _fields(reference)
        )
        rows.append(row)
    return {
        "amplitudes": list(amplitudes),
        "rows": rows,
        "field_orders": _orders([row["six_field_rms_error"] for row in rows]),
        "constraint_orders": _orders(
            [row["maximum_null_constraint_over_trajectory"] for row in rows]
        ),
        "uplift_orders": _orders(
            [row["maximum_orthonormal_5d_ricci_in_interior_window"] for row in rows]
        ),
    }


def _gauge_case() -> dict:
    rows = []
    for n in RESOLUTIONS:
        trajectory, row = _measure(gauge_wave_state(n, T_INITIAL))
        row["six_field_rms_error"] = _norm(
            _fields(trajectory.states[-1]) - _fields(gauge_wave_state(n, T_FINAL))
        )
        rows.append(row)
    return {
        "scope": "exact coordinate-inhomogeneous pullback, not a physical area-wave claim",
        "rows": rows,
        "field_orders": _orders([row["six_field_rms_error"] for row in rows]),
        "constraint_orders": _orders(
            [row["maximum_null_constraint_over_trajectory"] for row in rows]
        ),
        "uplift_orders": _orders(
            [row["maximum_orthonormal_5d_ricci_in_interior_window"] for row in rows]
        ),
    }


def _independent_initial_data_case() -> dict:
    rows, finals = [], []
    for n in RESOLUTIONS:
        x = np.arange(n) * 2 * np.pi / n
        initial = constrained_areal_initial_data(
            T_INITIAL, x,
            0.04 * np.cos(x) + 0.02 * np.cos(2 * x),
            0.03 * np.cos(x) - 0.01 * np.cos(2 * x),
        )
        trajectory, row = _measure(initial)
        finals.append(_fields(trajectory.states[-1]))
        rows.append(row)
    differences = [
        _norm(coarse - fine[:, ::2])
        for coarse, fine in zip(finals, finals[1:])
    ]
    return {
        "profile": "psi=.04 cos(x)+.02 cos(2x); psi_t=.03 cos(x)-.01 cos(2x)",
        "initialization": "centered-derivative sampled constraints; O(dx^2) data error",
        "rows": rows,
        "nested_grid_differences": differences,
        "self_convergence_orders": _orders(differences),
        "constraint_orders": _orders(
            [row["maximum_null_constraint_over_trajectory"] for row in rows]
        ),
        "uplift_orders": _orders(
            [row["maximum_orthonormal_5d_ricci_in_interior_window"] for row in rows]
        ),
    }


def _temporal_case() -> dict:
    initial = bessel_state(64, T_INITIAL, (0.12,))
    steps = (16, 32, 64)
    finals = [
        _fields(evolve_planar_radion(
            initial, T_FINAL, (T_FINAL - T_INITIAL) / count
        ).states[-1])
        for count in steps
    ]
    differences = [_norm(a - b) for a, b in zip(finals, finals[1:])]
    return {
        "n": initial.n, "steps": list(steps),
        "differences": differences, "observed_order": _orders(differences)[0],
        "scope": "fixed spatial mesh; temporal differences, not total solution error",
    }


def _negative_controls() -> dict[str, bool]:
    n, time = 64, 1.2
    good = bessel_state(n, time, (0.12,))
    violated = replace(good, sigma_t=good.sigma_t + 0.01)
    constraint_detected = max(
        np.max(np.abs(value))
        for name, value in planar_constraint_diagnostic(violated).items()
        if name in ("Cu", "Cv")
    ) > 1e-3
    x = np.arange(n) * good.dx
    periodic_rejected = False
    try:
        constrained_areal_initial_data(time, x, np.cos(x), np.sin(x))
    except ValueError as exc:
        if "mean" not in str(exc):
            raise
        periodic_rejected = True
    t = np.linspace(1.0, 1.4, 17)
    shape = (len(t), n)
    # Fixed transverse geometry with a scalar wave is not a vacuum uplift.
    scalar = 0.1 * np.cos(t[:, None] - x[None, :])
    frozen = evaluate_planar_ricci(t, x, np.ones(shape), np.zeros(shape), scalar)
    # A constant scalar with curved q also fails the discarded transverse equation.
    curved = evaluate_planar_ricci(
        t, x, np.ones(shape), 0.1 * t[:, None]**2 * np.ones(shape),
        np.zeros(shape),
    )
    # Match the 4D metric in the wrong frame by absorbing psi into sigma/r.
    states = [bessel_state(n, float(value), (0.12,)) for value in t]
    r = np.stack([state.r for state in states])
    sigma = np.stack([state.sigma for state in states])
    psi = np.stack([state.psi for state in states])
    wrong = evaluate_planar_ricci(
        t, x, r * np.exp(psi / 2), sigma + psi / 2, psi
    )
    tt = np.broadcast_to(t[:, None], shape)
    wrong_normalization = evaluate_planar_ricci(
        t, x, np.sqrt(tt), 0.5 * np.log(tt), 0.8 * np.log(tt)
    )
    return {
        "constraint_injection_detected": bool(constraint_detected),
        "incompatible_periodic_data_rejected": periodic_rejected,
        "frozen_spectator_scalar_wave_detected": bool(np.max(frozen.frame_norm) > 1e-3),
        "omitted_transverse_equation_detected": bool(np.max(curved.frame_norm) > 1e-3),
        "wrong_frame_uplift_detected": bool(np.max(wrong.frame_norm) > 1e-3),
        "wrong_scalar_normalization_detected": bool(
            np.max(wrong_normalization.frame_norm) > 1e-3
        ),
    }


def _symbolic_case() -> dict:
    from src.physics.planar_radion.derivation import exact_symbolic_checks

    checks = exact_symbolic_checks()
    bessel = checks["bessel_mode"]
    identities = {
        name: values
        for name, values in checks.items()
        if name != "bessel_mode"
    }
    identities["bessel_equation_and_period"] = {
        "mode_equation": bessel["mode_equation"],
        "periodic_momentum": bessel["momentum_integral"],
    }
    residuals = {
        name: {key: str(value) for key, value in values.items()}
        for name, values in identities.items()
    }
    return {
        "residuals": residuals,
        "identities_checked": sum(len(values) for values in identities.values()),
        "all_zero": all(value == 0 for values in identities.values() for value in values.values()),
        "not_machine_formalized": [
            "GHY boundary bookkeeping", "local Sobolev energy-method well-posedness",
        ],
    }


def acceptance_gates(report: dict) -> dict[str, bool]:
    """Conjunctive gates; nonfinite results cannot be successful receipts."""
    def second_order(values):
        return all(math.isfinite(p) and MIN_ORDER <= p <= MAX_ORDER for p in values[-2:])

    bessel = report["bessel_cases"]
    independent = report["independent_initial_data"]
    exact_cases = [*bessel, report["gauge_wave"]]
    cases = [*exact_cases, independent]
    return {
        "symbolic_identities_verified": report["symbolic_checks"]["all_zero"] is True,
        "complete_experiment_matrix": (
            len(bessel) == 3
            and all([row["n"] for row in case["rows"]] == list(RESOLUTIONS) for case in cases)
            and all(len(case["field_orders"]) == 3 for case in exact_cases)
            and len(independent["self_convergence_orders"]) == 2
            and all(len(case["constraint_orders"]) == len(case["uplift_orders"]) == 3 for case in cases)
            and len(report["negative_controls"]) == 6
            and all(isinstance(value, bool) for value in report["negative_controls"].values())
        ),
        "bessel_solution_second_order": all(second_order(case["field_orders"]) for case in bessel),
        "gauge_wave_solution_second_order": second_order(report["gauge_wave"]["field_orders"]),
        "independent_data_second_order": second_order(independent["self_convergence_orders"]),
        "constraints_second_order": all(second_order(case["constraint_orders"]) for case in cases),
        "uplift_second_order": all(second_order(case["uplift_orders"]) for case in cases),
        "finest_field_errors_below_tolerance": all(
            0 <= case["rows"][-1]["six_field_rms_error"] < FIELD_TOLERANCE for case in exact_cases
        ),
        "finest_constraints_below_tolerance": all(
            0 <= case["rows"][-1]["maximum_null_constraint_over_trajectory"] < RESIDUAL_TOLERANCE
            for case in cases
        ),
        "finest_uplift_below_tolerance": all(
            0 <= case["rows"][-1]["maximum_orthonormal_5d_ricci_in_interior_window"] < RESIDUAL_TOLERANCE
            for case in cases
        ),
        "fourth_order_time_differences": 3.5 <= report["temporal_refinement"]["observed_order"] <= 4.5,
        "negative_controls_rejected": all(report["negative_controls"].values()),
    }


def run_acceptance() -> dict:
    sources = [
        Path(__file__).resolve(),
        ROOT / "src/physics/planar_radion/evolution.py",
        ROOT / "src/physics/planar_radion/geometry.py",
        ROOT / "src/physics/planar_radion/derivation.py",
    ]
    hashes = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sources
    }
    report = {
        "scope": "massless, zero-vector, transversely isotropic circle-zero-mode sector",
        "not_claimed": [
            "general 5D evolution", "global existence", "empirical confirmation",
            "derivation of the existing relaxation law", "full repository regression",
        ],
        "units": "dimensionless; reference length=1; spatial period=2*pi",
        "parameters": {
            "resolutions": list(RESOLUTIONS), "t_initial": T_INITIAL,
            "t_final": T_FINAL, "cfl": CFL, "minimum_order": MIN_ORDER,
            "maximum_order": MAX_ORDER, "field_tolerance": FIELD_TOLERANCE,
            "residual_tolerance": RESIDUAL_TOLERANCE,
            "oracle_window": "nine midpoint snapshots; five retained interior times",
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__, "scipy": scipy.__version__,
            "sympy": sympy.__version__,
        },
        "baseline_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_sha256": hashes,
        "symbolic_checks": _symbolic_case(),
        "bessel_cases": [_bessel_case(amplitudes) for amplitudes in ((0.04,), (0.12,), (0.04, 0.025))],
        "gauge_wave": _gauge_case(),
        "independent_initial_data": _independent_initial_data_case(),
        "temporal_refinement": _temporal_case(),
        "negative_controls": _negative_controls(),
    }
    after = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    if after != hashes:
        raise RuntimeError("scientific sources changed during acceptance execution")
    report["gates"] = acceptance_gates(report)
    report["passed"] = all(report["gates"].values())
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="persist the complete JSON evidence packet")
    args = parser.parse_args()
    report = run_acceptance()
    payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
