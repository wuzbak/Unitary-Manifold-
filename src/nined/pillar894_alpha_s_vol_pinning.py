# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 894 — ALPHA_S_M7_VOL_PINNING.

The 9D tadpole plus braid-topology constraint pins the T² volume in string
units to Vol(T²)/α' = K_CS / n_w² = 74/25.  That removes the large volume freedom
left in the earlier 7D α_s routes and leaves only the string-coupling / S¹
normalisation ambiguity in the reduced gauge coupling.

Honest status
-------------
Volume pinning is real progress, but it does not by itself fix the full gauge
kinetic prefactor.  The α_s prediction is therefore narrowed substantially, yet
still reported as bounded rather than exactly pinned.
"""
from __future__ import annotations

import math
from typing import Any

from src.sevend.pillar861_ckm_7d_bulk_mass_spectrum import K_CS, N_W, PI_K_R

PILLAR_NUMBER: int = 894
PILLAR_GATE: str = "ALPHA_S_M7_VOL_PINNING"

ALPHA_PRIME: float = 1.0
I3_TOPOLOGY: float = (N_W**2 / K_CS) * (2.0 * math.pi) ** 2
VOL_T2_ALPHA_PRIME: float = K_CS / float(N_W**2)
G_S_CANONICAL: float = 2.95
G_S_SCAN: tuple[float, float, float] = (2.70, 2.95, 3.10)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "VOL_T2_ALPHA_PRIME",
    "ALPHA_S_PINNED",
    "ALPHA_S_INTERVAL_PINNED",
    "ALPHA_S_PINNING_GATE",
    "STATUS_LABEL",
    "vol_pinning_summary",
]


def inverse_g3_squared(vol_t2_alpha_prime: float = VOL_T2_ALPHA_PRIME, g_s: float = G_S_CANONICAL) -> float:
    """Return the reduced inverse QCD coupling 1/g3²."""
    if vol_t2_alpha_prime <= 0.0 or g_s <= 0.0:
        raise ValueError("vol_t2_alpha_prime and g_s must be positive")
    return K_CS * vol_t2_alpha_prime / (PI_K_R * g_s**2)



def alpha_s_from_gs(g_s: float = G_S_CANONICAL) -> float:
    """Return α_s from the pinned T² volume and a chosen string coupling."""
    g3_sq = 1.0 / inverse_g3_squared(g_s=g_s)
    return g3_sq / (4.0 * math.pi)


ALPHA_S_PINNED: float = alpha_s_from_gs()
_ALPHA_SCAN = [alpha_s_from_gs(g_s=value) for value in G_S_SCAN]
ALPHA_S_INTERVAL_PINNED: tuple[float, float] = (min(_ALPHA_SCAN), max(_ALPHA_SCAN))
ALPHA_S_PINNING_GATE: str = "PINNED" if ALPHA_S_INTERVAL_PINNED[1] - ALPHA_S_INTERVAL_PINNED[0] < 0.01 else "BOUNDED_NOT_PINNED"
STATUS_LABEL: str = "RESOLVED" if ALPHA_S_PINNING_GATE == "PINNED" else "PARTIAL"


def vol_pinning_summary() -> dict[str, Any]:
    """Return the machine-readable α_s volume-pinning certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": ALPHA_S_PINNING_GATE,
        "alpha_prime": ALPHA_PRIME,
        "i3_topology": I3_TOPOLOGY,
        "vol_t2_alpha_prime": VOL_T2_ALPHA_PRIME,
        "g_s_canonical": G_S_CANONICAL,
        "g_s_scan": list(G_S_SCAN),
        "alpha_s_pinned": ALPHA_S_PINNED,
        "alpha_s_interval_pinned": list(ALPHA_S_INTERVAL_PINNED),
        "epistemic_status": (
            "The braid-topology tadpole fixes Vol(T²), shrinking the old α_s band substantially. "
            "A residual coupling normalisation remains, so the result is still bounded rather than exact."
        ),
    }
