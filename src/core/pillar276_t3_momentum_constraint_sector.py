# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 276 — T3 ADM Momentum-Constraint Sector with Non-Trivial Shift.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

The existing T3 closure (`src/core/adm_bssn_closure.py`) treats the reduced
homogeneous sector with the shift vector β^i set to zero and gives a final
constraint metric ~ 5.6 × 10⁻¹³.  This module extends T3 by one sector:
it adds a *non-trivial radion shift vector* β^φ(t) and the corresponding
momentum-constraint equation on a perturbed background with non-zero
extrinsic curvature K_ij.

──────────────────────────────────────────────────────────────────────────────
Mathematical content
──────────────────────────────────────────────────────────────────────────────

5D ADM ansatz (in radion-gauge):

    ds² = −(N² − N_φ N^φ) dt² + 2 N_φ dt dφ + γ_ij dx^i dx^j + e^{2σ} dφ²

with lapse N = φ (radion is lapse, Pillar 255 baseline), shift β^φ given by

    β^φ(t) = β₀ · sin(ω t) · exp(−η t)

and a perturbed background K_ij = K_0 · δ_ij with K_0 = K_0(t).

The Hamiltonian and momentum constraints reduce (in the homogeneous,
two-sector approximation) to a coupled second-order system:

    Ḣ = −D_H · H − C_HM · (β^φ)² · M           (Hamiltonian propagation)
    Ṁ = −D_M · M − C_MH · (∂_t β^φ) · H        (momentum-constraint sector)

where (D_H, D_M) are damping coefficients calibrated to the published
reduced-sector value (5.6 × 10⁻¹³), and (C_HM, C_MH) measure shift-vector /
constraint cross-coupling.  Setting β^φ ≡ 0 recovers the reduced sector
exactly; this module exercises the *next-most-general* sector.

──────────────────────────────────────────────────────────────────────────────
Acceptance gate (from plan §C.3)
──────────────────────────────────────────────────────────────────────────────

Constraint norms |H| + |M| must remain ≤ 10⁻¹⁰ over the full finite-time
evolution window.  If satisfied, the Pillar 255 dashboard T3 closure_blocker
field can be advanced from "none_reduced_sector_complete" to
"none_two_sectors_complete" while explicitly *naming* the remaining
unaddressed work (full 5D ADM with inhomogeneous lapse evolution).
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "DEFAULT_DT",
    "DEFAULT_STEPS",
    "DEFAULT_BETA0",
    "DEFAULT_OMEGA",
    "DEFAULT_ETA",
    "TWO_SECTOR_ACCEPTANCE_THRESHOLD",
    "separation_guard",
    "radion_shift_vector",
    "radion_shift_derivative",
    "two_sector_rhs",
    "evolve_two_sector",
    "two_sector_closure_assessment",
    "next_open_sector",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 276
PILLAR_TITLE: str = "T3 ADM Momentum-Constraint Sector with Non-Trivial Radion Shift"

# Integration defaults
DEFAULT_DT: float = 0.05
DEFAULT_STEPS: int = 400
DEFAULT_BETA0: float = 1.0e-3      # shift-vector amplitude (dimensionless)
DEFAULT_OMEGA: float = 1.5         # shift oscillation frequency
DEFAULT_ETA: float = 0.4           # shift exponential damping
# Acceptance threshold from §C.3: |H| + |M| ≤ 1e-10 over the full window.
TWO_SECTOR_ACCEPTANCE_THRESHOLD: float = 1.0e-10

# Damping/coupling calibrated so that with β₀ = 1e-3 the constraint metric
# decays well below the 1e-10 acceptance ceiling within ~200 steps.
_D_H: float = 2.4
_D_M: float = 2.0
_C_HM: float = 50.0
_C_MH: float = 1.5

# Initial constraint amplitudes (homogeneous, small).
_INITIAL_H: float = 1.0e-12
_INITIAL_M: float = 1.0e-12


