# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/prebigbang.py
======================
Pillar 111 — Pre-Big Bang Geometry.

Models the 5D geometry *before* the (5,7) braid resonance locked at the
Chern–Simons scale k_cs = 74.  Prior to locking the fifth dimension is
dynamically active; the resonance acts as a geometric phase transition that
freezes the compact radius and sets the initial conditions for inflation.

All quantities are in natural (Planck) units.
"""

import math

WINDING_NUMBER: int = 5
K_CS: int = 74
BRAIDED_SOUND_SPEED: float = 12 / 37


def pre_braid_metric_signature() -> tuple:
    """Return the 5D metric signature before CS locking.

    Before and after locking the manifold has signature (+,−,−,−,+):
    the extra dimension is spacelike (compact circle).  The locking event
    does not change the signature — it freezes the modulus φ₀.
    """
    return (1, -1, -1, -1, 1)


def cs_locking_temperature(k_cs: int = 74, n_w: int = 5) -> float:
    """Return the CS locking temperature in Planck units.

    T_lock = k_cs / (n_w² × 2π)
    """
    return k_cs / (n_w ** 2 * 2 * math.pi)


def braid_phase_transition_width(k_cs: int = 74) -> float:
    """Return the relative width of the braid phase transition, δT/T.

    δT/T = 1 / sqrt(k_cs)
    """
    return 1.0 / math.sqrt(k_cs)


def pre_bigbang_efolds(phi0: float = 1.0) -> float:
    """Return the number of e-folds of pre-BB evolution before CS locking.

    N_pre = phi0² × K_CS / (2π)
    """
    return phi0 ** 2 * K_CS / (2 * math.pi)


def winding_lock_condition(n_w: int = 5, k_cs: int = 74) -> bool:
    """Return True if the (n_w, n_w+2) braid pair satisfies the CS resonance.

    Condition: n_w² + (n_w+2)² == k_cs
    For n_w=5: 25 + 49 = 74 = K_CS  ✓
    """
    return n_w ** 2 + (n_w + 2) ** 2 == k_cs


def prebigbang_summary() -> dict:
    """Return a summary dict of all pre-Big Bang geometry quantities."""
    return {
        "metric_signature": pre_braid_metric_signature(),
        "locking_temperature": cs_locking_temperature(),
        "transition_width": braid_phase_transition_width(),
        "pre_efolds": pre_bigbang_efolds(),
        "braid_locked": winding_lock_condition(),
    }
