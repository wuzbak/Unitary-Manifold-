# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Post-MAS Track 2: variance-based global sensitivity analysis.

Implements a compact Saltelli/Sobol estimator for core solver outputs.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import numpy as np

from src.core.sensitivity_analysis import (
    C_S_BRAIDED,
    PHI0_CANONICAL,
    ns_from_phi0,
)

__all__ = [
    "DEFAULT_PARAMETER_BOUNDS",
    "core_solver_model",
    "saltelli_sobol_indices",
    "ranked_influence_table",
    "track2_gsa_artifact",
]


DEFAULT_PARAMETER_BOUNDS: Dict[str, Tuple[float, float]] = {
    "phi0_scale": (0.90, 1.10),
    "cs_scale": (0.95, 1.05),
}


def core_solver_model(params: np.ndarray) -> Dict[str, np.ndarray]:
    """Evaluate core outputs for a matrix of parameter samples.

    params columns:
      0 -> phi0_scale
      1 -> cs_scale
    """
    phi0 = PHI0_CANONICAL * params[:, 0]
    cs = C_S_BRAIDED * params[:, 1]
    n_w = 5.0
    r_braided = (32.0 * n_w / phi0**2) * cs
    w_kk = -1.0 + (2.0 / 3.0) * cs**2
    n_s = np.array([ns_from_phi0(v) for v in phi0], dtype=float)
    return {"n_s": n_s, "r_braided": r_braided, "w_KK": w_kk}


def _saltelli_matrices(
    n: int,
    bounds: List[Tuple[float, float]],
    seed: int,
) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    d = len(bounds)
    a = rng.random((n, d))
    b = rng.random((n, d))
    for j, (lo, hi) in enumerate(bounds):
        span = hi - lo
        a[:, j] = lo + span * a[:, j]
        b[:, j] = lo + span * b[:, j]
    return a, b


def saltelli_sobol_indices(
    model_fn: Callable[[np.ndarray], Dict[str, np.ndarray]],
    parameter_bounds: Dict[str, Tuple[float, float]] | None = None,
    n_samples: int = 1024,
    seed: int = 185,
) -> Dict[str, object]:
    """Compute first-order and total-effect Sobol indices."""
    bounds = parameter_bounds or DEFAULT_PARAMETER_BOUNDS
    names = list(bounds.keys())
    matrix_bounds = [bounds[name] for name in names]

    a, b = _saltelli_matrices(n_samples, matrix_bounds, seed)
    ya = model_fn(a)
    yb = model_fn(b)

    output: Dict[str, object] = {
        "method": "Saltelli Sobol (variance-based)",
        "n_samples": n_samples,
        "parameters": names,
        "outputs": {},
    }

    for out_name in ya.keys():
        y_a = np.asarray(ya[out_name], dtype=float)
        y_b = np.asarray(yb[out_name], dtype=float)
        var_y = float(np.var(np.concatenate([y_a, y_b]), ddof=1))
        if var_y <= 1e-30:
            s1 = {p: 0.0 for p in names}
            st = {p: 0.0 for p in names}
        else:
            s1 = {}
            st = {}
            for i, p in enumerate(names):
                a_bi = a.copy()
                a_bi[:, i] = b[:, i]
                y_ab_i = np.asarray(model_fn(a_bi)[out_name], dtype=float)
                s1[p] = float(np.mean(y_b * (y_ab_i - y_a)) / var_y)
                st[p] = float(0.5 * np.mean((y_a - y_ab_i) ** 2) / var_y)

        output["outputs"][out_name] = {
            "variance": var_y,
            "first_order": s1,
            "total_effect": st,
        }

    return output


def ranked_influence_table(gsa_result: Dict[str, object]) -> Dict[str, List[Dict[str, float]]]:
    """Rank parameter influence per output by total-effect Sobol index."""
    ranked: Dict[str, List[Dict[str, float]]] = {}
    for out_name, out_data in gsa_result["outputs"].items():
        st = out_data["total_effect"]
        entries = [
            {
                "parameter": p,
                "first_order": float(out_data["first_order"][p]),
                "total_effect": float(st[p]),
            }
            for p in st.keys()
        ]
        entries.sort(key=lambda item: item["total_effect"], reverse=True)
        ranked[out_name] = entries
    return ranked


def track2_gsa_artifact(
    n_samples: int = 1024,
    seed: int = 185,
) -> Dict[str, object]:
    """Return complete Track 2 artifact including robustness verdict."""
    raw = saltelli_sobol_indices(
        model_fn=core_solver_model,
        parameter_bounds=DEFAULT_PARAMETER_BOUNDS,
        n_samples=n_samples,
        seed=seed,
    )
    ranked = ranked_influence_table(raw)

    critical_failures: List[str] = []
    for out_name, table in ranked.items():
        if not table:
            critical_failures.append(f"{out_name}: empty influence table")
            continue
        top = table[0]["total_effect"]
        if top > 1.05:
            critical_failures.append(
                f"{out_name}: invalid Sobol total-effect top score {top:.3f}"
            )

    verdict = "PASS" if not critical_failures else "FAIL"
    return {
        "track": "T2",
        "title": "Global sensitivity analysis",
        "method": raw["method"],
        "ranked_parameter_influence": ranked,
        "robustness_verdict": verdict,
        "critical_failures": critical_failures,
        "n_samples": n_samples,
        "seed": seed,
    }

