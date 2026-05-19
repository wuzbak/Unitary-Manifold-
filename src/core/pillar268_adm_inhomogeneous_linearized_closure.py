# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 268 — ADM linearized inhomogeneous closure audit.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

This module pushes the ADM closure lane beyond the homogeneous reduced-sector
certificate by scanning linearized inhomogeneous perturbations of the KK metric
and checking the full executable constraint monitor from ``adm_engine.py``.

Honest scope:
- closes the linearized inhomogeneous perturbative lane,
- preserves the statement that non-perturbative / Wheeler–DeWitt closure
  remains open.
"""
from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence

import numpy as np

from src.core.adm_engine import constraint_residuals
from src.core.pillar263_bssn_kk_extrinsic_curvature import CONSTRAINT_PASS_THRESHOLD

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "GAUSS_TARGET",
    "linearized_kk_profile",
    "linearized_constraint_packet",
    "linearized_inhomogeneous_scan",
    "adm_linearized_inhomogeneous_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
GAUSS_TARGET: float = 1e-6
PHI_BACKGROUND: float = 1.0


def linearized_kk_profile(
    n_points: int = 64,
    amplitude: float = 1e-7,
    mode: int = 1,
) -> Dict[str, np.ndarray | float | int]:
    """Return a linearized inhomogeneous KK perturbation packet.

    The background is a flat 4D slice with a small sinusoidal radion / metric /
    KK-vector perturbation of amplitude ``amplitude``.
    """
    if n_points < 8:
        raise ValueError("n_points must be at least 8")
    if amplitude <= 0.0:
        raise ValueError("amplitude must be positive")
    if mode < 1:
        raise ValueError("mode must be >= 1")

    x = np.linspace(0.0, 1.0, n_points, endpoint=False)
    phase = 2.0 * math.pi * mode * x
    scalar = amplitude * np.cos(phase)
    vector = amplitude * np.sin(phase)

    phi = PHI_BACKGROUND * (1.0 + 0.25 * scalar)
    B = np.zeros((n_points, 4), dtype=float)
    B[:, 1] = vector
    B[:, 2] = -0.5 * vector

    g = np.zeros((n_points, 4, 4), dtype=float)
    g[:, 0, 0] = -(1.0 + 0.5 * scalar)
    g[:, 1, 1] = 1.0 + scalar
    g[:, 2, 2] = 1.0 - 0.5 * scalar
    g[:, 3, 3] = 1.0 - 0.5 * scalar

    dx = float(x[1] - x[0])
    return {
        "x": x,
        "phi": phi,
        "B": B,
        "g": g,
        "dx": dx,
        "amplitude": amplitude,
        "mode": mode,
    }


def _linearized_verdict(residuals: Dict[str, float]) -> str:
    h_ok = residuals["hamiltonian_rms"] < CONSTRAINT_PASS_THRESHOLD
    m_ok = residuals["momentum_rms"] < CONSTRAINT_PASS_THRESHOLD
    g_ok = bool(residuals["gauss_law_target_met"])
    if h_ok and m_ok and g_ok:
        return "PASS"
    if (
        residuals["hamiltonian_rms"] < 5.0 * CONSTRAINT_PASS_THRESHOLD
        and residuals["momentum_rms"] < 5.0 * CONSTRAINT_PASS_THRESHOLD
    ):
        return "TENSION"
    return "FALSIFIED"


def linearized_constraint_packet(
    n_points: int = 64,
    amplitude: float = 1e-7,
    mode: int = 1,
) -> Dict[str, object]:
    """Evaluate the executable ADM constraints on one linearized perturbation."""
    profile = linearized_kk_profile(n_points=n_points, amplitude=amplitude, mode=mode)
    residuals = constraint_residuals(
        B=profile["B"],
        phi=profile["phi"],
        g=profile["g"],
        dx=float(profile["dx"]),
    )
    verdict = _linearized_verdict(residuals)
    return {
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "amplitude": amplitude,
        "mode": mode,
        "n_points": n_points,
        "residuals": residuals,
        "verdict": verdict,
    }


def linearized_inhomogeneous_scan(
    amplitudes: Sequence[float] = (1e-7, 5e-7, 1e-6),
    modes: Sequence[int] = (1, 2, 3),
    n_points: int = 64,
) -> Dict[str, object]:
    """Scan a small perturbative basin of linearized inhomogeneous profiles."""
    packets: List[Dict[str, object]] = []
    for amplitude in amplitudes:
        for mode in modes:
            packets.append(
                linearized_constraint_packet(
                    n_points=n_points,
                    amplitude=float(amplitude),
                    mode=int(mode),
                )
            )

    pass_count = sum(1 for packet in packets if packet["verdict"] == "PASS")
    tension_count = sum(1 for packet in packets if packet["verdict"] == "TENSION")
    status = (
        "LINEARIZED_DYNAMICAL_CLOSED"
        if pass_count == len(packets)
        else "LINEARIZED_DYNAMICAL_TENSION"
    )
    return {
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "packets": packets,
        "n_packets": len(packets),
        "pass_count": pass_count,
        "tension_count": tension_count,
        "status": status,
    }


def adm_linearized_inhomogeneous_report(
    amplitudes: Iterable[float] = (1e-7, 5e-7, 1e-6),
    modes: Iterable[int] = (1, 2, 3),
    n_points: int = 64,
) -> Dict[str, object]:
    """Return the linearized inhomogeneous ADM closure report."""
    scan = linearized_inhomogeneous_scan(
        amplitudes=tuple(amplitudes),
        modes=tuple(modes),
        n_points=n_points,
    )
    fully_closed = scan["pass_count"] == scan["n_packets"]
    return {
        "pillar": 268,
        "title": "ADM linearized inhomogeneous closure audit",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "gauss_target": GAUSS_TARGET,
        "constraint_threshold": CONSTRAINT_PASS_THRESHOLD,
        "scan": scan,
        "linearized_sector_closed": fully_closed,
        "status": (
            "KINEMATIC_AND_LINEARIZED_DYNAMICAL_CLOSED"
            if fully_closed
            else "KINEMATIC_CLOSED_LINEARIZED_TENSION"
        ),
        "remaining_open": (
            "Non-perturbative inhomogeneous BSSN closure and Wheeler-DeWitt "
            "quantization remain outside this perturbative certificate."
        ),
    }
