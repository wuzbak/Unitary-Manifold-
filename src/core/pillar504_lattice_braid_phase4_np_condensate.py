# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 504 — Lattice Braid Phase 4 Non-Perturbative Condensate.

🔵 ADJACENT TRACK — non-hardgate; no ToE score change.

STATUS: LATTICE_BRAID_PHASE4_NP_CONDENSATE_BOUNDED

This module turns the Phase-3 g_braid interval into a deterministic Phase-4
finite-volume condensate certificate.  It is an executable CPU-side surrogate,
not an external GPU HMC receipt; the exact HMC result remains an evidence lane.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

from src.core.pillar483_lattice_braid_phase3_gbraid import (
    DELTA_GAMMA_CENTRAL,
    DELTA_GAMMA_LOWER,
    DELTA_GAMMA_UPPER,
    ETA_BRAID,
    G_BRAID_CENTRAL,
    GAMMA_RESIDUAL_TARGET,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "ADJACENCY_TRACK_LABEL",
    "FINITE_VOLUME_SIZES",
    "finite_volume_condensate",
    "np_condensate_sequence",
    "phase4_residual_band",
    "l2_closure_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 504
PILLAR_STATUS: str = "LATTICE_BRAID_PHASE4_NP_CONDENSATE_BOUNDED"
ADJACENCY_TRACK_LABEL: str = "🔵 ADJACENT TRACK"
FINITE_VOLUME_SIZES: List[int] = [16, 24, 32, 48, 64, 96]


def finite_volume_condensate(size: int, g_braid: float = G_BRAID_CENTRAL) -> Dict[str, float]:
    """Evaluate the finite-volume non-perturbative condensate proxy."""
    if size <= 0:
        raise ValueError("size must be positive")
    anomalous_scaling = size ** (-ETA_BRAID / 2.0)
    finite_volume_loss = 1.0 / (1.0 + math.sqrt(size))
    condensate = g_braid * anomalous_scaling * (1.0 - finite_volume_loss)
    return {
        "size": float(size),
        "g_braid": g_braid,
        "eta": ETA_BRAID,
        "condensate": condensate,
        "finite_volume_loss": finite_volume_loss,
    }


def np_condensate_sequence(sizes: List[int] | None = None) -> List[Dict[str, float]]:
    """Return the deterministic finite-volume sequence."""
    return [finite_volume_condensate(size) for size in (sizes or FINITE_VOLUME_SIZES)]


def phase4_residual_band() -> Dict[str, float]:
    """Convert the Phase-3 bound into the Phase-4 residual band."""
    central_remaining = abs(GAMMA_RESIDUAL_TARGET - DELTA_GAMMA_CENTRAL)
    best_case_remaining = max(0.0, GAMMA_RESIDUAL_TARGET - DELTA_GAMMA_UPPER)
    conservative_remaining = abs(GAMMA_RESIDUAL_TARGET - DELTA_GAMMA_LOWER)
    return {
        "target": GAMMA_RESIDUAL_TARGET,
        "delta_gamma_lower": DELTA_GAMMA_LOWER,
        "delta_gamma_central": DELTA_GAMMA_CENTRAL,
        "delta_gamma_upper": DELTA_GAMMA_UPPER,
        "central_remaining": central_remaining,
        "best_case_remaining": best_case_remaining,
        "conservative_remaining": conservative_remaining,
        "sub_1pct_coverable": DELTA_GAMMA_UPPER >= GAMMA_RESIDUAL_TARGET - 0.01,
    }


def l2_closure_certificate() -> Dict[str, object]:
    """Machine-readable L2 γ residual verdict."""
    band = phase4_residual_band()
    sequence = np_condensate_sequence()
    monotone = all(
        sequence[i + 1]["condensate"] >= sequence[i]["condensate"] * 0.90
        for i in range(len(sequence) - 1)
    )
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "adjacent_track": True,
        "external_hmc_receipt": False,
        "finite_volume_monotone_stable": monotone,
        "residual_band": band,
        "epistemic_delta": "L2_GBRAID_BOUNDED_QUANTIFIED -> L2_PHASE4_NP_CONDENSATE_BOUNDED",
        "hardgate_score_delta": 0.0,
    }


def pillar_report() -> Dict[str, object]:
    """Machine-readable Pillar 504 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "label": ADJACENCY_TRACK_LABEL,
        "certificate": l2_closure_certificate(),
    }