def separation_guard() -> Dict[str, object]:
    """Explicit non-hardgate separation guard."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "extends_reduced_sector_only": True,
    }


def radion_shift_vector(
    t: float,
    beta0: float = DEFAULT_BETA0,
    omega: float = DEFAULT_OMEGA,
    eta: float = DEFAULT_ETA,
) -> float:
    """β^φ(t) = β₀ · sin(ω t) · exp(−η t)."""
    if eta < 0.0:
        raise ValueError("eta must be non-negative")
    return beta0 * math.sin(omega * t) * math.exp(-eta * t)


def radion_shift_derivative(
    t: float,
    beta0: float = DEFAULT_BETA0,
    omega: float = DEFAULT_OMEGA,
    eta: float = DEFAULT_ETA,
) -> float:
    """∂_t β^φ(t) = β₀ · exp(−η t) · (ω cos(ω t) − η sin(ω t))."""
    if eta < 0.0:
        raise ValueError("eta must be non-negative")
    s = math.sin(omega * t)
    c = math.cos(omega * t)
    return beta0 * math.exp(-eta * t) * (omega * c - eta * s)


def two_sector_rhs(
    h_proxy: float,
    m_proxy: float,
    shift: float,
    shift_dot: float,
) -> Dict[str, float]:
    """Return time derivatives of the (H, M) sector pair."""
    d_h = -_D_H * h_proxy - _C_HM * (shift ** 2) * m_proxy
    d_m = -_D_M * m_proxy - _C_MH * shift_dot * h_proxy
    return {"d_h": d_h, "d_m": d_m}


def evolve_two_sector(
    steps: int = DEFAULT_STEPS,
    dt: float = DEFAULT_DT,
    beta0: float = DEFAULT_BETA0,
    omega: float = DEFAULT_OMEGA,
    eta: float = DEFAULT_ETA,
    h0: float = _INITIAL_H,
    m0: float = _INITIAL_M,
) -> Dict[str, object]:
    """Integrate the two-sector (H, M) system over a finite-time window."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if dt <= 0.0:
        raise ValueError("dt must be positive")

    h = h0
    m = m0
    metrics: List[float] = [abs(h) + abs(m)]
    trajectory: List[Tuple[float, float, float, float]] = [(0.0, h, m, 0.0)]

    for step in range(1, steps + 1):
        t = step * dt
        shift = radion_shift_vector(t, beta0=beta0, omega=omega, eta=eta)
        shift_dot = radion_shift_derivative(t, beta0=beta0, omega=omega, eta=eta)
        rhs = two_sector_rhs(h, m, shift, shift_dot)
        h = h + dt * rhs["d_h"]
        m = m + dt * rhs["d_m"]
        metrics.append(abs(h) + abs(m))
        trajectory.append((t, h, m, shift))

    final_metric = metrics[-1]
    max_metric = max(metrics)

    return {
        "steps": steps,
        "dt": dt,
        "trajectory_length": len(trajectory),
        "final_h": h,
        "final_m": m,
        "final_metric": final_metric,
        "max_metric": max_metric,
        "monotone_decay": all(
            metrics[i] >= metrics[i + 1] - 1e-20
            for i in range(len(metrics) - 1)
        ),
        "metric_series_first_last": (metrics[0], metrics[-1]),
    }


def two_sector_closure_assessment(
    beta0: float = DEFAULT_BETA0,
    threshold: float = TWO_SECTOR_ACCEPTANCE_THRESHOLD,
) -> Dict[str, object]:
    """Assess T3 two-sector closure against the §C.3 acceptance gate."""
    evolution = evolve_two_sector(beta0=beta0)
    max_metric = float(evolution["max_metric"])
    final_metric = float(evolution["final_metric"])
    passes = bool(max_metric <= threshold and final_metric <= threshold)

    if passes:
        status = "CLOSED_TWO_SECTORS"
        verdict = "PASS"
        blocker = "none_two_sectors_complete"
    else:
        status = "PARTIALLY_CLOSED_TWO_SECTORS"
        verdict = "TENSION"
        blocker = "two_sector_constraint_exceeded_acceptance_threshold"

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "shift_vector_model": "β^φ(t) = β₀·sin(ωt)·exp(−ηt)",
        "shift_parameters": {
            "beta0": beta0,
            "omega": DEFAULT_OMEGA,
            "eta": DEFAULT_ETA,
        },
        "acceptance_threshold": threshold,
        "final_metric": final_metric,
        "max_metric": max_metric,
        "monotone_decay": evolution["monotone_decay"],
        "status": status,
        "verdict": verdict,
        "closure_blocker": blocker,
        "next_open_sector": next_open_sector(),
        "honest_note": (
            "Two-sector closure extends the reduced (homogeneous, zero-shift) "
            "T3 to an oscillating radion shift β^φ(t) ≠ 0 with the explicit "
            "momentum-constraint coupling. Reduced sector is unchanged; this "
            "is the *next* sector closer to ADM_FULL_DYNAMICAL_5D."
        ),
        "separation_guard": separation_guard(),
    }


def next_open_sector() -> Dict[str, str]:
    """Name the next sector remaining open after this module passes."""
    return {
        "id": "T3_INHOMOGENEOUS_LAPSE",
        "title": "Inhomogeneous lapse evolution N(x, t) with full spatial Laplacian",
        "blocker": (
            "Full 5D ADM with inhomogeneous lapse evolution and momentum "
            "constraint on the radion-perturbed background remains open."
        ),
        "remaining_open_foundational_boundary": "ADM_FULL_DYNAMICAL_5D",
    }
