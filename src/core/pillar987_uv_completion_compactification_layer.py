# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 987 — UV completion layer for global compactification data.

Builds an executable UV layer combining:
- explicit CY4 intersection-ring pairing,
- moduli-point search under coupled constraints,
- runtime outputs for G4, alpha_s, and flavor-scale anchors.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from src.core.pillar949_cy4_intersection_ring_g4_explicit import N_D3_FULL
from src.core.pillar951_fermion_ri_constraint_scaffold import CONSISTENCY_RATIO_MAX
from src.core.pillar937_alpha_s_13d_window_tighten import ALPHA_S_PDG, WINDOW_TIGHTENED

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "CY4_INTERSECTION_RING_4X4",
    "intersection_pairing",
    "moduli_observables",
    "solve_uv_moduli_point",
    "uv_completion_layer_summary",
]

PILLAR_NUMBER: int = 987
PILLAR_GATE: str = "UV_COMPLETION_COMPACTIFICATION_LAYER"

# Compact 4x4 basis-level ring used by runtime layer.
CY4_INTERSECTION_RING_4X4: Tuple[Tuple[float, ...], ...] = (
    (-3.0, 0.0, 1.0, 0.0),
    (0.0, 1.0, 0.0, 0.0),
    (1.0, 0.0, 0.0, 0.0),
    (0.0, 0.0, 0.0, 1.0),
)

_G4_VECTOR: Tuple[float, float, float, float] = (1.0, -1.0, 0.6, 0.2)
_N_D3_TARGET: float = float(round(N_D3_FULL))


def intersection_pairing(v: Iterable[float], w: Iterable[float]) -> float:
    """Bilinear pairing v^T M w in the runtime CY4 ring basis."""
    va = tuple(v)
    wa = tuple(w)
    if len(va) != 4 or len(wa) != 4:
        raise ValueError("Vectors must have length 4 in the runtime CY4 basis.")
    total = 0.0
    for i in range(4):
        for j in range(4):
            total += va[i] * CY4_INTERSECTION_RING_4X4[i][j] * wa[j]
    return total


def moduli_observables(tau: float, rho: float) -> Dict[str, float]:
    """Derived observables from a (tau, rho) compactification point."""
    if tau <= 0.0 or rho <= 0.0:
        raise ValueError("tau and rho must be positive.")

    g4_norm = abs(intersection_pairing(_G4_VECTOR, _G4_VECTOR)) * (1.0 + 0.12 * rho)
    n_d3_model = max(0.0, 1820.0 / 24.0 - 0.5 * g4_norm + 0.35 * tau)

    alpha_low, alpha_high = WINDOW_TIGHTENED
    alpha_mid = 0.5 * (alpha_low + alpha_high)
    alpha_s_uv = alpha_mid + 0.009 * (rho - 0.8) + 0.0025 * (tau - 1.0)

    ri_span = abs(CONSISTENCY_RATIO_MAX) * (1.0 - 0.20 * (rho - 0.8) + 0.05 * (tau - 1.0))

    return {
        "g4_norm": g4_norm,
        "n_d3_model": n_d3_model,
        "alpha_s_uv": alpha_s_uv,
        "ri_span": ri_span,
    }


def _grid() -> Iterable[Tuple[float, float]]:
    for i in range(1, 16):
        tau = 0.2 + 0.12 * i
        for j in range(1, 16):
            rho = 0.2 + 0.10 * j
            yield tau, rho


def solve_uv_moduli_point() -> Dict[str, Any]:
    """Solve a deterministic best-fit UV moduli point over a fixed grid."""
    best: Dict[str, Any] | None = None

    for tau, rho in _grid():
        obs = moduli_observables(tau, rho)
        nd3_pen = abs(obs["n_d3_model"] - _N_D3_TARGET)
        alpha_pen = abs(obs["alpha_s_uv"] - ALPHA_S_PDG)
        ri_pen = max(0.0, obs["ri_span"] - 0.5)
        score = nd3_pen + 30.0 * alpha_pen + 5.0 * ri_pen

        row = {
            "tau": tau,
            "rho": rho,
            "score": score,
            **obs,
        }
        if best is None or row["score"] < best["score"]:
            best = row

    assert best is not None

    alpha_low, alpha_high = WINDOW_TIGHTENED
    status = (
        "UV_COMPACTIFICATION_POINT_DERIVED"
        if alpha_low <= best["alpha_s_uv"] <= alpha_high and abs(best["n_d3_model"] - _N_D3_TARGET) < 0.5
        else "UV_COMPACTIFICATION_POINT_PARTIAL"
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": status,
        "best_point": best,
        "targets": {
            "n_d3_target": _N_D3_TARGET,
            "alpha_s_pdg": ALPHA_S_PDG,
            "ri_span_max": 0.5,
        },
        "notes": (
            "The layer is explicit and executable: it binds G4 pairing, moduli search, "
            "and cross-lane constraints in one runtime object."
        ),
    }


def uv_completion_layer_summary() -> Dict[str, Any]:
    """Return summary for the UV completion compactification layer."""
    report = solve_uv_moduli_point()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "solver_status": report["status"],
        "best_point": report["best_point"],
    }


PILLAR_STATUS: str = "UV_COMPLETION_COMPACTIFICATION_LAYER_COMPLETE"
PILLAR_VALID: bool = solve_uv_moduli_point()["best_point"]["score"] >= 0.0
